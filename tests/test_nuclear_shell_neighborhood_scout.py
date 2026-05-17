"""Reproducibility tests for AGENT-RUN-0012 shell-neighborhood scout."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_shell_neighborhood_scout.py"
METRICS_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0012" / "metrics.json"


def _load_scout_module():
    spec = importlib.util.spec_from_file_location("run_nuclear_shell_neighborhood_scout", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _assert_nested_close(actual, expected, *, abs_tol: float = 1.0e-12) -> None:
    if isinstance(expected, dict):
        assert isinstance(actual, dict)
        assert set(actual) == set(expected)
        for key in expected:
            _assert_nested_close(actual[key], expected[key], abs_tol=abs_tol)
        return

    if isinstance(expected, list):
        assert isinstance(actual, list)
        assert len(actual) == len(expected)
        for actual_item, expected_item in zip(actual, expected, strict=True):
            _assert_nested_close(actual_item, expected_item, abs_tol=abs_tol)
        return

    if isinstance(expected, float):
        assert actual == pytest.approx(expected, abs=abs_tol, rel=0.0)
        return

    assert actual == expected


def test_shell_neighborhood_scout_metrics_recompute() -> None:
    module = _load_scout_module()
    recomputed = module.build_metrics()
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert recomputed["agent_run_id"] == "AGENT-RUN-0012"
    assert recomputed["task_id"] == "TASK-0278"
    assert recomputed["sandbox_only"] is True
    assert recomputed["summary"] == committed["summary"]
    assert recomputed["frozen_baseline"] == committed["frozen_baseline"]
    _assert_nested_close(
        recomputed["baseline_metrics_by_subset"],
        committed["baseline_metrics_by_subset"],
    )


def test_shell_neighborhood_scout_candidate_triage_and_verdicts() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    assert metrics["summary"]["generated_candidate_count"] == 9
    assert metrics["summary"]["executed_candidate_count"] == 6
    assert metrics["summary"]["rejected_before_execution_count"] == 3
    assert metrics["summary"]["near_null_control_preserved"] is True
    assert metrics["summary"]["verdict_counts"] == {
        "INCONCLUSIVE": 1,
        "OVERFITTED": 2,
        "PARTIALLY_VALID": 3,
    }


def test_shell_neighborhood_scout_preserves_negative_and_null_controls() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()
    executed = {item["candidate_id"]: item for item in metrics["executed_items"]}

    assert executed["SHELL-SCOUT-001"]["verdict"] == "OVERFITTED"
    assert executed["SHELL-SCOUT-004"]["verdict"] == "OVERFITTED"
    assert executed["SHELL-SCOUT-006"]["verdict"] == "INCONCLUSIVE"
    assert executed["SHELL-SCOUT-006"]["delta_mae_by_subset_mev"]["primary"] == 0.0
    assert executed["SHELL-SCOUT-006"]["delta_mae_by_subset_mev"]["magic_any"] == 0.0


def test_shell_neighborhood_scout_promotion_boundary() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert metrics["summary"]["canonical_results_changed"] is False
    assert metrics["summary"]["canonical_claims_changed"] is False
    assert metrics["summary"]["prediction_registry_changed"] is False
    assert metrics["promotion_boundary"]["writes_prediction_registry"] is False
    assert metrics["promotion_boundary"]["claim_promotion_allowed"] is False
