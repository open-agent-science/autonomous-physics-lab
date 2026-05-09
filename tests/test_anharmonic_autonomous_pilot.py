from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from physics_lab.engines.anharmonic_oscillator import AnharmonicOscillatorParameters, generate_reference_samples
from physics_lab.registry.agent_runs import load_agent_run
from physics_lab.registry.experiments import load_experiment


def _relative_metrics(predicted: np.ndarray, expected: np.ndarray) -> dict[str, float]:
    rel = np.abs(predicted - expected) / expected
    return {
        "mean_relative_error": float(rel.mean()),
        "max_relative_error": float(rel.max()),
    }


def _classify_candidate(*, train_mean: float, holdout_mean: float, holdout_max: float) -> str:
    if holdout_mean <= 0.01 and holdout_max <= 0.025:
        return "VALID"
    if holdout_mean <= 0.03 and holdout_max <= 0.08:
        return "PARTIALLY_VALID"
    if train_mean > 0.0 and holdout_mean / train_mean >= 3.0:
        return "OVERFITTED"
    return "INVALID"


def test_anharmonic_autonomous_pilot_metrics_recompute() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    metrics_path = repo_root / "agent_runs" / "AGENT-RUN-0004" / "metrics.json"
    agent_run_path = repo_root / "agent_runs" / "AGENT-RUN-0004" / "agent_run.yaml"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    agent_run = load_agent_run(agent_run_path, root=repo_root)
    experiment = load_experiment(repo_root / "experiments" / "EXP-0011-anharmonic-oscillator-period.yaml")
    data = experiment["data"]
    amplitudes = np.linspace(
        float(data["amplitude_range"]["start"]),
        float(data["amplitude_range"]["end"]),
        int(data["amplitude_range"]["sample_count"]),
    )
    quartic_coefficients = [float(value) for value in data["quartic_coefficients"]]
    samples = generate_reference_samples(
        mass=float(data["mass"]),
        stiffness=float(data["stiffness"]),
        amplitudes=amplitudes,
        quartic_coefficients=quartic_coefficients,
    )
    train = [sample for sample in samples if sample.anharmonicity_ratio <= float(data["train_max_anharmonicity"])]
    holdout = [
        sample
        for sample in samples
        if float(data["train_max_anharmonicity"]) < sample.anharmonicity_ratio <= float(data["holdout_max_anharmonicity"])
    ]
    stress = [
        sample
        for sample in samples
        if float(data["holdout_max_anharmonicity"]) < sample.anharmonicity_ratio <= float(data["stress_max_anharmonicity"])
    ]

    def ratios(samples_subset: list) -> np.ndarray:
        values: list[float] = []
        for sample in samples_subset:
            params = AnharmonicOscillatorParameters(
                mass=float(data["mass"]),
                stiffness=float(data["stiffness"]),
                quartic_coefficient=float(sample.quartic_coefficient),
            )
            values.append(sample.reference_period / params.harmonic_period)
        return np.asarray(values, dtype=float)

    train_ratio = ratios(train)
    holdout_ratio = ratios(holdout)
    stress_ratio = ratios(stress)
    train_epsilon = np.asarray([sample.anharmonicity_ratio for sample in train], dtype=float)
    holdout_epsilon = np.asarray([sample.anharmonicity_ratio for sample in holdout], dtype=float)
    stress_epsilon = np.asarray([sample.anharmonicity_ratio for sample in stress], dtype=float)
    train_amplitude = np.asarray([sample.amplitude for sample in train], dtype=float)
    holdout_amplitude = np.asarray([sample.amplitude for sample in holdout], dtype=float)
    stress_amplitude = np.asarray([sample.amplitude for sample in stress], dtype=float)

    assert agent_run["campaign_profile_id"] == "anharmonic-oscillator"
    assert metrics["summary"]["generated_proposal_count"] == 6
    assert metrics["summary"]["executed_candidate_count"] == 2
    assert metrics["summary"]["rejected_before_execution_count"] == 4
    assert len(metrics["executed_items"]) == 2

    for item in metrics["executed_items"]:
        family = item["family"]
        if family == "pade11_epsilon":
            lhs = np.column_stack([train_epsilon, -train_epsilon * train_ratio])
            coeff = np.linalg.lstsq(lhs, train_ratio - 1.0, rcond=None)[0]

            def predict(x: np.ndarray) -> np.ndarray:
                return (1.0 + coeff[0] * x) / (1.0 + coeff[1] * x)

            expected_coefficients = {"a": float(coeff[0]), "b": float(coeff[1])}
            train_pred = predict(train_epsilon)
            holdout_pred = predict(holdout_epsilon)
            stress_pred = predict(stress_epsilon)
        elif family == "amp2_only":
            coeff = np.linalg.lstsq((train_amplitude**2)[:, None], train_ratio - 1.0, rcond=None)[0]

            def predict(x: np.ndarray) -> np.ndarray:
                return 1.0 + coeff[0] * x**2

            expected_coefficients = {"c": float(coeff[0])}
            train_pred = predict(train_amplitude)
            holdout_pred = predict(holdout_amplitude)
            stress_pred = predict(stress_amplitude)
        else:
            raise AssertionError(f"Unexpected family: {family}")

        for key, value in expected_coefficients.items():
            assert abs(item["coefficients"][key] - value) <= 1.0e-12

        train_metrics = _relative_metrics(train_pred, train_ratio)
        holdout_metrics = _relative_metrics(holdout_pred, holdout_ratio)
        stress_metrics = _relative_metrics(stress_pred, stress_ratio)

        for field in ("mean_relative_error", "max_relative_error"):
            assert abs(item["train_metrics"][field] - train_metrics[field]) <= 1.0e-12
            assert abs(item["holdout_metrics"][field] - holdout_metrics[field]) <= 1.0e-12
            assert abs(item["stress_metrics"][field] - stress_metrics[field]) <= 1.0e-12

        expected_verdict = _classify_candidate(
            train_mean=train_metrics["mean_relative_error"],
            holdout_mean=holdout_metrics["mean_relative_error"],
            holdout_max=holdout_metrics["max_relative_error"],
        )
        assert item["expected_verdict"] == expected_verdict
        assert item["observed_verdict"] == expected_verdict
        assert item["agrees"] is True
