"""Reproducibility tests for AGENT-RUN-0024 neutron-rich tail audit."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_shell_axis_neutron_rich_tail_audit.py"
METRICS_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0024" / "metrics.json"
AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0024" / "agent_run.yaml"


def _load_neutron_rich_tail_module():
    spec = importlib.util.spec_from_file_location(
        "run_nuclear_shell_axis_neutron_rich_tail_audit", SCRIPT_PATH
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


def test_neutron_rich_tail_runner_imports_cleanly() -> None:
    module = _load_neutron_rich_tail_module()

    assert module.AGENT_RUN_ID == "AGENT-RUN-0024"
    assert module.TASK_ID == "TASK-0324"
    assert hasattr(module, "build_metrics")
    assert hasattr(module, "render_report")


def test_neutron_rich_tail_metrics_recompute() -> None:
    module = _load_neutron_rich_tail_module()
    recomputed = module.build_metrics()
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert recomputed["agent_run_id"] == "AGENT-RUN-0024"
    assert recomputed["task_id"] == "TASK-0324"
    assert recomputed["sandbox_only"] is True
    assert recomputed["summary"] == committed["summary"]
    assert recomputed["datasets"] == committed["datasets"]
    assert recomputed["subset_rules"] == committed["subset_rules"]
    _assert_nested_close(recomputed["subset_composition"], committed["subset_composition"])
    _assert_nested_close(recomputed["candidate_summaries"], committed["candidate_summaries"])


def test_neutron_rich_tail_verdict_and_outlier_sensitivity() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert metrics["summary"]["neutron_rich_row_count"] == 31
    assert metrics["summary"]["neutron_rich_high_error_tail_row_count"] == 20
    assert metrics["summary"]["matched_non_neutron_rich_high_error_row_count"] == 20
    assert metrics["summary"]["domain_recommendation"] == "OUTLIER_DIAGNOSTIC"

    for item in metrics["candidate_summaries"]:
        assert item["neutron_rich_high_error_tail"]["delta_mae_mev"] < 0.0
        assert item["neutron_rich_high_error_tail"]["delta_rmse_mev"] < 0.0
        assert item["tail_outlier_sensitivity"]["drop_largest_1_baseline_error"][
            "summary"
        ]["delta_mae_mev"] < 0.0
        assert item["tail_outlier_sensitivity"]["drop_largest_2_baseline_errors"][
            "summary"
        ]["delta_mae_mev"] < 0.0
        assert item["top_tail_delta_contributors"]


def test_neutron_rich_tail_matched_control_limits_claim_scope() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    by_id = {item["candidate_id"]: item for item in metrics["candidate_summaries"]}
    assert set(by_id) == {
        "FULLKNOWN-SHELL-001",
        "FULLKNOWN-SHELL-002",
        "FULLKNOWN-SHELL-003",
    }
    assert by_id["FULLKNOWN-SHELL-001"]["matched_non_neutron_rich_high_error"][
        "delta_mae_mev"
    ] < 0.0
    assert by_id["FULLKNOWN-SHELL-002"]["matched_non_neutron_rich_high_error"][
        "delta_mae_mev"
    ] < by_id["FULLKNOWN-SHELL-002"]["neutron_rich_high_error_tail"][
        "delta_mae_mev"
    ]
    assert by_id["FULLKNOWN-SHELL-003"]["matched_non_neutron_rich_high_error"][
        "delta_mae_mev"
    ] < by_id["FULLKNOWN-SHELL-003"]["neutron_rich_high_error_tail"][
        "delta_mae_mev"
    ]


def test_neutron_rich_tail_manifest_and_no_registry_writes(tmp_path: Path) -> None:
    module = _load_neutron_rich_tail_module()
    manifest = yaml.safe_load(AGENT_RUN_PATH.read_text(encoding="utf-8"))
    out_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"

    assert manifest["id"] == "AGENT-RUN-0024"
    assert manifest["task_id"] == "TASK-0324"
    assert manifest["sandbox_only"] is True
    assert manifest["verdict"] == "INCONCLUSIVE"
    assert manifest["promotion_boundary"]["writes_canonical_result"] is False
    assert manifest["promotion_boundary"]["claim_promotion_allowed"] is False

    registry_dir = REPO_ROOT / "prediction_registry" / "nuclear_masses"
    before = sorted(path.name for path in registry_dir.iterdir())
    module.main(["--out", str(out_path), "--report", str(report_path)])
    after = sorted(path.name for path in registry_dir.iterdir())

    assert out_path.exists()
    assert report_path.exists()
    assert before == after
