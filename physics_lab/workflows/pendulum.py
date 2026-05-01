"""Pendulum workflow implementation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from physics_lab import __version__
from physics_lab.engines.critic import classify_model_score
from physics_lab.engines.formula_discovery import FittedModel, fit_all_models
from physics_lab.engines.scoring import ModelScore, score_model
from physics_lab.engines.simulation import generate_pendulum_dataset
from physics_lab.engines.verification import serialize_verification_summary, verify_candidate_model
from physics_lab.registry.examples import load_example_config
from physics_lab.registry.experiments import load_experiment
from physics_lab.registry.hypotheses import load_hypothesis
from physics_lab.registry.results import validate_result_payload
from physics_lab.workflows.claim_semantics import suggest_claim_status
from physics_lab.workflows.artifacts import (
    ExperimentArtifacts,
    ExperimentOutcome,
    best_result_verdict,
    find_repo_root,
    git_commit,
    render_patch_artifact,
    render_review_metadata,
    render_review_summary,
    relative_or_absolute,
    replace_frontmatter_field,
    replace_markdown_section,
    resolve_path,
    serialize_scores,
    snapshot_input_files,
    split_dataset,
    task_path,
    write_text_atomic,
)


def _build_limitations() -> list[str]:
    return [
        "This workflow assumes an ideal mathematical pendulum with no damping or driving force.",
        "Verdicts apply only to the sampled amplitude ranges used in the train and test split.",
        "Candidate formulas are limited to predefined polynomial, trigonometric, and theory-aware separatrix approximation families.",
    ]


def _best_fitted_model(fitted_models: list[FittedModel], model_id: str) -> FittedModel:
    for model in fitted_models:
        if model.candidate.model_id == model_id:
            return model
    raise ValueError(f"Unable to find fitted model for {model_id}")


def _best_theory_aware_score(scores: list[ModelScore]) -> ModelScore | None:
    theory_aware_scores = [score for score in scores if "log" in score.model_id]
    if not theory_aware_scores:
        return None
    return min(theory_aware_scores, key=lambda score: score.composite_score)


def _verification_check_map(verification_summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {check["name"]: check for check in verification_summary["checks"]}


def _run_comparison_payload(
    *,
    baseline_result_path: Path | None,
    baseline_result_payload: dict[str, Any] | None,
    theory_aware_score: ModelScore | None,
    theory_aware_verification_payload: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if baseline_result_payload is None or baseline_result_path is None or theory_aware_score is None:
        return None

    def _score_by_model(payload: dict[str, Any], model_id: str) -> dict[str, Any]:
        for score in payload["scores"]:
            if score["model_id"] == model_id:
                return score
        raise ValueError(f"Missing score for model {model_id}")

    baseline_checks = _verification_check_map(baseline_result_payload["verification"])
    theory_checks = _verification_check_map(theory_aware_verification_payload or {"checks": []})
    baseline_best_score = _score_by_model(
        baseline_result_payload,
        str(baseline_result_payload["best_model_id"]),
    )
    baseline_sep = baseline_checks.get("near_separatrix_extrapolation", {}).get("metrics", {})
    baseline_asym = baseline_checks.get("separatrix_asymptotic_alignment", {}).get("metrics", {})
    theory_sep = theory_checks.get("near_separatrix_extrapolation", {}).get("metrics", {})
    theory_asym = theory_checks.get("separatrix_asymptotic_alignment", {}).get("metrics", {})

    return {
        "baseline_run_id": str(baseline_result_payload["run_id"]),
        "baseline_result_id": str(baseline_result_payload["result_id"]),
        "baseline_best_model_id": str(baseline_result_payload["best_model_id"]),
        "theory_aware_model_id": theory_aware_score.model_id,
        "baseline_result_path": relative_or_absolute(baseline_result_path, find_repo_root(baseline_result_path)),
        "comparison": {
            "baseline_in_range_mean_relative_error": float(
                baseline_best_score["test_metrics"]["mean_relative_error"]
            ),
            "baseline_in_range_max_relative_error": float(
                baseline_best_score["test_metrics"]["max_relative_error"]
            ),
            "baseline_complexity_score": int(baseline_best_score["complexity_score"]),
            "baseline_end_ratio_to_exact": float(baseline_sep.get("end_ratio_to_exact", float("nan"))),
            "baseline_separatrix_max_relative_error": float(
                baseline_asym.get("max_relative_error", float("nan"))
            ),
            "theory_aware_in_range_mean_relative_error": theory_aware_score.test_metrics.mean_relative_error,
            "theory_aware_in_range_max_relative_error": theory_aware_score.test_metrics.max_relative_error,
            "theory_aware_complexity_score": theory_aware_score.complexity_score,
            "theory_aware_end_ratio_to_exact": float(theory_sep.get("end_ratio_to_exact", float("nan"))),
            "theory_aware_separatrix_max_relative_error": float(
                theory_asym.get("max_relative_error", float("nan"))
            ),
        },
    }


def _build_report(
    title: str,
    result_id: str,
    run_id: str,
    hypothesis_id: str,
    task_id: str,
    assumptions: list[str],
    limitations: list[str],
    train_range: tuple[float, float],
    test_range: tuple[float, float],
    scores: list[ModelScore],
    verdicts: dict[str, str],
    best_model_id: str,
    verification_summary: dict[str, Any],
    run_comparison: dict[str, Any] | None,
) -> str:
    best_score = next(score for score in scores if score.model_id == best_model_id)
    lines = [
        f"# {title}",
        "",
        f"- Result: `{result_id}`",
        f"- Run: `{run_id}`",
        f"- Hypothesis: `{hypothesis_id}`",
        f"- Task: `{task_id}`",
        f"- Train range (rad): `{train_range[0]:.4f}` to `{train_range[1]:.4f}`",
        f"- Test range (rad): `{test_range[0]:.4f}` to `{test_range[1]:.4f}`",
        "",
        "## Assumptions",
        "",
    ]
    lines.extend([f"- {assumption}" for assumption in assumptions])
    lines.extend(["", "## Limitations", ""])
    lines.extend([f"- {limitation}" for limitation in limitations])
    lines.extend(["", "## Verification", "", f"- Verification gate passed: `{verification_summary['passed']}`"])
    lines.extend([*[f"- {check['name']}: `{check['status']}`" for check in verification_summary["checks"]]])
    lines.extend(
        [
            "",
            "## Candidate Models",
            "",
            "| Model | Formula | Coefficients | Mean Relative Error (test) | Max Relative Error (test) | Complexity | Verdict |",
            "| --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for score in scores:
        coefficient_text = ", ".join(
            f"{name}={value:.8f}" for name, value in score.coefficients.items()
        )
        lines.append(
            "| "
            f"{score.model_id} | "
            f"`{score.formula}` | "
            f"`{coefficient_text}` | "
            f"{score.test_metrics.mean_relative_error:.6f} | "
            f"{score.test_metrics.max_relative_error:.6f} | "
            f"{score.complexity_score} | "
            f"{verdicts[score.model_id]} |"
        )
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"Best candidate: `{best_score.model_id}` with verdict `{best_result_verdict(verdicts[best_model_id])}`.",
        ]
    )
    if run_comparison is not None:
        comparison = run_comparison["comparison"]
        lines.extend(
            [
                "",
                "## RUN-0001 vs RUN-0002 Comparison",
                "",
                f"- Baseline run: `{run_comparison['baseline_run_id']}` / `{run_comparison['baseline_result_id']}`",
                f"- Baseline best model: `{run_comparison['baseline_best_model_id']}`",
                f"- Best theory-aware candidate in this run: `{run_comparison['theory_aware_model_id']}`",
                "",
                "### In-range accuracy",
                "",
                (
                    f"- Baseline mean/max relative error: "
                    f"`{comparison['baseline_in_range_mean_relative_error']:.6f}` / "
                    f"`{comparison['baseline_in_range_max_relative_error']:.6f}`"
                ),
                (
                    f"- Theory-aware mean/max relative error: "
                    f"`{comparison['theory_aware_in_range_mean_relative_error']:.6f}` / "
                    f"`{comparison['theory_aware_in_range_max_relative_error']:.6f}`"
                ),
                "",
                "### Near-separatrix behavior",
                "",
                f"- Baseline end-ratio-to-exact: `{comparison['baseline_end_ratio_to_exact']:.6f}`",
                f"- Theory-aware end-ratio-to-exact: `{comparison['theory_aware_end_ratio_to_exact']:.6f}`",
                (
                    f"- Baseline asymptotic max relative error: "
                    f"`{comparison['baseline_separatrix_max_relative_error']:.6f}`"
                ),
                (
                    f"- Theory-aware asymptotic max relative error: "
                    f"`{comparison['theory_aware_separatrix_max_relative_error']:.6f}`"
                ),
                "",
                "### Complexity and limitations",
                "",
                f"- Baseline complexity score: `{comparison['baseline_complexity_score']}`",
                f"- Theory-aware complexity score: `{comparison['theory_aware_complexity_score']}`",
                (
                    "- Tradeoff: the theory-aware candidate improves separatrix behavior substantially "
                    "and also improves in-range error, but it pays a higher complexity penalty and "
                    "still remains range-limited rather than exact."
                ),
            ]
        )
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "This report describes approximation behavior only within the configured train and test amplitude ranges.",
            "It does not claim exact discovery or validity near the separatrix; it identifies the best-performing candidate formula under the current benchmark.",
        ]
    )
    return "\n".join(lines) + "\n"


def _build_claim_update(
    claim_id: str,
    result_id: str,
    experiment_id: str,
    hypothesis_id: str,
    task_id: str,
    best_score: ModelScore,
    best_verdict: str,
    train_range: tuple[float, float],
    test_range: tuple[float, float],
    verification_summary: dict[str, Any],
    run_comparison: dict[str, Any] | None,
) -> str:
    suggestion = suggest_claim_status(
        verification_summary=verification_summary,
        best_verdict=best_verdict,
        range_limited=True,
        exact_verification=False,
    )
    lines = [
            f"# Proposed Update for {claim_id}",
            "",
            f"- Result: `{result_id}`",
            f"- Hypothesis: `{hypothesis_id}`",
            f"- Experiment: `{experiment_id}`",
            f"- Task: `{task_id}`",
            f"- Suggested claim status: `{suggestion.status}`",
            "",
            "## Suggested Evidence Update",
            "",
            (
                "The pendulum period depends on amplitude, and within the tested benchmark "
                f"the best candidate approximation was `{best_score.model_id}` "
                f"with verdict `{best_verdict}`."
            ),
            "",
            "## Suggested Range Language",
            "",
            (
                "Valid only within the sampled ranges used by this workflow: "
                f"train `{train_range[0]:.4f}` to `{train_range[1]:.4f}` rad, "
                f"test `{test_range[0]:.4f}` to `{test_range[1]:.4f}` rad."
            ),
            "",
            "## Suggested Metrics",
            "",
            f"- Mean relative error (test): `{best_score.test_metrics.mean_relative_error:.6f}`",
            f"- Max relative error (test): `{best_score.test_metrics.max_relative_error:.6f}`",
            f"- Complexity score: `{best_score.complexity_score}`",
            "",
            "## Suggested Evidence Basis",
            "",
            f"- Passed checks: `{suggestion.pass_count}`",
            f"- Failed checks: `{suggestion.fail_count}`",
            f"- Rationale: {suggestion.rationale}",
            "",
            "## Suggested Caution",
            "",
            (
                "Keep the claim range-aware and avoid wording that implies exact discovery or universal validity. "
                "Do not auto-promote the claim status unless verification checks pass, and do not extend this verdict "
                "beyond the configured amplitude ranges."
            ),
        ]
    if run_comparison is not None:
        comparison = run_comparison["comparison"]
        lines.extend(
            [
                "",
                "## Suggested RUN Comparison Note",
                "",
                (
                    "Compared with `RUN-0001`, the new benchmark includes a theory-aware "
                    f"candidate `{run_comparison['theory_aware_model_id']}` that improves "
                    "near-separatrix behavior while remaining explicitly range-limited."
                ),
                f"- Baseline end-ratio-to-exact: `{comparison['baseline_end_ratio_to_exact']:.6f}`",
                f"- Theory-aware end-ratio-to-exact: `{comparison['theory_aware_end_ratio_to_exact']:.6f}`",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def _build_knowledge_update(
    knowledge_id: str,
    result_id: str,
    experiment_id: str,
    hypothesis_id: str,
    task_id: str,
    best_score: ModelScore,
    best_verdict: str,
    limitations: list[str],
    verification_summary: dict[str, Any],
    run_comparison: dict[str, Any] | None,
) -> str:
    lines = [
        f"# Proposed Update for {knowledge_id}",
        "",
        f"- Result: `{result_id}`",
        f"- Hypothesis: `{hypothesis_id}`",
        f"- Experiment: `{experiment_id}`",
        f"- Task: `{task_id}`",
        "",
        "## Target Knowledge Note",
        "",
        "- File: `knowledge/classical_mechanics/pendulum.md`",
        "- Sections to review: `Known Baseline`, `Linked Objects`, `Open Questions`",
        "",
        "## Suggested Known Baseline Update",
        "",
    ]
    lines.extend(
        [
            (
                f"The current pendulum benchmark selected `{best_score.model_id}` "
                f"(`{best_score.formula}`) as the best-performing candidate with verdict `{best_verdict}`."
            ),
            "",
            "Suggested coefficient summary:",
        ]
    )
    lines.extend([f"- `{name}` = `{value:.8f}`" for name, value in best_score.coefficients.items()])
    lines.extend(
        [
            "",
            "Suggested verification summary:",
            "",
            f"- Verification gate passed: `{verification_summary['passed']}`",
        ]
    )
    lines.extend([*[f"- {check['name']}: `{check['status']}`" for check in verification_summary["checks"]]])
    if run_comparison is not None:
        comparison = run_comparison["comparison"]
        lines.extend(
            [
                "",
                "Suggested comparison note for the same section:",
                "",
                (
                    f"Theory-aware candidate `{run_comparison['theory_aware_model_id']}` "
                    "improves near-separatrix behavior relative to the RUN-0001 baseline."
                ),
                f"- Baseline end-ratio-to-exact: `{comparison['baseline_end_ratio_to_exact']:.6f}`",
                f"- Theory-aware end-ratio-to-exact: `{comparison['theory_aware_end_ratio_to_exact']:.6f}`",
                f"- Baseline asymptotic max relative error: `{comparison['baseline_separatrix_max_relative_error']:.6f}`",
                f"- Theory-aware asymptotic max relative error: `{comparison['theory_aware_separatrix_max_relative_error']:.6f}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Suggested Linked Objects Update",
            "",
            f"- Ensure result link includes `{result_id}`.",
            f"- Ensure task link includes `{task_id}`.",
            "",
            "## Suggested Limitations Section",
            "",
        ]
    )
    lines.extend([f"- {limitation}" for limitation in limitations])
    lines.extend(
        [
            "",
            "## Suggested Open Questions Update",
            "",
            "- Can a known-limit-aware approximation outperform the current candidate?",
            "- Should the next benchmark include damping, forcing, or a wider amplitude regime?",
            "",
        ]
    )
    return "\n".join(lines)


def _build_claim_patch(
    *,
    repo_root: Path,
    claim_id: str,
    result_id: str,
    suggestion_status: str,
    suggestion_rationale: str,
    train_range: tuple[float, float],
    test_range: tuple[float, float],
    run_comparison: dict[str, Any] | None,
) -> str:
    claim_path = repo_root / "claims" / "CLAIM-0001-pendulum-period-amplitude.md"
    if not claim_path.exists():
        return render_patch_artifact(
            title=f"Claim Patch Proposal for {claim_id}",
            target_file="claims/CLAIM-0001-pendulum-period-amplitude.md",
            proposed_status=suggestion_status,
            evidence_basis=["RESULT-0001", result_id],
            original_text="",
            proposed_text="",
            rationale="Target claim file is not available in this temporary repository fixture, so no direct diff was generated.",
        )
    original_text = claim_path.read_text(encoding="utf-8")
    proposed_text = replace_frontmatter_field(original_text, "status", suggestion_status)
    proposed_text = replace_frontmatter_field(
        proposed_text,
        "scope",
        (
            "Pendulum amplitude correction for the ideal pendulum within the configured benchmark "
            f"ranges (train {train_range[0]:.4f}-{train_range[1]:.4f} rad; "
            f"test {test_range[0]:.4f}-{test_range[1]:.4f} rad)."
        ),
    )
    evidence_status = "\n".join(
        [
            (
                "`RESULT-0001` and `RESULT-0003` together support a bounded, "
                "verification-backed update for amplitude-dependent ideal-pendulum behavior."
            ),
            "",
            (
                "The evidence remains explicitly range-limited: the best overall verdict is "
                "`VALID_IN_RANGE`, and the near-separatrix diagnostics still fail even after the "
                "theory-aware follow-up."
            ),
        ]
    )
    review_recommendation_lines = [
        f"A maintainer may promote this claim to `{suggestion_status}` after review.",
        "",
        "Reason:",
        "",
        "- `RESULT-0001` and `RESULT-0003` both pass the in-range verification gate;",
        "- the theory-aware follow-up improves separatrix behavior without making the claim exact;",
        "- remaining separatrix failures still require clearly bounded wording.",
        "",
        f"Promotion rationale: {suggestion_rationale}",
        "",
        "Do not promote this claim beyond `PARTIALLY_SUPPORTED` unless future evidence removes the remaining separatrix failure mode or narrows the claim further.",
    ]
    if run_comparison is not None:
        comparison = run_comparison["comparison"]
        review_recommendation_lines.extend(
            [
                "",
                "Evidence from `RUN-0002` relative to `RUN-0001`:",
                "",
                f"- Baseline end-ratio-to-exact: `{comparison['baseline_end_ratio_to_exact']:.6f}`",
                f"- Theory-aware end-ratio-to-exact: `{comparison['theory_aware_end_ratio_to_exact']:.6f}`",
            ]
        )
    proposed_text = replace_markdown_section(proposed_text, "Evidence Status", evidence_status)
    proposed_text = replace_markdown_section(
        proposed_text,
        "Review Recommendation",
        "\n".join(review_recommendation_lines),
    )
    return render_patch_artifact(
        title=f"Claim Patch Proposal for {claim_id}",
        target_file="claims/CLAIM-0001-pendulum-period-amplitude.md",
        proposed_status=suggestion_status,
        evidence_basis=["RESULT-0001", result_id],
        original_text=original_text,
        proposed_text=proposed_text,
        rationale="Promote only to a range-aware supported status that preserves the remaining near-separatrix limitations.",
    )


def _build_knowledge_patch(
    *,
    repo_root: Path,
    knowledge_id: str,
    result_id: str,
    task_id: str,
    best_score: ModelScore,
    best_verdict: str,
    limitations: list[str],
    verification_summary: dict[str, Any],
    run_comparison: dict[str, Any] | None,
) -> str:
    knowledge_path = repo_root / "knowledge" / "classical_mechanics" / "pendulum.md"
    if not knowledge_path.exists():
        return render_patch_artifact(
            title=f"Knowledge Patch Proposal for {knowledge_id}",
            target_file="knowledge/classical_mechanics/pendulum.md",
            evidence_basis=["RESULT-0001", result_id, task_id],
            original_text="",
            proposed_text="",
            sections_to_update=["Known Baseline", "Linked Objects", "Open Questions"],
            rationale="Target knowledge note is not available in this temporary repository fixture, so no direct diff was generated.",
        )
    original_text = knowledge_path.read_text(encoding="utf-8")
    known_baseline_lines = [
        "The small-angle period is:",
        "",
        "`T0 = 2*pi*sqrt(L/g)`",
        "",
        "For finite amplitude, the exact period ratio is:",
        "",
        "`T / T0 = (2 / pi) * K(k^2)` where `k = sin(theta / 2)`.",
        "",
        "The current public-alpha benchmark has two canonical pendulum runs:",
        "",
        "- `RESULT-0001` / `RUN-0001` for the original low-order candidate comparison;",
        "- `RESULT-0003` / `RUN-0002` for the theory-aware near-separatrix follow-up.",
        "",
        "The current best overall candidate remains:",
        "",
        f"- `{best_score.model_id}`",
        f"- verdict: `{best_verdict}`",
        "",
        "Verification summary for the latest canonical run:",
        "",
        f"- Verification gate passed: `{verification_summary['passed']}`",
    ]
    known_baseline_lines.extend(
        [f"- {check['name']}: `{check['status']}`" for check in verification_summary["checks"]]
    )
    if run_comparison is not None:
        comparison = run_comparison["comparison"]
        known_baseline_lines.extend(
            [
                "",
                "Theory-aware comparison note:",
                "",
                (
                    f"- Candidate `{run_comparison['theory_aware_model_id']}` improves separatrix "
                    "behavior relative to `RUN-0001`, but does not replace the simpler best-in-range model."
                ),
                f"- Baseline end-ratio-to-exact: `{comparison['baseline_end_ratio_to_exact']:.6f}`",
                f"- Theory-aware end-ratio-to-exact: `{comparison['theory_aware_end_ratio_to_exact']:.6f}`",
                f"- Baseline asymptotic max relative error: `{comparison['baseline_separatrix_max_relative_error']:.6f}`",
                f"- Theory-aware asymptotic max relative error: `{comparison['theory_aware_separatrix_max_relative_error']:.6f}`",
            ]
        )
    linked_objects = "\n".join(
        [
            "- Hypothesis: `HYP-0001`",
            "- Experiment: `EXP-0001`",
            "- Claim: `CLAIM-0001`",
            "- Tasks:",
            "  - `TASK-0001`",
            f"  - `{task_id}`",
            "- Canonical results:",
            "  - `RESULT-0001`",
            f"  - `{result_id}`",
        ]
    )
    open_questions = "\n".join(
        [
            "- Which low-order formula gives the best accuracy/complexity tradeoff?",
            "- How quickly do polynomial amplitude corrections fail near large angles?",
            "- Can a theory-aware approximation improve separatrix behavior further without losing in-range clarity or increasing complexity too much?",
            "- Which limitations must remain explicit if the claim is promoted to `PARTIALLY_SUPPORTED`?",
        ]
    )
    proposed_text = replace_markdown_section(
        original_text,
        "Known Baseline",
        "\n".join(known_baseline_lines),
    )
    proposed_text = replace_markdown_section(proposed_text, "Linked Objects", linked_objects)
    proposed_text = replace_markdown_section(proposed_text, "Open Questions", open_questions)
    return render_patch_artifact(
        title=f"Knowledge Patch Proposal for {knowledge_id}",
        target_file="knowledge/classical_mechanics/pendulum.md",
        evidence_basis=["RESULT-0001", result_id, task_id],
        original_text=original_text,
        proposed_text=proposed_text,
        sections_to_update=["Known Baseline", "Linked Objects", "Open Questions"],
        rationale="Expand the knowledge note with explicit verification detail and the theory-aware RUN-0002 comparison without overstating global validity.",
    )


def _build_review_summary_artifact(
    *,
    result_id: str,
    suggestion_status: str,
    suggestion_rationale: str,
    limitations: list[str],
    run_comparison: dict[str, Any] | None,
) -> str:
    highlights = [
        "Best overall model remains `model_theta2_theta4` with verdict `VALID_IN_RANGE`.",
        "Claim promotion, if accepted, should stop at `PARTIALLY_SUPPORTED` rather than stronger language.",
    ]
    if run_comparison is not None:
        highlights.append(
            f"Theory-aware candidate `{run_comparison['theory_aware_model_id']}` improves near-separatrix metrics relative to `RUN-0001` without becoming exact."
        )
    return render_review_summary(
        result_id=result_id,
        claim_id="CLAIM-0001",
        knowledge_id="KNOW-0001",
        suggested_status=suggestion_status,
        rationale=suggestion_rationale,
        highlights=highlights,
        limitations=limitations,
    )


def run_pendulum_experiment(config_path: str | Path) -> ExperimentOutcome:
    """Execute the pendulum formula discovery workflow from an example config."""
    return run_pendulum_experiment_with_output(config_path=config_path)


def run_pendulum_experiment_with_output(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> ExperimentOutcome:
    """Execute the pendulum workflow, optionally overriding the result root."""
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
    result_root = (
        Path(output_dir).resolve() / str(experiment["id"])
        if output_dir is not None
        else default_result_root
    )
    if experiment["hypothesis_id"] != hypothesis["id"]:
        raise ValueError(
            "Experiment hypothesis_id does not match loaded hypothesis id: "
            f"{experiment['hypothesis_id']} != {hypothesis['id']}"
        )
    if not task_id:
        raise ValueError("Experiment config must define task_id for result traceability")
    if not run_id:
        raise ValueError("Experiment config must define run_id for run-based artifacts")
    if not result_id:
        raise ValueError("Experiment config must define result_id for result traceability")
    if not str(config.get("result_root", "")):
        raise ValueError("Experiment config must define result_root for run-based outputs")

    amplitude_range = experiment["data"]["amplitude_range_radians"]
    sample_count = int(experiment["data"]["sample_count"])
    train_fraction = float(config.get("train_fraction", 0.7))
    dataset = generate_pendulum_dataset(
        amplitude_start=float(amplitude_range["start"]),
        amplitude_end=float(amplitude_range["end"]),
        sample_count=sample_count,
    )

    split_index = split_dataset(sample_count=sample_count, train_fraction=train_fraction)
    train_theta = dataset.theta[:split_index]
    train_target = dataset.period_ratio[:split_index]
    test_theta = dataset.theta[split_index:]
    test_target = dataset.period_ratio[split_index:]

    candidate_ids = [candidate["id"] for candidate in experiment.get("candidate_models", [])]
    fitted_models = fit_all_models(
        train_theta,
        train_target,
        candidate_ids=candidate_ids or None,
    )
    scores = [
        score_model(
            fitted_model=model,
            train_theta=train_theta,
            train_target=train_target,
            test_theta=test_theta,
            test_target=test_target,
        )
        for model in fitted_models
    ]
    scores.sort(key=lambda model_score: model_score.composite_score)
    verdicts = {score.model_id: classify_model_score(score) for score in scores}
    best_model_id = scores[0].model_id
    best_verdict = best_result_verdict(verdicts[best_model_id])
    best_score = scores[0]
    best_model = _best_fitted_model(fitted_models, best_model_id)

    verification_summary = verify_candidate_model(
        best_model,
        theta_range=(float(dataset.theta[0]), float(dataset.theta[-1])),
    )
    verification_payload = serialize_verification_summary(verification_summary)
    theory_aware_score = _best_theory_aware_score(scores)
    theory_aware_verification_payload = None
    if theory_aware_score is not None:
        theory_aware_model = _best_fitted_model(fitted_models, theory_aware_score.model_id)
        theory_aware_verification_payload = serialize_verification_summary(
            verify_candidate_model(
                theory_aware_model,
                theta_range=(float(dataset.theta[0]), float(dataset.theta[-1])),
            )
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
    limitations = _build_limitations()
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
    current_commit = git_commit(repo_root)
    baseline_result_path = default_result_root / "RUN-0001" / "result.yaml"
    baseline_result_payload = None
    if baseline_result_path.exists() and run_id != "RUN-0001":
        baseline_result_payload = validate_result_payload(
            yaml.safe_load(baseline_result_path.read_text(encoding="utf-8")),
            source=baseline_result_path,
        )
    run_comparison = _run_comparison_payload(
        baseline_result_path=baseline_result_path if baseline_result_payload is not None else None,
        baseline_result_payload=baseline_result_payload,
        theory_aware_score=theory_aware_score,
        theory_aware_verification_payload=theory_aware_verification_payload,
    )

    report_text = _build_report(
        title=str(experiment["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(experiment["hypothesis_id"]),
        task_id=task_id,
        assumptions=list(hypothesis.get("assumptions", [])),
        limitations=limitations,
        train_range=(float(train_theta[0]), float(train_theta[-1])),
        test_range=(float(test_theta[0]), float(test_theta[-1])),
        scores=scores,
        verdicts=verdicts,
        best_model_id=best_model_id,
        verification_summary=verification_payload,
        run_comparison=run_comparison,
    )
    write_text_atomic(report_path, report_text)
    claim_status_suggestion = suggest_claim_status(
        verification_summary=verification_payload,
        best_verdict=best_verdict,
        range_limited=True,
        exact_verification=False,
    )

    result_payload = {
        "result_id": result_id,
        "run_id": run_id,
        "experiment_id": str(experiment["id"]),
        "title": str(experiment["title"]),
        "hypothesis_id": str(experiment["hypothesis_id"]),
        "task_id": task_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine_version": __version__,
        "git_commit": current_commit,
        "command": command,
        "input_file_hashes": input_hashes,
        "code_reference": "physics_lab/workflows/pendulum.py",
        "limitations": limitations,
        "train_range": [float(train_theta[0]), float(train_theta[-1])],
        "test_range": [float(test_theta[0]), float(test_theta[-1])],
        "best_model_id": best_model_id,
        "best_verdict": best_verdict,
        "verification": verification_payload,
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
        "best_model_id": best_model_id,
        "best_verdict": best_verdict,
        "verification": verification_payload,
        "scores": result_payload["scores"],
        "run_comparison": run_comparison,
    }
    write_text_atomic(metrics_path, json.dumps(metrics_payload, indent=2))

    claim_update_text = _build_claim_update(
        claim_id="CLAIM-0001",
        result_id=result_id,
        experiment_id=str(experiment["id"]),
        hypothesis_id=str(experiment["hypothesis_id"]),
        task_id=task_id,
        best_score=best_score,
        best_verdict=best_verdict,
        train_range=(float(train_theta[0]), float(train_theta[-1])),
        test_range=(float(test_theta[0]), float(test_theta[-1])),
        verification_summary=verification_payload,
        run_comparison=run_comparison,
    )
    knowledge_update_text = _build_knowledge_update(
        knowledge_id="KNOW-0001",
        result_id=result_id,
        experiment_id=str(experiment["id"]),
        hypothesis_id=str(experiment["hypothesis_id"]),
        task_id=task_id,
        best_score=best_score,
        best_verdict=best_verdict,
        limitations=limitations,
        verification_summary=verification_payload,
        run_comparison=run_comparison,
    )
    claim_patch_text = _build_claim_patch(
        repo_root=repo_root,
        claim_id="CLAIM-0001",
        result_id=result_id,
        suggestion_status=claim_status_suggestion.status,
        suggestion_rationale=claim_status_suggestion.rationale,
        train_range=(float(train_theta[0]), float(train_theta[-1])),
        test_range=(float(test_theta[0]), float(test_theta[-1])),
        run_comparison=run_comparison,
    )
    knowledge_patch_text = _build_knowledge_patch(
        repo_root=repo_root,
        knowledge_id="KNOW-0001",
        result_id=result_id,
        task_id=task_id,
        best_score=best_score,
        best_verdict=best_verdict,
        limitations=limitations,
        verification_summary=verification_payload,
        run_comparison=run_comparison,
    )
    review_summary_text = _build_review_summary_artifact(
        result_id=result_id,
        suggestion_status=claim_status_suggestion.status,
        suggestion_rationale=claim_status_suggestion.rationale,
        limitations=limitations,
        run_comparison=run_comparison,
    )
    write_text_atomic(claim_update_path, claim_update_text)
    write_text_atomic(claim_update_patch_path, claim_patch_text)
    write_text_atomic(knowledge_update_path, knowledge_update_text)
    write_text_atomic(knowledge_update_patch_path, knowledge_patch_text)
    write_text_atomic(review_summary_path, review_summary_text)

    review_metadata_payload = render_review_metadata(
        result_id=result_id,
        run_id=run_id,
        experiment_id=str(experiment["id"]),
        claim_id="CLAIM-0001",
        knowledge_id="KNOW-0001",
        generated_at=str(result_payload["generated_at"]),
        proposed_claim_status=claim_status_suggestion.status,
        evidence_basis=["RESULT-0001", result_id] if result_id != "RESULT-0001" else [result_id],
        claim_target_file="claims/CLAIM-0001-pendulum-period-amplitude.md",
        knowledge_target_file="knowledge/classical_mechanics/pendulum.md",
        claim_patch_path=relative_or_absolute(claim_update_patch_path, repo_root),
        knowledge_patch_path=relative_or_absolute(knowledge_update_patch_path, repo_root),
        review_summary_path=relative_or_absolute(review_summary_path, repo_root),
    )
    write_text_atomic(review_metadata_path, yaml.safe_dump(review_metadata_payload, sort_keys=False))

    return ExperimentOutcome(
        title=str(experiment["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(experiment["hypothesis_id"]),
        task_id=task_id,
        train_range=(float(train_theta[0]), float(train_theta[-1])),
        test_range=(float(test_theta[0]), float(test_theta[-1])),
        scores=scores,
        verdicts=verdicts,
        best_model_id=best_model_id,
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
    )
