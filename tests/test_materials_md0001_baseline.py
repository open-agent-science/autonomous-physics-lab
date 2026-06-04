from __future__ import annotations

from pathlib import Path

from physics_lab.engines.materials_md0001_baseline import run_materials_md0001_baseline


CONFIG = Path("examples/benchmarks/materials_md0001_baseline.yaml")


def test_materials_md0001_baseline_is_deterministic() -> None:
    first = run_materials_md0001_baseline(CONFIG)
    second = run_materials_md0001_baseline(CONFIG)
    assert first == second


def test_materials_md0001_baseline_keeps_axes_and_nulls_separate() -> None:
    metrics = run_materials_md0001_baseline(CONFIG)
    assert metrics["task_id"] == "TASK-0550"
    assert metrics["verdict"] == "INCONCLUSIVE"
    assert set(metrics["axis_outputs"]) == {"formation_energy_per_atom", "band_gap"}

    for axis in metrics["axis_outputs"].values():
        assert axis["row_count"] == 169
        assert axis["split_counts"] == {"train": 119, "validation": 17, "holdout": 33}
        assert set(axis["baseline_summaries"]) == {
            "global_mean",
            "global_median",
            "cation_group_mean",
        }
        for baseline in axis["baseline_summaries"].values():
            assert baseline["metrics"]["holdout"]["count"] == 33
            assert baseline["metrics"]["holdout"]["mae"] >= 0.0
            assert {
                "cation_group",
                "formula_family",
                "spacegroup_bucket",
                "property_range",
            } <= set(baseline["subset_metrics"])

    assert (
        metrics["axis_outputs"]["formation_energy_per_atom"]["units"]
        != metrics["axis_outputs"]["band_gap"]["units"]
    )
