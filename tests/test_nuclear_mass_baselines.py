from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from physics_lab.cli import app
from physics_lab.engines.nmd0003_baseline_family_gate import run_nmd0003_baseline_family_gate
from physics_lab.engines.nmd0003_duflo_zuker_baseline import (
    FEATURE_NAMES,
    duflo_zuker_design_matrix,
    run_nmd0003_duflo_zuker_baseline,
)
from physics_lab.engines.nuclear_mass_baselines import (
    REFERENCE_SEMI_EMPIRICAL_COEFFICIENTS,
    design_matrix,
    evaluate_baseline,
    fit_semi_empirical_coefficients,
    fit_semi_empirical_coefficients_ridge,
    fit_semi_empirical_coefficients_weighted,
    pairing_class,
    pairing_sign,
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset
from physics_lab.registry import load_claim, load_experiment, load_hypothesis, load_knowledge, load_task
from physics_lab.registry.task_discovery import find_task_file
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


def test_weighted_least_squares_matches_ols_for_uniform_weights() -> None:
    dataset = load_nuclear_mass_dataset("data/nuclear_masses/nmd-0002-curated-measured-slice.yaml")
    ols = fit_semi_empirical_coefficients(dataset.entries)
    uniform = fit_semi_empirical_coefficients_weighted(
        dataset.entries, weights=[1.0] * len(dataset.entries)
    )
    for key in ("volume", "surface", "coulomb", "asymmetry", "pairing"):
        assert getattr(uniform, key) == pytest.approx(getattr(ols, key), rel=1e-6)


def test_weighted_least_squares_rejects_mismatched_weight_length() -> None:
    dataset = load_nuclear_mass_dataset("data/nuclear_masses/nmd-0002-curated-measured-slice.yaml")
    with pytest.raises(ValueError):
        fit_semi_empirical_coefficients_weighted(dataset.entries, weights=[1.0, 2.0])


def test_ridge_shrinks_coefficients_toward_zero_as_alpha_grows() -> None:
    dataset = load_nuclear_mass_dataset("data/nuclear_masses/nmd-0002-curated-measured-slice.yaml")
    ols = fit_semi_empirical_coefficients(dataset.entries)
    weak = fit_semi_empirical_coefficients_ridge(dataset.entries, alpha=1e-9)
    strong = fit_semi_empirical_coefficients_ridge(dataset.entries, alpha=1000.0)
    # A negligible penalty reproduces the ordinary least-squares solution.
    for key in ("volume", "surface", "coulomb", "asymmetry", "pairing"):
        assert getattr(weak, key) == pytest.approx(getattr(ols, key), rel=1e-4)
    # A large penalty shrinks the standardized coefficients, lowering the
    # dominant volume term magnitude.
    assert abs(strong.volume) < abs(ols.volume)


def test_design_matrix_shape_matches_entries() -> None:
    dataset = load_nuclear_mass_dataset("data/nuclear_masses/nmd-0002-curated-measured-slice.yaml")
    matrix = design_matrix(dataset.entries)
    assert matrix.shape == (len(dataset.entries), 5)


def test_baseline_family_gate_separates_domain_mismatch_from_family_weakness() -> None:
    config = Path("examples/benchmarks/nuclear_mass_baseline_family_nmd0003.yaml")
    metrics = run_nmd0003_baseline_family_gate(config)

    assert metrics["task_id"] == "TASK-0535"
    assert metrics["verdict"] == "INCONCLUSIVE"
    assert set(metrics["splits"]) == {"sorted_aZN_70_30", "stratified_interleaved_70_30"}

    expected_families = {
        "inherited_result0015_nmd0002_frozen",
        "nmd0003_train_fitted_ols",
        "nmd0003_train_fitted_wls",
        "nmd0003_train_fitted_ridge",
        "nmd0003_region_stratified_diagnostic",
    }
    for split in metrics["splits"].values():
        assert set(split["baseline_summaries"]) == expected_families

    sensitivity = metrics["split_sensitivity_diagnostic"]["per_family"]["nmd0003_train_fitted_ols"]
    # The OLS refit regresses on the sorted (extrapolation) holdout but improves
    # on the stratified (interpolation) holdout: the domain-mismatch signature.
    assert sensitivity["sorted_validation_mae_relative_improvement"] < 0.0
    assert sensitivity["stratified_validation_mae_relative_improvement"] > 0.0
    assert sensitivity["domain_mismatch_signature"] is True
    assert (
        metrics["split_sensitivity_diagnostic"]["dominant_factor"]
        == "domain_mismatch_extrapolation_split"
    )

    # Region coefficient drift is reported and non-trivial.
    assert metrics["region_coefficient_diagnostic"]["max_relative_coefficient_range"] > 0.0

    recommendation = metrics["recommendation"]["decision"]
    assert recommendation in {
        "promote a scoped baseline benchmark result",
        "create_narrower_baseline_follow_up",
        "permit a bounded residual-feature sprint with the winning baseline frozen",
        "pause_nuclear_factory_work_until_baseline_or_split_coverage_improves",
    }


def test_baseline_family_gate_is_deterministic() -> None:
    config = Path("examples/benchmarks/nuclear_mass_baseline_family_nmd0003.yaml")
    first = run_nmd0003_baseline_family_gate(config)
    second = run_nmd0003_baseline_family_gate(config)
    assert first == second


def test_duflo_zuker_structured_design_and_benchmark_are_deterministic() -> None:
    dataset = load_nuclear_mass_dataset("data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml")
    matrix = duflo_zuker_design_matrix(dataset.entries[:5])

    assert matrix.shape == (5, len(FEATURE_NAMES))

    first = run_nmd0003_duflo_zuker_baseline()
    second = run_nmd0003_duflo_zuker_baseline()
    assert first == second
    assert first["task_id"] == "TASK-0823"
    assert first["dataset_summary"]["post_ame2020_rows_used_for_fit"] == 0
    assert first["model_scope"]["not_canonical_dz10_code"] is True


def test_nuclear_mass_registry_files_validate() -> None:
    load_hypothesis("hypotheses/HYP-0012-nuclear-mass-baseline.yaml")
    load_experiment("experiments/EXP-0012-nuclear-mass-baseline.yaml")
    load_task(find_task_file(".", "TASK-0168"))
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
