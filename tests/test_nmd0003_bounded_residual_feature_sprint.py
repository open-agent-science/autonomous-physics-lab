from __future__ import annotations

from scripts.run_nmd0003_bounded_residual_feature_sprint import (
    run_bounded_residual_feature_sprint,
)


def test_bounded_residual_feature_sprint_is_deterministic() -> None:
    first = run_bounded_residual_feature_sprint()
    second = run_bounded_residual_feature_sprint()

    assert first == second
    assert first["task_id"] == "TASK-0584"
    assert first["dataset"]["row_count"] == 2309
    assert first["dataset"]["train_count"] == 1617
    assert first["dataset"]["validation_holdout_count"] == 692


def test_bounded_residual_feature_sprint_uses_disjoint_family_and_controls() -> None:
    metrics = run_bounded_residual_feature_sprint()

    family = metrics["selected_feature_family"]
    assert family["family_id"] == "coulomb_surface_interaction"
    assert family["family_id"] not in family["disjoint_from_task0517_families"]
    assert set(metrics["lanes_primary_readiness_baseline"]) == {
        "candidate_coulomb_surface_interaction",
        "matched_random_slice",
        "label_shuffle",
        "smooth_control",
    }
    assert metrics["verdict"] in {
        "BOUNDED_FOLLOWUP_CANDIDATE",
        "INCONCLUSIVE_CONTROL_DOMINATED",
        "NEGATIVE_RESULT",
    }
