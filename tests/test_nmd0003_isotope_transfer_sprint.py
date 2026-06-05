from __future__ import annotations

from scripts.run_nmd0003_isotope_transfer_sprint import run_isotope_transfer_sprint


def test_isotope_transfer_sprint_is_deterministic() -> None:
    first = run_isotope_transfer_sprint()
    second = run_isotope_transfer_sprint()

    assert first == second
    assert first["task_id"] == "TASK-0595"
    assert first["agent_run_id"] == "AGENT-RUN-0063"
    assert first["dataset"]["row_count"] == 2309
    assert first["dataset"]["train_count"] == 1617
    assert first["dataset"]["validation_holdout_count"] == 692


def test_isotope_transfer_sprint_declares_controls_and_forbidden_inputs() -> None:
    metrics = run_isotope_transfer_sprint()
    family = metrics["selected_feature_family"]

    assert family["family_id"] == "neutron_excess_curvature_transfer"
    assert "post_ame2020_values" in family["forbidden_inputs_excluded"]
    assert set(metrics["lanes_primary_readiness_baseline"]) == {
        "candidate_neutron_excess_curvature_transfer",
        "matched_random_chain",
        "sign_inverted",
        "label_shuffle",
    }


def test_isotope_transfer_sprint_reports_chain_panels_and_verdict() -> None:
    metrics = run_isotope_transfer_sprint()
    transfer = metrics["isotope_chain_transfer"]

    assert transfer["summary"]["interpretable_chain_count"] >= 3
    assert transfer["chain_panels"]
    assert all("lanes" in panel for panel in transfer["chain_panels"])
    assert metrics["verdict"] in {
        "BOUNDED_FOLLOWUP_CANDIDATE",
        "DIAGNOSTIC_ONLY",
        "NEGATIVE_RESULT",
        "INCONCLUSIVE",
    }
    assert metrics["output_routing"]["result_impact"] == "no RESULT artifact created"
