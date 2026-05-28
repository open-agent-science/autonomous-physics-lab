"""Tests for the TASK-0427 compact/sub-Neptune matched-control audit."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_exoplanet_compact_subneptune_matched_control_audit as audit  # noqa: E402

SYNTHETIC_FIXTURE = (
    ROOT / "tests" / "fixtures" / "exoplanets" / "synthetic_pscomppars_snapshot.yaml"
)


# ---------------------------------------------------------------------------
# _classify_audit branch coverage
# ---------------------------------------------------------------------------


def _stats_from_rmse(count: int, rmse: float | None) -> dict:
    return {
        "count": count,
        "log10_rmse": rmse,
        "log10_mae": None if rmse is None else rmse * 0.8,
        "log10_bias": 0.0,
        "log10_median": 0.0,
    }


def _control(
    count: int,
    rmse: float,
    *,
    kind: str = "matched_cohort",
    status: str = "usable_control",
) -> dict:
    return {
        "label": "control",
        "kind": kind,
        "status": status,
        "stats": _stats_from_rmse(count, rmse),
        "interpretation": "test control",
    }


def test_classify_under_minimum_slice_blocks_interpretation():
    result = audit._classify_audit(
        target_stats=_stats_from_rmse(10, 0.30),
        eligible_stats=_stats_from_rmse(100, 0.10),
        controls={"nearest": _control(10, 0.10)},
    )
    assert result["outcome"] == "under_minimum_slice"
    assert result["verdict"] == "INCONCLUSIVE"


def test_classify_target_above_eligible_and_controls():
    result = audit._classify_audit(
        target_stats=_stats_from_rmse(100, 0.30),
        eligible_stats=_stats_from_rmse(1000, 0.15),
        controls={
            "nearest": _control(100, 0.20),
            "host": _control(100, 0.24),
        },
    )
    assert result["outcome"] == "residual_stress_above_eligible_and_controls"
    assert result["verdict"] == "SANDBOX_PASS"
    assert result["adverse_control"] == "host"
    assert result["delta_log10_rmse_target_minus_eligible"] == pytest.approx(0.15)
    assert result["delta_log10_rmse_target_minus_adverse_control"] == pytest.approx(
        0.06
    )


def test_classify_control_sensitive_when_adverse_control_is_close():
    result = audit._classify_audit(
        target_stats=_stats_from_rmse(100, 0.30),
        eligible_stats=_stats_from_rmse(1000, 0.15),
        controls={"nearest": _control(100, 0.29)},
    )
    assert result["outcome"] == "control_sensitive_residual_stress"
    assert result["verdict"] == "INCONCLUSIVE"


def test_classify_close_to_eligible():
    result = audit._classify_audit(
        target_stats=_stats_from_rmse(100, 0.16),
        eligible_stats=_stats_from_rmse(1000, 0.15),
        controls={"nearest": _control(100, 0.10)},
    )
    assert result["outcome"] == "residual_close_to_eligible"
    assert result["verdict"] == "INCONCLUSIVE"


def test_classify_below_eligible():
    result = audit._classify_audit(
        target_stats=_stats_from_rmse(100, 0.05),
        eligible_stats=_stats_from_rmse(1000, 0.15),
        controls={"nearest": _control(100, 0.04)},
    )
    assert result["outcome"] == "residual_below_eligible"
    assert result["verdict"] == "INCONCLUSIVE"


def test_classify_excludes_shuffled_from_adverse_pool():
    """Shuffled-label control's high RMSE is expected behaviour, not adverse."""
    result = audit._classify_audit(
        target_stats=_stats_from_rmse(100, 0.30),
        eligible_stats=_stats_from_rmse(1000, 0.15),
        controls={
            "nearest": _control(100, 0.20, kind="matched_cohort"),
            "shuffled": _control(100, 0.80, kind="negative_control_shuffle"),
        },
    )
    # Adverse should not be "shuffled" even though it has the highest RMSE.
    assert result["adverse_control"] == "nearest"
    assert result["outcome"] == "residual_stress_above_eligible_and_controls"


def test_classify_excludes_uncertainty_equalized_from_adverse_pool():
    """uncertainty_equalized_subset rising RMSE is signal-strength, not adverse."""
    result = audit._classify_audit(
        target_stats=_stats_from_rmse(100, 0.30),
        eligible_stats=_stats_from_rmse(1000, 0.15),
        controls={
            "nearest": _control(100, 0.20, kind="matched_cohort"),
            "uncertainty_eq": _control(
                100, 0.40, kind="negative_control_uncertainty"
            ),
        },
    )
    # Adverse should not be "uncertainty_eq" even though it has the highest RMSE.
    assert result["adverse_control"] == "nearest"
    assert result["outcome"] == "residual_stress_above_eligible_and_controls"


