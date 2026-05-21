"""Reproducibility tests for AGENT-RUN-0021 magic-axis asymmetry audit."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_shell_axis_magic_asymmetry_audit.py"
METRICS_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0021" / "metrics.json"
AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0021" / "agent_run.yaml"


def _load_magic_axis_module():
    spec = importlib.util.spec_from_file_location(
        "run_nuclear_shell_axis_magic_asymmetry_audit", SCRIPT_PATH
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


def test_magic_axis_audit_runner_imports_cleanly() -> None:
    module = _load_magic_axis_module()
    assert module.AGENT_RUN_ID == "AGENT-RUN-0021"
    assert module.TASK_ID == "TASK-0321"
    assert hasattr(module, "build_metrics")
    assert hasattr(module, "render_report")


def test_magic_axis_audit_metrics_recompute() -> None:
    module = _load_magic_axis_module()
    recomputed = module.build_metrics()
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert recomputed["agent_run_id"] == "AGENT-RUN-0021"
    assert recomputed["task_id"] == "TASK-0321"
    assert recomputed["sandbox_only"] is True
    assert recomputed["summary"] == committed["summary"]
    assert recomputed["datasets"] == committed["datasets"]
    _assert_nested_close(recomputed["subset_summary"], committed["subset_summary"])
    _assert_nested_close(recomputed["candidate_items"], committed["candidate_items"])


def test_magic_axis_audit_subset_counts_and_sparse_warnings() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    subsets = metrics["subset_summary"]

    assert subsets["primary_holdout"]["row_count"] == 295
    assert subsets["magic_n"]["row_count"] == 17
    assert subsets["magic_z"]["row_count"] == 13
    assert subsets["near_magic"]["row_count"] == 126
    assert subsets["double_magic"]["row_count"] == 5
    assert subsets["double_magic"]["sparse_warning"] is True
    assert subsets["non_magic_matched_double_magic"]["row_count"] == 5
    assert subsets["non_magic_matched_double_magic"]["sparse_warning"] is True


def test_magic_axis_audit_directional_verdict() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert metrics["directional_summary"]["verdict"] == "NEUTRON_DOMINANT_BUT_SPARSE"
    assert metrics["directional_summary"]["neutron_dominant_candidate_count"] == 3
    assert metrics["directional_summary"]["proton_dominant_candidate_count"] == 0
    labels = metrics["directional_summary"]["primary_candidate_labels"]
    assert labels == {
        "FULLKNOWN-SHELL-001": "NEUTRON_DOMINANT",
        "FULLKNOWN-SHELL-002": "NEUTRON_DOMINANT",
        "FULLKNOWN-SHELL-003": "NEUTRON_DOMINANT",
    }


def test_magic_axis_audit_controls_behave_conservatively() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    by_id = {item["candidate_id"]: item for item in metrics["candidate_items"]}

    for candidate_id in ("FULLKNOWN-SHELL-001", "FULLKNOWN-SHELL-002", "FULLKNOWN-SHELL-003"):
        item = by_id[candidate_id]
        assert item["focus_delta_mae_mev"]["magic_n"] < item["focus_delta_mae_mev"]["magic_z"]
        assert item["focus_delta_mae_mev"]["magic_n"] < 0.0
        assert item["focus_delta_mae_mev"]["near_magic"] < 0.0

    sign = by_id["FULLKNOWN-SHELL-004"]
    assert sign["sign_inverted"] is True
    assert sign["focus_delta_mae_mev"]["magic_n"] > 0.0
    assert sign["focus_delta_mae_mev"]["magic_z"] > 0.0

    shuffled = by_id["FULLKNOWN-SHELL-005"]
    assert shuffled["shuffle_scheme"] == "cyclic-shift-5"
    assert abs(shuffled["focus_delta_mae_mev"]["magic_n"]) < 1.0e-3

    baseline = by_id["FULLKNOWN-SHELL-006"]
    assert baseline["baseline_reference_control"] is True
    assert all(value == 0.0 for value in baseline["focus_delta_mae_mev"].values())


def test_magic_axis_audit_manifest_and_no_registry_writes(tmp_path: Path) -> None:
    module = _load_magic_axis_module()
    manifest = yaml.safe_load(AGENT_RUN_PATH.read_text(encoding="utf-8"))
    out_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"

    assert manifest["id"] == "AGENT-RUN-0021"
    assert manifest["task_id"] == "TASK-0321"
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
