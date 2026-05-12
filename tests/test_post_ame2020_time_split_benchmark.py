from __future__ import annotations

import json
from pathlib import Path

import pytest

from physics_lab.registry.agent_runs import load_agent_run
from physics_lab.registry.post_ame2020_holdout import (
    HYP_0021_FROZEN_SPEC,
    assert_candidate_spec_unchanged,
    assess_post_ame2020_activation,
    build_post_ame2020_dry_run_metrics,
    calculate_time_split_metrics,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def test_time_split_metric_calculation_supports_uncertainty_normalization() -> None:
    metrics = calculate_time_split_metrics(
        observed_mev=[10.0, 12.0, 15.0],
        predicted_mev=[9.0, 13.5, 14.0],
        uncertainties_mev=[0.5, 1.5, None],
    )

    assert metrics["count"] == 3
    assert metrics["mae_mev"] == pytest.approx((1.0 + 1.5 + 1.0) / 3.0)
    assert metrics["rmse_mev"] == pytest.approx(((1.0**2 + (-1.5) ** 2 + 1.0**2) / 3.0) ** 0.5)
    assert metrics["mean_abs_uncertainty_normalized_error"] == pytest.approx((2.0 + 1.0) / 2.0)
    assert metrics["max_abs_uncertainty_normalized_error"] == pytest.approx(2.0)


def test_candidate_freeze_rejects_post_hoc_formula_mutation() -> None:
    assert_candidate_spec_unchanged(HYP_0021_FROZEN_SPEC)

    mutated = HYP_0021_FROZEN_SPEC.to_dict()
    mutated["formula"] = "r_corr = c1*m2 + c2*mh + c3*oa + c4*new_term"
    with pytest.raises(ValueError, match="formula"):
        assert_candidate_spec_unchanged(mutated)


def test_post_ame2020_activation_guard_sees_row_level_dataset_but_blocks_metrics() -> None:
    repo_root = _repo_root()
    activation = assess_post_ame2020_activation(
        repo_root / "data" / "nuclear_masses" / "post_ame2020_sources.yaml"
    )

    assert activation["status"] == "ROW_LEVEL_HOLDOUT_READY_METRICS_BLOCKED"
    assert activation["active"] is False
    assert activation["row_level_holdout_dataset_committed"] is True
    assert activation["time_split_holdout_active"] is False
    assert activation["row_level_dataset_exists"] is True
    assert "new_measurement_value" in activation["required_columns"]


def test_post_ame2020_activation_guard_rejects_missing_row_level_dataset(tmp_path: Path) -> None:
    repo_root = _repo_root()
    activation = assess_post_ame2020_activation(
        repo_root / "data" / "nuclear_masses" / "post_ame2020_sources.yaml",
        row_level_dataset_path=tmp_path / "missing.yaml",
    )

    assert activation["status"] == "ROW_LEVEL_MANIFEST_WITH_MISSING_DATASET"
    assert activation["active"] is False
    assert activation["row_level_dataset_exists"] is False


def test_agent_run_0007_documents_inconclusive_time_split_dry_run() -> None:
    repo_root = _repo_root()
    metrics_path = repo_root / "agent_runs" / "AGENT-RUN-0007" / "metrics.json"
    agent_run_path = repo_root / "agent_runs" / "AGENT-RUN-0007" / "agent_run.yaml"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    rebuilt = build_post_ame2020_dry_run_metrics(
        manifest_path=repo_root / "data" / "nuclear_masses" / "post_ame2020_sources.yaml",
        split_replay_metrics_path=repo_root / "agent_runs" / "AGENT-RUN-0006" / "metrics.json",
    )
    agent_run = load_agent_run(agent_run_path, root=repo_root)

    assert agent_run["task_id"] == "TASK-0188"
    assert agent_run["verdict"] == "INCONCLUSIVE"
    assert metrics["benchmark_status"] == "NOT_ACTIVATED_SOURCE_MANIFEST_ONLY"
    assert metrics["time_split_metrics_active"] is False
    assert metrics["candidate_evaluations_performed"] is False
    assert metrics["canonical_results_changed"] is False
    assert metrics["canonical_claims_changed"] is False
    assert metrics["split_replay_context"] == rebuilt["split_replay_context"]
