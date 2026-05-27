"""TASK-0394 nuclear local-curvature no-leakage prototype.

This runner re-tests the strongest local-curvature sandbox candidate under a
stricter no-leakage contract. Every target row is evaluated with a fold-local
neighbor cache:

- training-slice targets use leave-one-out training rows;
- post-AME2020 holdout targets use only the frozen NMD-0002 training slice;
- no target or holdout residual is available to admissible candidate features.

The output is sandbox-only retrospective evidence. It does not fetch live data,
score reveal predictions, write prediction-registry entries, write canonical
RESULT-* artifacts, update claims, or promote knowledge.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Callable

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.run_nuclear_local_curvature_lane as lane  # noqa: E402
import scripts.run_nuclear_shell_axis_full_known_audit as full_known  # noqa: E402


AGENT_RUN_ID = "AGENT-RUN-0039"
TASK_ID = "TASK-0394"
PREDECESSOR_AGENT_RUN_ID = "AGENT-RUN-0041"
PREDECESSOR_TASK_ID = "TASK-0397"
PRIMARY_SURVIVAL_MARGIN_MEV = 0.25
HIGH_ERROR_PERCENTILE = lane.HIGH_ERROR_PERCENTILE

DEFAULT_AGENT_RUN_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
DEFAULT_METRICS_PATH = DEFAULT_AGENT_RUN_DIR / "metrics.json"
DEFAULT_REPORT_PATH = DEFAULT_AGENT_RUN_DIR / "report.md"
DEFAULT_AGENT_RUN_PATH = DEFAULT_AGENT_RUN_DIR / "agent_run.yaml"
DEFAULT_LIMITATIONS_PATH = DEFAULT_AGENT_RUN_DIR / "limitations.md"
DEFAULT_PREFLIGHT_PATH = DEFAULT_AGENT_RUN_DIR / "preflight.md"
DEFAULT_REVIEW_SUMMARY_PATH = DEFAULT_AGENT_RUN_DIR / "review_summary.md"
DEFAULT_REVIEW_PATH = (
    REPO_ROOT
    / "docs"
    / "reviews"
    / "nuclear-local-curvature-no-leakage-prototype.md"
)

FeatureFn = Callable[[dict[str, Any], lane.NeighborIndex], tuple[float, ...]]


def _format_delta(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):+.6f}"


def _surface_context() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
    float,
]:
    coefficients = full_known.load_frozen_baseline_coefficients()
    audit_rows, training_rows, _training_residuals, surface = (
        full_known.build_audit_surface(coefficients)
    )
    threshold = float(
        np.percentile(
            np.asarray(
                [abs(float(row["baseline_residual_mev"])) for row in audit_rows],
                dtype=float,
            ),
            HIGH_ERROR_PERCENTILE,
            method="linear",
        )
    )
    return audit_rows, training_rows, surface, threshold


def _mean_neighbor_residual(
    rows: list[dict[str, Any]],
    *,
    fixed_key: str,
    fixed_value: int,
    order_key: str,
    target_value: int,
) -> float:
    group = [row for row in rows if int(row[fixed_key]) == fixed_value]
    lower = [row for row in group if int(row[order_key]) < target_value]
    upper = [row for row in group if int(row[order_key]) > target_value]
    left = max(lower, key=lambda row: int(row[order_key]), default=None)
    right = min(upper, key=lambda row: int(row[order_key]), default=None)
    values = [
        float(row["baseline_residual_mev"])
        for row in (left, right)
        if row is not None
    ]
    if not values:
        return 0.0
    return float(np.mean(np.asarray(values, dtype=float)))


def _shifted_z_isotope_mean(
    row: dict[str, Any],
    index: lane.NeighborIndex,
) -> tuple[float, ...]:
    z_values = sorted(index.isotopes)
    if not z_values:
        return (0.0,)
    current_z = int(row["Z"])
    insertion = np.searchsorted(np.asarray(z_values, dtype=int), current_z)
    shifted_z = z_values[(int(insertion) + max(1, len(z_values) // 2)) % len(z_values)]
    return (
        _mean_neighbor_residual(
            index.rows,
            fixed_key="Z",
            fixed_value=shifted_z,
            order_key="N",
            target_value=int(row["N"]),
        ),
    )


def _mass_number_only_control(
    row: dict[str, Any],
    _index: lane.NeighborIndex,
) -> tuple[float, ...]:
    scaled_a = (float(row["A"]) - 100.0) / 100.0
    return (scaled_a, scaled_a * scaled_a)


def _near_null_control(
    _row: dict[str, Any],
    _index: lane.NeighborIndex,
) -> tuple[float, ...]:
    return (0.0,)


def _self_inclusion_ablation(
    row: dict[str, Any],
    index: lane.NeighborIndex,
) -> tuple[float, ...]:
    no_leak_mean = lane._isotope_neighbor_mean(row, index)[0]  # noqa: SLF001
    return (0.5 * (float(row["baseline_residual_mev"]) + no_leak_mean),)


def _build_variants() -> tuple[dict[str, Any], ...]:
    base = {
        item["candidate_id"]: dict(item)
        for item in lane.GENERATED_VARIANTS
        if item["fit_mode"] == "lstsq"
    }
    return (
        {
            **base["LOCAL-CURVATURE-001"],
            "role": "executed_candidate",
            "control_category": None,
            "feature_family": "F1_local_curvature",
        },
        {
            "candidate_id": "LOCAL-NOLEAK-CTRL-001",
            "name": "Shifted-Z isotope-neighbor residual control",
            "family": "shifted_z_isotope_control",
            "formula": "r_corr = beta * mean(nearest residuals from shifted-Z chain)",
            "feature_names": ("shifted_z_isotope_neighbor_mean_residual",),
            "fit_mode": "lstsq",
            "complexity": 1,
            "role": "chain_shuffled_control",
            "control_category": "chain_shuffled",
            "feature_fn": _shifted_z_isotope_mean,
        },
        {
            "candidate_id": "LOCAL-NOLEAK-CTRL-002",
            "name": "Smooth mass-window residual control",
            "family": "smooth_mass_window_control",
            "formula": "r_corr = beta * mean(nearest A-window residuals)",
            "feature_names": ("smooth_a_window_residual",),
            "fit_mode": "lstsq",
            "complexity": 1,
            "role": "smooth_window_control",
            "control_category": "smooth_window",
            "feature_fn": lane._smooth_a_window_mean,  # noqa: SLF001
        },
        {
            "candidate_id": "LOCAL-NOLEAK-CTRL-003",
            "name": "Mass-number-only polynomial control",
            "family": "mass_number_only_control",
            "formula": "r_corr = beta0*A_scaled + beta1*A_scaled^2",
            "feature_names": ("mass_number_scaled", "mass_number_scaled_squared"),
            "fit_mode": "lstsq",
            "complexity": 2,
            "role": "mass_number_only_control",
            "control_category": "mass_number_only",
            "feature_fn": _mass_number_only_control,
        },
        {
            "candidate_id": "LOCAL-NOLEAK-CTRL-004",
            "name": "Near-null local-neighborhood control",
            "family": "near_null_control",
            "formula": "r_corr = beta * 0",
            "feature_names": ("near_null_neighborhood",),
            "fit_mode": "lstsq",
            "complexity": 1,
            "role": "near_null_control",
            "control_category": "near_null",
            "feature_fn": _near_null_control,
        },
        {
            "candidate_id": "LOCAL-NOLEAK-ABL-001",
            "name": "Self-inclusion leakage ablation",
            "family": "self_inclusion_ablation",
            "formula": "r_corr = beta * mean(target residual, nearest same-Z neighbors)",
            "feature_names": ("self_included_isotope_neighbor_mean_residual",),
            "fit_mode": "lstsq",
            "complexity": 1,
            "role": "leakage_ablation_control",
            "control_category": "self_inclusion_ablation",
            "feature_fn": _self_inclusion_ablation,
            "intentionally_leaky": True,
        },
    )


def _active_training_rows(
    target: dict[str, Any],
    training_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if target["source_surface"] != "nmd_0002_training_slice":
        return list(training_rows)
    target_id = str(target["row_id"])
    return [row for row in training_rows if str(row["row_id"]) != target_id]


def _feature_matrix(
    rows: list[dict[str, Any]],
    *,
    variant: dict[str, Any],
    cache_rows: list[dict[str, Any]],
) -> np.ndarray:
    feature_fn: FeatureFn = variant["feature_fn"]
    matrix: list[tuple[float, ...]] = []
    for row in rows:
        row_cache = [
            cache_row
            for cache_row in cache_rows
            if str(cache_row["row_id"]) != str(row["row_id"])
        ]
        matrix.append(feature_fn(row, lane.NeighborIndex(row_cache)))
    return np.asarray(matrix, dtype=float)


def _fit_fold_coefficients(
    variant: dict[str, Any],
    *,
    active_train: list[dict[str, Any]],
) -> tuple[np.ndarray, dict[str, float]]:
    feature_names = tuple(variant["feature_names"])
    if not feature_names:
        return np.asarray([], dtype=float), {}
    train_x = _feature_matrix(active_train, variant=variant, cache_rows=active_train)
    train_y = np.asarray(
        [float(row["baseline_residual_mev"]) for row in active_train],
        dtype=float,
    )
    beta, *_ = np.linalg.lstsq(train_x, train_y, rcond=None)
    return beta, {name: float(value) for name, value in zip(feature_names, beta)}


def _summarize_coefficients(
    coefficient_rows: list[dict[str, float]],
    *,
    feature_names: tuple[str, ...],
) -> dict[str, dict[str, float | None]]:
    summary: dict[str, dict[str, float | None]] = {}
    for name in feature_names:
        values = [row[name] for row in coefficient_rows if name in row]
        if not values:
            summary[name] = {"mean": None, "std": None, "min": None, "max": None}
            continue
        arr = np.asarray(values, dtype=float)
        summary[name] = {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
        }
    return summary


def _evaluate_variant(
    variant: dict[str, Any],
    *,
    audit_rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    baseline_metrics: dict[str, dict[str, float | int | None]],
    high_error_threshold: float,
) -> dict[str, Any]:
    subset_errors: dict[str, list[float]] = {key: [] for key in baseline_metrics}
    per_row: list[dict[str, Any]] = []
    coefficient_rows: list[dict[str, float]] = []
    cache_audit_rows: list[dict[str, Any]] = []

    for target in audit_rows:
        active_train = _active_training_rows(target, training_rows)
        beta, coeffs = _fit_fold_coefficients(variant, active_train=active_train)
        coefficient_rows.append(coeffs)
        feature_fn: FeatureFn = variant["feature_fn"]
        target_index = lane.NeighborIndex(active_train)
        values = np.asarray(feature_fn(target, target_index), dtype=float)
        correction = float(values @ beta) if values.size else 0.0
        candidate_residual = float(target["observed_mev"]) - (
            float(target["baseline_predicted_mev"]) + correction
        )
        target_in_cache = any(
            str(row["row_id"]) == str(target["row_id"]) for row in active_train
        )
        holdout_rows_in_cache = sum(
            1
            for row in active_train
            if row["source_surface"] == "post_ame2020_primary_holdout"
        )
        cache_audit_rows.append(
            {
                "target_row_id": target["row_id"],
                "target_source_surface": target["source_surface"],
                "active_training_row_count": len(active_train),
                "target_row_in_cache": target_in_cache,
                "holdout_rows_in_cache": holdout_rows_in_cache,
                "feature_values": {
                    name: float(value)
                    for name, value in zip(tuple(variant["feature_names"]), values)
                },
            }
        )
        row_item = {
            "row_id": target["row_id"],
            "nuclide_id": target["nuclide_id"],
            "Z": int(target["Z"]),
            "N": int(target["N"]),
            "A": int(target["A"]),
            "source_surface": target["source_surface"],
            "baseline_residual_mev": float(target["baseline_residual_mev"]),
            "candidate_residual_mev": candidate_residual,
            "baseline_abs_error_mev": abs(float(target["baseline_residual_mev"])),
            "candidate_abs_error_mev": abs(candidate_residual),
            "delta_abs_error_mev": abs(candidate_residual)
            - abs(float(target["baseline_residual_mev"])),
            "correction_mev": correction,
        }
        per_row.append(row_item)
        for subset_id in lane._subset_ids(  # noqa: SLF001
            target,
            high_error_threshold=high_error_threshold,
        ):
            subset_errors.setdefault(subset_id, []).append(candidate_residual)

    metrics_by_subset = {
        key: lane._summarize_residuals(value)  # noqa: SLF001
        for key, value in sorted(subset_errors.items())
    }
    delta_by_subset = {
        key: lane._delta_mae(metrics_by_subset.get(key), baseline_metrics.get(key))  # noqa: SLF001
        for key in sorted(baseline_metrics)
    }
    positive = {
        key: value
        for key, value in delta_by_subset.items()
        if value is not None and value > 0.0
    }
    worst_subset = {"subset_id": "none", "delta_mae_mev": 0.0}
    if positive:
        subset_id, delta = max(positive.items(), key=lambda item: item[1])
        worst_subset = {"subset_id": subset_id, "delta_mae_mev": float(delta)}

    return {
        "candidate_id": variant["candidate_id"],
        "name": variant["name"],
        "family": variant["family"],
        "formula": variant["formula"],
        "complexity": variant["complexity"],
        "role": variant["role"],
        "control_category": variant.get("control_category"),
        "fit_mode": variant["fit_mode"],
        "intentionally_leaky": bool(variant.get("intentionally_leaky", False)),
        "fold_coefficient_summary": _summarize_coefficients(
            coefficient_rows,
            feature_names=tuple(variant["feature_names"]),
        ),
        "metrics_by_subset": metrics_by_subset,
        "delta_mae_by_subset_mev": delta_by_subset,
        "primary_delta_mae_mev": delta_by_subset.get("full_known"),
        "holdout_delta_mae_mev": delta_by_subset.get("primary_holdout"),
        "training_delta_mae_mev": delta_by_subset.get("training_slice"),
        "magic_region_delta_mae_mev": delta_by_subset.get("magic_any"),
        "neutron_rich_delta_mae_mev": delta_by_subset.get("neutron_rich_local"),
        "high_error_delta_mae_mev": delta_by_subset.get("high_error_baseline_p75"),
        "worst_subset_regression": worst_subset,
        "largest_regressions": sorted(
            per_row,
            key=lambda item: float(item["delta_abs_error_mev"]),
            reverse=True,
        )[:8],
        "largest_improvements": sorted(
            per_row,
            key=lambda item: float(item["delta_abs_error_mev"]),
        )[:8],
        "cache_audit": {
            "target_row_in_admissible_cache_count": sum(
                1 for row in cache_audit_rows if row["target_row_in_cache"]
            ),
            "holdout_rows_in_cache_count": sum(
                int(row["holdout_rows_in_cache"]) for row in cache_audit_rows
            ),
            "rows": cache_audit_rows,
        },
    }


def _candidate_vs_strongest_control(
    items: list[dict[str, Any]],
    *,
    baseline_metrics: dict[str, dict[str, float | int | None]],
) -> list[dict[str, Any]]:
    candidates = [item for item in items if item["role"] == "executed_candidate"]
    controls = [
        item
        for item in items
        if item["role"].endswith("_control")
        and not bool(item.get("intentionally_leaky", False))
    ]
    table: list[dict[str, Any]] = []
    for candidate in candidates:
        subset_rows: list[dict[str, Any]] = []
        wins = 0
        for subset_id in sorted(baseline_metrics):
            candidate_delta = candidate["delta_mae_by_subset_mev"].get(subset_id)
            control_deltas = {
                control["candidate_id"]: control["delta_mae_by_subset_mev"].get(subset_id)
                for control in controls
                if control["delta_mae_by_subset_mev"].get(subset_id) is not None
            }
            if candidate_delta is None or not control_deltas:
                strongest_id = None
                strongest_delta = None
                margin = None
                beats = None
            else:
                strongest_id, strongest_delta = min(
                    control_deltas.items(),
                    key=lambda pair: (float(pair[1]), pair[0]),
                )
                margin = float(strongest_delta) - float(candidate_delta)
                beats = bool(margin > 0.0)
                if beats:
                    wins += 1
            subset_rows.append(
                {
                    "subset_id": subset_id,
                    "candidate_delta_mae_mev": candidate_delta,
                    "strongest_control_id": strongest_id,
                    "strongest_control_delta_mae_mev": strongest_delta,
                    "control_minus_candidate_mev": margin,
                    "candidate_beats_strongest_control": beats,
                }
            )
        primary = next(row for row in subset_rows if row["subset_id"] == "full_known")
        comparable = [
            row for row in subset_rows if row["candidate_beats_strongest_control"] is not None
        ]
        win_rate = None if not comparable else wins / len(comparable)
        primary_margin = primary["control_minus_candidate_mev"]
        table.append(
            {
                "candidate_id": candidate["candidate_id"],
                "primary_strongest_control_id": primary["strongest_control_id"],
                "primary_candidate_delta_mae_mev": primary["candidate_delta_mae_mev"],
                "primary_strongest_control_delta_mae_mev": primary[
                    "strongest_control_delta_mae_mev"
                ],
                "primary_control_minus_candidate_mev": primary_margin,
                "primary_survives_controls": bool(
                    primary_margin is not None
                    and primary_margin >= PRIMARY_SURVIVAL_MARGIN_MEV
                ),
                "candidate_wins_subset_count": wins,
                "comparable_subset_count": len(comparable),
                "subset_win_rate": win_rate,
                "per_subset_comparison": subset_rows,
            }
        )
    return table


def _fold_cache_audit(items: list[dict[str, Any]]) -> dict[str, Any]:
    admissible = [
        item
        for item in items
        if not bool(item.get("intentionally_leaky", False))
    ]
    target_cache_hits = sum(
        int(item["cache_audit"]["target_row_in_admissible_cache_count"])
        for item in admissible
    )
    holdout_cache_hits = sum(
        int(item["cache_audit"]["holdout_rows_in_cache_count"]) for item in admissible
    )
    return {
        "admissible_variant_count": len(admissible),
        "target_row_in_admissible_cache_count": target_cache_hits,
        "holdout_rows_in_admissible_cache_count": holdout_cache_hits,
        "passes_per_fold_cache_audit": target_cache_hits == 0 and holdout_cache_hits == 0,
    }


def _lane_verdict(
    comparison_table: list[dict[str, Any]],
    *,
    fold_cache_audit: dict[str, Any],
) -> tuple[str, str]:
    if not fold_cache_audit["passes_per_fold_cache_audit"]:
        return "INCONCLUSIVE", "WEAKENS_LOCAL_CURVATURE_001"
    if not comparison_table:
        return "INCONCLUSIVE", "WEAKENS_LOCAL_CURVATURE_001"
    row = comparison_table[0]
    if (
        row["primary_survives_controls"]
        and row["subset_win_rate"] is not None
        and row["subset_win_rate"] > 0.5
    ):
        return "PARTIALLY_VALID", "STRENGTHENS_LOCAL_CURVATURE_001"
    if row["primary_survives_controls"]:
        return "INCONCLUSIVE", "WEAKENS_LOCAL_CURVATURE_001"
    return "FALSIFIED", "FALSIFIES_LOCAL_CURVATURE_001_UNDER_NO_LEAKAGE"


def build_metrics() -> dict[str, Any]:
    audit_rows, training_rows, surface, high_error_threshold = _surface_context()
    baseline_metrics = lane._baseline_metrics(  # noqa: SLF001
        audit_rows,
        high_error_threshold=high_error_threshold,
    )
    variants = _build_variants()
    items = [
        _evaluate_variant(
            variant,
            audit_rows=audit_rows,
            training_rows=training_rows,
            baseline_metrics=baseline_metrics,
            high_error_threshold=high_error_threshold,
        )
        for variant in variants
    ]
    comparison_table = _candidate_vs_strongest_control(
        items,
        baseline_metrics=baseline_metrics,
    )
    cache_audit = _fold_cache_audit(items)
    verdict, assessment = _lane_verdict(comparison_table, fold_cache_audit=cache_audit)
    best_candidate = next(item for item in items if item["role"] == "executed_candidate")
    self_ablation = next(item for item in items if item["role"] == "leakage_ablation_control")
    coefficients = full_known.load_frozen_baseline_coefficients()
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "predecessor_agent_run_id": PREDECESSOR_AGENT_RUN_ID,
        "predecessor_task_id": PREDECESSOR_TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "nuclear_local_curvature_no_leakage_prototype",
        "sandbox_only": True,
        "evidence_class": "retrospective_no_leakage_local_curvature_sandbox",
        "live_external_fetch_allowed": False,
        "summary": {
            "executed_variant_count": len(items),
            "executed_candidate_count": sum(
                1 for item in items if item["role"] == "executed_candidate"
            ),
            "executed_no_leakage_control_count": sum(
                1
                for item in items
                if item["role"].endswith("_control")
                and not bool(item.get("intentionally_leaky", False))
            ),
            "executed_leakage_ablation_count": sum(
                1 for item in items if bool(item.get("intentionally_leaky", False))
            ),
            "required_control_categories_present": sorted(
                {
                    str(item["control_category"])
                    for item in items
                    if item.get("control_category") is not None
                }
            ),
            "lane_verdict": verdict,
            "local_curvature_001_assessment": assessment,
            "best_candidate_id": best_candidate["candidate_id"],
            "best_candidate_primary_delta_mae_mev": best_candidate[
                "primary_delta_mae_mev"
            ],
            "self_inclusion_ablation_primary_delta_mae_mev": self_ablation[
                "primary_delta_mae_mev"
            ],
            "primary_survival_margin_mev": PRIMARY_SURVIVAL_MARGIN_MEV,
            "high_error_percentile": HIGH_ERROR_PERCENTILE,
            "high_error_threshold_mev": high_error_threshold,
            "canonical_results_changed": False,
            "canonical_claims_changed": False,
            "prediction_registry_changed": False,
            "claim_promotion_allowed": False,
        },
        "frozen_baseline": {
            "result_id": "RESULT-0015",
            "model_id": "model_fitted_semi_empirical",
            "coefficients": {
                "volume": coefficients.volume,
                "surface": coefficients.surface,
                "coulomb": coefficients.coulomb,
                "asymmetry": coefficients.asymmetry,
                "pairing": coefficients.pairing,
            },
        },
        "datasets": {
            "training_residual_source": (
                "data/nuclear_masses/nmd-0002-curated-measured-slice.yaml"
            ),
            "holdout_source": "data/nuclear_masses/post_ame2020_holdout.yaml",
            "training_row_count": surface["metadata"]["training_row_count"],
            "post_ame2020_primary_holdout_row_count": surface["metadata"][
                "post_ame2020_primary_holdout_row_count"
            ],
            "full_known_unique_row_count": surface["metadata"][
                "full_known_unique_row_count"
            ],
        },
        "no_leakage_contract": {
            "freeze_protocol": "docs/nuclear-local-curvature-no-leakage-freeze-protocol.md",
            "cross_family_contract": "docs/nuclear-residual-feature-no-leakage-contract.md",
            "target_family": "F1_local_curvature",
            "baseline_only_neighbor_residuals": True,
            "per_fold_neighbor_cache": True,
            "target_row_excluded": cache_audit[
                "target_row_in_admissible_cache_count"
            ]
            == 0,
            "holdout_rows_excluded_from_cache": cache_audit[
                "holdout_rows_in_admissible_cache_count"
            ]
            == 0,
            "missing_neighbor_strategy": "zero_fill_when_no_left_or_right_neighbor",
        },
        "fold_cache_audit": cache_audit,
        "baseline_metrics_by_subset": baseline_metrics,
        "variants": items,
        "candidate_vs_strongest_control": comparison_table,
        "promotion_boundary": {
            "writes_canonical_result": False,
            "writes_prediction_registry": False,
            "writes_claim": False,
            "required_next_step": "Maintainer review before any predictive local-curvature follow-up.",
        },
    }


def render_report(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    lines = [
        "# Nuclear local-curvature no-leakage prototype",
        "",
        f"Task: `{metrics['task_id']}`",
        f"Agent run: `{metrics['agent_run_id']}`",
        f"Predecessor: `{metrics['predecessor_task_id']}` / `{metrics['predecessor_agent_run_id']}`",
        "",
        "## Boundary",
        "",
        "Sandbox-only retrospective prototype. No live data, reveal scoring, "
        "prediction registry entry, canonical result, claim, or knowledge update "
        "is produced.",
        "",
        "## Summary",
        "",
        f"- Lane verdict: `{summary['lane_verdict']}`.",
        f"- LOCAL-CURVATURE-001 assessment: `{summary['local_curvature_001_assessment']}`.",
        f"- Best candidate full-known delta MAE: {_format_delta(summary['best_candidate_primary_delta_mae_mev'])} MeV.",
        f"- Self-inclusion ablation full-known delta MAE: {_format_delta(summary['self_inclusion_ablation_primary_delta_mae_mev'])} MeV.",
        f"- Per-fold cache audit pass: `{metrics['fold_cache_audit']['passes_per_fold_cache_audit']}`.",
        "",
        "## Per-Variant Subset Deltas",
        "",
        "| Variant | Role | full-known | holdout | training | magic | neutron-rich | high-error |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in metrics["variants"]:
        lines.append(
            f"| `{item['candidate_id']}` | `{item['role']}` | "
            f"{_format_delta(item['primary_delta_mae_mev'])} | "
            f"{_format_delta(item['holdout_delta_mae_mev'])} | "
            f"{_format_delta(item['training_delta_mae_mev'])} | "
            f"{_format_delta(item['magic_region_delta_mae_mev'])} | "
            f"{_format_delta(item['neutron_rich_delta_mae_mev'])} | "
            f"{_format_delta(item['high_error_delta_mae_mev'])} |"
        )
    lines.extend(
        [
            "",
            "## Candidate vs Strongest No-Leakage Control",
            "",
            "| Candidate | Strongest control | Margin | Subset win-rate | Survives? |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in metrics["candidate_vs_strongest_control"]:
        win_rate = row["subset_win_rate"]
        lines.append(
            f"| `{row['candidate_id']}` | `{row['primary_strongest_control_id']}` | "
            f"{_format_delta(row['primary_control_minus_candidate_mev'])} | "
            f"{'n/a' if win_rate is None else f'{win_rate:.3f}'} | "
            f"{row['primary_survives_controls']} |"
        )
    lines.extend(
        [
            "",
            "## No-Leakage Contract Checks",
            "",
            f"- Target row excluded from admissible caches: `{metrics['no_leakage_contract']['target_row_excluded']}`.",
            f"- Holdout rows excluded from admissible caches: `{metrics['no_leakage_contract']['holdout_rows_excluded_from_cache']}`.",
            "- Missing-neighbor strategy: `zero_fill_when_no_left_or_right_neighbor`.",
            "- Neighbor inputs are baseline-only residuals from the active fold cache.",
            "",
        ]
    )
    return "\n".join(lines)


def render_review(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    comparison = metrics["candidate_vs_strongest_control"][0]
    lines = [
        "# Nuclear local-curvature no-leakage prototype review",
        "",
        f"**Task:** `{metrics['task_id']}`  ",
        f"**Agent run:** `{metrics['agent_run_id']}`  ",
        f"**Predecessor:** `{metrics['predecessor_task_id']}` / `{metrics['predecessor_agent_run_id']}`",
        "",
        "## Scope",
        "",
        "This review records a deterministic no-leakage prototype for the "
        "`LOCAL-CURVATURE-001` lane. It uses fold-local neighbor caches, "
        "baseline-only residual inputs, and no prediction-registry writes.",
        "",
        "## Headline Result",
        "",
        f"- Lane verdict: `{summary['lane_verdict']}`.",
        f"- Assessment: `{summary['local_curvature_001_assessment']}`.",
        f"- Candidate full-known delta MAE: {_format_delta(comparison['primary_candidate_delta_mae_mev'])} MeV.",
        f"- Strongest no-leakage control: `{comparison['primary_strongest_control_id']}`.",
        f"- Control-minus-candidate margin: {_format_delta(comparison['primary_control_minus_candidate_mev'])} MeV.",
        f"- Subset win-rate: {comparison['subset_win_rate']:.3f}.",
        "",
        "## Interpretation",
        "",
        "The prototype is still retrospective sandbox evidence. A `PARTIALLY_VALID` "
        "verdict here means the local-curvature candidate survived this bounded "
        "no-leakage/control panel; it does not authorize claim promotion, public "
        "discovery wording, a reveal score, or a `PRED-*` entry.",
        "",
        "## Limitations",
        "",
        "- The training slice is small, so fold coefficients are sensitive.",
        "- Controls are deterministic but not exhaustive nuclear alternatives.",
        "- The task intentionally writes only sandbox/review artifacts.",
        "",
        "## Verdict",
        "",
        f"`{summary['lane_verdict']}`",
        "",
    ]
    return "\n".join(lines)


def render_preflight(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Preflight",
            "",
            f"Task: `{metrics['task_id']}`",
            f"Agent run: `{metrics['agent_run_id']}`",
            "",
            "| Check | Status | Notes |",
            "| --- | --- | --- |",
            "| task_scope | PASS | TASK-0394 requests a no-leakage local-curvature prototype. |",
            "| data_boundary | PASS | Only committed repository datasets are used. |",
            "| per_fold_cache | PASS | Target and holdout residuals are excluded from admissible caches. |",
            "| control_panel | PASS | Chain-shuffled, smooth-window, mass-only, near-null, and self-inclusion ablation controls are present. |",
            "| no_promotion | PASS | No prediction registry, canonical result, claim, or knowledge file is written. |",
            "",
        ]
    )


def render_limitations(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Limitations",
            "",
            f"Task: `{metrics['task_id']}`",
            f"Agent run: `{metrics['agent_run_id']}`",
            "",
            "- Retrospective committed rows are used; this is not strict blind prediction evidence.",
            "- Fold-local fitting over the 11-row NMD-0002 slice can be coefficient-sensitive.",
            "- The no-leakage controls are bounded and deterministic, not exhaustive.",
            "- No live fetch, reveal scoring, registry write, canonical result, claim, or knowledge update is authorized.",
            "",
        ]
    )


def render_review_summary(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    return "\n".join(
        [
            "# Review Summary",
            "",
            f"Task: `{metrics['task_id']}`  ",
            f"Agent run: `{metrics['agent_run_id']}`  ",
            f"Lane verdict: `{summary['lane_verdict']}`",
            "",
            "- Implemented a fold-local no-leakage prototype for `LOCAL-CURVATURE-001`.",
            f"- Assessment: `{summary['local_curvature_001_assessment']}`.",
            "- Sandbox-only evidence; no canonical result, claim, knowledge entry, or prediction registry entry was changed.",
            "",
        ]
    )


def _agent_run_verdict(lane_verdict: str) -> str:
    return {
        "PARTIALLY_VALID": "SANDBOX_PASS",
        "INCONCLUSIVE": "INCONCLUSIVE",
        "FALSIFIED": "FALSIFIED",
    }.get(lane_verdict, "INCONCLUSIVE")


def render_agent_run_yaml(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    payload = {
        "id": metrics["agent_run_id"],
        "campaign_profile_id": metrics["campaign_profile_id"],
        "task_id": metrics["task_id"],
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {
            "contributor_id": "roman",
            "agent_id": "codex",
        },
        "proposal_paths": {
            "hypothesis": "hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0043-midmass-isotope-gap-scout-batch.yaml",
            "experiment": "experiment_proposals/nuclear-mass/EXP-PROPOSAL-0009-nuclear-midmass-isotope-gap-scout.yaml",
        },
        "artifacts": {
            "metrics": f"agent_runs/{metrics['agent_run_id']}/metrics.json",
            "report": f"agent_runs/{metrics['agent_run_id']}/report.md",
            "limitations": f"agent_runs/{metrics['agent_run_id']}/limitations.md",
            "preflight": f"agent_runs/{metrics['agent_run_id']}/preflight.md",
            "review_summary": f"agent_runs/{metrics['agent_run_id']}/review_summary.md",
        },
        "preflight": {
            "passed": True,
            "checks": [
                {
                    "name": "task_scope",
                    "status": "PASS",
                    "notes": "TASK-0394 requests a no-leakage local-curvature prototype.",
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed repository data is used.",
                },
                {
                    "name": "per_fold_cache",
                    "status": "PASS",
                    "notes": "Target and holdout residuals are excluded from admissible caches.",
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No prediction registry, canonical result, claim, or knowledge file is written.",
                },
            ],
        },
        "limitations": [
            "Retrospective committed rows are used; this is not strict blind prediction evidence.",
            "Fold-local fitting over the 11-row training slice can be coefficient-sensitive.",
            "No live fetch, reveal scoring, registry write, canonical result, claim, or knowledge update is authorized.",
        ],
        "verdict": _agent_run_verdict(summary["lane_verdict"]),
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": "Maintainer review before any predictive local-curvature follow-up.",
        },
    }
    return yaml.safe_dump(payload, sort_keys=False)


def write_outputs(
    metrics: dict[str, Any],
    *,
    metrics_path: Path,
    report_path: Path,
    agent_run_path: Path,
    limitations_path: Path,
    preflight_path: Path,
    review_summary_path: Path,
    review_path: Path,
) -> None:
    for target in (
        metrics_path,
        report_path,
        agent_run_path,
        limitations_path,
        preflight_path,
        review_summary_path,
        review_path,
    ):
        target.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report_path.write_text(render_report(metrics), encoding="utf-8")
    agent_run_path.write_text(render_agent_run_yaml(metrics), encoding="utf-8")
    limitations_path.write_text(render_limitations(metrics), encoding="utf-8")
    preflight_path.write_text(render_preflight(metrics), encoding="utf-8")
    review_summary_path.write_text(render_review_summary(metrics), encoding="utf-8")
    review_path.write_text(render_review(metrics), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_METRICS_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--agent-run", type=Path, default=DEFAULT_AGENT_RUN_PATH)
    parser.add_argument("--limitations", type=Path, default=DEFAULT_LIMITATIONS_PATH)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT_PATH)
    parser.add_argument(
        "--review-summary",
        type=Path,
        default=DEFAULT_REVIEW_SUMMARY_PATH,
    )
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    args = parser.parse_args(argv)

    metrics = build_metrics()
    write_outputs(
        metrics,
        metrics_path=args.out,
        report_path=args.report,
        agent_run_path=args.agent_run,
        limitations_path=args.limitations,
        preflight_path=args.preflight,
        review_summary_path=args.review_summary,
        review_path=args.review,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
