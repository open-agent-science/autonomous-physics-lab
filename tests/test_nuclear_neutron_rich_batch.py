"""Reproducibility test for AGENT-RUN-0010 neutron-rich nuclear sandbox batch."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
METRICS_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0010" / "metrics.json"
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_neutron_rich_batch.py"


def _load_batch_module():
    spec = importlib.util.spec_from_file_location("run_nuclear_neutron_rich_batch", SCRIPT_PATH)
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


def test_neutron_rich_batch_metrics_recompute() -> None:
    module = _load_batch_module()
    recomputed = module.build_metrics()
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert recomputed["agent_run_id"] == "AGENT-RUN-0010"
    assert recomputed["task_id"] == "TASK-0202"
    assert recomputed["sandbox_only"] is True
    assert recomputed["verdict"] == "SANDBOX_PASS"
    assert recomputed["lane"] == "neutron_rich"

    assert recomputed["summary"]["generated_proposal_count"] == 5
    assert recomputed["summary"]["executed_candidate_count"] == 2
    assert recomputed["summary"]["rejected_before_execution_count"] == 3
    assert recomputed["summary"]["canonical_results_changed"] is False
    assert recomputed["summary"]["canonical_claims_changed"] is False
    assert recomputed["summary"]["claim_promotion_allowed"] is False

    assert recomputed["summary"] == committed["summary"]
    assert recomputed["frozen_baseline"] == committed["frozen_baseline"]

    assert recomputed["post_ame2020_baseline"]["primary_holdout_row_count"] == 295
    assert _approx_equal(
        recomputed["post_ame2020_baseline"]["primary_metrics"]["mae_mev"],
        4.552568580201034,
    )

    executed_ids = [item["proposal_id"] for item in recomputed["executed_items"]]
    assert executed_ids == ["HYP-PROPOSAL-0033", "HYP-PROPOSAL-0034"]

    rejected_ids = [item["proposal_id"] for item in recomputed["rejected_before_execution"]]
    assert rejected_ids == ["HYP-PROPOSAL-0035", "HYP-PROPOSAL-0036", "HYP-PROPOSAL-0037"]


def test_quartic_candidate_regresses_post_ame2020_primary() -> None:
    module = _load_batch_module()
    metrics = module.build_metrics()
    quartic = metrics["executed_items"][0]
    assert quartic["proposal_id"] == "HYP-PROPOSAL-0033"
    assert quartic["post_ame2020_eval"]["feature_activation_counts"] == {
        "i_sq": 292,
        "i_quartic": 292,
    }
    primary_delta = quartic["post_ame2020_eval"]["primary_delta_mae_mev"]
    assert primary_delta > 0.5, f"quartic candidate should regress primary; got {primary_delta}"
    assert quartic["observed_verdict"] == "OVERFITTED"


def test_asymmetric_feature_is_proton_rich_neutral() -> None:
    module = _load_batch_module()
    metrics = module.build_metrics()
    asymmetric = metrics["executed_items"][1]
    assert asymmetric["proposal_id"] == "HYP-PROPOSAL-0034"
    activation = asymmetric["post_ame2020_eval"]["feature_activation_counts"]
    assert activation == {"neutron_excess_sq_over_a": 264}
    primary_delta = abs(
        float(asymmetric["post_ame2020_eval"]["primary_delta_mae_mev"])
    )
    assert primary_delta < 1.0e-9, (
        "asymmetric (N-Z, capped at zero)^2/A on full NMD-0002 should fit a "
        f"near-zero coefficient; primary delta MAE = {primary_delta}"
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
