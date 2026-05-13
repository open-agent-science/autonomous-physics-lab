"""Recomputation tests for AGENT-RUN-0011 (TASK-0201) nuclear pairing batch.

These tests verify that the deterministic sandbox metrics are stable
across re-runs. They import the build_metrics function from the batch
script and compare key fields against pre-computed expected values.
"""

from __future__ import annotations

import pytest

from scripts.run_nuclear_pairing_batch import build_metrics, feature_values


class TestFeatureValues:
    def test_eta_ee_even_even(self) -> None:
        vals = feature_values("differential_pairing_ee_oo", z=82, n=126, a=208)
        assert vals == (1.0, 0.0), "Pb-208 is even-even: eta_ee=1, eta_oo=0"

    def test_eta_oo_odd_odd(self) -> None:
        vals = feature_values("differential_pairing_ee_oo", z=7, n=7, a=14)
        assert vals == (0.0, 1.0), "N-14 is odd-odd: eta_ee=0, eta_oo=1"

    def test_eta_odd_a(self) -> None:
        vals = feature_values("differential_pairing_ee_oo", z=8, n=9, a=17)
        assert vals == (0.0, 0.0), "O-17 is odd-A: eta_ee=0, eta_oo=0"

    def test_wigner_n_eq_z(self) -> None:
        vals = feature_values("wigner_energy_n_eq_z", z=20, n=20, a=40)
        assert abs(vals[0] - 1.0 / 40.0) < 1e-12, "Ca-40: wigner = 1/40"

    def test_wigner_n_ne_z(self) -> None:
        vals = feature_values("wigner_energy_n_eq_z", z=92, n=146, a=238)
        assert vals == (0.0,), "U-238: N != Z, wigner = 0"

    def test_unknown_family_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown family"):
            feature_values("no_such_family", z=1, n=1, a=2)


class TestBatchMetrics:
    @pytest.fixture(scope="class")
    def metrics(self) -> dict:
        return build_metrics()

    def test_agent_run_id(self, metrics: dict) -> None:
        assert metrics["agent_run_id"] == "AGENT-RUN-0011"

    def test_task_id(self, metrics: dict) -> None:
        assert metrics["task_id"] == "TASK-0201"

    def test_lane(self, metrics: dict) -> None:
        assert metrics["lane"] == "pairing_odd_even"

    def test_sandbox_only(self, metrics: dict) -> None:
        assert metrics["sandbox_only"] is True

    def test_no_canonical_changes(self, metrics: dict) -> None:
        assert metrics["summary"]["canonical_results_changed"] is False
        assert metrics["summary"]["canonical_claims_changed"] is False
        assert metrics["summary"]["claim_promotion_allowed"] is False

    def test_generated_proposal_count(self, metrics: dict) -> None:
        assert metrics["summary"]["generated_proposal_count"] == 5

    def test_executed_candidate_count(self, metrics: dict) -> None:
        assert metrics["summary"]["executed_candidate_count"] == 2

    def test_rejected_count(self, metrics: dict) -> None:
        assert metrics["summary"]["rejected_before_execution_count"] == 3

    def test_no_improved_all_holdouts(self, metrics: dict) -> None:
        assert metrics["summary"]["improved_all_structured_holdouts_count"] == 0

    def test_no_improved_post_ame2020_primary(self, metrics: dict) -> None:
        assert metrics["summary"]["improved_post_ame2020_primary_count"] == 0

    def test_hyp_0038_is_overfitted(self, metrics: dict) -> None:
        item = next(
            i for i in metrics["executed_items"] if i["proposal_id"] == "HYP-PROPOSAL-0038"
        )
        assert item["observed_verdict"] == "OVERFITTED"

    def test_hyp_0038_worst_regression_above_threshold(self, metrics: dict) -> None:
        item = next(
            i for i in metrics["executed_items"] if i["proposal_id"] == "HYP-PROPOSAL-0038"
        )
        assert item["summary"]["worst_regression_mev"] >= 1.0

    def test_hyp_0039_verdict(self, metrics: dict) -> None:
        item = next(
            i for i in metrics["executed_items"] if i["proposal_id"] == "HYP-PROPOSAL-0039"
        )
        assert item["observed_verdict"] in {"INCONCLUSIVE", "PARTIALLY_VALID", "OVERFITTED"}

    def test_hyp_0039_wigner_low_activation(self, metrics: dict) -> None:
        item = next(
            i for i in metrics["executed_items"] if i["proposal_id"] == "HYP-PROPOSAL-0039"
        )
        activation = item["post_ame2020_eval"]["feature_activation_counts"]["wigner_n_eq_z"]
        assert activation <= 10, "Wigner N=Z feature should activate on very few neutron-rich rows"

    def test_hyp_0039_near_zero_post_ame2020_delta(self, metrics: dict) -> None:
        item = next(
            i for i in metrics["executed_items"] if i["proposal_id"] == "HYP-PROPOSAL-0039"
        )
        delta = item["post_ame2020_eval"]["primary_delta_mae_mev"]
        assert abs(delta) < 0.05, "Wigner term should have near-zero effect on neutron-rich holdout"

    def test_four_holdouts_per_candidate(self, metrics: dict) -> None:
        for item in metrics["executed_items"]:
            assert len(item["holdout_results"]) == 4

    def test_frozen_baseline_result_id(self, metrics: dict) -> None:
        assert metrics["frozen_baseline"]["result_id"] == "RESULT-0015"

    def test_promotion_boundary(self, metrics: dict) -> None:
        pb = metrics["promotion_boundary"]
        assert pb["writes_canonical_result"] is False
        assert pb["claim_promotion_allowed"] is False
