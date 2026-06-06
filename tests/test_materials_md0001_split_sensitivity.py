from __future__ import annotations

from physics_lab.engines.materials_md0001_split_sensitivity import (
    run_materials_md0001_split_sensitivity_audit,
)


def test_audit_is_deterministic() -> None:
    first = run_materials_md0001_split_sensitivity_audit()
    second = run_materials_md0001_split_sensitivity_audit()
    assert first == second
    assert first["task_id"] == "TASK-0601"
    assert first["verdict"] == "INCONCLUSIVE"


def test_axis_row_counts_and_committed_reference() -> None:
    metrics = run_materials_md0001_split_sensitivity_audit()
    for axis in ("formation_energy_per_atom", "band_gap"):
        axis_out = metrics["axis_outputs"][axis]
        assert axis_out["row_count"] == 169
        # Both axes' committed holdout winner is cation_group_mean (AGENT-RUN-0057).
        assert (
            axis_out["committed_reference"]["best_holdout_baseline"]["baseline_id"]
            == "cation_group_mean"
        )


def test_formation_energy_conclusion_is_split_robust() -> None:
    metrics = run_materials_md0001_split_sensitivity_audit()
    axis_out = metrics["axis_outputs"]["formation_energy_per_atom"]
    robustness = axis_out["split_robustness"]
    assert robustness["verdict"] == "split_robust"
    # cation_group_mean wins all five seeded random holdouts by a wide margin.
    assert (
        axis_out["seeded_random_70_30"]["per_baseline"]["cation_group_mean"][
            "seed_win_count"
        ]
        == 5
    )
    assert robustness["margin_exceeds_noise"] is True
    assert metrics["overall_split_robustness"]["formation_energy_per_atom"] == "split_robust"


def test_band_gap_conclusion_is_split_sensitive() -> None:
    metrics = run_materials_md0001_split_sensitivity_audit()
    axis_out = metrics["axis_outputs"]["band_gap"]
    robustness = axis_out["split_robustness"]
    assert robustness["verdict"] == "split_sensitive"
    # The committed-split holdout winner wins only a bare majority of seeds and
    # its margin over the runner-up does not exceed the across-seed noise.
    assert robustness["winner_seed_win_count"] == 3
    assert robustness["margin_exceeds_noise"] is False
    assert metrics["overall_split_robustness"]["band_gap"] == "split_sensitive"


def test_leave_one_cation_group_out_degenerates_to_global_mean() -> None:
    metrics = run_materials_md0001_split_sensitivity_audit()
    for axis in ("formation_energy_per_atom", "band_gap"):
        macro = metrics["axis_outputs"][axis]["leave_one_cation_group_out"][
            "macro_holdout_mae"
        ]
        # A fully held-out cation group has no train rows, so cation_group_mean
        # falls back to the global mean and matches it exactly.
        assert macro["cation_group_mean"] == macro["global_mean"]
