from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "results" / "EXP-0021" / "RUN-0001"
SCRIPT = ROOT / "scripts" / "package_exoplanet_null_baseline_result.py"
EXAMPLE = ROOT / "examples" / "exoplanet_null_baseline_result.yaml"


def test_result_package_reproduces_byte_for_byte(tmp_path: Path) -> None:
    result = yaml.safe_load((RUN_DIR / "result.yaml").read_text(encoding="utf-8"))
    replay_dir = tmp_path / "replay"
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--output-dir",
            str(replay_dir),
            "--git-commit",
            result["git_commit"],
            "--write",
        ],
        cwd=ROOT,
        check=True,
    )

    expected_files = sorted(path.relative_to(RUN_DIR) for path in RUN_DIR.rglob("*") if path.is_file())
    replay_files = sorted(path.relative_to(replay_dir) for path in replay_dir.rglob("*") if path.is_file())
    assert replay_files == expected_files
    for relative in expected_files:
        assert (replay_dir / relative).read_bytes() == (RUN_DIR / relative).read_bytes()


def test_gate_b_safe_workflow_reproduces_result(tmp_path: Path) -> None:
    replay_root = tmp_path / "workflow-replay"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "physics_lab.cli",
            "run",
            str(EXAMPLE),
            "--output-dir",
            str(replay_root),
        ],
        cwd=ROOT,
        check=True,
    )

    replay_dir = replay_root / "EXP-0021" / "RUN-0001"
    expected_files = sorted(path.relative_to(RUN_DIR) for path in RUN_DIR.rglob("*") if path.is_file())
    replay_files = sorted(path.relative_to(replay_dir) for path in replay_dir.rglob("*") if path.is_file())
    assert replay_files == expected_files
    assert (replay_dir / "result.yaml").read_bytes() == (RUN_DIR / "result.yaml").read_bytes()
    assert (replay_dir / "metrics.json").read_bytes() == (RUN_DIR / "metrics.json").read_bytes()


def test_result_preserves_control_sensitive_and_underpowered_boundaries() -> None:
    metrics = json.loads((RUN_DIR / "metrics.json").read_text(encoding="utf-8"))
    result = yaml.safe_load((RUN_DIR / "result.yaml").read_text(encoding="utf-8"))

    assert result["result_id"] == "RESULT-0027"
    assert result["experiment_id"] == "EXP-0021"
    assert result["hypothesis_id"] == "HYP-0021"
    assert result["best_verdict"] == "INCONCLUSIVE"
    assert result["review_tier"] == "AGENT_VALIDATED"
    assert result["command"] == "physics-lab run examples/exoplanet_null_baseline_result.yaml"
    assert result["code_reference"] == "physics_lab/workflows/exoplanet_null_baseline_result.py"
    assert result["verification"]["passed"] is True
    assert all(result["agent_proposal_evaluation"]["gates_checked"].values())
    validation_record = result["agent_proposal_evaluation"]["validation_record"]
    assert validation_record["validation_independence"] == "independent"
    assert validation_record["helper_status"] == "PASS"
    assert validation_record["metric_count"] == 52

    assert len(metrics["true_mass_slices"]) == 4
    assert all(
        row["classification"] == "null_family_matches_or_beats_ck17"
        and row["best_null_baseline"] == "nearest_radius_neighbor"
        and row["nearest_radius_null_rmse_dex"] < row["ck17_frozen_rmse_dex"]
        for row in metrics["true_mass_slices"].values()
    )
    assert all(
        row["classification"] == "underpowered_slice"
        for row in metrics["minimum_mass_diagnostics"].values()
    )


def test_result_surfaces_fair_null_comparisons() -> None:
    result = yaml.safe_load((RUN_DIR / "result.yaml").read_text(encoding="utf-8"))
    report = (RUN_DIR / "report.md").read_text(encoding="utf-8")
    comparison_by_id = {row["target_id"]: row for row in result["comparison_summary"]}

    assert len(result["comparison_summary"]) == 12
    nearest_mass = comparison_by_id["target_compact_radius_lt1p5re_nearest_mass_neighbor"]
    assert nearest_mass["observed_value"] == 0.28322440879329114
    assert nearest_mass["reference_value"] == 0.2633500276766559
    assert "fair-null row" in nearest_mass["notes"]

    per_class = comparison_by_id["target_sub_neptune_radius_1p5_4re_per_class_median"]
    assert per_class["observed_value"] == 0.17317295090168003
    assert per_class["observed_value"] < per_class["reference_value"]

    nearest_radius = comparison_by_id["target_jovian_radius_8_16re_null_control"]
    assert "diagnostic control" in nearest_radius["notes"]
    assert "not a prospective predictor" in nearest_radius["notes"]

    assert "Fair-null comparators" in report
    assert "three of four highlighted true-mass slices" in report
    assert "not a deployable predictor" in report
