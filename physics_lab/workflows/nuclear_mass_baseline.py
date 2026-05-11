"""Nuclear mass baseline residual benchmark workflow."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from physics_lab import __version__
from physics_lab.engines.nuclear_mass_baselines import (
    REFERENCE_SEMI_EMPIRICAL_COEFFICIENTS,
    SemiEmpiricalCoefficients,
    evaluate_baseline,
    fit_semi_empirical_coefficients,
    summarize_absolute_metrics,
    top_residual_rows,
)
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset
from physics_lab.engines.scoring import ModelScore, compute_error_metrics
from physics_lab.registry.examples import load_example_config
from physics_lab.registry.experiments import load_experiment
from physics_lab.registry.hypotheses import load_hypothesis
from physics_lab.registry.results import validate_result_payload
from physics_lab.workflows.artifacts import (
    ExperimentArtifacts,
    ExperimentOutcome,
    best_result_verdict,
    find_repo_root,
    git_commit,
    relative_or_absolute,
    render_patch_artifact,
    render_review_metadata,
    render_review_summary,
    resolve_path,
    serialize_scores,
    snapshot_input_files,
    task_path,
    write_text_atomic,
)
from physics_lab.workflows.claim_semantics import suggest_claim_status


def _baseline_limitations() -> list[str]:
    return [
        "This benchmark uses a small pinned measured slice rather than the full AME2020 surface.",
        "Residual maps here characterize a simple semi-empirical baseline only; they do not imply a new shell model or universal mass law.",
        "The fitted coefficient set is slice-specific and should not be treated as a holdout-validated predictive model before TASK-0169 lands.",
    ]


def _verification_check(name: str, status: str, details: str, metrics: dict[str, Any]) -> dict[str, Any]:
    return {"name": name, "status": status, "details": details, "metrics": metrics}


def _classify_baseline_score(
    score: ModelScore,
    *,
    overall_mae_mev: float,
    magic_mae_mev: float,
) -> str:
    if overall_mae_mev <= 1.5 and magic_mae_mev <= 3.5:
        return "VALID"
    if overall_mae_mev <= 4.0 and magic_mae_mev <= 8.0:
        return "PARTIALLY_VALID"
    if score.test_metrics.mean_relative_error > score.train_metrics.mean_relative_error * 2.0:
        return "OVERFITTED"
    return "INCONCLUSIVE"


def _score_candidate(
    *,
    model_id: str,
    formula: str,
    complexity_score: int,
    overall_observed: np.ndarray,
    overall_predicted: np.ndarray,
    magic_observed: np.ndarray,
    magic_predicted: np.ndarray,
    coefficients: SemiEmpiricalCoefficients,
) -> ModelScore:
    overall_metrics = compute_error_metrics(overall_predicted, overall_observed)
    magic_metrics = compute_error_metrics(magic_predicted, magic_observed)
    composite_score = overall_metrics.mean_relative_error + 0.75 * magic_metrics.mean_relative_error + 0.001 * complexity_score
    return ModelScore(
        model_id=model_id,
        formula=formula,
        coefficients=coefficients.to_dict(),
        complexity_score=complexity_score,
        train_metrics=overall_metrics,
        test_metrics=magic_metrics,
        composite_score=float(composite_score),
    )


def _build_claim_update(
    *,
    claim_id: str,
    result_id: str,
    experiment_id: str,
    hypothesis_id: str,
    task_id: str,
    verification_summary: dict[str, Any],
) -> str:
    return "\n".join(
        [
            f"# Claim Update Proposal for {claim_id}",
            "",
            "## Scope",
            "",
            "Keep the claim benchmark-scoped. The current run evaluates one pinned nuclear-mass slice and one simple semi-empirical baseline family only.",
            "",
            "## Linked Evidence",
            "",
            f"- Hypothesis: `{hypothesis_id}`",
            f"- Experiment: `{experiment_id}`",
            f"- Result: `{result_id}`",
            f"- Task: `{task_id}`",
            "",
            "## Verification Snapshot",
            "",
            f"- Verification gate passed: `{verification_summary['passed']}`",
            *(f"- {check['name']}: `{check['status']}`" for check in verification_summary["checks"]),
            "",
            "## Recommendation",
            "",
            "Retain `DRAFT` until the dataset slice, baseline wording, and future holdout contract are reviewed together.",
            "",
        ]
    )


def _build_claim_patch(
    *,
    repo_root: Path,
    result_id: str,
    suggestion_status: str,
    suggestion_rationale: str,
) -> str:
    target_file = "claims/CLAIM-0010-nuclear-mass-baseline.md"
    target_path = repo_root / target_file
    original_text = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
    proposed_text = original_text.replace("status: DRAFT", f"status: {suggestion_status}", 1)
    proposed_text = proposed_text.replace(
        "A maintainer should keep this claim draft until broader dataset and holdout semantics are reviewed.",
        suggestion_rationale,
        1,
    )
    if result_id not in proposed_text:
        proposed_text = proposed_text.replace("  results:\n    - RESULT-0015", f"  results:\n    - {result_id}", 1)
    return render_patch_artifact(
        title="Claim Patch Proposal for CLAIM-0010",
        target_file=target_file,
        evidence_basis=[result_id],
        original_text=original_text,
        proposed_text=proposed_text,
        proposed_status=suggestion_status,
        sections_to_update=["Evidence Status", "Review Recommendation"],
        rationale="Keep any support statement tied to the pinned slice and current semi-empirical baseline family only.",
    )


def _build_knowledge_update(
    *,
    knowledge_id: str,
    result_id: str,
    experiment_id: str,
    hypothesis_id: str,
    task_id: str,
    best_model_id: str,
) -> str:
    return "\n".join(
        [
            f"# Knowledge Update Proposal for {knowledge_id}",
            "",
            "## Target Knowledge Note",
            "",
            "- Topic: nuclear mass baseline residual benchmark",
            "",
            "## Suggested Linked Objects Update",
            "",
            f"- Hypothesis: `{hypothesis_id}`",
            f"- Experiment: `{experiment_id}`",
            "- Claim: `CLAIM-0010`",
            f"- Task: `{task_id}`",
            f"- Canonical result: `{result_id}`",
            "",
            "## Proposed Additions",
            "",
            "- Add the first pinned measured nuclear-mass slice as a benchmark bring-up surface.",
            f"- Record `{best_model_id}` as the current best semi-empirical baseline on this slice.",
            "- Preserve shell-closure residual concentration as a diagnostic rather than a discovery statement.",
            "",
        ]
    )


def _build_knowledge_patch(
    *,
    repo_root: Path,
    result_id: str,
    best_model_id: str,
) -> str:
    target_file = "knowledge/nuclear_physics/nuclear_mass_baseline.md"
    target_path = repo_root / target_file
    original_text = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
    proposed_text = original_text
    if result_id not in proposed_text:
        proposed_text = proposed_text.replace("- Canonical result: `RESULT-0015`", f"- Canonical result: `{result_id}`", 1)
    if best_model_id not in proposed_text:
        proposed_text = proposed_text.replace(
            "The benchmark compares reference-coefficient and fitted semi-empirical baselines against a small pinned measured slice.",
            "The benchmark compares reference-coefficient and fitted semi-empirical baselines against a small pinned measured slice.\n"
            f"The current canonical run selects `{best_model_id}` as the best model on the slice and shell subset diagnostics.",
            1,
        )
    return render_patch_artifact(
        title="Knowledge Patch Proposal for KNOW-0009",
        target_file=target_file,
        evidence_basis=[result_id],
        original_text=original_text,
        proposed_text=proposed_text,
        sections_to_update=["Known Baseline", "Linked Objects", "Open Questions"],
        rationale="Preserve the baseline benchmark as reusable scientific memory without overstating shell-structure interpretation.",
    )


def _build_review_summary(
    *,
    result_id: str,
    suggestion_status: str,
    suggestion_rationale: str,
    limitations: list[str],
) -> str:
    return render_review_summary(
        result_id=result_id,
        claim_id="CLAIM-0010",
        knowledge_id="KNOW-0009",
        suggested_status=suggestion_status,
        rationale=suggestion_rationale,
        highlights=[
            "The repository now has a first pinned measured nuclear-mass slice and an executable semi-empirical baseline benchmark.",
            "Magic-number and pairing-sensitive residual subsets are explicit benchmark diagnostics rather than loose commentary.",
        ],
        limitations=limitations,
    )


def _build_report(
    *,
    title: str,
    result_id: str,
    run_id: str,
    hypothesis_id: str,
    task_id: str,
    dataset_id: str,
    assumptions: list[str],
    limitations: list[str],
    scores: list[ModelScore],
    verdicts: dict[str, str],
    summary_by_model: dict[str, dict[str, Any]],
    top_rows_by_model: dict[str, list[dict[str, Any]]],
    verification_summary: dict[str, Any],
    best_model_id: str,
) -> str:
    lines = [
        f"# {title}",
        "",
        f"- Result: `{result_id}`",
        f"- Run: `{run_id}`",
        f"- Hypothesis: `{hypothesis_id}`",
        f"- Task: `{task_id}`",
        f"- Dataset: `{dataset_id}`",
        "",
        "## Assumptions",
        "",
        *(f"- {assumption}" for assumption in assumptions),
        "",
        "## Limitations",
        "",
        *(f"- {limitation}" for limitation in limitations),
        "",
        "## Verification",
        "",
        f"- Verification gate passed: `{verification_summary['passed']}`",
        *(f"- {check['name']}: `{check['status']}`" for check in verification_summary["checks"]),
        "",
        "## Candidate Models",
        "",
        "| Model | Complexity | Overall MAE (MeV) | Magic-subset MAE (MeV) | Odd-even MAE (MeV) | Verdict |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for score in scores:
        model_summary = summary_by_model[score.model_id]
        lines.append(
            "| "
            + " | ".join(
                [
                    score.model_id,
                    str(score.complexity_score),
                    f"{model_summary['overall']['mae_mev']:.3f}",
                    f"{model_summary['magic']['mae_mev']:.3f}",
                    f"{model_summary['odd_even_delta_mae_mev']:.3f}",
                    verdicts[score.model_id],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Residual Diagnostics",
            "",
        ]
    )
    for model_id, model_summary in summary_by_model.items():
        lines.extend(
            [
                f"### {model_id}",
                "",
                f"- Overall RMSE: `{model_summary['overall']['rmse_mev']:.3f}` MeV",
                f"- Magic-subset MAE inflation factor: `{model_summary['magic_mae_inflation']:.3f}`",
                f"- Mean abs normalized residual: `{model_summary['overall']['mean_abs_normalized_residual']:.2f}`",
                f"- Pairing-class MAE spread: `{model_summary['odd_even_delta_mae_mev']:.3f}` MeV",
                "",
                "Top absolute residual entries:",
                "",
            ]
        )
        for row in top_rows_by_model[model_id]:
            lines.append(
                f"- `{row['nuclide_id']}`: residual `{row['residual_mev']:.3f}` MeV "
                f"(magic_any=`{row['is_magic_any']}`, pairing=`{row['pairing_class']}`)"
            )
        lines.append("")
    lines.extend(
        [
            "## Verdict",
            "",
            f"`{best_model_id}` is the current best semi-empirical baseline on the pinned slice, reported as `{verdicts[best_model_id]}`.",
            "",
            "## Conclusion",
            "",
            "This benchmark establishes a first reviewable nuclear-mass residual surface: a pinned measured slice, explicit semi-empirical baselines, and shell-aware diagnostics ready for later holdout work.",
            "",
        ]
    )
    return "\n".join(lines)


def _model_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    magic_rows = [row for row in rows if row["is_magic_any"]]
    odd_even_rows = [row for row in rows if row["pairing_class"] == "even_even"]
    odd_a_rows = [row for row in rows if row["pairing_class"] == "odd_a"]
    odd_odd_rows = [row for row in rows if row["pairing_class"] == "odd_odd"]

    overall = summarize_absolute_metrics(_dict_rows_to_objects(rows))
    magic = summarize_absolute_metrics(_dict_rows_to_objects(magic_rows))
    even_even = summarize_absolute_metrics(_dict_rows_to_objects(odd_even_rows))
    odd_a = summarize_absolute_metrics(_dict_rows_to_objects(odd_a_rows))
    odd_odd = summarize_absolute_metrics(_dict_rows_to_objects(odd_odd_rows))

    subgroup_maes = [
        value
        for value in (
            even_even["mae_mev"],
            odd_a["mae_mev"],
            odd_odd["mae_mev"],
        )
        if value is not None
    ]
    return {
        "overall": overall,
        "magic": magic,
        "pairing_classes": {
            "even_even": even_even,
            "odd_a": odd_a,
            "odd_odd": odd_odd,
        },
        "magic_mae_inflation": (
            float(magic["mae_mev"] / overall["mae_mev"])
            if magic["mae_mev"] is not None and overall["mae_mev"] not in {None, 0.0}
            else None
        ),
        "odd_even_delta_mae_mev": (
            float(max(subgroup_maes) - min(subgroup_maes)) if subgroup_maes else 0.0
        ),
    }


def _dict_rows_to_objects(rows: list[dict[str, Any]]) -> list[_ResidualView]:
    return [_ResidualView(**row) for row in rows]


class _ResidualView:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)


def run_nuclear_mass_baseline_experiment_with_output(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> ExperimentOutcome:
    """Execute the nuclear-mass baseline residual benchmark."""
    config_path = Path(config_path).resolve()
    config = load_example_config(config_path)
    experiment_path = resolve_path(config_path, config["experiment_path"])
    hypothesis_path = resolve_path(config_path, config["hypothesis_path"])
    repo_root = find_repo_root(config_path)
    experiment = load_experiment(experiment_path)
    hypothesis = load_hypothesis(hypothesis_path)
    task_id = str(config.get("task_id", ""))
    run_id = str(config.get("run_id", ""))
    result_id = str(config.get("result_id", ""))
    default_result_root = resolve_path(config_path, str(config.get("result_root", "")))
    result_root = Path(output_dir).resolve() / str(experiment["id"]) if output_dir is not None else default_result_root

    if experiment["hypothesis_id"] != hypothesis["id"]:
        raise ValueError("Experiment hypothesis_id does not match loaded hypothesis id")
    if not task_id or not run_id or not result_id:
        raise ValueError("Experiment config must define task_id, run_id, and result_id")
    if not str(config.get("result_root", "")):
        raise ValueError("Experiment config must define result_root for run-based outputs")

    dataset_path = resolve_path(experiment_path, experiment["data"]["dataset_path"])
    dataset = load_nuclear_mass_dataset(dataset_path)
    target_payload = experiment["comparison_targets"][0]
    target_magic_mae_mev = float(target_payload["reference_value"])
    expected_item_count = int(experiment["data"]["expected_item_count"])
    if len(dataset.entries) != expected_item_count:
        raise ValueError(
            f"Expected {expected_item_count} nuclear-mass entries, got {len(dataset.entries)}"
        )

    fitted_coefficients = fit_semi_empirical_coefficients(dataset.entries)
    reference_no_pairing = SemiEmpiricalCoefficients(
        volume=REFERENCE_SEMI_EMPIRICAL_COEFFICIENTS.volume,
        surface=REFERENCE_SEMI_EMPIRICAL_COEFFICIENTS.surface,
        coulomb=REFERENCE_SEMI_EMPIRICAL_COEFFICIENTS.coulomb,
        asymmetry=REFERENCE_SEMI_EMPIRICAL_COEFFICIENTS.asymmetry,
        pairing=0.0,
    )
    coefficient_sets = {
        "model_reference_liquid_drop_no_pairing": reference_no_pairing,
        "model_reference_semi_empirical": REFERENCE_SEMI_EMPIRICAL_COEFFICIENTS,
        "model_fitted_semi_empirical": fitted_coefficients,
    }

    rows_by_model = {
        model_id: [row.to_dict() for row in evaluate_baseline(entries=dataset.entries, model_id=model_id, coefficients=coefficients)]
        for model_id, coefficients in coefficient_sets.items()
    }
    summary_by_model = {
        model_id: _model_summary(rows)
        for model_id, rows in rows_by_model.items()
    }
    top_rows_by_model = {
        model_id: [row.to_dict() for row in top_residual_rows(evaluate_baseline(entries=dataset.entries, model_id=model_id, coefficients=coefficients), limit=5)]
        for model_id, coefficients in coefficient_sets.items()
    }

    candidate_formulas = {candidate["id"]: candidate["formula"] for candidate in experiment["candidate_models"]}
    scores: list[ModelScore] = []
    verdicts: dict[str, str] = {}
    for model_id, rows in rows_by_model.items():
        observed = np.asarray([row["observed_binding_energy_mev"] for row in rows], dtype=float)
        predicted = np.asarray([row["predicted_binding_energy_mev"] for row in rows], dtype=float)
        magic_rows = [row for row in rows if row["is_magic_any"]]
        magic_observed = np.asarray([row["observed_binding_energy_mev"] for row in magic_rows], dtype=float)
        magic_predicted = np.asarray([row["predicted_binding_energy_mev"] for row in magic_rows], dtype=float)
        score = _score_candidate(
            model_id=model_id,
            formula=candidate_formulas[model_id],
            complexity_score=4 if model_id == "model_reference_liquid_drop_no_pairing" else 5,
            overall_observed=observed,
            overall_predicted=predicted,
            magic_observed=magic_observed,
            magic_predicted=magic_predicted,
            coefficients=coefficient_sets[model_id],
        )
        scores.append(score)
        verdicts[model_id] = _classify_baseline_score(
            score,
            overall_mae_mev=float(summary_by_model[model_id]["overall"]["mae_mev"]),
            magic_mae_mev=float(summary_by_model[model_id]["magic"]["mae_mev"]),
        )
    scores.sort(key=lambda item: item.composite_score)
    best_model_id = scores[0].model_id
    best_verdict = best_result_verdict(verdicts[best_model_id])

    fitted_overall_mae = float(summary_by_model["model_fitted_semi_empirical"]["overall"]["mae_mev"])
    reference_overall_mae = float(summary_by_model["model_reference_semi_empirical"]["overall"]["mae_mev"])
    no_pairing_odd_even_delta = float(summary_by_model["model_reference_liquid_drop_no_pairing"]["odd_even_delta_mae_mev"])
    with_pairing_odd_even_delta = float(summary_by_model["model_reference_semi_empirical"]["odd_even_delta_mae_mev"])
    verification_payload = {
        "passed": True,
        "checks": [
            _verification_check(
                "dataset_slice_loaded",
                "PASS",
                "Loaded the pinned measured nuclear-mass slice with the expected entry count.",
                {"dataset_id": dataset.dataset_id, "entry_count": len(dataset.entries)},
            ),
            _verification_check(
                "binding_energy_reconstruction",
                "PASS",
                "Derived binding energies and atomic-mass residuals deterministically from the pinned dataset entries.",
                {"dataset_kind": experiment["data"]["dataset_kind"]},
            ),
            _verification_check(
                "fitted_baseline_improves_overall_mae",
                "PASS" if fitted_overall_mae < reference_overall_mae else "FAIL",
                "Checked whether the fitted semi-empirical baseline improves the overall mean absolute residual on the pinned slice.",
                {"reference_mae_mev": reference_overall_mae, "fitted_mae_mev": fitted_overall_mae},
            ),
            _verification_check(
                "pairing_term_reduces_pairing_spread",
                "PASS" if with_pairing_odd_even_delta <= no_pairing_odd_even_delta else "FAIL",
                "Compared pairing-class residual spread with and without the explicit pairing term.",
                {
                    "no_pairing_odd_even_delta_mae_mev": no_pairing_odd_even_delta,
                    "with_pairing_odd_even_delta_mae_mev": with_pairing_odd_even_delta,
                },
            ),
            _verification_check(
                "magic_subset_diagnostics_present",
                "PASS",
                "Computed shell-closure subset metrics and top residual rows for review.",
                {
                    "magic_entry_count": len([row for row in rows_by_model[best_model_id] if row["is_magic_any"]]),
                    "top_residual_count": len(top_rows_by_model[best_model_id]),
                },
            ),
            _verification_check(
                "uncertainty_normalized_residuals_present",
                "PASS",
                "Recorded uncertainty-normalized residual summaries for the pinned measured slice.",
                {
                    "mean_abs_normalized_residual": summary_by_model[best_model_id]["overall"]["mean_abs_normalized_residual"],
                },
            ),
        ],
    }
    verification_payload["passed"] = all(check["status"] == "PASS" for check in verification_payload["checks"])
    claim_status_suggestion = suggest_claim_status(
        verification_summary=verification_payload,
        best_verdict=best_verdict,
        range_limited=True,
        exact_verification=False,
    )

    run_dir = result_root / run_id
    result_path = run_dir / "result.yaml"
    report_path = run_dir / "report.md"
    metrics_path = run_dir / "metrics.json"
    claim_update_path = run_dir / "claim_update.md"
    claim_update_patch_path = run_dir / "claim_update.patch.md"
    knowledge_update_path = run_dir / "knowledge_update.md"
    knowledge_update_patch_path = run_dir / "knowledge_update.patch.md"
    review_summary_path = run_dir / "review_summary.md"
    review_metadata_path = run_dir / "review_metadata.yaml"
    run_dir.mkdir(parents=True, exist_ok=True)

    limitations = _baseline_limitations()
    assumptions = list(hypothesis["assumptions"])
    task_file = task_path(repo_root, task_id)
    command_path = relative_or_absolute(config_path, repo_root)
    command = f"physics-lab run {command_path}"
    if output_dir is not None:
        command += f" --output-dir {relative_or_absolute(Path(output_dir).resolve(), repo_root)}"
    input_hashes = snapshot_input_files(
        run_dir=run_dir,
        repo_root=repo_root,
        input_files={
            "config": config_path,
            "experiment": experiment_path,
            "hypothesis": hypothesis_path,
            "task": task_file,
        },
    )
    dataset_input_path = run_dir / "inputs" / "dataset.yaml"
    write_text_atomic(dataset_input_path, dataset_path.read_text(encoding="utf-8"))
    from physics_lab.workflows.artifacts import hash_file

    dataset_input_hash = hash_file(dataset_input_path, repo_root)
    current_commit = git_commit(repo_root)

    report_text = _build_report(
        title=str(experiment["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(experiment["hypothesis_id"]),
        task_id=task_id,
        dataset_id=dataset.dataset_id,
        assumptions=assumptions,
        limitations=limitations,
        scores=scores,
        verdicts=verdicts,
        summary_by_model=summary_by_model,
        top_rows_by_model=top_rows_by_model,
        verification_summary=verification_payload,
        best_model_id=best_model_id,
    )
    write_text_atomic(report_path, report_text)

    generated_at = datetime.now(timezone.utc).isoformat()
    result_payload = {
        "result_id": result_id,
        "run_id": run_id,
        "experiment_id": str(experiment["id"]),
        "title": str(experiment["title"]),
        "hypothesis_id": str(experiment["hypothesis_id"]),
        "task_id": task_id,
        "generated_at": generated_at,
        "engine_version": __version__,
        "git_commit": current_commit,
        "command": command,
        "input_file_hashes": {
            "config": input_hashes["config"],
            "experiment": input_hashes["experiment"],
            "hypothesis": input_hashes["hypothesis"],
            "task": input_hashes["task"],
        },
        "code_reference": "physics_lab/workflows/nuclear_mass_baseline.py",
        "limitations": limitations,
        "best_model_id": best_model_id,
        "best_verdict": best_verdict,
        "verification": verification_payload,
        "comparison_summary": [
            {
                "target_id": str(target_payload["id"]),
                "label": str(target_payload["label"]),
                "reference_value": target_magic_mae_mev,
                "observed_value": summary_by_model[best_model_id]["magic"]["mae_mev"],
                "unit": "MeV",
                "absolute_difference": abs(
                    float(summary_by_model[best_model_id]["magic"]["mae_mev"]) - target_magic_mae_mev
                ),
                "relative_difference": abs(
                    float(summary_by_model[best_model_id]["magic"]["mae_mev"]) - target_magic_mae_mev
                )
                / target_magic_mae_mev,
                "notes": str(target_payload.get("notes", "")),
            }
        ],
        "uncertainty_summary": {
            "method": "atomic_mass_uncertainty_to_binding_energy",
            "observed_uncertainty": summary_by_model[best_model_id]["overall"]["mean_abs_normalized_residual"],
            "reference_uncertainty": None,
            "combined_uncertainty": None,
            "z_score": None,
            "within_combined_uncertainty": None,
            "notes": "The pinned slice uses explicit atomic-mass uncertainties, but they are not yet a full-review uncertainty benchmark surface.",
        },
        "artifacts": {
            "report": relative_or_absolute(report_path, repo_root),
            "metrics": relative_or_absolute(metrics_path, repo_root),
            "claim_update": relative_or_absolute(claim_update_path, repo_root),
            "claim_update_patch": relative_or_absolute(claim_update_patch_path, repo_root),
            "knowledge_update": relative_or_absolute(knowledge_update_path, repo_root),
            "knowledge_update_patch": relative_or_absolute(knowledge_update_patch_path, repo_root),
            "review_summary": relative_or_absolute(review_summary_path, repo_root),
            "review_metadata": relative_or_absolute(review_metadata_path, repo_root),
        },
        "scores": serialize_scores(scores, verdicts),
    }
    validate_result_payload(result_payload, source=result_path)
    write_text_atomic(result_path, yaml.safe_dump(result_payload, sort_keys=False))

    metrics_payload = {
        "result_id": result_id,
        "run_id": run_id,
        "dataset_id": dataset.dataset_id,
        "best_model_id": best_model_id,
        "best_verdict": best_verdict,
        "verification": verification_payload,
        "dataset_input_hash": dataset_input_hash,
        "model_summaries": summary_by_model,
        "top_residual_rows": top_rows_by_model,
        "scores": result_payload["scores"],
    }
    write_text_atomic(metrics_path, json.dumps(metrics_payload, indent=2))

    write_text_atomic(
        claim_update_path,
        _build_claim_update(
            claim_id="CLAIM-0010",
            result_id=result_id,
            experiment_id=str(experiment["id"]),
            hypothesis_id=str(experiment["hypothesis_id"]),
            task_id=task_id,
            verification_summary=verification_payload,
        ),
    )
    write_text_atomic(
        claim_update_patch_path,
        _build_claim_patch(
            repo_root=repo_root,
            result_id=result_id,
            suggestion_status=claim_status_suggestion.status,
            suggestion_rationale=claim_status_suggestion.rationale,
        ),
    )
    write_text_atomic(
        knowledge_update_path,
        _build_knowledge_update(
            knowledge_id="KNOW-0009",
            result_id=result_id,
            experiment_id=str(experiment["id"]),
            hypothesis_id=str(experiment["hypothesis_id"]),
            task_id=task_id,
            best_model_id=best_model_id,
        ),
    )
    write_text_atomic(
        knowledge_update_patch_path,
        _build_knowledge_patch(
            repo_root=repo_root,
            result_id=result_id,
            best_model_id=best_model_id,
        ),
    )
    review_summary_text = _build_review_summary(
        result_id=result_id,
        suggestion_status=claim_status_suggestion.status,
        suggestion_rationale=claim_status_suggestion.rationale,
        limitations=limitations,
    )
    write_text_atomic(review_summary_path, review_summary_text)
    review_metadata_payload = render_review_metadata(
        result_id=result_id,
        run_id=run_id,
        experiment_id=str(experiment["id"]),
        claim_id="CLAIM-0010",
        knowledge_id="KNOW-0009",
        generated_at=generated_at,
        proposed_claim_status=claim_status_suggestion.status,
        evidence_basis=[result_id],
        claim_target_file="claims/CLAIM-0010-nuclear-mass-baseline.md",
        knowledge_target_file="knowledge/nuclear_physics/nuclear_mass_baseline.md",
        claim_patch_path=relative_or_absolute(claim_update_patch_path, repo_root),
        knowledge_patch_path=relative_or_absolute(knowledge_update_patch_path, repo_root),
        review_summary_path=relative_or_absolute(review_summary_path, repo_root),
    )
    write_text_atomic(review_metadata_path, yaml.safe_dump(review_metadata_payload, sort_keys=False))

    artifacts = ExperimentArtifacts(
        result_path=result_path,
        report_path=report_path,
        metrics_path=metrics_path,
        claim_update_path=claim_update_path,
        claim_update_patch_path=claim_update_patch_path,
        knowledge_update_path=knowledge_update_path,
        knowledge_update_patch_path=knowledge_update_patch_path,
        review_summary_path=review_summary_path,
        review_metadata_path=review_metadata_path,
    )
    return ExperimentOutcome(
        title=str(experiment["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(experiment["hypothesis_id"]),
        task_id=task_id,
        artifacts=artifacts,
        best_model_id=best_model_id,
        verdicts=verdicts,
        scores=scores,
        summary_lines=(
            f"Dataset: {dataset.dataset_id}",
            f"Magic-subset MAE: {summary_by_model[best_model_id]['magic']['mae_mev']:.3f} MeV",
        ),
    )
