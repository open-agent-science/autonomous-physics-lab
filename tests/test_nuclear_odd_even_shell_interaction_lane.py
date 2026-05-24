"""Reproducibility tests for AGENT-RUN-0027 odd-even shell-interaction lane."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_odd_even_shell_interaction_lane.py"
METRICS_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0027" / "metrics.json"
AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0027" / "agent_run.yaml"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "run_nuclear_odd_even_shell_interaction_lane", SCRIPT_PATH
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


def test_odd_even_shell_runner_imports_cleanly() -> None:
    module = _load_module()

    assert module.AGENT_RUN_ID == "AGENT-RUN-0027"
    assert module.TASK_ID == "TASK-0340"
    assert hasattr(module, "build_metrics")
    assert hasattr(module, "render_report")


def test_odd_even_shell_metrics_recompute() -> None:
    module = _load_module()
    recomputed = module.build_metrics()
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert recomputed["agent_run_id"] == "AGENT-RUN-0027"
    assert recomputed["task_id"] == "TASK-0340"
    assert recomputed["sandbox_only"] is True
    assert recomputed["summary"] == committed["summary"]
    assert recomputed["datasets"] == committed["datasets"]
    _assert_nested_close(recomputed["candidate_items"], committed["candidate_items"])
    _assert_nested_close(
        recomputed["lower_complexity_control_gate"],
        committed["lower_complexity_control_gate"],
    )


def test_odd_even_shell_preserves_candidate_and_control_boundary() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    summary = metrics["summary"]

    assert summary["generated_interaction_variant_count"] == 6
    assert summary["executed_interaction_count"] == 3
    assert summary["executed_control_count"] == 4
    assert summary["canonical_results_changed"] is False
    assert summary["canonical_claims_changed"] is False
    assert summary["prediction_registry_changed"] is False
    assert summary["claim_promotion_allowed"] is False

    roles = {item["candidate_id"]: item["role"] for item in metrics["candidate_items"]}
    assert roles["ODD-SHELL-CONTROL-001"] == "pairing_only_control"
    assert roles["ODD-SHELL-CONTROL-002"] == "shell_only_control"
    assert roles["ODD-SHELL-CONTROL-003"] == "smooth_a_control"
    assert roles["ODD-SHELL-CONTROL-004"] == "shuffled_interaction_control"


def test_odd_even_shell_reports_required_subsets_and_control_gate() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert metrics["lower_complexity_control_gate"]
    for item in metrics["candidate_items"]:
        assert item["primary_delta_mae_mev"] is not None
        assert item["holdout_delta_mae_mev"] is not None
        assert item["even_even_delta_mae_mev"] is not None
        assert item["odd_even_delta_mae_mev"] is not None
        assert item["odd_odd_delta_mae_mev"] is not None
        assert item["magic_z_delta_mae_mev"] is not None
        assert item["magic_n_delta_mae_mev"] is not None
        assert item["light_a_warning_delta_mae_mev"] is not None
        assert item["neutron_rich_delta_mae_mev"] is not None
        assert item["largest_regressions"]
        assert item["largest_improvements"]


def test_odd_even_shell_manifest_and_no_registry_writes(tmp_path: Path) -> None:
    module = _load_module()
    manifest = yaml.safe_load(AGENT_RUN_PATH.read_text(encoding="utf-8"))
    out_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"
    agent_run_path = tmp_path / "agent_run.yaml"
    limitations_path = tmp_path / "limitations.md"
    preflight_path = tmp_path / "preflight.md"
    review_summary_path = tmp_path / "review_summary.md"
    review_path = tmp_path / "review.md"

    assert manifest["id"] == "AGENT-RUN-0027"
    assert manifest["task_id"] == "TASK-0340"
    assert manifest["sandbox_only"] is True
    assert manifest["promotion_boundary"]["writes_canonical_result"] is False
    assert manifest["promotion_boundary"]["claim_promotion_allowed"] is False

    registry_dir = REPO_ROOT / "prediction_registry" / "nuclear_masses"
    before = sorted(path.name for path in registry_dir.iterdir())
    module.main(
        [
            "--out",
            str(out_path),
            "--report",
            str(report_path),
            "--agent-run",
            str(agent_run_path),
            "--limitations",
            str(limitations_path),
            "--preflight",
            str(preflight_path),
            "--review-summary",
            str(review_summary_path),
            "--review",
            str(review_path),
        ]
    )
    after = sorted(path.name for path in registry_dir.iterdir())

    assert out_path.exists()
    assert report_path.exists()
    assert agent_run_path.exists()
    assert limitations_path.exists()
    assert preflight_path.exists()
    assert review_summary_path.exists()
    assert review_path.exists()
    assert before == after
