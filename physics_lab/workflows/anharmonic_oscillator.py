"""Anharmonic oscillator period benchmark workflow."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from physics_lab import __version__
from physics_lab.engines.anharmonic_oscillator import (
    AnharmonicOscillatorParameters,
    AnharmonicSample,
    empirical_quadratic_period,
    fit_empirical_quadratic_ratio,
    generate_reference_samples,
    harmonic_period_prediction,
    perturbative_period,
    reference_period,
)
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


def _anharmonic_limitations() -> list[str]:
    return [
        "This benchmark covers the conservative 1D quartic anharmonic oscillator with V(x) = 1/2 k x^2 + lambda x^4.",
        "Only non-negative quartic coefficients are included; softening and double-well cases are outside scope.",
        "Reported verdicts are benchmark-slice statements, not claims about driven, damped, chaotic, or large-parameter regimes.",
    ]


def _verification_check(name: str, status: str, details: str, metrics: dict[str, Any]) -> dict[str, Any]:
    return {"name": name, "status": status, "details": details, "metrics": metrics}


def _slice_arrays(samples: list[AnharmonicSample]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    amplitudes = np.asarray([sample.amplitude for sample in samples], dtype=float)
    ratios = np.asarray([sample.anharmonicity_ratio for sample in samples], dtype=float)
    reference_periods = np.asarray([sample.reference_period for sample in samples], dtype=float)
    return amplitudes, ratios, reference_periods


def _classify_anharmonic_score(score: ModelScore) -> str:
    train_mean = score.train_metrics.mean_relative_error
    test_mean = score.test_metrics.mean_relative_error
    test_max = score.test_metrics.max_relative_error

    if test_mean <= 0.01 and test_max <= 0.025:
        return "VALID"
    if test_mean <= 0.03 and test_max <= 0.08:
        return "PARTIALLY_VALID"
    if train_mean > 0.0 and test_mean / train_mean >= 3.0:
        return "OVERFITTED"
    if not all(metric >= 0.0 for metric in (train_mean, test_mean, test_max)):
        return "INCONCLUSIVE"
    return "INVALID"


def _score_candidate(
    *,
    model_id: str,
    formula: str,
    complexity_score: int,
    train_pred: np.ndarray,
    train_target: np.ndarray,
    holdout_pred: np.ndarray,
    holdout_target: np.ndarray,
    coefficients: dict[str, float],
) -> ModelScore:
    train_metrics = compute_error_metrics(train_pred, train_target)
    holdout_metrics = compute_error_metrics(holdout_pred, holdout_target)
    composite_score = (
        holdout_metrics.mean_relative_error
        + 0.25 * holdout_metrics.max_relative_error
        + 0.001 * complexity_score
    )
    return ModelScore(
        model_id=model_id,
        formula=formula,
        coefficients=coefficients,
        complexity_score=complexity_score,
        train_metrics=train_metrics,
        test_metrics=holdout_metrics,
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
            "Keep the claim benchmark-scoped. The current run evaluates one canonical anharmonic oscillator benchmark surface only.",
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
            "Retain `DRAFT` until a maintainer explicitly reviews the benchmark wording and decides whether the scope is narrow enough for promotion.",
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
    target_file = "claims/CLAIM-0009-anharmonic-oscillator-period.md"
    target_path = repo_root / target_file
    original_text = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
    proposed_text = original_text.replace(
        "status: DRAFT",
        f"status: {suggestion_status}",
        1,
    )
    proposed_text = proposed_text.replace(
        "A maintainer should review benchmark wording before any promotion.",
        suggestion_rationale,
        1,
    )
    if result_id not in proposed_text:
        proposed_text = proposed_text.replace(
            "  results:\n    - RESULT-0014",
            f"  results:\n    - {result_id}",
            1,
        )
    return render_patch_artifact(
        title="Claim Patch Proposal for CLAIM-0009",
        target_file=target_file,
        evidence_basis=[result_id],
        original_text=original_text,
        proposed_text=proposed_text,
        proposed_status=suggestion_status,
        sections_to_update=["Evidence Status", "Review Recommendation"],
        rationale="Keep any claim promotion benchmark-scoped and explicitly range-aware.",
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
            "- Topic: conservative quartic anharmonic oscillator period benchmark",
            "",
            "## Suggested Linked Objects Update",
            "",
            f"- Hypothesis: `{hypothesis_id}`",
            f"- Experiment: `{experiment_id}`",
            "- Claim: `CLAIM-0009`",
            f"- Task: `{task_id}`",
            f"- Canonical result: `{result_id}`",
            "",
            "## Proposed Additions",
            "",
            "- Add the benchmark as a nonlinear mechanics baseline with a deterministic period-integral reference.",
            f"- Record `{best_model_id}` as the current best benchmark candidate under the configured slices.",
            "- Preserve the perturbative breakdown boundary as part of the note rather than as a public success claim.",
            "",
        ]
    )


def _build_knowledge_patch(
    *,
    repo_root: Path,
    result_id: str,
    best_model_id: str,
) -> str:
    target_file = "knowledge/classical_mechanics/anharmonic_oscillator.md"
    target_path = repo_root / target_file
    original_text = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
    proposed_text = original_text
    if result_id not in proposed_text:
        proposed_text = proposed_text.replace(
            "- Canonical result: `RESULT-0014`",
            f"- Canonical result: `{result_id}`",
            1,
        )
    if best_model_id not in proposed_text:
        proposed_text = proposed_text.replace(
            "The benchmark compares the harmonic baseline, the leading-order perturbative correction, and a train-fitted empirical quadratic model.",
            "The benchmark compares the harmonic baseline, the leading-order perturbative correction, and a train-fitted empirical quadratic model.\n"
            f"The current canonical run selects `{best_model_id}` as the best model on the configured holdout slice.",
            1,
        )
    return render_patch_artifact(
        title="Knowledge Patch Proposal for KNOW-0008",
        target_file=target_file,
        evidence_basis=[result_id],
        original_text=original_text,
        proposed_text=proposed_text,
        sections_to_update=["Known Baseline", "Linked Objects", "Open Questions"],
        rationale="Preserve the anharmonic oscillator benchmark as reusable scientific memory without overpromoting its scope.",
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
        claim_id="CLAIM-0009",
        knowledge_id="KNOW-0008",
        suggested_status=suggestion_status,
        rationale=suggestion_rationale,
        highlights=[
            "The benchmark now includes a deterministic anharmonic period reference path and a predeclared holdout slice.",
            "The perturbative baseline stays useful in the weak regime but breaks down as anharmonicity grows.",
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
    assumptions: list[str],
    limitations: list[str],
    train_ratio_range: tuple[float, float],
    holdout_ratio_range: tuple[float, float],
    stress_ratio_range: tuple[float, float],
    scores: list[ModelScore],
    verdicts: dict[str, str],
    best_model_id: str,
    verification_summary: dict[str, Any],
    dataset_summary: dict[str, Any],
) -> str:
    lines = [
        f"# {title}",
        "",
        f"- Result: `{result_id}`",
        f"- Run: `{run_id}`",
        f"- Hypothesis: `{hypothesis_id}`",
        f"- Task: `{task_id}`",
        f"- Train anharmonicity ratio: `{train_ratio_range[0]:.4f}` to `{train_ratio_range[1]:.4f}`",
        f"- Holdout anharmonicity ratio: `{holdout_ratio_range[0]:.4f}` to `{holdout_ratio_range[1]:.4f}`",
        f"- Stress anharmonicity ratio: `{stress_ratio_range[0]:.4f}` to `{stress_ratio_range[1]:.4f}`",
        "",
        "## Assumptions",
        "",
        *(f"- {assumption}" for assumption in assumptions),
        "",
        "## Dataset",
        "",
        f"- Mass: `{dataset_summary['mass']}`",
        f"- Stiffness: `{dataset_summary['stiffness']}`",
        f"- Amplitude range: `{dataset_summary['amplitude_start']:.3f}` to `{dataset_summary['amplitude_end']:.3f}`",
        f"- Quartic coefficients: `{', '.join(f'{value:.3f}' for value in dataset_summary['quartic_coefficients'])}`",
        f"- Sample count: `{dataset_summary['sample_count']}`",
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
        "| Model | Formula | Complexity | Train mean rel. error | Holdout mean rel. error | Verdict |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for score in scores:
        lines.append(
            "| "
            + " | ".join(
                [
                    score.model_id,
                    f"`{score.formula}`",
                    str(score.complexity_score),
                    f"{score.train_metrics.mean_relative_error:.6f}",
                    f"{score.test_metrics.mean_relative_error:.6f}",
                    verdicts[score.model_id],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"`{best_model_id}` is the best model on the configured holdout slice, reported as `{verdicts[best_model_id]}`.",
            "",
            "## Conclusion",
            "",
            "The benchmark establishes a deterministic nonlinear mechanics surface with a reference integral, a perturbative baseline, and an explicit breakdown region.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_anharmonic_oscillator_experiment_with_output(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> ExperimentOutcome:
    """Execute the anharmonic oscillator period benchmark."""
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

    data = experiment["data"]
    mass = float(data["mass"])
    stiffness = float(data["stiffness"])
    amplitude_start = float(data["amplitude_range"]["start"])
    amplitude_end = float(data["amplitude_range"]["end"])
    amplitude_count = int(data["amplitude_range"]["sample_count"])
    quartic_coefficients = np.asarray(data["quartic_coefficients"], dtype=float)
    train_max_ratio = float(data["train_max_anharmonicity"])
    holdout_max_ratio = float(data["holdout_max_anharmonicity"])
    stress_max_ratio = float(data["stress_max_anharmonicity"])

    amplitudes = np.linspace(amplitude_start, amplitude_end, amplitude_count)
    samples = generate_reference_samples(
        mass=mass,
        stiffness=stiffness,
        amplitudes=amplitudes,
        quartic_coefficients=quartic_coefficients,
    )
    train_samples = [sample for sample in samples if sample.anharmonicity_ratio <= train_max_ratio]
    holdout_samples = [
        sample
        for sample in samples
        if train_max_ratio < sample.anharmonicity_ratio <= holdout_max_ratio
    ]
    stress_samples = [
        sample
        for sample in samples
        if holdout_max_ratio < sample.anharmonicity_ratio <= stress_max_ratio
    ]
    if not train_samples or not holdout_samples or not stress_samples:
        raise ValueError("Configured anharmonic sample slices must all be non-empty")

    empirical_coefficients = fit_empirical_quadratic_ratio(train_samples, mass=mass, stiffness=stiffness)

    def _predict(samples_subset: list[AnharmonicSample], model_id: str) -> np.ndarray:
        predictions: list[float] = []
        for sample in samples_subset:
            parameters = AnharmonicOscillatorParameters(
                mass=mass,
                stiffness=stiffness,
                quartic_coefficient=sample.quartic_coefficient,
            )
            if model_id == "model_harmonic":
                predictions.append(harmonic_period_prediction(parameters, sample.amplitude))
            elif model_id == "model_perturbative_leading":
                predictions.append(perturbative_period(parameters, sample.amplitude))
            elif model_id == "model_empirical_quadratic":
                predictions.append(empirical_quadratic_period(parameters, sample.amplitude, empirical_coefficients))
            else:
                raise ValueError(f"Unknown anharmonic model id: {model_id}")
        return np.asarray(predictions, dtype=float)

    _, _, train_target = _slice_arrays(train_samples)
    _, _, holdout_target = _slice_arrays(holdout_samples)
    _, _, stress_target = _slice_arrays(stress_samples)

    candidate_formulas = {candidate["id"]: candidate["formula"] for candidate in experiment["candidate_models"]}
    scores = [
        _score_candidate(
            model_id="model_harmonic",
            formula=candidate_formulas["model_harmonic"],
            complexity_score=1,
            train_pred=_predict(train_samples, "model_harmonic"),
            train_target=train_target,
            holdout_pred=_predict(holdout_samples, "model_harmonic"),
            holdout_target=holdout_target,
            coefficients={"baseline_ratio": 1.0},
        ),
        _score_candidate(
            model_id="model_perturbative_leading",
            formula=candidate_formulas["model_perturbative_leading"],
            complexity_score=1,
            train_pred=_predict(train_samples, "model_perturbative_leading"),
            train_target=train_target,
            holdout_pred=_predict(holdout_samples, "model_perturbative_leading"),
            holdout_target=holdout_target,
            coefficients={"series_coefficient": -1.5},
        ),
        _score_candidate(
            model_id="model_empirical_quadratic",
            formula=candidate_formulas["model_empirical_quadratic"],
            complexity_score=2,
            train_pred=_predict(train_samples, "model_empirical_quadratic"),
            train_target=train_target,
            holdout_pred=_predict(holdout_samples, "model_empirical_quadratic"),
            holdout_target=holdout_target,
            coefficients=empirical_coefficients,
        ),
    ]
    scores.sort(key=lambda score: score.composite_score)
    verdicts = {score.model_id: _classify_anharmonic_score(score) for score in scores}
    best_model_id = scores[0].model_id
    best_verdict = best_result_verdict(verdicts[best_model_id])

    perturbative_score = next(score for score in scores if score.model_id == "model_perturbative_leading")
    empirical_score = next(score for score in scores if score.model_id == "model_empirical_quadratic")

    harmonic_limit_errors = []
    for amplitude in (0.2, 0.8, 1.4):
        params = AnharmonicOscillatorParameters(mass=mass, stiffness=stiffness, quartic_coefficient=0.0)
        reference_value = reference_period(params, amplitude)
        harmonic_limit_errors.append(abs(reference_value - params.harmonic_period))
    harmonic_limit_max_error = float(max(harmonic_limit_errors))

    monotonic_checks: list[bool] = []
    for coefficient in quartic_coefficients:
        subset = [
            sample for sample in samples
            if abs(sample.quartic_coefficient - float(coefficient)) <= 1.0e-12
            and sample.anharmonicity_ratio <= stress_max_ratio
        ]
        ordered = sorted(subset, key=lambda sample: sample.amplitude)
        monotonic_checks.append(
            all(
                ordered[index].reference_period >= ordered[index + 1].reference_period
                for index in range(len(ordered) - 1)
            )
        )

    perturbative_stress_pred = _predict(stress_samples, "model_perturbative_leading")
    perturbative_stress_metrics = compute_error_metrics(perturbative_stress_pred, stress_target)
    breakdown_ratio = None
    for sample, predicted in zip(stress_samples, perturbative_stress_pred):
        error = abs(predicted - sample.reference_period) / sample.reference_period
        if error > 0.01:
            breakdown_ratio = sample.anharmonicity_ratio
            break
    if breakdown_ratio is None:
        for sample, predicted in zip(holdout_samples, _predict(holdout_samples, "model_perturbative_leading")):
            error = abs(predicted - sample.reference_period) / sample.reference_period
            if error > 0.01:
                breakdown_ratio = sample.anharmonicity_ratio
                break

    verification_payload = {
        "passed": True,
        "checks": [
            _verification_check(
                name="harmonic_limit",
                status="PASS" if harmonic_limit_max_error <= 1.0e-10 else "FAIL",
                details="With lambda = 0, the numerical reference period collapses to the harmonic period.",
                metrics={"max_absolute_error": harmonic_limit_max_error},
            ),
            _verification_check(
                name="perturbative_train_window",
                status="PASS" if perturbative_score.train_metrics.max_relative_error <= 0.01 else "FAIL",
                details="The leading-order perturbative baseline stays within 1% max relative error on the declared train window.",
                metrics={
                    "mean_relative_error": perturbative_score.train_metrics.mean_relative_error,
                    "max_relative_error": perturbative_score.train_metrics.max_relative_error,
                    "train_max_anharmonicity": train_max_ratio,
                },
            ),
            _verification_check(
                name="holdout_generalization",
                status="PASS" if empirical_score.test_metrics.mean_relative_error < perturbative_score.test_metrics.mean_relative_error else "FAIL",
                details="The train-fitted empirical quadratic model improves holdout error over the perturbative baseline.",
                metrics={
                    "empirical_holdout_mean_relative_error": empirical_score.test_metrics.mean_relative_error,
                    "perturbative_holdout_mean_relative_error": perturbative_score.test_metrics.mean_relative_error,
                },
            ),
            _verification_check(
                name="monotonic_hardening",
                status="PASS" if all(monotonic_checks) else "FAIL",
                details="For positive lambda, the reference period decreases with amplitude on each sampled quartic-coefficient slice.",
                metrics={
                    "checked_quartic_count": int(len(quartic_coefficients)),
                    "checked_quartic_coefficients_csv": ",".join(f"{float(value):.3f}" for value in quartic_coefficients),
                },
            ),
            _verification_check(
                name="perturbative_breakdown_mapping",
                status="PASS" if breakdown_ratio is not None and breakdown_ratio > train_max_ratio else "FAIL",
                details="The first >1% perturbative miss occurs outside the declared train slice, preserving the benchmark's weak-regime claim ceiling.",
                metrics={
                    "first_breakdown_anharmonicity": breakdown_ratio,
                    "stress_mean_relative_error": perturbative_stress_metrics.mean_relative_error,
                    "stress_max_relative_error": perturbative_stress_metrics.max_relative_error,
                },
            ),
        ],
    }
    verification_payload["passed"] = all(check["status"] == "PASS" for check in verification_payload["checks"])

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

    limitations = _anharmonic_limitations()
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

    train_range = (min(sample.anharmonicity_ratio for sample in train_samples), max(sample.anharmonicity_ratio for sample in train_samples))
    holdout_range = (min(sample.anharmonicity_ratio for sample in holdout_samples), max(sample.anharmonicity_ratio for sample in holdout_samples))
    stress_range = (min(sample.anharmonicity_ratio for sample in stress_samples), max(sample.anharmonicity_ratio for sample in stress_samples))

    report_text = _build_report(
        title=str(experiment["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(experiment["hypothesis_id"]),
        task_id=task_id,
        assumptions=list(hypothesis.get("assumptions", [])),
        limitations=limitations,
        train_ratio_range=train_range,
        holdout_ratio_range=holdout_range,
        stress_ratio_range=stress_range,
        scores=scores,
        verdicts=verdicts,
        best_model_id=best_model_id,
        verification_summary=verification_payload,
        dataset_summary={
            "mass": mass,
            "stiffness": stiffness,
            "amplitude_start": amplitude_start,
            "amplitude_end": amplitude_end,
            "quartic_coefficients": [float(value) for value in quartic_coefficients],
            "sample_count": len(samples),
        },
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
        "code_reference": "physics_lab/workflows/anharmonic_oscillator.py",
        "limitations": limitations,
        "train_range": [train_range[0], train_range[1]],
        "test_range": [holdout_range[0], holdout_range[1]],
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
        "slice_summary": {
            "train_max_anharmonicity": train_max_ratio,
            "holdout_max_anharmonicity": holdout_max_ratio,
            "stress_max_anharmonicity": stress_max_ratio,
        },
        "stress_metrics": {
            "perturbative_mean_relative_error": perturbative_stress_metrics.mean_relative_error,
            "perturbative_max_relative_error": perturbative_stress_metrics.max_relative_error,
        },
        "scores": result_payload["scores"],
    }
    write_text_atomic(metrics_path, json.dumps(metrics_payload, indent=2))

    write_text_atomic(
        claim_update_path,
        _build_claim_update(
            claim_id="CLAIM-0009",
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
            knowledge_id="KNOW-0008",
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
        claim_id="CLAIM-0009",
        knowledge_id="KNOW-0008",
        generated_at=result_payload["generated_at"],
        proposed_claim_status=claim_status_suggestion.status,
        evidence_basis=[result_id],
        claim_target_file="claims/CLAIM-0009-anharmonic-oscillator-period.md",
        knowledge_target_file="knowledge/classical_mechanics/anharmonic_oscillator.md",
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
        train_range=train_range,
        test_range=holdout_range,
        scores=scores,
        verdicts=verdicts,
        best_model_id=best_model_id,
        summary_lines=(
            f"Best model: {best_model_id}",
            f"Holdout verdict: {best_verdict}",
        ),
    )
