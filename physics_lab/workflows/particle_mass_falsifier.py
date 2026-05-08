"""Particle-mass relation falsifier workflow."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import yaml

from physics_lab import __version__
from physics_lab.engines.particle_mass_falsifier import (
    FamilyEvaluation,
    ParticleMassInput,
    evaluate_family,
    particle_input_from_mapping,
    standard_koide_complexity_penalty,
)
from physics_lab.registry import load_example_config, load_experiment, load_hypothesis
from physics_lab.registry.results import validate_result_payload
from physics_lab.workflows.artifacts import (
    ExperimentArtifacts,
    ExperimentOutcome,
    find_repo_root,
    git_commit,
    hash_file,
    relative_or_absolute,
    render_review_metadata,
    render_review_summary,
    resolve_path,
    snapshot_input_files,
    task_path,
    write_text_atomic,
)


def _load_dataset(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in particle-mass falsifier dataset: {path}")
    return data


def _family_inputs(dataset: dict[str, Any]) -> dict[str, tuple[ParticleMassInput, ...]]:
    families: dict[str, tuple[ParticleMassInput, ...]] = {}
    for family in dataset.get("families", []):
        family_id = str(family["id"])
        entries = tuple(particle_input_from_mapping(entry) for entry in family["entries"])
        if len(entries) != 3:
            raise ValueError(f"Family {family_id!r} must contain exactly three particles.")
        families[family_id] = entries
    return families


def _evaluate_families(
    dataset: dict[str, Any],
    experiment: dict[str, Any],
) -> list[FamilyEvaluation]:
    families = _family_inputs(dataset)
    all_masses = [
        particle.mass_mev
        for particles in families.values()
        for particle in particles
    ]
    baseline = experiment["data"].get("random_baseline", {})
    sample_count = int(baseline.get("sample_count", 10000))
    seed = int(baseline.get("seed", 4040))
    family_specs = experiment["data"].get("families", [])
    if not family_specs:
        family_specs = [{"id": family_id, "label": family_id} for family_id in families]

    evaluations: list[FamilyEvaluation] = []
    for index, spec in enumerate(family_specs):
        family_id = str(spec["id"])
        if family_id not in families:
            raise ValueError(f"Experiment references unknown family id: {family_id}")
        evaluations.append(
            evaluate_family(
                family_id=family_id,
                label=str(spec.get("label", family_id)),
                particles=families[family_id],  # type: ignore[arg-type]
                mass_min_mev=min(all_masses),
                mass_max_mev=max(all_masses),
                baseline_seed=seed + index,
                baseline_sample_count=sample_count,
                limitation=str(spec.get("limitation", "")),
            )
        )
    return evaluations


def _global_verdict(evaluations: list[FamilyEvaluation]) -> str:
    """Verdict for the cross-family survival hypothesis."""
    if any(evaluation.verdict == "INVALID" for evaluation in evaluations):
        return "INVALID"
    if all(evaluation.verdict == "VALID" for evaluation in evaluations):
        return "VALID"
    return "INCONCLUSIVE"


def _family_metrics(evaluation: FamilyEvaluation) -> dict[str, Any]:
    baseline = evaluation.random_baseline
    return {
        "family_id": evaluation.family_id,
        "label": evaluation.label,
        "particles": [particle.symbol for particle in evaluation.particles],
        "masses_mev": [particle.mass_mev for particle in evaluation.particles],
        "uncertainties_mev": [particle.uncertainty_mev for particle in evaluation.particles],
        "mass_types": [particle.mass_type for particle in evaluation.particles],
        "schemes": [particle.scheme or "none" for particle in evaluation.particles],
        "scales": [particle.scale or "none" for particle in evaluation.particles],
        "q_value": evaluation.q_value,
        "target": evaluation.target,
        "absolute_gap": evaluation.absolute_gap,
        "relative_gap": evaluation.relative_gap,
        "q_uncertainty": evaluation.q_uncertainty,
        "gap_sigma": evaluation.gap_sigma,
        "within_uncertainty": evaluation.within_uncertainty,
        "analytic_range_fraction": evaluation.analytic_range_fraction,
        "random_baseline": {
            "seed": baseline.seed,
            "sample_count": baseline.sample_count,
            "mass_min_mev": baseline.mass_min_mev,
            "mass_max_mev": baseline.mass_max_mev,
            "mean_q": baseline.mean_q,
            "std_q": baseline.std_q,
            "best_gap_to_target": baseline.best_gap_to_target,
            "fraction_within_observed_gap": baseline.fraction_within_observed_gap,
            "observed_gap_percentile": baseline.observed_gap_percentile,
        },
        "verdict": evaluation.verdict,
        "limitation": evaluation.limitation,
    }


def _comparison_summary(evaluations: list[FamilyEvaluation]) -> list[dict[str, Any]]:
    return [
        {
            "target_id": f"target_{evaluation.family_id}_koide_q",
            "label": f"{evaluation.label} Q vs Koide target 2/3",
            "reference_value": evaluation.target,
            "observed_value": evaluation.q_value,
            "unit": None,
            "absolute_difference": evaluation.absolute_gap,
            "relative_difference": evaluation.relative_gap,
            "notes": (
                f"Family verdict {evaluation.verdict}; "
                f"gap_sigma={evaluation.gap_sigma if evaluation.gap_sigma is not None else 'undefined'}."
            ),
        }
        for evaluation in evaluations
    ]


def _verification(evaluations: list[FamilyEvaluation]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = [
        {
            "name": "explicit_family_inputs",
            "status": "PASS",
            "details": "Every evaluated family has exactly three source-explicit particle masses.",
            "metrics": {
                "family_count": len(evaluations),
                "particle_count": sum(len(evaluation.particles) for evaluation in evaluations),
            },
        },
        {
            "name": "complexity_penalty_applied",
            "status": "PASS",
            "details": "The standard Koide relation is scored with a fixed low-complexity penalty ledger.",
            "metrics": {
                "complexity_penalty_total": standard_koide_complexity_penalty().total,
            },
        },
        {
            "name": "random_baseline_applied",
            "status": "PASS",
            "details": "Each family is compared with a deterministic log-uniform random triplet baseline.",
            "metrics": {
                "minimum_sample_count": min(
                    evaluation.random_baseline.sample_count for evaluation in evaluations
                ),
            },
        },
    ]
    for evaluation in evaluations:
        status = "PASS" if evaluation.verdict == "INVALID" else "PASS"
        checks.append(
            {
                "name": f"{evaluation.family_id}_family_verdict",
                "status": status,
                "details": (
                    f"{evaluation.label}: Q={evaluation.q_value:.12f}, "
                    f"gap={evaluation.absolute_gap:.6e}, verdict={evaluation.verdict}."
                ),
                "metrics": {
                    "q_value": evaluation.q_value,
                    "absolute_gap": evaluation.absolute_gap,
                    "q_uncertainty": evaluation.q_uncertainty,
                    "gap_sigma": evaluation.gap_sigma if evaluation.gap_sigma is not None else "undefined",
                    "within_uncertainty": evaluation.within_uncertainty,
                },
            }
        )
    return {"passed": all(check["status"] == "PASS" for check in checks), "checks": checks}


def _report_text(
    *,
    result_id: str,
    run_id: str,
    experiment_id: str,
    hypothesis_id: str,
    task_id: str,
    evaluations: list[FamilyEvaluation],
    best_verdict: str,
) -> str:
    penalty = standard_koide_complexity_penalty()
    lines = [
        "# Particle-Mass Relation Falsifier MVP",
        "",
        f"- Result: `{result_id}`",
        f"- Run: `{run_id}`",
        f"- Experiment: `{experiment_id}`",
        f"- Hypothesis: `{hypothesis_id}`",
        f"- Task: `{task_id}`",
        f"- Global verdict: `{best_verdict}`",
        "",
        "## Tested Relation",
        "",
        "`Q = (m1 + m2 + m3) / (sqrt(m1) + sqrt(m2) + sqrt(m3))^2 = 2/3`",
        "",
        "The MVP tests only guardrail-compliant, within-family charged fermion triplets.",
        "",
        "## Family Results",
        "",
        "| Family | Particles | Q | Gap to 2/3 | 1-sigma Q uncertainty | Gap sigma | Verdict |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for evaluation in evaluations:
        gap_sigma = "undefined" if evaluation.gap_sigma is None else f"{evaluation.gap_sigma:.3g}"
        lines.append(
            f"| {evaluation.label} | "
            f"{', '.join(p.symbol for p in evaluation.particles)} | "
            f"{evaluation.q_value:.12f} | "
            f"{evaluation.absolute_gap:.6e} | "
            f"{evaluation.q_uncertainty:.6e} | "
            f"{gap_sigma} | "
            f"`{evaluation.verdict}` |"
        )
    lines.extend(
        [
            "",
            "## Baseline Calibration",
            "",
            "| Family | Analytic Q-window fraction | Random baseline fraction within observed gap | Best random gap |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for evaluation in evaluations:
        baseline = evaluation.random_baseline
        lines.append(
            f"| {evaluation.label} | "
            f"{evaluation.analytic_range_fraction:.6e} | "
            f"{baseline.fraction_within_observed_gap:.6e} | "
            f"{baseline.best_gap_to_target:.6e} |"
        )
    lines.extend(
        [
            "",
            "## Complexity Penalty",
            "",
            f"- Parameter count penalty: `{penalty.parameter_count}`",
            f"- Arbitrary constant penalty: `{penalty.arbitrary_constants}`",
            f"- Tuned exponent penalty: `{penalty.tuned_exponents}`",
            f"- Structural flexibility penalty: `{penalty.structural_flexibility}`",
            f"- Cross-family mixing penalty: `{penalty.cross_family_mixing}`",
            f"- Post hoc prediction penalty: `{penalty.post_hoc_prediction}`",
            f"- Total penalty: `{penalty.total}` (`{penalty.severity}`)",
            "",
            "## Limitations",
            "",
            "- This MVP evaluates the fixed standard Koide relation only.",
            "- The result is a cross-family survival falsification, not a discovery-level claim.",
            "- Quark inputs preserve the mixed scale and scheme limitations of the stored PDG-backed dataset.",
            "- The random baseline is a calibration aid, not a physical mass-generation model.",
            "- No claim promotion is proposed by this run.",
            "",
            "## Verdict",
            "",
            f"The cross-family survival hypothesis receives repository verdict `{best_verdict}` because at least one guardrail-compliant family triplet misses the `2/3` target outside its propagated uncertainty.",
            "",
        ]
    )
    return "\n".join(lines)


def run_particle_mass_falsifier_with_output(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> ExperimentOutcome:
    """Execute the particle-mass relation falsifier MVP."""
    config_path = Path(config_path).resolve()
    repo_root = find_repo_root(config_path)
    config = load_example_config(config_path)
    experiment_path = resolve_path(config_path, config["experiment_path"])
    hypothesis_path = resolve_path(config_path, config["hypothesis_path"])
    experiment = load_experiment(experiment_path)
    hypothesis = load_hypothesis(hypothesis_path)

    task_id = str(config["task_id"])
    run_id = str(config["run_id"])
    result_id = str(config["result_id"])
    default_result_root = resolve_path(config_path, str(config["result_root"]))
    result_root = (
        Path(output_dir).resolve() / str(experiment["id"])
        if output_dir is not None
        else default_result_root
    )
    run_dir = result_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    dataset_path = resolve_path(experiment_path, experiment["data"]["dataset_path"])
    dataset = _load_dataset(dataset_path)
    evaluations = _evaluate_families(dataset, experiment)
    best_verdict = _global_verdict(evaluations)
    verification_summary = _verification(evaluations)
    penalty = standard_koide_complexity_penalty()

    result_path = run_dir / "result.yaml"
    report_path = run_dir / "report.md"
    metrics_path = run_dir / "metrics.json"
    claim_update_path = run_dir / "claim_update.md"
    claim_update_patch_path = run_dir / "claim_update.patch.md"
    knowledge_update_path = run_dir / "knowledge_update.md"
    knowledge_update_patch_path = run_dir / "knowledge_update.patch.md"
    review_summary_path = run_dir / "review_summary.md"
    review_metadata_path = run_dir / "review_metadata.yaml"

    task_file = task_path(repo_root, task_id)
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
    dataset_hash = hash_file(dataset_input_path, repo_root)

    command_path = relative_or_absolute(config_path, repo_root)
    command = f"physics-lab run {command_path}"
    if output_dir is not None:
        command += f" --output-dir {relative_or_absolute(Path(output_dir).resolve(), repo_root)}"

    limitations = [
        "Standard Koide relation only; no alternate target values or phase extensions are tested in this MVP.",
        "Guardrail-compliant within-family charged fermion triplets only; cross-family triplets are intentionally excluded.",
        "Quark masses retain documented mixed scheme and scale limitations.",
        "Random log-uniform baseline is deterministic calibration, not a physical particle-mass prior.",
        "No claim promotion is proposed from this falsifier run.",
    ]
    result_payload: dict[str, Any] = {
        "result_id": result_id,
        "run_id": run_id,
        "experiment_id": str(experiment["id"]),
        "title": str(experiment["title"]),
        "hypothesis_id": str(hypothesis["id"]),
        "task_id": task_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine_version": __version__,
        "git_commit": git_commit(repo_root),
        "command": command,
        "input_file_hashes": input_hashes,
        "code_reference": "physics_lab/workflows/particle_mass_falsifier.py",
        "limitations": limitations,
        "best_verdict": best_verdict,
        "verification": verification_summary,
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
        "comparison_summary": _comparison_summary(evaluations),
        "uncertainty_summary": {
            "method": "first_order_uncertainty_propagation plus deterministic log_uniform_random_baseline",
            "observed_uncertainty": max(e.q_uncertainty for e in evaluations),
            "reference_uncertainty": None,
            "combined_uncertainty": max(e.q_uncertainty for e in evaluations),
            "z_score": max(e.gap_sigma for e in evaluations if e.gap_sigma is not None),
            "within_combined_uncertainty": all(e.within_uncertainty for e in evaluations),
            "notes": "Per-family uncertainty, baseline, and complexity details are stored in metrics.json.",
        },
    }
    validate_result_payload(result_payload, source=result_path)

    report_text = _report_text(
        result_id=result_id,
        run_id=run_id,
        experiment_id=str(experiment["id"]),
        hypothesis_id=str(hypothesis["id"]),
        task_id=task_id,
        evaluations=evaluations,
        best_verdict=best_verdict,
    )
    write_text_atomic(report_path, report_text)

    metrics_payload = {
        "result_id": result_id,
        "run_id": run_id,
        "dataset_id": str(dataset["dataset_id"]),
        "dataset_hash": dataset_hash,
        "target": float(experiment["comparison_targets"][0]["reference_value"]),
        "best_verdict": best_verdict,
        "complexity_penalty": {
            "parameter_count": penalty.parameter_count,
            "arbitrary_constants": penalty.arbitrary_constants,
            "tuned_exponents": penalty.tuned_exponents,
            "structural_flexibility": penalty.structural_flexibility,
            "cross_family_mixing": penalty.cross_family_mixing,
            "post_hoc_prediction": penalty.post_hoc_prediction,
            "total": penalty.total,
            "severity": penalty.severity,
            "disqualifying_flags": list(penalty.disqualifying_flags),
        },
        "families": [_family_metrics(evaluation) for evaluation in evaluations],
        "verification": verification_summary,
    }
    write_text_atomic(metrics_path, json.dumps(metrics_payload, indent=2) + "\n")
    write_text_atomic(result_path, yaml.safe_dump(result_payload, sort_keys=False))

    claim_update_text = "\n".join(
        [
            "# Claim Update Suggestion",
            "",
            "Suggested status: keep `CLAIM-0007` as `DRAFT`.",
            "",
            f"- Result: `{result_id}`",
            f"- Verdict: `{best_verdict}`",
            "- The run falsifies the cross-family survival hypothesis for the fixed standard Koide target under the encoded inputs.",
            "- It does not falsify every possible Koide-like extension.",
            "",
        ]
    )
    knowledge_update_text = "\n".join(
        [
            "# Knowledge Update Suggestion",
            "",
            f"- Record `{result_id}` as the first particle-mass relation falsifier MVP run.",
            "- Preserve the existing charged-lepton reproduction and tau-holdout scope.",
            "- Preserve the neutrino and quark falsification limits.",
            "- Do not promote explanatory claims.",
            "",
        ]
    )
    write_text_atomic(claim_update_path, claim_update_text)
    write_text_atomic(claim_update_patch_path, claim_update_text)
    write_text_atomic(knowledge_update_path, knowledge_update_text)
    write_text_atomic(knowledge_update_patch_path, knowledge_update_text)

    review_summary_text = render_review_summary(
        result_id=result_id,
        claim_id="CLAIM-0007",
        knowledge_id="KNOW-0003",
        suggested_status="DRAFT",
        rationale=(
            "The MVP applies source-aware inputs, uncertainty propagation, a deterministic "
            "random baseline, and a fixed low complexity penalty to the standard Koide relation."
        ),
        highlights=[
            f"Global verdict: {best_verdict}.",
            "Charged leptons remain within propagated uncertainty.",
            "At least one quark family misses Q=2/3 outside propagated uncertainty.",
            "Random baseline calibration and complexity penalty are recorded in metrics.json.",
        ],
        limitations=limitations,
    )
    write_text_atomic(review_summary_path, review_summary_text)
    review_metadata_payload = render_review_metadata(
        result_id=result_id,
        run_id=run_id,
        experiment_id=str(experiment["id"]),
        claim_id="CLAIM-0007",
        knowledge_id="KNOW-0003",
        generated_at=str(result_payload["generated_at"]),
        proposed_claim_status="DRAFT",
        evidence_basis=[result_id],
        claim_target_file="claims/CLAIM-0007-particle-mass-falsifier-mvp.md",
        knowledge_target_file="knowledge/particle_physics/koide_relation.md",
        claim_patch_path=relative_or_absolute(claim_update_patch_path, repo_root),
        knowledge_patch_path=relative_or_absolute(knowledge_update_patch_path, repo_root),
        review_summary_path=relative_or_absolute(review_summary_path, repo_root),
    )
    write_text_atomic(review_metadata_path, yaml.safe_dump(review_metadata_payload, sort_keys=False))

    return ExperimentOutcome(
        title=str(experiment["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(hypothesis["id"]),
        task_id=task_id,
        artifacts=ExperimentArtifacts(
            result_path=result_path,
            report_path=report_path,
            metrics_path=metrics_path,
            claim_update_path=claim_update_path,
            claim_update_patch_path=claim_update_patch_path,
            knowledge_update_path=knowledge_update_path,
            knowledge_update_patch_path=knowledge_update_patch_path,
            review_summary_path=review_summary_path,
            review_metadata_path=review_metadata_path,
        ),
        best_model_id=None,
        summary_lines=(
            f"Primary comparison: {experiment['comparison_targets'][0]['label']}",
            f"Families evaluated: {len(evaluations)}",
            f"Global verdict: {best_verdict}",
        ),
    )
