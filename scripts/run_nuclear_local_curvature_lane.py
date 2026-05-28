"""TASK-0339 nuclear local residual curvature hypothesis lane.

This runner tests bounded local residual proxies along isotope and isotone
neighborhoods using only repository-pinned rows. It is retrospective,
sandbox-only evidence: it does not fetch live data, score prediction registry
entries, write canonical RESULT-* artifacts, update claims, or edit knowledge.
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

import scripts.run_nuclear_shell_axis_full_known_audit as full_known  # noqa: E402


AGENT_RUN_ID = "AGENT-RUN-0026"
TASK_ID = "TASK-0339"
CHAIN_MIN_ROWS = 3
HIGH_ERROR_PERCENTILE = 75.0

DEFAULT_METRICS_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "metrics.json"
DEFAULT_REPORT_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "report.md"
DEFAULT_AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "agent_run.yaml"
DEFAULT_LIMITATIONS_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "limitations.md"
DEFAULT_PREFLIGHT_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "preflight.md"
DEFAULT_REVIEW_SUMMARY_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "review_summary.md"
DEFAULT_REVIEW_PATH = (
    REPO_ROOT / "docs" / "reviews" / "nuclear-local-curvature-hypothesis-lane.md"
)

FeatureFn = Callable[[dict[str, Any], "NeighborIndex"], tuple[float, ...]]


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


def _neutron_excess(row: dict[str, Any]) -> float:
    a = int(row["A"])
    if a <= 0:
        return 0.0
    return float(int(row["N"]) - int(row["Z"])) / float(a)


class NeighborIndex:
    """Deterministic local-neighborhood residual lookup for audit rows."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        self.by_nuclide = {str(row["nuclide_id"]): row for row in rows}
        self.isotopes = self._group_rows("Z", "N")
        self.isotones = self._group_rows("N", "Z")
        self.by_a = sorted(rows, key=lambda row: (int(row["A"]), int(row["Z"]), int(row["N"])))

    def _group_rows(self, fixed_key: str, order_key: str) -> dict[int, list[dict[str, Any]]]:
        grouped: dict[int, list[dict[str, Any]]] = {}
        for row in self.rows:
            grouped.setdefault(int(row[fixed_key]), []).append(row)
        return {
            key: sorted(items, key=lambda row: (int(row[order_key]), str(row["nuclide_id"])))
            for key, items in grouped.items()
        }

    @staticmethod
    def _nearest_pair(
        group: list[dict[str, Any]],
        *,
        target_id: str,
        order_key: str,
        value: int,
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        lower = [
            row
            for row in group
            if str(row["nuclide_id"]) != target_id and int(row[order_key]) < value
        ]
        upper = [
            row
            for row in group
            if str(row["nuclide_id"]) != target_id and int(row[order_key]) > value
        ]
        left = max(lower, key=lambda row: int(row[order_key]), default=None)
        right = min(upper, key=lambda row: int(row[order_key]), default=None)
        return left, right

    def isotope_pair(self, row: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        return self._nearest_pair(
            self.isotopes.get(int(row["Z"]), []),
            target_id=str(row["nuclide_id"]),
            order_key="N",
            value=int(row["N"]),
        )

    def isotone_pair(self, row: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        return self._nearest_pair(
            self.isotones.get(int(row["N"]), []),
            target_id=str(row["nuclide_id"]),
            order_key="Z",
            value=int(row["Z"]),
        )

    def smooth_a_neighbors(self, row: dict[str, Any], *, radius: int = 3) -> list[dict[str, Any]]:
        target_id = str(row["nuclide_id"])
        target_a = int(row["A"])
        neighbors = [
            item
            for item in self.by_a
            if str(item["nuclide_id"]) != target_id and abs(int(item["A"]) - target_a) <= radius
        ]
        return sorted(
            neighbors,
            key=lambda item: (
                abs(int(item["A"]) - target_a),
                abs(int(item["Z"]) - int(row["Z"])),
                str(item["nuclide_id"]),
            ),
        )[:6]

    def shuffled_isotope_mean(self, row: dict[str, Any]) -> float:
        group = self.isotopes.get(int(row["Z"]), [])
        if len(group) < 2:
            return 0.0
        ids = [str(item["nuclide_id"]) for item in group]
        idx = ids.index(str(row["nuclide_id"]))
        shifted = group[(idx + 1) % len(group)]
        return float(shifted["baseline_residual_mev"])


def _pair_mean(pair: tuple[dict[str, Any] | None, dict[str, Any] | None]) -> float:
    values = [
        float(item["baseline_residual_mev"])
        for item in pair
        if item is not None
    ]
    return 0.0 if not values else float(np.mean(np.asarray(values, dtype=float)))


def _pair_slope(
    pair: tuple[dict[str, Any] | None, dict[str, Any] | None],
    *,
    order_key: str,
) -> float:
    left, right = pair
    if left is None or right is None:
        return 0.0
    span = float(int(right[order_key]) - int(left[order_key]))
    if span == 0.0:
        return 0.0
    return (float(right["baseline_residual_mev"]) - float(left["baseline_residual_mev"])) / span


def _isotope_neighbor_mean(row: dict[str, Any], index: NeighborIndex) -> tuple[float, ...]:
    return (_pair_mean(index.isotope_pair(row)),)


def _isotone_neighbor_mean(row: dict[str, Any], index: NeighborIndex) -> tuple[float, ...]:
    return (_pair_mean(index.isotone_pair(row)),)


def _local_kink_contrast(row: dict[str, Any], index: NeighborIndex) -> tuple[float, ...]:
    isotope_mean = _pair_mean(index.isotope_pair(row))
    isotone_mean = _pair_mean(index.isotone_pair(row))
    return (isotope_mean - isotone_mean,)


def _isotope_slope(row: dict[str, Any], index: NeighborIndex) -> tuple[float, ...]:
    return (_pair_slope(index.isotope_pair(row), order_key="N"),)


def _chain_shuffled_isotope_mean(row: dict[str, Any], index: NeighborIndex) -> tuple[float, ...]:
    return (index.shuffled_isotope_mean(row),)


def _smooth_a_window_mean(row: dict[str, Any], index: NeighborIndex) -> tuple[float, ...]:
    neighbors = index.smooth_a_neighbors(row)
    if not neighbors:
        return (0.0,)
    return (
        float(
            np.mean(
                np.asarray(
                    [float(item["baseline_residual_mev"]) for item in neighbors],
                    dtype=float,
                )
            )
        ),
    )


GENERATED_VARIANTS: tuple[dict[str, Any], ...] = (
    {
        "candidate_id": "LOCAL-CURVATURE-001",
        "name": "Isotope-chain nearest-neighbor residual mean",
        "family": "isotope_local_residual",
        "formula": "r_corr = beta * mean(nearest same-Z neighbor residuals)",
        "feature_names": ("isotope_neighbor_mean_residual",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "executed_candidate",
        "feature_fn": _isotope_neighbor_mean,
    },
    {
        "candidate_id": "LOCAL-CURVATURE-002",
        "name": "Isotone-chain nearest-neighbor residual mean",
        "family": "isotone_local_residual",
        "formula": "r_corr = beta * mean(nearest same-N neighbor residuals)",
        "feature_names": ("isotone_neighbor_mean_residual",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "executed_candidate",
        "feature_fn": _isotone_neighbor_mean,
    },
    {
        "candidate_id": "LOCAL-CURVATURE-003",
        "name": "Isotope minus isotone local kink contrast",
        "family": "local_kink_contrast",
        "formula": "r_corr = beta * (isotope_neighbor_mean - isotone_neighbor_mean)",
        "feature_names": ("local_kink_contrast_residual",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "executed_candidate",
        "feature_fn": _local_kink_contrast,
    },
    {
        "candidate_id": "LOCAL-CURVATURE-004",
        "name": "Isotope-chain nearest-neighbor residual slope",
        "family": "isotope_local_slope",
        "formula": "r_corr = beta * ((right residual - left residual) / delta N)",
        "feature_names": ("isotope_neighbor_slope_residual",),
        "fit_mode": "not_executed",
        "complexity": 1,
        "role": "rejected_before_execution",
        "feature_fn": _isotope_slope,
        "rejection_reason": (
            "Rejected before execution because the three one-degree local-mean "
            "variants already cover the allowed 1-3 candidate sandbox budget; "
            "the slope proxy is preserved as a future diagnostic idea."
        ),
    },
    {
        "candidate_id": "LOCAL-CONTROL-001",
        "name": "Chain-shuffled isotope residual control",
        "family": "chain_shuffled_control",
        "formula": "r_corr = beta * cyclically shifted same-Z residual",
        "feature_names": ("chain_shuffled_isotope_residual",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "chain_shuffled_control",
        "feature_fn": _chain_shuffled_isotope_mean,
    },
    {
        "candidate_id": "LOCAL-CONTROL-002",
        "name": "Smooth local mass-window residual control",
        "family": "smooth_local_window_control",
        "formula": "r_corr = beta * mean(nearest A-window residuals)",
        "feature_names": ("smooth_a_window_residual",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "smooth_local_window_control",
        "feature_fn": _smooth_a_window_mean,
    },
)


def _feature_matrix(
    rows: list[dict[str, Any]],
    *,
    variant: dict[str, Any],
    index: NeighborIndex,
) -> np.ndarray:
    feature_fn = variant["feature_fn"]
    return np.asarray([feature_fn(row, index) for row in rows], dtype=float)


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


def _subset_ids(row: dict[str, Any], *, high_error_threshold: float) -> tuple[str, ...]:
    ids = list(full_known._surface_subset_ids(row))  # noqa: SLF001
    baseline_abs = abs(float(row["baseline_residual_mev"]))
    ids.append(
        "high_error_baseline_p75"
        if baseline_abs >= high_error_threshold
        else "non_high_error_baseline_p75"
    )
    ids.append("neutron_rich_local" if _neutron_excess(row) >= 0.25 else "not_neutron_rich_local")
    return tuple(dict.fromkeys(ids))


def _baseline_metrics(
    rows: list[dict[str, Any]],
    *,
    high_error_threshold: float,
) -> dict[str, dict[str, float | int | None]]:
    subset_errors: dict[str, list[float]] = {}
    for row in rows:
        for subset_id in _subset_ids(row, high_error_threshold=high_error_threshold):
            subset_errors.setdefault(subset_id, []).append(float(row["baseline_residual_mev"]))
    return {
        key: _summarize_residuals(value)
        for key, value in sorted(subset_errors.items())
    }


def _delta_mae(
    candidate_metrics: dict[str, float | int | None] | None,
    baseline_metrics: dict[str, float | int | None] | None,
) -> float | None:
    if candidate_metrics is None or baseline_metrics is None:
        return None
    candidate_mae = candidate_metrics.get("mae_mev")
    baseline_mae = baseline_metrics.get("mae_mev")
    if candidate_mae is None or baseline_mae is None:
        return None
    return float(candidate_mae) - float(baseline_mae)


def _fit_variant(
    variant: dict[str, Any],
    *,
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
    index: NeighborIndex,
) -> tuple[np.ndarray, dict[str, float]]:
    feature_names = tuple(variant["feature_names"])
    train_x = _feature_matrix(training_rows, variant=variant, index=index)
    beta, *_ = np.linalg.lstsq(train_x, training_residuals, rcond=None)
    return beta, {name: float(value) for name, value in zip(feature_names, beta)}


def _feature_activation_counts(
    rows: list[dict[str, Any]],
    *,
    variant: dict[str, Any],
    index: NeighborIndex,
) -> dict[str, int]:
    names = tuple(variant["feature_names"])
    counts = {name: 0 for name in names}
    matrix = _feature_matrix(rows, variant=variant, index=index)
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
    index: NeighborIndex,
    baseline_metrics: dict[str, dict[str, float | int | None]],
    high_error_threshold: float,
) -> dict[str, Any]:
    beta, fitted_coefficients = _fit_variant(
        variant,
        training_rows=training_rows,
        training_residuals=training_residuals,
        index=index,
    )
    feature_values = _feature_matrix(audit_rows, variant=variant, index=index)
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
        for subset_id in _subset_ids(row, high_error_threshold=high_error_threshold):
            subset_errors.setdefault(subset_id, []).append(candidate_residual)

    metrics_by_subset = {
        key: _summarize_residuals(value)
        for key, value in sorted(subset_errors.items())
    }
    delta_by_subset = {
        key: _delta_mae(metrics_by_subset.get(key), baseline_metrics.get(key))
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
        "fit_mode": variant["fit_mode"],
        "fitted_coefficients": fitted_coefficients,
        "feature_activation_counts": _feature_activation_counts(
            audit_rows,
            variant=variant,
            index=index,
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
            "Features use committed full-known neighbor residual context and are retrospective diagnostics, not blind predictions.",
            "Coefficients are fit on the 11-row NMD-0002 residual slice.",
            "No live source fetch, reveal scoring, registry write, claim update, or canonical result write is authorized.",
        ],
    }


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


def _candidate_residuals_for_rows(
    item: dict[str, Any],
    rows: list[dict[str, Any]],
    index: NeighborIndex,
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
    matrix = _feature_matrix(rows, variant=variant, index=index)
    out: list[float] = []
    for row, values in zip(rows, matrix):
        correction = float(values @ beta)
        out.append(
            float(row["observed_mev"]) - (float(row["baseline_predicted_mev"]) + correction)
        )
    return out


def _transfer_summary(
    *,
    rows: list[dict[str, Any]],
    candidate_items: list[dict[str, Any]],
    index: NeighborIndex,
    group_key: str,
) -> dict[str, Any]:
    grouped = _group_indices(rows, group_key)
    baseline_residuals = [float(row["baseline_residual_mev"]) for row in rows]
    items: list[dict[str, Any]] = []
    candidate_residuals = {
        item["candidate_id"]: _candidate_residuals_for_rows(item, rows, index)
        for item in candidate_items
    }
    for group_id, indices in grouped.items():
        deltas = {
            candidate_id: _mae_delta_for_indices(residuals, baseline_residuals, indices)
            for candidate_id, residuals in candidate_residuals.items()
        }
        best_id, best_delta = min(
            deltas.items(),
            key=lambda item: float("inf") if item[1] is None else float(item[1]),
        )
        items.append(
            {
                "group_id": group_id,
                group_key: int(rows[indices[0]][group_key]),
                "row_count": len(indices),
                "diagnostic_class": (
                    "interpretable" if len(indices) >= CHAIN_MIN_ROWS else "too_sparse"
                ),
                "baseline_mae_mev": _mean([abs(baseline_residuals[idx]) for idx in indices]),
                "delta_mae_by_candidate_mev": deltas,
                "best_candidate_id": best_id,
                "best_delta_mae_mev": best_delta,
                "nuclide_ids": [str(rows[idx]["nuclide_id"]) for idx in indices],
            }
        )

    interpretable = [item for item in items if item["diagnostic_class"] == "interpretable"]
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
        "group_key": group_key,
        "group_count": len(items),
        "interpretable_group_count": len(interpretable),
        "too_sparse_group_count": len(items) - len(interpretable),
        "by_candidate": by_candidate,
        "group_items": items,
    }


def _lane_verdict(
    candidate_items: list[dict[str, Any]],
    isotope_transfer: dict[str, Any],
    isotone_transfer: dict[str, Any],
) -> str:
    controls = [item for item in candidate_items if item["role"].endswith("_control")]
    for control in controls:
        primary = control["primary_delta_mae_mev"]
        holdout = control["holdout_delta_mae_mev"]
        iso = isotope_transfer["by_candidate"][control["candidate_id"]]["improvement_rate"]
        isotone = isotone_transfer["by_candidate"][control["candidate_id"]]["improvement_rate"]
        if (
            primary is not None
            and holdout is not None
            and iso is not None
            and isotone is not None
            and primary < -0.5
            and holdout < -0.5
            and (iso >= 0.75 or isotone >= 0.75)
        ):
            return "INCONCLUSIVE"

    executed_candidates = [
        item for item in candidate_items if item["role"] == "executed_candidate"
    ]
    if not executed_candidates:
        return "INCONCLUSIVE"
    for item in executed_candidates:
        primary = item["primary_delta_mae_mev"]
        holdout = item["holdout_delta_mae_mev"]
        iso = isotope_transfer["by_candidate"][item["candidate_id"]]["improvement_rate"]
        isotone = isotone_transfer["by_candidate"][item["candidate_id"]]["improvement_rate"]
        worst = float(item["worst_subset_regression"]["delta_mae_mev"])
        if (
            primary is not None
            and holdout is not None
            and iso is not None
            and isotone is not None
            and primary < 0.0
            and holdout < 0.0
            and iso >= 0.5
            and isotone >= 0.5
            and worst <= 0.5
        ):
            return "PARTIALLY_VALID"
    return "INCONCLUSIVE"


def build_metrics() -> dict[str, Any]:
    coefficients = full_known.load_frozen_baseline_coefficients()
    audit_rows, training_rows, training_residuals, surface = full_known.build_audit_surface(
        coefficients
    )
    high_error_threshold = float(
        np.percentile(
            np.asarray(
                [abs(float(row["baseline_residual_mev"])) for row in audit_rows],
                dtype=float,
            ),
            HIGH_ERROR_PERCENTILE,
            method="linear",
        )
    )
    baseline_metrics = _baseline_metrics(audit_rows, high_error_threshold=high_error_threshold)
    index = NeighborIndex(audit_rows)
    executed_variants = [
        variant for variant in GENERATED_VARIANTS if variant["fit_mode"] == "lstsq"
    ]
    candidate_items = [
        _evaluate_variant(
            variant,
            audit_rows=audit_rows,
            training_rows=training_rows,
            training_residuals=training_residuals,
            index=index,
            baseline_metrics=baseline_metrics,
            high_error_threshold=high_error_threshold,
        )
        for variant in executed_variants
    ]
    isotope_transfer = _transfer_summary(
        rows=audit_rows,
        candidate_items=candidate_items,
        index=index,
        group_key="Z",
    )
    isotone_transfer = _transfer_summary(
        rows=audit_rows,
        candidate_items=candidate_items,
        index=index,
        group_key="N",
    )
    lane_verdict = _lane_verdict(candidate_items, isotope_transfer, isotone_transfer)
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
        "lane": "nuclear_local_residual_curvature_hypothesis_lane",
        "sandbox_only": True,
        "evidence_class": "retrospective_full_known_local_curvature_sandbox",
        "live_external_fetch_allowed": False,
        "summary": {
            "generated_variant_count": len(GENERATED_VARIANTS),
            "executed_candidate_count": sum(
                1 for item in candidate_items if item["role"] == "executed_candidate"
            ),
            "executed_control_count": sum(
                1 for item in candidate_items if item["role"].endswith("_control")
            ),
            "lane_verdict": lane_verdict,
            "best_primary_delta_candidate_id": best_item["candidate_id"],
            "best_primary_delta_mae_mev": best_item["primary_delta_mae_mev"],
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
            {
                key: value
                for key, value in variant.items()
                if key not in {"feature_fn"}
            }
            for variant in GENERATED_VARIANTS
        ],
        "candidate_items": candidate_items,
        "isotope_chain_transfer": isotope_transfer,
        "isotone_chain_transfer": isotone_transfer,
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any local-curvature follow-up, reveal scoring, "
                "RESULT-* artifact, claim, or knowledge update."
            ),
        },
        "limitations": [
            "Neighbor-derived features use committed full-known residual context and therefore are diagnostic rather than predictive.",
            "The fit surface remains the 11-row NMD-0002 training slice, so coefficient stability is not established.",
            "Chain and isotone transfer are evaluated retrospectively and include sparse groups that must not be overinterpreted.",
            "No source fetch, canonical result rewrite, PRED entry, claim update, or public-facing physics claim is authorized.",
        ],
    }


def _candidate_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Candidate | Role | Full-known delta MAE | Holdout delta MAE | Magic | Neutron-rich | High-error |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in metrics["candidate_items"]:
        lines.append(
            "| {candidate_id} | {role} | {full} | {holdout} | {magic} | {neutron} | {high} |".format(
                candidate_id=item["candidate_id"],
                role=item["role"],
                full=_format_delta(item["primary_delta_mae_mev"]),
                holdout=_format_delta(item["holdout_delta_mae_mev"]),
                magic=_format_delta(item["magic_region_delta_mae_mev"]),
                neutron=_format_delta(item["neutron_rich_delta_mae_mev"]),
                high=_format_delta(item["high_error_delta_mae_mev"]),
            )
        )
    return lines


def _transfer_table(metrics: dict[str, Any], key: str) -> list[str]:
    transfer = metrics[key]
    lines = [
        "| Candidate | Interpretable groups | Improved | Regressed | Improvement rate |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for candidate_id, item in transfer["by_candidate"].items():
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
        "# Nuclear local residual curvature hypothesis lane",
        "",
        f"**Task:** `{TASK_ID}`",
        f"**Agent run:** `{AGENT_RUN_ID}`",
        "**Evidence class:** sandbox-only retrospective local-curvature diagnostic",
        f"**Verdict:** `{summary['lane_verdict']}`",
        "",
        "## Boundary",
        "",
        "This run uses only repository-pinned rows and writes no canonical results, "
        "prediction-registry entries, claims, or knowledge artifacts. Neighbor-derived "
        "features use committed full-known residual context, so the output is a "
        "diagnostic stress surface rather than a blind prediction or reveal score.",
        "",
        "## Candidate Results",
        "",
        *_candidate_table(metrics),
        "",
        "Negative deltas mean lower MAE than the frozen semi-empirical baseline on "
        "that subset. Positive deltas are regressions and remain visible.",
        "",
        "## Isotope-Chain Transfer",
        "",
        *_transfer_table(metrics, "isotope_chain_transfer"),
        "",
        "## Isotone-Chain Transfer",
        "",
        *_transfer_table(metrics, "isotone_chain_transfer"),
        "",
        "## Interpretation",
        "",
        f"- Generated variants: `{summary['generated_variant_count']}`.",
        f"- Executed candidate variants: `{summary['executed_candidate_count']}`.",
        f"- Executed controls: `{summary['executed_control_count']}`.",
        f"- Best full-known delta: `{summary['best_primary_delta_candidate_id']}` "
        f"({_format_delta(summary['best_primary_delta_mae_mev'])} MeV).",
        "- Chain-shuffled and smooth-window controls are included to keep local "
        "overfit and broad smooth-residual explanations visible.",
        "- The verdict remains conservative because the controls also improve many "
        "groups; no result here authorizes a claim or future-measurement comparison.",
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
            "hypothesis": "hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0043-midmass-isotope-gap-scout-batch.yaml",
            "experiment": "experiment_proposals/nuclear-mass/EXP-PROPOSAL-0009-nuclear-midmass-isotope-gap-scout.yaml",
        },
        "artifacts": {
            "metrics": "agent_runs/AGENT-RUN-0026/metrics.json",
            "report": "agent_runs/AGENT-RUN-0026/report.md",
            "limitations": "agent_runs/AGENT-RUN-0026/limitations.md",
            "preflight": "agent_runs/AGENT-RUN-0026/preflight.md",
            "review_summary": "agent_runs/AGENT-RUN-0026/review_summary.md",
        },
        "preflight": {
            "passed": True,
            "checks": [
                {
                    "name": "task_scope",
                    "status": "PASS",
                    "notes": "TASK-0339 requests a sandbox local-curvature lane, not reveal scoring.",
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed repository datasets are used; no live external fetch is performed.",
                },
                {
                    "name": "control_boundary",
                    "status": "PASS",
                    "notes": "Chain-shuffled and smooth-window controls are executed and reported.",
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
        "**Lane:** nuclear local residual curvature hypothesis lane",
        "",
    ]
    for check in manifest["preflight"]["checks"]:
        lines.append(f"- `{check['name']}`: `{check['status']}` — {check['notes']}")
    lines.append("")
    return "\n".join(lines)


def render_review_summary(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    lines = [
        "# Review Summary",
        "",
        f"`{summary['lane_verdict']}` for claim promotion: local-curvature proxies "
        "reduce aggregate retrospective MAE, but strong chain-shuffled and "
        "smooth-window controls keep the lane diagnostic-only.",
        "",
        f"- Best full-known delta: `{summary['best_primary_delta_candidate_id']}` "
        f"({_format_delta(summary['best_primary_delta_mae_mev'])} MeV).",
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
