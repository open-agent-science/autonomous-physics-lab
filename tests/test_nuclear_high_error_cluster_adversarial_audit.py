"""Tests for the TASK-0367 adversarial-stability audit runner.

The runner re-evaluates the AGENT-RUN-0030 high-error cluster candidates
with three new adversarial controls and two stability diagnostics
(threshold perturbation and leave-one-out). These tests verify the
variant composition, the new control feature shapes, the verdict logic,
and the committed sandbox artifacts.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    REPO_ROOT / "scripts" / "run_nuclear_high_error_cluster_adversarial_audit.py"
)
AGENT_RUN_DIR = REPO_ROOT / "agent_runs" / "AGENT-RUN-0033"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "run_nuclear_high_error_cluster_adversarial_audit", SCRIPT_PATH
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
        for candidate_id in adv.EXECUTED_CANDIDATE_IDS:
            assert candidate_id in ids, candidate_id

    def test_includes_three_existing_controls(self) -> None:
        variants = adv._build_adversarial_variants()  # noqa: SLF001
        ids = {item["candidate_id"] for item in variants}
        for control_id in adv.EXISTING_CONTROL_IDS:
            assert control_id in ids, control_id

    def test_includes_three_new_adversarial_controls(self) -> None:
        variants = adv._build_adversarial_variants()  # noqa: SLF001
        ids = {item["candidate_id"] for item in variants}
        for control_id in adv.NEW_ADVERSARIAL_CONTROL_IDS:
            assert control_id in ids, control_id

    def test_every_variant_has_lstsq_fit_mode(self) -> None:
        for item in adv._build_adversarial_variants():  # noqa: SLF001
            assert item["fit_mode"] == "lstsq", item["candidate_id"]

    def test_new_control_roles_are_explicit(self) -> None:
        variants = {
            item["candidate_id"]: item
            for item in adv._build_adversarial_variants()  # noqa: SLF001
        }
        assert (
            variants["HIGHCLUSTER-ADV-001"]["role"]
            == "random_permutation_cluster_label_control"
        )
        assert (
            variants["HIGHCLUSTER-ADV-002"]["role"] == "pure_local_density_control"
        )
        assert (
            variants["HIGHCLUSTER-ADV-003"]["role"] == "near_null_jitter_control"
        )


# ---------------------------------------------------------------------------
# New adversarial control feature functions
# ---------------------------------------------------------------------------


def _toy_audit_rows() -> list[dict]:
    """Six-row audit surface across two Z chains with varied residuals."""

    rows: list[dict] = []
    for idx, (z, n, residual, extrapolated) in enumerate(
        [
            (10, 10, -1.0, False),
            (10, 12, 7.0, False),
            (10, 14, 0.5, True),
            (20, 22, -0.5, False),
            (20, 24, 8.0, False),
            (20, 26, 0.25, True),
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
                "was_extrapolated": extrapolated,
                "baseline_residual_mev": residual,
                "observed_mev": 0.0,
                "baseline_predicted_mev": -residual,
            }
        )
    return rows


class TestNewAdversarialControls:
    @pytest.fixture
    def index(self) -> lane.ClusterIndex:
        rows = _toy_audit_rows()
        threshold = 5.0
        # Reset module-level deterministic caches so the toy surface does not
        # share state with any previously evaluated ClusterIndex.
        adv._PERMUTED_CACHE.clear()  # noqa: SLF001
        adv._NOISE_CACHE.clear()  # noqa: SLF001
        return lane.ClusterIndex(rows, threshold)

    def test_random_permuted_label_returns_one_value(
        self, index: lane.ClusterIndex
    ) -> None:
        for row in index.rows:
            values = adv._random_permuted_cluster_label(row, index)  # noqa: SLF001
            assert len(values) == 1
            assert values[0] in {0.0, 1.0}

    def test_random_permuted_label_is_deterministic(
        self, index: lane.ClusterIndex
    ) -> None:
        first = [
            adv._random_permuted_cluster_label(row, index)  # noqa: SLF001
            for row in index.rows
        ]
        second = [
            adv._random_permuted_cluster_label(row, index)  # noqa: SLF001
            for row in index.rows
        ]
        assert first == second

    def test_pure_local_density_uses_index_density(
        self, index: lane.ClusterIndex
    ) -> None:
        for row in index.rows:
            values = adv._pure_local_density(row, index)  # noqa: SLF001
            assert len(values) == 1
            assert values[0] == pytest.approx(float(index.local_density(row)))

    def test_near_null_jitter_is_small_and_deterministic(
        self, index: lane.ClusterIndex
    ) -> None:
        first = [adv._near_null_jitter(row, index) for row in index.rows]  # noqa: SLF001
        second = [adv._near_null_jitter(row, index) for row in index.rows]  # noqa: SLF001
        assert first == second
        for values in first:
            assert len(values) == 1
            # 1e-3 std should keep individual draws well below ~1e-2.
            assert abs(values[0]) < 1.0e-2


# ---------------------------------------------------------------------------
# Per-candidate adversarial verdict logic
# ---------------------------------------------------------------------------


def _make_candidate_item(
    *,
    high_error: float | None,
    non_high_error: float | None,
) -> dict:
    return {
        "candidate_id": "TEST-001",
        "high_error_delta_mae_mev": high_error,
        "non_high_error_delta_mae_mev": non_high_error,
    }


def _make_comparison_row(
    *,
    primary_margin: float | None,
    win_rate: float | None,
) -> dict:
    survives = primary_margin is not None and primary_margin >= adv.PRIMARY_SURVIVAL_MARGIN_MEV
    return {
        "primary_survives_adversarial_controls": survives,
        "subset_win_rate": win_rate,
    }


class TestCandidateAdversarialVerdict:
    def test_partially_valid_requires_all_gates(self) -> None:
        candidate = _make_candidate_item(high_error=-2.0, non_high_error=0.0)
        comparison = _make_comparison_row(primary_margin=0.6, win_rate=0.8)
        threshold = {
            "improves_at_every_percentile": True,
            "coefficient_sign_flip": False,
        }
        loo = {"loo_stable": True}
        result = adv._candidate_adversarial_verdict(  # noqa: SLF001
            candidate_item=candidate,
            comparison_row=comparison,
            threshold_summary=threshold,
            loo_summary=loo,
        )
        assert result["verdict"] == "PARTIALLY_VALID"

    def test_overfit_when_only_high_error_improves(self) -> None:
        candidate = _make_candidate_item(high_error=-2.0, non_high_error=0.5)
        comparison = _make_comparison_row(primary_margin=0.6, win_rate=0.8)
        threshold = {
            "improves_at_every_percentile": True,
            "coefficient_sign_flip": False,
        }
        loo = {"loo_stable": True}
        result = adv._candidate_adversarial_verdict(  # noqa: SLF001
            candidate_item=candidate,
            comparison_row=comparison,
            threshold_summary=threshold,
            loo_summary=loo,
        )
        assert result["verdict"] == "OVERFITTED"
        assert result["high_error_only_overfit"] is True

    def test_inconclusive_when_loo_unstable_but_primary_survives(self) -> None:
        candidate = _make_candidate_item(high_error=-2.0, non_high_error=0.0)
        comparison = _make_comparison_row(primary_margin=0.6, win_rate=0.8)
        threshold = {
            "improves_at_every_percentile": True,
            "coefficient_sign_flip": False,
        }
        loo = {"loo_stable": False}
        result = adv._candidate_adversarial_verdict(  # noqa: SLF001
            candidate_item=candidate,
            comparison_row=comparison,
            threshold_summary=threshold,
            loo_summary=loo,
        )
        assert result["verdict"] == "INCONCLUSIVE"

    def test_falsified_when_no_gate_passes(self) -> None:
        candidate = _make_candidate_item(high_error=0.1, non_high_error=0.1)
        comparison = _make_comparison_row(primary_margin=-0.5, win_rate=0.1)
        threshold = {
            "improves_at_every_percentile": False,
            "coefficient_sign_flip": True,
        }
        loo = {"loo_stable": False}
        result = adv._candidate_adversarial_verdict(  # noqa: SLF001
            candidate_item=candidate,
            comparison_row=comparison,
            threshold_summary=threshold,
            loo_summary=loo,
        )
        assert result["verdict"] == "FALSIFIED"


# ---------------------------------------------------------------------------
# Lane verdict aggregation
# ---------------------------------------------------------------------------


class TestLaneVerdict:
    def test_partially_valid_if_any_candidate_passes(self) -> None:
        verdicts = {
            "A": {"verdict": "PARTIALLY_VALID"},
            "B": {"verdict": "INCONCLUSIVE"},
            "C": {"verdict": "FALSIFIED"},
        }
        assert adv._lane_verdict(verdicts) == "PARTIALLY_VALID"  # noqa: SLF001

    def test_overfitted_when_all_overfit_or_falsified(self) -> None:
        verdicts = {
            "A": {"verdict": "OVERFITTED"},
            "B": {"verdict": "FALSIFIED"},
        }
        assert adv._lane_verdict(verdicts) == "OVERFITTED"  # noqa: SLF001

    def test_inconclusive_when_any_candidate_inconclusive(self) -> None:
        verdicts = {
            "A": {"verdict": "INCONCLUSIVE"},
            "B": {"verdict": "FALSIFIED"},
        }
        assert adv._lane_verdict(verdicts) == "INCONCLUSIVE"  # noqa: SLF001

    def test_falsified_when_all_falsified(self) -> None:
        verdicts = {
            "A": {"verdict": "FALSIFIED"},
            "B": {"verdict": "FALSIFIED"},
        }
        assert adv._lane_verdict(verdicts) == "FALSIFIED"  # noqa: SLF001

    def test_inconclusive_when_no_candidate_verdicts(self) -> None:
        assert adv._lane_verdict({}) == "INCONCLUSIVE"  # noqa: SLF001


# ---------------------------------------------------------------------------
# Verdict mapping to agent_run schema enum
# ---------------------------------------------------------------------------


class TestAgentRunVerdictMapping:
    @pytest.mark.parametrize(
        "lane_verdict, expected",
        [
            ("PARTIALLY_VALID", "SANDBOX_PASS"),
            ("INCONCLUSIVE", "INCONCLUSIVE"),
            ("OVERFITTED", "OVERFITTED"),
            ("FALSIFIED", "FALSIFIED"),
            ("UNKNOWN", "INCONCLUSIVE"),
        ],
    )
    def test_mapping(self, lane_verdict: str, expected: str) -> None:
        assert (
            adv._map_lane_verdict_to_agent_run_verdict(lane_verdict)  # noqa: SLF001
            == expected
        )


# ---------------------------------------------------------------------------
# Committed artifact regression guards
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not (AGENT_RUN_DIR / "metrics.json").exists(),
    reason="AGENT-RUN-0033 artifacts not committed yet",
)
class TestCommittedAgentRunArtifacts:
    def test_metrics_top_level_keys(self) -> None:
        metrics = json.loads(
            (AGENT_RUN_DIR / "metrics.json").read_text(encoding="utf-8")
        )
        for key in (
            "agent_run_id",
            "task_id",
            "summary",
            "baseline_metrics_by_subset",
            "variants",
            "candidate_vs_strongest_control",
            "threshold_perturbation",
            "leave_one_out_stability",
            "per_candidate_adversarial_verdict",
        ):
            assert key in metrics, key
        assert metrics["agent_run_id"] == "AGENT-RUN-0033"
        assert metrics["task_id"] == "TASK-0367"
        assert metrics["sandbox_only"] is True
        assert metrics["live_external_fetch_allowed"] is False

    def test_summary_records_three_new_controls(self) -> None:
        metrics = json.loads(
            (AGENT_RUN_DIR / "metrics.json").read_text(encoding="utf-8")
        )
        assert metrics["summary"]["new_adversarial_control_count"] == 3
        assert (
            metrics["summary"]["primary_survival_margin_mev"]
            == adv.PRIMARY_SURVIVAL_MARGIN_MEV
        )

    def test_no_canonical_promotion_flags(self) -> None:
        metrics = json.loads(
            (AGENT_RUN_DIR / "metrics.json").read_text(encoding="utf-8")
        )
        summary = metrics["summary"]
        assert summary["canonical_results_changed"] is False
        assert summary["canonical_claims_changed"] is False
        assert summary["prediction_registry_changed"] is False
        assert summary["claim_promotion_allowed"] is False

    def test_each_executed_candidate_has_full_diagnostic_coverage(self) -> None:
        metrics = json.loads(
            (AGENT_RUN_DIR / "metrics.json").read_text(encoding="utf-8")
        )
        comparison_ids = {
            row["candidate_id"] for row in metrics["candidate_vs_strongest_control"]
        }
        threshold_ids = set(
            metrics["threshold_perturbation"]["per_candidate_summary"].keys()
        )
        loo_ids = set(metrics["leave_one_out_stability"]["per_candidate"].keys())
        verdict_ids = set(metrics["per_candidate_adversarial_verdict"].keys())
        candidate_ids = set(adv.EXECUTED_CANDIDATE_IDS)
        assert comparison_ids == candidate_ids
        assert threshold_ids == candidate_ids
        assert loo_ids == candidate_ids
        assert verdict_ids == candidate_ids

    def test_threshold_perturbation_evaluates_each_percentile(self) -> None:
        metrics = json.loads(
            (AGENT_RUN_DIR / "metrics.json").read_text(encoding="utf-8")
        )
        rows = metrics["threshold_perturbation"]["rows_by_threshold"]
        percentiles = [row["percentile"] for row in rows]
        assert percentiles == list(adv.THRESHOLD_PERTURBATION_PERCENTILES)
