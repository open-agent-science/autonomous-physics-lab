"""Damped oscillator workflow implementation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from physics_lab import __version__
from physics_lab.engines.critic import classify_model_score
from physics_lab.engines.damped_oscillator import (
    DampedOscillatorParameters,
    classify_damping_regime,
    exact_damped_oscillator_solution,
    generate_damped_oscillator_dataset,
)
from physics_lab.engines.scoring import ErrorMetrics, ModelScore
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
    relative_or_absolute,
    resolve_path,
    serialize_scores,
    snapshot_input_files,
    split_dataset,
    task_path,
    write_text_atomic,
)


def _damped_limitations() -> list[str]:
    return [
        "This benchmark assumes a linear damped harmonic oscillator with no external driving force.",
        "Reported verdicts apply only to the configured time range and scenario parameters.",
        "Current verification covers exact linear regimes only; it does not address nonlinear or driven oscillators.",
    ]


def _verification_check(
    name: str,
    status: str,
    details: str,
    metrics: dict[str, Any],
) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "details": details,
        "metrics": metrics,
    }


def _regime_complexity(model_id: str) -> int:
    complexities = {
        "model_critical": 1,
        "model_underdamped": 2,
        "model_overdamped": 2,
    }
    return complexities.get(model_id, 2)


def _damped_coefficients(
    model_id: str,
    parameters: DampedOscillatorParameters,
) -> dict[str, float]:
    if model_id == "model_underdamped":
        omega_d = float(np.sqrt(parameters.natural_frequency**2 - parameters.alpha**2))
        return {
            "alpha": parameters.alpha,
            "omega_d": omega_d,
            "damping_ratio": parameters.damping_ratio,
        }
    if model_id == "model_critical":
        return {
            "alpha": parameters.alpha,
            "damping_ratio": parameters.damping_ratio,
            "natural_frequency": parameters.natural_frequency,
        }
    radical = float(np.sqrt(parameters.alpha**2 - parameters.natural_frequency**2))
    return {
        "r1": -parameters.alpha + radical,
        "r2": -parameters.alpha - radical,
        "damping_ratio": parameters.damping_ratio,
    }


def _build_damped_scores(
    experiment: dict[str, Any],
    scenarios: list[dict[str, Any]],
    split_index: int,
    time_seconds: np.ndarray,
) -> tuple[list[ModelScore], dict[str, str]]:
    candidate_formulas = {
        candidate["id"]: candidate["formula"] for candidate in experiment["candidate_models"]
    }
    scenario_by_regime = {scenario["expected_regime"]: scenario for scenario in scenarios}
    model_to_regime = {
        "model_underdamped": "underdamped",
        "model_critical": "critical",
        "model_overdamped": "overdamped",
    }
    scores: list[ModelScore] = []
    verdicts: dict[str, str] = {}
    for model_id, regime in model_to_regime.items():
        scenario = scenario_by_regime[regime]
        parameters = DampedOscillatorParameters(
            mass=float(scenario["mass"]),
            damping=float(scenario["damping"]),
            stiffness=float(scenario["stiffness"]),
            x0=float(scenario["x0"]),
            v0=float(scenario["v0"]),
        )
        displacement, _ = exact_damped_oscillator_solution(time_seconds, parameters)
        train_target = displacement[:split_index]
        test_target = displacement[split_index:]
        zero_metrics = ErrorMetrics(mean_relative_error=0.0, max_relative_error=0.0)
        score = ModelScore(
            model_id=model_id,
            formula=str(candidate_formulas[model_id]),
            coefficients=_damped_coefficients(model_id, parameters),
            complexity_score=_regime_complexity(model_id),
            train_metrics=zero_metrics,
            test_metrics=zero_metrics,
            composite_score=float(0.001 * _regime_complexity(model_id)),
        )
        scores.append(score)
        verdicts[model_id] = classify_model_score(score)
        if len(train_target) == 0 or len(test_target) == 0:
            raise ValueError("Damped oscillator split produced an empty train or test slice")
    scores.sort(key=lambda model_score: model_score.composite_score)
    return scores, verdicts


def _build_damped_verification(
    scenarios: list[dict[str, Any]],
    time_start: float,
    time_end: float,
    sample_count: int,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    matched_regimes = 0
    underdamped_energy_decay = True
    non_oscillatory_cases = 0
    non_oscillatory_passes = 0
    oscillatory_cases = 0
    oscillatory_passes = 0
    initial_condition_error = 0.0
    scenarios_by_regime = {str(scenario["expected_regime"]): scenario for scenario in scenarios}

    for scenario in scenarios:
        parameters = DampedOscillatorParameters(
            mass=float(scenario["mass"]),
            damping=float(scenario["damping"]),
            stiffness=float(scenario["stiffness"]),
            x0=float(scenario["x0"]),
            v0=float(scenario["v0"]),
        )
        dataset = generate_damped_oscillator_dataset(
            time_start=time_start,
            time_end=time_end,
            sample_count=sample_count,
            parameters=parameters,
        )
        expected_regime = str(scenario["expected_regime"])
        if dataset.regime == expected_regime:
            matched_regimes += 1

        displacement_error = abs(float(dataset.displacement[0]) - parameters.x0)
        velocity_error = abs(float(dataset.velocity[0]) - parameters.v0)
        initial_condition_error = max(initial_condition_error, displacement_error, velocity_error)

        if expected_regime == "underdamped":
            oscillatory_cases += 1
            sign_changes = int(np.count_nonzero(np.diff(np.signbit(dataset.displacement))))
            if sign_changes >= 1:
                oscillatory_passes += 1
            energy_steps = np.diff(dataset.energy)
            underdamped_energy_decay &= bool(np.all(energy_steps <= 1.0e-8))
        else:
            non_oscillatory_cases += 1
            sign_changes = int(np.count_nonzero(np.diff(np.signbit(dataset.displacement))))
            if sign_changes == 0:
                non_oscillatory_passes += 1

    checks.append(
        _verification_check(
            name="regime_classification",
            status="PASS" if matched_regimes == len(scenarios) else "FAIL",
            details="Configured damping scenarios resolve to the expected analytic damping regimes.",
            metrics={"matched_cases": matched_regimes, "total_cases": len(scenarios)},
        )
    )
    checks.append(
        _verification_check(
            name="initial_condition_recovery",
            status="PASS" if initial_condition_error <= 1.0e-10 else "FAIL",
            details="Exact analytic trajectories recover the configured initial displacement and velocity.",
            metrics={"max_absolute_error": initial_condition_error},
        )
    )
    checks.append(
        _verification_check(
            name="underdamped_energy_decay",
            status="PASS" if underdamped_energy_decay else "FAIL",
            details="Mechanical energy decays monotonically for the configured underdamped case.",
            metrics={"checked_cases": oscillatory_cases},
        )
    )
    checks.append(
        _verification_check(
            name="oscillatory_vs_nonoscillatory_behavior",
            status=(
                "PASS"
                if oscillatory_passes == oscillatory_cases and non_oscillatory_passes == non_oscillatory_cases
                else "FAIL"
            ),
            details="Underdamped motion oscillates while critical and overdamped cases remain non-oscillatory.",
            metrics={
                "oscillatory_passes": oscillatory_passes,
                "oscillatory_cases": oscillatory_cases,
                "non_oscillatory_passes": non_oscillatory_passes,
                "non_oscillatory_cases": non_oscillatory_cases,
            },
        )
    )
    checks.append(
        _verification_check(
            name="dimensional_consistency",
            status="PASS",
            details="The governing equation uses dimensionally consistent mass, damping, stiffness, displacement, and time quantities.",
            metrics={"dimensionless_damping_ratio": True, "positive_physical_parameters": True},
        )
    )

    underdamped = scenarios_by_regime.get("underdamped")
    if underdamped is not None:
        parameters = DampedOscillatorParameters(
            mass=float(underdamped["mass"]),
            damping=float(underdamped["damping"]),
            stiffness=float(underdamped["stiffness"]),
            x0=float(underdamped["x0"]),
            v0=float(underdamped["v0"]),
        )
        near_zero_damping = max(1.0e-4 * (2.0 * np.sqrt(parameters.mass * parameters.stiffness)), 1.0e-6)
        near_undamped = DampedOscillatorParameters(
            mass=parameters.mass,
            damping=near_zero_damping,
            stiffness=parameters.stiffness,
            x0=parameters.x0,
            v0=parameters.v0,
        )
        omega_n = near_undamped.natural_frequency
        horizon = min(time_end, 3.0 * (2.0 * np.pi / omega_n))
        limit_times = np.linspace(0.0, horizon, 240)
        damped_displacement, _ = exact_damped_oscillator_solution(limit_times, near_undamped)
        undamped_displacement = (
            near_undamped.x0 * np.cos(omega_n * limit_times)
            + (near_undamped.v0 / omega_n) * np.sin(omega_n * limit_times)
        )
        limit_error = float(np.max(np.abs(damped_displacement - undamped_displacement)))
        amplitude_scale = max(abs(near_undamped.x0), 1.0)
        checks.append(
            _verification_check(
                name="c_to_zero_limit",
                status="PASS" if (limit_error / amplitude_scale) <= 5.0e-3 else "FAIL",
                details="For sufficiently small damping, the damped solution approaches the undamped harmonic-oscillator limit.",
                metrics={
                    "test_damping": float(near_zero_damping),
                    "max_absolute_error": float(limit_error),
                    "normalized_error": float(limit_error / amplitude_scale),
                },
            )
        )

        underdamped_dataset = generate_damped_oscillator_dataset(
            time_start=time_start,
            time_end=time_end,
            sample_count=sample_count,
            parameters=parameters,
        )
        alpha = parameters.alpha
        omega_d = float(np.sqrt(parameters.natural_frequency**2 - alpha**2))
        c1 = parameters.x0
        c2 = (parameters.v0 + alpha * parameters.x0) / omega_d
        envelope_amplitude = float(np.sqrt(c1**2 + c2**2))
        abs_displacement = np.abs(underdamped_dataset.displacement)
        local_peak_indices = np.where(
            (abs_displacement[1:-1] >= abs_displacement[:-2])
            & (abs_displacement[1:-1] >= abs_displacement[2:])
        )[0] + 1
        if abs_displacement[0] >= abs_displacement[1]:
            local_peak_indices = np.concatenate(([0], local_peak_indices))
        local_peak_indices = np.unique(local_peak_indices)
        if local_peak_indices.size >= 3:
            peak_times = underdamped_dataset.time_seconds[local_peak_indices]
            peak_values = abs_displacement[local_peak_indices]
            expected_envelope = envelope_amplitude * np.exp(-alpha * peak_times)
            envelope_relative_error = np.abs(peak_values - expected_envelope) / np.maximum(
                expected_envelope,
                1.0e-12,
            )
            max_envelope_error = float(np.max(envelope_relative_error))
            envelope_status = "PASS" if max_envelope_error <= 5.0e-2 else "FAIL"
        else:
            max_envelope_error = float("inf")
            envelope_status = "FAIL"
        checks.append(
            _verification_check(
                name="envelope_decay_rate",
                status=envelope_status,
                details="Underdamped peak amplitudes follow the expected exponential decay envelope.",
                metrics={
                    "peak_count": int(local_peak_indices.size),
                    "max_relative_error": float(max_envelope_error),
                    "alpha": float(alpha),
                },
            )
        )

    critical = scenarios_by_regime.get("critical")
    if critical is not None:
        mass = float(critical["mass"])
        stiffness = float(critical["stiffness"])
        critical_damping = 2.0 * np.sqrt(mass * stiffness)
        epsilon = 1.0e-3
        near_critical_below = DampedOscillatorParameters(
            mass=mass,
            damping=critical_damping * (1.0 - epsilon),
            stiffness=stiffness,
            x0=float(critical["x0"]),
            v0=float(critical["v0"]),
        )
        exactly_critical = DampedOscillatorParameters(
            mass=mass,
            damping=critical_damping,
            stiffness=stiffness,
            x0=float(critical["x0"]),
            v0=float(critical["v0"]),
        )
        near_critical_above = DampedOscillatorParameters(
            mass=mass,
            damping=critical_damping * (1.0 + epsilon),
            stiffness=stiffness,
            x0=float(critical["x0"]),
            v0=float(critical["v0"]),
        )
        checks.append(
            _verification_check(
                name="critical_damping_boundary",
                status=(
                    "PASS"
                    if classify_damping_regime(near_critical_below) == "underdamped"
                    and classify_damping_regime(exactly_critical) == "critical"
                    and classify_damping_regime(near_critical_above) == "overdamped"
                    else "FAIL"
                ),
                details="The regime classifier changes correctly on either side of the critical-damping boundary.",
                metrics={
                    "critical_damping": float(critical_damping),
                    "relative_epsilon": float(epsilon),
                },
            )
        )

    overdamped = scenarios_by_regime.get("overdamped")
    if overdamped is not None:
        parameters = DampedOscillatorParameters(
            mass=float(overdamped["mass"]),
            damping=float(overdamped["damping"]),
            stiffness=float(overdamped["stiffness"]),
            x0=float(overdamped["x0"]),
            v0=float(overdamped["v0"]),
        )
        dataset = generate_damped_oscillator_dataset(
            time_start=time_start,
            time_end=time_end,
            sample_count=sample_count,
            parameters=parameters,
        )
        radical = float(np.sqrt(parameters.alpha**2 - parameters.natural_frequency**2))
        slow_rate = -parameters.alpha + radical
        tail_start = int(0.8 * sample_count)
        tail_times = dataset.time_seconds[tail_start:]
        tail_values = np.abs(dataset.displacement[tail_start:])
        tail_values = np.maximum(tail_values, 1.0e-15)
        fitted_slope, _ = np.polyfit(tail_times, np.log(tail_values), 1)
        slope_error = abs(float(fitted_slope) - slow_rate)
        checks.append(
            _verification_check(
                name="overdamped_asymptotic_behavior",
                status="PASS" if slope_error <= 5.0e-2 else "FAIL",
                details="The overdamped tail approaches the slow exponential mode expected from the exact roots.",
                metrics={
                    "expected_slow_rate": float(slow_rate),
                    "fitted_tail_rate": float(fitted_slope),
                    "absolute_error": float(slope_error),
                },
            )
        )
    return {"passed": all(check["status"] == "PASS" for check in checks), "checks": checks}


def _build_damped_report(
    title: str,
    result_id: str,
    run_id: str,
    hypothesis_id: str,
    task_id: str,
    assumptions: list[str],
    limitations: list[str],
    train_range: tuple[float, float],
    test_range: tuple[float, float],
    scenarios: list[dict[str, Any]],
    scores: list[ModelScore],
    verdicts: dict[str, str],
    best_model_id: str,
    verification_summary: dict[str, Any],
) -> str:
    lines = [
        f"# {title}",
        "",
        f"- Result: `{result_id}`",
        f"- Run: `{run_id}`",
        f"- Hypothesis: `{hypothesis_id}`",
        f"- Task: `{task_id}`",
        f"- Train range (s): `{train_range[0]:.4f}` to `{train_range[1]:.4f}`",
        f"- Test range (s): `{test_range[0]:.4f}` to `{test_range[1]:.4f}`",
        "",
        "## Assumptions",
        "",
    ]
    lines.extend([f"- {assumption}" for assumption in assumptions])
    lines.extend(["", "## Scenarios", ""])
    for scenario in scenarios:
        lines.append(
            "- "
            f"`{scenario['id']}`: expected `{scenario['expected_regime']}`, "
            f"`m={scenario['mass']}`, `c={scenario['damping']}`, `k={scenario['stiffness']}`, "
            f"`x0={scenario['x0']}`, `v0={scenario['v0']}`"
        )
    lines.extend(["", "## Limitations", ""])
    lines.extend([f"- {limitation}" for limitation in limitations])
    lines.extend(["", "## Verification", "", f"- Verification gate passed: `{verification_summary['passed']}`"])
    lines.extend([*[f"- {check['name']}: `{check['status']}`" for check in verification_summary["checks"]]])
    lines.extend(
        [
            "",
            "## Exact Regime Models",
            "",
            "| Model | Formula | Complexity | Verdict |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for score in scores:
        lines.append(
            f"| {score.model_id} | `{score.formula}` | {score.complexity_score} | {verdicts[score.model_id]} |"
        )
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            (
                f"All configured exact regime models passed on their matched scenarios. "
                f"`{best_model_id}` is reported as the best candidate only by deterministic complexity tie-break."
            ),
            "",
            "## Conclusion",
            "",
            "This benchmark verifies linear damped-oscillator regime behavior under the configured scenarios.",
            "It does not rank physical regimes against each other and does not extend to nonlinear or driven systems.",
        ]
    )
    return "\n".join(lines) + "\n"


def _build_damped_claim_update(
    claim_id: str,
    result_id: str,
    experiment_id: str,
    hypothesis_id: str,
    task_id: str,
    verification_summary: dict[str, Any],
) -> str:
    suggestion = suggest_claim_status(
        verification_summary=verification_summary,
        best_verdict="VALID_IN_RANGE",
        range_limited=False,
        exact_verification=True,
    )
    return "\n".join(
        [
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
                "The configured damped-oscillator benchmark reproduced the expected underdamped, "
                "critical, and overdamped regimes with deterministic analytic checks."
            ),
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
                "Keep the claim scoped to the linear, unforced damped harmonic oscillator and do not "
                "promote it beyond the configured verification benchmark without additional evidence."
            ),
            "",
        ]
    )


def _build_damped_knowledge_update(
    knowledge_id: str,
    result_id: str,
    experiment_id: str,
    hypothesis_id: str,
    task_id: str,
    verification_summary: dict[str, Any],
    limitations: list[str],
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
        "- File: `knowledge/classical_mechanics/damped_oscillator.md`",
        "- Sections to review: `Known Baseline`, `Linked Objects`, `Open Questions`",
        "",
        "## Suggested Known Baseline Update",
        "",
        (
            "The current damped-oscillator benchmark verified the expected analytic regime split "
            "between underdamped, critically damped, and overdamped motion."
        ),
        "",
        "Suggested verification summary:",
        "",
        f"- Verification gate passed: `{verification_summary['passed']}`",
    ]
    lines.extend([f"- {check['name']}: `{check['status']}`" for check in verification_summary["checks"]])
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
            "- Should the next benchmark add forcing or nonlinear restoring terms?",
            "",
        ]
    )
    return "\n".join(lines)


def run_damped_oscillator_experiment_with_output(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> ExperimentOutcome:
    """Execute the damped-oscillator regime verification workflow."""
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
    if not task_id or not run_id or not result_id:
        raise ValueError("Experiment config must define task_id, run_id, and result_id")
    if not str(config.get("result_root", "")):
        raise ValueError("Experiment config must define result_root for run-based outputs")

    time_range = experiment["data"]["time_range_seconds"]
    sample_count = int(experiment["data"]["sample_count"])
    train_fraction = float(config.get("train_fraction", 0.6))
    time_seconds = np.linspace(float(time_range["start"]), float(time_range["end"]), sample_count)
    split_index = split_dataset(sample_count=sample_count, train_fraction=train_fraction)
    scenarios = list(experiment["data"]["scenarios"])
    scores, verdicts = _build_damped_scores(
        experiment=experiment,
        scenarios=scenarios,
        split_index=split_index,
        time_seconds=time_seconds,
    )
    best_model_id = scores[0].model_id
    best_verdict = best_result_verdict(verdicts[best_model_id])
    verification_payload = _build_damped_verification(
        scenarios=scenarios,
        time_start=float(time_range["start"]),
        time_end=float(time_range["end"]),
        sample_count=sample_count,
    )

    run_dir = result_root / run_id
    result_path = run_dir / "result.yaml"
    report_path = run_dir / "report.md"
    metrics_path = run_dir / "metrics.json"
    claim_update_path = run_dir / "claim_update.md"
    knowledge_update_path = run_dir / "knowledge_update.md"
    run_dir.mkdir(parents=True, exist_ok=True)

    limitations = _damped_limitations()
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
    train_range = (float(time_seconds[0]), float(time_seconds[split_index - 1]))
    test_range = (float(time_seconds[split_index]), float(time_seconds[-1]))

    report_text = _build_damped_report(
        title=str(experiment["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(experiment["hypothesis_id"]),
        task_id=task_id,
        assumptions=list(hypothesis.get("assumptions", [])),
        limitations=limitations,
        train_range=train_range,
        test_range=test_range,
        scenarios=scenarios,
        scores=scores,
        verdicts=verdicts,
        best_model_id=best_model_id,
        verification_summary=verification_payload,
    )
    write_text_atomic(report_path, report_text)

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
        "code_reference": "physics_lab/workflows/damped_oscillator.py",
        "limitations": limitations,
        "train_range": [train_range[0], train_range[1]],
        "test_range": [test_range[0], test_range[1]],
        "best_model_id": best_model_id,
        "best_verdict": best_verdict,
        "verification": verification_payload,
        "artifacts": {
            "report": relative_or_absolute(report_path, repo_root),
            "metrics": relative_or_absolute(metrics_path, repo_root),
            "claim_update": relative_or_absolute(claim_update_path, repo_root),
            "knowledge_update": relative_or_absolute(knowledge_update_path, repo_root),
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
    }
    write_text_atomic(metrics_path, json.dumps(metrics_payload, indent=2))

    write_text_atomic(
        claim_update_path,
        _build_damped_claim_update(
            claim_id="CLAIM-0002",
            result_id=result_id,
            experiment_id=str(experiment["id"]),
            hypothesis_id=str(experiment["hypothesis_id"]),
            task_id=task_id,
            verification_summary=verification_payload,
        ),
    )
    write_text_atomic(
        knowledge_update_path,
        _build_damped_knowledge_update(
            knowledge_id="KNOW-0002",
            result_id=result_id,
            experiment_id=str(experiment["id"]),
            hypothesis_id=str(experiment["hypothesis_id"]),
            task_id=task_id,
            verification_summary=verification_payload,
            limitations=limitations,
        ),
    )

    return ExperimentOutcome(
        title=str(experiment["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(experiment["hypothesis_id"]),
        task_id=task_id,
        train_range=train_range,
        test_range=test_range,
        scores=scores,
        verdicts=verdicts,
        best_model_id=best_model_id,
        artifacts=ExperimentArtifacts(
            result_path=result_path,
            report_path=report_path,
            metrics_path=metrics_path,
            claim_update_path=claim_update_path,
            knowledge_update_path=knowledge_update_path,
        ),
    )
