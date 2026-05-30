"""Tests for the TASK-0474 pairing-asymmetry interaction control lane runner."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_nuclear_pairing_asymmetry_interaction_control_lane import (  # noqa: E402
    CUSTOM_TO_SCHEMA_VERDICT,
    CUSTOM_VERDICTS,
    LOO_SIGN_FLIP_THRESHOLD,
    SURVIVAL_MARGIN_MEV,
    build_metrics,
    decide_verdict,
    fit_beta,
    interaction_feature,
    loo_stability_summary,
    neutron_excess,
    pairing_only_feature,
)


def test_neutron_excess_uses_committed_identifiers_only() -> None:
    assert neutron_excess(20, 28, 48) == pytest.approx(8 / 48)
    assert neutron_excess(28, 20, 48) == pytest.approx(-8 / 48)
    assert neutron_excess(1, 1, 0) == 0.0


def test_pairing_asymmetry_interaction_combines_pairing_and_asymmetry() -> None:
    # even-even row: pairing_sign=+1
    assert interaction_feature(20, 28, 48) == pytest.approx(8 / 48)
    # odd-odd row: pairing_sign=-1, so the neutron excess contribution flips
    assert interaction_feature(21, 29, 50) == pytest.approx(-8 / 50)
    # odd-A row: pairing_sign=0, so the interaction is inert
    assert interaction_feature(20, 29, 49) == 0.0


def test_pairing_only_feature_scales_with_a() -> None:
    assert pairing_only_feature(20, 28, 48) == pytest.approx(1 / (48**0.5))
    assert pairing_only_feature(21, 29, 50) == pytest.approx(-1 / (50**0.5))
    assert pairing_only_feature(20, 29, 49) == 0.0


def test_fit_beta_recovers_exact_signal() -> None:
    beta_true = 4.2
    rows = [
        {"Z": 20, "N": 28, "A": 48, "baseline_residual_mev": beta_true * interaction_feature(20, 28, 48)},
        {"Z": 21, "N": 29, "A": 50, "baseline_residual_mev": beta_true * interaction_feature(21, 29, 50)},
        {"Z": 50, "N": 82, "A": 132, "baseline_residual_mev": beta_true * interaction_feature(50, 82, 132)},
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
    metrics["control_pairing_only"]["full_known"]["mae_mev"] = 1.95
    metrics["control_matched_degree_random"]["full_known"]["mae_mev"] = 1.95
    metrics["coefficient_loo_stability"]["sign_flip_count"] = LOO_SIGN_FLIP_THRESHOLD
    verdict, _ = decide_verdict(metrics)
    assert verdict == "FRAGILE_INCONCLUSIVE"


def test_decide_verdict_shell_adjacent_when_full_gauntlet_passed() -> None:
    metrics = _passable_metrics_template()
    metrics["baseline"]["full_known"]["mae_mev"] = 2.0
    metrics["candidate"]["full_known"]["mae_mev"] = 1.5
    metrics["control_smooth_a"]["full_known"]["mae_mev"] = 1.95
    metrics["control_asymmetry_only"]["full_known"]["mae_mev"] = 1.95
    metrics["control_pairing_only"]["full_known"]["mae_mev"] = 1.95
    metrics["control_matched_degree_random"]["full_known"]["mae_mev"] = 1.95
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
        "control_pairing_only": {
            "training_lstsq": {"mae_mev": 2.0},
            "primary_holdout": {"mae_mev": 2.0},
            "full_known": {"mae_mev": 2.0},
        },
        "control_matched_degree_random": {
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
    assert metrics["agent_run_id"] == "AGENT-RUN-0046"
    assert metrics["survival_margin_mev"] == SURVIVAL_MARGIN_MEV
    for surface in ("training_lstsq", "primary_holdout", "full_known"):
        for block in (
            "candidate",
            "baseline",
            "control_smooth_a",
            "control_asymmetry_only",
            "control_pairing_only",
            "control_matched_degree_random",
        ):
            assert "mae_mev" in metrics[block][surface]


def test_committed_metrics_matches_runner_output() -> None:
    committed = json.loads(
        (REPO_ROOT / "agent_runs" / "AGENT-RUN-0046" / "metrics.json").read_text(
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
            "control_pairing_only",
            "control_matched_degree_random",
        ):
            c = committed[block][surface]["mae_mev"]
            r = recomputed[block][surface]["mae_mev"]
            assert c == pytest.approx(r), f"{block} {surface} MAE drift"
    assert committed["verdict"] == recomputed["verdict"]
    assert committed["schema_verdict"] == recomputed["schema_verdict"]
    assert committed["candidate_coefficient_beta_mev"] == pytest.approx(
        recomputed["candidate_coefficient_beta_mev"]
    )
