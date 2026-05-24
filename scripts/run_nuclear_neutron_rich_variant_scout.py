"""TASK-0279 neutron-rich nuclear sandbox scout.

This sandbox-only scout evaluates bounded neutron-rich, neutron-excess, and
asymmetry residual features against the frozen RESULT-0015 fitted
semi-empirical baseline using repository-pinned data only. It does not write
prediction registry entries, canonical results, claims, or knowledge artifacts.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.engines.nuclear_mass_baselines import (  # noqa: E402
    SemiEmpiricalCoefficients,
    evaluate_baseline,
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset  # noqa: E402


NMD_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0002-curated-measured-slice.yaml"
POST_AME_PATH = REPO_ROOT / "data" / "nuclear_masses" / "post_ame2020_holdout.yaml"
RESULT_PATH = REPO_ROOT / "results" / "EXP-0012" / "RUN-0001" / "result.yaml"

AGENT_RUN_ID = "AGENT-RUN-0013"
TASK_ID = "TASK-0279"


EXECUTED_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "candidate_id": "NR-SCOUT-001",
        "name": "Quadratic asymmetric neutron-excess ramp",
        "formula": "r_corr = beta_q * max(N-Z, 0)^2 / A",
        "feature_names": ("neutron_excess_sq_over_a",),
        "complexity": 1,
    },
    {
        "candidate_id": "NR-SCOUT-002",
        "name": "Cubic asymmetric neutron-excess ramp",
        "formula": "r_corr = beta_c * max(N-Z, 0)^3 / A^2",
        "feature_names": ("neutron_excess_cu_over_a_sq",),
        "complexity": 1,
    },
    {
        "candidate_id": "NR-SCOUT-003",
        "name": "Positive asymmetry fraction",
        "formula": "r_corr = beta_i * max((N-Z)/A, 0)",
        "feature_names": ("positive_asymmetry_fraction",),
        "complexity": 1,
    },
    {
        "candidate_id": "NR-SCOUT-004",
        "name": "Frontier excess beyond N-Z equals 20",
        "formula": "r_corr = beta_f * max(N-Z-20, 0) / A",
        "feature_names": ("frontier_excess_after_20_over_a",),
        "complexity": 1,
    },
    {
        "candidate_id": "NR-SCOUT-005",
        "name": "Matched quadratic plus cubic neutron-excess pair",
        "formula": (
            "r_corr = beta_q * max(N-Z, 0)^2 / A "
            "+ beta_c * max(N-Z, 0)^3 / A^2"
        ),
        "feature_names": ("neutron_excess_sq_over_a", "neutron_excess_cu_over_a_sq"),
        "complexity": 2,
    },
    {
        "candidate_id": "NR-SCOUT-006",
        "name": "Near-null neutron-rich sanity control",
        "formula": "r_corr = 0.0",
        "feature_names": (),
        "complexity": 0,
        "fixed_zero_control": True,
    },
)


REJECTED_BEFORE_EXECUTION: tuple[dict[str, str], ...] = (
    {
        "candidate_id": "NR-SCOUT-007",
        "name": "Free-power neutron-excess exponent",
        "rejection_reason": (
            "Rejected before execution because fitting a free exponent on the "
            "11-row NMD-0002 residual surface would introduce a nonlinear "
            "overfit knob outside the bounded linear scout contract."
        ),
    },
    {
        "candidate_id": "NR-SCOUT-008",
        "name": "In/Sb frontier-cluster indicator",
        "rejection_reason": (
            "Rejected before sandbox evaluation because an element-cluster "
            "indicator would target known post-AME2020 residual clusters "
            "retrospectively rather than test a general neutron-rich feature."
        ),
    },
    {
        "candidate_id": "NR-SCOUT-009",
        "name": "Per-threshold neutron-rich sweep",
        "rejection_reason": (
            "Rejected before execution because sweeping many N-Z thresholds "
            "duplicates the bounded frontier ramp while adding arbitrary "
            "selection degrees of freedom."
        ),
    },
)


def load_frozen_baseline_coefficients() -> SemiEmpiricalCoefficients:
    """Load RESULT-0015 fitted semi-empirical coefficients."""
    with RESULT_PATH.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    for score in payload["scores"]:
        if score["model_id"] == "model_fitted_semi_empirical":
            coeffs = score["coefficients"]
            return SemiEmpiricalCoefficients(
                volume=float(coeffs["volume"]),
                surface=float(coeffs["surface"]),
                coulomb=float(coeffs["coulomb"]),
                asymmetry=float(coeffs["asymmetry"]),
                pairing=float(coeffs["pairing"]),
            )
    raise RuntimeError("RESULT-0015 fitted semi-empirical coefficients not found")


def feature_vector(feature_names: tuple[str, ...], *, z: int, n: int, a: int) -> tuple[float, ...]:
    """Return neutron-rich feature values for one target row."""
    excess = max(n - z, 0)
    asymmetry = float(n - z) / float(a)
    values = {
        "neutron_excess_sq_over_a": float(excess * excess) / float(a),
        "neutron_excess_cu_over_a_sq": float(excess * excess * excess) / float(a * a),
        "positive_asymmetry_fraction": max(asymmetry, 0.0),
        "frontier_excess_after_20_over_a": float(max(n - z - 20, 0)) / float(a),
    }
    return tuple(values[name] for name in feature_names)


def subset_ids(*, z: int, n: int, a: int, was_extrapolated: bool) -> tuple[str, ...]:
    """Subset labels for neutron-rich/asymmetry diagnostics."""
    delta = n - z
    asymmetry = float(delta) / float(a)
    ids = ["primary"]
    ids.append("ame2020_extrapolated_comparison" if was_extrapolated else "ame2020_measured_comparison")
    if delta >= 20:
        ids.append("neutron_rich_delta_ge_20")
    if delta >= 30:
        ids.append("neutron_rich_delta_ge_30")
    if delta >= 40:
        ids.append("neutron_rich_delta_ge_40")
    if asymmetry >= 0.20:
        ids.append("asymmetry_ge_0_20")
    if asymmetry >= 0.25:
        ids.append("asymmetry_ge_0_25")
    if n < z:
        ids.append("proton_rich_n_lt_z")
    if a >= 100:
        ids.append("heavy_a_ge_100")
    return tuple(ids)


def summarize_errors(errors: list[float]) -> dict[str, float | int | None]:
    """Summarize signed residuals."""
    if not errors:
        return {
            "count": 0,
            "mae_mev": None,
            "rmse_mev": None,
            "mean_error_mev": None,
            "max_abs_error_mev": None,
        }
    abs_errors = [abs(error) for error in errors]
    return {
        "count": len(errors),
        "mae_mev": float(sum(abs_errors) / len(abs_errors)),
        "rmse_mev": float(math.sqrt(sum(error * error for error in errors) / len(errors))),
        "mean_error_mev": float(sum(errors) / len(errors)),
        "max_abs_error_mev": float(max(abs_errors)),
    }


def baseline_post_ame2020_rows(coefficients: SemiEmpiricalCoefficients) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build baseline residual rows and subset metrics for the pinned post-AME2020 holdout."""
    with POST_AME_PATH.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    rows = [row for row in payload["entries"] if bool(row["included_in_time_split_holdout"])]
    per_row: list[dict[str, Any]] = []
    subset_errors: dict[str, list[float]] = {}
    for row in rows:
        z, n, a = int(row["Z"]), int(row["N"]), int(row["A"])
        predicted = semi_empirical_binding_energy(z=z, n=n, coefficients=coefficients)
        observed = float(row["new_measurement"]["value_mev"])
        residual = observed - predicted
        item = {
            "row_id": row["row_id"],
            "nuclide_id": row["nuclide_id"],
            "Z": z,
            "N": n,
            "A": a,
            "observed_mev": observed,
            "baseline_predicted_mev": predicted,
            "baseline_residual_mev": residual,
            "was_extrapolated": bool(row["ame2020_comparison"]["was_extrapolated"]),
        }
        per_row.append(item)
        for subset_id in subset_ids(
            z=z,
            n=n,
            a=a,
            was_extrapolated=bool(row["ame2020_comparison"]["was_extrapolated"]),
        ):
            subset_errors.setdefault(subset_id, []).append(residual)
    return per_row, {key: summarize_errors(value) for key, value in sorted(subset_errors.items())}


