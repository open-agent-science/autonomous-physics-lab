from __future__ import annotations

from pathlib import Path

from physics_lab.engines.nmd0003_uncertainty_weighted_diagnostic import (
    run_nmd0003_uncertainty_weighted_baseline_diagnostic,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0003-stratified-baseline-gate.yaml"


def test_diagnostic_is_deterministic() -> None:
    first = run_nmd0003_uncertainty_weighted_baseline_diagnostic()
    second = run_nmd0003_uncertainty_weighted_baseline_diagnostic()
    assert first == second
    assert first["task_id"] == "TASK-0596"
    assert first["verdict"] == "INCONCLUSIVE"


def test_split_matches_frozen_gate() -> None:
    metrics = run_nmd0003_uncertainty_weighted_baseline_diagnostic()
    summary = metrics["dataset_summary"]
    assert summary["row_count"] == 2309
    assert summary["train_count"] == 1617
    assert summary["validation_holdout_count"] == 692
    assert summary["post_ame2020_holdout_excluded"] is True
    assert metrics["frozen_split"]["mutated"] is False


def test_ols_audit_baseline_reproduces_frozen_gate_validation_mae() -> None:
    metrics = run_nmd0003_uncertainty_weighted_baseline_diagnostic()
    audit = metrics["unweighted_baselines"]["nmd0003_train_fitted_ols_audit"]
    # Reproduces the frozen gate required_audit_baseline validation MAE (2.61432).
    assert audit["metrics"]["validation_holdout"]["mae_mev"] == 2.61432


def test_ambiguous_uncertainty_row_is_c12_and_excluded() -> None:
    metrics = run_nmd0003_uncertainty_weighted_baseline_diagnostic()
    train_coverage = metrics["uncertainty_coverage"]["train"]
    assert train_coverage["missing_sigma_count"] == 0
    assert train_coverage["nonpositive_sigma_count"] == 1
    assert train_coverage["nonpositive_sigma_nuclide_ids"] == ["C-12"]
    # The weighted fits run on the positive-sigma rows only (1617 - 1 = 1616).
    weighted = metrics["uncertainty_weighted_baselines"]["inverse_variance"]
    assert weighted["train_row_count"] == 1616


def test_raw_inverse_variance_is_degenerate_and_regresses() -> None:
    metrics = run_nmd0003_uncertainty_weighted_baseline_diagnostic()
    raw = metrics["uncertainty_weighted_baselines"]["inverse_variance"]
    concentration = raw["weight_concentration"]
    # The effective sample collapses onto a handful of ultra-precise rows.
    assert concentration["effective_sample_size"] < 5.0
    assert concentration["top1_weight_share"] > 0.5
    # And the validation holdout regresses badly versus the OLS audit baseline.
    per_policy = metrics["readiness_decision"]["per_policy"]["inverse_variance"]
    assert per_policy["validation_mae_relative_improvement_vs_ols_audit"] < -1.0
    assert per_policy["is_readiness_relevant_improvement"] is False


def test_model_scale_floor_recovers_unweighted_fit() -> None:
    metrics = run_nmd0003_uncertainty_weighted_baseline_diagnostic()
    floored = metrics["uncertainty_weighted_baselines"]["inverse_variance_floored_1mev"]
    # Flooring sigma at the ~1 MeV model-error scale yields near-uniform weights.
    assert floored["weight_concentration"]["effective_sample_fraction"] == 1.0
    ols_weightable = metrics["unweighted_baselines"][
        "nmd0003_train_fitted_ols_weightable_rows"
    ]["metrics"]["validation_holdout"]["mae_mev"]
    assert abs(floored["metrics"]["validation_holdout"]["mae_mev"] - ols_weightable) < 1e-3


def test_weighting_does_not_change_readiness_interpretation() -> None:
    metrics = run_nmd0003_uncertainty_weighted_baseline_diagnostic()
    decision = metrics["readiness_decision"]
    assert decision["weighting_changes_candidate_readiness_interpretation"] is False
    assert decision["qualifying_policies"] == []


def test_run_does_not_mutate_frozen_gate() -> None:
    before = GATE_PATH.read_text(encoding="utf-8")
    run_nmd0003_uncertainty_weighted_baseline_diagnostic()
    after = GATE_PATH.read_text(encoding="utf-8")
    assert before == after
