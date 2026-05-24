"""Tests for the atomic-clock metadata-only source manifest template."""

from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "data" / "atomic_clocks" / "source_manifest_template.yaml"


def _load_manifest() -> dict:
    return yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_atomic_clock_source_manifest_is_metadata_only() -> None:
    manifest = _load_manifest()

    assert manifest["task_id"] == "TASK-0327"
    assert manifest["status"] == "template_only"
    assert manifest["scope"]["value_policy"] == "no_measurement_values_recorded"
    assert manifest["scope"]["live_fetch_allowed"] is False
    assert manifest["scope"]["benchmark_allowed"] is False
    assert manifest["promotion_boundary"] == {
        "writes_real_clock_values": False,
        "writes_derived_constraint_values": False,
        "writes_benchmark_metrics": False,
        "writes_prediction_registry": False,
        "writes_canonical_result": False,
        "claim_promotion_allowed": False,
    }


def test_atomic_clock_source_manifest_source_classes_are_separated() -> None:
    manifest = _load_manifest()
    classes = manifest["row_classes"]

    assert set(classes) == {
        "direct_frequency_ratio_measurement",
        "repeated_comparison_campaign",
        "drift_bound_or_constants_constraint",
        "evaluation_or_review_summary",
    }
    assert classes["direct_frequency_ratio_measurement"]["admissible_as"] == (
        "direct_measurement"
    )
    assert classes["drift_bound_or_constants_constraint"]["admissible_as"] == (
        "derived_constraint"
    )
    assert classes["evaluation_or_review_summary"]["admissible_as"] == (
        "review_summary_only"
    )


def test_atomic_clock_source_manifest_candidate_families_have_no_values() -> None:
    manifest = _load_manifest()
    families = manifest["candidate_source_families"]

    assert len(families) >= 3
    forbidden_value_keys = {"value", "frequency_ratio", "drift_bound", "constraint_value"}
    for family in families:
        assert family["value_status"] == "metadata_only_no_values"
        assert family["source_locator"] is None
        assert family["retrieval_date"] is None
        assert family["checksum_sha256"] is None
        assert family["holdout_or_reveal_boundary"] == "source_manifest_only"
        assert family["stop_conditions"]
        assert forbidden_value_keys.isdisjoint(family)


def test_atomic_clock_source_manifest_has_global_stop_conditions() -> None:
    manifest = _load_manifest()
    stop_conditions = set(manifest["global_stop_conditions"])

    assert "source_hides_primary_rows" in stop_conditions
    assert "source_omits_uncertainty_semantics" in stop_conditions
    assert "source_license_or_reuse_terms_unclear" in stop_conditions
    assert "task_requests_constants_drift_fit_before_source_review" in stop_conditions
