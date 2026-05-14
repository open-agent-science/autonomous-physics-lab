from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from physics_lab.cli import app
from physics_lab.engines.nuclear_mass_baselines import (
    REFERENCE_SEMI_EMPIRICAL_COEFFICIENTS,
    evaluate_baseline,
    fit_semi_empirical_coefficients,
    pairing_class,
    pairing_sign,
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset
from physics_lab.registry import load_claim, load_experiment, load_hypothesis, load_knowledge, load_task
from physics_lab.registry.results import load_result
from physics_lab.workflows.nuclear_mass_baseline import run_nuclear_mass_baseline_experiment_with_output
from physics_lab.workflows.runner import run_experiment_with_output


def test_pairing_helpers_classify_even_odd_structure() -> None:
    assert pairing_sign(8, 8) == 1
    assert pairing_sign(7, 7) == -1
    assert pairing_sign(8, 9) == 0
    assert pairing_class(8, 8) == "even_even"
    assert pairing_class(7, 7) == "odd_odd"
    assert pairing_class(8, 9) == "odd_a"


def test_reference_semi_empirical_binding_energy_is_reasonable_for_helium_four() -> None:
    binding_energy = semi_empirical_binding_energy(
        z=2,
        n=2,
        coefficients=REFERENCE_SEMI_EMPIRICAL_COEFFICIENTS,
    )
    assert 20.0 <= binding_energy <= 35.0


def test_fitted_baseline_improves_overall_mae_on_curated_slice() -> None:
    dataset = load_nuclear_mass_dataset("data/nuclear_masses/nmd-0002-curated-measured-slice.yaml")
    reference_rows = evaluate_baseline(
        entries=dataset.entries,
        model_id="model_reference_semi_empirical",
        coefficients=REFERENCE_SEMI_EMPIRICAL_COEFFICIENTS,
    )
    fitted_coefficients = fit_semi_empirical_coefficients(dataset.entries)
    fitted_rows = evaluate_baseline(
        entries=dataset.entries,
        model_id="model_fitted_semi_empirical",
        coefficients=fitted_coefficients,
    )

    reference_mae = sum(abs(row.residual_mev) for row in reference_rows) / len(reference_rows)
    fitted_mae = sum(abs(row.residual_mev) for row in fitted_rows) / len(fitted_rows)
    assert fitted_mae < reference_mae


def test_nuclear_mass_registry_files_validate() -> None:
    load_hypothesis("hypotheses/HYP-0012-nuclear-mass-baseline.yaml")
    load_experiment("experiments/EXP-0012-nuclear-mass-baseline.yaml")
    load_task("tasks/TASK-0168-implement-nuclear-mass-baselines-and-residual-reports.yaml")
    load_claim("claims/CLAIM-0010-nuclear-mass-baseline.md")
    load_knowledge("knowledge/nuclear_physics/nuclear_mass_baseline.md")


def test_nuclear_mass_runner_writes_temp_artifacts(tmp_path: Path) -> None:
    outcome = run_nuclear_mass_baseline_experiment_with_output(
        config_path=Path("examples/nuclear_mass_baseline.yaml"),
        output_dir=tmp_path / "apl-results",
    )

    result_path = tmp_path / "apl-results" / "EXP-0012" / "RUN-0001" / "result.yaml"
    assert outcome.result_id == "RESULT-0015"
    assert result_path.exists()

    result_payload = load_result(result_path)
    check_names = {check["name"] for check in result_payload["verification"]["checks"]}
    assert result_payload["experiment_id"] == "EXP-0012"
    assert result_payload["best_verdict"] in {"VALID_IN_RANGE", "PARTIALLY_VALID", "INCONCLUSIVE"}
    assert {
        "dataset_slice_loaded",
        "binding_energy_reconstruction",
        "fitted_baseline_improves_overall_mae",
        "pairing_term_reduces_pairing_spread",
        "magic_subset_diagnostics_present",
        "uncertainty_normalized_residuals_present",
    } <= check_names


def test_nuclear_mass_dispatch_writes_temp_artifacts(tmp_path: Path) -> None:
    outcome = run_experiment_with_output(
        config_path=Path("examples/nuclear_mass_baseline.yaml"),
        output_dir=tmp_path / "apl-results",
    )

    assert outcome.result_id == "RESULT-0015"
    assert outcome.artifacts.result_path == tmp_path / "apl-results" / "EXP-0012" / "RUN-0001" / "result.yaml"


def test_cli_run_nuclear_mass_baseline_smoke(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "run",
            "examples/nuclear_mass_baseline.yaml",
            "--output-dir",
            str(tmp_path / "apl-nuclear-mass-test"),
        ],
    )

    assert result.exit_code == 0
    assert "Completed: Nuclear Mass Baseline Residual Benchmark" in result.stdout
