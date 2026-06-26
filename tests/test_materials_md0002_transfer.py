from __future__ import annotations

import json
from pathlib import Path

from physics_lab.engines.materials_md0002_transfer import (
    AGENT_RUN_ID,
    CONTROL_IDS,
    CONTROL_SEEDS,
    FAMILY_ALKALI_TRANSITION,
    FAMILY_ALKALINE_EARTH_TRANSITION,
    FROZEN_MODEL_ID,
    MIN_TRANSFER_MARGIN_EV_PER_ATOM,
    TRANSFER_DIRECTIONS,
    run_materials_md0002_transfer_benchmark,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_transfer_benchmark_is_deterministic_and_frozen() -> None:
    first = run_materials_md0002_transfer_benchmark()
    second = run_materials_md0002_transfer_benchmark()
    assert first == second
    assert first["task_id"] == "TASK-0838"
    assert first["agent_run_id"] == AGENT_RUN_ID
    assert first["frozen_model_under_test"]["model_id"] == FROZEN_MODEL_ID
    assert first["frozen_model_under_test"]["frozen_before_reading_transfer_error"] is True
    assert (
        first["frozen_model_under_test"]["post_hoc_descriptor_or_hyperparameter_change"]
        is False
    )
    assert first["dataset_summary"]["property_kind"] == "formation_energy_per_atom"
    assert first["dataset_summary"]["provenance_class"] == "computed_dft"
    assert first["dataset_summary"]["license"] == "CC_BY_4_0"
    assert first["dataset_summary"]["live_external_fetch"] is False


def test_transfer_benchmark_uses_disjoint_total_family_partition() -> None:
    metrics = run_materials_md0002_transfer_benchmark()
    counts = metrics["dataset_summary"]["family_counts"]
    # Matches the TASK-0817 scout's deterministic row read (225 / 137, exhaustive).
    assert counts == {
        FAMILY_ALKALI_TRANSITION: 225,
        FAMILY_ALKALINE_EARTH_TRANSITION: 137,
    }
    assert counts[FAMILY_ALKALI_TRANSITION] + counts[FAMILY_ALKALINE_EARTH_TRANSITION] == (
        metrics["dataset_summary"]["row_count"]
    )
    # Both holdout directions are evaluated, and the families share no cation pair,
    # so every held-out row falls back to the global train mean by construction.
    direction_ids = {d["direction_id"] for d in metrics["transfer_directions"]}
    assert direction_ids == {d["direction_id"] for d in TRANSFER_DIRECTIONS}
    for direction in metrics["transfer_directions"]:
        assert direction["shared_cation_pairs_between_families"] == []
        assert (
            direction["holdout_rows_falling_back_to_global_mean"]
            == direction["holdout_count"]
        )


def test_transfer_benchmark_predeclares_controls_and_margin() -> None:
    metrics = run_materials_md0002_transfer_benchmark()
    pf = metrics["predeclared_pass_fail"]
    assert pf["declared_before_metric_computation"] is True
    assert tuple(pf["controls"]) == CONTROL_IDS
    assert pf["control_seeds"] == list(CONTROL_SEEDS)
    assert (
        pf["minimum_margin_over_best_control_eV_per_atom"]
        == MIN_TRANSFER_MARGIN_EV_PER_ATOM
    )
    # Margin bookkeeping is mechanical and consistent in every direction.
    for direction in metrics["transfer_directions"]:
        best_control_mae = min(
            control["holdout_mae"] for control in direction["controls"].values()
        )
        assert direction["best_control_holdout_mae"] == best_control_mae
        expected_margin = round(
            best_control_mae - direction["frozen_model_holdout_mae"], 6
        )
        assert direction["margin_over_best_control_eV_per_atom"] == expected_margin
        assert direction["clears_margin_over_best_control"] == (
            expected_margin >= MIN_TRANSFER_MARGIN_EV_PER_ATOM
        )


def test_transfer_benchmark_records_family_localized_negative() -> None:
    metrics = run_materials_md0002_transfer_benchmark()
    # The frozen cation-pair advantage does not transfer across the disjoint family;
    # the honest negative is recorded rather than rescued.
    assert metrics["verdict"] == "SANDBOX_FAIL"
    assert (
        metrics["transfer_summary"]["transfer_outcome"] == "advantage_is_family_localized"
    )
    assert metrics["transfer_summary"]["transfers_in_all_directions"] is False
    assert metrics["output_routing"]["claim_impact"] == "no claim change"
    assert metrics["output_routing"]["knowledge_impact"] == "no knowledge change"


def test_committed_metrics_match_deterministic_replay() -> None:
    committed = json.loads(
        (REPO_ROOT / "agent_runs/AGENT-RUN-0081/metrics.json").read_text(
            encoding="utf-8"
        )
    )
    assert committed == run_materials_md0002_transfer_benchmark()
