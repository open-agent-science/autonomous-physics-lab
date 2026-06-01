"""Tests for the TASK-0480 compact-radius mass-quartile scout."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.resource_sensitive,
    pytest.mark.xdist_group(name="exoplanet_snapshot"),
]

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_exoplanet_compact_radius_mass_quartile_scout as scout  # noqa: E402
from physics_lab.registry.agent_runs import (  # noqa: E402
    validate_agent_run_payload,
)

SNAPSHOT_PATH = (
    ROOT / "data" / "exoplanets" / "exo-0001-pscomppars-snapshot.yaml"
)


# ---------------------------------------------------------------------------
# Helper / predicate sanity
# ---------------------------------------------------------------------------


def _row_with_radius(value: float) -> dict:
    return {"radius": {"value": value, "radius_class": "transit_radius"}}


def test_compact_predicate_is_strict_below_1p5():
    assert scout._is_compact(_row_with_radius(1.0)) is True
    assert scout._is_compact(_row_with_radius(1.499)) is True
    assert scout._is_compact(_row_with_radius(1.5)) is False


def test_stats_handles_empty_input():
    out = scout._stats([])
    assert out["count"] == 0
    assert out["log10_rmse"] is None


def test_control_status_thresholds():
    assert scout._control_status(10, 40) == "underpowered"
    assert scout._control_status(scout.MIN_BIN_ROW_COUNT, 40) == "partial_control"
    assert scout._control_status(40, 40) == "usable_control"


# ---------------------------------------------------------------------------
# Predeclared partitioning
# ---------------------------------------------------------------------------


def _rows_for_masses(masses: list[float]) -> list[dict]:
    return [
        {
            "row_id": f"r{i}",
            "mass": {"value": m, "mass_class": "true_mass"},
            "radius": {"value": 1.0, "radius_class": "transit_radius"},
        }
        for i, m in enumerate(masses)
    ]


def test_contiguous_equal_count_bins_preserves_rows_and_is_contiguous():
    rows = _rows_for_masses([float(i) for i in range(10)])
    bins = scout._contiguous_equal_count_bins(rows, 4)
    assert [len(b) for b in bins] == [2, 3, 2, 3]
    # Concatenated bins reproduce the original order exactly.
    flat = [row for b in bins for row in b]
    assert [row["row_id"] for row in flat] == [row["row_id"] for row in rows]


def test_contiguous_equal_count_bins_handles_exact_quartiles():
    rows = _rows_for_masses([float(i) for i in range(92)])
    bins = scout._contiguous_equal_count_bins(rows, 4)
    assert [len(b) for b in bins] == [23, 23, 23, 23]


# ---------------------------------------------------------------------------
# _classify_bin branch coverage
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


def test_classify_under_minimum_bin_blocks_interpretation():
    result = scout._classify_bin(
        _stats_from_rmse(23, 0.30),
        _stats_from_rmse(1000, 0.15),
        {"nearest": _control(23, 0.10, status="underpowered")},
    )
    assert result["interpretable"] is False
    assert result["outcome"] == "under_minimum_bin"
    assert result["verdict"] == "INCONCLUSIVE"
    # Even an underpowered bin reports its delta vs eligible for context.
    assert result["delta_log10_rmse_bin_minus_eligible"] == pytest.approx(0.15)


def test_classify_bin_above_eligible_and_controls():
    result = scout._classify_bin(
        _stats_from_rmse(46, 0.35),
        _stats_from_rmse(1000, 0.15),
        {
            "nearest": _control(46, 0.20),
            "per_class_median": _control(46, 0.31, kind="residual_shift"),
        },
    )
    assert result["interpretable"] is True
    assert result["outcome"] == "residual_stress_above_eligible_and_controls"
    assert result["verdict"] == "SANDBOX_PASS"
    assert result["adverse_control"] == "per_class_median"


def test_classify_bin_control_sensitive_when_adverse_close():
    result = scout._classify_bin(
        _stats_from_rmse(46, 0.30),
        _stats_from_rmse(1000, 0.15),
        {"nearest": _control(46, 0.29)},
    )
    assert result["outcome"] == "control_sensitive_residual_stress"
    assert result["verdict"] == "INCONCLUSIVE"


def test_classify_bin_below_eligible():
    result = scout._classify_bin(
        _stats_from_rmse(46, 0.11),
        _stats_from_rmse(1000, 0.158),
        {"nearest": _control(46, 0.17)},
    )
    assert result["outcome"] == "residual_below_eligible"
    assert result["verdict"] == "INCONCLUSIVE"


# ---------------------------------------------------------------------------
# Numerical regression on the committed snapshot
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def metrics() -> dict:
    return scout.build_metrics(SNAPSHOT_PATH)


def test_reproduces_eligible_and_compact_anchors(metrics):
    assert metrics["eligible_reproduction"]["reproduces_anchor"] is True
    assert metrics["compact_slice_reproduction"]["reproduces_anchor"] is True
    assert metrics["loader_summary"]["compact_slice_count"] == 92
    assert metrics["loader_summary"]["eligible_true_mass_with_transit_radius"] == 1207
    assert metrics["reproduction_status"] == "match"


def test_headline_verdict_is_inconclusive_underpowered(metrics):
    # The compact slice (92 rows) cannot support an interpretable mass-quartile
    # partition (~23 rows/bin < 30-row floor), so the headline verdict is
    # INCONCLUSIVE regardless of the coarse fallback diagnostic.
    assert metrics["verdict"] == "INCONCLUSIVE"
    assert (
        metrics["scout_outcome"]
        == "compact_slice_underpowered_for_mass_quartile_localization"
    )


def test_quartile_partition_is_underpowered(metrics):
    quartile = next(p for p in metrics["partitions"] if p["id"] == "mass_quartile")
    assert quartile["role"] == "primary"
    assert quartile["n_bins"] == 4
    assert quartile["interpretable_bin_count"] == 0
    assert quartile["survivor_bin_ids"] == []
    for b in quartile["bins"]:
        assert b["bin_stats"]["count"] == 23
        assert b["classification"]["interpretable"] is False


def test_half_partition_is_a_reported_fallback_diagnostic(metrics):
    half = next(p for p in metrics["partitions"] if p["id"] == "mass_half")
    assert half["role"] == "fallback_diagnostic"
    assert half["interpretable_bin_count"] == 2
    for b in half["bins"]:
        assert b["bin_stats"]["count"] == 46


def test_bins_predeclared_flag_is_set(metrics):
    assert metrics["data_boundary"]["bins_predeclared_before_metrics"] is True
    assert metrics["data_boundary"]["live_external_fetch_performed"] is False
    assert metrics["data_boundary"]["baseline_refit_performed"] is False


# ---------------------------------------------------------------------------
# Artifact round-trip + manifest schema validation
# ---------------------------------------------------------------------------


def test_write_outputs_and_validate_agent_run(tmp_path, metrics):
    out = tmp_path / "metrics.json"
    agent_run = tmp_path / "agent_run.yaml"
    scout.write_outputs(
        metrics,
        out=out,
        report=tmp_path / "report.md",
        agent_run=agent_run,
        limitations=tmp_path / "limitations.md",
        preflight=tmp_path / "preflight.md",
        review_summary=tmp_path / "review_summary.md",
        review=tmp_path / "review.md",
    )
    # metrics.json round-trips.
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["verdict"] == "INCONCLUSIVE"

    # Temp-output manifests can validate schema/boundary rules without pretending
    # that disposable files under tmp_path are committed repository artifacts.
    payload = scout._build_agent_run_payload(metrics)
    validate_agent_run_payload(payload, source=agent_run)
    assert payload["sandbox_only"] is True
    assert payload["promotion_boundary"]["writes_canonical_result"] is False


def test_committed_agent_run_manifest_validates_under_repo_root(metrics):
    payload = scout._build_agent_run_payload(metrics)
    validate_agent_run_payload(
        payload,
        source=ROOT / "agent_runs" / scout.AGENT_RUN_ID / "agent_run.yaml",
        root=ROOT,
    )
