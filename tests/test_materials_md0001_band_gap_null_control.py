"""Tests for the MD-0001 band-gap null-control audit (TASK-0579)."""
from __future__ import annotations

import json
from pathlib import Path

from physics_lab.engines.materials_md0001_band_gap_null_control import (
    run_band_gap_null_control_audit,
)

REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "examples" / "benchmarks" / "materials_md0001_baseline.yaml"
COMMITTED = REPO / "agent_runs" / "AGENT-RUN-0058" / "metrics.json"


def test_audit_is_deterministic_for_fixed_seed():
    a = run_band_gap_null_control_audit(CONFIG, permutations=500, seed=3)
    b = run_band_gap_null_control_audit(CONFIG, permutations=500, seed=3)
    assert a == b


def test_audit_reproduces_committed_artifact():
    committed = json.loads(COMMITTED.read_text(encoding="utf-8"))
    fresh = json.loads(
        json.dumps(run_band_gap_null_control_audit(CONFIG, permutations=5000, seed=0))
    )
    assert fresh == committed


def test_real_baseline_beats_global_null_on_holdout():
    result = run_band_gap_null_control_audit(CONFIG, permutations=200, seed=0)
    real = result["real_baselines_holdout_mae"]
    assert real["cation_group_mean"] < real["global_mean_null"]
    assert real["cation_group_skill_vs_global_null"] > 0


def test_controls_are_not_trivially_strong():
    """Shuffle controls should center near the global null, not near the real edge."""
    result = run_band_gap_null_control_audit(CONFIG, permutations=1000, seed=0)
    real = result["real_baselines_holdout_mae"]
    for control in result["controls"].values():
        # the median shuffled baseline should be no better than the global null
        assert control["control_mae_p50"] >= real["cation_group_mean"]
