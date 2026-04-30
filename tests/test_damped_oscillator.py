from pathlib import Path

from physics_lab.engines.damped_oscillator import (
    DampedOscillatorParameters,
    classify_damping_regime,
    generate_damped_oscillator_dataset,
)
from physics_lab.registry import load_claim, load_experiment, load_hypothesis, load_knowledge, load_task
from physics_lab.registry.results import load_result
from physics_lab.workflows.runner import run_damped_oscillator_experiment_with_output


def test_damped_oscillator_regime_classification() -> None:
    underdamped = DampedOscillatorParameters(mass=1.0, damping=0.5, stiffness=4.0, x0=1.0, v0=0.0)
    critical = DampedOscillatorParameters(mass=1.0, damping=4.0, stiffness=4.0, x0=1.0, v0=0.0)
    overdamped = DampedOscillatorParameters(mass=1.0, damping=5.0, stiffness=4.0, x0=1.0, v0=0.0)

    assert classify_damping_regime(underdamped) == "underdamped"
    assert classify_damping_regime(critical) == "critical"
    assert classify_damping_regime(overdamped) == "overdamped"


def test_damped_oscillator_dataset_energy_decays() -> None:
    parameters = DampedOscillatorParameters(
        mass=1.0,
        damping=0.4,
        stiffness=4.0,
        x0=1.0,
        v0=0.0,
    )
    dataset = generate_damped_oscillator_dataset(
        time_start=0.0,
        time_end=10.0,
        sample_count=200,
        parameters=parameters,
    )

    assert dataset.regime == "underdamped"
    assert dataset.energy[0] > dataset.energy[-1]


def test_damped_oscillator_registry_files_validate() -> None:
    load_hypothesis("hypotheses/HYP-0002-damped-oscillator-regimes.yaml")
    load_experiment("experiments/EXP-0002-damped-oscillator-regimes.yaml")
    load_task("tasks/TASK-0002-verify-damped-oscillator-regimes.yaml")
    load_claim("claims/CLAIM-0002-damped-oscillator-regimes.md")
    load_knowledge("knowledge/classical_mechanics/damped_oscillator.md")


def test_damped_oscillator_runner_writes_temp_artifacts(tmp_path) -> None:
    outcome = run_damped_oscillator_experiment_with_output(
        config_path=Path("examples/damped_oscillator.yaml"),
        output_dir=tmp_path / "apl-results",
    )

    result_path = tmp_path / "apl-results" / "EXP-0002" / "RUN-0001" / "result.yaml"
    assert outcome.result_id == "RESULT-0002"
    assert result_path.exists()

    result_payload = load_result(result_path)
    check_names = {check["name"] for check in result_payload["verification"]["checks"]}

    assert result_payload["experiment_id"] == "EXP-0002"
    assert result_payload["best_verdict"] == "VALID_IN_RANGE"
    assert result_payload["verification"]["passed"] is True
    assert {
        "regime_classification",
        "initial_condition_recovery",
        "underdamped_energy_decay",
        "oscillatory_vs_nonoscillatory_behavior",
        "dimensional_consistency",
    } <= check_names
