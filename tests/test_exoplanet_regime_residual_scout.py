"""Tests for the TASK-0370 exoplanet regime residual scout runner.

Tests cover (1) regime predicate behaviour, (2) verdict classification
logic with explicit margin cases, (3) end-to-end runner determinism
on the committed synthetic fixture, and (4) agent_run.yaml shape.
"""

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

import scripts.run_exoplanet_regime_residual_scout as scout  # noqa: E402

SYNTHETIC_FIXTURE = (
    ROOT / "tests" / "fixtures" / "exoplanets" / "synthetic_pscomppars_snapshot.yaml"
)


# ---------------------------------------------------------------------------
# Verdict classification
# ---------------------------------------------------------------------------


def _stats_from_rmse(count: int, rmse: float | None) -> dict:
    return {
        "count": count,
        "log10_rmse": rmse,
        "log10_mae": None if rmse is None else rmse * 0.8,
        "log10_bias": 0.0,
        "log10_median": 0.0,
    }


def test_classify_under_minimum_slice_blocks_verdict():
    out = scout._classify_regime_outcome(
        candidate_stats=_stats_from_rmse(10, 0.05),
        control_stats={"per_class_median": _stats_from_rmse(10, 0.08)},
        eligible_stats=_stats_from_rmse(1000, 0.20),
        min_count=30,
        survival_margin=0.022,
    )
    assert out["outcome"] == "under_minimum_slice"
    assert out["strongest_control"] is None


def test_classify_beats_eligible_and_controls():
    out = scout._classify_regime_outcome(
        candidate_stats=_stats_from_rmse(200, 0.10),
        control_stats={
            "per_class_median": _stats_from_rmse(200, 0.20),
            "shuffled_regime": _stats_from_rmse(200, 0.18),
            "matched_size_neighbor": _stats_from_rmse(200, 0.15),
        },
        eligible_stats=_stats_from_rmse(1000, 0.18),
        min_count=30,
        survival_margin=0.022,
    )
    assert out["outcome"] == "regime_residual_lower_than_eligible_and_controls"
    assert out["strongest_control"] == "matched_size_neighbor"
    assert out["delta_log10_rmse_eligible_minus_candidate"] == pytest.approx(0.08)
    assert out["delta_log10_rmse_strongest_control_minus_candidate"] == pytest.approx(0.05)


def test_classify_beats_eligible_but_not_controls():
    out = scout._classify_regime_outcome(
        candidate_stats=_stats_from_rmse(200, 0.10),
        control_stats={
            "per_class_median": _stats_from_rmse(200, 0.105),
            "matched_size_neighbor": _stats_from_rmse(200, 0.11),
        },
        eligible_stats=_stats_from_rmse(1000, 0.18),
        min_count=30,
        survival_margin=0.022,
    )
    # Beats eligible by 0.08 (> 0.022), beats strongest control by only 0.005.
    assert out["outcome"] == "regime_residual_lower_than_eligible_only"


def test_classify_regime_higher_than_eligible():
    out = scout._classify_regime_outcome(
        candidate_stats=_stats_from_rmse(200, 0.30),
        control_stats={"per_class_median": _stats_from_rmse(200, 0.28)},
        eligible_stats=_stats_from_rmse(1000, 0.18),
        min_count=30,
        survival_margin=0.022,
    )
    assert out["outcome"] == "regime_residual_higher_than_eligible"


def test_classify_inconclusive_when_close():
    out = scout._classify_regime_outcome(
        candidate_stats=_stats_from_rmse(200, 0.18),
        control_stats={"per_class_median": _stats_from_rmse(200, 0.19)},
        eligible_stats=_stats_from_rmse(1000, 0.18),
        min_count=30,
        survival_margin=0.022,
    )
    assert out["outcome"] == "inconclusive"


def test_agent_verdict_maps_to_sandbox_enum():
    # All inconclusive -> INCONCLUSIVE
    results = {
        "REGIME-001": {
            "role": "executed_regime",
            "classification": {"outcome": "inconclusive"},
        },
        "REGIME-002": {
            "role": "executed_regime",
            "classification": {"outcome": "regime_residual_lower_than_eligible_only"},
        },
    }
    assert scout._agent_verdict(results) == "INCONCLUSIVE"
    # Add a surviving regime -> SANDBOX_PASS
    results["REGIME-003"] = {
        "role": "executed_regime",
        "classification": {
            "outcome": "regime_residual_lower_than_eligible_and_controls"
        },
    }
    assert scout._agent_verdict(results) == "SANDBOX_PASS"
    # No executed regimes -> INCONCLUSIVE
    assert (
        scout._agent_verdict(
            {"REGIME-001": {"role": "generated_only", "classification": {"outcome": "x"}}}
        )
        == "INCONCLUSIVE"
    )


