from __future__ import annotations

from scripts.run_nuclear_f2_controls_first_scoring import (
    run_f2_controls_first_scoring,
)


def test_f2_controls_first_scoring_is_deterministic() -> None:
    first = run_f2_controls_first_scoring()
    second = run_f2_controls_first_scoring()

    assert first == second
    assert first["task_id"] == "TASK-0553"
    assert first["dataset"]["row_count"] == 2309
    assert first["dataset"]["train_count"] == 1617
    assert first["dataset"]["validation_holdout_count"] == 692


def test_f2_controls_first_scoring_runs_required_controls() -> None:
    metrics = run_f2_controls_first_scoring()

    assert metrics["controls_first_contract"]["f2_eligibility"] == "diagnostic_only"
    assert set(metrics["controls_first_contract"]["controls"]) == {
        "matched_random",
        "smooth_a",
        "asymmetry_only",
        "cluster_label_shuffle",
    }
    assert metrics["decision"]["candidate_minus_best_control_full_known_mae_improvement_mev"] < (
        metrics["controls_first_contract"]["survival_margin_mev"]
    )
    assert metrics["verdict"] in {
        "BOUNDED_FOLLOWUP_CANDIDATE_DIAGNOSTIC_ONLY",
        "DIAGNOSTIC_ONLY_CONTROL_DOMINATED",
        "NEGATIVE_RESULT",
    }
