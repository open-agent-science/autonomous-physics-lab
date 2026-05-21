"""Reproducibility tests for AGENT-RUN-0019 shell-axis stability audit."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_shell_axis_stability_audit.py"
METRICS_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0019" / "metrics.json"
AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0019" / "agent_run.yaml"


def _load_stability_module():
    spec = importlib.util.spec_from_file_location(
        "run_nuclear_shell_axis_stability_audit", SCRIPT_PATH
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


def test_stability_audit_runner_imports_cleanly() -> None:
    module = _load_stability_module()
    assert module.AGENT_RUN_ID == "AGENT-RUN-0019"
    assert module.TASK_ID == "TASK-0316"
    assert hasattr(module, "build_metrics")
    assert hasattr(module, "render_report")


def test_stability_audit_metrics_recompute() -> None:
    module = _load_stability_module()
    recomputed = module.build_metrics()
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert recomputed["agent_run_id"] == "AGENT-RUN-0019"
    assert recomputed["task_id"] == "TASK-0316"
    assert recomputed["sandbox_only"] is True
    assert recomputed["summary"] == committed["summary"]
    assert recomputed["datasets"] == committed["datasets"]
    _assert_nested_close(recomputed["candidate_summaries"], committed["candidate_summaries"])
    _assert_nested_close(recomputed["controls"], committed["controls"])


def test_stability_audit_preserves_fragile_verdict() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert metrics["summary"]["overall_verdict"] == "FRAGILE"
    assert metrics["summary"]["verdict_counts"] == {"FRAGILE": 3}
    assert metrics["summary"]["leave_one_out_fit_count_per_candidate"] == 11
    assert metrics["summary"]["small_resample_fit_count_per_candidate"] == 165


def test_stability_audit_leave_one_out_survives_but_size8_fragilizes() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    for item in metrics["candidate_summaries"]:
        loo = item["resampling"]["leave_one_out"]
        size8 = item["resampling"]["small_resample_size_8_of_11"]
        assert loo["coefficient_sign_stable"] is True
        assert loo["full_known_improvement_rate"] == 1.0
        assert loo["holdout_improvement_rate"] == 1.0
        assert size8["coefficient_sign_stable"] is False
        assert 0.0 < size8["max_full_known_regression_mev"]
        assert 0.0 < size8["max_holdout_regression_mev"]


def test_stability_audit_controls_and_manifest() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    manifest_text = AGENT_RUN_PATH.read_text(encoding="utf-8")

    assert metrics["controls"]["near_null_reference"]["all_delta_mae_mev"] == 0.0
    assert metrics["controls"]["shuffled_feature_control"]["status"] == (
        "not_rerun_under_resampling"
    )
    sign = metrics["controls"]["sign_inverted_proton_axis"]["resampling"]["leave_one_out"]
    assert sign["full_known_improvement_rate"] == 0.0
    assert sign["holdout_improvement_rate"] == 0.0
    assert "verdict: INCONCLUSIVE" in manifest_text


def test_stability_audit_does_not_write_prediction_registry(tmp_path: Path) -> None:
    module = _load_stability_module()
    out_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"

    registry_dir = REPO_ROOT / "prediction_registry" / "nuclear_masses"
    before = sorted(path.name for path in registry_dir.iterdir())
    module.main(["--out", str(out_path), "--report", str(report_path)])
    after = sorted(path.name for path in registry_dir.iterdir())

    assert out_path.exists()
    assert report_path.exists()
    assert before == after
