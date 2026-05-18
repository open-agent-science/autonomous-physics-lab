"""Reproducibility tests for AGENT-RUN-0016 shell-axis adversarial stress scout."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_nuclear_shell_axis_stress_scout.py"
METRICS_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0016" / "metrics.json"
AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / "AGENT-RUN-0016" / "agent_run.yaml"


def _load_scout_module():
    spec = importlib.util.spec_from_file_location(
        "run_nuclear_shell_axis_stress_scout", SCRIPT_PATH
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


def test_shell_axis_stress_runner_imports_cleanly() -> None:
    module = _load_scout_module()
    assert hasattr(module, "build_metrics")
    assert hasattr(module, "render_report")
    assert module.AGENT_RUN_ID == "AGENT-RUN-0016"
    assert module.TASK_ID == "TASK-0288"


def test_shell_axis_stress_metrics_recompute() -> None:
    module = _load_scout_module()
    recomputed = module.build_metrics()
    committed = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert recomputed["agent_run_id"] == "AGENT-RUN-0016"
    assert recomputed["task_id"] == "TASK-0288"
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
        recomputed["repeated_target_pressure"],
        committed["repeated_target_pressure"],
    )


def test_shell_axis_stress_candidate_triage() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    assert metrics["summary"]["generated_candidate_count"] == 9
    assert metrics["summary"]["executed_candidate_count"] == 6
    assert metrics["summary"]["rejected_before_execution_count"] == 3
    assert metrics["summary"]["near_null_control_preserved"] is True


def test_shell_axis_stress_rejected_have_reasons() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    rejected = metrics["rejected_before_execution"]
    assert len(rejected) == 3
    rejected_ids = {item["candidate_id"] for item in rejected}
    assert rejected_ids == {
        "STRESS-SHELL-007",
        "STRESS-SHELL-008",
        "STRESS-SHELL-009",
    }
    for item in rejected:
        assert "rejection_reason" in item
        assert isinstance(item["rejection_reason"], str)
        assert len(item["rejection_reason"]) > 0


def test_shell_axis_stress_executed_candidates_produce_deltas() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    executed = metrics["executed_items"]
    assert len(executed) == 6
    expected_ids = {
        "STRESS-SHELL-001",
        "STRESS-SHELL-002",
        "STRESS-SHELL-003",
        "STRESS-SHELL-004",
        "STRESS-SHELL-005",
        "STRESS-SHELL-006",
    }
    assert {item["candidate_id"] for item in executed} == expected_ids

    for item in executed:
        deltas = item["delta_mae_by_subset_mev"]
        for required_subset in ("primary", "magic_z", "magic_n", "heavy_a_ge_100"):
            assert required_subset in deltas
            assert deltas[required_subset] is not None
            assert isinstance(deltas[required_subset], float)


def test_shell_axis_stress_near_null_control_is_zero() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    by_id = {item["candidate_id"]: item for item in metrics["executed_items"]}
    null = by_id["STRESS-SHELL-006"]
    assert null["verdict"] == "INCONCLUSIVE"
    deltas = null["delta_mae_by_subset_mev"]
    for subset, delta in deltas.items():
        if delta is None:
            continue
        assert abs(delta) < 1.0e-12, f"near-null delta on {subset} is {delta}"
    assert null["frontier_contrast_mev"] == 0.0


def test_shell_axis_stress_sign_inverted_applies_negated_correction() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    by_id = {item["candidate_id"]: item for item in metrics["executed_items"]}
    proton_only = by_id["STRESS-SHELL-001"]
    sign_inverted = by_id["STRESS-SHELL-004"]
    assert sign_inverted.get("sign_inverted") is True

    proton_beta = proton_only["fitted_coefficients"]["s_z2"]
    inverted_beta = sign_inverted["fitted_coefficients"]["s_z2"]
    assert inverted_beta == pytest.approx(-proton_beta, abs=1.0e-12, rel=0.0)


def test_shell_axis_stress_metrics_schema() -> None:
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
        "repeated_target_pressure",
        "generated_candidates",
        "executed_items",
        "rejected_before_execution",
        "promotion_boundary",
        "limitations",
    }
    assert required_keys.issubset(metrics.keys())
    assert metrics["sandbox_only"] is True
    assert metrics["live_external_fetch_allowed"] is False
    assert metrics["lane"] == "shell_axis_adversarial_stress_scout"


def test_shell_axis_stress_agent_run_manifest() -> None:
    manifest = yaml.safe_load(AGENT_RUN_PATH.read_text(encoding="utf-8"))

    assert manifest["id"] == "AGENT-RUN-0016"
    assert manifest["task_id"] == "TASK-0288"
    assert manifest["campaign_profile_id"] == "nuclear-mass-surface"
    assert manifest["sandbox_only"] is True
    assert manifest["proposal_paths"]["hypothesis"] == str(
        Path("hypothesis_proposals")
        / "nuclear-mass"
        / "HYP-PROPOSAL-0044-shell-axis-stress-scout-batch.yaml"
    )
    assert manifest["proposal_paths"]["experiment"] == str(
        Path("experiment_proposals")
        / "nuclear-mass"
        / "EXP-PROPOSAL-0010-nuclear-shell-axis-stress-scout.yaml"
    )
    assert manifest["artifacts"]["metrics"] == str(
        Path("agent_runs") / "AGENT-RUN-0016" / "metrics.json"
    )
    assert manifest["promotion_boundary"]["writes_canonical_result"] is False
    assert manifest["promotion_boundary"]["claim_promotion_allowed"] is False


def test_shell_axis_stress_promotion_boundary() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    assert metrics["summary"]["canonical_results_changed"] is False
    assert metrics["summary"]["canonical_claims_changed"] is False
    assert metrics["summary"]["prediction_registry_changed"] is False
    assert metrics["promotion_boundary"]["writes_prediction_registry"] is False
    assert metrics["promotion_boundary"]["writes_canonical_result"] is False
    assert metrics["promotion_boundary"]["claim_promotion_allowed"] is False
    assert metrics["promotion_boundary"]["writes_knowledge"] is False


def test_shell_axis_stress_does_not_write_prediction_registry(tmp_path: Path) -> None:
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


def test_shell_axis_stress_subset_definitions_match_design() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()
    defs = metrics["subset_definitions"]
    for required in (
        "primary",
        "ame2020_measured_comparison",
        "ame2020_extrapolated_comparison",
        "magic_any",
        "magic_z",
        "magic_n",
        "double_magic",
        "near_magic",
        "heavy_a_ge_100",
        "mid_mass",
        "light_a_lt_50",
        "neutron_rich_high",
        "registry_repeat_target",
        "registry_repeat_chain_neighbor",
        "frontier_contrast",
    ):
        assert required in defs


def test_shell_axis_stress_repeated_target_pressure_holdout_overlap_is_zero() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    pressure = metrics["repeated_target_pressure"]
    overlap = pressure["holdout_target_overlap"]
    for nuclide_id in ("Ni-76", "Ca-55", "Ga-85", "Zn-80"):
        assert nuclide_id in overlap
        assert overlap[nuclide_id] is False, (
            f"overrepresented target {nuclide_id} unexpectedly appeared in the holdout"
        )

    overrepresented = pressure["overrepresented_registry_targets"]
    assert {item["nuclide_id"] for item in overrepresented} == {
        "Ni-76",
        "Ca-55",
        "Ga-85",
        "Zn-80",
    }


def test_shell_axis_stress_chain_neighbor_rows_match_expected() -> None:
    module = _load_scout_module()
    metrics = module.build_metrics()

    pressure = metrics["repeated_target_pressure"]
    rows = pressure["holdout_chain_neighbor_rows"]
    nuclide_ids = {row["nuclide_id"] for row in rows}
    assert nuclide_ids == {"Ni-74", "Ni-75", "Ca-54", "Ga-83", "Ga-84", "Zn-79"}
    assert len(rows) == 6
