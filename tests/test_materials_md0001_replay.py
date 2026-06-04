"""Independent replay guard for the MD-0001 baseline benchmark (TASK-0578).

Re-running the deterministic benchmark engine must reproduce the committed
TASK-0550 result artifact exactly. This locks the published metrics against
silent drift in the engine, dataset, or holdout manifest.
"""
from __future__ import annotations

import json
from pathlib import Path

from physics_lab.engines.materials_md0001_baseline import run_materials_md0001_baseline

REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "examples" / "benchmarks" / "materials_md0001_baseline.yaml"
COMMITTED_METRICS = REPO / "agent_runs" / "AGENT-RUN-0057" / "metrics.json"


def test_engine_reproduces_committed_md0001_metrics():
    committed = json.loads(COMMITTED_METRICS.read_text(encoding="utf-8"))
    # json round-trip normalizes tuples/whitespace so the comparison is structural.
    fresh = json.loads(json.dumps(run_materials_md0001_baseline(CONFIG)))
    assert fresh == committed


def test_committed_band_gap_holdout_is_inconclusive_null_grade():
    """Sanity anchors on the published headline numbers (no claim, just guard)."""
    committed = json.loads(COMMITTED_METRICS.read_text(encoding="utf-8"))
    assert committed["verdict"] == "INCONCLUSIVE"
    band_gap = committed["axis_outputs"]["band_gap"]["best_holdout_baseline"]
    assert band_gap["baseline_id"] == "cation_group_mean"
    assert band_gap["mae"] == 1.247901
