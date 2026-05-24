"""Reproducibility tests for AGENT-RUN-0020 shell-axis specificity controls."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_shell_axis_specificity_controls.py"
METRICS_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0020" / "metrics.json"
AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0020" / "agent_run.yaml"


def _load_specificity_module():
    spec = importlib.util.spec_from_file_location(
        "run_nuclear_shell_axis_specificity_controls", SCRIPT_PATH
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


def test_specificity_controls_runner_imports_cleanly() -> None:
    module = _load_specificity_module()
    assert module.AGENT_RUN_ID == "AGENT-RUN-0020"
    assert module.TASK_ID == "TASK-0317"
    assert hasattr(module, "build_metrics")
    assert hasattr(module, "render_report")


def test_specificity_controls_metrics_recompute() -> None:
    module = _load_specificity_module()
    recomputed = module.build_metrics()
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert recomputed["agent_run_id"] == "AGENT-RUN-0020"
    assert recomputed["task_id"] == "TASK-0317"
    assert recomputed["sandbox_only"] is True
    assert recomputed["summary"] == committed["summary"]
    assert recomputed["datasets"] == committed["datasets"]
    _assert_nested_close(recomputed["specificity"], committed["specificity"])
    _assert_nested_close(
        recomputed["shell_axis_candidates"],
        committed["shell_axis_candidates"],
    )
    _assert_nested_close(recomputed["non_shell_controls"], committed["non_shell_controls"])


def test_specificity_controls_preserve_required_surfaces() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert metrics["datasets"]["training_row_count"] == 11
    assert metrics["datasets"]["post_ame2020_primary_holdout_row_count"] == 295
    assert metrics["datasets"]["full_known_unique_row_count"] == 306
    assert metrics["summary"]["required_subset_delta_keys"] == [
        "full_known",
        "primary_holdout",
        "training_slice",
        "magic_z",
        "magic_n",
        "light_a_lt_50",
    ]


def test_specificity_controls_compare_shell_against_non_shell_controls() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert metrics["summary"]["shell_candidate_count"] == 3
    assert metrics["summary"]["non_shell_control_count"] == 5
    assert metrics["specificity"]["verdict"] == "SHELL_SPECIFIC_BUT_BOUNDED"
    assert metrics["specificity"]["best_shell_candidate_id"] == "FULLKNOWN-SHELL-001"
    assert metrics["specificity"]["best_non_shell_control_id"] == (
        "SPECIFICITY-CONTROL-001"
    )
    assert metrics["specificity"]["best_shell_full_known_delta_mae_mev"] < (
        metrics["specificity"]["best_non_shell_full_known_delta_mae_mev"]
    )
    assert metrics["specificity"]["best_shell_primary_holdout_delta_mae_mev"] < (
        metrics["specificity"]["best_non_shell_primary_holdout_delta_mae_mev"]
    )


def test_specificity_controls_keep_negative_and_bounded_findings_visible() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    shell_by_id = {item["candidate_id"]: item for item in metrics["shell_axis_candidates"]}
    for candidate_id in ("FULLKNOWN-SHELL-001", "FULLKNOWN-SHELL-002", "FULLKNOWN-SHELL-003"):
        item = shell_by_id[candidate_id]
        assert item["required_delta_mae_mev"]["full_known"] < 0.0
        assert item["required_delta_mae_mev"]["primary_holdout"] < 0.0
        assert item["required_delta_mae_mev"]["light_a_lt_50"] > 0.0

    control_by_id = {item["candidate_id"]: item for item in metrics["non_shell_controls"]}
    assert control_by_id["SPECIFICITY-CONTROL-000"]["required_delta_mae_mev"] == {
        "full_known": 0.0,
        "primary_holdout": 0.0,
        "training_slice": 0.0,
        "magic_z": 0.0,
        "magic_n": 0.0,
        "light_a_lt_50": 0.0,
    }
    assert control_by_id["SPECIFICITY-CONTROL-004"]["required_delta_mae_mev"][
        "primary_holdout"
    ] > 0.0


def test_specificity_controls_manifest_and_no_registry_writes(tmp_path: Path) -> None:
    module = _load_specificity_module()
    manifest = yaml.safe_load(AGENT_RUN_PATH.read_text(encoding="utf-8"))
    out_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"

    assert manifest["id"] == "AGENT-RUN-0020"
    assert manifest["task_id"] == "TASK-0317"
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
