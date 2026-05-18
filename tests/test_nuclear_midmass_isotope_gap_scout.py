"""Reproducibility tests for AGENT-RUN-0015 mid-mass / isotope-chain scout."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_midmass_isotope_gap_scout.py"
METRICS_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0015" / "metrics.json"
AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0015" / "agent_run.yaml"


def _load_scout_module():
    spec = importlib.util.spec_from_file_location(
        "run_nuclear_midmass_isotope_gap_scout", SCRIPT_PATH
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


def test_midmass_isotope_scout_runner_imports_cleanly() -> None:
    module = _load_scout_module()
    assert hasattr(module, "build_metrics")
    assert hasattr(module, "render_report")
    assert module.AGENT_RUN_ID == "AGENT-RUN-0015"
    assert module.TASK_ID == "TASK-0286"


def test_midmass_isotope_scout_metrics_recompute() -> None:
    module = _load_scout_module()
    recomputed = module.build_metrics()
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert recomputed["agent_run_id"] == "AGENT-RUN-0015"
    assert recomputed["task_id"] == "TASK-0286"
    assert recomputed["sandbox_only"] is True
    assert recomputed["summary"] == committed["summary"]
    assert recomputed["frozen_baseline"] == committed["frozen_baseline"]
    _assert_nested_close(
        recomputed["baseline_metrics_by_subset"],
        committed["baseline_metrics_by_subset"],
    )
    _assert_nested_close(
        recomputed["executed_items"],
        committed["executed_items"],
    )


def test_midmass_isotope_scout_candidate_triage() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    assert metrics["summary"]["generated_candidate_count"] == 8
    assert metrics["summary"]["executed_candidate_count"] == 5
    assert metrics["summary"]["rejected_before_execution_count"] == 3
    assert metrics["summary"]["near_null_control_preserved"] is True


def test_midmass_isotope_scout_rejected_have_reasons() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    rejected = metrics["rejected_before_execution"]
    assert len(rejected) == 3
    rejected_ids = {item["candidate_id"] for item in rejected}
    assert rejected_ids == {
        "MIDMASS-SCOUT-006",
        "MIDMASS-SCOUT-007",
        "MIDMASS-SCOUT-008",
    }
    for item in rejected:
        assert "rejection_reason" in item
        assert isinstance(item["rejection_reason"], str)
        assert len(item["rejection_reason"]) > 0


def test_midmass_isotope_scout_executed_candidates_produce_deltas() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    executed = metrics["executed_items"]
    assert len(executed) == 5
    expected_ids = {
        "MIDMASS-SCOUT-001",
        "MIDMASS-SCOUT-002",
        "MIDMASS-SCOUT-003",
        "MIDMASS-SCOUT-004",
        "MIDMASS-SCOUT-005",
    }
    assert {item["candidate_id"] for item in executed} == expected_ids

    for item in executed:
        deltas = item["delta_mae_by_subset_mev"]
        for required_subset in ("primary", "mid_mass", "light", "heavy"):
            assert required_subset in deltas
            assert deltas[required_subset] is not None
            assert isinstance(deltas[required_subset], float)


def test_midmass_isotope_scout_near_null_control_is_zero() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    by_id = {item["candidate_id"]: item for item in metrics["executed_items"]}
    null = by_id["MIDMASS-SCOUT-005"]
    assert null["verdict"] == "INCONCLUSIVE"
    deltas = null["delta_mae_by_subset_mev"]
    for subset, delta in deltas.items():
        if delta is None:
            continue
        assert abs(delta) < 1.0e-12, f"near-null delta on {subset} is {delta}"
    assert null["frontier_contrast_mev"] == 0.0


def test_midmass_isotope_scout_metrics_schema() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    required_keys = {
        "agent_run_id",
        "task_id",
        "campaign_profile_id",
        "lane",
        "sandbox_only",
        "evidence_class",
        "live_external_fetch_allowed",
        "summary",
        "frozen_baseline",
        "datasets",
        "subset_definitions",
        "feature_definitions",
        "isotope_chain_reference",
        "baseline_metrics_by_subset",
        "generated_candidates",
        "executed_items",
        "rejected_before_execution",
        "promotion_boundary",
        "limitations",
    }
    assert required_keys.issubset(metrics.keys())
    assert metrics["sandbox_only"] is True
    assert metrics["live_external_fetch_allowed"] is False
    assert metrics["lane"] == "midmass_isotope_gap_scout"


def test_midmass_isotope_scout_agent_run_manifest() -> None:
    manifest = yaml.safe_load(AGENT_RUN_PATH.read_text(encoding="utf-8"))

    assert manifest["id"] == "AGENT-RUN-0015"
    assert manifest["task_id"] == "TASK-0286"
    assert manifest["campaign_profile_id"] == "nuclear-mass-surface"
    assert manifest["sandbox_only"] is True
    assert manifest["proposal_paths"]["hypothesis"] == str(
        Path("hypothesis_proposals")
        / "nuclear-mass"
        / "HYP-PROPOSAL-0043-midmass-isotope-gap-scout-batch.yaml"
    )
    assert manifest["proposal_paths"]["experiment"] == str(
        Path("experiment_proposals")
        / "nuclear-mass"
        / "EXP-PROPOSAL-0009-nuclear-midmass-isotope-gap-scout.yaml"
    )
    assert manifest["artifacts"]["metrics"] == str(
        Path("agent_runs") / "AGENT-RUN-0015" / "metrics.json"
    )
    assert manifest["promotion_boundary"]["writes_canonical_result"] is False
    assert manifest["promotion_boundary"]["claim_promotion_allowed"] is False


def test_midmass_isotope_scout_promotion_boundary() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert metrics["summary"]["canonical_results_changed"] is False
    assert metrics["summary"]["canonical_claims_changed"] is False
    assert metrics["summary"]["prediction_registry_changed"] is False
    assert metrics["promotion_boundary"]["writes_prediction_registry"] is False
    assert metrics["promotion_boundary"]["writes_canonical_result"] is False
    assert metrics["promotion_boundary"]["claim_promotion_allowed"] is False


def test_midmass_isotope_scout_does_not_write_prediction_registry(tmp_path: Path) -> None:
    """Running the runner with custom output paths must not touch prediction_registry/."""
    module = _load_scout_module()
    out_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"

    registry_dir = REPO_ROOT / "prediction_registry" / "nuclear_masses"
    before = (
        sorted(p.name for p in registry_dir.iterdir()) if registry_dir.exists() else []
    )

    module.main(["--out", str(out_path), "--report", str(report_path)])

    assert out_path.exists()
    assert report_path.exists()
    after = (
        sorted(p.name for p in registry_dir.iterdir()) if registry_dir.exists() else []
    )
    assert before == after


def test_midmass_isotope_scout_subset_definitions_match_design() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()
    defs = metrics["subset_definitions"]
    for required in (
        "primary",
        "mid_mass",
        "light",
        "heavy",
        "isotope_chain_z20",
        "isotope_chain_z28",
        "isotope_chain_z50",
        "frontier_contrast",
    ):
        assert required in defs
