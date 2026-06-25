"""Tests for the TASK-0824 calibrated-uncertainty GP residual extrapolation engine.

The full-surface GP fit takes tens of seconds, so the committed sandbox
``agent_runs/AGENT-RUN-0080/metrics.json`` artifact (produced by the pinned,
deterministic runner) is the fixture for the headline-number, leakage, controls,
and calibration assertions. The engine's fitting logic and determinism are
exercised directly on small synthetic inputs that run in well under a second.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from physics_lab.engines.nmd0003_residual_gp import (
    FROZEN_BASELINE_ID,
    SURVIVAL_MARGIN_MEV,
    fit_residual_gp,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
COMMITTED_METRICS_PATH = REPO_ROOT / "agent_runs/AGENT-RUN-0080/metrics.json"


@pytest.fixture(scope="module")
def metrics() -> dict:
    """The committed, deterministic sandbox AGENT-RUN-0080 metrics artifact."""
    return json.loads(COMMITTED_METRICS_PATH.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# Engine fitting logic on small synthetic inputs (fast, no full-surface fit)
# --------------------------------------------------------------------------- #


def test_fit_residual_gp_is_deterministic() -> None:
    """The GP marginal-likelihood fit is bit-reproducible on identical inputs."""
    rng = np.random.default_rng(0)
    z = rng.integers(1, 60, size=80).astype(float)
    n = rng.integers(1, 80, size=80).astype(float)
    residual = 0.3 * np.sin(z / 5.0) + 0.1 * n + rng.normal(0, 0.2, size=80)
    fit_a = fit_residual_gp(z, n, residual)
    fit_b = fit_residual_gp(z, n, residual)
    assert fit_a.sigma_f == fit_b.sigma_f
    assert fit_a.length_scale == fit_b.length_scale
    assert fit_a.sigma_n == fit_b.sigma_n
    assert fit_a.log_marginal_likelihood == fit_b.log_marginal_likelihood


def test_fit_residual_gp_recovers_training_signal() -> None:
    """Posterior mean tracks a smooth synthetic residual surface in-sample."""
    rng = np.random.default_rng(1)
    z = rng.integers(1, 60, size=120).astype(float)
    n = rng.integers(1, 80, size=120).astype(float)
    truth = 0.5 * np.sin(z / 6.0) + 0.02 * n
    residual = truth + rng.normal(0, 0.05, size=120)
    fit = fit_residual_gp(z, n, residual)
    mean, sigma = fit.predict(z, n)
    assert np.mean(np.abs(mean - truth)) < np.mean(np.abs(residual - truth)) + 0.05
    assert np.all(sigma > 0.0)


def test_predict_with_targets_matches_predict_on_same_targets() -> None:
    """The fixed-hyperparameter null path agrees with predict() on the real targets."""
    rng = np.random.default_rng(2)
    z = rng.integers(1, 50, size=60).astype(float)
    n = rng.integers(1, 70, size=60).astype(float)
    residual = 0.4 * np.cos(z / 4.0) + 0.05 * n + rng.normal(0, 0.1, size=60)
    fit = fit_residual_gp(z, n, residual)
    z_star = rng.integers(1, 50, size=15).astype(float)
    n_star = rng.integers(1, 70, size=15).astype(float)
    mean_a, sigma_a = fit.predict(z_star, n_star)
    mean_b, sigma_b = fit.predict_with_targets(z_star, n_star, residual)
    assert np.allclose(mean_a, mean_b, atol=1e-9)
    assert np.allclose(sigma_a, sigma_b, atol=1e-9)


# --------------------------------------------------------------------------- #
# Committed-artifact invariants
# --------------------------------------------------------------------------- #


def test_no_holdout_leakage(metrics: dict) -> None:
    assert metrics["dataset_summary"]["post_ame2020_rows_used_for_fitting"] == 0
    assert metrics["dataset_summary"]["training_row_count"] == 2309
    assert metrics["dataset_summary"]["holdout_primary_row_count"] == 295


def test_frozen_baseline_identity(metrics: dict) -> None:
    assert metrics["frozen_baseline"]["baseline_id"] == FROZEN_BASELINE_ID
    assert metrics["input_references"]["frozen_baseline_id"] == FROZEN_BASELINE_ID


def test_extrapolation_metrics_recorded(metrics: dict) -> None:
    extrapolation = metrics["extrapolation"]
    baseline = extrapolation["frozen_baseline_holdout"]
    gp = extrapolation["gp_corrected_holdout"]
    assert baseline["count"] == 295
    assert gp["count"] == 295
    # The GP reduces holdout extrapolation MAE versus the frozen baseline.
    assert gp["mae_mev"] < baseline["mae_mev"]
    assert extrapolation["gp_mae_improvement_mev"] > 0.0
    # Lock the headline numbers so regressions are caught.
    assert baseline["mae_mev"] == pytest.approx(2.979273, abs=1e-5)
    assert gp["mae_mev"] == pytest.approx(0.462129, abs=1e-4)


def test_calibration_block_present_and_honest(metrics: dict) -> None:
    calibration = metrics["calibration"]
    for key in (
        "empirical_coverage_1sigma",
        "empirical_coverage_2sigma",
        "rms_standardized_residual",
    ):
        assert key in calibration
    # Coverage fractions are valid probabilities.
    assert 0.0 <= calibration["empirical_coverage_1sigma"] <= 1.0
    assert 0.0 <= calibration["empirical_coverage_2sigma"] <= 1.0
    # The honest finding: predictive bands are heavy-tailed / mis-calibrated.
    assert calibration["rms_standardized_residual"] > 1.0
    assert metrics["calibration_verdict"] in {
        "WELL_CALIBRATED",
        "MILDLY_MISCALIBRATED",
        "UNDERCONFIDENT_HEAVY_TAILED",
        "OVERCONFIDENT",
    }


def test_controls_first_decision(metrics: dict) -> None:
    decision = metrics["decision"]
    assert decision["predeclared_survival_margin_mev"] == SURVIVAL_MARGIN_MEV
    assert "null_shuffled_target_gp" in decision["control_mae_improvements_mev"]
    assert "smooth_a_gp" in decision["control_mae_improvements_mev"]
    # Survival margin is GP improvement minus the best control improvement.
    assert decision["gp_minus_best_control_mae_improvement_mev"] == pytest.approx(
        decision["gp_mae_improvement_mev"] - decision["best_control_mae_improvement_mev"],
        abs=1e-6,
    )
    # Null shuffled-target control must not manufacture a real extrapolation gain.
    assert decision["control_mae_improvements_mev"]["null_shuffled_target_gp"] < (
        decision["gp_mae_improvement_mev"]
    )


def test_verdict_and_routing_promote_no_claim(metrics: dict) -> None:
    assert metrics["verdict"] in {
        "CONTROL_SURVIVING_GAIN_WELL_CALIBRATED",
        "CONTROL_SURVIVING_GAIN_MISCALIBRATED_UNCERTAINTY",
        "INCONCLUSIVE_CONTROL_DOMINATED",
        "NEGATIVE_RESULT_NO_EXTRAPOLATION_GAIN",
    }
    routing = metrics["output_routing"]
    assert routing["claim_impact"] == "none"
    assert routing["knowledge_impact"] == "none"
    assert metrics["limitations"]
