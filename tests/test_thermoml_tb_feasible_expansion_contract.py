from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/thermophysical/thermoml_tb_feasible_expansion_contract.yaml"


def _load() -> dict:
    return yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))


def _all_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return {str(key) for key in value} | {
            nested_key for nested in value.values() for nested_key in _all_keys(nested)
        }
    if isinstance(value, list):
        return {nested_key for nested in value for nested_key in _all_keys(nested)}
    return set()


def test_contract_is_value_blind_and_non_executable() -> None:
    contract = _load()
    boundary = contract["adjudication_boundary"]

    assert contract["task_id"] == "TASK-1084"
    assert contract["verdict"] == "REVISED_CONTRACT_READY_NO_SCORE"
    assert contract["planning_only"] is True
    assert contract["execution_authorized"] is False
    assert contract["benchmark_authorized"] is False
    assert all(value is False for key, value in boundary.items() if key.endswith("_accessed"))


def test_option_counts_and_effective_information_are_count_driven() -> None:
    contract = _load()
    caps = contract["family_caps"]
    selected = next(option for option in contract["predeclared_options"] if option.get("selected"))

    assert len(caps) == 8
    assert sum(item["existing_row_count"] for item in caps) == 40
    assert sum(item["revised_row_cap"] for item in caps) == 74
    assert sum(item["maximum_additions"] for item in caps) == 34
    expected_effective_rows = 64.0 / sum(1.0 / item["revised_row_cap"] for item in caps)
    assert selected["equal_family_weighted_effective_row_count"] == pytest.approx(
        expected_effective_rows, abs=1e-6
    )
    assert selected["option_id"] == "availability_capped_family_equal_weighting"


def test_selected_option_clears_predeclared_incremental_floor() -> None:
    contract = _load()
    floor = contract["incremental_information_rule"]
    selected = contract["selected_option"]
    caps = contract["family_caps"]

    assert floor["declared_before_option_selection"] is True
    assert selected["maximum_total_rows"] >= floor["minimum_total_rows"]
    assert selected["maximum_new_identities"] >= floor["minimum_new_identities_vs_existing_fixture"]
    assert min(item["revised_row_cap"] for item in caps) >= floor["minimum_rows_per_family"]
    assert floor["required_effective_family_count"] == 8.0
    assert floor["minimum_equal_family_weighted_effective_row_count"] == 64.0


def test_rights_and_selection_boundaries_remain_frozen() -> None:
    contract = _load()
    rights = contract["rights"]
    selection = contract["deterministic_selection"]

    assert rights["max_public_rows_total"] == 80
    assert rights["max_rows_per_source_article"] == 5
    assert rights["covered_by_repo_license"] is False
    assert rights["raw_archive_bytes_allowed"] is False
    assert rights["normalized_corpus_allowed"] is False
    assert rights["external_dataset_release_allowed"] is False
    assert selection["existing_fixture_identities_excluded_from_addition_pool"] is True
    assert selection["source_article_cap_applies_across_existing_and_added_rows"] is True
    assert selection["identities_and_counts_frozen_before_scoring"] is True
    assert selection["outcome_or_residual_based_selection_allowed"] is False


def test_future_split_controls_weighting_and_routes_are_predeclared() -> None:
    contract = _load()
    weighting = contract["future_weighting"]
    protocol = contract["future_split_and_controls"]
    routing = contract["future_verdict_routing"]

    assert weighting["family_weight"] == 0.125
    assert weighting["pooled_unweighted_rows_can_determine_verdict"] is False
    assert protocol["split"] == "leave_one_family_out_eight_folds"
    assert protocol["survival_margin_k"] == 5.0
    assert protocol["minimum_families_clearing_margin"] == 6
    assert protocol["shuffle_seed"] == 851
    assert protocol["controls"] == [
        "global_median",
        "molecular_weight_only",
        "nearest_homolog",
        "shuffled_group_counts",
        "within_family_constant",
    ]
    assert "PASS_TRANSFER_SUPPORTED_IN_SCOPE" in routing["pass"]
    assert "FAIL_CONTROL_DOMINATED" in routing["fail"]
    assert "INCONCLUSIVE_FAMILY_DEPENDENT" in routing["inconclusive"]
    assert routing["post_score_threshold_or_route_change_allowed"] is False


def test_contract_contains_no_rows_values_scores_or_result_mutation() -> None:
    contract = _load()
    keys = _all_keys(contract)

    for forbidden_key in (
        "rows",
        "selected_identities",
        "experimental_tb_k",
        "observed_scores",
        "family_performance",
        "result_id",
    ):
        assert forbidden_key not in keys
    assert contract["output_routing"]["gate_a"] == "not_attempted"
    assert contract["output_routing"]["gate_b"] == "not_applicable"
    assert contract["output_routing"]["existing_results_changed"] is False
