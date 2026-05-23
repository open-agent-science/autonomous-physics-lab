"""TASK-0338 nuclear deformation-proxy hypothesis lane.

This runner evaluates bounded deformation-like proxies derived only from
repository-pinned Z, N, and A fields. It is retrospective, sandbox-only
evidence: it does not fetch external deformation data, score prediction
registry entries, write canonical RESULT-* artifacts, update claims, or edit
knowledge.
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

from physics_lab.engines.nuclear_mass_baselines import MAGIC_NUMBERS  # noqa: E402

import scripts.run_nuclear_shell_axis_full_known_audit as full_known  # noqa: E402


AGENT_RUN_ID = "AGENT-RUN-0025"
TASK_ID = "TASK-0338"
SHUFFLE_OFFSET = 7
CHAIN_MIN_ROWS = 3

DEFAULT_METRICS_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "metrics.json"
DEFAULT_REPORT_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "report.md"
DEFAULT_AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "agent_run.yaml"
DEFAULT_LIMITATIONS_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "limitations.md"
DEFAULT_PREFLIGHT_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "preflight.md"
DEFAULT_REVIEW_SUMMARY_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "review_summary.md"
DEFAULT_REVIEW_PATH = (
    REPO_ROOT / "docs" / "reviews" / "nuclear-deformation-proxy-hypothesis-lane.md"
)

FeatureFn = Callable[[dict[str, Any]], tuple[float, ...]]


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return float(np.mean(np.asarray(values, dtype=float)))


def _rmse(values: list[float]) -> float | None:
    if not values:
        return None
    arr = np.asarray(values, dtype=float)
    return float(np.sqrt(np.mean(arr * arr)))


def _format_delta(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value == 0.0:
        return "+0.000000"
    return f"{'+' if value > 0 else '-'}{abs(value):.6f}"


def _nearest_magic_distance(value: int) -> int:
    return min(abs(value - magic) for magic in MAGIC_NUMBERS)


def _magic_interval(value: int) -> tuple[int, int]:
    ordered = sorted(MAGIC_NUMBERS)
    lower = ordered[0]
    upper = ordered[-1]
    for idx, magic in enumerate(ordered):
        if value == magic:
            return magic, magic
        if value < magic:
            upper = magic
            lower = ordered[max(0, idx - 1)]
            return lower, upper
    return lower, upper


def _mid_shell_occupancy(value: int) -> float:
    lower, upper = _magic_interval(value)
    span = float(upper - lower)
    if span <= 0.0:
        return 0.0
    x = (float(value) - float(lower)) / span
    x = max(0.0, min(1.0, x))
    return float(4.0 * x * (1.0 - x))


def _neutron_excess(row: dict[str, Any]) -> float:
    a = int(row["A"])
    if a <= 0:
        return 0.0
    return float(int(row["N"]) - int(row["Z"])) / float(a)


def _scaled_a(row: dict[str, Any]) -> float:
    return (float(row["A"]) - 100.0) / 100.0


def _pn_mid_shell_product(row: dict[str, Any]) -> tuple[float, ...]:
    return (
        _mid_shell_occupancy(int(row["Z"]))
        * _mid_shell_occupancy(int(row["N"])),
    )


def _average_mid_shell(row: dict[str, Any]) -> tuple[float, ...]:
    return (
        0.5
        * (
            _mid_shell_occupancy(int(row["Z"]))
            + _mid_shell_occupancy(int(row["N"]))
        ),
    )


def _valence_balance(row: dict[str, Any]) -> tuple[float, ...]:
    z_mid = _mid_shell_occupancy(int(row["Z"]))
    n_mid = _mid_shell_occupancy(int(row["N"]))
    return (z_mid * n_mid * (1.0 - abs(z_mid - n_mid)),)


def _asymmetry_mid_shell(row: dict[str, Any]) -> tuple[float, ...]:
    z_mid = _mid_shell_occupancy(int(row["Z"]))
    n_mid = _mid_shell_occupancy(int(row["N"]))
    return ((_neutron_excess(row) ** 2) * z_mid * n_mid,)


def _parity_mid_shell(row: dict[str, Any]) -> tuple[float, ...]:
    odd_factor = 1.0 if int(row["Z"]) % 2 and int(row["N"]) % 2 else 0.5
    if int(row["Z"]) % 2 == 0 and int(row["N"]) % 2 == 0:
        odd_factor = -0.5
    return (_pn_mid_shell_product(row)[0] * odd_factor,)


def _heavy_mid_shell(row: dict[str, Any]) -> tuple[float, ...]:
    heavy_gate = 1.0 if int(row["A"]) >= 100 else 0.0
    return (_pn_mid_shell_product(row)[0] * heavy_gate,)


def _smooth_a_control(row: dict[str, Any]) -> tuple[float, ...]:
    a_scaled = _scaled_a(row)
    return (a_scaled * a_scaled,)


GENERATED_VARIANTS: tuple[dict[str, Any], ...] = (
    {
        "candidate_id": "DEFORM-PROXY-001",
        "name": "Proton-neutron mid-shell occupancy product",
        "family": "mid_shell_product",
        "formula": "r_corr = beta * mZ * mN",
        "feature_names": ("mid_shell_product",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "executed_candidate",
        "feature_fn": _pn_mid_shell_product,
    },
    {
        "candidate_id": "DEFORM-PROXY-002",
        "name": "Average proton/neutron mid-shell occupancy",
        "family": "average_mid_shell",
        "formula": "r_corr = beta * 0.5 * (mZ + mN)",
        "feature_names": ("average_mid_shell",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "executed_candidate",
        "feature_fn": _average_mid_shell,
    },
    {
        "candidate_id": "DEFORM-PROXY-003",
        "name": "Balanced proton-neutron valence occupancy",
        "family": "valence_balance",
        "formula": "r_corr = beta * mZ * mN * (1 - abs(mZ - mN))",
        "feature_names": ("balanced_valence_occupancy",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "executed_candidate",
        "feature_fn": _valence_balance,
    },
    {
        "candidate_id": "DEFORM-PROXY-004",
        "name": "Asymmetry-weighted mid-shell product",
        "family": "asymmetry_mid_shell",
        "formula": "r_corr = beta * ((N - Z) / A)^2 * mZ * mN",
        "feature_names": ("asymmetry_mid_shell_product",),
        "fit_mode": "not_executed",
        "complexity": 1,
        "role": "rejected_before_execution",
        "feature_fn": _asymmetry_mid_shell,
        "rejection_reason": (
            "Rejected before execution because the task budget is capped at "
            "1-3 candidates and the primary mid-shell family is already "
            "covered by three one-degree proxy variants."
        ),
    },
    {
        "candidate_id": "DEFORM-PROXY-005",
        "name": "Parity-gated mid-shell product",
        "family": "parity_mid_shell",
        "formula": "r_corr = beta * parity_gate * mZ * mN",
        "feature_names": ("parity_mid_shell_product",),
        "fit_mode": "not_executed",
        "complexity": 1,
        "role": "rejected_before_execution",
        "feature_fn": _parity_mid_shell,
        "rejection_reason": (
            "Rejected before execution because odd-even structure has a "
            "separate READY lane and should not be mixed into this scoped "
            "deformation-proxy comparison."
        ),
    },
    {
        "candidate_id": "DEFORM-PROXY-006",
        "name": "Heavy-region mid-shell product",
        "family": "heavy_mid_shell",
        "formula": "r_corr = beta * I(A >= 100) * mZ * mN",
        "feature_names": ("heavy_mid_shell_product",),
        "fit_mode": "not_executed",
        "complexity": 1,
        "role": "rejected_before_execution",
        "feature_fn": _heavy_mid_shell,
        "rejection_reason": (
            "Rejected before execution because an A>=100 gate risks turning "
            "the lane into a targeted subset patch rather than a general "
            "bounded proxy test."
        ),
    },
    {
        "candidate_id": "DEFORM-CONTROL-001",
        "name": "Smooth-A squared matched-complexity control",
        "family": "smooth_a_control",
        "formula": "r_corr = beta * ((A - 100) / 100)^2",
        "feature_names": ("smooth_a_squared",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "smooth_a_control",
        "feature_fn": _smooth_a_control,
    },
    {
        "candidate_id": "DEFORM-CONTROL-002",
        "name": "Cyclically shuffled mid-shell product control",
        "family": "shuffled_proxy_control",
        "formula": "r_corr = beta * shuffled(mZ * mN)",
        "feature_names": ("shuffled_mid_shell_product",),
        "fit_mode": "lstsq_shuffled",
        "complexity": 1,
        "role": "shuffled_proxy_control",
        "feature_fn": _pn_mid_shell_product,
        "shuffle_scheme": "cyclic-shift-7",
        "shuffle_seed": SHUFFLE_OFFSET,
    },
)


def _feature_matrix(
    rows: list[dict[str, Any]],
    *,
    variant: dict[str, Any],
    shuffled: bool = False,
) -> np.ndarray:
    source_rows = rows
    if shuffled:
        count = len(rows)
        source_rows = [rows[(idx + SHUFFLE_OFFSET) % count] for idx in range(count)]
    feature_fn = variant["feature_fn"]
    return np.asarray([feature_fn(row) for row in source_rows], dtype=float)


def _summarize_residuals(residuals: list[float]) -> dict[str, float | int | None]:
    if not residuals:
        return {
            "count": 0,
            "mae_mev": None,
            "rmse_mev": None,
            "mean_error_mev": None,
            "max_abs_error_mev": None,
        }
    abs_errors = [abs(value) for value in residuals]
    return {
        "count": len(residuals),
        "mae_mev": float(np.mean(np.asarray(abs_errors, dtype=float))),
        "rmse_mev": _rmse(residuals),
        "mean_error_mev": _mean(residuals),
        "max_abs_error_mev": float(max(abs_errors)),
    }


def _subset_ids(row: dict[str, Any]) -> tuple[str, ...]:
    ids = list(full_known._surface_subset_ids(row))  # noqa: SLF001
    if _nearest_magic_distance(int(row["Z"])) <= 2:
        ids.append("near_magic_z")
    if _nearest_magic_distance(int(row["N"])) <= 2:
        ids.append("near_magic_n")
    ids.append("light_a_warning" if int(row["A"]) < 50 else "not_light_a_warning")
    return tuple(dict.fromkeys(ids))


def _baseline_metrics(rows: list[dict[str, Any]]) -> dict[str, dict[str, float | int | None]]:
    subset_errors: dict[str, list[float]] = {}
    for row in rows:
        for subset_id in _subset_ids(row):
            subset_errors.setdefault(subset_id, []).append(float(row["baseline_residual_mev"]))
    return {
        key: _summarize_residuals(value)
        for key, value in sorted(subset_errors.items())
    }


def _delta(
    candidate_metrics: dict[str, float | int | None] | None,
    baseline_metrics: dict[str, float | int | None] | None,
    metric_name: str,
) -> float | None:
    if candidate_metrics is None or baseline_metrics is None:
        return None
    candidate_value = candidate_metrics.get(metric_name)
    baseline_value = baseline_metrics.get(metric_name)
    if candidate_value is None or baseline_value is None:
        return None
    return float(candidate_value) - float(baseline_value)


def _fit_variant(
    variant: dict[str, Any],
    *,
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
) -> tuple[np.ndarray, dict[str, float]]:
    shuffled = variant["fit_mode"] == "lstsq_shuffled"
    train_x = _feature_matrix(training_rows, variant=variant, shuffled=shuffled)
    beta, *_ = np.linalg.lstsq(train_x, training_residuals, rcond=None)
    return beta, {
        name: float(value)
        for name, value in zip(tuple(variant["feature_names"]), beta)
    }


def _feature_activation_counts(
    rows: list[dict[str, Any]],
    *,
    variant: dict[str, Any],
) -> dict[str, int]:
    names = tuple(variant["feature_names"])
    matrix = _feature_matrix(
        rows,
        variant=variant,
        shuffled=variant["fit_mode"] == "lstsq_shuffled",
    )
    counts = {name: 0 for name in names}
    for row_values in matrix:
        for name, value in zip(names, row_values):
            if abs(float(value)) > 0.0:
                counts[name] += 1
    return counts


def _evaluate_variant(
    variant: dict[str, Any],
    *,
    audit_rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
    baseline_metrics: dict[str, dict[str, float | int | None]],
) -> dict[str, Any]:
    beta, fitted_coefficients = _fit_variant(
        variant,
        training_rows=training_rows,
        training_residuals=training_residuals,
    )
    feature_values = _feature_matrix(
        audit_rows,
        variant=variant,
        shuffled=variant["fit_mode"] == "lstsq_shuffled",
    )
    subset_errors: dict[str, list[float]] = {key: [] for key in baseline_metrics}
    per_row: list[dict[str, Any]] = []
    for row, values in zip(audit_rows, feature_values):
        correction = float(values @ beta)
        candidate_residual = float(row["observed_mev"]) - (
            float(row["baseline_predicted_mev"]) + correction
        )
        item = {
            "row_id": row["row_id"],
            "nuclide_id": row["nuclide_id"],
            "Z": int(row["Z"]),
            "N": int(row["N"]),
            "A": int(row["A"]),
            "source_surface": row["source_surface"],
            "baseline_residual_mev": float(row["baseline_residual_mev"]),
            "candidate_residual_mev": candidate_residual,
            "baseline_abs_error_mev": abs(float(row["baseline_residual_mev"])),
            "candidate_abs_error_mev": abs(candidate_residual),
            "delta_abs_error_mev": abs(candidate_residual)
            - abs(float(row["baseline_residual_mev"])),
            "correction_mev": correction,
            "feature_values": {
                name: float(value)
                for name, value in zip(tuple(variant["feature_names"]), values)
            },
        }
        per_row.append(item)
        for subset_id in _subset_ids(row):
            subset_errors.setdefault(subset_id, []).append(candidate_residual)

    metrics_by_subset = {
        key: _summarize_residuals(value)
        for key, value in sorted(subset_errors.items())
    }
    delta_mae_by_subset = {
        key: _delta(metrics_by_subset.get(key), baseline_metrics.get(key), "mae_mev")
        for key in sorted(baseline_metrics)
    }
    delta_rmse_by_subset = {
        key: _delta(metrics_by_subset.get(key), baseline_metrics.get(key), "rmse_mev")
        for key in sorted(baseline_metrics)
    }
    positive = {
        key: value
        for key, value in delta_mae_by_subset.items()
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
        "fit_mode": variant["fit_mode"],
        "fitted_coefficients": fitted_coefficients,
        "feature_activation_counts": _feature_activation_counts(
            audit_rows,
            variant=variant,
        ),
        "metrics_by_subset": metrics_by_subset,
        "delta_mae_by_subset_mev": delta_mae_by_subset,
        "delta_rmse_by_subset_mev": delta_rmse_by_subset,
        "primary_delta_mae_mev": delta_mae_by_subset.get("full_known"),
        "primary_delta_rmse_mev": delta_rmse_by_subset.get("full_known"),
        "holdout_delta_mae_mev": delta_mae_by_subset.get("primary_holdout"),
        "training_delta_mae_mev": delta_mae_by_subset.get("training_slice"),
        "magic_z_delta_mae_mev": delta_mae_by_subset.get("magic_z"),
        "magic_n_delta_mae_mev": delta_mae_by_subset.get("magic_n"),
        "mid_mass_delta_mae_mev": delta_mae_by_subset.get("mid_mass"),
        "heavy_delta_mae_mev": delta_mae_by_subset.get("heavy_a_ge_100"),
        "neutron_rich_delta_mae_mev": delta_mae_by_subset.get("neutron_rich_high"),
        "light_a_warning_delta_mae_mev": delta_mae_by_subset.get("light_a_warning"),
        "worst_subset_regression": worst_subset,
        "worst_abs_error_cases": sorted(
            per_row,
            key=lambda item: float(item["candidate_abs_error_mev"]),
            reverse=True,
        )[:8],
        "largest_regressions": sorted(
            per_row,
            key=lambda item: float(item["delta_abs_error_mev"]),
            reverse=True,
        )[:8],
        "largest_improvements": sorted(
            per_row,
            key=lambda item: float(item["delta_abs_error_mev"]),
        )[:8],
        "limitations": [
            "Features are derived proxy terms, not measured deformation parameters.",
            "Coefficients are fit on the 11-row NMD-0002 residual slice.",
            "No live source fetch, reveal scoring, registry write, claim update, or canonical result write is authorized.",
        ],
    }


def _candidate_residuals_for_rows(
    item: dict[str, Any],
    rows: list[dict[str, Any]],
) -> list[float]:
    variant = next(
        variant
        for variant in GENERATED_VARIANTS
        if variant["candidate_id"] == item["candidate_id"]
    )
    beta = np.asarray(
        [item["fitted_coefficients"][name] for name in variant["feature_names"]],
        dtype=float,
    )
    matrix = _feature_matrix(
        rows,
        variant=variant,
        shuffled=variant["fit_mode"] == "lstsq_shuffled",
    )
    out: list[float] = []
    for row, values in zip(rows, matrix):
        correction = float(values @ beta)
        out.append(
            float(row["observed_mev"])
            - (float(row["baseline_predicted_mev"]) + correction)
        )
    return out


def _group_indices(rows: list[dict[str, Any]], key: str) -> dict[str, list[int]]:
    grouped: dict[str, list[int]] = {}
    for idx, row in enumerate(rows):
        grouped.setdefault(f"{key}_{int(row[key]):03d}", []).append(idx)
    return dict(sorted(grouped.items(), key=lambda item: int(item[0].split("_")[1])))


def _mae_delta_for_indices(
    candidate_residuals: list[float],
    baseline_residuals: list[float],
    indices: list[int],
) -> float | None:
    baseline_mae = _mean([abs(baseline_residuals[idx]) for idx in indices])
    candidate_mae = _mean([abs(candidate_residuals[idx]) for idx in indices])
    if baseline_mae is None or candidate_mae is None:
        return None
    return candidate_mae - baseline_mae


def _isotope_chain_diagnostics(
    *,
    rows: list[dict[str, Any]],
    candidate_items: list[dict[str, Any]],
) -> dict[str, Any]:
    groups = _group_indices(rows, "Z")
    baseline_residuals = [float(row["baseline_residual_mev"]) for row in rows]
    candidate_residuals = {
        item["candidate_id"]: _candidate_residuals_for_rows(item, rows)
        for item in candidate_items
    }
    group_items: list[dict[str, Any]] = []
    for group_id, indices in groups.items():
        deltas = {
            candidate_id: _mae_delta_for_indices(values, baseline_residuals, indices)
            for candidate_id, values in candidate_residuals.items()
        }
        numeric = {
            candidate_id: value
            for candidate_id, value in deltas.items()
            if value is not None
        }
        best_id = None
        best_delta = None
        if numeric:
            best_id, best_delta = min(numeric.items(), key=lambda item: item[1])
        group_items.append(
            {
                "group_id": group_id,
                "Z": int(rows[indices[0]]["Z"]),
                "row_count": len(indices),
                "diagnostic_class": (
                    "interpretable" if len(indices) >= CHAIN_MIN_ROWS else "too_sparse"
                ),
                "baseline_mae_mev": _mean(
                    [abs(baseline_residuals[idx]) for idx in indices]
                ),
                "delta_mae_by_candidate_mev": deltas,
                "best_candidate_id": best_id,
                "best_delta_mae_mev": best_delta,
                "nuclide_ids": [str(rows[idx]["nuclide_id"]) for idx in indices],
            }
        )

    interpretable = [
        item for item in group_items if item["diagnostic_class"] == "interpretable"
    ]
    by_candidate: dict[str, Any] = {}
    for candidate in candidate_items:
        candidate_id = candidate["candidate_id"]
        deltas = [
            item["delta_mae_by_candidate_mev"][candidate_id]
            for item in interpretable
            if item["delta_mae_by_candidate_mev"][candidate_id] is not None
        ]
        improved = sum(1 for value in deltas if value < 0.0)
        regressed = sum(1 for value in deltas if value > 0.0)
        by_candidate[candidate_id] = {
            "interpretable_group_count": len(deltas),
            "improved_group_count": improved,
            "regressed_group_count": regressed,
            "neutral_group_count": len(deltas) - improved - regressed,
            "improvement_rate": improved / len(deltas) if deltas else None,
            "regression_rate": regressed / len(deltas) if deltas else None,
            "worst_group_regressions": sorted(
                [
                    {
                        "group_id": item["group_id"],
                        "row_count": item["row_count"],
                        "delta_mae_mev": item["delta_mae_by_candidate_mev"][candidate_id],
                    }
                    for item in interpretable
                    if item["delta_mae_by_candidate_mev"][candidate_id] is not None
                    and item["delta_mae_by_candidate_mev"][candidate_id] > 0.0
                ],
                key=lambda item: float(item["delta_mae_mev"]),
                reverse=True,
            )[:8],
        }

    return {
        "group_key": "Z",
        "group_count": len(group_items),
        "interpretable_group_count": len(interpretable),
        "too_sparse_group_count": len(group_items) - len(interpretable),
        "by_candidate": by_candidate,
        "group_items": group_items,
    }


def _lane_verdict(
    candidate_items: list[dict[str, Any]],
    isotope_chain_diagnostics: dict[str, Any],
) -> str:
    controls = [item for item in candidate_items if item["role"].endswith("_control")]
    executed = [item for item in candidate_items if item["role"] == "executed_candidate"]
    if not executed:
        return "INCONCLUSIVE"

    best_candidate = min(
        executed,
        key=lambda item: (
            float("inf")
            if item["primary_delta_mae_mev"] is None
            else float(item["primary_delta_mae_mev"]),
            item["candidate_id"],
        ),
    )
    best_primary = best_candidate["primary_delta_mae_mev"]
    best_holdout = best_candidate["holdout_delta_mae_mev"]
    best_chain_rate = isotope_chain_diagnostics["by_candidate"][
        best_candidate["candidate_id"]
    ]["improvement_rate"]
    worst_regression = float(best_candidate["worst_subset_regression"]["delta_mae_mev"])
    control_primary = [
        item["primary_delta_mae_mev"]
        for item in controls
        if item["primary_delta_mae_mev"] is not None
    ]
    comparable_control = any(
        best_primary is not None and value <= float(best_primary) + 0.02
        for value in control_primary
    )
    if comparable_control:
        return "INCONCLUSIVE"
    if (
        best_primary is not None
        and best_holdout is not None
        and best_chain_rate is not None
        and best_primary < 0.0
        and best_holdout < 0.0
        and best_chain_rate >= 0.5
        and worst_regression <= 0.5
    ):
        return "PARTIALLY_VALID"
    return "INCONCLUSIVE"


def build_metrics() -> dict[str, Any]:
    coefficients = full_known.load_frozen_baseline_coefficients()
    audit_rows, training_rows, training_residuals, surface = full_known.build_audit_surface(
        coefficients
    )
    baseline_metrics = _baseline_metrics(audit_rows)
    executed_variants = [
        variant
        for variant in GENERATED_VARIANTS
        if variant["fit_mode"] in {"lstsq", "lstsq_shuffled"}
    ]
    candidate_items = [
        _evaluate_variant(
            variant,
            audit_rows=audit_rows,
            training_rows=training_rows,
            training_residuals=training_residuals,
            baseline_metrics=baseline_metrics,
        )
        for variant in executed_variants
    ]
    isotope_diagnostics = _isotope_chain_diagnostics(
        rows=audit_rows,
        candidate_items=candidate_items,
    )
    lane_verdict = _lane_verdict(candidate_items, isotope_diagnostics)
    best_item = min(
        candidate_items,
        key=lambda item: (
            float("inf")
            if item["primary_delta_mae_mev"] is None
            else float(item["primary_delta_mae_mev"]),
            item["candidate_id"],
        ),
    )
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "nuclear_deformation_proxy_hypothesis_lane",
        "sandbox_only": True,
        "evidence_class": "retrospective_full_known_deformation_proxy_sandbox",
        "live_external_fetch_allowed": False,
        "summary": {
            "generated_variant_count": len(GENERATED_VARIANTS) - 2,
            "generated_control_count": 2,
            "executed_candidate_count": sum(
                1 for item in candidate_items if item["role"] == "executed_candidate"
            ),
            "executed_control_count": sum(
                1 for item in candidate_items if item["role"].endswith("_control")
            ),
            "lane_verdict": lane_verdict,
            "best_primary_delta_candidate_id": best_item["candidate_id"],
            "best_primary_delta_mae_mev": best_item["primary_delta_mae_mev"],
            "best_primary_delta_rmse_mev": best_item["primary_delta_rmse_mev"],
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
            "full_known_unique_row_count": surface["metadata"]["full_known_unique_row_count"],
            "duplicate_post_rows_excluded_from_full_known": surface["metadata"][
                "duplicate_post_rows_excluded_from_full_known"
            ],
        },
        "baseline_metrics_by_subset": baseline_metrics,
        "generated_variants": [
            {key: value for key, value in variant.items() if key not in {"feature_fn"}}
            for variant in GENERATED_VARIANTS
        ],
        "candidate_items": candidate_items,
        "isotope_chain_diagnostics": isotope_diagnostics,
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any deformation-proxy follow-up, reveal scoring, "
                "RESULT-* artifact, claim, or knowledge update."
            ),
        },
        "limitations": [
            "These features are deformation-like proxies derived from Z, N, and A, not measured deformation parameters.",
            "The fit surface remains the 11-row NMD-0002 training slice, so coefficient stability is not established.",
            "The full-known surface is retrospective committed repository data, not a future-measurement reveal.",
            "Smooth-A and shuffled controls are included because aggregate improvements can reflect small-sample residual structure.",
            "No source fetch, canonical result rewrite, PRED entry, claim update, or public-facing physics claim is authorized.",
        ],
    }


def _candidate_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Candidate | Role | Full-known MAE | Full-known RMSE | Holdout | Magic-Z | Magic-N | Mid-mass | Heavy | Neutron-rich | Light-A |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in metrics["candidate_items"]:
        lines.append(
            "| {candidate_id} | {role} | {primary} | {rmse} | {holdout} | {mz} | {mn} | {mid} | {heavy} | {neutron} | {light} |".format(
                candidate_id=item["candidate_id"],
                role=item["role"],
                primary=_format_delta(item["primary_delta_mae_mev"]),
                rmse=_format_delta(item["primary_delta_rmse_mev"]),
                holdout=_format_delta(item["holdout_delta_mae_mev"]),
                mz=_format_delta(item["magic_z_delta_mae_mev"]),
                mn=_format_delta(item["magic_n_delta_mae_mev"]),
                mid=_format_delta(item["mid_mass_delta_mae_mev"]),
                heavy=_format_delta(item["heavy_delta_mae_mev"]),
                neutron=_format_delta(item["neutron_rich_delta_mae_mev"]),
                light=_format_delta(item["light_a_warning_delta_mae_mev"]),
            )
        )
    return lines


def _chain_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Candidate | Interpretable Z chains | Improved | Regressed | Improvement rate |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for candidate_id, item in metrics["isotope_chain_diagnostics"]["by_candidate"].items():
        rate = item["improvement_rate"]
        lines.append(
            "| {candidate_id} | {groups} | {improved} | {regressed} | {rate} |".format(
                candidate_id=candidate_id,
                groups=item["interpretable_group_count"],
                improved=item["improved_group_count"],
                regressed=item["regressed_group_count"],
                rate="n/a" if rate is None else f"{rate:.3f}",
            )
        )
    return lines


def render_report(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    lines = [
        "# Nuclear deformation-proxy hypothesis lane",
        "",
        f"**Task:** `{TASK_ID}`",
        f"**Agent run:** `{AGENT_RUN_ID}`",
        "**Evidence class:** sandbox-only retrospective deformation-proxy diagnostic",
        f"**Verdict:** `{summary['lane_verdict']}`",
        "",
        "## Boundary",
        "",
        "This run uses only repository-pinned rows and Z/N/A-derived proxy features. "
        "It writes no canonical results, prediction-registry entries, claims, or "
        "knowledge artifacts. The proxy features are not measured deformation "
        "parameters, so the output is a bounded retrospective diagnostic surface.",
        "",
        "## Candidate Results",
        "",
        *_candidate_table(metrics),
        "",
        "Negative deltas mean lower error than the frozen semi-empirical baseline on "
        "that subset. Positive deltas are regressions and remain visible.",
        "",
        "## Isotope-Chain Diagnostics",
        "",
        *_chain_table(metrics),
        "",
        "## Interpretation",
        "",
        f"- Generated proxy variants: `{summary['generated_variant_count']}`.",
        f"- Generated controls: `{summary['generated_control_count']}`.",
        f"- Executed candidate variants: `{summary['executed_candidate_count']}`.",
        f"- Executed controls: `{summary['executed_control_count']}`.",
        f"- Best full-known delta: `{summary['best_primary_delta_candidate_id']}` "
        f"({_format_delta(summary['best_primary_delta_mae_mev'])} MeV MAE; "
        f"{_format_delta(summary['best_primary_delta_rmse_mev'])} MeV RMSE).",
        "- Smooth-A and shuffled controls are reported next to candidates to keep "
        "non-deformation and small-sample explanations visible.",
        "- The verdict stays conservative; no result here authorizes claim promotion "
        "or future-measurement comparison.",
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in metrics["limitations"]],
        "",
    ]
    return "\n".join(lines)


def render_agent_run(metrics: dict[str, Any]) -> str:
    payload = {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "task_id": TASK_ID,
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {
            "contributor_id": "master",
            "agent_id": "codex",
        },
        "proposal_paths": {
            "hypothesis": "hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0046-deformation-proxy-scout-batch.yaml",
            "experiment": "experiment_proposals/nuclear-mass/EXP-PROPOSAL-0012-nuclear-deformation-proxy-scout.yaml",
        },
        "artifacts": {
            "metrics": f"agent_runs/{AGENT_RUN_ID}/metrics.json",
            "report": f"agent_runs/{AGENT_RUN_ID}/report.md",
            "limitations": f"agent_runs/{AGENT_RUN_ID}/limitations.md",
            "preflight": f"agent_runs/{AGENT_RUN_ID}/preflight.md",
            "review_summary": f"agent_runs/{AGENT_RUN_ID}/review_summary.md",
        },
        "preflight": {
            "passed": True,
            "checks": [
                {
                    "name": "task_scope",
                    "status": "PASS",
                    "notes": "TASK-0338 requests a sandbox deformation-proxy lane, not reveal scoring.",
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed repository datasets and derived Z/N/A proxies are used.",
                },
                {
                    "name": "control_boundary",
                    "status": "PASS",
                    "notes": "Smooth-A and shuffled proxy controls are executed and reported.",
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No prediction registry, canonical result, claim, or knowledge file is written.",
                },
            ],
        },
        "limitations": metrics["limitations"],
        "verdict": metrics["summary"]["lane_verdict"],
        "promotion_boundary": metrics["promotion_boundary"],
    }
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=False)


def render_limitations(metrics: dict[str, Any]) -> str:
    lines = [
        "# Limitations",
        "",
        *[f"- {item}" for item in metrics["limitations"]],
        "",
    ]
    return "\n".join(lines)


def render_preflight(metrics: dict[str, Any]) -> str:
    manifest = yaml.safe_load(render_agent_run(metrics))
    lines = [
        "# Preflight",
        "",
        "**Lane:** nuclear deformation-proxy hypothesis lane",
        "",
    ]
    for check in manifest["preflight"]["checks"]:
        lines.append(f"- `{check['name']}`: `{check['status']}` - {check['notes']}")
    lines.append("")
    return "\n".join(lines)


def render_review_summary(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    lines = [
        "# Review Summary",
        "",
        f"`{summary['lane_verdict']}` for claim promotion: deformation-like proxies "
        "derived from Z/N/A are deterministic and reviewable, but smooth-A and "
        "shuffled controls remain visible and the lane stays sandbox-only.",
        "",
        f"- Best full-known delta: `{summary['best_primary_delta_candidate_id']}` "
        f"({_format_delta(summary['best_primary_delta_mae_mev'])} MeV MAE).",
        "- No live fetch, prediction-registry write, canonical RESULT artifact, "
        "claim update, or knowledge update.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(
    metrics: dict[str, Any],
    *,
    out: Path,
    report: Path,
    agent_run: Path,
    limitations: Path,
    preflight: Path,
    review_summary: Path,
    review: Path,
) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    agent_run.parent.mkdir(parents=True, exist_ok=True)
    limitations.parent.mkdir(parents=True, exist_ok=True)
    preflight.parent.mkdir(parents=True, exist_ok=True)
    review_summary.parent.mkdir(parents=True, exist_ok=True)
    review.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rendered = render_report(metrics)
    report.write_text(rendered, encoding="utf-8")
    review.write_text(rendered, encoding="utf-8")
    agent_run.write_text(render_agent_run(metrics), encoding="utf-8")
    limitations.write_text(render_limitations(metrics), encoding="utf-8")
    preflight.write_text(render_preflight(metrics), encoding="utf-8")
    review_summary.write_text(render_review_summary(metrics), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_METRICS_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--agent-run", type=Path, default=DEFAULT_AGENT_RUN_PATH)
    parser.add_argument("--limitations", type=Path, default=DEFAULT_LIMITATIONS_PATH)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT_PATH)
    parser.add_argument("--review-summary", type=Path, default=DEFAULT_REVIEW_SUMMARY_PATH)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    args = parser.parse_args(argv)

    metrics = build_metrics()
    write_outputs(
        metrics,
        out=args.out,
        report=args.report,
        agent_run=args.agent_run,
        limitations=args.limitations,
        preflight=args.preflight,
        review_summary=args.review_summary,
        review=args.review,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
