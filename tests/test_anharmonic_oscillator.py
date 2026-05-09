from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from physics_lab.cli import app
from physics_lab.engines.anharmonic_oscillator import (
    AnharmonicOscillatorParameters,
    anharmonicity_ratio,
    fit_empirical_quadratic_ratio,
    generate_reference_samples,
    perturbative_period,
    reference_period,
)
from physics_lab.registry import load_claim, load_experiment, load_hypothesis, load_knowledge, load_task
from physics_lab.registry.results import load_result
from physics_lab.workflows.runner import run_anharmonic_oscillator_experiment_with_output, run_experiment_with_output


def test_reference_period_matches_harmonic_limit() -> None:
    parameters = AnharmonicOscillatorParameters(mass=1.0, stiffness=1.0, quartic_coefficient=0.0)
    period = reference_period(parameters, amplitude=1.2)

    assert abs(period - parameters.harmonic_period) <= 1.0e-10


def test_perturbative_period_is_accurate_in_weak_regime() -> None:
    parameters = AnharmonicOscillatorParameters(mass=1.0, stiffness=1.0, quartic_coefficient=0.02)
    amplitude = 1.0
    reference_value = reference_period(parameters, amplitude)
    perturbative_value = perturbative_period(parameters, amplitude)
    relative_error = abs(perturbative_value - reference_value) / reference_value

    assert anharmonicity_ratio(parameters, amplitude) == 0.02
    assert relative_error < 0.01


def test_empirical_quadratic_fit_improves_holdout_error() -> None:
    amplitudes = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2]
    quartic_coefficients = [0.02, 0.04, 0.06, 0.08]
    samples = generate_reference_samples(
        mass=1.0,
        stiffness=1.0,
        amplitudes=amplitudes,
        quartic_coefficients=quartic_coefficients,
    )
    train = [sample for sample in samples if sample.anharmonicity_ratio <= 0.05]
    holdout = [sample for sample in samples if 0.05 < sample.anharmonicity_ratio <= 0.10]
    coefficients = fit_empirical_quadratic_ratio(train, mass=1.0, stiffness=1.0)

    perturbative_errors = []
    empirical_errors = []
    for sample in holdout:
        parameters = AnharmonicOscillatorParameters(
            mass=1.0,
            stiffness=1.0,
            quartic_coefficient=sample.quartic_coefficient,
        )
        perturbative_errors.append(
            abs(perturbative_period(parameters, sample.amplitude) - sample.reference_period) / sample.reference_period
        )
        empirical_value = parameters.harmonic_period * (
            1.0
            + coefficients["a"] * sample.anharmonicity_ratio
            + coefficients["b"] * sample.anharmonicity_ratio**2
        )
        empirical_errors.append(abs(empirical_value - sample.reference_period) / sample.reference_period)

    assert sum(empirical_errors) / len(empirical_errors) < sum(perturbative_errors) / len(perturbative_errors)


def test_anharmonic_registry_files_validate() -> None:
    load_hypothesis("hypotheses/HYP-0011-anharmonic-oscillator-period.yaml")
    load_experiment("experiments/EXP-0011-anharmonic-oscillator-period.yaml")
    load_task("tasks/TASK-0159-implement-anharmonic-oscillator-period-benchmark.yaml")
    load_claim("claims/CLAIM-0009-anharmonic-oscillator-period.md")
    load_knowledge("knowledge/classical_mechanics/anharmonic_oscillator.md")


def test_anharmonic_runner_writes_temp_artifacts(tmp_path: Path) -> None:
    outcome = run_anharmonic_oscillator_experiment_with_output(
        config_path=Path("examples/anharmonic_oscillator.yaml"),
        output_dir=tmp_path / "apl-results",
    )

    result_path = tmp_path / "apl-results" / "EXP-0011" / "RUN-0001" / "result.yaml"
    assert outcome.result_id == "RESULT-0014"
    assert result_path.exists()

    result_payload = load_result(result_path)
    check_names = {check["name"] for check in result_payload["verification"]["checks"]}

    assert result_payload["experiment_id"] == "EXP-0011"
    assert result_payload["best_verdict"] in {"VALID_IN_RANGE", "PARTIALLY_VALID"}
    assert {
        "harmonic_limit",
        "perturbative_train_window",
        "holdout_generalization",
        "monotonic_hardening",
        "perturbative_breakdown_mapping",
    } <= check_names


def test_anharmonic_dispatch_writes_temp_artifacts(tmp_path: Path) -> None:
    outcome = run_experiment_with_output(
        config_path=Path("examples/anharmonic_oscillator.yaml"),
        output_dir=tmp_path / "apl-results",
    )

    assert outcome.result_id == "RESULT-0014"
    assert outcome.artifacts.result_path == tmp_path / "apl-results" / "EXP-0011" / "RUN-0001" / "result.yaml"


def test_cli_run_anharmonic_smoke() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["run", "examples/anharmonic_oscillator.yaml", "--output-dir", "/tmp/apl-anharmonic-test"],
    )

    assert result.exit_code == 0
    assert "Completed: Anharmonic Oscillator Period Benchmark" in result.stdout