def verdict_for_candidate(
    *,
    candidate: dict[str, Any],
    primary_delta: float,
    neutron_delta: float | None,
    high_asymmetry_delta: float | None,
    worst_subset_regression: float,
) -> str:
    """Assign conservative scout verdicts without promoting scientific claims."""
    material_delta = 1.0e-6
    if candidate.get("fixed_zero_control"):
        return "INCONCLUSIVE"
    if primary_delta > 1.0 or worst_subset_regression > 2.0:
        return "OVERFITTED"
    if neutron_delta is not None and neutron_delta < -material_delta and primary_delta <= 0.25:
        return "PARTIALLY_VALID"
    if high_asymmetry_delta is not None and high_asymmetry_delta < -material_delta and primary_delta <= 0.25:
        return "PARTIALLY_VALID"
    if primary_delta < -material_delta and worst_subset_regression <= 0.5:
        return "PARTIALLY_VALID"
    return "INCONCLUSIVE"


def evaluate_candidate(
    candidate: dict[str, Any],
    *,
    training_entries: list[Any],
    training_residuals: np.ndarray,
    post_rows: list[dict[str, Any]],
    baseline_metrics: dict[str, Any],
) -> dict[str, Any]:
    """Fit a candidate on NMD-0002 residuals and evaluate it on pinned holdout rows."""
    feature_names = tuple(candidate["feature_names"])
    if candidate.get("fixed_zero_control"):
        beta = np.asarray([], dtype=float)
    else:
        train_x = np.asarray(
            [
                feature_vector(feature_names, z=entry.Z, n=entry.N, a=entry.A)
                for entry in training_entries
            ],
            dtype=float,
        )
        beta, *_ = np.linalg.lstsq(train_x, training_residuals, rcond=None)

    subset_errors: dict[str, list[float]] = {key: [] for key in baseline_metrics}
    per_row: list[dict[str, Any]] = []
    activation_counts = {name: 0 for name in feature_names}
    for row in post_rows:
        z, n, a = int(row["Z"]), int(row["N"]), int(row["A"])
        values = feature_vector(feature_names, z=z, n=n, a=a)
        for name, value in zip(feature_names, values):
            if abs(value) > 0.0:
                activation_counts[name] += 1
        correction = 0.0 if candidate.get("fixed_zero_control") else float(np.asarray(values) @ beta)
        predicted = float(row["baseline_predicted_mev"]) + correction
        residual = float(row["observed_mev"]) - predicted
        item = {
            "row_id": row["row_id"],
            "nuclide_id": row["nuclide_id"],
            "Z": z,
            "N": n,
            "A": a,
            "correction_mev": correction,
            "candidate_residual_mev": residual,
            "feature_values": {
                name: float(value)
                for name, value in zip(feature_names, values)
            },
        }
        per_row.append(item)
        for subset_id in subset_ids(
            z=z,
            n=n,
            a=a,
            was_extrapolated=bool(row["was_extrapolated"]),
        ):
            subset_errors.setdefault(subset_id, []).append(residual)

    metrics_by_subset = {key: summarize_errors(value) for key, value in sorted(subset_errors.items())}
    delta_mae_by_subset: dict[str, float | None] = {}
    for subset_id, metric in metrics_by_subset.items():
        baseline_metric = baseline_metrics.get(subset_id, {})
        if metric["mae_mev"] is None or baseline_metric.get("mae_mev") is None:
            delta_mae_by_subset[subset_id] = None
        else:
            delta_mae_by_subset[subset_id] = float(metric["mae_mev"]) - float(baseline_metric["mae_mev"])

    numeric_deltas = [value for value in delta_mae_by_subset.values() if value is not None]
    worst_subset_regression = max([0.0, *numeric_deltas])
    verdict = verdict_for_candidate(
        candidate=candidate,
        primary_delta=float(delta_mae_by_subset["primary"] or 0.0),
        neutron_delta=delta_mae_by_subset.get("neutron_rich_delta_ge_20"),
        high_asymmetry_delta=delta_mae_by_subset.get("asymmetry_ge_0_25"),
        worst_subset_regression=worst_subset_regression,
    )

    return {
        "candidate_id": candidate["candidate_id"],
        "name": candidate["name"],
        "formula": candidate["formula"],
        "complexity": candidate["complexity"],
        "fitted_coefficients": {
            name: float(value) for name, value in zip(feature_names, beta)
        },
        "feature_activation_counts": activation_counts,
        "metrics_by_subset": metrics_by_subset,
        "delta_mae_by_subset_mev": delta_mae_by_subset,
        "worst_subset_regression_mae_mev": worst_subset_regression,
        "worst_abs_error_cases": sorted(
            per_row,
            key=lambda item: abs(float(item["candidate_residual_mev"])),
            reverse=True,
        )[:8],
        "verdict": verdict,
        "limitations": [
            "Feature coefficients are fit on the 11-row NMD-0002 residual slice.",
            "Post-AME2020 evaluation uses committed retrospective rows only; it is not a reveal of new live measurements.",
            "Verdict is a sandbox triage label, not a promoted claim.",
        ],
    }


