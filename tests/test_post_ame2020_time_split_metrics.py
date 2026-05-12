from __future__ import annotations

import json
from pathlib import Path

import pytest

from physics_lab.registry.agent_runs import load_agent_run
from physics_lab.registry.post_ame2020_holdout import (
    build_post_ame2020_time_split_benchmark,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _build_metrics() -> dict:
    repo_root = _repo_root()
    return build_post_ame2020_time_split_benchmark(
        holdout_dataset_path=repo_root / "data" / "nuclear_masses" / "post_ame2020_holdout.yaml",
        source_manifest_path=repo_root / "data" / "nuclear_masses" / "post_ame2020_sources.yaml",
        result_path=repo_root / "results" / "EXP-0012" / "RUN-0001" / "result.yaml",
        training_dataset_path=repo_root
        / "data"
        / "nuclear_masses"
        / "nmd-0002-curated-measured-slice.yaml",
        split_replay_metrics_path=repo_root / "agent_runs" / "AGENT-RUN-0006" / "metrics.json",
        guard_metrics_path=repo_root / "agent_runs" / "AGENT-RUN-0007" / "metrics.json",
    )


def test_post_ame2020_time_split_metrics_are_active_and_retrospective() -> None:
    metrics = _build_metrics()

    assert metrics["benchmark_status"] == "ACTIVE_RETROSPECTIVE_TIME_SPLIT"
    assert metrics["evidence_class"] == "retrospective_time_split_validation_not_blind_prediction"
    assert metrics["activation"]["status"] == "ACTIVE"
    assert metrics["activation"]["active"] is True
    assert metrics["sandbox_only"] is True
    assert metrics["canonical_results_changed"] is False
    assert metrics["canonical_claims_changed"] is False
    assert metrics["claim_promotion_allowed"] is False
    assert metrics["summary"]["retrospective_not_blind_prediction"] is True


def test_post_ame2020_time_split_primary_candidate_outcomes() -> None:
    metrics = _build_metrics()
    baseline = metrics["evaluations"]["frozen_baseline"]["metrics_by_subset"]["primary"]
    candidates = metrics["evaluations"]["candidate_families"]

    assert metrics["dataset_summary"]["primary_holdout_row_count"] == 295
    assert metrics["dataset_summary"]["ame2020_extrapolated_comparison_count"] == 55
    assert baseline["mae_mev"] == pytest.approx(4.552568580201034)
    assert baseline["rmse_mev"] == pytest.approx(5.8796369910752775)

    hyp20_delta = candidates["HYP-PROPOSAL-0020"]["delta_vs_frozen_baseline"]["primary"]
    hyp21_delta = candidates["HYP-PROPOSAL-0021"]["delta_vs_frozen_baseline"]["primary"]
    hyp22_delta = candidates["HYP-PROPOSAL-0022"]["delta_vs_frozen_baseline"]["primary"]

    assert hyp20_delta["delta_mae_mev"] == pytest.approx(0.0)
    assert hyp21_delta["delta_mae_mev"] == pytest.approx(0.07964307256953074)
    assert hyp21_delta["improved_mae"] is False
    assert hyp22_delta["delta_mae_mev"] == pytest.approx(-0.38855507395615607)
    assert hyp22_delta["improved_mae"] is True
    assert metrics["summary"]["best_candidate_by_primary_mae"] == "HYP-PROPOSAL-0022"
    assert metrics["summary"]["verdict"] == "INCONCLUSIVE"


def test_post_ame2020_time_split_subsets_and_regressions_are_recorded() -> None:
    metrics = _build_metrics()
    baseline_subsets = metrics["evaluations"]["frozen_baseline"]["metrics_by_subset"]
    hyp21 = metrics["evaluations"]["candidate_families"]["HYP-PROPOSAL-0021"]

    assert baseline_subsets["ame2020_extrapolated_comparison"]["count"] == 55
    assert baseline_subsets["neutron_rich_delta_ge_20"]["count"] == 116
    assert baseline_subsets["magic_any"]["count"] == 18
    assert baseline_subsets["double_magic"]["count"] == 0
    assert hyp21["feature_activation_counts"] == {
        "magic_both": 0,
        "heavy_double_magic": 0,
        "odd_a": 156,
    }
    assert hyp21["worst_regression_cases_vs_baseline"]
    assert (
        hyp21["worst_regression_cases_vs_baseline"][0]["delta_abs_error_vs_baseline_mev"]
        > 0.0
    )


def test_agent_run_0008_artifacts_match_rebuilt_metrics() -> None:
    repo_root = _repo_root()
    stored = json.loads(
        (repo_root / "agent_runs" / "AGENT-RUN-0008" / "metrics.json").read_text(
            encoding="utf-8"
        )
    )
    rebuilt = _build_metrics()
    agent_run = load_agent_run(
        repo_root / "agent_runs" / "AGENT-RUN-0008" / "agent_run.yaml",
        root=repo_root,
    )

    assert stored["summary"] == rebuilt["summary"]
    assert stored["evaluations"]["frozen_baseline"]["metrics_by_subset"]["primary"] == rebuilt[
        "evaluations"
    ]["frozen_baseline"]["metrics_by_subset"]["primary"]
    assert agent_run["task_id"] == "TASK-0197"
    assert agent_run["verdict"] == "INCONCLUSIVE"
    assert agent_run["promotion_boundary"]["writes_canonical_result"] is False
