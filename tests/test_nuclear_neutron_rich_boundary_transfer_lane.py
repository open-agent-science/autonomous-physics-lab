"""Tests for the TASK-0450 neutron-rich boundary transfer lane runner."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_nuclear_neutron_rich_boundary_transfer_lane import (  # noqa: E402
    NEUTRON_RICH_ASYMMETRY_THRESHOLD,
    SURVIVAL_MARGIN_MEV,
    boundary_distance,
    build_metrics,
    decide_verdict,
    fit_beta,
    is_neutron_rich,
)


def test_boundary_distance_zero_for_symmetric_or_proton_rich() -> None:
    """N=Z and proton-rich rows return zero boundary distance."""
    assert boundary_distance(20, 20, 40) == 0.0
    assert boundary_distance(10, 8, 18) == 0.0  # proton-rich
    assert boundary_distance(50, 50, 100) == 0.0


def test_boundary_distance_positive_for_neutron_rich() -> None:
    """N >> Z rows return positive boundary distance."""
    value = boundary_distance(50, 80, 130)
    expected = (80 - 50) / 130 - NEUTRON_RICH_ASYMMETRY_THRESHOLD
    assert value == pytest.approx(expected, abs=1e-9)
    assert is_neutron_rich(50, 80, 130) is True


def test_boundary_distance_rejects_invalid_mass_number() -> None:
    with pytest.raises(ValueError):
        boundary_distance(1, 1, 0)


def test_fit_beta_recovers_exact_signal() -> None:
    """If residuals equal beta_true * boundary, fit recovers beta_true."""
    beta_true = 3.5
    rows = [
        {"Z": 50, "N": 80, "A": 130, "baseline_residual_mev": beta_true * boundary_distance(50, 80, 130)},
        {"Z": 50, "N": 70, "A": 120, "baseline_residual_mev": beta_true * boundary_distance(50, 70, 120)},
        {"Z": 20, "N": 20, "A": 40, "baseline_residual_mev": 0.0},
    ]
    beta = fit_beta(rows)
    assert beta == pytest.approx(beta_true, abs=1e-9)


def test_fit_beta_returns_zero_when_feature_all_zero() -> None:
    """If no row has positive boundary distance, fit returns 0.0 not NaN."""
    rows = [
        {"Z": 20, "N": 20, "A": 40, "baseline_residual_mev": 1.0},
        {"Z": 10, "N": 8, "A": 18, "baseline_residual_mev": -2.0},
    ]
    assert fit_beta(rows) == 0.0


def test_decide_verdict_inconclusive_when_training_sparse() -> None:
    """If <2 neutron-rich training rows, verdict is INCONCLUSIVE."""
    metrics = _passable_metrics_template()
    metrics["training_rows_overview"] = [
        {"Z": 20, "N": 20, "A": 40, "is_neutron_rich": False},
        {"Z": 10, "N": 12, "A": 22, "is_neutron_rich": False},
    ]
    verdict, _ = decide_verdict(metrics)
    assert verdict == "INCONCLUSIVE"


def test_decide_verdict_negative_when_candidate_fails_margin() -> None:
    metrics = _passable_metrics_template()
    metrics["baseline"]["full_known"]["mae_mev"] = 2.0
    metrics["candidate"]["full_known"]["mae_mev"] = 1.9  # only 0.1 better
    verdict, _ = decide_verdict(metrics)
    assert verdict == "NEGATIVE_RESULT"


def test_decide_verdict_diagnostic_when_matched_control_matches() -> None:
    metrics = _passable_metrics_template()
    metrics["baseline"]["full_known"]["mae_mev"] = 2.0
    metrics["candidate"]["full_known"]["mae_mev"] = 1.5  # 0.5 over baseline
    metrics["control_matched_high_error"]["full_known"]["mae_mev"] = 1.6  # delta 0.1 only
    verdict, _ = decide_verdict(metrics)
    assert verdict == "DIAGNOSTIC_ONLY"


def test_decide_verdict_diagnostic_when_chain_transfer_low() -> None:
    metrics = _passable_metrics_template()
    metrics["baseline"]["full_known"]["mae_mev"] = 2.0
    metrics["candidate"]["full_known"]["mae_mev"] = 1.5
    metrics["control_matched_high_error"]["full_known"]["mae_mev"] = 1.9
    metrics["control_sign_inverted"]["full_known"]["mae_mev"] = 1.95
    metrics["isotope_chain_transfer_rate"] = 0.25
    verdict, rationale = decide_verdict(metrics)
    assert verdict == "DIAGNOSTIC_ONLY"
    assert any("transfer" in line for line in rationale)


def test_decide_verdict_bounded_followup_when_full_gauntlet_passed() -> None:
    metrics = _passable_metrics_template()
    metrics["baseline"]["full_known"]["mae_mev"] = 2.0
    metrics["candidate"]["full_known"]["mae_mev"] = 1.5
    metrics["control_matched_high_error"]["full_known"]["mae_mev"] = 1.9
    metrics["control_sign_inverted"]["full_known"]["mae_mev"] = 1.95
    metrics["isotope_chain_transfer_rate"] = 0.75
    metrics["candidate"]["primary_holdout"]["mae_mev"] = 1.5
    metrics["baseline"]["primary_holdout"]["mae_mev"] = 1.6
    verdict, _ = decide_verdict(metrics)
    assert verdict == "BOUNDED_FOLLOWUP_CANDIDATE"


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
        "control_matched_high_error": {
            "training_lstsq": {"mae_mev": 2.0},
            "primary_holdout": {"mae_mev": 2.0},
            "full_known": {"mae_mev": 2.0},
        },
        "control_sign_inverted": {
            "training_lstsq": {"mae_mev": 2.0},
            "primary_holdout": {"mae_mev": 2.0},
            "full_known": {"mae_mev": 2.0},
        },
        "training_rows_overview": [
            {"Z": 50, "N": 80, "A": 130, "is_neutron_rich": True},
            {"Z": 50, "N": 70, "A": 120, "is_neutron_rich": True},
        ],
        "isotope_chain_transfer_rate": 0.75,
    }


def test_runner_smoke_against_committed_data() -> None:
    metrics = build_metrics()
    assert metrics["verdict"] in {
        "BOUNDED_FOLLOWUP_CANDIDATE",
        "DIAGNOSTIC_ONLY",
        "NEGATIVE_RESULT",
        "INCONCLUSIVE",
    }
    assert metrics["agent_run_id"] == "AGENT-RUN-0044"
    assert metrics["survival_margin_mev"] == SURVIVAL_MARGIN_MEV
    for surface in ("training_lstsq", "primary_holdout", "full_known"):
        for block in ("candidate", "baseline", "control_matched_high_error", "control_sign_inverted"):
            assert "mae_mev" in metrics[block][surface]


def test_committed_metrics_matches_runner_output() -> None:
    committed = json.loads(
        (REPO_ROOT / "agent_runs" / "AGENT-RUN-0044" / "metrics.json").read_text(
            encoding="utf-8"
        )
    )
    recomputed = build_metrics()
    for surface in ("training_lstsq", "primary_holdout", "full_known"):
        for block in ("candidate", "baseline", "control_matched_high_error", "control_sign_inverted"):
            c = committed[block][surface]["mae_mev"]
            r = recomputed[block][surface]["mae_mev"]
            assert c == pytest.approx(r), f"{block} {surface} MAE drift"
    assert committed["verdict"] == recomputed["verdict"]
    assert committed["candidate_coefficient_beta_mev"] == pytest.approx(
        recomputed["candidate_coefficient_beta_mev"]
    )
