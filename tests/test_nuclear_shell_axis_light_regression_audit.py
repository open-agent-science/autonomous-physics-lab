"""Reproducibility tests for AGENT-RUN-0022 light-regression audit."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_shell_axis_light_regression_audit.py"
METRICS_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0022" / "metrics.json"
AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0022" / "agent_run.yaml"


def _load_light_regression_module():
    spec = importlib.util.spec_from_file_location(
        "run_nuclear_shell_axis_light_regression_audit", SCRIPT_PATH
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


def test_light_regression_runner_imports_cleanly() -> None:
    module = _load_light_regression_module()

    assert module.AGENT_RUN_ID == "AGENT-RUN-0022"
    assert module.TASK_ID == "TASK-0320"
    assert hasattr(module, "build_metrics")
    assert hasattr(module, "render_report")


def test_light_regression_metrics_recompute() -> None:
    module = _load_light_regression_module()
    recomputed = module.build_metrics()
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert recomputed["agent_run_id"] == "AGENT-RUN-0022"
    assert recomputed["task_id"] == "TASK-0320"
    assert recomputed["sandbox_only"] is True
    assert recomputed["summary"] == committed["summary"]
    assert recomputed["datasets"] == committed["datasets"]
    _assert_nested_close(recomputed["subset_composition"], committed["subset_composition"])
    _assert_nested_close(recomputed["candidate_summaries"], committed["candidate_summaries"])


def test_light_regression_preserves_warning_zone_verdict() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert metrics["summary"]["light_row_count"] == 24
    assert metrics["summary"]["matched_non_light_row_count"] == 24
    assert metrics["summary"]["all_primary_candidates_regress_light_a_lt_50"] is True
    assert metrics["summary"]["domain_recommendation"] == "WARNING_ZONE"


def test_light_regression_all_primary_candidates_regress_light_rows() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    by_id = {item["candidate_id"]: item for item in metrics["candidate_summaries"]}
    assert set(by_id) == {
        "FULLKNOWN-SHELL-001",
        "FULLKNOWN-SHELL-002",
        "FULLKNOWN-SHELL-003",
    }
    for item in by_id.values():
        assert item["light_a_lt_50"]["delta_mae_mev"] > 0.0
        assert item["light_a_lt_50"]["regression_row_count"] == 15
        assert item["light_a_lt_50"]["row_count"] == 24
        assert item["worst_light_row_regressions"]

    assert by_id["FULLKNOWN-SHELL-001"]["matched_non_light"]["delta_mae_mev"] < 0.0
    assert by_id["FULLKNOWN-SHELL-002"]["matched_non_light"]["delta_mae_mev"] < 0.0
    assert by_id["FULLKNOWN-SHELL-003"]["matched_non_light"]["delta_mae_mev"] > 0.0


def test_light_regression_manifest_and_no_registry_writes(tmp_path: Path) -> None:
    module = _load_light_regression_module()
    manifest = yaml.safe_load(AGENT_RUN_PATH.read_text(encoding="utf-8"))
    out_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"

    assert manifest["id"] == "AGENT-RUN-0022"
    assert manifest["task_id"] == "TASK-0320"
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
