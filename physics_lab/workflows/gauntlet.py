"""Gauntlet workflow: run deterministic pendulum candidates and rank them."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from physics_lab import __version__
from physics_lab.engines.critic import classify_model_score
from physics_lab.engines.formula_discovery import fit_candidate_model
from physics_lab.engines.gauntlet import (
    atom_family,
    build_asymptotic_refined_candidate,
    build_constrained_candidate,
    build_gauntlet_candidates,
    classify_failure_mode,
)
from physics_lab.engines.scoring import ModelScore, score_model
from physics_lab.engines.simulation import generate_pendulum_dataset
from physics_lab.engines.verification import serialize_verification_summary, verify_candidate_model
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
    replace_frontmatter_field,
    replace_markdown_section,
    resolve_path,
    serialize_scores,
    snapshot_input_files,
    split_dataset,
    task_path,
    write_text_atomic,
)
from physics_lab.workflows.claim_semantics import suggest_claim_status


def _committed_git_commit(repo_root: Path) -> str | None:
    """Return HEAD SHA only when physics_lab/workflows/gauntlet.py is tracked in git.

    Returns None during bootstrap runs where the gauntlet code is not yet committed,
    so canonical artifacts never claim a SHA that predates this implementation.
    """
    try:
        r = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "physics_lab/workflows/gauntlet.py"],
            cwd=repo_root,
            capture_output=True,
            check=False,
        )
        if r.returncode != 0:
            return None
    except Exception:
        return None
    return git_commit(repo_root)


_GAUNTLET_LIMITATIONS = [
    "This workflow evaluates an ideal mathematical pendulum with no damping or driving force.",
    "Core gauntlet candidates are linear-in-coefficients models fitted by least squares.",
    "Verdicts apply only to the configured train and test amplitude ranges.",
    "Core candidates are drawn from a configured fixed atom basis; other functional forms are not tested unless explicitly configured.",
    "Configured comparison candidates expand the evaluated set but do not make the search exhaustive.",
    "The leaderboard ranks by composite score; top candidates may still fail separatrix diagnostics.",
]


def _build_leaderboard_entry(
    rank: int,
    score: ModelScore,
    atoms: tuple[str, ...],
    verdict: str,
) -> dict[str, Any]:
    return {
        "rank": rank,
        "model_id": score.model_id,
        "formula": score.formula,
        "family": atom_family(atoms),
        "atoms": list(atoms),
        "complexity_score": score.complexity_score,
        "test_mean_relative_error": score.test_metrics.mean_relative_error,
        "test_max_relative_error": score.test_metrics.max_relative_error,
        "train_mean_relative_error": score.train_metrics.mean_relative_error,
        "composite_score": score.composite_score,
        "verdict": verdict,
        "failure_mode": classify_failure_mode(score),
    }


def _build_leaderboard_md(
    entries: list[dict[str, Any]],
    train_range: tuple[float, float],
    test_range: tuple[float, float],
    result_id: str,
    run_id: str,
) -> str:
    lines = [
        "# Pendulum Gauntlet Leaderboard",
        "",
        f"- Result: `{result_id}` / Run: `{run_id}`",
        f"- Train range (rad): `{train_range[0]:.4f}` to `{train_range[1]:.4f}`",
        f"- Test range (rad): `{test_range[0]:.4f}` to `{test_range[1]:.4f}`",
        f"- Total candidates: {len(entries)}",
        "",
        "| Rank | Model ID | Family | Cpx | Test Mean Err | Test Max Err | Verdict | Failure Mode |",
        "| ---: | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for entry in entries:
        lines.append(
            f"| {entry['rank']} "
            f"| `{entry['model_id']}` "
            f"| {entry['family']} "
            f"| {entry['complexity_score']} "
            f"| {entry['test_mean_relative_error']:.6f} "
            f"| {entry['test_max_relative_error']:.6f} "
            f"| {entry['verdict']} "
            f"| {entry['failure_mode']} |"
        )
    lines.extend(["", "All errors are mean/max relative error on the test split."])
    return "\n".join(lines) + "\n"


def _failure_mode_summary(entries: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        fm = entry["failure_mode"]
        counts[fm] = counts.get(fm, 0) + 1
    return counts


def _build_report(
    title: str,
    result_id: str,
    run_id: str,
    hypothesis_id: str,
    task_id: str,
    limitations: list[str],
    train_range: tuple[float, float],
    test_range: tuple[float, float],
    leaderboard_entries: list[dict[str, Any]],
    best_score: ModelScore,
    best_verdict: str,
    verification_summary: dict[str, Any],
) -> str:
    top_entries = leaderboard_entries[:10]
    fm_summary = _failure_mode_summary(leaderboard_entries)
    lines = [
        f"# {title}",
        "",
        f"- Result: `{result_id}`",
        f"- Run: `{run_id}`",
        f"- Hypothesis: `{hypothesis_id}`",
        f"- Task: `{task_id}`",
        f"- Train range (rad): `{train_range[0]:.4f}` to `{train_range[1]:.4f}`",
        f"- Test range (rad): `{test_range[0]:.4f}` to `{test_range[1]:.4f}`",
        f"- Total candidates evaluated: {len(leaderboard_entries)}",
        "",
        "## Limitations",
        "",
    ]
    lines.extend([f"- {lim}" for lim in limitations])
    lines.extend(
        [
            "",
            "## Verification (Best Candidate)",
            "",
            f"- Best candidate: `{best_score.model_id}`",
            f"- Verification gate passed: `{verification_summary['passed']}`",
        ]
    )
    lines.extend([f"- {check['name']}: `{check['status']}`" for check in verification_summary["checks"]])
    lines.extend(
        [
            "",
            "## Top 10 Leaderboard",
            "",
            "| Rank | Model ID | Family | Cpx | Test Mean Err | Test Max Err | Verdict | Failure Mode |",
            "| ---: | --- | --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for entry in top_entries:
        lines.append(
            f"| {entry['rank']} "
            f"| `{entry['model_id']}` "
            f"| {entry['family']} "
            f"| {entry['complexity_score']} "
            f"| {entry['test_mean_relative_error']:.6f} "
            f"| {entry['test_max_relative_error']:.6f} "
            f"| {entry['verdict']} "
            f"| {entry['failure_mode']} |"
        )
    lines.extend(
        [
            "",
            "## Failure Mode Summary",
            "",
        ]
    )
    for mode, count in sorted(fm_summary.items()):
        lines.append(f"- `{mode}`: {count} candidate(s)")
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"Best candidate: `{best_score.model_id}` with verdict `{best_result_verdict(best_verdict)}`.",
            f"Formula: `{best_score.formula}`",
            "",
            "## Conclusion",
            "",
            (
                "This report describes approximation behavior only within the configured amplitude ranges. "
                "It keeps the interpretation benchmark-scoped and range-limited. "
                "The leaderboard identifies the best-performing candidate formula under the current benchmark "
                f"across {len(leaderboard_entries)} evaluated deterministic candidates."
            ),
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
    total_candidates: int,
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
        f"- Gauntlet candidates evaluated: {total_candidates}",
        "",
        "## Suggested Evidence Update",
        "",
        (
            f"The pendulum gauntlet evaluated {total_candidates} deterministic candidate formulas. "
            f"The best candidate was `{best_score.model_id}` with verdict `{best_verdict}`."
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
            "Keep the claim range-aware. The gauntlet improves confidence in the best-in-class formula "
            "family, but does not establish a closed-form or exhaustive pendulum formula."
        ),
        "",
    ]
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
    total_candidates: int,
) -> str:
    claim_path = repo_root / "claims" / "CLAIM-0001-pendulum-period-amplitude.md"
    if not claim_path.exists():
        return render_patch_artifact(
            title=f"Claim Patch Proposal for {claim_id}",
            target_file="claims/CLAIM-0001-pendulum-period-amplitude.md",
            proposed_status=suggestion_status,
            evidence_basis=["RESULT-0001", "RESULT-0003", result_id],
            original_text="",
            proposed_text="",
            rationale="Target claim file unavailable; no direct diff generated.",
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
    evidence_status = (
        f"`RESULT-0001`, `RESULT-0003`, and `{result_id}` together support a bounded, "
        "verification-backed update for amplitude-dependent ideal-pendulum behavior. "
        f"The latest gauntlet ({total_candidates} evaluated candidates) identifies the "
        "best-in-class formula family within the tested range. The result still requires "
        "range-aware wording and maintainer review before claim promotion."
    )
    review_lines = [
        f"A maintainer may promote this claim to `{suggestion_status}` after review.",
        "",
        "Reason:",
        "",
        "- The pendulum evidence set includes multiple reproducible runs;",
        f"- a systematic gauntlet evaluates {total_candidates} deterministic candidates;",
        "- non-exhaustive search coverage requires clearly bounded wording.",
        "",
        f"Promotion rationale: {suggestion_rationale}",
    ]
    proposed_text = replace_markdown_section(proposed_text, "Evidence Status", evidence_status)
    proposed_text = replace_markdown_section(
        proposed_text, "Review Recommendation", "\n".join(review_lines)
    )
    return render_patch_artifact(
        title=f"Claim Patch Proposal for {claim_id}",
        target_file="claims/CLAIM-0001-pendulum-period-amplitude.md",
        proposed_status=suggestion_status,
        evidence_basis=["RESULT-0001", "RESULT-0003", result_id],
        original_text=original_text,
        proposed_text=proposed_text,
        rationale="Gauntlet result strengthens range-limited evidence without overstating scope.",
    )


def _build_knowledge_patch(
    *,
    repo_root: Path,
    knowledge_id: str,
    result_id: str,
    run_id: str,
    task_id: str,
    best_score: ModelScore,
    best_verdict: str,
    limitations: list[str],
    verification_summary: dict[str, Any],
    total_candidates: int,
) -> str:
    knowledge_path = repo_root / "knowledge" / "classical_mechanics" / "pendulum.md"
    if not knowledge_path.exists():
        return render_patch_artifact(
            title=f"Knowledge Patch Proposal for {knowledge_id}",
            target_file="knowledge/classical_mechanics/pendulum.md",
            evidence_basis=["RESULT-0001", "RESULT-0003", result_id, task_id],
            original_text="",
            proposed_text="",
            sections_to_update=["Known Baseline", "Linked Objects", "Open Questions"],
            rationale="Target knowledge note unavailable; no direct diff generated.",
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
        "The current public-alpha benchmark has three canonical pendulum runs:",
        "",
        "- `RESULT-0001` / `RUN-0001` — original low-order candidate comparison;",
        "- `RESULT-0003` / `RUN-0002` — theory-aware near-separatrix follow-up;",
        f"- `{result_id}` / `{run_id}` — systematic gauntlet of {total_candidates} candidates.",
        "",
        "The gauntlet best candidate is:",
        "",
        f"- `{best_score.model_id}`",
        f"- formula: `{best_score.formula}`",
        f"- verdict: `{best_verdict}`",
        "",
        "Verification summary for the gauntlet best candidate:",
        "",
        f"- Verification gate passed: `{verification_summary['passed']}`",
    ]
    known_baseline_lines.extend(
        [f"- {check['name']}: `{check['status']}`" for check in verification_summary["checks"]]
    )
    linked_objects = "\n".join(
        [
            "- Hypothesis: `HYP-0001`",
            "- Experiment: `EXP-0001`",
            "- Claim: `CLAIM-0001`",
            "- Tasks:",
            "  - `TASK-0001`",
            "  - `TASK-0003`",
            f"  - `{task_id}`",
            "- Canonical results:",
            "  - `RESULT-0001`",
            "  - `RESULT-0003`",
            f"  - `{result_id}`",
        ]
    )
    open_questions = "\n".join(
        [
            "- Which low-order formula gives the best accuracy/complexity tradeoff?",
            "- How quickly do polynomial amplitude corrections fail near large angles?",
            (
                f"- The gauntlet ({total_candidates} candidates) identifies a current "
                "best family; are there further improvements beyond the tested atom basis?"
            ),
            "- Which limitations must remain explicit if the claim is promoted to `PARTIALLY_SUPPORTED`?",
        ]
    )
    proposed_text = replace_markdown_section(
        original_text, "Known Baseline", "\n".join(known_baseline_lines)
    )
    proposed_text = replace_markdown_section(proposed_text, "Linked Objects", linked_objects)
    proposed_text = replace_markdown_section(proposed_text, "Open Questions", open_questions)
    return render_patch_artifact(
        title=f"Knowledge Patch Proposal for {knowledge_id}",
        target_file="knowledge/classical_mechanics/pendulum.md",
        evidence_basis=["RESULT-0001", "RESULT-0003", result_id, task_id],
        original_text=original_text,
        proposed_text=proposed_text,
        sections_to_update=["Known Baseline", "Linked Objects", "Open Questions"],
        rationale="Expand with latest gauntlet evidence and bounded review language.",
    )


def _build_constrained_comparison_section(
    constrained_score: ModelScore,
    constrained_verdict: str,
    reference_score: ModelScore | None,
    reference_verdict: str | None,
    constrained_coefficients: dict[str, float],
) -> str:
    """Build a markdown section comparing the constrained candidate to the reference."""
    lines = [
        "## Physics-Constrained Candidate (c = 1/π fixed)",
        "",
        "| Property | Value |",
        "| --- | --- |",
        f"| Model ID | `{constrained_score.model_id}` |",
        f"| Formula | `{constrained_score.formula}` |",
        f"| Test mean relative error | `{constrained_score.test_metrics.mean_relative_error:.6f}` |",
        f"| Test max relative error | `{constrained_score.test_metrics.max_relative_error:.6f}` |",
        f"| Verdict | `{constrained_verdict}` |",
        "",
        "### Fitted Coefficients",
        "",
    ]
    for name, value in constrained_coefficients.items():
        lines.append(f"- `{name}` = `{value:.8f}`")
    lines.append(f"- `c` = `1/π = {1.0 / 3.141592653589793:.8f}` (fixed)")
    lines.append("")

    if reference_score is not None and reference_verdict is not None:
        lines.extend(
            [
                "### Comparison with Best Unconstrained Log Candidate",
                "",
                "| Metric | Unconstrained (`model_t2_x4_l1`) | Constrained (`model_phys_constrained_l1`) |",
                "| --- | ---: | ---: |",
                f"| Test mean relative error | `{reference_score.test_metrics.mean_relative_error:.6f}` | `{constrained_score.test_metrics.mean_relative_error:.6f}` |",
                f"| Test max relative error | `{reference_score.test_metrics.max_relative_error:.6f}` | `{constrained_score.test_metrics.max_relative_error:.6f}` |",
                f"| Verdict | `{reference_verdict}` | `{constrained_verdict}` |",
                "",
            ]
        )

    lines.extend(
        [
            "### Physical Interpretation",
            "",
            "The log coefficient `c = 1/π` is derived from the exact asymptotic expansion",
            "of `K(k²) ≈ ln(4/√(1-k²))` as `k → 1` (near-separatrix limit).",
            "Fixing this coefficient to its theoretically correct value allows the free",
            "parameters `a` and `b` to capture intermediate-angle corrections without",
            "sacrificing near-separatrix divergence behavior.",
            "",
        ]
    )
    return "\n".join(lines)


def _build_asymptotic_comparison_section(
    asymptotic_score: ModelScore,
    asymptotic_verdict: str,
    asymptotic_coefficients: dict[str, float],
) -> str:
    """Build a markdown section for the high-precision asymptotic candidate."""
    import math

    lines = [
        "## High-Precision Asymptotic Candidate (A&S Inspired)",
        "",
        "| Property | Value |",
        "| --- | --- |",
        f"| Model ID | `{asymptotic_score.model_id}` |",
        f"| Formula | `{asymptotic_score.formula}` |",
        f"| Test mean relative error | `{asymptotic_score.test_metrics.mean_relative_error:.6e}` |",
        f"| Test max relative error | `{asymptotic_score.test_metrics.max_relative_error:.6e}` |",
        f"| Verdict | `{asymptotic_verdict}` |",
        "",
        "### Fitted Coefficients",
        "",
    ]
    for name, value in asymptotic_coefficients.items():
        lines.append(f"- `{name}` = `{value:.8f}`")
        if name == "a":
            constrained_b = (math.pi / 2.0) - math.log(4.0) - value
            lines.append(f"- `b` = `{constrained_b:.8f}` (constrained by small-angle limit)")
    lines.extend(
        [
            "",
            "### Physical Interpretation",
            "",
            "This model uses a 4-term polynomial in `(1-x)` and `(1-x)ln(1-x)` to refine",
            "the basic logarithmic asymptotic expansion from Abramowitz & Stegun.",
            "The `m1^2` coefficient is constrained so the small-angle limit is exact,",
            "while the fitted log terms preserve the near-separatrix divergence diagnostics.",
            "",
        ]
    )
    return "\n".join(lines)


def run_gauntlet_experiment_with_output(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> ExperimentOutcome:
    """Execute the pendulum gauntlet workflow, optionally overriding the result root."""
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
        raise ValueError("Config must define task_id for result traceability")
    if not run_id:
        raise ValueError("Config must define run_id for run-based artifacts")
    if not result_id:
        raise ValueError("Config must define result_id for result traceability")

    amplitude_range_override = config.get("amplitude_range_override")
    if amplitude_range_override:
        amplitude_start = float(amplitude_range_override["start"])
        amplitude_end = float(amplitude_range_override["end"])
    else:
        amplitude_range = experiment["data"]["amplitude_range_radians"]
        amplitude_start = float(amplitude_range["start"])
        amplitude_end = float(amplitude_range["end"])
    sample_count = int(experiment["data"]["sample_count"])
    train_fraction = float(config.get("train_fraction", 0.7))
    dataset = generate_pendulum_dataset(
        amplitude_start=amplitude_start,
        amplitude_end=amplitude_end,
        sample_count=sample_count,
    )
    split_index = split_dataset(sample_count=sample_count, train_fraction=train_fraction)
    train_theta = dataset.theta[:split_index]
    train_target = dataset.period_ratio[:split_index]
    test_theta = dataset.theta[split_index:]
    test_target = dataset.period_ratio[split_index:]

    gauntlet_atom_set = str(config.get("gauntlet_atom_set", "current_11"))
    atom_groups, candidates = build_gauntlet_candidates(atom_set=gauntlet_atom_set)

    # Collect all candidates to fit and score
    all_candidates = list(candidates)
    all_atom_groups = list(atom_groups)

    if config.get("include_constrained_candidate"):
        c_atoms, c_model = build_constrained_candidate()
        all_candidates.append(c_model)
        all_atom_groups.append(c_atoms)

    if config.get("include_asymptotic_refined_candidate"):
        a_atoms, a_model = build_asymptotic_refined_candidate()
        all_candidates.append(a_model)
        all_atom_groups.append(a_atoms)

    fitted_models = [
        fit_candidate_model(model, train_theta, train_target) for model in all_candidates
    ]
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

    # Sort by composite score; keep atom_groups aligned via index lookup.
    model_id_to_atoms: dict[str, tuple[str, ...]] = {
        all_candidates[i].model_id: all_atom_groups[i] for i in range(len(all_candidates))
    }
    scores.sort(key=lambda s: s.composite_score)
    verdicts = {score.model_id: classify_model_score(score) for score in scores}
    best_model_id = scores[0].model_id
    best_verdict = best_result_verdict(verdicts[best_model_id])
    best_score = scores[0]
    best_fitted = next(m for m in fitted_models if m.candidate.model_id == best_model_id)

    verification_summary = verify_candidate_model(
        best_fitted,
        theta_range=(float(dataset.theta[0]), float(dataset.theta[-1])),
    )
    verification_payload = serialize_verification_summary(verification_summary)

    leaderboard_entries = [
        _build_leaderboard_entry(
            rank=rank + 1,
            score=scores[rank],
            atoms=model_id_to_atoms[scores[rank].model_id],
            verdict=verdicts[scores[rank].model_id],
        )
        for rank in range(len(scores))
    ]

    # Populate optional candidate data for metrics even if they are in the leaderboard.
    constrained_score_data: ModelScore | None = next(
        (s for s in scores if s.model_id == "model_phys_constrained_l1"),
        None,
    )
    asymptotic_score_data: ModelScore | None = next(
        (s for s in scores if s.model_id == "model_asymptotic_refined"),
        None,
    )

    constrained_coefficients: dict[str, float] = {}
    if constrained_score_data:
        constrained_fitted_model = next(
            m for m in fitted_models if m.candidate.model_id == "model_phys_constrained_l1"
        )
        constrained_coefficients = constrained_fitted_model.coefficients

    asymptotic_coefficients: dict[str, float] = {}
    if asymptotic_score_data:
        asymptotic_fitted_model = next(
            m for m in fitted_models if m.candidate.model_id == "model_asymptotic_refined"
        )
        asymptotic_coefficients = asymptotic_fitted_model.coefficients

    run_dir = result_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    result_path = run_dir / "result.yaml"
    report_path = run_dir / "report.md"
    metrics_path = run_dir / "metrics.json"
    leaderboard_json_path = run_dir / "leaderboard.json"
    leaderboard_md_path = run_dir / "leaderboard.md"
    claim_update_path = run_dir / "claim_update.md"
    claim_update_patch_path = run_dir / "claim_update.patch.md"
    knowledge_update_path = run_dir / "knowledge_update.md"
    knowledge_update_patch_path = run_dir / "knowledge_update.patch.md"
    review_summary_path = run_dir / "review_summary.md"
    review_metadata_path = run_dir / "review_metadata.yaml"

    limitations = _GAUNTLET_LIMITATIONS
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
    current_commit = _committed_git_commit(repo_root)

    leaderboard_payload: dict[str, Any] = {
        "schema_version": "1",
        "experiment_id": str(experiment["id"]),
        "run_id": run_id,
        "result_id": result_id,
        "total_candidates": len(leaderboard_entries),
        "train_range": [float(train_theta[0]), float(train_theta[-1])],
        "test_range": [float(test_theta[0]), float(test_theta[-1])],
        "entries": leaderboard_entries,
    }
    write_text_atomic(leaderboard_json_path, json.dumps(leaderboard_payload, indent=2))
    write_text_atomic(
        leaderboard_md_path,
        _build_leaderboard_md(
            entries=leaderboard_entries,
            train_range=(float(train_theta[0]), float(train_theta[-1])),
            test_range=(float(test_theta[0]), float(test_theta[-1])),
            result_id=result_id,
            run_id=run_id,
        ),
    )

    report_title = f"{experiment['title']} — Gauntlet ({len(leaderboard_entries)} Candidates)"
    report_text = _build_report(
        title=report_title,
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(experiment["hypothesis_id"]),
        task_id=task_id,
        limitations=limitations,
        train_range=(float(train_theta[0]), float(train_theta[-1])),
        test_range=(float(test_theta[0]), float(test_theta[-1])),
        leaderboard_entries=leaderboard_entries,
        best_score=best_score,
        best_verdict=verdicts[best_model_id],
        verification_summary=verification_payload,
    )
    if constrained_score_data is not None:
        reference_score_for_constrained = next(
            (s for s in scores if s.model_id == "model_t2_x4_l1"), None
        )
        reference_verdict_for_constrained = (
            verdicts.get("model_t2_x4_l1") if reference_score_for_constrained else None
        )
        report_text = report_text.rstrip("\n") + "\n\n" + _build_constrained_comparison_section(
            constrained_score=constrained_score_data,
            constrained_verdict=verdicts[constrained_score_data.model_id],
            reference_score=reference_score_for_constrained,
            reference_verdict=reference_verdict_for_constrained,
            constrained_coefficients=constrained_coefficients,
        )
    if asymptotic_score_data is not None:
        report_text = report_text.rstrip("\n") + "\n\n" + _build_asymptotic_comparison_section(
            asymptotic_score=asymptotic_score_data,
            asymptotic_verdict=verdicts[asymptotic_score_data.model_id],
            asymptotic_coefficients=asymptotic_coefficients,
        )
    write_text_atomic(report_path, report_text)

    claim_status_suggestion = suggest_claim_status(
        verification_summary=verification_payload,
        best_verdict=best_verdict,
        range_limited=True,
        exact_verification=False,
    )

    result_payload: dict[str, Any] = {
        "result_id": result_id,
        "run_id": run_id,
        "experiment_id": str(experiment["id"]),
        "title": report_title,
        "hypothesis_id": str(experiment["hypothesis_id"]),
        "task_id": task_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine_version": __version__,
        "git_commit": current_commit,
        "command": command,
        "input_file_hashes": input_hashes,
        "code_reference": "physics_lab/workflows/gauntlet.py",
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
        "gauntlet_candidate_set": gauntlet_atom_set,
    }
    validate_result_payload(result_payload, source=result_path)
    write_text_atomic(result_path, yaml.safe_dump(result_payload, sort_keys=False))

    metrics_payload: dict[str, Any] = {
        "result_id": result_id,
        "run_id": run_id,
        "best_model_id": best_model_id,
        "best_verdict": best_verdict,
        "total_candidates": len(leaderboard_entries),
        "verification": verification_payload,
        "scores": result_payload["scores"],
        "gauntlet_candidate_set": gauntlet_atom_set,
        "leaderboard_top10": leaderboard_entries[:10],
        "failure_mode_summary": _failure_mode_summary(leaderboard_entries),
    }
    if constrained_score_data is not None:
        metrics_payload["constrained_candidate"] = {
            "model_id": constrained_score_data.model_id,
            "formula": constrained_score_data.formula,
            "verdict": verdicts[constrained_score_data.model_id],
            "coefficients": constrained_coefficients,
            "fixed_coefficient": {"c": 1.0 / 3.141592653589793},
            "test_mean_relative_error": constrained_score_data.test_metrics.mean_relative_error,
            "test_max_relative_error": constrained_score_data.test_metrics.max_relative_error,
            "train_mean_relative_error": constrained_score_data.train_metrics.mean_relative_error,
            "composite_score": constrained_score_data.composite_score,
        }
    if asymptotic_score_data is not None:
        metrics_payload["asymptotic_candidate"] = {
            "model_id": asymptotic_score_data.model_id,
            "formula": asymptotic_score_data.formula,
            "verdict": verdicts[asymptotic_score_data.model_id],
            "coefficients": asymptotic_coefficients,
            "test_mean_relative_error": asymptotic_score_data.test_metrics.mean_relative_error,
            "test_max_relative_error": asymptotic_score_data.test_metrics.max_relative_error,
            "train_mean_relative_error": asymptotic_score_data.train_metrics.mean_relative_error,
            "composite_score": asymptotic_score_data.composite_score,
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
        total_candidates=len(leaderboard_entries),
    )
    knowledge_update_text = (
        f"# Proposed Update for KNOW-0001\n\n"
        f"- Result: `{result_id}`\n"
        f"- Task: `{task_id}`\n\n"
        f"See `knowledge_update.patch.md` for the section-aware patch proposal.\n"
    )
    claim_patch_text = _build_claim_patch(
        repo_root=repo_root,
        claim_id="CLAIM-0001",
        result_id=result_id,
        suggestion_status=claim_status_suggestion.status,
        suggestion_rationale=claim_status_suggestion.rationale,
        train_range=(float(train_theta[0]), float(train_theta[-1])),
        test_range=(float(test_theta[0]), float(test_theta[-1])),
        total_candidates=len(leaderboard_entries),
    )
    knowledge_patch_text = _build_knowledge_patch(
        repo_root=repo_root,
        knowledge_id="KNOW-0001",
        result_id=result_id,
        run_id=run_id,
        task_id=task_id,
        best_score=best_score,
        best_verdict=best_verdict,
        limitations=limitations,
        verification_summary=verification_payload,
        total_candidates=len(leaderboard_entries),
    )
    review_summary_text = render_review_summary(
        result_id=result_id,
        claim_id="CLAIM-0001",
        knowledge_id="KNOW-0001",
        suggested_status=claim_status_suggestion.status,
        rationale=claim_status_suggestion.rationale,
        highlights=[
            f"Gauntlet evaluated {len(leaderboard_entries)} deterministic candidates.",
            f"Best candidate: `{best_model_id}` with verdict `{best_verdict}`.",
            "Claim promotion, if accepted, should remain bounded at `PARTIALLY_SUPPORTED`.",
        ],
        limitations=limitations,
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
        evidence_basis=["RESULT-0001", "RESULT-0003", result_id],
        claim_target_file="claims/CLAIM-0001-pendulum-period-amplitude.md",
        knowledge_target_file="knowledge/classical_mechanics/pendulum.md",
        claim_patch_path=relative_or_absolute(claim_update_patch_path, repo_root),
        knowledge_patch_path=relative_or_absolute(knowledge_update_patch_path, repo_root),
        review_summary_path=relative_or_absolute(review_summary_path, repo_root),
    )
    write_text_atomic(review_metadata_path, yaml.safe_dump(review_metadata_payload, sort_keys=False))

    return ExperimentOutcome(
        title=str(result_payload["title"]),
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
