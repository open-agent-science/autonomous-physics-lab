"""Reproducibility tests for AGENT-RUN-0023 chain-transfer audit."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_shell_axis_chain_transfer_audit.py"
METRICS_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0023" / "metrics.json"
AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0023" / "agent_run.yaml"


def _load_chain_transfer_module():
    spec = importlib.util.spec_from_file_location(
        "run_nuclear_shell_axis_chain_transfer_audit", SCRIPT_PATH
    )
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
        for actual_item, expected_item in zip(actual, expected):
            _assert_nested_close(actual_item, expected_item, abs_tol=abs_tol)
        return
    if isinstance(expected, float):
        assert actual == pytest.approx(expected, abs=abs_tol, rel=0.0)
        return
    assert actual == expected


def test_chain_transfer_runner_imports_cleanly() -> None:
    module = _load_chain_transfer_module()

    assert module.AGENT_RUN_ID == "AGENT-RUN-0023"
    assert module.TASK_ID == "TASK-0323"
    assert hasattr(module, "build_metrics")
    assert hasattr(module, "render_report")


def test_chain_transfer_metrics_recompute() -> None:
    module = _load_chain_transfer_module()
    recomputed = module.build_metrics()
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert recomputed["agent_run_id"] == "AGENT-RUN-0023"
    assert recomputed["task_id"] == "TASK-0323"
    assert recomputed["sandbox_only"] is True
    assert recomputed["summary"] == committed["summary"]
    assert recomputed["datasets"] == committed["datasets"]
    _assert_nested_close(
        recomputed["candidate_transfer_summary"],
        committed["candidate_transfer_summary"],
    )
    _assert_nested_close(recomputed["chain_items"], committed["chain_items"])


def test_chain_transfer_preserves_mixed_chain_local_verdict() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert metrics["summary"]["chain_count"] == 74
    assert metrics["summary"]["transfer_verdict"] == "MIXED_CHAIN_LOCAL"
    assert metrics["transfer_summary"]["interpretable_chain_count"] == 48
    assert metrics["transfer_summary"]["too_sparse_chain_count"] == 26
    assert metrics["transfer_summary"]["best_shell_improved_chain_count"] == 21
    assert metrics["transfer_summary"]["best_shell_regressed_chain_count"] == 20


def test_chain_transfer_candidate_summaries_keep_regressions_visible() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    summary = metrics["candidate_transfer_summary"]

    assert set(summary) == {
        "FULLKNOWN-SHELL-001",
        "FULLKNOWN-SHELL-002",
        "FULLKNOWN-SHELL-003",
    }
    for candidate_id, item in summary.items():
        assert item["interpretable_chain_count"] == 48
        assert item["improved_chain_count"] > 0
        assert item["regressed_chain_count"] > 0
        assert item["worst_chain_regressions"], candidate_id

    assert summary["FULLKNOWN-SHELL-001"]["improvement_rate"] == pytest.approx(
        19 / 48,
        abs=1.0e-12,
        rel=0.0,
    )


def test_chain_transfer_reports_best_non_shell_control_where_available() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    interpretable = [
        item for item in metrics["chain_items"] if item["diagnostic_class"] == "interpretable"
    ]
    assert interpretable
    for item in interpretable:
        assert item["best_non_shell_control_id"].startswith("SPECIFICITY-CONTROL-")
        assert item["best_non_shell_control_delta_mae_mev"] is not None


def test_chain_transfer_manifest_and_no_registry_writes(tmp_path: Path) -> None:
    module = _load_chain_transfer_module()
    manifest = yaml.safe_load(AGENT_RUN_PATH.read_text(encoding="utf-8"))
    out_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"

    assert manifest["id"] == "AGENT-RUN-0023"
    assert manifest["task_id"] == "TASK-0323"
    assert manifest["sandbox_only"] is True
    assert manifest["promotion_boundary"]["writes_canonical_result"] is False
    assert manifest["promotion_boundary"]["claim_promotion_allowed"] is False

    registry_dir = REPO_ROOT / "prediction_registry" / "nuclear_masses"
    before = sorted(path.name for path in registry_dir.iterdir())
    module.main(["--out", str(out_path), "--report", str(report_path)])
    after = sorted(path.name for path in registry_dir.iterdir())

    assert out_path.exists()
    assert report_path.exists()
    assert before == after
