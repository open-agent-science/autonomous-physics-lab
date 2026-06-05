from __future__ import annotations

from scripts.run_nmd0003_pairing_residual_sprint import run_pairing_residual_sprint


def test_pairing_residual_sprint_is_deterministic() -> None:
    first = run_pairing_residual_sprint()
    second = run_pairing_residual_sprint()

    assert first == second
    assert first["task_id"] == "TASK-0594"
    assert first["agent_run_id"] == "AGENT-RUN-0062"
    assert first["dataset"]["row_count"] == 2309
    assert first["dataset"]["train_count"] == 1617
    assert first["dataset"]["validation_holdout_count"] == 692


def test_pairing_residual_sprint_declares_disjoint_family_and_controls() -> None:
    metrics = run_pairing_residual_sprint()
    family = metrics["selected_feature_family"]

    assert family["family_id"] == "pairing_asymmetry_coupling"
    assert family["family_id"] not in family["disjoint_from_task0517_families"]
    assert family["task0584_family_id"] != family["family_id"]
    assert set(metrics["lanes_primary_readiness_baseline"]) == {
        "candidate_pairing_asymmetry_coupling",
        "matched_random_slice",
        "label_shuffle",
        "same_degree_parity_control",
    }


def test_pairing_residual_sprint_reports_required_surfaces_and_routing() -> None:
    metrics = run_pairing_residual_sprint()
    candidate = metrics["lanes_primary_readiness_baseline"][
        "candidate_pairing_asymmetry_coupling"
    ]

    assert set(candidate["baseline"]) == {
        "train",
        "validation_holdout",
        "full_known",
        "sorted_aZN_diagnostic",
    }
    assert set(metrics["candidate_baseline_comparisons"]) == {
        "region_stratified_readiness",
        "global_ols_audit",
        "inherited_continuity",
    }
    assert metrics["verdict"] in {
        "BOUNDED_FOLLOWUP_CANDIDATE",
        "DIAGNOSTIC_ONLY",
        "NEGATIVE_RESULT",
    }
    assert metrics["output_routing"]["result_impact"] == "no RESULT artifact created"
