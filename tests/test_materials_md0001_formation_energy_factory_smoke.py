from __future__ import annotations

from scripts.run_materials_md0001_formation_energy_factory_smoke import (
    run_materials_factory_smoke_sprint,
)


def test_materials_factory_smoke_is_bounded_and_formation_energy_only() -> None:
    metrics = run_materials_factory_smoke_sprint()

    assert metrics["task_id"] == "TASK-0626"
    assert metrics["factory_contract"]["executed_candidate_count"] <= 12
    assert metrics["factory_contract"]["target_axis"] == "formation_energy_per_atom"
    assert metrics["factory_contract"]["excluded_axis"] == "band_gap"
    assert metrics["dataset"]["split_counts"] == {"train": 119, "validation": 17, "holdout": 33}


def test_materials_factory_smoke_keeps_diagnostic_only_routing() -> None:
    metrics = run_materials_factory_smoke_sprint()

    assert metrics["outcome"]["classification"] in {
        "NEGATIVE",
        "DIAGNOSTIC_ONLY",
        "REPLAY_NEEDED",
    }
    assert metrics["output_routing"]["result_impact"] == "no RESULT artifact created"
    assert metrics["output_routing"]["claim_impact"] == "none"
    assert set(metrics["controls"]) == {
        "label_shuffle_control",
        "cation_group_shuffle_control",
        "matched_random_formula_family_control",
    }
