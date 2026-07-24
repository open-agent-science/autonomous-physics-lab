"""Tests for TASK-1066 and RESULT-0032."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

from physics_lab.engines.materials_oqmd_baseline import (
    run_oqmd_within_source_benchmark,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "materials_oqmd_within_source_baseline.yaml"


def test_frozen_oqmd_benchmark_is_deterministic_and_preserves_fail() -> None:
    first = run_oqmd_within_source_benchmark()
    second = run_oqmd_within_source_benchmark()

    assert first == second
    assert first["verdict"] == "FAIL"
    assert first["partition_counts"] == {"train": 120, "validation": 26, "holdout": 26}
    assert first["composition_leakage"] == []
    assert first["row_order_invariance"]["passes"] is True


def test_frozen_metrics_and_control_failure_are_exact() -> None:
    metrics = run_oqmd_within_source_benchmark()
    fixed = metrics["fixed_split"]
    candidate = fixed["model_metrics"]["candidate"]["holdout"]
    group_null = fixed["model_metrics"]["iupac_group_pair_null"]["holdout"]

    assert candidate["mae"] == 0.308533591392
    assert candidate["rmse"] == 0.454728159583
    assert candidate["unseen_group_count"] == 5
    assert group_null["mae"] == 0.154250620789
    assert fixed["survival_gate"]["all_comparators_pass"] is False
    assert metrics["sensitivity"]["all_seeds_pass"] is False
    assert [row["all_comparators_pass"] for row in metrics["sensitivity"]["per_seed"]] == [
        False,
        False,
        False,
        False,
        False,
    ]
    assert len(metrics["failure_cases"]) == 26


def test_cli_writes_gate_a_candidate_with_fail_to_invalid_routing(tmp_path: Path) -> None:
    subprocess.run(
        [sys.executable, "-m", "physics_lab.cli", "run", str(EXAMPLE), "--output-dir", str(tmp_path)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result = yaml.safe_load(
        (tmp_path / "EXP-0024" / "RUN-0001" / "result.yaml").read_text(encoding="utf-8")
    )
    assert result["result_id"] == "RESULT-0032"
    assert result["review_tier"] == "AGENT_PUBLISHED"
    assert result["best_verdict"] == "INVALID"
    assert result["verification"]["passed"] is True
    assert result["agent_proposal_evaluation"]["published_by"]["github_username"] == "akutenyov"
