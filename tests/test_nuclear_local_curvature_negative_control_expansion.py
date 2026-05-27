from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "run_nuclear_local_curvature_negative_control_expansion.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "local_curvature_negative_controls",
        MODULE_PATH,
    )
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _assert_nested_close(left, right) -> None:
    if isinstance(left, dict):
        assert left.keys() == right.keys()
        for key in left:
            _assert_nested_close(left[key], right[key])
        return
    if isinstance(left, list):
        assert len(left) == len(right)
        for left_item, right_item in zip(left, right):
            _assert_nested_close(left_item, right_item)
        return
    if isinstance(left, float):
        assert left == pytest.approx(right, abs=1e-12)
        return
    assert left == right


def test_negative_control_variant_panel_covers_required_categories() -> None:
    module = _load_module()
    variants = module._build_negative_control_variants()

    candidate_ids = [variant["candidate_id"] for variant in variants]
    assert candidate_ids[:3] == [
        "LOCAL-CURVATURE-001",
        "LOCAL-CURVATURE-002",
        "LOCAL-CURVATURE-003",
    ]

    controls = [variant for variant in variants if variant["role"].endswith("_control")]
    assert len(controls) == 8
    assert {
        variant["control_category"]
        for variant in controls
        if "control_category" in variant
    } == {
        "chain_shuffled",
        "mass_number_only",
        "magic_distance_only",
        "smooth_window",
        "near_null_neighborhood",
        "neighbor_availability",
    }


def test_build_metrics_records_sandbox_boundary_and_required_outputs() -> None:
    module = _load_module()
    metrics = module.build_metrics()
    summary = metrics["summary"]

    assert metrics["agent_run_id"] == "AGENT-RUN-0041"
    assert metrics["task_id"] == "TASK-0397"
    assert metrics["sandbox_only"] is True
    assert metrics["live_external_fetch_allowed"] is False
    assert summary["executed_candidate_count"] == 3
    assert summary["executed_negative_control_count"] >= 5
    assert summary["canonical_results_changed"] is False
    assert summary["canonical_claims_changed"] is False
    assert summary["prediction_registry_changed"] is False
    assert summary["claim_promotion_allowed"] is False
    assert summary["lane_verdict"] in {"PARTIALLY_VALID", "INCONCLUSIVE", "FALSIFIED"}
    assert summary["control_explanation_verdict"] in {
        "CONTROL_EXPLAINS_OR_MATCHES",
        "INCONCLUSIVE",
        "NOT_EXPLAINED_BY_TESTED_CONTROLS",
    }

    for subset_id in (
        "full_known",
        "primary_holdout",
        "magic_any",
        "neutron_rich_local",
        "high_error_baseline_p75",
    ):
        assert subset_id in metrics["baseline_metrics_by_subset"]


def test_candidate_comparison_and_transfer_tables_are_complete() -> None:
    module = _load_module()
    metrics = module.build_metrics()

    comparisons = metrics["candidate_vs_strongest_control"]
    assert {row["candidate_id"] for row in comparisons} == {
        "LOCAL-CURVATURE-001",
        "LOCAL-CURVATURE-002",
        "LOCAL-CURVATURE-003",
    }
    for row in comparisons:
        assert row["primary_strongest_control_id"] is not None
        assert row["comparable_subset_count"] > 0
        assert 0.0 <= row["subset_win_rate"] <= 1.0

    for transfer_key in ("isotope_chain_transfer", "isotone_chain_transfer"):
        transfer = metrics[transfer_key]
        assert transfer["interpretable_group_count"] > 0
        for candidate_id in (
            "LOCAL-CURVATURE-001",
            "LOCAL-CURVATURE-002",
            "LOCAL-CURVATURE-003",
        ):
            assert candidate_id in transfer["by_candidate"]
            assert transfer["by_candidate"][candidate_id]["improvement_rate"] is not None


def test_committed_metrics_match_recomputed_summary() -> None:
    module = _load_module()
    committed = json.loads(
        (
            Path(__file__).resolve().parents[1]
            / "agent_runs"
            / "AGENT-RUN-0041"
            / "metrics.json"
        ).read_text(encoding="utf-8")
    )
    recomputed = module.build_metrics()

    _assert_nested_close(committed["summary"], recomputed["summary"])
    _assert_nested_close(
        committed["control_explanation"],
        recomputed["control_explanation"],
    )
    _assert_nested_close(
        committed["candidate_vs_strongest_control"],
        recomputed["candidate_vs_strongest_control"],
    )


def test_runner_writes_only_sandbox_outputs(tmp_path: Path) -> None:
    module = _load_module()
    targets = {
        "--out": tmp_path / "metrics.json",
        "--report": tmp_path / "report.md",
        "--agent-run": tmp_path / "agent_run.yaml",
        "--limitations": tmp_path / "limitations.md",
        "--preflight": tmp_path / "preflight.md",
        "--review-summary": tmp_path / "review_summary.md",
        "--review": tmp_path / "review.md",
    }
    args: list[str] = []
    for flag, path in targets.items():
        args.extend([flag, str(path)])

    assert module.main(args) == 0
    for path in targets.values():
        assert path.exists()
