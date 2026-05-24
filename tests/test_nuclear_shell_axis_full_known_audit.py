"""Reproducibility tests for AGENT-RUN-0018 full-known shell-axis audit."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_shell_axis_full_known_audit.py"
METRICS_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0018" / "metrics.json"
AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0018" / "agent_run.yaml"


def _load_audit_module():
    spec = importlib.util.spec_from_file_location(
        "run_nuclear_shell_axis_full_known_audit", SCRIPT_PATH
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


def test_full_known_audit_runner_imports_cleanly() -> None:
    module = _load_audit_module()
    assert module.AGENT_RUN_ID == "AGENT-RUN-0018"
    assert module.TASK_ID == "TASK-0310"
    assert hasattr(module, "build_metrics")
    assert hasattr(module, "render_report")


def test_full_known_audit_metrics_recompute() -> None:
    module = _load_audit_module()
    recomputed = module.build_metrics()
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert recomputed["agent_run_id"] == "AGENT-RUN-0018"
    assert recomputed["task_id"] == "TASK-0310"
    assert recomputed["sandbox_only"] is True
    assert recomputed["summary"] == committed["summary"]
    assert recomputed["datasets"] == committed["datasets"]
    _assert_nested_close(
        recomputed["baseline_metrics_by_subset"],
        committed["baseline_metrics_by_subset"],
    )
    _assert_nested_close(recomputed["executed_items"], committed["executed_items"])


def test_full_known_audit_surfaces_and_controls() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert metrics["datasets"]["training_row_count"] == 11
    assert metrics["datasets"]["post_ame2020_primary_holdout_row_count"] == 295
    assert metrics["datasets"]["full_known_unique_row_count"] == 306
    assert metrics["summary"]["sign_inverted_control_preserved"] is True
    assert metrics["summary"]["shuffled_feature_control_preserved"] is True
    assert metrics["summary"]["near_null_control_preserved"] is True


def test_full_known_audit_executed_candidate_ids() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    executed = metrics["executed_items"]
    assert {item["candidate_id"] for item in executed} == {
        "FULLKNOWN-SHELL-001",
        "FULLKNOWN-SHELL-002",
        "FULLKNOWN-SHELL-003",
        "FULLKNOWN-SHELL-004",
        "FULLKNOWN-SHELL-005",
        "FULLKNOWN-SHELL-006",
    }


def test_full_known_audit_primary_candidates_improve_holdout() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    by_id = {item["candidate_id"]: item for item in metrics["executed_items"]}
    for candidate_id in (
        "FULLKNOWN-SHELL-001",
        "FULLKNOWN-SHELL-002",
        "FULLKNOWN-SHELL-003",
    ):
        item = by_id[candidate_id]
        assert item["verdict"] == "PARTIALLY_VALID"
        assert item["delta_mae_by_subset_mev"]["full_known"] < 0.0
        assert item["delta_mae_by_subset_mev"]["primary_holdout"] < 0.0


def test_full_known_audit_null_controls_behave_conservatively() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    by_id = {item["candidate_id"]: item for item in metrics["executed_items"]}

    sign = by_id["FULLKNOWN-SHELL-004"]
    assert sign["sign_inverted"] is True
    assert sign["delta_mae_by_subset_mev"]["full_known"] > 0.0
    assert sign["delta_mae_by_subset_mev"]["primary_holdout"] > 0.0

    shuffled = by_id["FULLKNOWN-SHELL-005"]
    assert shuffled["shuffle_scheme"] == "cyclic-shift-5"
    assert shuffled["shuffle_noise_floor"] is True

    near_null = by_id["FULLKNOWN-SHELL-006"]
    assert near_null["baseline_reference_control"] is True
    for value in near_null["delta_mae_by_subset_mev"].values():
        if value is not None:
            assert abs(value) < 1.0e-12


def test_full_known_audit_agent_run_manifest() -> None:
    manifest = yaml.safe_load(AGENT_RUN_PATH.read_text(encoding="utf-8"))

    assert manifest["id"] == "AGENT-RUN-0018"
    assert manifest["task_id"] == "TASK-0310"
    assert manifest["sandbox_only"] is True
    assert manifest["promotion_boundary"]["writes_canonical_result"] is False
    assert manifest["promotion_boundary"]["claim_promotion_allowed"] is False
    assert manifest["artifacts"]["metrics"] == (
        Path("agent_runs") / "AGENT-RUN-0018" / "metrics.json"
    ).as_posix()


def test_full_known_audit_does_not_write_prediction_registry(tmp_path: Path) -> None:
    module = _load_audit_module()
    out_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"

    registry_dir = REPO_ROOT / "prediction_registry" / "nuclear_masses"
    before = sorted(path.name for path in registry_dir.iterdir())
    module.main(["--out", str(out_path), "--report", str(report_path)])
    after = sorted(path.name for path in registry_dir.iterdir())

    assert out_path.exists()
    assert report_path.exists()
    assert before == after

