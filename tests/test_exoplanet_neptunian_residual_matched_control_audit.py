"""Tests for the TASK-0391 neptunian matched-control audit."""

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

import scripts.run_exoplanet_neptunian_residual_matched_control_audit as audit  # noqa: E402

SYNTHETIC_FIXTURE = (
    ROOT / "tests" / "fixtures" / "exoplanets" / "synthetic_pscomppars_snapshot.yaml"
)


def _stats_from_rmse(count: int, rmse: float | None) -> dict:
    return {
        "count": count,
        "log10_rmse": rmse,
        "log10_mae": None if rmse is None else rmse * 0.8,
        "log10_bias": 0.0,
        "log10_median": 0.0,
    }


def _control(count: int, rmse: float, status: str = "usable_control") -> dict:
    return {
        "label": "control",
        "status": status,
        "stats": _stats_from_rmse(count, rmse),
        "interpretation": "test control",
    }


def test_classify_under_minimum_slice_blocks_interpretation():
    result = audit._classify_audit(
        neptunian_stats=_stats_from_rmse(10, 0.30),
        eligible_stats=_stats_from_rmse(100, 0.10),
        controls={"nearest": _control(10, 0.10)},
    )
    assert result["outcome"] == "under_minimum_slice"
    assert result["verdict"] == "INCONCLUSIVE"


def test_classify_neptunian_above_eligible_and_controls():
    result = audit._classify_audit(
        neptunian_stats=_stats_from_rmse(100, 0.30),
        eligible_stats=_stats_from_rmse(1000, 0.15),
        controls={
            "nearest": _control(100, 0.20),
            "host": _control(100, 0.24),
        },
    )
    assert result["outcome"] == "neptunian_residual_above_eligible_and_controls"
    assert result["verdict"] == "SANDBOX_PASS"
    assert result["adverse_control"] == "host"
    assert result["delta_log10_rmse_neptunian_minus_eligible"] == pytest.approx(0.15)
    assert result["delta_log10_rmse_neptunian_minus_adverse_control"] == pytest.approx(
        0.06
    )


def test_classify_control_sensitive_when_adverse_control_is_close():
    result = audit._classify_audit(
        neptunian_stats=_stats_from_rmse(100, 0.30),
        eligible_stats=_stats_from_rmse(1000, 0.15),
        controls={"nearest": _control(100, 0.29)},
    )
    assert result["outcome"] == "control_sensitive_residual_stress"
    assert result["verdict"] == "INCONCLUSIVE"


def test_classify_close_to_eligible():
    result = audit._classify_audit(
        neptunian_stats=_stats_from_rmse(100, 0.16),
        eligible_stats=_stats_from_rmse(1000, 0.15),
        controls={"nearest": _control(100, 0.10)},
    )
    assert result["outcome"] == "neptunian_residual_close_to_eligible"


def test_uncertainty_band_helper_uses_max_available_component():
    entry = {
        "mass": {"value": 10.0, "uncertainty_upper": 0.5, "uncertainty_lower": -0.1},
        "radius": {"value": 3.0, "uncertainty_upper": 0.6, "uncertainty_lower": -0.3},
    }
    assert math.isclose(audit._combined_uncertainty(entry), 0.2)
    assert audit._uncertainty_band(entry) == "loose_gt15pct"


def test_greedy_match_without_replacement_picks_distinct_rows():
    targets = [{"row_id": "t1", "x": 1.0}, {"row_id": "t2", "x": 2.0}]
    candidates = [
        {"row_id": "c1", "x": 1.1},
        {"row_id": "c2", "x": 1.9},
        {"row_id": "c3", "x": 9.0},
    ]
    out = audit._greedy_match_without_replacement(
        targets,
        candidates,
        target_key=lambda row: row["x"],
        candidate_key=lambda row: row["x"],
    )
    assert [row["row_id"] for row in out] == ["c1", "c2"]


def _run_runner(tmp_path: Path) -> dict:
    metrics_path = tmp_path / "metrics.json"
    audit.main(
        [
            "--snapshot",
            str(SYNTHETIC_FIXTURE),
            "--out",
            str(metrics_path),
            "--report",
            str(tmp_path / "report.md"),
            "--agent-run",
            str(tmp_path / "agent_run.yaml"),
            "--limitations",
            str(tmp_path / "limitations.md"),
            "--preflight",
            str(tmp_path / "preflight.md"),
            "--review-summary",
            str(tmp_path / "review_summary.md"),
            "--review",
            str(tmp_path / "review.md"),
        ]
    )
    return json.loads(metrics_path.read_text(encoding="utf-8"))


def test_runner_produces_sandbox_artifact_bundle(tmp_path):
    metrics = _run_runner(tmp_path)
    assert metrics["task_id"] == "TASK-0391"
    assert metrics["agent_run_id"] == "AGENT-RUN-0037"
    assert metrics["campaign_profile_id"] == "exoplanet-mass-radius"
    assert metrics["data_boundary"]["live_external_fetch_performed"] is False
    assert metrics["data_boundary"]["baseline_refit_performed"] is False
    assert metrics["data_boundary"]["minimum_mass_rows_in_headline_metrics"] is False
    assert set(metrics["controls"]) == {
        "per_class_median",
        "nearest_radius_non_neptunian",
        "host_temperature_non_neptunian",
        "uncertainty_band_non_neptunian",
    }
    assert metrics["verdict"] == "INCONCLUSIVE"


def test_runner_is_deterministic(tmp_path):
    first = _run_runner(tmp_path / "first")
    second = _run_runner(tmp_path / "second")
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_agent_run_yaml_preserves_promotion_boundary(tmp_path):
    _run_runner(tmp_path)
    payload = yaml.safe_load((tmp_path / "agent_run.yaml").read_text(encoding="utf-8"))
    assert payload["sandbox_only"] is True
    assert payload["created_by"]["agent_id"] == "codex"
    assert payload["proposal_paths"]["hypothesis"].startswith(
        "hypothesis_proposals/exoplanet-mass/HYP-PROPOSAL-0052"
    )
    assert payload["proposal_paths"]["experiment"].startswith(
        "experiment_proposals/exoplanet-mass/EXP-PROPOSAL-0018"
    )
    assert payload["promotion_boundary"]["writes_canonical_result"] is False
    assert payload["promotion_boundary"]["claim_promotion_allowed"] is False
    assert payload["artifacts"]["metrics"] == "agent_runs/AGENT-RUN-0037/metrics.json"


def test_invalid_residual_row_returns_none():
    assert audit._log_residual({"mass": {"value": 0.0}, "radius": {"value": 1.0}}) is None
    assert audit._host_teff({"host_star": {"effective_temperature_K": None}}) is None
