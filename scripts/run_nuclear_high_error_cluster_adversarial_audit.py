"""TASK-0367 high-error cluster adversarial stability audit.

Re-evaluates the TASK-0343 / AGENT-RUN-0030 high-error cluster sandbox
signal against stronger adversarial controls and small-sample coefficient
stability checks. The runner is deterministic and sandbox-only: it uses only
committed repository inputs, does not fetch live data, does not score reveal
or prediction-registry entries, does not write canonical RESULT-* artifacts,
and does not promote claims.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.run_nuclear_high_error_cluster_lane as lane  # noqa: E402
import scripts.run_nuclear_shell_axis_full_known_audit as full_known  # noqa: E402


AGENT_RUN_ID = "AGENT-RUN-0033"
TASK_ID = "TASK-0367"
HIGH_ERROR_PERCENTILE = lane.HIGH_ERROR_PERCENTILE
PERTURBED_HIGH_ERROR_PERCENTILE = 80.0
PRIMARY_SURVIVAL_MARGIN_MEV = 0.25
MATERIAL_NON_HIGH_ERROR_REGRESSION_MEV = 0.25

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
    / "nuclear-high-error-cluster-adversarial-stability.md"
)


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _format_delta(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):+.6f}"


def _threshold_perturbed_near_magic(
    row: dict[str, Any],
    _index: lane.ClusterIndex,
    *,
    threshold: float,
) -> tuple[float, ...]:
    is_high_error = abs(float(row["baseline_residual_mev"])) >= threshold
    return (1.0 if is_high_error and lane._near_magic(row) else 0.0,)  # noqa: SLF001


def _smooth_a_local_density_control(
    row: dict[str, Any], index: lane.ClusterIndex
) -> tuple[float, ...]:
    scaled_a = lane._scaled_a(row)  # noqa: SLF001
    local_density_scaled = float(index.local_density(row)) / 20.0
    return (scaled_a, scaled_a * scaled_a, local_density_scaled)


def _near_null_control(
    _row: dict[str, Any], _index: lane.ClusterIndex
) -> tuple[float, ...]:
    return (0.0,)


def _build_adversarial_variants(
    *, perturbed_high_error_threshold: float
) -> tuple[dict[str, Any], ...]:
    base = {
        item["candidate_id"]: dict(item)
        for item in lane.GENERATED_VARIANTS
        if item["fit_mode"] == "lstsq"
    }
    variants: list[dict[str, Any]] = [
        base[item_id]
        for item_id in (
            "HIGHCLUSTER-001",
            "HIGHCLUSTER-002",
            "HIGHCLUSTER-003",
            "HIGHCLUSTER-CONTROL-001",
            "HIGHCLUSTER-CONTROL-002",
            "HIGHCLUSTER-CONTROL-003",
        )
    ]
    variants.extend(
        (
            {
                "candidate_id": "HIGHCLUSTER-CONTROL-004",
                "name": "Perturbed high-error threshold near-magic control",
                "family": "high_error_threshold_perturbation_control",
                "formula": "r_corr = beta * I(|baseline_residual| >= p80 and near_magic)",
                "feature_names": ("near_magic_high_error_p80",),
                "fit_mode": "lstsq",
                "complexity": 1,
                "role": "high_error_threshold_perturbation_control",
                "feature_fn": lambda row, index: _threshold_perturbed_near_magic(
                    row, index, threshold=perturbed_high_error_threshold
                ),
            },
            {
                "candidate_id": "HIGHCLUSTER-CONTROL-005",
                "name": "Smooth-A plus local-density control",
                "family": "smooth_a_local_density_control",
                "formula": "r_corr = beta0*A_scaled + beta1*A_scaled^2 + beta2*local_density_scaled",
                "feature_names": (
                    "smooth_a_scaled",
                    "smooth_a_scaled_squared",
                    "local_density_scaled",
                ),
                "fit_mode": "lstsq",
                "complexity": 3,
                "role": "smooth_a_local_density_control",
                "feature_fn": _smooth_a_local_density_control,
            },
            {
                "candidate_id": "HIGHCLUSTER-CONTROL-006",
                "name": "Near-null zero-feature control",
                "family": "near_null_control",
                "formula": "r_corr = beta * 0",
                "feature_names": ("near_null_zero_feature",),
                "fit_mode": "lstsq",
                "complexity": 1,
                "role": "near_null_control",
                "feature_fn": _near_null_control,
            },
        )
    )
    return tuple(variants)


def _surface_and_index() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    np.ndarray,
    dict[str, Any],
    float,
    float,
    lane.ClusterIndex,
]:
    coefficients = full_known.load_frozen_baseline_coefficients()
    audit_rows, training_rows, training_residuals, surface = (
        full_known.build_audit_surface(coefficients)
    )
    abs_residuals = np.asarray(
        [abs(float(row["baseline_residual_mev"])) for row in audit_rows],
        dtype=float,
    )
    high_error_threshold = float(
        np.percentile(abs_residuals, HIGH_ERROR_PERCENTILE, method="linear")
    )
    perturbed_threshold = float(
        np.percentile(
            abs_residuals,
            PERTURBED_HIGH_ERROR_PERCENTILE,
            method="linear",
        )
    )
    index = lane.ClusterIndex(audit_rows, high_error_threshold)
    return (
        audit_rows,
        training_rows,
        training_residuals,
        surface,
        high_error_threshold,
        perturbed_threshold,
        index,
    )


def _evaluate_all_variants(
    variants: tuple[dict[str, Any], ...],
    *,
    audit_rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
    index: lane.ClusterIndex,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, float | int | None]]]:
    baseline_metrics = lane._baseline_metrics(audit_rows, index=index)  # noqa: SLF001
    items = [
        lane._evaluate_variant(  # noqa: SLF001
            variant,
            audit_rows=audit_rows,
            training_rows=training_rows,
            training_residuals=training_residuals,
            baseline_metrics=baseline_metrics,
            index=index,
        )
        for variant in variants
    ]
    return items, baseline_metrics


def _residuals_from_item(
    item: dict[str, Any],
    rows: list[dict[str, Any]],
    *,
    variants_by_id: dict[str, dict[str, Any]],
    index: lane.ClusterIndex,
) -> list[float]:
    variant = variants_by_id[item["candidate_id"]]
    beta = np.asarray(
        [item["fitted_coefficients"][name] for name in variant["feature_names"]],
        dtype=float,
    )
    residuals, _ = lane._candidate_residuals(  # noqa: SLF001
        rows, variant=variant, beta=beta, index=index
    )
    return residuals


def _mae_delta_for_indices(
    candidate_residuals: list[float],
    baseline_residuals: list[float],
    indices: list[int],
) -> float | None:
    if not indices:
        return None
    candidate_mae = float(
        np.mean(np.asarray([abs(candidate_residuals[idx]) for idx in indices]))
    )
    baseline_mae = float(
        np.mean(np.asarray([abs(baseline_residuals[idx]) for idx in indices]))
    )
    return candidate_mae - baseline_mae


def _chain_transfer_summary(
    rows: list[dict[str, Any]],
    items: list[dict[str, Any]],
    *,
    variants_by_id: dict[str, dict[str, Any]],
    index: lane.ClusterIndex,
    group_key: str,
) -> dict[str, Any]:
    groups: dict[int, list[int]] = {}
    for idx, row in enumerate(rows):
        groups.setdefault(int(row[group_key]), []).append(idx)

    baseline_residuals = [float(row["baseline_residual_mev"]) for row in rows]
    residuals_by_id = {
        item["candidate_id"]: _residuals_from_item(
            item, rows, variants_by_id=variants_by_id, index=index
        )
        for item in items
    }
    group_items: list[dict[str, Any]] = []
    for group_value, indices in sorted(groups.items()):
        deltas = {
            candidate_id: _mae_delta_for_indices(values, baseline_residuals, indices)
            for candidate_id, values in residuals_by_id.items()
        }
        valid_deltas = {key: value for key, value in deltas.items() if value is not None}
        best_id = None
        best_delta = None
        if valid_deltas:
            best_id, best_delta = min(
                valid_deltas.items(), key=lambda item: (float(item[1]), item[0])
            )
        high_error_rows = [rows[idx] for idx in indices if index.is_high_error(rows[idx])]
        group_items.append(
            {
                "group_id": f"{group_key}_{group_value:03d}",
                group_key: group_value,
                "row_count": len(indices),
                "high_error_row_count": len(high_error_rows),
                "diagnostic_class": (
                    "interpretable" if len(indices) >= lane.CHAIN_MIN_ROWS else "too_sparse"
                ),
                "baseline_mae_mev": float(
                    np.mean(np.asarray([abs(baseline_residuals[idx]) for idx in indices]))
                ),
                "delta_mae_by_candidate_mev": deltas,
                "best_candidate_id": best_id,
                "best_delta_mae_mev": best_delta,
            }
        )

    interpretable = [
        item for item in group_items if item["diagnostic_class"] == "interpretable"
    ]
    by_candidate: dict[str, dict[str, Any]] = {}
    for candidate_id in residuals_by_id:
        deltas = [
            item["delta_mae_by_candidate_mev"][candidate_id]
            for item in interpretable
            if item["delta_mae_by_candidate_mev"][candidate_id] is not None
        ]
        by_candidate[candidate_id] = {
            "interpretable_group_count": len(deltas),
            "improved_group_count": sum(1 for value in deltas if float(value) < 0.0),
            "worsened_group_count": sum(1 for value in deltas if float(value) > 0.0),
            "neutral_group_count": sum(1 for value in deltas if float(value) == 0.0),
            "improvement_rate": (None if not deltas else sum(1 for value in deltas if float(value) < 0.0) / len(deltas)),
            "mean_delta_mae_mev": (
                None if not deltas else float(np.mean(np.asarray(deltas, dtype=float)))
            ),
            "min_delta_mae_mev": None if not deltas else float(min(deltas)),
            "max_delta_mae_mev": None if not deltas else float(max(deltas)),
        }
    return {
        "group_key": group_key,
        "group_count": len(group_items),
        "interpretable_group_count": len(interpretable),
        "too_sparse_group_count": len(group_items) - len(interpretable),
        "by_candidate": by_candidate,
        "group_items": group_items,
    }


def _candidate_vs_strongest_control_table(
    items: list[dict[str, Any]],
    *,
    baseline_metrics: dict[str, dict[str, float | int | None]],
) -> list[dict[str, Any]]:
    candidates = [item for item in items if item["role"] == "executed_candidate"]
    controls = [item for item in items if item["role"].endswith("_control")]
    table: list[dict[str, Any]] = []
    for candidate in candidates:
        per_subset: list[dict[str, Any]] = []
        candidate_wins_subset_count = 0
        for subset_id in sorted(baseline_metrics):
            candidate_delta = candidate["delta_mae_by_subset_mev"].get(subset_id)
            usable = {
                control["candidate_id"]: control["delta_mae_by_subset_mev"].get(subset_id)
                for control in controls
                if control["delta_mae_by_subset_mev"].get(subset_id) is not None
            }
            if not usable or candidate_delta is None:
                strongest_control_id = None
                strongest_control_delta = None
                margin = None
                beats_strongest = None
            else:
                strongest_control_id, strongest_control_delta = min(
                    usable.items(), key=lambda item: (float(item[1]), item[0])
                )
                margin = float(strongest_control_delta) - float(candidate_delta)
                beats_strongest = margin > 0.0
                if beats_strongest:
                    candidate_wins_subset_count += 1
            per_subset.append(
                {
                    "subset_id": subset_id,
                    "candidate_delta_mae_mev": candidate_delta,
                    "strongest_control_id": strongest_control_id,
                    "strongest_control_delta_mae_mev": strongest_control_delta,
                    "control_minus_candidate_mev": margin,
                    "candidate_beats_strongest_control": beats_strongest,
                }
            )
        primary = next(
            row for row in per_subset if row["subset_id"] == "full_known"
        )
        comparable = [
            row for row in per_subset if row["candidate_beats_strongest_control"] is not None
        ]
        subset_win_rate = (
            None
            if not comparable
            else candidate_wins_subset_count / float(len(comparable))
        )
        primary_margin = primary["control_minus_candidate_mev"]
        primary_survives = bool(
            primary_margin is not None
            and primary_margin >= PRIMARY_SURVIVAL_MARGIN_MEV
        )
        non_high_error_delta = _float_or_none(candidate["non_high_error_delta_mae_mev"])
        high_error_delta = _float_or_none(candidate["high_error_delta_mae_mev"])
        material_non_high_error_regression = bool(
            non_high_error_delta is not None
            and non_high_error_delta > MATERIAL_NON_HIGH_ERROR_REGRESSION_MEV
        )
        only_high_error_improves = bool(
            high_error_delta is not None
            and high_error_delta < 0.0
            and material_non_high_error_regression
        )
        table.append(
            {
                "candidate_id": candidate["candidate_id"],
                "primary_strongest_control_id": primary["strongest_control_id"],
                "primary_candidate_delta_mae_mev": primary["candidate_delta_mae_mev"],
                "primary_strongest_control_delta_mae_mev": primary[
                    "strongest_control_delta_mae_mev"
                ],
                "primary_control_minus_candidate_mev": primary_margin,
                "primary_survives_adversarial_controls": primary_survives,
                "candidate_wins_subset_count": candidate_wins_subset_count,
                "comparable_subset_count": len(comparable),
                "subset_win_rate": subset_win_rate,
                "material_non_high_error_regression": material_non_high_error_regression,
                "only_high_error_improvement_flag": only_high_error_improves,
                "per_subset": per_subset,
            }
        )
    return table


def _adversarial_verdict(table: list[dict[str, Any]]) -> str:
    if not table:
        return "INCONCLUSIVE"
    usable = [
        item
        for item in table
        if not item["material_non_high_error_regression"]
        and not item["only_high_error_improvement_flag"]
    ]
    primary_survivors = [
        item for item in usable if item["primary_survives_adversarial_controls"]
    ]
    subset_dominators = [
        item
        for item in usable
        if item["subset_win_rate"] is not None and item["subset_win_rate"] > 0.5
    ]
    if any(
        survivor["candidate_id"] == dominator["candidate_id"]
        for survivor in primary_survivors
        for dominator in subset_dominators
    ):
        return "PARTIALLY_VALID"
    if primary_survivors or subset_dominators:
        return "INCONCLUSIVE"
    return "FALSIFIED"


def _subset_deltas_for_residuals(
    rows: list[dict[str, Any]],
    residuals: list[float],
    *,
    baseline_metrics: dict[str, dict[str, float | int | None]],
    index: lane.ClusterIndex,
) -> dict[str, float | None]:
    subset_errors: dict[str, list[float]] = {key: [] for key in baseline_metrics}
    for row, residual in zip(rows, residuals):
        for subset_id in lane._subset_ids(row, index):  # noqa: SLF001
            subset_errors.setdefault(subset_id, []).append(residual)
    return {
        subset_id: lane._delta_mae(  # noqa: SLF001
            lane._summarize_residuals(values),  # noqa: SLF001
            baseline_metrics.get(subset_id),
        )
        for subset_id, values in sorted(subset_errors.items())
    }


def _candidate_stability(
    variants: tuple[dict[str, Any], ...],
    *,
    audit_rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    baseline_metrics: dict[str, dict[str, float | int | None]],
    index: lane.ClusterIndex,
) -> dict[str, Any]:
    candidate_variants = [
        variant for variant in variants if variant["role"] == "executed_candidate"
    ]
    items: list[dict[str, Any]] = []
    for variant in candidate_variants:
        folds: list[dict[str, Any]] = []
        for omitted in training_rows:
            fold_training_rows = [
                row
                for row in training_rows
                if str(row["row_id"]) != str(omitted["row_id"])
            ]
            fold_residuals = np.asarray(
                [float(row["baseline_residual_mev"]) for row in fold_training_rows],
                dtype=float,
            )
            beta, coefficients = lane._fit_variant(  # noqa: SLF001
                variant,
                training_rows=fold_training_rows,
                training_residuals=fold_residuals,
                index=index,
            )
            residuals, _ = lane._candidate_residuals(  # noqa: SLF001
                audit_rows, variant=variant, beta=beta, index=index
            )
            subset_deltas = _subset_deltas_for_residuals(
                audit_rows,
                residuals,
                baseline_metrics=baseline_metrics,
                index=index,
            )
            folds.append(
                {
                    "omitted_row_id": str(omitted["row_id"]),
                    "omitted_nuclide_id": str(omitted["nuclide_id"]),
                    "coefficients": coefficients,
                    "full_known_delta_mae_mev": subset_deltas.get("full_known"),
                    "holdout_delta_mae_mev": subset_deltas.get("holdout"),
                    "high_error_delta_mae_mev": subset_deltas.get(
                        "high_error_baseline_p75"
                    ),
                    "non_high_error_delta_mae_mev": subset_deltas.get(
                        "non_high_error_baseline_p75"
                    ),
                }
            )
        coefficient_summary: dict[str, dict[str, Any]] = {}
        for name in variant["feature_names"]:
            values = np.asarray(
                [float(fold["coefficients"][name]) for fold in folds],
                dtype=float,
            )
            observed_signs = sorted(
                {
                    -1 if value < -1e-12 else 1 if value > 1e-12 else 0
                    for value in values
                }
            )
            coefficient_summary[name] = {
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "observed_signs": observed_signs,
                "sign_flipped": (-1 in observed_signs and 1 in observed_signs),
            }
        full_known_values = [
            float(fold["full_known_delta_mae_mev"])
            for fold in folds
            if fold["full_known_delta_mae_mev"] is not None
        ]
        high_error_values = [
            float(fold["high_error_delta_mae_mev"])
            for fold in folds
            if fold["high_error_delta_mae_mev"] is not None
        ]
        non_high_error_values = [
            float(fold["non_high_error_delta_mae_mev"])
            for fold in folds
            if fold["non_high_error_delta_mae_mev"] is not None
        ]
        items.append(
            {
                "candidate_id": variant["candidate_id"],
                "fold_count": len(folds),
                "coefficient_summary": coefficient_summary,
                "full_known_delta_range_mev": [
                    float(min(full_known_values)),
                    float(max(full_known_values)),
                ],
                "high_error_delta_range_mev": [
                    float(min(high_error_values)),
                    float(max(high_error_values)),
                ],
                "non_high_error_delta_range_mev": [
                    float(min(non_high_error_values)),
                    float(max(non_high_error_values)),
                ],
                "sign_flip_detected": any(
                    summary["sign_flipped"]
                    for summary in coefficient_summary.values()
                ),
                "fold_items": folds,
            }
        )
    return {
        "method": "deterministic_leave_one_training_row_out",
        "training_row_count": len(training_rows),
        "candidate_count": len(items),
        "items": items,
    }


def build_metrics() -> dict[str, Any]:
    (
        audit_rows,
        training_rows,
        training_residuals,
        surface,
        high_error_threshold,
        perturbed_threshold,
        index,
    ) = _surface_and_index()
    variants = _build_adversarial_variants(
        perturbed_high_error_threshold=perturbed_threshold
    )
    variants_by_id = {variant["candidate_id"]: variant for variant in variants}
    items, baseline_metrics = _evaluate_all_variants(
        variants,
        audit_rows=audit_rows,
        training_rows=training_rows,
        training_residuals=training_residuals,
        index=index,
    )
    comparison_table = _candidate_vs_strongest_control_table(
        items, baseline_metrics=baseline_metrics
    )
    verdict = _adversarial_verdict(comparison_table)
    candidate_items = [item for item in items if item["role"] == "executed_candidate"]
    best_primary = min(
        candidate_items,
        key=lambda item: (
            float("inf")
            if item["primary_delta_mae_mev"] is None
            else float(item["primary_delta_mae_mev"]),
            item["candidate_id"],
        ),
    )
    all_transfer_items = [
        item
        for item in items
        if item["role"] == "executed_candidate" or item["role"].endswith("_control")
    ]
    coefficients = full_known.load_frozen_baseline_coefficients()
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "predecessor_agent_run_id": lane.AGENT_RUN_ID,
        "predecessor_task_id": lane.TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "nuclear_high_error_cluster_adversarial_stability_audit",
        "sandbox_only": True,
        "evidence_class": "retrospective_full_known_high_error_cluster_adversarial_sandbox",
        "live_external_fetch_allowed": False,
        "summary": {
            "executed_variant_count": len(items),
            "executed_candidate_count": sum(
                1 for item in items if item["role"] == "executed_candidate"
            ),
            "executed_control_count": sum(
                1 for item in items if item["role"].endswith("_control")
            ),
            "new_adversarial_control_count": 3,
            "primary_survival_margin_mev": PRIMARY_SURVIVAL_MARGIN_MEV,
            "material_non_high_error_regression_mev": MATERIAL_NON_HIGH_ERROR_REGRESSION_MEV,
            "lane_verdict": verdict,
            "best_primary_delta_candidate_id": best_primary["candidate_id"],
            "best_primary_delta_mae_mev": best_primary["primary_delta_mae_mev"],
            "high_error_percentile": HIGH_ERROR_PERCENTILE,
            "high_error_threshold_mev": high_error_threshold,
            "perturbed_high_error_percentile": PERTURBED_HIGH_ERROR_PERCENTILE,
            "perturbed_high_error_threshold_mev": perturbed_threshold,
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
            "training_residual_source": "data/nuclear_masses/nmd-0002-curated-measured-slice.yaml",
            "holdout_source": "data/nuclear_masses/post_ame2020_holdout.yaml",
            "training_row_count": surface["metadata"]["training_row_count"],
            "post_ame2020_primary_holdout_row_count": surface["metadata"][
                "post_ame2020_primary_holdout_row_count"
            ],
            "full_known_unique_row_count": surface["metadata"][
                "full_known_unique_row_count"
            ],
        },
        "adversarial_controls": [
            {
                "candidate_id": variant["candidate_id"],
                "role": variant["role"],
                "family": variant["family"],
                "feature_names": list(variant["feature_names"]),
            }
            for variant in variants
            if variant["role"].endswith("_control")
        ],
        "baseline_metrics_by_subset": baseline_metrics,
        "candidate_items": items,
        "candidate_vs_strongest_control": comparison_table,
        "coefficient_stability": _candidate_stability(
            variants,
            audit_rows=audit_rows,
            training_rows=training_rows,
            baseline_metrics=baseline_metrics,
            index=index,
        ),
        "isotope_chain_transfer": _chain_transfer_summary(
            audit_rows,
            all_transfer_items,
            variants_by_id=variants_by_id,
            index=index,
            group_key="Z",
        ),
        "isotone_chain_transfer": _chain_transfer_summary(
            audit_rows,
            all_transfer_items,
            variants_by_id=variants_by_id,
            index=index,
            group_key="N",
        ),
        "cluster_summary": lane._cluster_summary(audit_rows, index),  # noqa: SLF001
        "promotion_boundary": {
            "writes_canonical_result": False,
            "writes_prediction_registry": False,
            "writes_claim": False,
            "required_next_step": "Maintainer review of the sandbox adversarial audit before any follow-up implementation task.",
        },
    }


def _subset_table_row(item: dict[str, Any]) -> str:
    return (
        f"| `{item['candidate_id']}` | `{item['role']}` | "
        f"{_format_delta(item['primary_delta_mae_mev'])} | "
        f"{_format_delta(item['holdout_delta_mae_mev'])} | "
        f"{_format_delta(item['high_error_delta_mae_mev'])} | "
        f"{_format_delta(item['non_high_error_delta_mae_mev'])} | "
        f"{_format_delta(item['neutron_rich_delta_mae_mev'])} | "
        f"{_format_delta(item['magic_region_delta_mae_mev'])} | "
        f"{_format_delta(item['light_a_warning_delta_mae_mev'])} |"
    )


def render_report(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    lines = [
        "# Nuclear high-error cluster adversarial stability audit",
        "",
        f"Task: `{metrics['task_id']}`",
        f"Agent run: `{metrics['agent_run_id']}`",
        f"Predecessor: `{metrics['predecessor_task_id']}` / `{metrics['predecessor_agent_run_id']}`",
        "",
        "## Boundary",
        "",
        "Sandbox-only retrospective audit. No live data, reveal scoring, prediction registry entry, canonical result, claim, or knowledge update is produced.",
        "",
        "## Summary",
        "",
        f"- Lane verdict: `{summary['lane_verdict']}`.",
        f"- High-error threshold: {summary['high_error_threshold_mev']:.6f} MeV at p{summary['high_error_percentile']:.1f}.",
        f"- Perturbed threshold control: {summary['perturbed_high_error_threshold_mev']:.6f} MeV at p{summary['perturbed_high_error_percentile']:.1f}.",
        f"- Executed candidates: {summary['executed_candidate_count']}; controls: {summary['executed_control_count']}.",
        "",
        "## Subset Delta MAE",
        "",
        "| Variant | Role | full-known | holdout | high-error | non-high-error | neutron-rich | magic | light-A |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in metrics["candidate_items"]:
        lines.append(_subset_table_row(item))
    lines.extend(
        [
            "",
            "## Candidate vs Strongest Control",
            "",
            "| Candidate | Strongest control on full-known | Margin | Subset win-rate | Non-high-error regression flag |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for comparison in metrics["candidate_vs_strongest_control"]:
        lines.append(
            f"| `{comparison['candidate_id']}` | `{comparison['primary_strongest_control_id']}` | "
            f"{_format_delta(comparison['primary_control_minus_candidate_mev'])} | "
            f"{comparison['subset_win_rate']:.3f} | "
            f"{comparison['material_non_high_error_regression']} |"
        )
    lines.extend(
        [
            "",
            "## Coefficient Stability",
            "",
            "| Candidate | Folds | Sign flip? | full-known delta range | high-error delta range | non-high-error delta range |",
            "| --- | ---: | --- | ---: | ---: | ---: |",
        ]
    )
    for item in metrics["coefficient_stability"]["items"]:
        full_range = item["full_known_delta_range_mev"]
        high_range = item["high_error_delta_range_mev"]
        non_range = item["non_high_error_delta_range_mev"]
        lines.append(
            f"| `{item['candidate_id']}` | {item['fold_count']} | "
            f"{item['sign_flip_detected']} | "
            f"{full_range[0]:+.6f} to {full_range[1]:+.6f} | "
            f"{high_range[0]:+.6f} to {high_range[1]:+.6f} | "
            f"{non_range[0]:+.6f} to {non_range[1]:+.6f} |"
        )
    lines.extend(
        [
            "",
            "## Chain Transfer",
            "",
            "| Candidate | Isotope interpretable groups | Isotope improvement rate | Isotone interpretable groups | Isotone improvement rate |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    isotope = metrics["isotope_chain_transfer"]["by_candidate"]
    isotone = metrics["isotone_chain_transfer"]["by_candidate"]
    for candidate_id in sorted(
        item["candidate_id"]
        for item in metrics["candidate_items"]
        if item["role"] == "executed_candidate"
    ):
        z_row = isotope[candidate_id]
        n_row = isotone[candidate_id]
        lines.append(
            f"| `{candidate_id}` | {z_row['interpretable_group_count']} | "
            f"{z_row['improvement_rate']:.3f} | "
            f"{n_row['interpretable_group_count']} | {n_row['improvement_rate']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The audit preserves the predecessor high-error cluster lane only as sandbox diagnostic evidence if a candidate beats the strongest control by the configured margin and does not materially regress non-high-error rows. Negative or inconclusive outcomes are retained in the artifacts and do not authorize claim promotion.",
            "",
        ]
    )
    return "\n".join(lines)


def render_review(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    return "\n".join(
        [
            "# Nuclear high-error cluster adversarial stability review",
            "",
            f"**Task:** `{metrics['task_id']}`  ",
            f"**Agent run:** `{metrics['agent_run_id']}`  ",
            f"**Predecessor:** `{metrics['predecessor_task_id']}` / `{metrics['predecessor_agent_run_id']}`",
            "",
            "## Scope",
            "",
            "This review attacks the TASK-0343 high-error cluster sandbox signal with stronger adversarial controls: cluster-label permutation, high-error threshold perturbation, smooth-A/local-density, and near-null controls. It also records deterministic leave-one-training-row-out coefficient stability.",
            "",
            "## Headline Result",
            "",
            f"- Lane verdict: `{summary['lane_verdict']}`.",
            f"- Best primary delta candidate: `{summary['best_primary_delta_candidate_id']}` with delta MAE {_format_delta(summary['best_primary_delta_mae_mev'])} MeV.",
            f"- Primary survival margin: {summary['primary_survival_margin_mev']:.2f} MeV.",
            "",
            "## Candidate vs Strongest Control",
            "",
            "| Candidate | Strongest control | Margin | Subset win-rate | Flags |",
            "| --- | --- | ---: | ---: | --- |",
            *[
                (
                    f"| `{row['candidate_id']}` | `{row['primary_strongest_control_id']}` | "
                    f"{_format_delta(row['primary_control_minus_candidate_mev'])} | "
                    f"{row['subset_win_rate']:.3f} | "
                    f"non-high-error={row['material_non_high_error_regression']}, "
                    f"only-high-error={row['only_high_error_improvement_flag']} |"
                )
                for row in metrics["candidate_vs_strongest_control"]
            ],
            "",
            "## Limitations",
            "",
            "- The audit is retrospective and uses committed full-known residual labels.",
            "- The coefficient stability check is small-sample leave-one-training-row-out, not a blind predictive validation.",
            "- The controls are stronger than the predecessor lane controls but are not exhaustive.",
            "- No live data, reveal scoring, registry entry, canonical result, claim, or knowledge update is produced.",
            "",
            "## Verdict",
            "",
            f"`{summary['lane_verdict']}`",
            "",
        ]
    )


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
            "| task_scope | PASS | TASK-0367 requests a high-error cluster adversarial stability audit; this run produces sandbox artifacts only. |",
            "| data_boundary | PASS | Only committed repository datasets and predecessor lane helpers are used. |",
            "| adversarial_controls | PASS | Cluster-label permutation, threshold perturbation, smooth-A/local-density, and near-null controls are present. |",
            "| stability | PASS | Deterministic leave-one-training-row-out coefficient stability is recorded for executed candidates. |",
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
            "- The audit is retrospective and depends on committed full-known baseline residual labels.",
            "- The high-error threshold perturbation uses p80 as one deterministic stronger threshold; other perturbations may differ.",
            "- The smooth-A/local-density control is intentionally simple and does not exhaust all smoothers.",
            "- Leave-one-training-row-out stability is deterministic but limited by the small training residual slice.",
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
            "- Re-evaluated HIGHCLUSTER-001 through HIGHCLUSTER-003 against six controls, including three stronger controls added here.",
            f"- High-error threshold p75={summary['high_error_threshold_mev']:.6f} MeV; perturbed p80={summary['perturbed_high_error_threshold_mev']:.6f} MeV.",
            "- Recorded full-known, holdout, high-error, non-high-error, neutron-rich, magic-region, light-A, isotope-chain, and isotone-chain diagnostics.",
            "- Preserved all negative and inconclusive outputs as sandbox evidence; no promotion artifacts were written.",
            "",
        ]
    )


def _map_lane_verdict_to_agent_run_verdict(lane_verdict: str) -> str:
    mapping = {
        "PARTIALLY_VALID": "SANDBOX_PASS",
        "INCONCLUSIVE": "INCONCLUSIVE",
        "FALSIFIED": "FALSIFIED",
    }
    return mapping.get(lane_verdict, "INCONCLUSIVE")


def render_agent_run_yaml(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    payload = {
        "id": metrics["agent_run_id"],
        "campaign_profile_id": metrics["campaign_profile_id"],
        "task_id": metrics["task_id"],
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {
            "contributor_id": "master",
            "agent_id": "codex",
        },
        "proposal_paths": {
            "hypothesis": "hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0050-high-error-cluster-scout.yaml",
            "experiment": "experiment_proposals/nuclear-mass/EXP-PROPOSAL-0016-nuclear-high-error-cluster-scout.yaml",
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
                    "notes": "TASK-0367 requests a high-error cluster adversarial stability audit with sandbox-only outputs.",
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed repository inputs are used; no live external fetch is performed.",
                },
                {
                    "name": "adversarial_controls",
                    "status": "PASS",
                    "notes": "Cluster-label permutation, threshold perturbation, smooth-A/local-density, and near-null controls are included.",
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No prediction registry, canonical result, claim, or knowledge file is written.",
                },
            ],
        },
        "limitations": [
            "Retrospective full-known residual labels are used.",
            "The p80 high-error threshold perturbation is one deterministic threshold stress test.",
            "Leave-one-training-row-out stability is limited by a small training residual slice.",
            "Controls are stronger than the predecessor controls but not exhaustive.",
            "No live fetch, reveal scoring, registry write, canonical result, claim, or knowledge update is authorized.",
        ],
        "verdict": _map_lane_verdict_to_agent_run_verdict(summary["lane_verdict"]),
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": "Maintainer review before any follow-up implementation or prediction-registry task.",
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
        "--review-summary", type=Path, default=DEFAULT_REVIEW_SUMMARY_PATH
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
