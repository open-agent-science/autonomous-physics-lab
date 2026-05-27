"""Tests for the TASK-0390 compact/sub-Neptune residual pilot."""

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

import scripts.run_exoplanet_compact_subneptune_residual_pilot as pilot  # noqa: E402

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


def test_classify_under_minimum_slice_blocks_interpretation():
    out = pilot._classify_stress_outcome(
        candidate_stats=_stats_from_rmse(10, 0.30),
        control_stats={"shuffled_label": _stats_from_rmse(10, 0.10)},
        eligible_stats=_stats_from_rmse(100, 0.10),
        min_count=30,
        survival_margin=0.022,
    )
    assert out["outcome"] == "under_minimum_slice"
    assert out["adverse_control"] is None


def test_classify_stress_above_eligible_and_controls():
    out = pilot._classify_stress_outcome(
        candidate_stats=_stats_from_rmse(100, 0.30),
        control_stats={
            "per_class_median": _stats_from_rmse(100, 0.20),
            "shuffled_label": _stats_from_rmse(100, 0.22),
            "matched_size_neighbor": _stats_from_rmse(100, 0.24),
        },
        eligible_stats=_stats_from_rmse(1000, 0.15),
        min_count=30,
        survival_margin=0.022,
    )
    assert out["outcome"] == "residual_stress_above_eligible_and_controls"
    assert out["adverse_control"] == "matched_size_neighbor"
    assert out["delta_log10_rmse_candidate_minus_eligible"] == pytest.approx(0.15)
    assert out["delta_log10_rmse_candidate_minus_adverse_control"] == pytest.approx(
        0.06
    )


def test_classify_stress_above_eligible_only_when_control_matches():
    out = pilot._classify_stress_outcome(
        candidate_stats=_stats_from_rmse(100, 0.30),
        control_stats={
            "per_class_median": _stats_from_rmse(100, 0.29),
            "shuffled_label": _stats_from_rmse(100, 0.28),
        },
        eligible_stats=_stats_from_rmse(1000, 0.15),
        min_count=30,
        survival_margin=0.022,
    )
    assert out["outcome"] == "residual_stress_above_eligible_only"


def test_classify_stress_below_eligible():
    out = pilot._classify_stress_outcome(
        candidate_stats=_stats_from_rmse(100, 0.10),
        control_stats={"shuffled_label": _stats_from_rmse(100, 0.11)},
        eligible_stats=_stats_from_rmse(1000, 0.16),
        min_count=30,
        survival_margin=0.022,
    )
    assert out["outcome"] == "residual_stress_below_eligible"


def test_agent_verdict_maps_surviving_hypothesis_to_sandbox_pass():
    results = {
        "CSN-001": {
            "role": "executed_hypothesis",
            "classification": {"outcome": "residual_stress_above_eligible_only"},
        }
    }
    assert pilot._agent_verdict(results) == "INCONCLUSIVE"
    results["CSN-002"] = {
        "role": "executed_hypothesis",
        "classification": {"outcome": "residual_stress_above_eligible_and_controls"},
    }
    assert pilot._agent_verdict(results) == "SANDBOX_PASS"


def test_hypothesis_slate_matches_task_bounds():
    generated = pilot.GENERATED_HYPOTHESES
    executed = [hypothesis for hypothesis in generated if hypothesis["executed"]]
    assert 4 <= len(generated) <= 8
    assert 1 <= len(executed) <= 3
    assert len({hypothesis["label"] for hypothesis in generated}) == len(generated)


def _run_runner(tmp_path: Path) -> dict:
    metrics_path = tmp_path / "metrics.json"
    pilot.main(
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
    assert metrics["task_id"] == "TASK-0390"
    assert metrics["agent_run_id"] == "AGENT-RUN-0036"
    assert metrics["campaign_profile_id"] == "exoplanet-mass-radius"
    assert metrics["data_boundary"]["live_external_fetch_performed"] is False
    assert metrics["data_boundary"]["baseline_refit_performed"] is False
    assert metrics["data_boundary"]["minimum_mass_rows_in_headline_metrics"] is False
    assert metrics["generated_hypothesis_count"] == len(pilot.GENERATED_HYPOTHESES)
    assert metrics["executed_hypothesis_count"] == sum(
        1 for hypothesis in pilot.GENERATED_HYPOTHESES if hypothesis["executed"]
    )
    assert metrics["verdict"] == "INCONCLUSIVE"
    for result in metrics["hypotheses"].values():
        if result["role"] == "executed_hypothesis":
            assert result["classification"]["outcome"] == "under_minimum_slice"


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
        "hypothesis_proposals/exoplanet-mass/HYP-PROPOSAL-0051"
    )
    assert payload["proposal_paths"]["experiment"].startswith(
        "experiment_proposals/exoplanet-mass/EXP-PROPOSAL-0017"
    )
    assert payload["promotion_boundary"]["writes_canonical_result"] is False
    assert payload["promotion_boundary"]["claim_promotion_allowed"] is False
    assert payload["artifacts"]["metrics"] == "agent_runs/AGENT-RUN-0036/metrics.json"
    assert payload["artifacts"]["limitations"] == (
        "agent_runs/AGENT-RUN-0036/limitations.md"
    )


def test_residual_helpers_handle_invalid_rows():
    assert pilot._host_teff({}) is None
    assert pilot._relative_uncertainty({"value": 1.0}) is None
    assert math.isclose(
        pilot._relative_uncertainty(
            {"value": 2.0, "uncertainty_upper": 0.2, "uncertainty_lower": -0.1}
        ),
        0.1,
    )
    assert pilot._log_residual({"mass": {"value": 0.0}, "radius": {"value": 1.0}}) is None
