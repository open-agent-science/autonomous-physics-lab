from __future__ import annotations

from pathlib import Path

from physics_lab.factories.nuclear_uncertainty import run_uncertainty_perturbation_control


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_nmd0002_uncertainty_control_is_deterministic() -> None:
    first = run_uncertainty_perturbation_control(
        dataset_path=REPO_ROOT / "data/nuclear_masses/nmd-0002-curated-measured-slice.yaml",
        factory_summary_path=REPO_ROOT / "agent_runs/AGENT-RUN-0052/factory_summary.yaml",
        baseline_result_path=REPO_ROOT / "results/EXP-0012/RUN-0001/result.yaml",
        trials=12,
        seed=518,
    )
    second = run_uncertainty_perturbation_control(
        dataset_path=REPO_ROOT / "data/nuclear_masses/nmd-0002-curated-measured-slice.yaml",
        factory_summary_path=REPO_ROOT / "agent_runs/AGENT-RUN-0052/factory_summary.yaml",
        baseline_result_path=REPO_ROOT / "results/EXP-0012/RUN-0001/result.yaml",
        trials=12,
        seed=518,
    )

    assert first == second
    assert first["task_id"] == "TASK-0518"
    assert first["dataset_summary"]["row_count"] == 11
    assert first["dataset_summary"]["all_rows_share_same_uncertainty"] is True
    assert first["dataset_summary"]["source_grade_per_row_uncertainty_available"] is False
    assert first["top_candidate_ids"] == [
        "CAND-0001",
        "CAND-0019",
        "CAND-0011",
        "CAND-0029",
        "CAND-0037",
    ]


def test_nmd0002_uncertainty_control_preserves_sandbox_ceiling() -> None:
    metrics = run_uncertainty_perturbation_control(
        dataset_path=REPO_ROOT / "data/nuclear_masses/nmd-0002-curated-measured-slice.yaml",
        factory_summary_path=REPO_ROOT / "agent_runs/AGENT-RUN-0052/factory_summary.yaml",
        baseline_result_path=REPO_ROOT / "results/EXP-0012/RUN-0001/result.yaml",
        trials=20,
        seed=518,
    )

    assert metrics["verdict"] == "INCONCLUSIVE"
    assert "Sandbox control evidence only" in metrics["limitations"][-1]
    for mode in metrics["mode_summaries"].values():
        for candidate in mode["candidate_stability"]:
            assert "READY_FOR_PRED_FREEZE" not in candidate["route_verdict_counts"]
