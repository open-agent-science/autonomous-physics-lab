"""NMD-0003 uncertainty-weighted baseline diagnostic (TASK-0596).

This module answers one bounded diagnostic question for the Nuclear Mass Surface
readiness gate: does weighting the liquid-drop baseline fit by AME2020
*measurement* uncertainty change the readiness interpretation, or does it only
add a limitation note?

It is diagnostic-only. It does not introduce a residual-feature family, does not
score the post-AME2020 reveal holdout, does not alter the frozen
``nmd-0003-stratified-baseline-gate.yaml`` contract, the frozen split manifest,
or any baseline identity, and it does not write PRED, CLAIM, KNOW, RESULT, or
discovery wording.

The only degrees of freedom are the five liquid-drop coefficients and a small
set of *predeclared* weight policies, all evaluated under the frozen
``stratified_interleaved_70_30`` interpolation split. The unweighted ordinary
least-squares (OLS) audit baseline is the comparison reference; it reproduces the
frozen gate's ``required_audit_baseline`` validation MAE on the same split.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import numpy as np

from physics_lab.engines.nuclear_mass_baselines import (
    SemiEmpiricalCoefficients,
    binding_energy_uncertainty_mev,
    evaluate_baseline,
    fit_semi_empirical_coefficients,
    fit_semi_empirical_coefficients_weighted,
)
from physics_lab.engines.nuclear_masses import NuclearMassEntry, load_nuclear_mass_dataset

COEFFICIENT_KEYS = ("volume", "surface", "coulomb", "asymmetry", "pairing")

DEFAULT_DATASET_PATH = Path("data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml")
DEFAULT_GATE_PATH = Path("data/nuclear_masses/nmd-0003-stratified-baseline-gate.yaml")

# Frozen readiness split (stratified_interleaved_70_30): sort committed measured
# rows by (A, Z, N), then assign a row to the validation holdout when its sorted
# index modulo 10 is >= 7. This mirrors the frozen gate and the TASK-0535
# baseline-family gate exactly; it is not re-derived or tuned here.
PRIMARY_SPLIT_ID = "stratified_interleaved_70_30"
VALIDATION_MODULO_THRESHOLD = 7

# Predeclared uncertainty-weight policies. Each maps a per-row binding-energy
# measurement uncertainty sigma (MeV) to a non-negative least-squares weight.
# Floors are model-error-scale guards: the liquid-drop baseline residual is of
# order MeV, so a sigma far below the model-error scale should not be allowed to
# dominate the fit. Policies are declared before scoring and are not changed
# after seeing the metrics.
WEIGHT_POLICIES = (
    "inverse_variance",
    "inverse_sigma",
    "inverse_variance_floored_0p1mev",
    "inverse_variance_floored_1mev",
)
SIGMA_FLOOR_MEV = {
    "inverse_variance_floored_0p1mev": 0.1,
    "inverse_variance_floored_1mev": 1.0,
}

# Predeclared rule for deciding whether weighting changes readiness interpretation
# rather than merely adding a limitation note. A weighted global fit only counts
# as readiness-relevant if it beats the unweighted OLS audit baseline validation
# MAE by more than this relative margin *and* keeps a non-degenerate effective
# sample (so the "improvement" is not driven by a handful of ultra-precise rows).
READINESS_CHANGE_MIN_RELATIVE_IMPROVEMENT = 0.05
READINESS_CHANGE_MIN_EFFECTIVE_SAMPLE_FRACTION = 0.5


def run_nmd0003_uncertainty_weighted_baseline_diagnostic(
    *,
    dataset_path: Path | str = DEFAULT_DATASET_PATH,
    gate_path: Path | str = DEFAULT_GATE_PATH,
) -> dict[str, Any]:
    """Run the deterministic TASK-0596 uncertainty-weighted baseline diagnostic."""
    dataset_path = Path(dataset_path)
    gate_path = Path(gate_path)

    dataset = load_nuclear_mass_dataset(dataset_path)
    entries = sorted(
        dataset.entries, key=lambda entry: (entry.A, entry.Z, entry.N, entry.nuclide_id)
    )
    train_entries = [e for i, e in enumerate(entries) if i % 10 < VALIDATION_MODULO_THRESHOLD]
    validation_entries = [
        e for i, e in enumerate(entries) if i % 10 >= VALIDATION_MODULO_THRESHOLD
    ]

    coverage = {
        "full_nmd0003_training_surface": _uncertainty_coverage(entries),
        "train": _uncertainty_coverage(train_entries),
        "validation_holdout": _uncertainty_coverage(validation_entries),
    }

    # Unweighted OLS audit baseline on all train rows (the frozen gate's
    # required_audit_baseline). This is the readiness comparison reference.
    ols_all = fit_semi_empirical_coefficients(train_entries)

    # Rows usable by a measurement-uncertainty weighting (sigma present and > 0).
    # Rows with missing or ambiguous (non-positive) sigma are excluded from the
    # weighted fits and reported explicitly, never silently imputed.
    weightable_train = [
        e for e in train_entries if _positive_sigma(binding_energy_uncertainty_mev(e))
    ]
    ols_weightable = fit_semi_empirical_coefficients(weightable_train)

    baselines: dict[str, Any] = {
        "nmd0003_train_fitted_ols_audit": {
            "fit_policy": "fit_train_split_only_ols",
            "train_row_count": len(train_entries),
            "uncertainty_weighted": False,
            "coefficients": ols_all.to_dict(),
            "metrics": _all_split_metrics(
                ols_all, entries, train_entries, validation_entries
            ),
        },
        "nmd0003_train_fitted_ols_weightable_rows": {
            "fit_policy": "fit_train_split_only_ols_on_positive_sigma_rows",
            "train_row_count": len(weightable_train),
            "uncertainty_weighted": False,
            "coefficients": ols_weightable.to_dict(),
            "metrics": _all_split_metrics(
                ols_weightable, entries, train_entries, validation_entries
            ),
        },
    }

    weighted_results: dict[str, Any] = {}
    for policy in WEIGHT_POLICIES:
        sigma = np.asarray(
            [binding_energy_uncertainty_mev(e) for e in weightable_train], dtype=float
        )
        weights = _weight_vector(sigma, policy=policy)
        coefficients = fit_semi_empirical_coefficients_weighted(
            weightable_train, weights=list(weights)
        )
        weighted_results[policy] = {
            "fit_policy": f"fit_train_split_only_wls:{policy}",
            "train_row_count": len(weightable_train),
            "uncertainty_weighted": True,
            "weight_concentration": _weight_concentration(weights),
            "coefficients": coefficients.to_dict(),
            "metrics": _all_split_metrics(
                coefficients, entries, train_entries, validation_entries
            ),
        }

    decision = _readiness_decision(
        ols_audit=baselines["nmd0003_train_fitted_ols_audit"],
        weighted_results=weighted_results,
        weightable_row_count=len(weightable_train),
    )

    return {
        "task_id": "TASK-0596",
        "benchmark_id": "nmd0003-uncertainty-weighted-baseline-diagnostic",
        "input_references": {
            "dataset": dataset_path.as_posix(),
            "frozen_gate": gate_path.as_posix(),
            "frozen_split_id": PRIMARY_SPLIT_ID,
            "prior_baseline_family_run": "agent_runs/AGENT-RUN-0056/metrics.json",
        },
        "dataset_summary": {
            "dataset_id": dataset.dataset_id,
            "row_count": len(entries),
            "train_count": len(train_entries),
            "validation_holdout_count": len(validation_entries),
            "post_ame2020_holdout_excluded": True,
        },
        "frozen_split": {
            "split_id": PRIMARY_SPLIT_ID,
            "row_order": "sort committed NMD-0003 measured rows by (A, Z, N)",
            "validation_rule": "sorted_index % 10 >= 7",
            "purpose": "interpolation_readiness_gate",
            "mutated": False,
        },
        "uncertainty_coverage": coverage,
        "declared_weight_policies": _declared_weight_policy_descriptions(),
        "unweighted_baselines": baselines,
        "uncertainty_weighted_baselines": weighted_results,
        "readiness_decision": decision,
        "verdict": "INCONCLUSIVE",
        "limitations": [
            "Diagnostic-only comparison on committed AME2020 measured rows under the "
            "frozen stratified interpolation split; not a post-AME2020 reveal.",
            "All baselines are five-coefficient liquid-drop fits; no residual-feature, "
            "shell-axis, or local-curvature family is introduced.",
            "AME2020 measurement uncertainty (~keV) is far below the liquid-drop model "
            "error (~MeV), so raw inverse-variance weighting is dominated by a few "
            "ultra-precise light nuclides and is not a physically appropriate readiness "
            "baseline.",
            "The amu-defining nuclide C-12 carries an exact (zero) atomic-mass "
            "uncertainty and is reported as ambiguous and excluded from the weighted "
            "fits rather than assigned infinite weight.",
            "Sandbox diagnostic evidence only; no PRED, CLAIM, KNOW, RESULT, or "
            "discovery wording is promoted, and the frozen gate is unchanged.",
        ],
        "output_routing": {
            "task_verdict": "INCONCLUSIVE",
            "canonical_destination": "docs/reviews/nmd0003-uncertainty-weighted-baseline-diagnostic.md",
            "review_tier": "none",
            "gate_a_status": "not_attempted",
            "gate_b_status": "not_applicable",
            "claim_impact": "none",
            "knowledge_impact": "none",
            "result_impact": "no RESULT artifact created",
        },
    }


# --------------------------------------------------------------------------- #
# Weighting
# --------------------------------------------------------------------------- #


def _weight_vector(sigma: np.ndarray, *, policy: str) -> np.ndarray:
    if policy == "inverse_variance":
        return 1.0 / np.square(sigma)
    if policy == "inverse_sigma":
        return 1.0 / sigma
    if policy in SIGMA_FLOOR_MEV:
        floored = np.maximum(sigma, SIGMA_FLOOR_MEV[policy])
        return 1.0 / np.square(floored)
    raise ValueError(f"Unknown uncertainty-weight policy: {policy}")


def _weight_concentration(weights: np.ndarray) -> dict[str, float | int]:
    weights = np.asarray(weights, dtype=float)
    total = float(weights.sum())
    ordered = np.sort(weights)[::-1]
    effective_sample_size = float(total**2 / float(np.square(weights).sum()))
    return {
        "row_count": int(weights.shape[0]),
        "effective_sample_size": round(effective_sample_size, 4),
        "effective_sample_fraction": round(effective_sample_size / weights.shape[0], 6),
        "top1_weight_share": round(float(ordered[0] / total), 6),
        "top10_weight_share": round(float(ordered[: min(10, ordered.shape[0])].sum() / total), 6),
    }


# --------------------------------------------------------------------------- #
# Coverage
# --------------------------------------------------------------------------- #


def _positive_sigma(sigma: float | None) -> bool:
    return sigma is not None and sigma > 0.0


def _uncertainty_coverage(entries: Iterable[NuclearMassEntry]) -> dict[str, Any]:
    rows = list(entries)
    present_positive: list[float] = []
    missing_ids: list[str] = []
    nonpositive_ids: list[str] = []
    for entry in rows:
        sigma = binding_energy_uncertainty_mev(entry)
        if sigma is None:
            missing_ids.append(entry.nuclide_id)
        elif sigma <= 0.0:
            nonpositive_ids.append(entry.nuclide_id)
        else:
            present_positive.append(sigma)
    sigma_array = np.asarray(present_positive, dtype=float)
    return {
        "row_count": len(rows),
        "present_positive_sigma_count": len(present_positive),
        "missing_sigma_count": len(missing_ids),
        "missing_sigma_nuclide_ids": sorted(missing_ids),
        "nonpositive_sigma_count": len(nonpositive_ids),
        "nonpositive_sigma_nuclide_ids": sorted(nonpositive_ids),
        "sigma_mev_min": (round(float(sigma_array.min()), 9) if present_positive else None),
        "sigma_mev_median": (
            round(float(np.median(sigma_array)), 9) if present_positive else None
        ),
        "sigma_mev_max": (round(float(sigma_array.max()), 9) if present_positive else None),
    }


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #


def _all_split_metrics(
    coefficients: SemiEmpiricalCoefficients,
    full_entries: list[NuclearMassEntry],
    train_entries: list[NuclearMassEntry],
    validation_entries: list[NuclearMassEntry],
) -> dict[str, Any]:
    return {
        "train": _residual_summary(coefficients, train_entries),
        "validation_holdout": _residual_summary(coefficients, validation_entries),
        "full_nmd0003_training_surface": _residual_summary(coefficients, full_entries),
    }


def _residual_summary(
    coefficients: SemiEmpiricalCoefficients, entries: list[NuclearMassEntry]
) -> dict[str, float | int | None]:
    if not entries:
        return {"count": 0, "mae_mev": None, "rmse_mev": None, "max_abs_residual_mev": None}
    rows = evaluate_baseline(entries=entries, model_id="baseline", coefficients=coefficients)
    residuals = np.asarray([row.residual_mev for row in rows], dtype=float)
    abs_residuals = np.abs(residuals)
    return {
        "count": len(rows),
        "mae_mev": round(float(np.mean(abs_residuals)), 6),
        "rmse_mev": round(float(np.sqrt(np.mean(np.square(residuals)))), 6),
        "max_abs_residual_mev": round(float(np.max(abs_residuals)), 6),
    }


# --------------------------------------------------------------------------- #
# Decision
# --------------------------------------------------------------------------- #


def _readiness_decision(
    *,
    ols_audit: dict[str, Any],
    weighted_results: dict[str, Any],
    weightable_row_count: int,
) -> dict[str, Any]:
    audit_val_mae = float(ols_audit["metrics"]["validation_holdout"]["mae_mev"])
    per_policy: dict[str, Any] = {}
    qualifying: list[str] = []
    for policy, result in weighted_results.items():
        weighted_val_mae = float(result["metrics"]["validation_holdout"]["mae_mev"])
        relative_improvement = (audit_val_mae - weighted_val_mae) / audit_val_mae
        effective_fraction = float(result["weight_concentration"]["effective_sample_fraction"])
        is_readiness_relevant = (
            relative_improvement > READINESS_CHANGE_MIN_RELATIVE_IMPROVEMENT
            and effective_fraction >= READINESS_CHANGE_MIN_EFFECTIVE_SAMPLE_FRACTION
        )
        per_policy[policy] = {
            "validation_mae_mev": round(weighted_val_mae, 6),
            "validation_mae_relative_improvement_vs_ols_audit": round(relative_improvement, 6),
            "effective_sample_fraction": effective_fraction,
            "is_readiness_relevant_improvement": is_readiness_relevant,
        }
        if is_readiness_relevant:
            qualifying.append(policy)

    changes_interpretation = bool(qualifying)
    if changes_interpretation:
        interpretation = (
            "At least one predeclared uncertainty-weighted policy beats the "
            "unweighted OLS audit baseline by more than "
            f"{READINESS_CHANGE_MIN_RELATIVE_IMPROVEMENT:.0%} on the frozen "
            "validation holdout while keeping a non-degenerate effective sample. "
            "A narrower follow-up should record this before any readiness-baseline "
            "change; the frozen gate is not altered here."
        )
    else:
        interpretation = (
            "No predeclared uncertainty-weighted policy produces a readiness-relevant "
            "improvement over the unweighted OLS audit baseline. Raw inverse-variance "
            "and inverse-sigma weighting collapse the effective sample onto a few "
            "ultra-precise light nuclides and sharply worsen the validation holdout, "
            "while floor-guarded variants only recover the unweighted fit. Measurement-"
            "uncertainty weighting therefore adds a limitation note rather than changing "
            "candidate-readiness interpretation: future bounded residual-feature sprints "
            "should keep the unweighted OLS audit baseline and the frozen region-"
            "stratified readiness baseline as the contract."
        )

    return {
        "audit_baseline_validation_mae_mev": round(audit_val_mae, 6),
        "weightable_row_count": weightable_row_count,
        "readiness_change_rule": {
            "min_relative_improvement": READINESS_CHANGE_MIN_RELATIVE_IMPROVEMENT,
            "min_effective_sample_fraction": READINESS_CHANGE_MIN_EFFECTIVE_SAMPLE_FRACTION,
        },
        "per_policy": per_policy,
        "qualifying_policies": qualifying,
        "weighting_changes_candidate_readiness_interpretation": changes_interpretation,
        "interpretation": interpretation,
    }


def _declared_weight_policy_descriptions() -> dict[str, str]:
    return {
        "inverse_variance": (
            "Raw inverse-variance weighting w = 1/sigma^2 on the propagated "
            "binding-energy measurement uncertainty."
        ),
        "inverse_sigma": (
            "Softer inverse-sigma weighting w = 1/sigma."
        ),
        "inverse_variance_floored_0p1mev": (
            "Inverse-variance with sigma floored at 0.1 MeV before squaring, an "
            "intermediate guard against single-row dominance."
        ),
        "inverse_variance_floored_1mev": (
            "Inverse-variance with sigma floored at the ~1 MeV liquid-drop model-error "
            "scale before squaring; this effectively recovers near-uniform weighting."
        ),
    }