def test_classify_adverse_negative_control_is_eligible_for_adverse():
    """adverse_nearest_radius_outside_slice IS an adverse-margin candidate."""
    result = audit._classify_audit(
        target_stats=_stats_from_rmse(100, 0.30),
        eligible_stats=_stats_from_rmse(1000, 0.15),
        controls={
            "nearest_match": _control(100, 0.20, kind="matched_cohort"),
            "adverse": _control(100, 0.29, kind="negative_control_adverse"),
        },
    )
    assert result["adverse_control"] == "adverse"
    # adverse RMSE 0.29 is within 0.022 of target 0.30, so signal does not
    # survive the adverse comparison.
    assert result["outcome"] == "control_sensitive_residual_stress"


# ---------------------------------------------------------------------------
# Predicate sanity
# ---------------------------------------------------------------------------


def _row_with_radius(value: float) -> dict:
    return {"radius": {"value": value, "radius_class": "transit_radius"}}


def test_compact_predicate_is_strict_below_1p5():
    assert audit._is_compact(_row_with_radius(1.0)) is True
    assert audit._is_compact(_row_with_radius(1.499)) is True
    assert audit._is_compact(_row_with_radius(1.5)) is False


def test_sub_neptune_predicate_is_1p5_to_4():
    assert audit._is_sub_neptune(_row_with_radius(1.5)) is True
    assert audit._is_sub_neptune(_row_with_radius(3.999)) is True
    assert audit._is_sub_neptune(_row_with_radius(4.0)) is False
    assert audit._is_sub_neptune(_row_with_radius(1.499)) is False


def test_combined_predicate_is_strict_below_4():
    assert audit._is_compact_or_sub_neptune(_row_with_radius(0.5)) is True
    assert audit._is_compact_or_sub_neptune(_row_with_radius(3.999)) is True
    assert audit._is_compact_or_sub_neptune(_row_with_radius(4.0)) is False


# ---------------------------------------------------------------------------
# Stats + uncertainty helpers
# ---------------------------------------------------------------------------


def test_stats_handles_empty_input():
    out = audit._stats([])
    assert out["count"] == 0
    assert out["log10_rmse"] is None


def test_uncertainty_band_uses_max_available_component():
    entry = {
        "mass": {"value": 10.0, "uncertainty_upper": 0.5, "uncertainty_lower": -0.1},
        "radius": {"value": 3.0, "uncertainty_upper": 0.6, "uncertainty_lower": -0.3},
    }
    combined = audit._combined_uncertainty(entry)
    assert math.isclose(combined, 0.2)
    assert audit._uncertainty_band(entry) == "loose_gt15pct"


def test_uncertainty_band_returns_missing_without_uncertainty():
    entry = {
        "mass": {"value": 10.0},
        "radius": {"value": 3.0},
    }
    assert audit._combined_uncertainty(entry) is None
    assert audit._uncertainty_band(entry) == "missing"


def test_detection_method_helper_returns_string_or_none():
    assert audit._detection_method({"detection_method": "transit"}) == "transit"
    assert audit._detection_method({"detection_method": ""}) is None
    assert audit._detection_method({}) is None


# ---------------------------------------------------------------------------
# Matching helpers
# ---------------------------------------------------------------------------


def test_greedy_match_without_replacement_picks_distinct_rows():
    targets = [{"row_id": "t1", "x": 1.0}, {"row_id": "t2", "x": 2.0}]
    candidates = [
        {"row_id": "c1", "x": 1.1},
        {"row_id": "c2", "x": 2.05},
        {"row_id": "c3", "x": 1.2},
    ]
    matched = audit._greedy_match_without_replacement(
        targets,
        candidates,
        target_key=lambda r: r["x"],
        candidate_key=lambda r: r["x"],
    )
    assert [m["row_id"] for m in matched] == ["c1", "c2"]


def test_matched_categorical_control_breaks_ties_by_nearest_log_mass():
    targets = [
        {"row_id": "t1", "detection_method": "transit", "mass": {"value": 5.0}},
    ]
    candidates = [
        {
            "row_id": "c_far",
            "detection_method": "transit",
            "mass": {"value": 50.0},
        },
        {
            "row_id": "c_close",
            "detection_method": "transit",
            "mass": {"value": 6.0},
        },
        {
            "row_id": "c_other",
            "detection_method": "radial_velocity",
            "mass": {"value": 5.1},
        },
    ]
    matched = audit._matched_categorical_control(
        targets,
        candidates,
        categorical_key=audit._detection_method,
    )
    assert [m["row_id"] for m in matched] == ["c_close"]


# ---------------------------------------------------------------------------
# Negative control helpers
# ---------------------------------------------------------------------------


