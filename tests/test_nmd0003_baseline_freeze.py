from __future__ import annotations

from pathlib import Path

from physics_lab.engines.nmd0003_baseline_freeze import run_nmd0003_baseline_freeze


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "examples" / "benchmarks" / "nuclear_mass_baseline_nmd0003.yaml"


def test_nmd0003_baseline_freeze_is_deterministic() -> None:
    first = run_nmd0003_baseline_freeze(CONFIG)
    second = run_nmd0003_baseline_freeze(CONFIG)

    assert first == second
    assert first["task_id"] == "TASK-0531"
    assert first["dataset_summary"]["row_count"] == 2309
    assert first["dataset_summary"]["train_count"] == 1616
    assert first["dataset_summary"]["validation_holdout_count"] == 693
    assert first["dataset_summary"]["post_ame2020_holdout_excluded"] is True


def test_nmd0003_broad_surface_fit_reports_train_full_and_validation_behavior() -> None:
    metrics = run_nmd0003_baseline_freeze(CONFIG)
    comparison = metrics["comparison"]

    assert comparison["train"]["mae_relative_improvement"] > 0.0
    assert comparison["full_nmd0003_training_surface"]["mae_relative_improvement"] > 0.0
    assert comparison["validation_holdout"]["mae_relative_improvement"] < 0.0
    assert metrics["verdict"] == "INCONCLUSIVE"
    assert "worsens the predeclared validation holdout" in metrics["task0517_interpretation_update"]
    assert "a_range" in metrics["baseline_summaries"]["nmd0003_train_fitted_frozen"]["subset_metrics"]
    assert "magic_distance" in metrics["baseline_summaries"]["nmd0003_train_fitted_frozen"]["subset_metrics"]
