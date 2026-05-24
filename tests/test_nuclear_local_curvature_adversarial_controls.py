"""Tests for the TASK-0351 adversarial-controls runner.

The runner reads only committed repository datasets and produces sandbox
artifacts under agent_runs/AGENT-RUN-0031/. These tests verify the
adversarial control feature shapes, the variant composition, the metrics
output, and the survival-margin verdict logic without re-fetching live
data.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_local_curvature_adversarial_controls.py"
AGENT_RUN_DIR = REPO_ROOT / "agent_runs" / "AGENT-RUN-0031"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "run_nuclear_local_curvature_adversarial_controls", SCRIPT_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


adv = _load_module()
lane = adv.lane


# ---------------------------------------------------------------------------
# Variant composition
# ---------------------------------------------------------------------------


class TestAdversarialVariantComposition:
    def test_includes_three_predecessor_candidates(self) -> None:
        variants = adv._build_adversarial_variants()  # noqa: SLF001
        ids = {item["candidate_id"] for item in variants}
        assert "LOCAL-CURVATURE-001" in ids
        assert "LOCAL-CURVATURE-002" in ids
        assert "LOCAL-CURVATURE-003" in ids

    def test_includes_two_existing_controls(self) -> None:
        variants = adv._build_adversarial_variants()  # noqa: SLF001
        ids = {item["candidate_id"] for item in variants}
        assert "LOCAL-CONTROL-001" in ids
        assert "LOCAL-CONTROL-002" in ids

    def test_includes_three_new_adversarial_controls(self) -> None:
        variants = adv._build_adversarial_variants()  # noqa: SLF001
        ids = {item["candidate_id"] for item in variants}
        assert "LOCAL-CONTROL-003" in ids
        assert "LOCAL-CONTROL-004" in ids
        assert "LOCAL-CONTROL-005" in ids

    def test_every_variant_has_lstsq_fit_mode(self) -> None:
        variants = adv._build_adversarial_variants()  # noqa: SLF001
        for item in variants:
            assert item["fit_mode"] == "lstsq", item["candidate_id"]

    def test_new_control_roles_are_explicit(self) -> None:
        variants = {
            item["candidate_id"]: item
            for item in adv._build_adversarial_variants()  # noqa: SLF001
        }
        assert (
            variants["LOCAL-CONTROL-003"]["role"]
            == "neighbor_availability_leakage_control"
        )
        assert variants["LOCAL-CONTROL-004"]["role"] == "chain_label_shuffle_control"
        assert (
            variants["LOCAL-CONTROL-005"]["role"]
            == "smooth_local_regression_control"
        )


# ---------------------------------------------------------------------------
# Feature-function shapes
# ---------------------------------------------------------------------------


def _toy_audit_rows() -> list[dict]:
    """Small in-memory audit surface with five rows across two Z chains."""

    rows: list[dict] = []
    for idx, (z, n, residual) in enumerate(
        [
            (10, 8, -1.0),
            (10, 10, 0.5),
            (10, 12, 1.5),
            (20, 22, -0.5),
            (20, 24, 0.25),
        ]
    ):
        a = z + n
        rows.append(
            {
                "row_id": f"ROW-{idx:03d}",
                "nuclide_id": f"Z{z}N{n}",
                "Z": z,
                "N": n,
                "A": a,
                "source_surface": "training_slice",
                "baseline_residual_mev": residual,
                "observed_mev": 0.0,
                "baseline_predicted_mev": -residual,
            }
        )
    return rows


class TestFeatureShapes:
    @pytest.fixture
    def index(self) -> lane.NeighborIndex:
        return lane.NeighborIndex(_toy_audit_rows())

    def test_closest_neighbor_only_returns_one_value(
        self,
        index: lane.NeighborIndex,
    ) -> None:
        target = index.by_nuclide["Z10N10"]
        values = adv._closest_neighbor_only_isotope_mean(target, index)  # noqa: SLF001
        assert len(values) == 1
        assert isinstance(values[0], float)

    def test_closest_neighbor_prefers_smaller_dN(
        self,
        index: lane.NeighborIndex,
    ) -> None:
        # Z10N10 has neighbors Z10N8 (Delta N=2) and Z10N12 (Delta N=2).
        # Tie broken by lower N first → picks Z10N8 (residual -1.0).
        target = index.by_nuclide["Z10N10"]
        values = adv._closest_neighbor_only_isotope_mean(target, index)  # noqa: SLF001
        assert values == (-1.0,)

    def test_label_shuffle_uses_a_different_chain(
        self,
        index: lane.NeighborIndex,
    ) -> None:
        # Observed Z values are {10, 20}; shuffle maps Z=10 to Z=20.
        # Z10N10 should look up neighbors in Z=20 chain, exclude itself
        # (it is not in Z=20), and use the two closest by Delta N.
        target = index.by_nuclide["Z10N10"]
        values = adv._label_shuffled_isotope_mean(target, index)  # noqa: SLF001
        assert len(values) == 1
        # Z=20 chain residuals are -0.5 (N=22) and 0.25 (N=24).
        # By |N - 10| ordering: N=22 has |Delta|=12, N=24 has |Delta|=14.
        # Pair mean = (-0.5 + 0.25) / 2 = -0.125.
        assert values[0] == pytest.approx(-0.125)

    def test_local_linear_regression_predicts_at_target_a(
        self,
        index: lane.NeighborIndex,
    ) -> None:
        target = index.by_nuclide["Z10N10"]
        values = adv._local_linear_regression_smoother(target, index)  # noqa: SLF001
        assert len(values) == 1
        # Function should return a single float; exact value depends on
        # the toy A-window neighborhood.
        assert isinstance(values[0], float)

    def test_features_handle_missing_neighbors_gracefully(
        self,
        index: lane.NeighborIndex,
    ) -> None:
        isolated_row = {
            "row_id": "ROW-ISO",
            "nuclide_id": "Z99N99",
            "Z": 99,
            "N": 99,
            "A": 198,
            "source_surface": "training_slice",
            "baseline_residual_mev": 0.0,
            "observed_mev": 0.0,
            "baseline_predicted_mev": 0.0,
        }
        # Without neighbors all three should return (0.0,) instead of raising.
        assert adv._closest_neighbor_only_isotope_mean(isolated_row, index) == (  # noqa: SLF001
            0.0,
        )
        # Label shuffle still has Z=10 and Z=20 chains; with target Z=99
        # not in observed list, returns (0.0,).
        assert adv._label_shuffled_isotope_mean(isolated_row, index) == (0.0,)  # noqa: SLF001


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------


def _make_comparison_row(
    *,
    candidate_id: str,
    primary_margin: float | None,
    win_rate: float | None,
    subset_count: int = 19,
) -> dict:
    return {
        "candidate_id": candidate_id,
        "primary_candidate_minus_strongest_control_mev": primary_margin,
        "primary_survival_margin_mev": adv.PRIMARY_SURVIVAL_MARGIN_MEV,
        "primary_survives_adversarial_controls": (
            primary_margin is not None
            and primary_margin >= adv.PRIMARY_SURVIVAL_MARGIN_MEV
        ),
        "subset_wins_count": int((win_rate or 0.0) * subset_count),
        "subset_evaluated_count": subset_count,
        "subset_win_rate": win_rate,
    }


class TestAdversarialVerdict:
    def test_falsified_when_no_candidate_survives_or_dominates(self) -> None:
        table = [
            _make_comparison_row(
                candidate_id="A", primary_margin=-1.0, win_rate=0.1
            ),
            _make_comparison_row(
                candidate_id="B", primary_margin=-0.5, win_rate=0.3
            ),
        ]
        assert adv._adversarial_verdict(table) == "FALSIFIED"  # noqa: SLF001

    def test_partially_valid_when_same_candidate_survives_and_dominates(
        self,
    ) -> None:
        table = [
            _make_comparison_row(
                candidate_id="A", primary_margin=0.6, win_rate=0.7
            ),
            _make_comparison_row(
                candidate_id="B", primary_margin=-1.0, win_rate=0.2
            ),
        ]
        assert adv._adversarial_verdict(table) == "PARTIALLY_VALID"  # noqa: SLF001

    def test_inconclusive_when_only_primary_survives_but_no_dominance(
        self,
    ) -> None:
        table = [
            _make_comparison_row(
                candidate_id="A", primary_margin=0.5, win_rate=0.3
            ),
        ]
        assert adv._adversarial_verdict(table) == "INCONCLUSIVE"  # noqa: SLF001

    def test_inconclusive_when_only_dominance_but_no_primary_survival(
        self,
    ) -> None:
        table = [
            _make_comparison_row(
                candidate_id="A", primary_margin=0.1, win_rate=0.8
            ),
        ]
        assert adv._adversarial_verdict(table) == "INCONCLUSIVE"  # noqa: SLF001

    def test_inconclusive_when_different_candidates_split_criteria(
        self,
    ) -> None:
        table = [
            _make_comparison_row(
                candidate_id="A", primary_margin=0.6, win_rate=0.2
            ),
            _make_comparison_row(
                candidate_id="B", primary_margin=0.1, win_rate=0.8
            ),
        ]
        assert adv._adversarial_verdict(table) == "INCONCLUSIVE"  # noqa: SLF001


# ---------------------------------------------------------------------------
# Committed artifacts (regression guards)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not (AGENT_RUN_DIR / "metrics.json").exists(),
    reason="AGENT-RUN-0031 artifacts not committed yet",
)
class TestCommittedAgentRunArtifacts:
    def test_metrics_json_has_expected_top_level_keys(self) -> None:
        metrics = json.loads((AGENT_RUN_DIR / "metrics.json").read_text(encoding="utf-8"))
        for key in (
            "agent_run_id",
            "task_id",
            "summary",
            "baseline_metrics_by_subset",
            "variants",
            "candidate_vs_strongest_control",
        ):
            assert key in metrics, key
        assert metrics["agent_run_id"] == "AGENT-RUN-0031"
        assert metrics["task_id"] == "TASK-0351"
        assert metrics["sandbox_only"] is True
        assert metrics["live_external_fetch_allowed"] is False

    def test_summary_records_three_new_controls(self) -> None:
        metrics = json.loads((AGENT_RUN_DIR / "metrics.json").read_text(encoding="utf-8"))
        assert metrics["summary"]["new_adversarial_control_count"] == 3
        assert (
            metrics["summary"]["primary_survival_margin_mev"]
            == adv.PRIMARY_SURVIVAL_MARGIN_MEV
        )

    def test_no_canonical_promotion_flags(self) -> None:
        metrics = json.loads((AGENT_RUN_DIR / "metrics.json").read_text(encoding="utf-8"))
        summary = metrics["summary"]
        assert summary["canonical_results_changed"] is False
        assert summary["canonical_claims_changed"] is False
        assert summary["prediction_registry_changed"] is False
        assert summary["claim_promotion_allowed"] is False

    def test_each_executed_candidate_has_strongest_control_entry(self) -> None:
        metrics = json.loads((AGENT_RUN_DIR / "metrics.json").read_text(encoding="utf-8"))
        comparison_rows = metrics["candidate_vs_strongest_control"]
        candidate_ids = [
            item["candidate_id"]
            for item in metrics["variants"]
            if item["role"] == "executed_candidate"
        ]
        comparison_ids = [row["candidate_id"] for row in comparison_rows]
        assert sorted(comparison_ids) == sorted(candidate_ids)
        for row in comparison_rows:
            assert "primary_survives_adversarial_controls" in row
            assert "subset_win_rate" in row
