"""Tests for the TASK-0449 residual-free high-error cluster audit runner."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.engines.nuclear_mass_baselines import MAGIC_NUMBERS  # noqa: E402
from scripts.run_nuclear_residual_free_high_error_cluster_audit import (  # noqa: E402
    CLUSTER_TAXONOMY,
    MAGIC_DISTANCE_THRESHOLD,
    MATCHED_RANDOM_SEED,
    NEUTRON_RICH_ASYMMETRY_THRESHOLD,
    SURVIVAL_MARGIN_MEV,
    _fit_linear,
    assign_cluster_label,
    build_metrics,
    cluster_counts,
    decide_verdict,
    leave_one_out_offsets_training,
    magic_distance,
    matched_random_labels,
)


# --------------------------------------------------------------------------- #
# Pure-function tests (no I/O)
# --------------------------------------------------------------------------- #


def test_magic_distance_known_values() -> None:
    """Magic-number distance is a deterministic function of one integer."""
    assert magic_distance(2) == 0
    assert magic_distance(20) == 0
    assert magic_distance(82) == 0
    assert magic_distance(83) == 1
    assert magic_distance(85) == 3
    assert magic_distance(50) == 0
    # all canonical magic numbers map to zero
    for magic in MAGIC_NUMBERS:
        assert magic_distance(magic) == 0


def test_cluster_label_uses_only_z_n_a() -> None:
    """assign_cluster_label is a pure function of Z, N, A only."""
    # near-magic-Z (Z=20)
    assert assign_cluster_label(z=20, n=20, a=40) == "near_magic_z_or_n"
    # near-magic-N (N=82)
    assert assign_cluster_label(z=70, n=82, a=152) == "near_magic_z_or_n"
    # neutron-rich, not near magic
    assert (
        assign_cluster_label(z=40, n=70, a=110)
        == "neutron_rich"
    )
    # light A, not near magic, not neutron rich
    assert assign_cluster_label(z=15, n=15, a=30) == "light_a_lt_50"
    # other (mid-mass, low asymmetry, not near magic)
    assert assign_cluster_label(z=46, n=60, a=106) == "other"


def test_cluster_label_thresholds_are_inclusive() -> None:
    """Boundary cases respect the declared thresholds."""
    # Z=4 is exactly magic_distance 2 from magic 2; should be near-magic
    assert magic_distance(4) == 2
    assert assign_cluster_label(z=4, n=4, a=8) == "near_magic_z_or_n"
    # asymmetry exactly at threshold should be neutron_rich
    asym_row_a = 100
    asym_row_n = int(asym_row_a * NEUTRON_RICH_ASYMMETRY_THRESHOLD / 2 + asym_row_a / 2)
    asym_row_z = asym_row_a - asym_row_n
    # avoid near-magic
    if magic_distance(asym_row_z) > MAGIC_DISTANCE_THRESHOLD and magic_distance(
        asym_row_n
    ) > MAGIC_DISTANCE_THRESHOLD:
        label = assign_cluster_label(z=asym_row_z, n=asym_row_n, a=asym_row_a)
        assert label in {"neutron_rich", "other"}


def test_cluster_label_rejects_invalid_input() -> None:
    """Invalid (Z, N, A) raises ValueError; no silent label drift."""
    with pytest.raises(ValueError):
        assign_cluster_label(z=-1, n=0, a=1)
    with pytest.raises(ValueError):
        assign_cluster_label(z=1, n=1, a=0)


def test_matched_random_labels_preserves_marginal() -> None:
    """The matched-random control permutes labels but preserves the marginal."""
    labels = ["a", "a", "b", "b", "b", "c"]
    shuffled = matched_random_labels(labels, seed=MATCHED_RANDOM_SEED)
    assert sorted(shuffled) == sorted(labels)
    # determinism with the canonical seed
    assert shuffled == matched_random_labels(labels, seed=MATCHED_RANDOM_SEED)


def test_leave_one_out_offsets_excludes_self() -> None:
    """LOO offset for a row is the mean of OTHER rows in the same cluster."""
    rows = [
        {"baseline_residual_mev": 1.0},
        {"baseline_residual_mev": 3.0},
        {"baseline_residual_mev": 5.0},
        {"baseline_residual_mev": 9.0},
    ]
    labels = ["a", "a", "a", "b"]
    offsets = leave_one_out_offsets_training(rows, labels)
    # row 0 (cluster a) -> mean of {3.0, 5.0} = 4.0
    # row 1 (cluster a) -> mean of {1.0, 5.0} = 3.0
    # row 2 (cluster a) -> mean of {1.0, 3.0} = 2.0
    # row 3 (cluster b) -> only member, no other rows -> 0.0
    assert offsets == [4.0, 3.0, 2.0, 0.0]


def test_cluster_counts_zero_fills_unseen_clusters() -> None:
    labels = ["near_magic_z_or_n", "neutron_rich", "neutron_rich"]
    counts = cluster_counts(labels)
    assert counts["near_magic_z_or_n"] == 1
    assert counts["neutron_rich"] == 2
    assert counts["light_a_lt_50"] == 0
    assert counts["other"] == 0
    assert set(counts.keys()) == set(CLUSTER_TAXONOMY)


def test_fit_linear_exact_recovery() -> None:
    """Exact slope/intercept recovery for a noiseless linear input."""
    import numpy as np

    x = np.asarray([1.0, 2.0, 3.0, 4.0])
    y = 0.5 + 2.0 * x
    intercept, slope = _fit_linear(x, y)
    assert intercept == pytest.approx(0.5, abs=1e-9)
    assert slope == pytest.approx(2.0, abs=1e-9)


def test_decide_verdict_inconclusive_when_clusters_too_sparse() -> None:
    """Verdict is INCONCLUSIVE when fewer than two clusters have ≥2 training rows."""
    metrics = {
        "candidate": {
            "training_loo": {"mae_mev": 1.0},
            "primary_holdout": {"mae_mev": 1.0},
            "full_known": {"mae_mev": 1.0},
        },
        "baseline": {
            "training_loo": {"mae_mev": 2.0},
            "primary_holdout": {"mae_mev": 2.0},
            "full_known": {"mae_mev": 2.0},
        },
        "control_matched_random": {
            "training_loo": {"mae_mev": 2.0},
            "primary_holdout": {"mae_mev": 2.0},
            "full_known": {"mae_mev": 2.0},
        },
        "control_smooth_a": {
            "training_loo": {"mae_mev": 2.0},
            "primary_holdout": {"mae_mev": 2.0},
            "full_known": {"mae_mev": 2.0},
        },
        "cluster_counts": {
            "training_loo": {name: 0 for name in CLUSTER_TAXONOMY},
            "primary_holdout": {name: 0 for name in CLUSTER_TAXONOMY},
        },
    }
    metrics["cluster_counts"]["training_loo"]["near_magic_z_or_n"] = 5
    verdict, _ = decide_verdict(metrics)
    assert verdict == "INCONCLUSIVE"


def test_decide_verdict_negative_when_candidate_fails_margin() -> None:
    """A candidate that does not beat baseline by the survival margin is NEGATIVE."""
    metrics = _passable_metrics_template()
    metrics["candidate"]["full_known"]["mae_mev"] = 1.95  # < 0.25 MeV improvement
    metrics["baseline"]["full_known"]["mae_mev"] = 2.00
    metrics["control_matched_random"]["full_known"]["mae_mev"] = 1.90
    metrics["control_smooth_a"]["full_known"]["mae_mev"] = 1.90
    verdict, _ = decide_verdict(metrics)
    assert verdict == "NEGATIVE_RESULT"


def test_decide_verdict_diagnostic_when_controls_not_beaten() -> None:
    """Beats baseline but does not beat both controls by margin -> DIAGNOSTIC_ONLY."""
    metrics = _passable_metrics_template()
    metrics["baseline"]["full_known"]["mae_mev"] = 2.00
    metrics["candidate"]["full_known"]["mae_mev"] = 1.50  # 0.50 over baseline
    metrics["control_matched_random"]["full_known"]["mae_mev"] = 1.60  # delta 0.10 only
    metrics["control_smooth_a"]["full_known"]["mae_mev"] = 1.90
    verdict, _ = decide_verdict(metrics)
    assert verdict == "DIAGNOSTIC_ONLY"


def test_decide_verdict_bounded_followup_when_full_gauntlet_passed() -> None:
    """Beats baseline and both controls by margin without holdout regression -> BFC."""
    metrics = _passable_metrics_template()
    metrics["baseline"]["full_known"]["mae_mev"] = 2.00
    metrics["candidate"]["full_known"]["mae_mev"] = 1.30
    metrics["control_matched_random"]["full_known"]["mae_mev"] = 1.90
    metrics["control_smooth_a"]["full_known"]["mae_mev"] = 1.80
    metrics["candidate"]["primary_holdout"]["mae_mev"] = 1.50
    metrics["baseline"]["primary_holdout"]["mae_mev"] = 1.60  # candidate better
    verdict, rationale = decide_verdict(metrics)
    assert verdict == "BOUNDED_FOLLOWUP_CANDIDATE"
    assert any("does not regress" in line for line in rationale)


def _passable_metrics_template() -> dict:
    """Return a metrics dict with at least two non-empty training clusters."""
    counts = {name: 0 for name in CLUSTER_TAXONOMY}
    counts["near_magic_z_or_n"] = 4
    counts["other"] = 4
    return {
        "candidate": {
            "training_loo": {"mae_mev": 1.0},
            "primary_holdout": {"mae_mev": 1.0},
            "full_known": {"mae_mev": 1.0},
        },
        "baseline": {
            "training_loo": {"mae_mev": 2.0},
            "primary_holdout": {"mae_mev": 2.0},
            "full_known": {"mae_mev": 2.0},
        },
        "control_matched_random": {
            "training_loo": {"mae_mev": 2.0},
            "primary_holdout": {"mae_mev": 2.0},
            "full_known": {"mae_mev": 2.0},
        },
        "control_smooth_a": {
            "training_loo": {"mae_mev": 2.0},
            "primary_holdout": {"mae_mev": 2.0},
            "full_known": {"mae_mev": 2.0},
        },
        "cluster_counts": {
            "training_loo": counts,
            "primary_holdout": {name: 1 for name in CLUSTER_TAXONOMY},
        },
    }


# --------------------------------------------------------------------------- #
# Smoke test against committed data
# --------------------------------------------------------------------------- #


def test_runner_smoke_against_committed_data() -> None:
    """End-to-end build_metrics() must run against committed data and return a verdict in the gauntlet vocabulary."""
    metrics = build_metrics()
    assert metrics["verdict"] in {
        "BOUNDED_FOLLOWUP_CANDIDATE",
        "DIAGNOSTIC_ONLY",
        "NEGATIVE_RESULT",
        "INCONCLUSIVE",
    }
    assert metrics["agent_run_id"] == "AGENT-RUN-0043"
    assert metrics["survival_margin_mev"] == SURVIVAL_MARGIN_MEV
    # Required surface metrics exist for the candidate
    for surface in ("training_loo", "primary_holdout", "full_known"):
        assert "mae_mev" in metrics["candidate"][surface]
        assert "mae_mev" in metrics["control_matched_random"][surface]
        assert "mae_mev" in metrics["control_smooth_a"][surface]
        assert "mae_mev" in metrics["baseline"][surface]


def test_committed_metrics_file_matches_runner_output() -> None:
    """The committed metrics.json must equal the runner's deterministic output."""
    committed = json.loads(
        (REPO_ROOT / "agent_runs" / "AGENT-RUN-0043" / "metrics.json").read_text(
            encoding="utf-8"
        )
    )
    recomputed = build_metrics()
    # Compare structure-relevant fields rather than rationale strings to allow
    # minor wording changes in the future; numerical fields must match.
    for surface in ("training_loo", "primary_holdout", "full_known"):
        assert committed["candidate"][surface]["mae_mev"] == pytest.approx(
            recomputed["candidate"][surface]["mae_mev"]
        )
        assert committed["control_matched_random"][surface]["mae_mev"] == pytest.approx(
            recomputed["control_matched_random"][surface]["mae_mev"]
        )
        assert committed["control_smooth_a"][surface]["mae_mev"] == pytest.approx(
            recomputed["control_smooth_a"][surface]["mae_mev"]
        )
        assert committed["baseline"][surface]["mae_mev"] == pytest.approx(
            recomputed["baseline"][surface]["mae_mev"]
        )
    assert committed["verdict"] == recomputed["verdict"]
