from __future__ import annotations

import json
from pathlib import Path

from physics_lab.engines.nuclear_f2_independent_replay import (
    run_nuclear_f2_independent_replay,
)


def test_replay_is_deterministic_and_matches_committed_run() -> None:
    first = run_nuclear_f2_independent_replay()
    second = run_nuclear_f2_independent_replay()
    assert first == second
    assert first["task_id"] == "TASK-0612"
    assert first["replay_verdict"] == "REPLAY_MATCH"
    check = first["replay_check"]
    assert check["full_metrics_deep_equal"] is True
    assert check["candidate_surface_metrics_match"] is True
    assert check["mismatch_count"] == 0


def test_candidate_surface_metrics_reproduce_committed_values() -> None:
    metrics = run_nuclear_f2_independent_replay()
    surfaces = metrics["replay_check"]["candidate_surface_verification"]
    # The committed AGENT-RUN-0060 candidate surfaces.
    assert surfaces["full_known"]["committed"]["baseline_mae_mev"] == 1.845344
    assert surfaces["full_known"]["committed"]["corrected_mae_mev"] == 1.644933
    for surface in ("train_loo", "validation_holdout", "full_known"):
        assert surfaces[surface]["matches"] is True


def test_control_ledger_records_diagnostic_only_decision() -> None:
    ledger = run_nuclear_f2_independent_replay()["control_ledger"]
    assert ledger["best_control_id"] == "asymmetry_only"
    assert ledger["candidate_full_known_mae_improvement_mev"] == 0.200411
    assert ledger["best_control_full_known_mae_improvement_mev"] == 0.001151
    assert ledger["survival_margin_rule_mev"] == 0.25
    assert ledger["candidate_minus_best_control_mev"] == 0.19926
    assert ledger["survival_margin_clears"] is False
    assert ledger["f2_scoring_verdict"] == "DIAGNOSTIC_ONLY_CONTROL_DOMINATED"
    assert set(ledger["controls"]) == {
        "matched_random",
        "smooth_a",
        "asymmetry_only",
        "cluster_label_shuffle",
    }


def test_replay_mismatch_blocks_and_does_not_interpret(tmp_path: Path) -> None:
    committed = json.loads(
        (
            Path(__file__).resolve().parents[1]
            / "agent_runs"
            / "AGENT-RUN-0060"
            / "metrics.json"
        ).read_text(encoding="utf-8")
    )
    # Tamper one committed surface value so the replay can no longer reproduce it.
    committed["lanes"]["candidate_f2_finer_taxonomy"]["baseline"]["full_known"][
        "mae_mev"
    ] = 9.999999
    tampered = tmp_path / "metrics.json"
    tampered.write_text(json.dumps(committed), encoding="utf-8")

    result = run_nuclear_f2_independent_replay(committed_metrics_path=tampered)
    assert result["replay_verdict"] == "BLOCKED_REPLAY_MISMATCH"
    assert result["replay_check"]["mismatch_count"] >= 1
    # Stop before interpretation: no control-ledger decision is emitted.
    assert result["control_ledger"]["status"] == "not_interpreted_due_to_replay_mismatch"
    assert "best_control_id" not in result["control_ledger"]
