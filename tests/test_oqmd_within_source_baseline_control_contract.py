from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/reviews/materials/oqmd-within-source-baseline-control-contract.yaml"


def _load_contract() -> dict:
    return yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))


def test_contract_is_value_blind_and_non_scoring() -> None:
    contract = _load_contract()
    authorship = contract["authorship"]
    routing = contract["routing"]

    assert contract["verdict"] == "CONTRACT_READY_FOR_FROZEN_SPLIT"
    assert authorship["no_oqmd_target_access"] is True
    assert authorship["target_values_or_aggregates_inspected"] is False
    assert routing["split_created"] is False
    assert routing["metrics_computed"] is False
    assert routing["result_created"] is False


def test_contract_freezes_required_model_controls_and_metrics() -> None:
    contract = _load_contract()

    assert contract["primary_model"]["model_id"] == (
        "unordered_non_oxygen_cation_pair_train_mean"
    )
    assert contract["primary_model"]["fit_scope"] == "train_only"
    assert len(contract["required_nulls"]) == 2
    assert contract["required_controls"]["label_shuffle"]["seeds"] == [
        1054,
        2054,
        3054,
        4054,
        5054,
    ]
    assert contract["required_controls"]["row_order_invariance"]["variants"] == [
        "canonical_entry_id_order",
        "reversed_entry_id_order",
    ]
    assert contract["metrics"]["primary"]["name"] == "MAE"
    assert contract["metrics"]["secondary"]["name"] == "RMSE"


def test_contract_fails_closed_and_forbids_cross_database_pooling() -> None:
    contract = _load_contract()
    scope = contract["scientific_scope"]
    gate = contract["survival_gate"]

    assert scope["within_source_only"] is True
    assert scope["materials_project_numeric_pooling_allowed"] is False
    assert scope["field_equality_claim_allowed"] is False
    assert gate["absolute_margin_eV_per_atom"] == 0.02
    assert gate["relative_margin_fraction"] == 0.05
    assert gate["ties_within_tolerance"] == "fail"
    assert gate["all_sensitivity_seeds_must_pass"] is True
    assert "CONTRACT_CONTAMINATED" in contract["stop_conditions"]
