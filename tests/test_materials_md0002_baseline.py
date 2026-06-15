from __future__ import annotations

import json
from pathlib import Path

from physics_lab.engines.materials_md0002_baseline import (
    BASELINE_IDS,
    CONTROL_SEEDS,
    SPLIT_SEEDS,
    run_materials_md0002_formation_energy_benchmark,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_md0002_benchmark_is_deterministic_and_frozen() -> None:
    first = run_materials_md0002_formation_energy_benchmark()
    second = run_materials_md0002_formation_energy_benchmark()
    assert first == second
    assert first["task_id"] == "TASK-0703"
    assert first["dataset_summary"]["property_kind"] == "formation_energy_per_atom"
    assert first["dataset_summary"]["row_count"] == 362
    assert first["dataset_summary"]["split_counts"] == {
        "train": 253,
        "validation": 55,
        "holdout": 54,
    }
    assert first["dataset_summary"]["live_external_fetch"] is False


def test_md0002_benchmark_reports_predeclared_controls_and_splits() -> None:
    metrics = run_materials_md0002_formation_energy_benchmark()
    assert set(metrics["baseline_summaries"]) == set(BASELINE_IDS)
    assert metrics["deterministic_controls"]["seeds"] == list(CONTROL_SEEDS)
    assert metrics["split_sensitivity"]["seeds"] == list(SPLIT_SEEDS)
    assert metrics["deterministic_controls"]["row_order_invariance"]["invariant"] is True
    assert {
        "leave_one_cation_pair_out",
        "leave_one_cation_family_out",
        "leave_one_structure_or_prototype_out",
    } == set(metrics["extrapolation_stress_tests"])


def test_md0002_promotion_assessment_is_mechanical() -> None:
    metrics = run_materials_md0002_formation_energy_benchmark()
    assessment = metrics["promotion_assessment"]
    assert assessment["eligible_for_gate_a"] == all(assessment["gates"].values())
    assert assessment["failed_gates"] == [
        gate for gate, passed in assessment["gates"].items() if not passed
    ]
    assert metrics["verdict"] in {"VALID_IN_RANGE", "INCONCLUSIVE"}
    assert metrics["output_routing"]["claim_impact"] == "no claim change"


def test_md0002_committed_metrics_match_deterministic_replay() -> None:
    committed = json.loads(
        (REPO_ROOT / "agent_runs/AGENT-RUN-0072/metrics.json").read_text(
            encoding="utf-8"
        )
    )
    assert committed == run_materials_md0002_formation_energy_benchmark()
