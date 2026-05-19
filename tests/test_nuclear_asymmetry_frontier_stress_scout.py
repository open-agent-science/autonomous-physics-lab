"""Reproducibility tests for AGENT-RUN-0017 asymmetry-frontier stress scout."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_asymmetry_frontier_stress_scout.py"
METRICS_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0017" / "metrics.json"
AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0017" / "agent_run.yaml"


def _load_scout_module():
    spec = importlib.util.spec_from_file_location(
        "run_nuclear_asymmetry_frontier_stress_scout", SCRIPT_PATH
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


def test_asymmetry_frontier_stress_runner_imports_cleanly() -> None:
    module = _load_scout_module()
    assert hasattr(module, "build_metrics")
    assert hasattr(module, "render_report")
    assert module.AGENT_RUN_ID == "AGENT-RUN-0017"
    assert module.TASK_ID == "TASK-0289"


def test_asymmetry_frontier_stress_metrics_recompute() -> None:
    module = _load_scout_module()
    recomputed = module.build_metrics()
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert recomputed["agent_run_id"] == "AGENT-RUN-0017"
    assert recomputed["task_id"] == "TASK-0289"
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
    _assert_nested_close(
        recomputed["lane_recommendation"],
        committed["lane_recommendation"],
    )


def test_asymmetry_frontier_stress_candidate_triage() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    assert metrics["summary"]["generated_candidate_count"] == 9
    assert metrics["summary"]["executed_candidate_count"] == 6
    assert metrics["summary"]["rejected_before_execution_count"] == 3
    assert metrics["summary"]["near_null_control_preserved"] is True


def test_asymmetry_frontier_stress_rejected_have_reasons() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    rejected = metrics["rejected_before_execution"]
    assert len(rejected) == 3
    rejected_ids = {item["candidate_id"] for item in rejected}
    assert rejected_ids == {
        "ASYM-STRESS-007",
        "ASYM-STRESS-008",
        "ASYM-STRESS-009",
    }
    for item in rejected:
        assert "rejection_reason" in item
        assert isinstance(item["rejection_reason"], str)
        assert len(item["rejection_reason"]) > 0


def test_asymmetry_frontier_stress_executed_candidates_produce_deltas() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    executed = metrics["executed_items"]
    assert len(executed) == 6
    expected_ids = {
        "ASYM-STRESS-001",
        "ASYM-STRESS-002",
        "ASYM-STRESS-003",
        "ASYM-STRESS-004",
        "ASYM-STRESS-005",
        "ASYM-STRESS-006",
    }
    assert {item["candidate_id"] for item in executed} == expected_ids

    for item in executed:
        deltas = item["delta_mae_by_subset_mev"]
        for required_subset in (
            "primary",
            "asymmetry_ge_0_25",
            "heavy_a_ge_100",
            "mid_mass",
        ):
            assert required_subset in deltas
            assert deltas[required_subset] is not None
            assert isinstance(deltas[required_subset], float)


def test_asymmetry_frontier_stress_near_null_control_is_zero() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    by_id = {item["candidate_id"]: item for item in metrics["executed_items"]}
    null = by_id["ASYM-STRESS-006"]
    assert null["verdict"] == "INCONCLUSIVE"
    deltas = null["delta_mae_by_subset_mev"]
    for subset, delta in deltas.items():
        if delta is None:
            continue
        assert abs(delta) < 1.0e-12, f"near-null delta on {subset} is {delta}"
    assert null["frontier_contrast_mev"] == 0.0


def test_asymmetry_frontier_stress_overfit_neighbor_is_overfitted() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    by_id = {item["candidate_id"]: item for item in metrics["executed_items"]}
    overfit = by_id["ASYM-STRESS-003"]
    assert overfit["verdict"] == "OVERFITTED"
    assert overfit.get("expected_overfit_neighbor") is True
    primary_delta = overfit["delta_mae_by_subset_mev"]["primary"]
    # Reproduces the NR-SCOUT-005 catastrophic +1.37 MeV blow-up.
    assert primary_delta > 1.0


def test_asymmetry_frontier_stress_sign_inverted_applies_negated_correction() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    by_id = {item["candidate_id"]: item for item in metrics["executed_items"]}
    base = by_id["ASYM-STRESS-001"]
    sign_inverted = by_id["ASYM-STRESS-004"]
    assert sign_inverted.get("sign_inverted") is True
    base_coef = base["fitted_coefficients"]["positive_asymmetry_fraction"]
    sign_coef = sign_inverted["fitted_coefficients"]["positive_asymmetry_fraction"]
    assert sign_coef == pytest.approx(-base_coef, abs=1.0e-12)


def test_asymmetry_frontier_stress_metrics_schema() -> None:
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
        "baseline_metrics_by_subset",
        "lane_recommendation",
        "generated_candidates",
        "executed_items",
        "rejected_before_execution",
        "promotion_boundary",
        "limitations",
    }
    assert required_keys.issubset(metrics.keys())
    assert metrics["sandbox_only"] is True
    assert metrics["live_external_fetch_allowed"] is False
    assert metrics["lane"] == "asymmetry_frontier_adversarial_stress_scout"
    assert "value" in metrics["lane_recommendation"]
    assert "rationale" in metrics["lane_recommendation"]
    assert "evidence_points" in metrics["lane_recommendation"]


def test_asymmetry_frontier_stress_agent_run_manifest() -> None:
    manifest = yaml.safe_load(AGENT_RUN_PATH.read_text(encoding="utf-8"))

    assert manifest["id"] == "AGENT-RUN-0017"
    assert manifest["task_id"] == "TASK-0289"
    assert manifest["campaign_profile_id"] == "nuclear-mass-surface"
    assert manifest["sandbox_only"] is True
    assert manifest["proposal_paths"]["hypothesis"] == str(
        Path("hypothesis_proposals")
        / "nuclear-mass"
        / "HYP-PROPOSAL-0045-asymmetry-frontier-stress-scout-batch.yaml"
    )
    assert manifest["proposal_paths"]["experiment"] == str(
        Path("experiment_proposals")
        / "nuclear-mass"
        / "EXP-PROPOSAL-0011-nuclear-asymmetry-frontier-stress-scout.yaml"
    )
    assert manifest["artifacts"]["metrics"] == str(
        Path("agent_runs") / "AGENT-RUN-0017" / "metrics.json"
    )
    assert manifest["promotion_boundary"]["writes_canonical_result"] is False
    assert manifest["promotion_boundary"]["claim_promotion_allowed"] is False


def test_asymmetry_frontier_stress_promotion_boundary() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert metrics["summary"]["canonical_results_changed"] is False
    assert metrics["summary"]["canonical_claims_changed"] is False
    assert metrics["summary"]["prediction_registry_changed"] is False
    assert metrics["promotion_boundary"]["writes_prediction_registry"] is False
    assert metrics["promotion_boundary"]["writes_canonical_result"] is False
    assert metrics["promotion_boundary"]["claim_promotion_allowed"] is False


def test_asymmetry_frontier_stress_does_not_write_prediction_registry(
    tmp_path: Path,
) -> None:
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


def test_asymmetry_frontier_stress_subset_definitions_match_design() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()
    defs = metrics["subset_definitions"]
    for required in (
        "primary",
        "asymmetry_ge_0_20",
        "asymmetry_ge_0_25",
        "n_z_ge_20",
        "n_z_ge_30",
        "heavy_a_ge_100",
        "mid_mass",
        "light_a_lt_50",
        "ame2020_measured_comparison",
        "ame2020_extrapolated_comparison",
        "frontier_contrast",
    ):
        assert required in defs


def test_asymmetry_frontier_stress_lane_recommendation_is_valid() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    rec = metrics["lane_recommendation"]
    assert rec["value"] in {
        "keep_as_review_surface",
        "demote_to_watchlist",
        "preserve_as_negative_evidence",
    }
    assert isinstance(rec["rationale"], str) and len(rec["rationale"]) > 0
    assert isinstance(rec["evidence_points"], list)
