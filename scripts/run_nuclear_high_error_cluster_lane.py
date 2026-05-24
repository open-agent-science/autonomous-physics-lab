"""TASK-0343 nuclear high-error cluster hypothesis lane.

This runner maps high-error clusters on the repository-pinned full-known
nuclear residual surface, then evaluates a small bounded set of cluster
explanations against matched controls. It is retrospective, sandbox-only
evidence: it does not fetch live data, score prediction registry entries,
write canonical RESULT-* artifacts, update claims, or edit knowledge.
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


AGENT_RUN_ID = "AGENT-RUN-0030"
TASK_ID = "TASK-0343"
HIGH_ERROR_PERCENTILE = 75.0
LOCAL_DENSITY_PERCENTILE = 25.0
LOCAL_DENSITY_A_RADIUS = 4
LOCAL_DENSITY_Z_RADIUS = 2
RANDOM_CONTROL_SEED = 343
SHUFFLE_OFFSET = 11
CHAIN_MIN_ROWS = 3

DEFAULT_METRICS_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "metrics.json"
DEFAULT_REPORT_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "report.md"
DEFAULT_AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "agent_run.yaml"
DEFAULT_LIMITATIONS_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "limitations.md"
DEFAULT_PREFLIGHT_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "preflight.md"
DEFAULT_REVIEW_SUMMARY_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "review_summary.md"
DEFAULT_REVIEW_PATH = (
    REPO_ROOT / "docs" / "reviews" / "nuclear-high-error-cluster-hypothesis-lane.md"
)

FeatureFn = Callable[[dict[str, Any], "ClusterIndex"], tuple[float, ...]]


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


def _nearest_magic_distance(value: int) -> int:
    return min(abs(value - magic) for magic in MAGIC_NUMBERS)


def _near_magic(row: dict[str, Any]) -> bool:
    return (
        _nearest_magic_distance(int(row["Z"])) <= 2
        or _nearest_magic_distance(int(row["N"])) <= 2
    )


def _scaled_a(row: dict[str, Any]) -> float:
    return (float(row["A"]) - 100.0) / 100.0


class ClusterIndex:
    """Deterministic labels and controls for the full-known residual surface."""

    def __init__(self, rows: list[dict[str, Any]], high_error_threshold: float) -> None:
        self.rows = sorted(rows, key=lambda row: (int(row["A"]), int(row["Z"]), int(row["N"]), str(row["nuclide_id"])))
        self.high_error_threshold = high_error_threshold
        self.local_density_by_row = {
            str(row["row_id"]): self._local_density(row) for row in self.rows
        }
        density_values = np.asarray(list(self.local_density_by_row.values()), dtype=float)
        self.sparse_density_threshold = float(
            np.percentile(density_values, LOCAL_DENSITY_PERCENTILE, method="linear")
        )
        self.random_control_ids = self._random_control_ids()
        self.cluster_labels_by_row = {
            str(row["row_id"]): self.cluster_labels(row) for row in self.rows
        }
        self.exclusive_cluster_by_row = {
            str(row["row_id"]): self.exclusive_cluster_label(row) for row in self.rows
        }
        self._row_order_ids = [str(row["row_id"]) for row in self.rows]

    def _local_density(self, row: dict[str, Any]) -> int:
        target_id = str(row["row_id"])
        target_a = int(row["A"])
        target_z = int(row["Z"])
        return sum(
            1
            for item in self.rows
            if str(item["row_id"]) != target_id
            and abs(int(item["A"]) - target_a) <= LOCAL_DENSITY_A_RADIUS
            and abs(int(item["Z"]) - target_z) <= LOCAL_DENSITY_Z_RADIUS
        )

    def _random_control_ids(self) -> set[str]:
        count = sum(1 for row in self.rows if self.is_high_error(row))
        rng = np.random.default_rng(RANDOM_CONTROL_SEED)
        ordered_ids = np.asarray([str(row["row_id"]) for row in self.rows], dtype=object)
        selected = rng.choice(ordered_ids, size=count, replace=False)
        return {str(item) for item in selected}

    def is_high_error(self, row: dict[str, Any]) -> bool:
        return abs(float(row["baseline_residual_mev"])) >= self.high_error_threshold

    def local_density(self, row: dict[str, Any]) -> int:
        return int(self.local_density_by_row[str(row["row_id"])])

    def is_sparse_local(self, row: dict[str, Any]) -> bool:
        return float(self.local_density(row)) <= self.sparse_density_threshold

    def cluster_labels(self, row: dict[str, Any]) -> tuple[str, ...]:
        if not self.is_high_error(row):
            return ("not_high_error",)
        labels: list[str] = []
        if _near_magic(row):
            labels.append("near_magic_high_error")
        if _neutron_excess(row) >= 0.25:
            labels.append("neutron_rich_high_error")
        if self.is_sparse_local(row):
            labels.append("sparse_local_high_error")
        if bool(row["was_extrapolated"]):
            labels.append("extrapolated_source_high_error")
        if int(row["A"]) < 50:
            labels.append("light_a_high_error")
        if not labels:
            labels.append("other_high_error")
        return tuple(labels)

    def exclusive_cluster_label(self, row: dict[str, Any]) -> str:
        labels = self.cluster_labels(row)
        priority = (
            "near_magic_high_error",
            "neutron_rich_high_error",
            "sparse_local_high_error",
            "extrapolated_source_high_error",
            "light_a_high_error",
            "other_high_error",
            "not_high_error",
        )
        return next(label for label in priority if label in labels)

    def shuffled_exclusive_label(self, row: dict[str, Any]) -> str:
        row_id = str(row["row_id"])
        idx = self._row_order_ids.index(row_id)
        shifted_id = self._row_order_ids[(idx + SHUFFLE_OFFSET) % len(self._row_order_ids)]
        return self.exclusive_cluster_by_row[shifted_id]


def _near_magic_high_error(row: dict[str, Any], index: ClusterIndex) -> tuple[float, ...]:
    return (1.0 if index.is_high_error(row) and _near_magic(row) else 0.0,)


def _neutron_rich_high_error(row: dict[str, Any], index: ClusterIndex) -> tuple[float, ...]:
    return (
        _neutron_excess(row)
        if index.is_high_error(row) and _neutron_excess(row) >= 0.25
        else 0.0,
    )


def _sparse_local_high_error(row: dict[str, Any], index: ClusterIndex) -> tuple[float, ...]:
    return (1.0 if index.is_high_error(row) and index.is_sparse_local(row) else 0.0,)


def _source_status_high_error(row: dict[str, Any], index: ClusterIndex) -> tuple[float, ...]:
    return (1.0 if index.is_high_error(row) and bool(row["was_extrapolated"]) else 0.0,)


def _light_a_high_error(row: dict[str, Any], index: ClusterIndex) -> tuple[float, ...]:
    return (1.0 if index.is_high_error(row) and int(row["A"]) < 50 else 0.0,)


def _a_band_high_error(row: dict[str, Any], index: ClusterIndex) -> tuple[float, ...]:
    if not index.is_high_error(row):
        return (0.0, 0.0, 0.0)
    a = int(row["A"])
    return (
        1.0 if a < 50 else 0.0,
        1.0 if 50 <= a < 150 else 0.0,
        1.0 if a >= 150 else 0.0,
    )


def _matched_random_high_error(row: dict[str, Any], index: ClusterIndex) -> tuple[float, ...]:
    return (1.0 if str(row["row_id"]) in index.random_control_ids else 0.0,)


def _smooth_a_control(row: dict[str, Any], index: ClusterIndex) -> tuple[float, ...]:
    del index
    scaled = _scaled_a(row)
    return (scaled * scaled,)


def _shuffled_cluster_label(row: dict[str, Any], index: ClusterIndex) -> tuple[float, ...]:
    return (
        1.0
        if index.shuffled_exclusive_label(row) in {
            "near_magic_high_error",
            "neutron_rich_high_error",
            "sparse_local_high_error",
            "extrapolated_source_high_error",
            "light_a_high_error",
            "other_high_error",
        }
        else 0.0,
    )


GENERATED_VARIANTS: tuple[dict[str, Any], ...] = (
    {
        "candidate_id": "HIGHCLUSTER-001",
        "name": "Near-magic high-error cluster offset",
        "family": "magic_proximity_high_error_cluster",
        "formula": "r_corr = beta * I[abs(residual) >= p75 and near_magic(Z,N)]",
        "feature_names": ("near_magic_high_error",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "executed_candidate",
        "feature_fn": _near_magic_high_error,
    },
    {
        "candidate_id": "HIGHCLUSTER-002",
        "name": "Neutron-rich high-error cluster slope",
        "family": "neutron_rich_high_error_cluster",
        "formula": "r_corr = beta * I[abs(residual) >= p75 and (N-Z)/A >= 0.25] * ((N-Z)/A)",
        "feature_names": ("neutron_rich_high_error",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "executed_candidate",
        "feature_fn": _neutron_rich_high_error,
    },
    {
        "candidate_id": "HIGHCLUSTER-003",
        "name": "Sparse local-neighborhood high-error cluster offset",
        "family": "local_density_high_error_cluster",
        "formula": "r_corr = beta * I[abs(residual) >= p75 and local_density <= p25]",
        "feature_names": ("sparse_local_high_error",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "executed_candidate",
        "feature_fn": _sparse_local_high_error,
    },
    {
        "candidate_id": "HIGHCLUSTER-004",
        "name": "Extrapolated-source high-error cluster offset",
        "family": "source_status_high_error_cluster",
        "formula": "r_corr = beta * I[abs(residual) >= p75 and AME2020 comparison was extrapolated]",
        "feature_names": ("extrapolated_source_high_error",),
        "fit_mode": "not_executed",
        "complexity": 1,
        "role": "rejected_before_execution",
        "feature_fn": _source_status_high_error,
        "rejection_reason": (
            "Rejected before execution because the 1-3 candidate budget is "
            "already used by magic, N/Z, and local-density cluster proxies; "
            "source-status behavior remains reported as cluster context."
        ),
    },
    {
        "candidate_id": "HIGHCLUSTER-005",
        "name": "Light-A high-error cluster offset",
        "family": "light_a_high_error_cluster",
        "formula": "r_corr = beta * I[abs(residual) >= p75 and A < 50]",
        "feature_names": ("light_a_high_error",),
        "fit_mode": "not_executed",
        "complexity": 1,
        "role": "rejected_before_execution",
        "feature_fn": _light_a_high_error,
        "rejection_reason": (
            "Rejected before execution because light-A behavior is required as "
            "a diagnostic subset, and using it as a fitted patch would risk "
            "turning the lane into a small-region correction."
        ),
    },
    {
        "candidate_id": "HIGHCLUSTER-006",
        "name": "Three-band A high-error cluster offsets",
        "family": "a_band_high_error_cluster",
        "formula": "r_corr = beta_l*I[A<50] + beta_m*I[50<=A<150] + beta_h*I[A>=150], gated by high-error membership",
        "feature_names": (
            "light_a_high_error",
            "mid_a_high_error",
            "heavy_a_high_error",
        ),
        "fit_mode": "not_executed",
        "complexity": 3,
        "role": "rejected_before_execution",
        "feature_fn": _a_band_high_error,
        "rejection_reason": (
            "Rejected before execution because three fitted A-band offsets would "
            "inflate degrees of freedom on the 11-row training residual slice."
        ),
    },
    {
        "candidate_id": "HIGHCLUSTER-CONTROL-001",
        "name": "Matched random high-error count control",
        "family": "matched_random_high_error_control",
        "formula": "r_corr = beta * I[row in deterministic random set with same count as p75 high-error rows]",
        "feature_names": ("matched_random_high_error_label",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "matched_random_high_error_control",
        "feature_fn": _matched_random_high_error,
        "random_seed": RANDOM_CONTROL_SEED,
    },
    {
        "candidate_id": "HIGHCLUSTER-CONTROL-002",
        "name": "Smooth-A matched-complexity control",
        "family": "smooth_a_control",
        "formula": "r_corr = beta * ((A - 100) / 100)^2",
        "feature_names": ("smooth_a_squared",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "smooth_a_control",
        "feature_fn": _smooth_a_control,
    },
    {
        "candidate_id": "HIGHCLUSTER-CONTROL-003",
        "name": "Cluster-label shuffle control",
        "family": "cluster_label_shuffle_control",
        "formula": "r_corr = beta * cyclically shifted high-error cluster label",
        "feature_names": ("shuffled_high_error_cluster_label",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "cluster_label_shuffle_control",
        "feature_fn": _shuffled_cluster_label,
        "shuffle_scheme": "cyclic-shift-11",
        "shuffle_seed": SHUFFLE_OFFSET,
    },
)


def _feature_matrix(
    rows: list[dict[str, Any]],
    *,
    variant: dict[str, Any],
    index: ClusterIndex,
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


def _subset_ids(row: dict[str, Any], index: ClusterIndex) -> tuple[str, ...]:
    ids = list(full_known._surface_subset_ids(row))  # noqa: SLF001
    ids.append(
        "high_error_baseline_p75"
        if index.is_high_error(row)
        else "non_high_error_baseline_p75"
    )
    ids.append("neutron_rich_local" if _neutron_excess(row) >= 0.25 else "not_neutron_rich_local")
    ids.append("magic_region" if _near_magic(row) else "not_magic_region")
    ids.append("light_a_warning" if int(row["A"]) < 50 else "not_light_a_warning")
    ids.append("sparse_local_density" if index.is_sparse_local(row) else "not_sparse_local_density")
    for label in index.cluster_labels(row):
        ids.append(label)
    return tuple(dict.fromkeys(ids))


def _baseline_metrics(
    rows: list[dict[str, Any]],
    *,
    index: ClusterIndex,
) -> dict[str, dict[str, float | int | None]]:
    subset_errors: dict[str, list[float]] = {}
    for row in rows:
        for subset_id in _subset_ids(row, index):
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


def _delta_rmse(
    candidate_metrics: dict[str, float | int | None] | None,
    baseline_metrics: dict[str, float | int | None] | None,
) -> float | None:
    if candidate_metrics is None or baseline_metrics is None:
        return None
    candidate_rmse = candidate_metrics.get("rmse_mev")
    baseline_rmse = baseline_metrics.get("rmse_mev")
    if candidate_rmse is None or baseline_rmse is None:
        return None
    return float(candidate_rmse) - float(baseline_rmse)


def _fit_variant(
    variant: dict[str, Any],
    *,
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
    index: ClusterIndex,
) -> tuple[np.ndarray, dict[str, float]]:
    train_x = _feature_matrix(training_rows, variant=variant, index=index)
    beta, *_ = np.linalg.lstsq(train_x, training_residuals, rcond=None)
    return beta, {
        name: float(value)
        for name, value in zip(tuple(variant["feature_names"]), beta)
    }


def _feature_activation_counts(
    rows: list[dict[str, Any]],
    *,
    variant: dict[str, Any],
    index: ClusterIndex,
) -> dict[str, int]:
    names = tuple(variant["feature_names"])
    matrix = _feature_matrix(rows, variant=variant, index=index)
    counts = {name: 0 for name in names}
    for row_values in matrix:
        for name, value in zip(names, row_values):
            if abs(float(value)) > 0.0:
                counts[name] += 1
    return counts


def _candidate_residuals(
    rows: list[dict[str, Any]],
    *,
    variant: dict[str, Any],
    beta: np.ndarray,
    index: ClusterIndex,
) -> tuple[list[float], list[dict[str, Any]]]:
    feature_values = _feature_matrix(rows, variant=variant, index=index)
    residuals: list[float] = []
    per_row: list[dict[str, Any]] = []
    for row, values in zip(rows, feature_values):
        correction = float(values @ beta)
        candidate_residual = float(row["observed_mev"]) - (
            float(row["baseline_predicted_mev"]) + correction
        )
        residuals.append(candidate_residual)
        per_row.append(
            {
                "row_id": row["row_id"],
                "nuclide_id": row["nuclide_id"],
                "Z": int(row["Z"]),
                "N": int(row["N"]),
                "A": int(row["A"]),
                "source_surface": row["source_surface"],
                "cluster_labels": list(index.cluster_labels(row)),
                "exclusive_cluster_label": index.exclusive_cluster_label(row),
                "local_density": index.local_density(row),
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
        )
    return residuals, per_row


def _candidate_verdict(item: dict[str, Any]) -> str:
    primary = item["primary_delta_mae_mev"]
    holdout = item["holdout_delta_mae_mev"]
    high_error = item["high_error_delta_mae_mev"]
    non_high_error = item["non_high_error_delta_mae_mev"]
    worst = float(item["worst_subset_regression"]["delta_mae_mev"])
    if high_error is not None and high_error < 0.0 and non_high_error is not None and non_high_error > 0.25:
        return "OVERFITTED"
    if primary is None or holdout is None:
        return "INCONCLUSIVE"
    if worst > 0.5:
        return "OVERFITTED"
    if primary < 0.0 and holdout < 0.0 and (non_high_error is None or non_high_error <= 0.25):
        return "PARTIALLY_VALID"
    return "INCONCLUSIVE"


def _evaluate_variant(
    variant: dict[str, Any],
    *,
    audit_rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
    baseline_metrics: dict[str, dict[str, float | int | None]],
    index: ClusterIndex,
) -> dict[str, Any]:
    beta, fitted_coefficients = _fit_variant(
        variant,
        training_rows=training_rows,
        training_residuals=training_residuals,
        index=index,
    )
    residuals, per_row = _candidate_residuals(
        audit_rows,
        variant=variant,
        beta=beta,
        index=index,
    )
    subset_errors: dict[str, list[float]] = {key: [] for key in baseline_metrics}
    for row, residual in zip(audit_rows, residuals):
        for subset_id in _subset_ids(row, index):
            subset_errors.setdefault(subset_id, []).append(residual)

    metrics_by_subset = {
        key: _summarize_residuals(value)
        for key, value in sorted(subset_errors.items())
    }
    delta_mae_by_subset = {
        key: _delta_mae(metrics_by_subset.get(key), baseline_metrics.get(key))
        for key in sorted(baseline_metrics)
    }
    delta_rmse_by_subset = {
        key: _delta_rmse(metrics_by_subset.get(key), baseline_metrics.get(key))
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

    item = {
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
        "delta_mae_by_subset_mev": delta_mae_by_subset,
        "delta_rmse_by_subset_mev": delta_rmse_by_subset,
        "primary_delta_mae_mev": delta_mae_by_subset.get("full_known"),
        "primary_delta_rmse_mev": delta_rmse_by_subset.get("full_known"),
        "holdout_delta_mae_mev": delta_mae_by_subset.get("primary_holdout"),
        "training_delta_mae_mev": delta_mae_by_subset.get("training_slice"),
        "high_error_delta_mae_mev": delta_mae_by_subset.get("high_error_baseline_p75"),
        "non_high_error_delta_mae_mev": delta_mae_by_subset.get("non_high_error_baseline_p75"),
        "neutron_rich_delta_mae_mev": delta_mae_by_subset.get("neutron_rich_local"),
        "magic_region_delta_mae_mev": delta_mae_by_subset.get("magic_region"),
        "light_a_warning_delta_mae_mev": delta_mae_by_subset.get("light_a_warning"),
        "sparse_local_density_delta_mae_mev": delta_mae_by_subset.get("sparse_local_density"),
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
    }
    item["candidate_verdict"] = _candidate_verdict(item)
    item["limitations"] = [
        "High-error cluster labels are selected from committed retrospective residuals and are not blind predictive features.",
        "Coefficients are fit on the 11-row NMD-0002 residual slice.",
        "No live source fetch, reveal scoring, registry write, claim update, or canonical result write is authorized.",
    ]
    return item


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


def _candidate_residuals_from_item(
    item: dict[str, Any],
    rows: list[dict[str, Any]],
    *,
    index: ClusterIndex,
) -> list[float]:
    variant = next(
        variant for variant in GENERATED_VARIANTS if variant["candidate_id"] == item["candidate_id"]
    )
    beta = np.asarray(
        [item["fitted_coefficients"][name] for name in variant["feature_names"]],
        dtype=float,
    )
    residuals, _ = _candidate_residuals(rows, variant=variant, beta=beta, index=index)
    return residuals


def _chain_transfer_summary(
    rows: list[dict[str, Any]],
    candidate_items: list[dict[str, Any]],
    *,
    index: ClusterIndex,
) -> dict[str, Any]:
    groups: dict[int, list[int]] = {}
    for idx, row in enumerate(rows):
        groups.setdefault(int(row["Z"]), []).append(idx)
    baseline_residuals = [float(row["baseline_residual_mev"]) for row in rows]
    candidate_residuals_by_id = {
        item["candidate_id"]: _candidate_residuals_from_item(item, rows, index=index)
        for item in candidate_items
    }
    group_items: list[dict[str, Any]] = []
    for z, indices in sorted(groups.items()):
        deltas = {
            candidate_id: _mae_delta_for_indices(values, baseline_residuals, indices)
            for candidate_id, values in candidate_residuals_by_id.items()
        }
        valid_deltas = {key: value for key, value in deltas.items() if value is not None}
        best_id = None
        best_delta = None
        if valid_deltas:
            best_id, best_delta = min(valid_deltas.items(), key=lambda item: (float(item[1]), item[0]))
        high_error_rows = [rows[idx] for idx in indices if index.is_high_error(rows[idx])]
        group_items.append(
            {
                "group_id": f"Z_{z:03d}",
                "Z": z,
                "row_count": len(indices),
                "high_error_row_count": len(high_error_rows),
                "diagnostic_class": "interpretable" if len(indices) >= CHAIN_MIN_ROWS else "too_sparse",
                "baseline_mae_mev": _mean([abs(baseline_residuals[idx]) for idx in indices]),
                "delta_mae_by_candidate_mev": deltas,
                "best_candidate_id": best_id,
                "best_delta_mae_mev": best_delta,
                "nuclide_ids": [str(rows[idx]["nuclide_id"]) for idx in indices],
            }
        )

    interpretable = [item for item in group_items if item["diagnostic_class"] == "interpretable"]
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
                        "high_error_row_count": item["high_error_row_count"],
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


def _cluster_summary(rows: list[dict[str, Any]], index: ClusterIndex) -> dict[str, Any]:
    counts: dict[str, int] = {}
    exclusive_counts: dict[str, int] = {}
    cluster_rows: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        for label in index.cluster_labels(row):
            counts[label] = counts.get(label, 0) + 1
            if label != "not_high_error":
                cluster_rows.setdefault(label, []).append(row)
        exclusive = index.exclusive_cluster_label(row)
        exclusive_counts[exclusive] = exclusive_counts.get(exclusive, 0) + 1
    items = []
    for label, label_rows in sorted(cluster_rows.items()):
        items.append(
            {
                "cluster_label": label,
                "row_count": len(label_rows),
                "baseline_mae_mev": _mean([abs(float(row["baseline_residual_mev"])) for row in label_rows]),
                "median_a": float(np.median(np.asarray([int(row["A"]) for row in label_rows], dtype=float))),
                "nuclide_ids": [str(row["nuclide_id"]) for row in label_rows[:12]],
            }
        )
    return {
        "thresholds_selected_before_candidate_fitting": True,
        "cluster_labels_are_overlapping": True,
        "high_error_count": sum(1 for row in rows if index.is_high_error(row)),
        "high_error_threshold_mev": index.high_error_threshold,
        "sparse_local_density_threshold": index.sparse_density_threshold,
        "cluster_counts": dict(sorted(counts.items())),
        "exclusive_cluster_counts": dict(sorted(exclusive_counts.items())),
        "cluster_items": items,
    }


def _best_control_delta(candidate_items: list[dict[str, Any]]) -> float | None:
    control_deltas = [
        item["primary_delta_mae_mev"]
        for item in candidate_items
        if item["role"].endswith("_control") and item["primary_delta_mae_mev"] is not None
    ]
    if not control_deltas:
        return None
    return float(min(control_deltas))


def _control_gate(candidate_items: list[dict[str, Any]]) -> dict[str, Any]:
    controls = [item for item in candidate_items if item["role"].endswith("_control")]
    best_control = min(
        controls,
        key=lambda item: (
            float("inf") if item["primary_delta_mae_mev"] is None else float(item["primary_delta_mae_mev"]),
            item["candidate_id"],
        ),
    )
    gated: dict[str, Any] = {}
    for item in candidate_items:
        if item["role"] != "executed_candidate":
            continue
        primary = item["primary_delta_mae_mev"]
        gated[item["candidate_id"]] = {
            "best_control_id": best_control["candidate_id"],
            "best_control_primary_delta_mae_mev": best_control["primary_delta_mae_mev"],
            "candidate_primary_delta_mae_mev": primary,
            "candidate_beats_controls": (
                primary is not None
                and best_control["primary_delta_mae_mev"] is not None
                and float(primary) < float(best_control["primary_delta_mae_mev"]) - 0.02
            ),
        }
    return gated


def _lane_verdict(candidate_items: list[dict[str, Any]]) -> str:
    best_control = _best_control_delta(candidate_items)
    for item in candidate_items:
        if item["role"] != "executed_candidate":
            continue
        if item["candidate_verdict"] == "OVERFITTED":
            continue
        primary = item["primary_delta_mae_mev"]
        holdout = item["holdout_delta_mae_mev"]
        non_high_error = item["non_high_error_delta_mae_mev"]
        if (
            primary is not None
            and holdout is not None
            and primary < 0.0
            and holdout < 0.0
            and (non_high_error is None or non_high_error <= 0.25)
            and (best_control is None or primary < best_control - 0.02)
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
    index = ClusterIndex(audit_rows, high_error_threshold)
    baseline_metrics = _baseline_metrics(audit_rows, index=index)
    executed_variants = [
        variant for variant in GENERATED_VARIANTS if variant["fit_mode"] == "lstsq"
    ]
    candidate_items = [
        _evaluate_variant(
            variant,
            audit_rows=audit_rows,
            training_rows=training_rows,
            training_residuals=training_residuals,
            baseline_metrics=baseline_metrics,
            index=index,
        )
        for variant in executed_variants
    ]
    chain_transfer = _chain_transfer_summary(audit_rows, candidate_items, index=index)
    lane_verdict = _lane_verdict(candidate_items)
    best_item = min(
        candidate_items,
        key=lambda item: (
            float("inf") if item["primary_delta_mae_mev"] is None else float(item["primary_delta_mae_mev"]),
            item["candidate_id"],
        ),
    )
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "nuclear_high_error_cluster_hypothesis_lane",
        "sandbox_only": True,
        "evidence_class": "retrospective_full_known_high_error_cluster_sandbox",
        "live_external_fetch_allowed": False,
        "summary": {
            "generated_candidate_count": sum(
                1 for item in GENERATED_VARIANTS if item["role"] in {"executed_candidate", "rejected_before_execution"}
            ),
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
        "cluster_summary": _cluster_summary(audit_rows, index),
        "baseline_metrics_by_subset": baseline_metrics,
        "generated_variants": [
            {key: value for key, value in variant.items() if key not in {"feature_fn"}}
            for variant in GENERATED_VARIANTS
        ],
        "candidate_items": candidate_items,
        "matched_control_gate": _control_gate(candidate_items),
        "isotope_chain_transfer": chain_transfer,
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any high-error-cluster follow-up, "
                "reveal scoring, RESULT-* artifact, claim, or knowledge update."
            ),
        },
        "limitations": [
            "High-error membership and cluster labels come from committed retrospective residuals, so this is a diagnostic lane rather than a blind prediction.",
            "Candidate thresholds are deterministic and selected before candidate fitting, but the surface is still full-known repository data.",
            "The fit surface remains the 11-row NMD-0002 training slice, so coefficient stability is not established.",
            "Matched random, smooth-A, and cluster-label-shuffle controls are reported because high-error targeting can overfit broad residual structure.",
            "No source fetch, canonical result rewrite, PRED entry, claim update, or public-facing physics claim is authorized.",
        ],
    }


def _candidate_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Candidate | Role | Verdict | Full-known MAE | Holdout | High-error | Non-high-error | Neutron-rich | Magic | Light-A | Chain improvement rate |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    transfer = metrics["isotope_chain_transfer"]["by_candidate"]
    for item in metrics["candidate_items"]:
        chain = transfer[item["candidate_id"]]["improvement_rate"]
        lines.append(
            "| {candidate_id} | {role} | {verdict} | {primary} | {holdout} | {high} | {non_high} | {neutron} | {magic} | {light} | {chain} |".format(
                candidate_id=item["candidate_id"],
                role=item["role"],
                verdict=item["candidate_verdict"],
                primary=_format_delta(item["primary_delta_mae_mev"]),
                holdout=_format_delta(item["holdout_delta_mae_mev"]),
                high=_format_delta(item["high_error_delta_mae_mev"]),
                non_high=_format_delta(item["non_high_error_delta_mae_mev"]),
                neutron=_format_delta(item["neutron_rich_delta_mae_mev"]),
                magic=_format_delta(item["magic_region_delta_mae_mev"]),
                light=_format_delta(item["light_a_warning_delta_mae_mev"]),
                chain="n/a" if chain is None else f"{chain:.3f}",
            )
        )
    return lines


def _cluster_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Cluster | Rows | Baseline MAE | Median A | Example nuclides |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for item in metrics["cluster_summary"]["cluster_items"]:
        examples = ", ".join(item["nuclide_ids"][:6])
        lines.append(
            "| {cluster} | {rows} | {mae} | {median_a:.1f} | {examples} |".format(
                cluster=item["cluster_label"],
                rows=item["row_count"],
                mae="n/a" if item["baseline_mae_mev"] is None else f"{item['baseline_mae_mev']:.6f}",
                median_a=float(item["median_a"]),
                examples=examples,
            )
        )
    return lines


def _control_gate_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Candidate | Best control | Candidate primary | Best control primary | Beats controls |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for candidate_id, item in metrics["matched_control_gate"].items():
        lines.append(
            "| {candidate_id} | {control} | {candidate} | {control_delta} | {beats} |".format(
                candidate_id=candidate_id,
                control=item["best_control_id"],
                candidate=_format_delta(item["candidate_primary_delta_mae_mev"]),
                control_delta=_format_delta(item["best_control_primary_delta_mae_mev"]),
                beats="yes" if item["candidate_beats_controls"] else "no",
            )
        )
    return lines


def render_report(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    cluster = metrics["cluster_summary"]
    lines = [
        "# Nuclear high-error cluster hypothesis lane",
        "",
        f"**Task:** `{TASK_ID}`",
        f"**Agent run:** `{AGENT_RUN_ID}`",
        "**Evidence class:** sandbox-only retrospective high-error cluster diagnostic",
        f"**Verdict:** `{summary['lane_verdict']}`",
        "",
        "## Boundary",
        "",
        "This run uses only repository-pinned rows and deterministic thresholds "
        "selected before candidate fitting. It writes no canonical results, "
        "prediction-registry entries, claims, or knowledge artifacts. High-error "
        "cluster labels come from committed residuals and are therefore diagnostic "
        "rather than blind prediction features.",
        "",
        "## High-Error Cluster Map",
        "",
        f"- High-error threshold: `{summary['high_error_threshold_mev']:.6f}` MeV "
        f"at baseline absolute-error percentile `{summary['high_error_percentile']:.1f}`.",
        f"- High-error rows: `{cluster['high_error_count']}`.",
        f"- Sparse local-density threshold: `{cluster['sparse_local_density_threshold']:.6f}` "
        f"neighbors at percentile `{LOCAL_DENSITY_PERCENTILE:.1f}`.",
        "",
        *_cluster_table(metrics),
        "",
        "## Candidate And Control Results",
        "",
        *_candidate_table(metrics),
        "",
        "Negative deltas mean lower MAE than the frozen semi-empirical baseline on "
        "that subset. Positive deltas are regressions and remain visible.",
        "",
        "## Matched Control Gate",
        "",
        *_control_gate_table(metrics),
        "",
        "## Interpretation",
        "",
        f"- Generated bounded cluster explanations: `{summary['generated_candidate_count']}`.",
        f"- Executed candidate explanations: `{summary['executed_candidate_count']}`.",
        f"- Executed controls: `{summary['executed_control_count']}`.",
        f"- Best full-known delta: `{summary['best_primary_delta_candidate_id']}` "
        f"({_format_delta(summary['best_primary_delta_mae_mev'])} MeV MAE; "
        f"{_format_delta(summary['best_primary_delta_rmse_mev'])} MeV RMSE).",
        "- Matched random high-error, smooth-A, and cluster-label-shuffle controls "
        "are reported to keep post-hoc cluster targeting visible.",
        "- Candidates that improve only high-error rows while materially regressing "
        "non-high-error rows are marked `OVERFITTED` and not promoted.",
        "- The lane verdict is conservative; no result here authorizes claim "
        "promotion or future-measurement comparison.",
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in metrics["limitations"]],
        "",
    ]
    return "\n".join(lines)


def render_agent_run(metrics: dict[str, Any]) -> str:
    lane_verdict = metrics["summary"]["lane_verdict"]
    manifest_verdict = {
        "PARTIALLY_VALID": "REVIEW_NEEDED",
        "INCONCLUSIVE": "INCONCLUSIVE",
        "OVERFITTED": "OVERFITTED",
        "FALSIFIED": "FALSIFIED",
    }.get(str(lane_verdict), "REVIEW_NEEDED")
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
            "hypothesis": "hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0050-high-error-cluster-scout.yaml",
            "experiment": "experiment_proposals/nuclear-mass/EXP-PROPOSAL-0016-nuclear-high-error-cluster-scout.yaml",
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
                    "notes": "TASK-0343 requests a sandbox high-error cluster lane, not reveal scoring.",
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed repository datasets and pinned baseline residuals are used.",
                },
                {
                    "name": "threshold_boundary",
                    "status": "PASS",
                    "notes": "High-error and sparse-density thresholds are deterministic and selected before candidate fitting.",
                },
                {
                    "name": "control_boundary",
                    "status": "PASS",
                    "notes": "Matched random high-error, smooth-A, and cluster-label-shuffle controls are executed and reported.",
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No prediction registry, canonical result, claim, or knowledge file is written.",
                },
            ],
        },
        "limitations": metrics["limitations"],
        "verdict": manifest_verdict,
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
        "**Lane:** nuclear high-error cluster hypothesis lane",
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
        f"`{summary['lane_verdict']}` for claim promotion: high-error cluster "
        "proxies are deterministic and reviewable, but the labels are derived "
        "from committed retrospective residuals and matched controls remain visible.",
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
