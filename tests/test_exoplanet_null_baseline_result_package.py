from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "results" / "EXP-0021" / "RUN-0001"
SCRIPT = ROOT / "scripts" / "package_exoplanet_null_baseline_result.py"


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


def test_result_preserves_control_sensitive_and_underpowered_boundaries() -> None:
    metrics = json.loads((RUN_DIR / "metrics.json").read_text(encoding="utf-8"))
    result = yaml.safe_load((RUN_DIR / "result.yaml").read_text(encoding="utf-8"))

    assert result["result_id"] == "RESULT-0027"
    assert result["experiment_id"] == "EXP-0021"
    assert result["hypothesis_id"] == "HYP-0021"
    assert result["best_verdict"] == "INCONCLUSIVE"
    assert result["review_tier"] == "AGENT_PUBLISHED"
    assert result["verification"]["passed"] is True
    assert all(result["agent_proposal_evaluation"]["gates_checked"].values())

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
