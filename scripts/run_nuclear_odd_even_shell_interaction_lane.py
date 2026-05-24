"""TASK-0340 nuclear odd-even shell-interaction hypothesis lane.

This runner evaluates bounded odd-even by shell-proximity interaction proxies
using only repository-pinned Z, N, and A fields. It is retrospective,
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

from physics_lab.engines.nuclear_mass_baselines import (  # noqa: E402
    MAGIC_NUMBERS,
    pairing_sign,
)

import scripts.run_nuclear_shell_axis_full_known_audit as full_known  # noqa: E402


AGENT_RUN_ID = "AGENT-RUN-0027"
TASK_ID = "TASK-0340"
SHUFFLE_OFFSET = 3

DEFAULT_METRICS_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "metrics.json"
DEFAULT_REPORT_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "report.md"
DEFAULT_AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "agent_run.yaml"
DEFAULT_LIMITATIONS_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "limitations.md"
DEFAULT_PREFLIGHT_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "preflight.md"
DEFAULT_REVIEW_SUMMARY_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "review_summary.md"
DEFAULT_REVIEW_PATH = (
    REPO_ROOT / "docs" / "reviews" / "nuclear-odd-even-shell-interaction-lane.md"
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


def _shell_proximity(value: int, *, sigma: float = 2.0) -> float:
    distance = float(_nearest_magic_distance(value))
    return float(np.exp(-(distance * distance) / (2.0 * sigma * sigma)))


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


def _pairing(row: dict[str, Any]) -> float:
    return float(pairing_sign(int(row["Z"]), int(row["N"])))


def _odd_a_indicator(row: dict[str, Any]) -> float:
    return 1.0 if pairing_sign(int(row["Z"]), int(row["N"])) == 0 else 0.0


def _shell_any(row: dict[str, Any]) -> float:
    return max(_shell_proximity(int(row["Z"])), _shell_proximity(int(row["N"])))


def _shell_product(row: dict[str, Any]) -> float:
    return _shell_proximity(int(row["Z"])) * _shell_proximity(int(row["N"]))


def _mid_shell_average(row: dict[str, Any]) -> float:
    return 0.5 * (
        _mid_shell_occupancy(int(row["Z"])) + _mid_shell_occupancy(int(row["N"]))
    )


def _scaled_a_squared(row: dict[str, Any]) -> float:
    scaled = (float(row["A"]) - 100.0) / 100.0
    return scaled * scaled


def _pairing_shell_any(row: dict[str, Any]) -> tuple[float, ...]:
    return (_pairing(row) * _shell_any(row),)


def _pairing_shell_product(row: dict[str, Any]) -> tuple[float, ...]:
    return (_pairing(row) * _shell_product(row),)


def _odd_a_mid_shell(row: dict[str, Any]) -> tuple[float, ...]:
    return (_odd_a_indicator(row) * _mid_shell_average(row),)


def _even_odd_shell_split(row: dict[str, Any]) -> tuple[float, ...]:
    sign = pairing_sign(int(row["Z"]), int(row["N"]))
    shell = _shell_any(row)
    return (
        shell if sign > 0 else 0.0,
        shell if sign < 0 else 0.0,
        shell if sign == 0 else 0.0,
    )


def _pairing_mid_shell(row: dict[str, Any]) -> tuple[float, ...]:
    return (_pairing(row) * _mid_shell_average(row),)


def _neutron_rich_pairing_shell(row: dict[str, Any]) -> tuple[float, ...]:
    return (_pairing(row) * _shell_any(row) * _neutron_excess(row),)


def _pairing_only(row: dict[str, Any]) -> tuple[float, ...]:
    return (_pairing(row) / np.sqrt(float(row["A"])),)


def _shell_only(row: dict[str, Any]) -> tuple[float, ...]:
    return (_shell_any(row),)


def _smooth_a_control(row: dict[str, Any]) -> tuple[float, ...]:
    return (_scaled_a_squared(row),)


GENERATED_VARIANTS: tuple[dict[str, Any], ...] = (
    {
        "candidate_id": "ODD-SHELL-001",
        "name": "Pairing sign times nearest shell proximity",
        "family": "pairing_shell_interaction",
        "formula": "r_corr = beta * pairing_sign(Z,N) * max(shell_Z, shell_N)",
        "feature_names": ("pairing_shell_any",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "executed_interaction_candidate",
        "feature_fn": _pairing_shell_any,
    },
    {
        "candidate_id": "ODD-SHELL-002",
        "name": "Pairing sign times double-axis shell proximity",
        "family": "pairing_double_shell_interaction",
        "formula": "r_corr = beta * pairing_sign(Z,N) * shell_Z * shell_N",
        "feature_names": ("pairing_shell_product",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "executed_interaction_candidate",
        "feature_fn": _pairing_shell_product,
    },
    {
        "candidate_id": "ODD-SHELL-003",
        "name": "Odd-A mid-shell interaction",
        "family": "odd_a_mid_shell_interaction",
        "formula": "r_corr = beta * I[odd-A] * mean(mid_shell_Z, mid_shell_N)",
        "feature_names": ("odd_a_mid_shell",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "executed_interaction_candidate",
        "feature_fn": _odd_a_mid_shell,
    },
    {
        "candidate_id": "ODD-SHELL-004",
        "name": "Three-class parity shell offsets",
        "family": "parity_shell_class_interaction",
        "formula": "r_corr = beta_ee*I[ee]*S + beta_oo*I[oo]*S + beta_oddA*I[odd-A]*S",
        "feature_names": (
            "even_even_shell",
            "odd_odd_shell",
            "odd_a_shell",
        ),
        "fit_mode": "not_executed",
        "complexity": 3,
        "role": "rejected_before_execution",
        "feature_fn": _even_odd_shell_split,
        "rejection_reason": (
            "Rejected before execution because three free parity-shell offsets "
            "would exceed the one-degree interaction comparison and risk "
            "memorizing sparse odd-odd behavior."
        ),
    },
    {
        "candidate_id": "ODD-SHELL-005",
        "name": "Pairing sign times mid-shell occupancy",
        "family": "pairing_mid_shell_interaction",
        "formula": "r_corr = beta * pairing_sign(Z,N) * mean(mid_shell_Z, mid_shell_N)",
        "feature_names": ("pairing_mid_shell",),
        "fit_mode": "not_executed",
        "complexity": 1,
        "role": "rejected_before_execution",
        "feature_fn": _pairing_mid_shell,
        "rejection_reason": (
            "Rejected before execution because the 1-3 candidate sandbox budget "
            "is already used by two shell-proximity interactions and one odd-A "
            "mid-shell interaction; the variant is preserved as future context."
        ),
    },
    {
        "candidate_id": "ODD-SHELL-006",
        "name": "Neutron-excess weighted pairing-shell interaction",
        "family": "neutron_rich_pairing_shell_interaction",
        "formula": "r_corr = beta * pairing_sign(Z,N) * shell_any * ((N-Z)/A)",
        "feature_names": ("neutron_rich_pairing_shell",),
        "fit_mode": "not_executed",
        "complexity": 1,
        "role": "rejected_before_execution",
        "feature_fn": _neutron_rich_pairing_shell,
        "rejection_reason": (
            "Rejected before execution because neutron-rich weighting is a "
            "separate subset diagnostic here and would add an extra targeted "
            "interpretation layer."
        ),
    },
    {
        "candidate_id": "ODD-SHELL-CONTROL-001",
        "name": "Pairing-only lower-complexity control",
        "family": "pairing_only_control",
        "formula": "r_corr = beta * pairing_sign(Z,N) / sqrt(A)",
        "feature_names": ("pairing_inv_sqrt_a",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "pairing_only_control",
        "feature_fn": _pairing_only,
    },
    {
        "candidate_id": "ODD-SHELL-CONTROL-002",
        "name": "Shell-only lower-complexity control",
        "family": "shell_only_control",
        "formula": "r_corr = beta * max(shell_Z, shell_N)",
        "feature_names": ("shell_any",),
        "fit_mode": "lstsq",
        "complexity": 1,
        "role": "shell_only_control",
        "feature_fn": _shell_only,
    },
    {
        "candidate_id": "ODD-SHELL-CONTROL-003",
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
        "candidate_id": "ODD-SHELL-CONTROL-004",
        "name": "Cyclically shuffled interaction control",
        "family": "shuffled_interaction_control",
        "formula": "r_corr = beta * shuffled(pairing_sign * shell_any)",
        "feature_names": ("shuffled_pairing_shell_any",),
        "fit_mode": "lstsq_shuffled",
        "complexity": 1,
        "role": "shuffled_interaction_control",
        "feature_fn": _pairing_shell_any,
        "shuffle_scheme": "cyclic-shift-3",
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
    sign = pairing_sign(int(row["Z"]), int(row["N"]))
    if sign > 0:
        ids.append("even_even")
    elif sign < 0:
        ids.append("odd_odd")
    else:
        ids.append("odd_even")
    ids.append("light_a_warning" if int(row["A"]) < 50 else "not_light_a_warning")
    ids.append("neutron_rich_local" if _neutron_excess(row) >= 0.25 else "not_neutron_rich_local")
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
        "even_even_delta_mae_mev": delta_mae_by_subset.get("even_even"),
        "odd_even_delta_mae_mev": delta_mae_by_subset.get("odd_even"),
        "odd_odd_delta_mae_mev": delta_mae_by_subset.get("odd_odd"),
        "magic_z_delta_mae_mev": delta_mae_by_subset.get("magic_z"),
        "magic_n_delta_mae_mev": delta_mae_by_subset.get("magic_n"),
        "light_a_warning_delta_mae_mev": delta_mae_by_subset.get("light_a_warning"),
        "neutron_rich_delta_mae_mev": delta_mae_by_subset.get("neutron_rich_local"),
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
            "Features are bounded odd-even by shell-proximity proxies, not direct nuclear-structure measurements.",
            "Coefficients are fit on the 11-row NMD-0002 residual slice.",
            "No live source fetch, reveal scoring, registry write, claim update, or canonical result write is authorized.",
        ],
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


def _control_gate(
    candidate_items: list[dict[str, Any]],
) -> dict[str, Any]:
    best_control = min(
        [item for item in candidate_items if item["role"].endswith("_control")],
        key=lambda item: (
            float("inf")
            if item["primary_delta_mae_mev"] is None
            else float(item["primary_delta_mae_mev"]),
            item["candidate_id"],
        ),
    )
    gated: dict[str, Any] = {}
    for item in candidate_items:
        if item["role"] != "executed_interaction_candidate":
            continue
        primary = item["primary_delta_mae_mev"]
        gated[item["candidate_id"]] = {
            "best_lower_or_matched_control_id": best_control["candidate_id"],
            "best_control_primary_delta_mae_mev": best_control["primary_delta_mae_mev"],
            "candidate_primary_delta_mae_mev": primary,
            "interaction_beats_controls": (
                primary is not None
                and best_control["primary_delta_mae_mev"] is not None
                and float(primary) < float(best_control["primary_delta_mae_mev"]) - 0.02
            ),
        }
    return gated


def _lane_verdict(candidate_items: list[dict[str, Any]]) -> str:
    best_control = _best_control_delta(candidate_items)
    for item in candidate_items:
        if item["role"] != "executed_interaction_candidate":
            continue
        primary = item["primary_delta_mae_mev"]
        holdout = item["holdout_delta_mae_mev"]
        worst = float(item["worst_subset_regression"]["delta_mae_mev"])
        if (
            primary is not None
            and holdout is not None
            and primary < 0.0
            and holdout < 0.0
            and worst <= 0.5
            and (best_control is None or primary < best_control - 0.02)
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
    lane_verdict = _lane_verdict(candidate_items)
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
        "lane": "nuclear_odd_even_shell_interaction_hypothesis_lane",
        "sandbox_only": True,
        "evidence_class": "retrospective_full_known_odd_even_shell_interaction_sandbox",
        "live_external_fetch_allowed": False,
        "summary": {
            "generated_interaction_variant_count": 6,
            "executed_interaction_count": sum(
                1
                for item in candidate_items
                if item["role"] == "executed_interaction_candidate"
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
        "lower_complexity_control_gate": _control_gate(candidate_items),
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any odd-even shell-interaction follow-up, "
                "reveal scoring, RESULT-* artifact, claim, or knowledge update."
            ),
        },
        "limitations": [
            "These features are odd-even by shell-proximity interaction proxies, not measured nuclear-structure parameters.",
            "The fit surface remains the 11-row NMD-0002 training slice, so coefficient stability is not established.",
            "Odd-odd subset behavior is sparse and must not be overinterpreted.",
            "The full-known surface is retrospective committed repository data, not a future-measurement reveal.",
            "Lower-complexity and shuffled controls are included because aggregate improvements can reflect pairing-only, shell-only, or small-sample residual structure.",
            "No source fetch, canonical result rewrite, PRED entry, claim update, or public-facing physics claim is authorized.",
        ],
    }


def _candidate_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Candidate | Role | Full-known MAE | Holdout | Even-even | Odd-even | Odd-odd | Magic-Z | Magic-N | Light-A | Neutron-rich |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in metrics["candidate_items"]:
        lines.append(
            "| {candidate_id} | {role} | {primary} | {holdout} | {ee} | {oe} | {oo} | {mz} | {mn} | {light} | {neutron} |".format(
                candidate_id=item["candidate_id"],
                role=item["role"],
                primary=_format_delta(item["primary_delta_mae_mev"]),
                holdout=_format_delta(item["holdout_delta_mae_mev"]),
                ee=_format_delta(item["even_even_delta_mae_mev"]),
                oe=_format_delta(item["odd_even_delta_mae_mev"]),
                oo=_format_delta(item["odd_odd_delta_mae_mev"]),
                mz=_format_delta(item["magic_z_delta_mae_mev"]),
                mn=_format_delta(item["magic_n_delta_mae_mev"]),
                light=_format_delta(item["light_a_warning_delta_mae_mev"]),
                neutron=_format_delta(item["neutron_rich_delta_mae_mev"]),
            )
        )
    return lines


def _control_gate_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Interaction | Best control | Candidate primary | Best control primary | Beats controls |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for candidate_id, item in metrics["lower_complexity_control_gate"].items():
        lines.append(
            "| {candidate_id} | {control} | {candidate} | {control_delta} | {beats} |".format(
                candidate_id=candidate_id,
                control=item["best_lower_or_matched_control_id"],
                candidate=_format_delta(item["candidate_primary_delta_mae_mev"]),
                control_delta=_format_delta(item["best_control_primary_delta_mae_mev"]),
                beats="yes" if item["interaction_beats_controls"] else "no",
            )
        )
    return lines


def render_report(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    lines = [
        "# Nuclear odd-even shell-interaction hypothesis lane",
        "",
        f"**Task:** `{TASK_ID}`",
        f"**Agent run:** `{AGENT_RUN_ID}`",
        "**Evidence class:** sandbox-only retrospective odd-even shell-interaction diagnostic",
        f"**Verdict:** `{summary['lane_verdict']}`",
        "",
        "## Boundary",
        "",
        "This run uses only repository-pinned rows and Z/N/A-derived parity and "
        "shell-proximity features. It writes no canonical results, "
        "prediction-registry entries, claims, or knowledge artifacts. Shell-axis "
        "and pairing-only evidence remain diagnostic context rather than promoted "
        "claims.",
        "",
        "## Candidate And Control Results",
        "",
        *_candidate_table(metrics),
        "",
        "Negative deltas mean lower MAE than the frozen semi-empirical baseline on "
        "that subset. Positive deltas are regressions and remain visible.",
        "",
        "## Lower-Complexity Control Gate",
        "",
        *_control_gate_table(metrics),
        "",
        "## Interpretation",
        "",
        f"- Generated interaction variants: `{summary['generated_interaction_variant_count']}`.",
        f"- Executed interaction candidates: `{summary['executed_interaction_count']}`.",
        f"- Executed controls: `{summary['executed_control_count']}`.",
        f"- Best full-known delta: `{summary['best_primary_delta_candidate_id']}` "
        f"({_format_delta(summary['best_primary_delta_mae_mev'])} MeV MAE; "
        f"{_format_delta(summary['best_primary_delta_rmse_mev'])} MeV RMSE).",
        "- Pairing-only, shell-only, smooth-A, and shuffled-interaction controls "
        "are reported next to candidates to keep simpler explanations visible.",
        "- The verdict stays conservative; no result here authorizes claim "
        "promotion or future-measurement comparison.",
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
            "hypothesis": "hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0047-odd-even-shell-interaction-scout-batch.yaml",
            "experiment": "experiment_proposals/nuclear-mass/EXP-PROPOSAL-0013-nuclear-odd-even-shell-interaction-scout.yaml",
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
                    "notes": "TASK-0340 requests a sandbox odd-even shell-interaction lane, not reveal scoring.",
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed repository datasets and derived Z/N/A proxies are used.",
                },
                {
                    "name": "control_boundary",
                    "status": "PASS",
                    "notes": "Pairing-only, shell-only, smooth-A, and shuffled-interaction controls are executed and reported.",
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
        "**Lane:** nuclear odd-even shell-interaction hypothesis lane",
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
        f"`{summary['lane_verdict']}` for claim promotion: odd-even shell-interaction "
        "proxies are deterministic and reviewable, but lower-complexity and shuffled "
        "controls remain visible and the lane stays sandbox-only.",
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
