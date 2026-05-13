"""Reproducibility test for AGENT-RUN-0011 pairing nuclear sandbox batch."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
METRICS_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0011" / "metrics.json"
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_pairing_batch.py"


def _load_batch_module():
    spec = importlib.util.spec_from_file_location("run_nuclear_pairing_batch", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _approx_equal(a: float | None, b: float | None, *, tol: float = 1.0e-9) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return abs(float(a) - float(b)) <= tol


def test_pairing_batch_metrics_recompute() -> None:
    module = _load_batch_module()
    recomputed = module.build_metrics()
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert recomputed["agent_run_id"] == "AGENT-RUN-0011"
    assert recomputed["task_id"] == "TASK-0201"
    assert recomputed["sandbox_only"] is True
    assert recomputed["verdict"] == "SANDBOX_PASS"
    assert recomputed["lane"] == "pairing"

    assert recomputed["summary"]["generated_proposal_count"] == 5
    assert recomputed["summary"]["executed_candidate_count"] == 2
    assert recomputed["summary"]["rejected_before_execution_count"] == 3
    assert recomputed["summary"]["canonical_results_changed"] is False
    assert recomputed["summary"]["canonical_claims_changed"] is False
    assert recomputed["summary"]["claim_promotion_allowed"] is False
    assert recomputed["summary"]["in_batch_negative_control_overfitted_count"] == 1

    assert recomputed["summary"] == committed["summary"]
    assert recomputed["frozen_baseline"] == committed["frozen_baseline"]

    assert recomputed["post_ame2020_baseline"]["primary_holdout_row_count"] == 295
    assert _approx_equal(
        recomputed["post_ame2020_baseline"]["primary_metrics"]["mae_mev"],
        4.552568580201034,
    )

    executed_ids = [item["proposal_id"] for item in recomputed["executed_items"]]
    assert executed_ids == ["HYP-PROPOSAL-0038", "HYP-PROPOSAL-0041"]

    rejected_ids = [item["proposal_id"] for item in recomputed["rejected_before_execution"]]
    assert rejected_ids == ["HYP-PROPOSAL-0039", "HYP-PROPOSAL-0040", "HYP-PROPOSAL-0042"]


def test_pairing_a_inverse_post_ame2020_primary_is_near_null() -> None:
    module = _load_batch_module()
    metrics = module.build_metrics()
    a_inverse = metrics["executed_items"][0]
    assert a_inverse["proposal_id"] == "HYP-PROPOSAL-0038"
    activation = a_inverse["post_ame2020_eval"]["feature_activation_counts"]
    assert activation == {"pairing_a_inverse": 139}
    primary_delta = abs(
        float(a_inverse["post_ame2020_eval"]["primary_delta_mae_mev"])
    )
    assert primary_delta < 0.05, (
        "pairing A-inverse refinement is sign-colinear with the baseline "
        "pairing term and should produce a near-null post-AME2020 primary "
        f"effect; primary delta MAE = {primary_delta}"
    )
    assert a_inverse["observed_verdict"] == "OVERFITTED"


def test_in_batch_negative_control_overfitted() -> None:
    module = _load_batch_module()
    metrics = module.build_metrics()
    negative_control = metrics["executed_items"][1]
    assert negative_control["proposal_id"] == "HYP-PROPOSAL-0041"
    activation = negative_control["post_ame2020_eval"]["feature_activation_counts"]
    assert activation == {"ee_indicator": 68, "oo_indicator": 71, "odd_a_indicator": 156}
    assert sum(activation.values()) == 295, (
        "per-parity-class indicators must partition the 295-row primary holdout"
    )
    assert negative_control["observed_verdict"] == "OVERFITTED"
    primary_delta = float(
        negative_control["post_ame2020_eval"]["primary_delta_mae_mev"]
    )
    assert primary_delta > 0.1, (
        "in-batch negative control should regress primary MAE on post-AME2020; "
        f"got primary delta MAE = {primary_delta}"
    )


def test_executed_candidate_structured_verdicts_overfitted() -> None:
    module = _load_batch_module()
    metrics = module.build_metrics()
    for item in metrics["executed_items"]:
        assert item["observed_verdict"] == "OVERFITTED"
        assert item["expected_verdict"] == "OVERFITTED"
        assert item["agrees"] is True


def test_negative_control_reference_present() -> None:
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    ref = committed["negative_control_reference"]
    assert ref["candidate_id"] == "HYP-PROPOSAL-0022"
    assert ref["family"] == "quadratic_asymmetry_refinement"
    assert ref["source_metrics_path"] == "agent_runs/AGENT-RUN-0008/metrics.json"
    assert ref["post_ame2020_primary_delta_mae_mev"] < 0.0


def test_in_batch_negative_control_record_present() -> None:
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    record = committed["in_batch_negative_control"]
    assert record["candidate_id"] == "HYP-PROPOSAL-0041"
    assert record["family"] == "parity_class_offsets"
    assert record["rationale"].strip()


def test_promotion_boundary_preserved() -> None:
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    assert committed["promotion_boundary"]["writes_canonical_result"] is False
    assert committed["promotion_boundary"]["claim_promotion_allowed"] is False
    assert committed["summary"]["canonical_results_changed"] is False
    assert committed["summary"]["canonical_claims_changed"] is False


def test_rejected_proposal_reasons_are_documented() -> None:
    module = _load_batch_module()
    metrics = module.build_metrics()
    for rejection in metrics["rejected_before_execution"]:
        assert rejection["rejection_reason"].strip(), (
            f"rejection {rejection['proposal_id']} must include a reason"
        )
