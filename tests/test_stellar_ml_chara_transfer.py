"""Regression tests for TASK-1050 CHARA no-refit transfer."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

from physics_lab.engines.stellar_ml_chara_transfer import (
    ALPHA_FROZEN,
    MINIMUM_EFFECTIVE_GROUPS,
    SURVIVAL_MARGIN_DEX,
    compute_chara_transfer_metrics,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "stellar_ml_chara_fixed_relation_transfer.yaml"


def test_chara_transfer_is_deterministic_and_frozen() -> None:
    first = compute_chara_transfer_metrics()
    second = compute_chara_transfer_metrics()
    assert first == second
    assert ALPHA_FROZEN == 4.526004
    assert first["frozen_contract"]["refit_on_chara"] is False
    assert first["frozen_contract"]["selection_after_metrics"] is False
    assert first["null_training"]["target_rows_used_for_null"] == 0
    assert first["null_training"]["train_count"] == 102


def test_exact_surface_grouping_and_source_replay_are_preserved() -> None:
    metrics = compute_chara_transfer_metrics()
    source = metrics["source_integrity"]
    assert source["source_replay_verdict"] == "INDEPENDENT_SOURCE_REPLAY_PASS"
    assert source["component_count"] == 12
    assert source["system_count"] == 6
    assert source["effective_group_count"] == 6
    assert source["effective_group_count"] >= MINIMUM_EFFECTIVE_GROUPS == 5
    assert source["melotte_25_rows_admitted"] == 0
    assert all(
        diagnostic["component_count"] == 2
        for diagnostic in metrics["per_system_diagnostics"].values()
    )


def test_numeric_outcome_is_inconclusive_without_rescue_fit() -> None:
    metrics = compute_chara_transfer_metrics()
    assert metrics["candidate_mae_dex"] == 0.06053
    assert metrics["models"]["control_textbook_alpha_3p5"]["mae_dex"] == 0.223985
    assert metrics["models"]["control_textbook_alpha_4p0"]["mae_dex"] == 0.097317
    assert (
        metrics["models"]["control_result0022_massband_median_null"]["mae_dex"]
        == 0.621336
    )
    assert metrics["best_control"] == "control_textbook_alpha_4p0"
    assert metrics["margin_over_best_control_dex"] == 0.036787
    assert SURVIVAL_MARGIN_DEX == 0.04
    assert metrics["clears_survival_margin"] is False
    assert metrics["verdict"] == "INCONCLUSIVE"


def test_system_sensitivity_is_reported_as_six_group_deletions() -> None:
    metrics = compute_chara_transfer_metrics()
    sensitivity = metrics["leave_one_effective_group_out"]
    assert len(sensitivity) == 6
    assert {item["remaining_group_count"] for item in sensitivity} == {5}
    assert metrics["leave_one_group_margin_min_dex"] == 0.021022
    assert metrics["leave_one_group_margin_max_dex"] == 0.065474


def test_workflow_writes_gate_a_replayable_package(tmp_path: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "physics_lab.cli",
            "run",
            str(EXAMPLE),
            "--output-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    run_dir = tmp_path / "EXP-0023" / "RUN-0001"
    result = yaml.safe_load((run_dir / "result.yaml").read_text(encoding="utf-8"))
    assert result["result_id"] == "RESULT-0031"
    assert result["task_id"] == "TASK-1050"
    assert result["review_tier"] == "AGENT_PUBLISHED"
    assert result["best_verdict"] == "INCONCLUSIVE"
    assert result["command"] == (
        "physics-lab run examples/stellar_ml_chara_fixed_relation_transfer.yaml"
    )
    assert result["verification"]["passed"] is True
    assert result["comparison_summary"][0]["observed_value"] == 0.036787
    assert set(result["input_file_hashes"]) == {
        "config",
        "experiment",
        "hypothesis",
        "task",
        "fixture",
    }
    assert (run_dir / "gate_a_report.md").exists()
