"""Reproducibility tests for AGENT-RUN-0029 uncertainty-weighted lane."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_uncertainty_weighted_residual_lane.py"
METRICS_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0029" / "metrics.json"
AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0029" / "agent_run.yaml"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "run_nuclear_uncertainty_weighted_residual_lane", SCRIPT_PATH
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


def test_uncertainty_weighted_runner_imports_cleanly() -> None:
    module = _load_module()

    assert module.AGENT_RUN_ID == "AGENT-RUN-0029"
    assert module.TASK_ID == "TASK-0342"
    assert hasattr(module, "build_metrics")
    assert hasattr(module, "render_report")


def test_uncertainty_weighted_metrics_recompute() -> None:
    module = _load_module()
    recomputed = module.build_metrics()
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert recomputed["agent_run_id"] == "AGENT-RUN-0029"
    assert recomputed["task_id"] == "TASK-0342"
    assert recomputed["sandbox_only"] is True
    assert recomputed["summary"] == committed["summary"]
    assert recomputed["datasets"] == committed["datasets"]
    _assert_nested_close(recomputed["variant_items"], committed["variant_items"])
    _assert_nested_close(
        recomputed["baseline_metrics_by_subset"],
        committed["baseline_metrics_by_subset"],
    )
    _assert_nested_close(
        recomputed["prior_lane_sensitivity_review"],
        committed["prior_lane_sensitivity_review"],
    )


def test_uncertainty_weighted_boundary_and_variants() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    summary = metrics["summary"]

    assert summary["variant_count"] == 5
    assert summary["lane_verdict"] == "INCONCLUSIVE"
    assert summary["uncertainty_field_grade"] == "review_only"
    assert summary["fit_grade_uncertainty_row_count"] == 0
    assert summary["review_only_uncertainty_row_count"] == 306
    assert summary["rows_missing_positive_weight_uncertainty"] == 0
    assert summary["canonical_results_changed"] is False
    assert summary["canonical_claims_changed"] is False
    assert summary["prediction_registry_changed"] is False
    assert summary["claim_promotion_allowed"] is False

    roles = {item["variant_id"]: item["role"] for item in metrics["variant_items"]}
    assert roles["UNCERTAINTY-BASELINE-001"] == "unweighted_reference"
    assert roles["UNCERTAINTY-WEIGHT-001"] == "uncertainty_weighted_diagnostic"
    assert roles["UNCERTAINTY-WEIGHT-002"] == "uncertainty_weighted_diagnostic"
    assert roles["UNCERTAINTY-FILTER-001"] == "uncertainty_filter_diagnostic"
    assert roles["UNCERTAINTY-FILTER-002"] == "uncertainty_filter_diagnostic"


def test_uncertainty_weighted_reports_required_diagnostics() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert metrics["datasets"]["training_row_count"] == 11
    assert metrics["datasets"]["post_ame2020_primary_holdout_row_count"] == 295
    assert metrics["datasets"]["full_known_unique_row_count"] == 306
    assert metrics["prior_lane_sensitivity_review"]["status"] == "sensitive_review_gate"
    assert metrics["baseline_metrics_by_subset"]["low_uncertainty_half"]["count"] > 0
    assert metrics["baseline_metrics_by_subset"]["high_uncertainty_half"]["count"] > 0
    assert metrics["largest_uncertainty_normalized_rows"]
    for item in metrics["variant_items"]:
        assert item["metrics"]["mae_mev"] is not None
        assert item["metrics"]["rmse_mev"] is not None
        assert item["metrics"]["weighted_mae_mev"] is not None
        assert item["metrics"]["mean_abs_uncertainty_normalized_error"] is not None


def test_uncertainty_weighted_manifest_and_no_registry_writes(tmp_path: Path) -> None:
    module = _load_module()
    manifest = yaml.safe_load(AGENT_RUN_PATH.read_text(encoding="utf-8"))
    out_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"
    agent_run_path = tmp_path / "agent_run.yaml"
    limitations_path = tmp_path / "limitations.md"
    preflight_path = tmp_path / "preflight.md"
    review_summary_path = tmp_path / "review_summary.md"
    review_path = tmp_path / "review.md"

    assert manifest["id"] == "AGENT-RUN-0029"
    assert manifest["task_id"] == "TASK-0342"
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
