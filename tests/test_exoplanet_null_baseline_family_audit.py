"""Tests for the TASK-0483 exoplanet null-baseline family audit."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_exoplanet_null_baseline_family_audit as audit  # noqa: E402

SYNTHETIC_FIXTURE = (
    ROOT / "tests" / "fixtures" / "exoplanets" / "synthetic_pscomppars_snapshot.yaml"
)


def _summary(count: int, rmse: float | None) -> dict:
    return {
        "count": count,
        "log10_mae": None if rmse is None else rmse * 0.8,
        "log10_rmse": rmse,
        "log10_bias": 0.0,
        "median_log10_residual": 0.0,
        "interval_68_coverage": 1.0,
        "interval_95_coverage": 1.0,
        "fraction_within_factor_2": 1.0,
        "missing_prediction_count": 0,
    }


def test_classify_slice_blocks_empty_slice():
    result = audit._classify_slice(
        ck17_summary=_summary(0, None),
        null_summaries={"null": _summary(0, None)},
    )
    assert result["status"] == "no_rows"
    assert result["verdict"] == "INCONCLUSIVE"


def test_classify_slice_preserves_underpowered_slice():
    result = audit._classify_slice(
        ck17_summary=_summary(audit.MIN_INTERPRETABLE_ROWS - 1, 0.2),
        null_summaries={"null": _summary(29, 0.1)},
    )
    assert result["status"] == "underpowered"
    assert result["best_null"] is None


def test_classify_slice_detects_control_sensitive_null_improvement():
    result = audit._classify_slice(
        ck17_summary=_summary(100, 0.30),
        null_summaries={
            "weak_null": _summary(100, 0.29),
            "strong_null": _summary(100, 0.20),
        },
    )
    assert result["status"] == "control_sensitive_null_family_explains"
    assert result["best_null"] == "strong_null"
    assert result["delta_log10_rmse_ck17_minus_best_null"] == pytest.approx(0.10)


def test_classify_slice_detects_weak_null_improvement_below_margin():
    result = audit._classify_slice(
        ck17_summary=_summary(100, 0.30),
        null_summaries={"weak_null": _summary(100, 0.29)},
    )
    assert result["status"] == "weak_null_family_improvement"


def test_classify_slice_detects_ck17_not_worse_than_nulls():
    result = audit._classify_slice(
        ck17_summary=_summary(100, 0.20),
        null_summaries={"null": _summary(100, 0.25)},
    )
    assert result["status"] == "ck17_not_worse_than_null_family"


def test_uncertainty_band_uses_max_available_relative_uncertainty():
    entry = {
        "mass": {"value": 10.0, "uncertainty_upper": 0.1, "uncertainty_lower": -0.1},
        "radius": {
            "value": 2.0,
            "uncertainty_upper": 0.4,
            "uncertainty_lower": -0.1,
        },
    }
    assert math.isclose(audit._combined_uncertainty(entry), 0.2)
    assert audit._uncertainty_band(entry) == "loose_gt15pct"


def test_nearest_residuals_excludes_self_and_is_deterministic():
    rows = [
        audit.AuditRow(
            row_id="A",
            planet_name="A",
            axis="true_mass_with_transit_radius",
            detection_method="transit",
            mass_mearth=1.0,
            radius_rearth=1.0,
            equilibrium_temperature_K=None,
            mass_class="true_mass",
            radius_class="transit_radius",
            planet_class="terran",
            uncertainty_band="tight_le5pct",
            ck17_log_residual=0.10,
        ),
        audit.AuditRow(
            row_id="B",
            planet_name="B",
            axis="true_mass_with_transit_radius",
            detection_method="transit",
            mass_mearth=1.1,
            radius_rearth=1.1,
            equilibrium_temperature_K=None,
            mass_class="true_mass",
            radius_class="transit_radius",
            planet_class="terran",
            uncertainty_band="tight_le5pct",
            ck17_log_residual=0.20,
        ),
        audit.AuditRow(
            row_id="C",
            planet_name="C",
            axis="true_mass_with_transit_radius",
            detection_method="transit",
            mass_mearth=2.0,
            radius_rearth=1.2,
            equilibrium_temperature_K=None,
            mass_class="true_mass",
            radius_class="transit_radius",
            planet_class="terran",
            uncertainty_band="tight_le5pct",
            ck17_log_residual=0.30,
        ),
    ]
    corrections = audit._nearest_residuals(rows, lambda row: row.mass_mearth)
    assert corrections["A"] == pytest.approx(0.20)
    assert corrections["B"] == pytest.approx(0.10)
    assert corrections["C"] == pytest.approx(0.20)


def test_runner_produces_full_artifact_bundle_on_synthetic_fixture(tmp_path):
    metrics_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"
    agent_run_path = tmp_path / "agent_run.yaml"
    limitations_path = tmp_path / "limitations.md"
    preflight_path = tmp_path / "preflight.md"
    review_summary_path = tmp_path / "review_summary.md"
    review_path = tmp_path / "review.md"

    exit_code = audit.main(
        [
            "--snapshot",
            str(SYNTHETIC_FIXTURE),
            "--out",
            str(metrics_path),
            "--report",
            str(report_path),
            "--agent-run",
            str(agent_run_path),
            "--limitations",
            str(limitations_path),
            "--preflight",
            str(preflight_path),
            "--review-summary",
            str(review_summary_path),
            "--review",
            str(review_path),
        ]
    )
    assert exit_code == 0

    for path in (
        metrics_path,
        report_path,
        agent_run_path,
        limitations_path,
        preflight_path,
        review_summary_path,
        review_path,
    ):
        assert path.exists()
        assert path.read_text(encoding="utf-8").strip()

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert metrics["task_id"] == "TASK-0483"
    assert metrics["data_boundary"]["live_fetch_performed"] is False
    assert len(metrics["null_baseline_family"]) == 4
    assert "compact_radius_lt1p5Re" in metrics["slices"]
    assert "axis_minimum_mass_with_transit_radius" in metrics["slices"]

    manifest = yaml.safe_load(agent_run_path.read_text(encoding="utf-8"))
    assert manifest["id"] == "AGENT-RUN-0050"
    assert manifest["sandbox_only"] is True
    assert manifest["promotion_boundary"]["claim_promotion_allowed"] is False


def test_build_metrics_on_committed_snapshot_has_required_slices():
    metrics = audit.build_metrics(audit.DEFAULT_SNAPSHOT_PATH)
    assert metrics["axis_counts"]["true_mass_with_transit_radius"] >= 1000
    assert set(metrics["slices"]) == {
        "axis_true_mass_with_transit_radius",
        "axis_minimum_mass_with_transit_radius",
        "compact_radius_lt1p5Re",
        "sub_neptune_radius_1p5_4Re",
        "jovian_radius_8_16Re",
        "hot_jupiter_high_irradiation",
    }
    assert metrics["slices"]["axis_minimum_mass_with_transit_radius"][
        "classification"
    ]["status"] in {"underpowered", "no_rows"}
