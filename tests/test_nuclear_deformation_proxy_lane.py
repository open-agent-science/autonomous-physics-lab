"""Reproducibility tests for AGENT-RUN-0025 deformation-proxy lane."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_deformation_proxy_lane.py"
METRICS_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0025" / "metrics.json"
AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0025" / "agent_run.yaml"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "run_nuclear_deformation_proxy_lane", SCRIPT_PATH
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


def test_deformation_proxy_runner_imports_cleanly() -> None:
    module = _load_module()

    assert module.AGENT_RUN_ID == "AGENT-RUN-0025"
    assert module.TASK_ID == "TASK-0338"
    assert hasattr(module, "build_metrics")
    assert hasattr(module, "render_report")


def test_deformation_proxy_metrics_recompute() -> None:
    module = _load_module()
    recomputed = module.build_metrics()
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert recomputed["agent_run_id"] == "AGENT-RUN-0025"
    assert recomputed["task_id"] == "TASK-0338"
    assert recomputed["sandbox_only"] is True
    assert recomputed["summary"] == committed["summary"]
    assert recomputed["datasets"] == committed["datasets"]
    _assert_nested_close(recomputed["candidate_items"], committed["candidate_items"])
    _assert_nested_close(
        recomputed["isotope_chain_diagnostics"],
        committed["isotope_chain_diagnostics"],
    )


def test_deformation_proxy_preserves_candidate_and_control_boundary() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    summary = metrics["summary"]

    assert summary["generated_variant_count"] == 6
    assert summary["generated_control_count"] == 2
    assert summary["executed_candidate_count"] == 3
    assert summary["executed_control_count"] == 2
    assert summary["canonical_results_changed"] is False
    assert summary["canonical_claims_changed"] is False
    assert summary["prediction_registry_changed"] is False
    assert summary["claim_promotion_allowed"] is False

    roles = {item["candidate_id"]: item["role"] for item in metrics["candidate_items"]}
    assert roles["DEFORM-CONTROL-001"] == "smooth_a_control"
    assert roles["DEFORM-CONTROL-002"] == "shuffled_proxy_control"


def test_deformation_proxy_reports_required_subsets_and_chain_diagnostics() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert metrics["isotope_chain_diagnostics"]["interpretable_group_count"] > 0
    for item in metrics["candidate_items"]:
        assert item["primary_delta_mae_mev"] is not None
        assert item["primary_delta_rmse_mev"] is not None
        assert item["holdout_delta_mae_mev"] is not None
        assert item["magic_z_delta_mae_mev"] is not None
        assert item["magic_n_delta_mae_mev"] is not None
        assert item["mid_mass_delta_mae_mev"] is not None
        assert item["heavy_delta_mae_mev"] is not None
        assert item["neutron_rich_delta_mae_mev"] is not None
        assert item["light_a_warning_delta_mae_mev"] is not None
        assert item["largest_regressions"]
        assert item["largest_improvements"]


def test_deformation_proxy_manifest_and_no_registry_writes(tmp_path: Path) -> None:
    module = _load_module()
    manifest = yaml.safe_load(AGENT_RUN_PATH.read_text(encoding="utf-8"))
    out_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"
    agent_run_path = tmp_path / "agent_run.yaml"
    limitations_path = tmp_path / "limitations.md"
    preflight_path = tmp_path / "preflight.md"
    review_summary_path = tmp_path / "review_summary.md"
    review_path = tmp_path / "review.md"

    assert manifest["id"] == "AGENT-RUN-0025"
    assert manifest["task_id"] == "TASK-0338"
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
