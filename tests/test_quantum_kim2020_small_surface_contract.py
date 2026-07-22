from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/quantum_dots/kim2020_cdse_small_surface_benchmark_contract.yaml"
ABSORPTION = ROOT / "data/quantum_dots/qd-0005-kim-2020-cdse-absorption.yaml"
EMISSION = ROOT / "data/quantum_dots/qd-0006-kim-2020-cdse-emission.yaml"


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_contract_holds_current_surface_without_execution() -> None:
    contract = _load(CONTRACT)

    assert contract["task_id"] == "TASK-1077"
    assert contract["planning_only"] is True
    assert contract["execution_authorized"] is False
    assert contract["verdict"] == "HOLD_UNDERPOWERED"
    assert contract["output_routing"]["benchmark_readiness"] == "HOLD_UNDERPOWERED"


def test_contract_reverifies_four_groups_and_source_metadata_per_axis() -> None:
    contract = _load(CONTRACT)
    absorption = _load(ABSORPTION)
    emission = _load(EMISSION)
    surface = contract["source_surface"]

    assert len(absorption["entries"]) == len(emission["entries"]) == 4
    assert {row["sample_id"] for row in absorption["entries"]} == {
        row["sample_id"] for row in emission["entries"]
    }
    assert surface["shared_sample_group_count"] == 4
    assert {axis["axis_id"] for axis in surface["axes"]} == {
        "absorption_peak_eV",
        "emission_peak_eV",
    }

    for row in absorption["entries"] + emission["entries"]:
        assert row["provenance_class"] == surface["provenance_class"]
        assert row["printed_precision_eV"] == surface["printed_precision_eV"]
        assert row["rounding_uncertainty_floor_eV"] == surface["rounding_uncertainty_floor_eV"]
        assert row["instrument_uncertainty"] == surface["instrument_uncertainty"]
        assert row["morphology"] == surface["morphology"]


def test_contract_freezes_one_candidate_family_controls_and_separate_axes() -> None:
    contract = _load(CONTRACT)

    assert contract["candidate_family"]["family_count"] == 1
    assert contract["candidate_family"]["parameter_count"] == 2
    assert [control["control_id"] for control in contract["null_controls"]] == [
        "train_mean",
        "affine_diameter_trend",
    ]
    assert contract["axis_policy"]["fit_and_score_separately"] is True
    assert contract["axis_policy"]["pooled_residual_metric_allowed"] is False
    assert contract["axis_policy"]["paired_stokes_shift_axis_enabled"] is False
    assert contract["metrics"]["primary"] == ["grouped_leave_one_out_mae_eV"]


def test_information_rule_rejects_exactly_determined_deletion_fits() -> None:
    contract = _load(CONTRACT)
    diagnostic = contract["resampling"]["current_surface_diagnostic"]
    minimum = contract["minimum_information_rule"]

    assert diagnostic["groups_after_outer_deletion"] == 3
    assert diagnostic["inner_loo_training_groups"] == 2
    assert diagnostic["candidate_parameter_count"] == 2
    assert diagnostic["inner_training_residual_degrees_of_freedom"] == 0
    assert minimum["minimum_groups_per_axis"] == 8
    assert minimum["minimum_inner_training_residual_degrees_of_freedom"] == 4
    assert minimum["current_surface_passes_group_floor"] is False
    assert minimum["current_surface_passes_uncertainty_requirement"] is False


def test_contract_contains_no_observed_scores_or_result_promotion() -> None:
    contract = _load(CONTRACT)
    serialized = yaml.safe_dump(contract, sort_keys=True)

    for forbidden_key in (
        "observed_scores:",
        "fit_coefficients:",
        "result_id:",
        "hypothesis_id:",
        "experiment_id:",
    ):
        assert forbidden_key not in serialized
    assert contract["output_routing"]["gate_a"] == "not_attempted"
    assert contract["output_routing"]["gate_b"] == "not_applicable"
    assert contract["output_routing"]["claim_impact"] == "none"
    assert contract["output_routing"]["knowledge_impact"] == "none"