def build_metrics() -> dict[str, Any]:
    """Build deterministic scout metrics."""
    coefficients = load_frozen_baseline_coefficients()
    nmd = load_nuclear_mass_dataset(NMD_PATH)
    baseline_rows = evaluate_baseline(
        entries=nmd.entries,
        model_id="model_fitted_semi_empirical",
        coefficients=coefficients,
    )
    residuals = np.asarray([row.residual_mev for row in baseline_rows], dtype=float)
    entries_by_id = {entry.nuclide_id: entry for entry in nmd.entries}
    training_entries = [entries_by_id[row.nuclide_id] for row in baseline_rows]

    post_rows, baseline_metrics = baseline_post_ame2020_rows(coefficients)
    executed_items = [
        evaluate_candidate(
            candidate,
            training_entries=training_entries,
            training_residuals=residuals,
            post_rows=post_rows,
            baseline_metrics=baseline_metrics,
        )
        for candidate in EXECUTED_CANDIDATES
    ]
    verdict_counts: dict[str, int] = {}
    for item in executed_items:
        verdict_counts[item["verdict"]] = verdict_counts.get(item["verdict"], 0) + 1

    generated_candidates = [
        {
            "candidate_id": candidate["candidate_id"],
            "name": candidate["name"],
            "formula": candidate["formula"],
            "decision": "executed",
        }
        for candidate in EXECUTED_CANDIDATES
    ]
    generated_candidates.extend(
        {
            "candidate_id": candidate["candidate_id"],
            "name": candidate["name"],
            "decision": "rejected_before_execution",
            "rejection_reason": candidate["rejection_reason"],
        }
        for candidate in REJECTED_BEFORE_EXECUTION
    )

    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "neutron_rich_variant_scout",
        "sandbox_only": True,
        "evidence_class": "bounded_sandbox_residual_scout",
        "live_external_fetch_allowed": False,
        "summary": {
            "generated_candidate_count": len(generated_candidates),
            "executed_candidate_count": len(EXECUTED_CANDIDATES),
            "rejected_before_execution_count": len(REJECTED_BEFORE_EXECUTION),
            "near_null_control_preserved": any(
                item["candidate_id"] == "NR-SCOUT-006" and item["verdict"] == "INCONCLUSIVE"
                for item in executed_items
            ),
            "verdict_counts": dict(sorted(verdict_counts.items())),
            "canonical_results_changed": False,
            "canonical_claims_changed": False,
            "prediction_registry_changed": False,
            "claim_promotion_allowed": False,
        },
        "frozen_baseline": {
            "result_id": "RESULT-0015",
            "model_id": "model_fitted_semi_empirical",
            "coefficients": coefficients.to_dict(),
        },
        "datasets": {
            "training_residual_source": "data/nuclear_masses/nmd-0002-curated-measured-slice.yaml",
            "holdout_source": "data/nuclear_masses/post_ame2020_holdout.yaml",
            "holdout_row_count": len(post_rows),
        },
        "baseline_metrics_by_subset": baseline_metrics,
        "feature_definitions": {
            "neutron_excess_sq_over_a": "max(N - Z, 0)^2 / A",
            "neutron_excess_cu_over_a_sq": "max(N - Z, 0)^3 / A^2",
            "positive_asymmetry_fraction": "max((N - Z) / A, 0)",
            "frontier_excess_after_20_over_a": "max(N - Z - 20, 0) / A",
        },
        "generated_candidates": generated_candidates,
        "executed_items": executed_items,
        "rejected_before_execution": list(REJECTED_BEFORE_EXECUTION),
        "promotion_boundary": {
            "writes_prediction_registry": False,
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": "Maintainer review before any registry, RESULT, claim, or knowledge update.",
        },
        "limitations": [
            "Sandbox-only scout; no canonical result, claim, knowledge, or prediction registry file is updated.",
            "Feature coefficients are fit on the small 11-row NMD-0002 residual slice.",
            "Post-AME2020 evaluation uses already committed retrospective rows and is not live-measurement reveal work.",
            "Rejected candidates are preserved to document overfit and leakage boundaries.",
        ],
    }


def main() -> None:
    """Write the deterministic scout metrics artifact."""
    metrics = build_metrics()
    out_dir = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(
        json.dumps(metrics, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {metrics_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
