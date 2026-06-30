"""Tests for the TASK-0899 no-peek NMD-0003 GP uncertainty-calibration audit.

The full-surface GP fit and closed-form LOO inversion take tens of seconds, so
the committed sandbox ``agent_runs/AGENT-RUN-0089/metrics.json`` artifact (produced
by the pinned, deterministic runner) is the fixture for the headline-number,
no-peek, frozen-config, and verdict assertions. The frozen-config construction
and scoring helpers are exercised directly on small synthetic LOO inputs that run
in well under a second.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from physics_lab.engines.nmd0003_gp_calibration_audit import (
    REGION_MIN_LOO_COUNT,
    SUCCESS_RMS_Z_HIGH,
    SUCCESS_RMS_Z_LOW,
    _a_band,
    _build_frozen_config,
    _evaluate_success,
    _magic_band,
    _neutron_excess_band,
    _score_intervals,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
COMMITTED_METRICS_PATH = REPO_ROOT / "agent_runs/AGENT-RUN-0089/metrics.json"


@pytest.fixture(scope="module")
def metrics() -> dict:
    """The committed, deterministic sandbox AGENT-RUN-0089 metrics artifact."""
    return json.loads(COMMITTED_METRICS_PATH.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# Region label helpers (predeclared definitions; must match the adjudication)
# --------------------------------------------------------------------------- #


def test_region_label_definitions() -> None:
    assert _a_band(23) == "light_A_lt_60"
    assert _a_band(84) == "medium_60_le_A_lt_140"
    assert _a_band(208) == "heavy_A_ge_140"
    # Si-23: Z=14, N=9; Z within 2 of magic 8 (|14-8|=6 no, |9-8|=1 yes) -> near.
    assert _magic_band(14, 9) == "near_magic_within_2"
    # Ga-84: Z=31, N=53; nearest magic distance |53-50|=3 (>2) and |31-28|=3 (>2)
    # -> not near magic, matching the merged TASK-0844 adjudication outlier ledger.
    assert _magic_band(31, 53) == "not_near_magic"
    assert _magic_band(40, 40) == "not_near_magic"
    # eta = (N - Z) / A; Ga-84 eta = 22/84 = 0.262 -> high band.
    assert _neutron_excess_band(31, 53, 84) == "high_eta_ge_0_25"
    assert _neutron_excess_band(14, 9, 23) == "low_eta_lt_0_15"


# --------------------------------------------------------------------------- #
# Frozen-config construction on small synthetic LOO inputs (fast)
# --------------------------------------------------------------------------- #


def test_frozen_config_built_from_loo_only() -> None:
    rng = np.random.default_rng(0)
    loo_std = rng.standard_t(df=4, size=2000)
    a_band_labels = np.array(
        ["light_A_lt_60"] * 700 + ["medium_60_le_A_lt_140"] * 700 + ["heavy_A_ge_140"] * 600
    )
    config = _build_frozen_config(loo_std, a_band_labels)
    assert config["frozen_before_holdout_scoring"] is True
    families = config["families"]
    assert set(families) == {
        "global_robust_tail",
        "region_quantile_min_count",
        "conformal_global",
    }
    # Student-t family records a degrees-of-freedom and positive multipliers.
    grt = families["global_robust_tail"]
    assert grt["student_t_nu"] >= 2
    assert grt["interval_multiplier_1sigma"] > 0.0
    assert grt["interval_multiplier_2sigma"] > grt["interval_multiplier_1sigma"]
    # Conformal multipliers equal the LOO empirical abs-standardized quantiles.
    conf = families["conformal_global"]
    assert conf["interval_multiplier_1sigma"] == pytest.approx(
        float(np.percentile(np.abs(loo_std), 68.2689)), abs=1e-6
    )
    # All three synthetic regions clear the minimum LOO count, so none falls back.
    region = families["region_quantile_min_count"]
    assert region["min_loo_count"] == REGION_MIN_LOO_COUNT
    for spec in region["regions"].values():
        assert spec["loo_count"] >= REGION_MIN_LOO_COUNT
        assert spec["uses_fallback"] is False


def test_region_quantile_falls_back_when_sparse() -> None:
    rng = np.random.default_rng(1)
    loo_std = rng.standard_normal(500)
    # Make the light region sparse (below the predeclared minimum count).
    a_band_labels = np.array(
        ["light_A_lt_60"] * 10
        + ["medium_60_le_A_lt_140"] * 240
        + ["heavy_A_ge_140"] * 250
    )
    config = _build_frozen_config(loo_std, a_band_labels)
    region = config["families"]["region_quantile_min_count"]
    light = region["regions"]["light_A_lt_60"]
    assert light["loo_count"] == 10
    assert light["uses_fallback"] is True
    grt = config["families"]["global_robust_tail"]
    assert light["interval_multiplier_1sigma"] == pytest.approx(
        grt["interval_multiplier_1sigma"], abs=1e-9
    )


def test_score_intervals_coverage_monotone() -> None:
    rng = np.random.default_rng(2)
    sigma = np.full(400, 1.0)
    residual = rng.standard_normal(400)
    narrow = _score_intervals(residual, sigma, 0.5 * np.ones(400), 1.0 * np.ones(400))
    wide = _score_intervals(residual, sigma, 2.0 * np.ones(400), 4.0 * np.ones(400))
    # Wider intervals cover at least as much as narrower ones.
    assert wide["empirical_coverage_1sigma"] >= narrow["empirical_coverage_1sigma"]
    # Width inflation reflects the supplied multiplier.
    assert narrow["median_width_inflation"] == pytest.approx(0.5, abs=1e-9)
    assert wide["median_width_inflation"] == pytest.approx(2.0, abs=1e-9)


def test_evaluate_success_passes_well_calibrated() -> None:
    well = {
        "empirical_coverage_1sigma": 0.68,
        "empirical_coverage_2sigma": 0.95,
        "rms_standardized_residual": 1.0,
        "median_width_inflation": 1.0,
        "p90_width_inflation": 1.2,
    }
    assert _evaluate_success(well)["all_conditions_pass"] is True
    heavy_tail = {**well, "rms_standardized_residual": 4.0}
    result = _evaluate_success(heavy_tail)
    assert result["tail_control_pass"] is False
    assert result["all_conditions_pass"] is False


# --------------------------------------------------------------------------- #
# Committed-artifact invariants (the honest no-peek FAIL)
# --------------------------------------------------------------------------- #


def test_no_holdout_used_for_calibration(metrics: dict) -> None:
    assert metrics["dataset_summary"]["post_ame2020_rows_used_for_calibration"] == 0
    assert metrics["dataset_summary"]["training_row_count"] == 2309
    assert metrics["dataset_summary"]["holdout_primary_row_count"] == 295
    assert metrics["frozen_config"]["frozen_before_holdout_scoring"] is True


def test_loo_diagnostics_match_merged_adjudication(metrics: dict) -> None:
    # The closed-form GP LOO diagnostics must reproduce the merged TASK-0844
    # adjudication note's train-only LOO numbers exactly.
    loo = metrics["train_only_loo_diagnostics"]
    assert loo["count"] == 2309
    assert loo["rms_standardized_residual"] == pytest.approx(1.08951, abs=1e-5)
    assert loo["abs_p99"] == pytest.approx(4.10063, abs=1e-4)
    assert loo["abs_max"] == pytest.approx(19.017237, abs=1e-4)


def test_uncalibrated_holdout_matches_result0025(metrics: dict) -> None:
    uncal = metrics["holdout_uncalibrated_reference"]
    cov = uncal["interval_metrics"]
    std = uncal["standardized_summary"]
    assert cov["empirical_coverage_1sigma"] == pytest.approx(0.823729, abs=1e-5)
    assert cov["empirical_coverage_2sigma"] == pytest.approx(0.966102, abs=1e-5)
    assert std["rms_standardized_residual"] == pytest.approx(2.826769, abs=1e-5)


def test_all_three_families_present_and_scored(metrics: dict) -> None:
    families = metrics["family_results"]
    assert set(families) == {
        "global_robust_tail",
        "region_quantile_min_count",
        "conformal_global",
    }
    for result in families.values():
        for key in (
            "empirical_coverage_1sigma",
            "empirical_coverage_2sigma",
            "rms_standardized_residual",
            "median_width_inflation",
            "p90_width_inflation",
        ):
            assert key in result["holdout_metrics"]
        assert "all_conditions_pass" in result["success"]


def test_audit_fails_and_keeps_freeze_blocked(metrics: dict) -> None:
    # The honest finding: no no-peek route meets the predeclared targets, so the
    # tail-control condition fails and the prediction freeze stays blocked.
    assert metrics["verdict"] == "NO_PEEK_CALIBRATION_FAIL_TASK_0827_STILL_BLOCKED"
    assert metrics["audit_decision"]["any_family_passes"] is False
    assert metrics["audit_decision"]["passing_families"] == []
    assert metrics["prediction_freeze_impact"] == "unchanged_task_0827_remains_blocked"
    # Every family fails tail control specifically (heavy-tailed holdout).
    for result in metrics["family_results"].values():
        rms_z = result["holdout_metrics"]["rms_standardized_residual"]
        within_band = SUCCESS_RMS_Z_LOW <= rms_z <= SUCCESS_RMS_Z_HIGH
        assert within_band is False
        assert result["success"]["tail_control_pass"] is False


def test_routing_promotes_no_artifact(metrics: dict) -> None:
    routing = metrics["output_routing"]
    assert routing["claim_impact"] == "none"
    assert routing["knowledge_impact"] == "none"
    assert routing["result_impact"] == "none"
    assert routing["prediction_impact"] == "none"
    assert routing["canonical_destination"] == "sandbox_agent_run_plus_review_note"
    assert metrics["limitations"]


def test_outlier_ledger_records_known_tail(metrics: dict) -> None:
    ledger = metrics["outlier_ledger"]
    assert ledger, "expected a non-empty holdout outlier ledger"
    # Ga-84 is the dominant heavy-tail outlier in the post-AME2020 holdout.
    top = ledger[0]
    assert top["nuclide_id"] == "Ga-84"
    assert top["standardized_residual"] == pytest.approx(46.302384, abs=1e-3)