# ---------------------------------------------------------------------------
# Hypothesis slate metadata
# ---------------------------------------------------------------------------


def test_hypothesis_slate_size_matches_task_contract():
    # TASK-0370 requires 4-8 generated and 1-3 executed.
    generated = scout.GENERATED_HYPOTHESES
    executed = [h for h in generated if h["executed"]]
    assert 4 <= len(generated) <= 8
    assert 1 <= len(executed) <= 3


def test_executed_hypotheses_have_distinct_labels():
    labels = [h["label"] for h in scout.GENERATED_HYPOTHESES if h["executed"]]
    assert len(labels) == len(set(labels))


# ---------------------------------------------------------------------------
# End-to-end runner on the synthetic fixture
# ---------------------------------------------------------------------------


def _run_runner(tmp_path: Path) -> dict:
    metrics_path = tmp_path / "metrics.json"
    scout.main(
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


def test_runner_produces_full_artifact_bundle(tmp_path):
    metrics = _run_runner(tmp_path)
    assert metrics["task_id"] == "TASK-0370"
    assert metrics["agent_run_id"] == "AGENT-RUN-0035"
    assert metrics["campaign_profile_id"] == "exoplanet-mass-radius"
    assert metrics["thresholds"]["min_regime_row_count"] == 30
    assert metrics["thresholds"]["shuffle_seed"] == 20260524
    assert metrics["generated_hypothesis_count"] == len(scout.GENERATED_HYPOTHESES)
    assert metrics["executed_hypothesis_count"] == sum(
        1 for h in scout.GENERATED_HYPOTHESES if h["executed"]
    )
    # On the synthetic fixture, every regime is under the minimum slice
    # gate (the fixture has 3 eligible rows); the verdict must therefore
    # be INCONCLUSIVE and every executed regime must be flagged.
    assert metrics["verdict"] == "INCONCLUSIVE"
    for regime in metrics["regimes"].values():
        if regime["role"] != "executed_regime":
            continue
        assert regime["classification"]["outcome"] == "under_minimum_slice"


def test_runner_is_deterministic(tmp_path):
    first = _run_runner(tmp_path / "first")
    second = _run_runner(tmp_path / "second")
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_runner_agent_run_yaml_matches_schema_required_shape(tmp_path):
    _run_runner(tmp_path)
    payload = yaml.safe_load((tmp_path / "agent_run.yaml").read_text(encoding="utf-8"))
    assert payload["sandbox_only"] is True
    assert payload["promotion_boundary"]["writes_canonical_result"] is False
    assert payload["promotion_boundary"]["claim_promotion_allowed"] is False
    assert payload["proposal_paths"]["hypothesis"].startswith(
        "hypothesis_proposals/exoplanet-mass/HYP-PROPOSAL-0050"
    )
    assert payload["proposal_paths"]["experiment"].startswith(
        "experiment_proposals/exoplanet-mass/EXP-PROPOSAL-0016"
    )
    # Schema-required artifact pointers all set.
    for key in ("metrics", "report", "limitations", "preflight", "review_summary"):
        assert payload["artifacts"][key].startswith("agent_runs/AGENT-RUN-0035/")


# ---------------------------------------------------------------------------
# Predicate guards (no NaN / no missing-field crashes)
# ---------------------------------------------------------------------------


def test_stellar_teff_handles_missing_field():
    assert scout._stellar_teff({}) is None
    assert scout._stellar_teff({"host_star": {}}) is None
    assert scout._stellar_teff({"host_star": {"effective_temperature_K": None}}) is None
    assert scout._stellar_teff({"host_star": {"effective_temperature_K": 5778.0}}) == 5778.0


def test_equilibrium_temp_handles_nan():
    assert scout._equilibrium_temp_K({}) is None
    assert scout._equilibrium_temp_K({"equilibrium_temperature_K": None}) is None
    assert (
        scout._equilibrium_temp_K({"equilibrium_temperature_K": float("nan")}) is None
    )
    assert scout._equilibrium_temp_K({"equilibrium_temperature_K": 1234.5}) == 1234.5


def test_log_residual_returns_finite_or_none():
    entry = {
        "row_id": "x",
        "mass": {"value": 1.0},
        "radius": {"value": 1.008},
    }
    val = scout._log_residual(entry)
    assert val is not None
    assert math.isfinite(val)
    # M=0 returns None
    bad = {"mass": {"value": 0.0}, "radius": {"value": 1.0}}
    assert scout._log_residual(bad) is None
