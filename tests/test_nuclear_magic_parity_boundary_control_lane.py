"""Tests for the TASK-0475 magic-parity boundary control lane runner."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.engines.nuclear_mass_baselines import MAGIC_NUMBERS  # noqa: E402

from scripts.run_nuclear_magic_parity_boundary_control_lane import (  # noqa: E402
    CUSTOM_TO_SCHEMA_VERDICT,
    CUSTOM_VERDICTS,
    GAUSSIAN_TWO_SIGMA_SQUARED,
    LOO_SIGN_FLIP_THRESHOLD,
    SURVIVAL_MARGIN_MEV,
    build_metrics,
    decide_verdict,
    fit_beta,
    interaction_feature,
    loo_stability_summary,
    magic_boundary_score,
    magic_distance,
    pairing_sign,
)


def test_interaction_feature_peaks_for_even_even_magic_boundary() -> None:
    """Interaction is +1.0 for even-even rows exactly on a magic boundary."""
    assert interaction_feature(20, 20) == pytest.approx(1.0, abs=1e-9)
    assert interaction_feature(82, 126) == pytest.approx(1.0, abs=1e-9)
    far = interaction_feature(60, 100)
    assert 0.0 < far < 1.0


def test_interaction_feature_combines_parity_and_magic_boundary() -> None:
    """interaction(Z, N) == pairing_sign * max(gauss_z, gauss_n)."""
    for z, n in [(60, 100), (11, 11), (50, 82), (40, 91)]:
        gz = math.exp(-magic_distance(z) ** 2 / GAUSSIAN_TWO_SIGMA_SQUARED)
        gn = math.exp(-magic_distance(n) ** 2 / GAUSSIAN_TWO_SIGMA_SQUARED)
        assert magic_boundary_score(z, n) == pytest.approx(max(gz, gn), abs=1e-12)
        assert interaction_feature(z, n) == pytest.approx(
            pairing_sign(z, n) * max(gz, gn), abs=1e-12
        )


def test_pairing_sign_zeroes_odd_a_rows() -> None:
    assert pairing_sign(20, 21) == 0.0
    assert interaction_feature(20, 21) == 0.0
    assert pairing_sign(21, 21) == -1.0


def test_magic_distance_matches_published_set() -> None:
    for magic in MAGIC_NUMBERS:
        assert magic_distance(magic) == 0
    assert magic_distance(21) == 1
    assert magic_distance(53) == 3


def test_fit_beta_recovers_exact_signal() -> None:
    beta_true = 4.2
    rows = [
        {"Z": 20, "N": 20, "baseline_residual_mev": beta_true * interaction_feature(20, 20)},
        {"Z": 82, "N": 126, "baseline_residual_mev": beta_true * interaction_feature(82, 126)},
        {"Z": 60, "N": 100, "baseline_residual_mev": beta_true * interaction_feature(60, 100)},
    ]
    assert fit_beta(rows) == pytest.approx(beta_true, abs=1e-9)


def test_fit_beta_zero_when_all_features_zero() -> None:
    """If no row has interaction > 0 (impossible with Gaussian) — but check edge."""
    rows: list[dict] = []
    assert fit_beta(rows) == 0.0


def test_loo_stability_summary_handles_empty_input() -> None:
    summary = loo_stability_summary([])
    assert summary["count"] == 0
    assert summary["mean_mev"] is None
    assert summary["sign_flip_count"] == 0


def test_loo_stability_summary_detects_sign_flips() -> None:
    """LOO betas of opposite sign to the mean produce sign-flip count."""
    # mean of [3, 4, -1, 2] is +2 (positive); the single negative flips vs mean
    summary = loo_stability_summary([3.0, 4.0, -1.0, 2.0])
    assert summary["mean_mev"] == pytest.approx(2.0)
    assert summary["sign_flip_count"] == 1


def test_decide_verdict_negative_when_candidate_fails_margin() -> None:
    metrics = _passable_metrics_template()
    metrics["baseline"]["full_known"]["mae_mev"] = 2.0
    metrics["candidate"]["full_known"]["mae_mev"] = 1.9
    verdict, _ = decide_verdict(metrics)
    assert verdict == "NEGATIVE_RESULT"


def test_decide_verdict_control_dominated() -> None:
    metrics = _passable_metrics_template()
    metrics["baseline"]["full_known"]["mae_mev"] = 2.0
    metrics["candidate"]["full_known"]["mae_mev"] = 1.5
    # smooth_a control matches
    metrics["control_smooth_a"]["full_known"]["mae_mev"] = 1.6
    verdict, rationale = decide_verdict(metrics)
    assert verdict == "CONTROL_DOMINATED"
    assert any("smooth_a" in line for line in rationale)


def test_decide_verdict_fragile_when_sign_flips() -> None:
    metrics = _passable_metrics_template()
    metrics["baseline"]["full_known"]["mae_mev"] = 2.0
    metrics["candidate"]["full_known"]["mae_mev"] = 1.5
    metrics["control_smooth_a"]["full_known"]["mae_mev"] = 1.95
    metrics["control_asymmetry_only"]["full_known"]["mae_mev"] = 1.95
    metrics["control_parity_only"]["full_known"]["mae_mev"] = 1.95
    metrics["control_magic_distance_only"]["full_known"]["mae_mev"] = 1.95
    metrics["control_shuffled_label"]["full_known"]["mae_mev"] = 1.95
    metrics["coefficient_loo_stability"]["sign_flip_count"] = LOO_SIGN_FLIP_THRESHOLD
    verdict, _ = decide_verdict(metrics)
    assert verdict == "FRAGILE_INCONCLUSIVE"


def test_decide_verdict_bounded_diagnostic_when_full_gauntlet_passed() -> None:
    metrics = _passable_metrics_template()
    metrics["baseline"]["full_known"]["mae_mev"] = 2.0
    metrics["candidate"]["full_known"]["mae_mev"] = 1.5
    metrics["control_smooth_a"]["full_known"]["mae_mev"] = 1.95
    metrics["control_asymmetry_only"]["full_known"]["mae_mev"] = 1.95
    metrics["control_parity_only"]["full_known"]["mae_mev"] = 1.95
    metrics["control_magic_distance_only"]["full_known"]["mae_mev"] = 1.95
    metrics["control_shuffled_label"]["full_known"]["mae_mev"] = 1.95
    metrics["coefficient_loo_stability"]["sign_flip_count"] = 0
    verdict, rationale = decide_verdict(metrics)
    assert verdict == "BOUNDED_DIAGNOSTIC"
    assert any("Capped at" in line for line in rationale)


def test_custom_to_schema_mapping_is_complete() -> None:
    """Every custom verdict has a schema mapping."""
    assert set(CUSTOM_TO_SCHEMA_VERDICT.keys()) == set(CUSTOM_VERDICTS)
    allowed_schema = {"SANDBOX_PASS", "SANDBOX_FAIL", "FALSIFIED", "INCONCLUSIVE", "OVERFITTED", "REVIEW_NEEDED"}
    for schema_value in CUSTOM_TO_SCHEMA_VERDICT.values():
        assert schema_value in allowed_schema


def _passable_metrics_template() -> dict:
    return {
        "candidate": {
            "training_lstsq": {"mae_mev": 1.0},
            "primary_holdout": {"mae_mev": 1.0},
            "full_known": {"mae_mev": 1.0},
        },
        "baseline": {
            "training_lstsq": {"mae_mev": 2.0},
            "primary_holdout": {"mae_mev": 2.0},
            "full_known": {"mae_mev": 2.0},
        },
        "control_smooth_a": {
            "training_lstsq": {"mae_mev": 2.0},
            "primary_holdout": {"mae_mev": 2.0},
            "full_known": {"mae_mev": 2.0},
        },
        "control_asymmetry_only": {
            "training_lstsq": {"mae_mev": 2.0},
            "primary_holdout": {"mae_mev": 2.0},
            "full_known": {"mae_mev": 2.0},
        },
        "control_parity_only": {
            "training_lstsq": {"mae_mev": 2.0},
            "primary_holdout": {"mae_mev": 2.0},
            "full_known": {"mae_mev": 2.0},
        },
        "control_magic_distance_only": {
            "training_lstsq": {"mae_mev": 2.0},
            "primary_holdout": {"mae_mev": 2.0},
            "full_known": {"mae_mev": 2.0},
        },
        "control_shuffled_label": {
            "training_lstsq": {"mae_mev": 2.0},
            "primary_holdout": {"mae_mev": 2.0},
            "full_known": {"mae_mev": 2.0},
        },
        "coefficient_loo_stability": {
            "count": 5,
            "mean_mev": 1.0,
            "std_mev": 0.1,
            "sign_flip_count": 0,
        },
    }


def test_runner_smoke_against_committed_data() -> None:
    metrics = build_metrics()
    assert metrics["verdict"] in CUSTOM_VERDICTS
    assert metrics["schema_verdict"] in {"REVIEW_NEEDED", "INCONCLUSIVE", "FALSIFIED"}
    assert metrics["agent_run_id"] == "AGENT-RUN-0047"
    assert metrics["survival_margin_mev"] == SURVIVAL_MARGIN_MEV
    for surface in ("training_lstsq", "primary_holdout", "full_known"):
        for block in (
            "candidate",
            "baseline",
            "control_smooth_a",
            "control_asymmetry_only",
            "control_parity_only",
            "control_magic_distance_only",
            "control_shuffled_label",
        ):
            assert "mae_mev" in metrics[block][surface]


def test_committed_metrics_matches_runner_output() -> None:
    committed = json.loads(
        (REPO_ROOT / "agent_runs" / "AGENT-RUN-0047" / "metrics.json").read_text(
            encoding="utf-8"
        )
    )
    recomputed = build_metrics()
    for surface in ("training_lstsq", "primary_holdout", "full_known"):
        for block in (
            "candidate",
            "baseline",
            "control_smooth_a",
            "control_asymmetry_only",
            "control_parity_only",
            "control_magic_distance_only",
            "control_shuffled_label",
        ):
            c = committed[block][surface]["mae_mev"]
            r = recomputed[block][surface]["mae_mev"]
            assert c == pytest.approx(r), f"{block} {surface} MAE drift"
    assert committed["verdict"] == recomputed["verdict"]
    assert committed["schema_verdict"] == recomputed["schema_verdict"]
    assert committed["candidate_coefficient_beta_mev"] == pytest.approx(
        recomputed["candidate_coefficient_beta_mev"]
    )