def test_uncertainty_equalized_subset_filters_loose_rows():
    target = [
        {
            "row_id": "tight",
            "mass": {"value": 10.0, "uncertainty_upper": 0.2, "uncertainty_lower": -0.2},
            "radius": {
                "value": 1.0,
                "uncertainty_upper": 0.02,
                "uncertainty_lower": -0.02,
            },
        },
        {
            "row_id": "loose",
            "mass": {"value": 10.0, "uncertainty_upper": 5.0, "uncertainty_lower": -5.0},
            "radius": {
                "value": 1.0,
                "uncertainty_upper": 0.5,
                "uncertainty_lower": -0.5,
            },
        },
    ]
    subset = audit._uncertainty_equalized_subset(
        target, max_combined_relative_uncertainty=0.15
    )
    assert [row["row_id"] for row in subset] == ["tight"]


def test_shuffled_radius_label_control_is_deterministic_under_seed():
    target = [
        {"row_id": "t1", "mass": {"value": 5.0}, "radius": {"value": 2.0}},
        {"row_id": "t2", "mass": {"value": 10.0}, "radius": {"value": 3.0}},
    ]
    pool = [
        {"row_id": "e1", "mass": {"value": 5.0}, "radius": {"value": 2.0}},
        {"row_id": "e2", "mass": {"value": 6.0}, "radius": {"value": 1.5}},
        {"row_id": "e3", "mass": {"value": 7.0}, "radius": {"value": 2.5}},
        {"row_id": "e4", "mass": {"value": 10.0}, "radius": {"value": 3.0}},
    ]
    first = audit._shuffled_radius_label_control(target, pool, seed=1234)
    second = audit._shuffled_radius_label_control(target, pool, seed=1234)
    assert first == second
    # Different seed must produce a different sequence.
    different = audit._shuffled_radius_label_control(target, pool, seed=4321)
    assert different != first


# ---------------------------------------------------------------------------
# End-to-end: synthetic fixture
# ---------------------------------------------------------------------------


def test_build_metrics_on_synthetic_fixture_runs_without_error():
    metrics = audit.build_metrics(SYNTHETIC_FIXTURE)
    assert metrics["task_id"] == "TASK-0427"
    assert metrics["agent_run_id"] == "AGENT-RUN-0042"
    assert "target_slices" in metrics
    assert len(metrics["target_slices"]) == 3
    for slice_payload in metrics["target_slices"]:
        assert slice_payload["id"] in {"CSN-001", "CSN-002", "CSN-003"}
        assert "controls" in slice_payload
        assert "classification" in slice_payload
        # Synthetic data is too small to reproduce pilot counts/RMSE; ensure
        # pilot_reproduction recorded but not asserted true.
        assert "pilot_reproduction" in slice_payload


def test_build_metrics_records_thresholds_and_seeds():
    metrics = audit.build_metrics(SYNTHETIC_FIXTURE)
    thresholds = metrics["thresholds"]
    assert thresholds["min_slice_row_count"] == audit.MIN_SLICE_ROW_COUNT
    assert thresholds["control_margin_log10_rmse"] == audit.CONTROL_MARGIN_LOG10_RMSE
    assert thresholds["pilot_reproduction_tolerance"] == audit.PILOT_REPRODUCTION_TOLERANCE
    assert thresholds["shuffle_seed"] == audit.SHUFFLE_SEED
    assert thresholds["random_outside_seed"] == audit.RANDOM_OUTSIDE_SEED


# ---------------------------------------------------------------------------
# Committed pilot reproduction
# ---------------------------------------------------------------------------


def test_committed_run_reproduces_pilot_for_all_slices():
    metrics_path = (
        ROOT / "agent_runs" / "AGENT-RUN-0042" / "metrics.json"
    )
    if not metrics_path.exists():
        pytest.skip("AGENT-RUN-0042 metrics.json not present in this workspace")
    metrics = json.loads(metrics_path.read_text())
    assert metrics["pilot_reproduction_status"] == "match"
    assert metrics["eligible_pilot_reproduction"]["reproduces_pilot"] is True
    for slice_payload in metrics["target_slices"]:
        assert slice_payload["pilot_reproduction"]["reproduces_pilot"] is True
        delta = slice_payload["pilot_reproduction"]["log10_rmse_delta"]
        assert abs(delta) <= audit.PILOT_REPRODUCTION_TOLERANCE


def test_committed_run_audit_verdict_is_sandbox_pass():
    metrics_path = (
        ROOT / "agent_runs" / "AGENT-RUN-0042" / "metrics.json"
    )
    if not metrics_path.exists():
        pytest.skip("AGENT-RUN-0042 metrics.json not present in this workspace")
    metrics = json.loads(metrics_path.read_text())
    # CSN-001 survives all controls; CSN-002/003 are control-sensitive.
    # Audit-level verdict aggregates as SANDBOX_PASS because at least one
    # slice cleared both eligible and adverse-control margins.
    assert metrics["verdict"] == "SANDBOX_PASS"
    csn001 = next(s for s in metrics["target_slices"] if s["id"] == "CSN-001")
    assert (
        csn001["classification"]["outcome"]
        == "residual_stress_above_eligible_and_controls"
    )
