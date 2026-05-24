from __future__ import annotations

from pathlib import Path

from physics_lab.registry.nuclear_prediction_coverage import (
    build_nuclear_prediction_registry_coverage,
)


ROOT = Path(__file__).resolve().parents[1]


def test_nuclear_prediction_registry_coverage_counts_current_registry() -> None:
    coverage = build_nuclear_prediction_registry_coverage(ROOT)

    assert coverage["task_id"] == "TASK-0272"
    assert coverage["audit_scope"]["entry_count"] == 60
    assert coverage["audit_scope"]["target_row_count"] == 261
    assert coverage["audit_scope"]["lowest_prediction_id"] == "PRED-0001"
    assert coverage["audit_scope"]["highest_prediction_id"] == "PRED-0068"
    assert coverage["audit_scope"]["live_external_fetch_allowed_values"] == [False]
    assert "PRED-0031" in coverage["audit_scope"]["id_gaps"]
    assert "PRED-0040" in coverage["audit_scope"]["id_gaps"]


def test_nuclear_prediction_registry_coverage_groups_source_and_transform_lanes() -> None:
    coverage = build_nuclear_prediction_registry_coverage(ROOT)
    task_counts = {
        item["label"]: item["count"] for item in coverage["source_task_counts"]
    }
    transform_counts = {
        item["label"]: item["count"] for item in coverage["transform_class_counts"]
    }

    assert task_counts["TASK-0205"] == 20
    assert task_counts["TASK-0251"] == 10
    assert task_counts["TASK-0265"] == 12
    assert task_counts["TASK-0297"] == 6
    assert transform_counts["feature_term_selected_registry"] == 12
    assert transform_counts["factory_coefficient_transform_selected_registry"] == 10


def test_nuclear_prediction_registry_coverage_surfaces_reuse_and_reveal_care() -> None:
    coverage = build_nuclear_prediction_registry_coverage(ROOT)
    repeated_targets = {
        item["nuclide_id"]: item for item in coverage["repeated_target_nuclides"]
    }
    flagged_entries = {
        item["prediction_id"]: set(item["flags"])
        for item in coverage["reveal_readiness_flags"]
    }

    assert repeated_targets["Ni-76"]["entry_count"] == 18
    assert repeated_targets["Ca-55"]["entry_count"] == 14
    assert "manual_lane_source_review" in flagged_entries["PRED-0001"]
    assert "feature_term_selected_wave" in flagged_entries["PRED-0051"]
    assert "high_reuse_target_batch" in flagged_entries["PRED-0041"]
    assert "manual_lane_source_review" in flagged_entries["PRED-0063"]
    assert "near_null_or_ablation_control" in flagged_entries["PRED-0067"]


def test_nuclear_prediction_registry_coverage_reports_domain_gaps_without_scoring() -> None:
    coverage = build_nuclear_prediction_registry_coverage(ROOT)
    domains = {item["domain"]: item for item in coverage["domain_coverage"]}
    gaps = {(item["domain"], item["status"]) for item in coverage["coverage_gaps"]}

    assert domains["shell_magic"]["entry_count"] > 0
    assert domains["shell_magic"]["entry_count"] == 22
    assert domains["neutron_rich"]["entry_count"] > 0
    assert domains["odd_even"]["entry_count"] > 0
    assert ("frontier", "overrepresented_target_batch") in gaps
    assert ("mid_mass", "missing_factory_feature_term_registry_batch") in gaps
