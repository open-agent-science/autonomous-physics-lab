"""Reproducibility test for AGENT-RUN-0009 shell-aware nuclear sandbox batch."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
METRICS_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0009" / "metrics.json"
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_shell_batch.py"


def _load_batch_module():
    spec = importlib.util.spec_from_file_location("run_nuclear_shell_batch", SCRIPT_PATH)
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


def test_shell_batch_metrics_recompute() -> None:
    module = _load_batch_module()
    recomputed = module.build_metrics()
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert recomputed["agent_run_id"] == "AGENT-RUN-0009"
    assert recomputed["task_id"] == "TASK-0200"
    assert recomputed["sandbox_only"] is True
    assert recomputed["verdict"] == "SANDBOX_PASS"

    assert recomputed["summary"]["generated_proposal_count"] == 5
    assert recomputed["summary"]["executed_candidate_count"] == 2
    assert recomputed["summary"]["rejected_before_execution_count"] == 3
    assert recomputed["summary"]["canonical_results_changed"] is False
    assert recomputed["summary"]["canonical_claims_changed"] is False
    assert recomputed["summary"]["claim_promotion_allowed"] is False

    assert recomputed["summary"] == committed["summary"]
    assert recomputed["frozen_baseline"] == committed["frozen_baseline"]
    committed_holdouts = committed["structured_holdouts"]["definition"]
    recomputed_holdouts = recomputed["structured_holdouts"]["definition"]
    normalized = {
        key: list(value) for key, value in module.HOLDOUTS.items()
    }
    assert {k: list(v) for k, v in recomputed_holdouts.items()} == normalized
    assert committed_holdouts == normalized

    assert recomputed["post_ame2020_baseline"]["primary_holdout_row_count"] == 295
    assert _approx_equal(
        recomputed["post_ame2020_baseline"]["primary_metrics"]["mae_mev"],
        4.552568580201034,
    )

    executed_ids = [item["proposal_id"] for item in recomputed["executed_items"]]
    assert executed_ids == ["HYP-PROPOSAL-0028", "HYP-PROPOSAL-0029"]

    rejected_ids = [item["proposal_id"] for item in recomputed["rejected_before_execution"]]
    assert rejected_ids == ["HYP-PROPOSAL-0030", "HYP-PROPOSAL-0031", "HYP-PROPOSAL-0032"]


@pytest.mark.parametrize(
    "candidate_index, expected_proposal_id, expected_feature_activation",
    [
        (0, "HYP-PROPOSAL-0028", {"s_z_gauss": 295, "s_n_gauss": 295}),
        (1, "HYP-PROPOSAL-0029", {"s_n_gauss": 295}),
    ],
)
def test_executed_candidate_activation_counts(
    candidate_index: int,
    expected_proposal_id: str,
    expected_feature_activation: dict[str, int],
) -> None:
    module = _load_batch_module()
    metrics = module.build_metrics()
    item = metrics["executed_items"][candidate_index]
    assert item["proposal_id"] == expected_proposal_id
    assert item["post_ame2020_eval"]["feature_activation_counts"] == expected_feature_activation


def test_executed_candidate_structured_verdicts_overfitted() -> None:
    module = _load_batch_module()
    metrics = module.build_metrics()
    for item in metrics["executed_items"]:
        assert item["observed_verdict"] == "OVERFITTED"
        assert item["expected_verdict"] == "OVERFITTED"
        assert item["agrees"] is True


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
