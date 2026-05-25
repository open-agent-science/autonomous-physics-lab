"""TASK-0367 nuclear high-error cluster adversarial stability audit.

Re-evaluates the TASK-0343 / AGENT-RUN-0030 high-error cluster candidates
(HIGHCLUSTER-001/002/003) against three stronger adversarial controls and
two additional stability diagnostics so the cluster signal can either be
preserved as evidence that survived stronger controls or recorded as an
overfit / threshold-specific diagnostic.

New adversarial controls (each at the same complexity-1 fit form as the
original candidates):

- ``HIGHCLUSTER-ADV-001`` — random-permutation cluster-label control. A
  deterministic random permutation of the exclusive cluster labels across
  rows; stronger than the predecessor cyclic shift-11 control because it
  breaks any residual locality that a cyclic shift can preserve.
- ``HIGHCLUSTER-ADV-002`` — pure local-density smoother. Uses the raw
  per-row local-density count with no high-error gating; competes directly
  with HIGHCLUSTER-003's density-gated feature.
- ``HIGHCLUSTER-ADV-003`` — near-null deterministic jitter. A per-row
  Normal(0, 1e-3 MeV) feature seeded deterministically; should produce
  essentially zero MAE delta and acts as the null floor.

Two stability diagnostics are added alongside the adversarial-controls
comparison:

- High-error threshold perturbation re-fits HIGHCLUSTER-001/002/003 at
  baseline-residual percentiles 65 / 70 / 75 / 80 and reports the
  full-known MAE delta and fitted coefficient at each threshold.
- Deterministic leave-one-out (LOO) coefficient stability re-fits each
  executed candidate on every 10-of-11 subset of the NMD-0002 training
  slice and reports the coefficient spread, sign-flip count, and
  full-known MAE delta range.

This runner is sandbox-only retrospective evidence. It reads only
committed repository datasets, fetches no live data, writes no canonical
RESULT-* artifact, no PRED-* entry, no claim, and no knowledge file.
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
PREDECESSOR_TASK_ID = lane.TASK_ID
PREDECESSOR_AGENT_RUN_ID = lane.AGENT_RUN_ID

PRIMARY_PERCENTILE = lane.HIGH_ERROR_PERCENTILE
THRESHOLD_PERTURBATION_PERCENTILES: tuple[float, ...] = (65.0, 70.0, 75.0, 80.0)
PRIMARY_SURVIVAL_MARGIN_MEV = 0.25
NON_HIGH_ERROR_REGRESSION_THRESHOLD_MEV = 0.25
LOO_COEFFICIENT_RANGE_LIMIT = 1.0
RANDOM_PERMUTATION_SEED = 367
NEAR_NULL_NOISE_SEED = 3670
NEAR_NULL_NOISE_STD_MEV = 1.0e-3

EXECUTED_CANDIDATE_IDS: tuple[str, ...] = (
    "HIGHCLUSTER-001",
    "HIGHCLUSTER-002",
    "HIGHCLUSTER-003",
)
EXISTING_CONTROL_IDS: tuple[str, ...] = (
    "HIGHCLUSTER-CONTROL-001",
    "HIGHCLUSTER-CONTROL-002",
    "HIGHCLUSTER-CONTROL-003",
)
NEW_ADVERSARIAL_CONTROL_IDS: tuple[str, ...] = (
    "HIGHCLUSTER-ADV-001",
    "HIGHCLUSTER-ADV-002",
    "HIGHCLUSTER-ADV-003",
)

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


# ---------------------------------------------------------------------------
# Deterministic per-index caches for new adversarial control features.
# Each cache is keyed by the ClusterIndex identity so that test runs with
# different surfaces (e.g. the toy fixtures) do not bleed across calls.
# ---------------------------------------------------------------------------


class _PermutedLabelCache:
    """Deterministic random permutation of exclusive cluster labels."""

    def __init__(self, index: lane.ClusterIndex, seed: int) -> None:
        rng = np.random.default_rng(seed)
        row_ids = sorted(index.exclusive_cluster_by_row.keys())
        labels = [index.exclusive_cluster_by_row[row_id] for row_id in row_ids]
        order = rng.permutation(len(row_ids))
        self.permuted: dict[str, str] = {
            row_id: labels[int(order[idx])] for idx, row_id in enumerate(row_ids)
        }

    def is_high_error_after_permutation(self, row: dict[str, Any]) -> bool:
        label = self.permuted.get(str(row["row_id"]), "not_high_error")
        return label != "not_high_error"


class _NoiseCache:
    """Deterministic Normal(0, std) jitter per row id."""

    def __init__(self, index: lane.ClusterIndex, seed: int, std: float) -> None:
        rng = np.random.default_rng(seed)
        row_ids = sorted(index.cluster_labels_by_row.keys())
        self.values: dict[str, float] = {
            row_id: float(rng.normal(0.0, std)) for row_id in row_ids
        }


_PERMUTED_CACHE: dict[int, _PermutedLabelCache] = {}
_NOISE_CACHE: dict[int, _NoiseCache] = {}


def _permuted_cache(index: lane.ClusterIndex) -> _PermutedLabelCache:
    cached = _PERMUTED_CACHE.get(id(index))
    if cached is None:
        cached = _PermutedLabelCache(index, RANDOM_PERMUTATION_SEED)
        _PERMUTED_CACHE[id(index)] = cached
    return cached


def _noise_cache(index: lane.ClusterIndex) -> _NoiseCache:
    cached = _NOISE_CACHE.get(id(index))
    if cached is None:
        cached = _NoiseCache(index, NEAR_NULL_NOISE_SEED, NEAR_NULL_NOISE_STD_MEV)
        _NOISE_CACHE[id(index)] = cached
    return cached


# ---------------------------------------------------------------------------
# New adversarial control feature functions
# ---------------------------------------------------------------------------


def _random_permuted_cluster_label(
    row: dict[str, Any], index: lane.ClusterIndex
) -> tuple[float, ...]:
    """HIGHCLUSTER-ADV-001 — random-permutation cluster-label control."""

    cache = _permuted_cache(index)
    return (1.0 if cache.is_high_error_after_permutation(row) else 0.0,)


def _pure_local_density(
    row: dict[str, Any], index: lane.ClusterIndex
) -> tuple[float, ...]:
    """HIGHCLUSTER-ADV-002 — pure local-density smoother (no high-error gating)."""

    return (float(index.local_density(row)),)


def _near_null_jitter(
    row: dict[str, Any], index: lane.ClusterIndex
) -> tuple[float, ...]:
    """HIGHCLUSTER-ADV-003 — near-null deterministic jitter control."""

    cache = _noise_cache(index)
    return (cache.values.get(str(row["row_id"]), 0.0),)


# ---------------------------------------------------------------------------
# Variant composition
# ---------------------------------------------------------------------------


def _build_adversarial_variants() -> tuple[dict[str, Any], ...]:
    """Compose executed candidates + existing controls + new adversarial controls."""

    base = {
        item["candidate_id"]: dict(item)
        for item in lane.GENERATED_VARIANTS
        if item["fit_mode"] == "lstsq"
    }
    ordered: list[dict[str, Any]] = [
        base[item_id] for item_id in EXECUTED_CANDIDATE_IDS + EXISTING_CONTROL_IDS
    ]
    ordered.extend(
        (
            {
                "candidate_id": "HIGHCLUSTER-ADV-001",
                "name": "Random-permutation cluster-label control",
                "family": "random_permutation_cluster_label_control",
                "formula": (
                    "r_corr = beta * I[random-permuted exclusive cluster label "
                    "(seed=367) is any high-error class]"
                ),
                "feature_names": ("random_permuted_cluster_label",),
                "fit_mode": "lstsq",
                "complexity": 1,
                "role": "random_permutation_cluster_label_control",
                "feature_fn": _random_permuted_cluster_label,
                "random_seed": RANDOM_PERMUTATION_SEED,
            },
            {
                "candidate_id": "HIGHCLUSTER-ADV-002",
                "name": "Pure local-density smoother (no high-error gating)",
                "family": "pure_local_density_control",
                "formula": "r_corr = beta * local_density(row) without high-error gating",
                "feature_names": ("local_density",),
                "fit_mode": "lstsq",
                "complexity": 1,
                "role": "pure_local_density_control",
                "feature_fn": _pure_local_density,
            },
            {
                "candidate_id": "HIGHCLUSTER-ADV-003",
                "name": "Near-null deterministic jitter control",
                "family": "near_null_jitter_control",
                "formula": (
                    "r_corr = beta * Normal(0, "
                    f"{NEAR_NULL_NOISE_STD_MEV:g} MeV) jitter seeded with "
                    f"{NEAR_NULL_NOISE_SEED}"
                ),
                "feature_names": ("near_null_jitter",),
                "fit_mode": "lstsq",
                "complexity": 1,
                "role": "near_null_jitter_control",
                "feature_fn": _near_null_jitter,
                "random_seed": NEAR_NULL_NOISE_SEED,
                "noise_std_mev": NEAR_NULL_NOISE_STD_MEV,
            },
        )
    )
    return tuple(ordered)


def _candidate_variant_by_id(candidate_id: str) -> dict[str, Any]:
    for variant in _build_adversarial_variants():
        if variant["candidate_id"] == candidate_id:
            return variant
    raise KeyError(f"Unknown adversarial variant: {candidate_id}")


# ---------------------------------------------------------------------------
# Surface preparation and variant evaluation
# ---------------------------------------------------------------------------


def _prepare_surface() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    np.ndarray,
    dict[str, Any],
    float,
    lane.ClusterIndex,
]:
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
            PRIMARY_PERCENTILE,
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


# ---------------------------------------------------------------------------
# Candidate vs strongest control table
# ---------------------------------------------------------------------------


def _candidate_vs_strongest_control_table(
    items: list[dict[str, Any]],
    *,
    baseline_metrics: dict[str, dict[str, float | int | None]],
) -> list[dict[str, Any]]:
    candidates = [item for item in items if item["role"] == "executed_candidate"]
    controls = [item for item in items if item["role"].endswith("_control")]
    subset_keys = sorted(baseline_metrics.keys())
    table: list[dict[str, Any]] = []
    for candidate in candidates:
        per_subset: list[dict[str, Any]] = []
        wins = 0
        for subset_id in subset_keys:
            candidate_delta = candidate["delta_mae_by_subset_mev"].get(subset_id)
            usable = {
                control["candidate_id"]: control["delta_mae_by_subset_mev"].get(subset_id)
                for control in controls
                if control["delta_mae_by_subset_mev"].get(subset_id) is not None
            }
            if not usable or candidate_delta is None:
                strongest_id = None
                strongest_delta: float | None = None
                margin: float | None = None
                beats: bool | None = None
            else:
                strongest_id, strongest_delta = min(
                    usable.items(), key=lambda kv: (float(kv[1]), kv[0])
                )
                margin = float(strongest_delta) - float(candidate_delta)
                beats = bool(margin > 0.0)
                if beats:
                    wins += 1
            per_subset.append(
                {
                    "subset_id": subset_id,
                    "candidate_delta_mae_mev": candidate_delta,
                    "strongest_control_id": strongest_id,
                    "strongest_control_delta_mae_mev": strongest_delta,
                    "candidate_minus_strongest_control_mev": margin,
                    "candidate_beats_strongest_control": beats,
                }
            )
        primary_row = next(
            (row for row in per_subset if row["subset_id"] == "full_known"), None
        )
        primary_margin = (
            primary_row["candidate_minus_strongest_control_mev"]
            if primary_row is not None
            else None
        )
        primary_strongest = (
            primary_row["strongest_control_id"] if primary_row is not None else None
        )
        primary_survives = bool(
            primary_margin is not None
            and primary_margin >= PRIMARY_SURVIVAL_MARGIN_MEV
        )
        usable_subsets = sum(
            1 for row in per_subset if row["candidate_beats_strongest_control"] is not None
        )
        win_rate = wins / usable_subsets if usable_subsets > 0 else None
        table.append(
            {
                "candidate_id": candidate["candidate_id"],
                "name": candidate["name"],
                "primary_subset_id": "full_known",
                "primary_strongest_control_id": primary_strongest,
                "primary_candidate_minus_strongest_control_mev": primary_margin,
                "primary_survival_margin_mev": PRIMARY_SURVIVAL_MARGIN_MEV,
                "primary_survives_adversarial_controls": primary_survives,
                "subset_wins_count": wins,
                "subset_evaluated_count": usable_subsets,
                "subset_win_rate": win_rate,
                "per_subset_comparison": per_subset,
            }
        )
    return table


# ---------------------------------------------------------------------------
# High-error threshold perturbation diagnostic
# ---------------------------------------------------------------------------


def _threshold_perturbation_diagnostic(
    *,
    audit_rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
) -> dict[str, Any]:
    absolute_baseline = np.asarray(
        [abs(float(row["baseline_residual_mev"])) for row in audit_rows],
        dtype=float,
    )
    rows_by_threshold: list[dict[str, Any]] = []
    sign_flip_flag: dict[str, bool] = {cid: False for cid in EXECUTED_CANDIDATE_IDS}
    per_candidate_signs: dict[str, set[int]] = {cid: set() for cid in EXECUTED_CANDIDATE_IDS}
    for percentile in THRESHOLD_PERTURBATION_PERCENTILES:
        threshold = float(np.percentile(absolute_baseline, percentile, method="linear"))
        perturbed_index = lane.ClusterIndex(audit_rows, threshold)
        baseline_metrics = lane._baseline_metrics(  # noqa: SLF001
            audit_rows, index=perturbed_index
        )
        per_candidate: dict[str, Any] = {}
        for candidate_id in EXECUTED_CANDIDATE_IDS:
            variant = _candidate_variant_by_id(candidate_id)
            beta, fitted = lane._fit_variant(  # noqa: SLF001
                variant,
                training_rows=training_rows,
                training_residuals=training_residuals,
                index=perturbed_index,
            )
            residuals, _ = lane._candidate_residuals(  # noqa: SLF001
                audit_rows,
                variant=variant,
                beta=beta,
                index=perturbed_index,
            )
            candidate_metrics = lane._summarize_residuals(residuals)  # noqa: SLF001
            delta_mae = lane._delta_mae(  # noqa: SLF001
                candidate_metrics, baseline_metrics.get("full_known")
            )
            coefficient_name = variant["feature_names"][0]
            coefficient = float(fitted[coefficient_name])
            sign = int(np.sign(coefficient)) if coefficient != 0.0 else 0
            per_candidate_signs[candidate_id].add(sign)
            per_candidate[candidate_id] = {
                "fitted_coefficient": coefficient,
                "coefficient_name": coefficient_name,
                "full_known_delta_mae_mev": delta_mae,
            }
        rows_by_threshold.append(
            {
                "percentile": percentile,
                "threshold_mev": threshold,
                "high_error_row_count": int(
                    sum(1 for row in audit_rows if perturbed_index.is_high_error(row))
                ),
                "per_candidate": per_candidate,
            }
        )
    per_candidate_summary: dict[str, Any] = {}
    for candidate_id in EXECUTED_CANDIDATE_IDS:
        deltas = [
            float(item["per_candidate"][candidate_id]["full_known_delta_mae_mev"])
            for item in rows_by_threshold
            if item["per_candidate"][candidate_id]["full_known_delta_mae_mev"] is not None
        ]
        coefficients = [
            float(item["per_candidate"][candidate_id]["fitted_coefficient"])
            for item in rows_by_threshold
        ]
        non_zero_signs = {sign for sign in per_candidate_signs[candidate_id] if sign != 0}
        sign_flip_flag[candidate_id] = len(non_zero_signs) > 1
        per_candidate_summary[candidate_id] = {
            "delta_mae_min_mev": min(deltas) if deltas else None,
            "delta_mae_max_mev": max(deltas) if deltas else None,
            "delta_mae_range_mev": (max(deltas) - min(deltas)) if deltas else None,
            "delta_mae_at_primary_percentile_mev": next(
                (
                    float(item["per_candidate"][candidate_id]["full_known_delta_mae_mev"])
                    for item in rows_by_threshold
                    if item["percentile"] == PRIMARY_PERCENTILE
                    and item["per_candidate"][candidate_id]["full_known_delta_mae_mev"] is not None
                ),
                None,
            ),
            "coefficient_min": min(coefficients) if coefficients else None,
            "coefficient_max": max(coefficients) if coefficients else None,
            "coefficient_sign_flip": sign_flip_flag[candidate_id],
            "improves_at_every_percentile": bool(
                deltas and all(value < 0.0 for value in deltas)
            ),
        }
    return {
        "primary_percentile": PRIMARY_PERCENTILE,
        "evaluated_percentiles": list(THRESHOLD_PERTURBATION_PERCENTILES),
        "rows_by_threshold": rows_by_threshold,
        "per_candidate_summary": per_candidate_summary,
    }


# ---------------------------------------------------------------------------
# Leave-one-out coefficient stability diagnostic
# ---------------------------------------------------------------------------


def _loo_coefficient_stability(
    *,
    audit_rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
    baseline_metrics: dict[str, dict[str, float | int | None]],
    index: lane.ClusterIndex,
) -> dict[str, Any]:
    full_known_baseline = baseline_metrics.get("full_known", {}).get("mae_mev")
    per_candidate: dict[str, Any] = {}
    training_count = len(training_rows)
    for candidate_id in EXECUTED_CANDIDATE_IDS:
        variant = _candidate_variant_by_id(candidate_id)
        coefficient_name = variant["feature_names"][0]
        full_x = lane._feature_matrix(  # noqa: SLF001
            training_rows, variant=variant, index=index
        )
        coefficients: list[float] = []
        full_known_deltas: list[float] = []
        per_fold: list[dict[str, Any]] = []
        for held_out in range(training_count):
            mask = np.arange(training_count) != held_out
            train_subset_x = full_x[mask]
            train_subset_y = training_residuals[mask]
            beta, *_ = np.linalg.lstsq(train_subset_x, train_subset_y, rcond=None)
            coefficient = float(beta[0]) if beta.size > 0 else 0.0
            coefficients.append(coefficient)
            residuals, _ = lane._candidate_residuals(  # noqa: SLF001
                audit_rows,
                variant=variant,
                beta=beta,
                index=index,
            )
            full_known_metrics = lane._summarize_residuals(residuals)  # noqa: SLF001
            mae = full_known_metrics.get("mae_mev")
            delta: float | None = None
            if mae is not None and full_known_baseline is not None:
                delta = float(mae) - float(full_known_baseline)
                full_known_deltas.append(delta)
            held_out_row = training_rows[held_out]
            per_fold.append(
                {
                    "held_out_row_id": str(held_out_row["row_id"]),
                    "held_out_nuclide_id": str(held_out_row["nuclide_id"]),
                    "fitted_coefficient": coefficient,
                    "full_known_delta_mae_mev": delta,
                }
            )
        non_zero_signs = {
            int(np.sign(value)) for value in coefficients if value != 0.0
        }
        coefficient_array = np.asarray(coefficients, dtype=float)
        delta_array = np.asarray(full_known_deltas, dtype=float)
        coefficient_range = (
            float(coefficient_array.max() - coefficient_array.min())
            if coefficient_array.size > 0
            else None
        )
        loo_stable = bool(
            len(non_zero_signs) <= 1
            and coefficient_range is not None
            and coefficient_range <= LOO_COEFFICIENT_RANGE_LIMIT
        )
        per_candidate[candidate_id] = {
            "training_row_count": training_count,
            "coefficient_name": coefficient_name,
            "coefficient_min": float(coefficient_array.min()) if coefficient_array.size > 0 else None,
            "coefficient_max": float(coefficient_array.max()) if coefficient_array.size > 0 else None,
            "coefficient_mean": float(coefficient_array.mean()) if coefficient_array.size > 0 else None,
            "coefficient_std": float(coefficient_array.std(ddof=0)) if coefficient_array.size > 0 else None,
            "coefficient_range": coefficient_range,
            "coefficient_sign_flip": bool(len(non_zero_signs) > 1),
            "full_known_delta_mae_min_mev": float(delta_array.min()) if delta_array.size > 0 else None,
            "full_known_delta_mae_max_mev": float(delta_array.max()) if delta_array.size > 0 else None,
            "full_known_delta_mae_range_mev": (
                float(delta_array.max() - delta_array.min())
                if delta_array.size > 0
                else None
            ),
            "loo_stable": loo_stable,
            "stability_thresholds": {
                "coefficient_range_limit": LOO_COEFFICIENT_RANGE_LIMIT,
                "sign_flip_allowed": False,
            },
            "per_fold": per_fold,
        }
    return {
        "method": "leave_one_out_over_training_slice",
        "training_row_count": training_count,
        "per_candidate": per_candidate,
    }


# ---------------------------------------------------------------------------
# Per-candidate adversarial verdict and lane verdict
# ---------------------------------------------------------------------------


def _candidate_adversarial_verdict(
    *,
    candidate_item: dict[str, Any],
    comparison_row: dict[str, Any],
    threshold_summary: dict[str, Any] | None,
    loo_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    non_high_error = candidate_item["non_high_error_delta_mae_mev"]
    high_error = candidate_item["high_error_delta_mae_mev"]
    high_error_only_overfit = bool(
        high_error is not None
        and high_error < 0.0
        and non_high_error is not None
        and non_high_error > NON_HIGH_ERROR_REGRESSION_THRESHOLD_MEV
    )
    survives_primary = bool(comparison_row["primary_survives_adversarial_controls"])
    win_rate = comparison_row.get("subset_win_rate")
    dominates_subsets = bool(win_rate is not None and win_rate > 0.5)
    threshold_stable = bool(
        threshold_summary is not None
        and threshold_summary.get("improves_at_every_percentile") is True
        and not threshold_summary.get("coefficient_sign_flip", False)
    )
    loo_stable = bool(loo_summary is not None and loo_summary.get("loo_stable") is True)
    if high_error_only_overfit:
        verdict = "OVERFITTED"
    elif survives_primary and dominates_subsets and threshold_stable and loo_stable:
        verdict = "PARTIALLY_VALID"
    elif survives_primary or dominates_subsets:
        verdict = "INCONCLUSIVE"
    else:
        verdict = "FALSIFIED"
    return {
        "verdict": verdict,
        "survives_primary_subset": survives_primary,
        "subset_win_rate": win_rate,
        "dominates_subsets": dominates_subsets,
        "threshold_stable": threshold_stable,
        "loo_stable": loo_stable,
        "high_error_only_overfit": high_error_only_overfit,
        "non_high_error_regression_threshold_mev": NON_HIGH_ERROR_REGRESSION_THRESHOLD_MEV,
    }


def _lane_verdict(per_candidate_verdicts: dict[str, dict[str, Any]]) -> str:
    if not per_candidate_verdicts:
        return "INCONCLUSIVE"
    verdicts = [item["verdict"] for item in per_candidate_verdicts.values()]
    if any(verdict == "PARTIALLY_VALID" for verdict in verdicts):
        return "PARTIALLY_VALID"
    if any(verdict == "OVERFITTED" for verdict in verdicts) and not any(
        verdict in {"INCONCLUSIVE", "PARTIALLY_VALID"} for verdict in verdicts
    ):
        return "OVERFITTED"
    if any(verdict == "INCONCLUSIVE" for verdict in verdicts):
        return "INCONCLUSIVE"
    return "FALSIFIED"


def _map_lane_verdict_to_agent_run_verdict(lane_verdict: str) -> str:
    mapping = {
        "PARTIALLY_VALID": "SANDBOX_PASS",
        "INCONCLUSIVE": "INCONCLUSIVE",
        "OVERFITTED": "OVERFITTED",
        "FALSIFIED": "FALSIFIED",
    }
    return mapping.get(lane_verdict, "INCONCLUSIVE")


# ---------------------------------------------------------------------------
# Metrics assembly
# ---------------------------------------------------------------------------


def build_metrics() -> dict[str, Any]:
    audit_rows, training_rows, training_residuals, surface, high_error_threshold, index = (
        _prepare_surface()
    )
    variants = _build_adversarial_variants()
    items, baseline_metrics = _evaluate_all_variants(
        variants,
        audit_rows=audit_rows,
        training_rows=training_rows,
        training_residuals=training_residuals,
        index=index,
    )
    candidate_items = [item for item in items if item["role"] == "executed_candidate"]
    comparison_table = _candidate_vs_strongest_control_table(
        items, baseline_metrics=baseline_metrics
    )
    threshold_diagnostic = _threshold_perturbation_diagnostic(
        audit_rows=audit_rows,
        training_rows=training_rows,
        training_residuals=training_residuals,
    )
    loo_diagnostic = _loo_coefficient_stability(
        audit_rows=audit_rows,
        training_rows=training_rows,
        training_residuals=training_residuals,
        baseline_metrics=baseline_metrics,
        index=index,
    )
    chain_transfer = lane._chain_transfer_summary(  # noqa: SLF001
        audit_rows, candidate_items, index=index
    )
    per_candidate_verdicts: dict[str, dict[str, Any]] = {}
    comparison_by_id = {row["candidate_id"]: row for row in comparison_table}
    threshold_summary = threshold_diagnostic["per_candidate_summary"]
    loo_per_candidate = loo_diagnostic["per_candidate"]
    for candidate in candidate_items:
        candidate_id = candidate["candidate_id"]
        per_candidate_verdicts[candidate_id] = _candidate_adversarial_verdict(
            candidate_item=candidate,
            comparison_row=comparison_by_id[candidate_id],
            threshold_summary=threshold_summary.get(candidate_id),
            loo_summary=loo_per_candidate.get(candidate_id),
        )
    lane_verdict = _lane_verdict(per_candidate_verdicts)
    best_primary = min(
        candidate_items,
        key=lambda item: (
            float("inf")
            if item["primary_delta_mae_mev"] is None
            else float(item["primary_delta_mae_mev"]),
            item["candidate_id"],
        ),
    )
    coefficients = full_known.load_frozen_baseline_coefficients()
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "predecessor_task_id": PREDECESSOR_TASK_ID,
        "predecessor_agent_run_id": PREDECESSOR_AGENT_RUN_ID,
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
            "new_adversarial_control_count": len(NEW_ADVERSARIAL_CONTROL_IDS),
            "primary_survival_margin_mev": PRIMARY_SURVIVAL_MARGIN_MEV,
            "non_high_error_regression_threshold_mev": NON_HIGH_ERROR_REGRESSION_THRESHOLD_MEV,
            "loo_coefficient_range_limit": LOO_COEFFICIENT_RANGE_LIMIT,
            "lane_verdict": lane_verdict,
            "best_primary_delta_candidate_id": best_primary["candidate_id"],
            "best_primary_delta_mae_mev": best_primary["primary_delta_mae_mev"],
            "high_error_percentile": PRIMARY_PERCENTILE,
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
        },
        "baseline_metrics_by_subset": baseline_metrics,
        "variants": items,
        "candidate_vs_strongest_control": comparison_table,
        "threshold_perturbation": threshold_diagnostic,
        "leave_one_out_stability": loo_diagnostic,
        "isotope_chain_transfer": chain_transfer,
        "per_candidate_adversarial_verdict": per_candidate_verdicts,
        "tasks_referenced": {
            "predecessor_lane_task": PREDECESSOR_TASK_ID,
            "predecessor_lane_agent_run": PREDECESSOR_AGENT_RUN_ID,
            "predecessor_lane_review": (
                "docs/reviews/nuclear-high-error-cluster-hypothesis-lane.md"
            ),
            "predecessor_local_curvature_adversarial_review": (
                "docs/reviews/nuclear-local-curvature-adversarial-controls.md"
            ),
        },
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any high-error-cluster follow-up. No "
                "predictive lane, PRED-* entry, RESULT-* artifact, claim, or "
                "knowledge update is authorized by this run."
            ),
        },
        "limitations": [
            "High-error membership and cluster labels still come from committed "
            "retrospective residuals; this lane sharpens controls but remains a "
            "diagnostic rather than a blind prediction.",
            "Coefficients are fit on the 11-row NMD-0002 training slice, so the "
            "leave-one-out stability check is itself a small-sample diagnostic.",
            "The three new adversarial controls do not exhaust the space of "
            "possible attacks (e.g. stronger label shuffles weighted by chain "
            "structure, richer non-linear smoothers, or feature-set ablations).",
            "Threshold perturbation rebuilds the ClusterIndex at each percentile, "
            "so cluster-membership composition shifts between thresholds; the "
            "diagnostic measures coefficient and delta stability rather than a "
            "fixed cluster definition.",
            "No live source fetch, reveal scoring, registry write, claim update, "
            "or canonical result write is authorized.",
        ],
    }


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _format_delta(value: float | None, *, decimals: int = 6) -> str:
    if value is None:
        return "n/a"
    if value == 0.0:
        return f"+{0.0:.{decimals}f}"
    return f"{'+' if value > 0 else '-'}{abs(value):.{decimals}f}"


def _per_variant_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Candidate / control | Role | Full-known | Holdout | High-error | Non-high-error | Neutron-rich | Magic | Light-A | Chain rate |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    chain = metrics["isotope_chain_transfer"]["by_candidate"]
    for item in metrics["variants"]:
        chain_rate = (
            chain[item["candidate_id"]]["improvement_rate"]
            if item["candidate_id"] in chain
            else None
        )
        lines.append(
            "| `{cid}` | {role} | {fk} | {ho} | {he} | {nhe} | {nr} | {mg} | {la} | {chain} |".format(
                cid=item["candidate_id"],
                role=item["role"],
                fk=_format_delta(item["primary_delta_mae_mev"]),
                ho=_format_delta(item["holdout_delta_mae_mev"]),
                he=_format_delta(item["high_error_delta_mae_mev"]),
                nhe=_format_delta(item["non_high_error_delta_mae_mev"]),
                nr=_format_delta(item["neutron_rich_delta_mae_mev"]),
                mg=_format_delta(item["magic_region_delta_mae_mev"]),
                la=_format_delta(item["light_a_warning_delta_mae_mev"]),
                chain="n/a" if chain_rate is None else f"{chain_rate:.3f}",
            )
        )
    return lines


def _adversarial_table(metrics: dict[str, Any]) -> list[str]:
    summary = metrics["summary"]
    lines = [
        "| Candidate | Strongest control on full_known | Candidate Δ MAE | Control Δ MAE | Margin (control − candidate) | Survives ≥ {margin:.2f} MeV? |".format(
            margin=summary["primary_survival_margin_mev"]
        ),
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for comparison in metrics["candidate_vs_strongest_control"]:
        full_known_row = next(
            (row for row in comparison["per_subset_comparison"] if row["subset_id"] == "full_known"),
            None,
        )
        lines.append(
            "| `{cid}` | `{strongest}` | {cdelta} | {sdelta} | {margin} | {surv} |".format(
                cid=comparison["candidate_id"],
                strongest=comparison["primary_strongest_control_id"] or "n/a",
                cdelta=_format_delta(
                    full_known_row["candidate_delta_mae_mev"] if full_known_row else None
                ),
                sdelta=_format_delta(
                    full_known_row["strongest_control_delta_mae_mev"]
                    if full_known_row
                    else None
                ),
                margin=_format_delta(
                    comparison["primary_candidate_minus_strongest_control_mev"]
                ),
                surv="yes"
                if comparison["primary_survives_adversarial_controls"]
                else "**no**",
            )
        )
    return lines


def _win_rate_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Candidate | Subsets evaluated | Subsets won vs strongest control | Win rate |",
        "| --- | ---: | ---: | ---: |",
    ]
    for comparison in metrics["candidate_vs_strongest_control"]:
        rate = comparison["subset_win_rate"]
        lines.append(
            "| `{cid}` | {total} | {won} | {rate} |".format(
                cid=comparison["candidate_id"],
                total=comparison["subset_evaluated_count"],
                won=comparison["subset_wins_count"],
                rate="n/a" if rate is None else f"{rate:.3f}",
            )
        )
    return lines


def _threshold_table(metrics: dict[str, Any]) -> list[str]:
    diagnostic = metrics["threshold_perturbation"]
    lines: list[str] = []
    header = "| Percentile | Threshold (MeV) | High-error rows | " + " | ".join(
        f"`{cid}` Δ MAE (coef)" for cid in EXECUTED_CANDIDATE_IDS
    ) + " |"
    lines.append(header)
    lines.append(
        "| ---: | ---: | ---: | " + " | ".join("---: " for _ in EXECUTED_CANDIDATE_IDS) + " |"
    )
    for row in diagnostic["rows_by_threshold"]:
        cells = []
        for cid in EXECUTED_CANDIDATE_IDS:
            value = row["per_candidate"][cid]
            delta = _format_delta(value["full_known_delta_mae_mev"])
            coef = value["fitted_coefficient"]
            cells.append(f"{delta} ({coef:+.4f})")
        lines.append(
            "| {pct:.1f} | {thr:.6f} | {he} | {cells} |".format(
                pct=float(row["percentile"]),
                thr=float(row["threshold_mev"]),
                he=int(row["high_error_row_count"]),
                cells=" | ".join(cells),
            )
        )
    return lines


def _threshold_summary_table(metrics: dict[str, Any]) -> list[str]:
    summary = metrics["threshold_perturbation"]["per_candidate_summary"]
    lines = [
        "| Candidate | Δ MAE range (MeV) | Coefficient range | Sign flip? | Improves at every percentile? |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for cid in EXECUTED_CANDIDATE_IDS:
        item = summary[cid]
        lines.append(
            "| `{cid}` | {rng} | [{cmin:+.4f}, {cmax:+.4f}] | {flip} | {imp} |".format(
                cid=cid,
                rng="n/a" if item["delta_mae_range_mev"] is None else f"{item['delta_mae_range_mev']:.6f}",
                cmin=float(item["coefficient_min"] or 0.0),
                cmax=float(item["coefficient_max"] or 0.0),
                flip="yes" if item["coefficient_sign_flip"] else "no",
                imp="yes" if item["improves_at_every_percentile"] else "**no**",
            )
        )
    return lines


def _loo_table(metrics: dict[str, Any]) -> list[str]:
    loo = metrics["leave_one_out_stability"]["per_candidate"]
    lines = [
        "| Candidate | Coefficient mean ± std | Coefficient range | Sign flip? | Δ MAE range (MeV) | LOO stable? |",
        "| --- | ---: | ---: | --- | ---: | --- |",
    ]
    for cid in EXECUTED_CANDIDATE_IDS:
        item = loo[cid]
        lines.append(
            "| `{cid}` | {mean:+.4f} ± {std:.4f} | [{cmin:+.4f}, {cmax:+.4f}] | {flip} | {drange} | {stable} |".format(
                cid=cid,
                mean=float(item["coefficient_mean"] or 0.0),
                std=float(item["coefficient_std"] or 0.0),
                cmin=float(item["coefficient_min"] or 0.0),
                cmax=float(item["coefficient_max"] or 0.0),
                flip="yes" if item["coefficient_sign_flip"] else "no",
                drange="n/a"
                if item["full_known_delta_mae_range_mev"] is None
                else f"{item['full_known_delta_mae_range_mev']:.6f}",
                stable="yes" if item["loo_stable"] else "**no**",
            )
        )
    return lines


def _candidate_verdict_table(metrics: dict[str, Any]) -> list[str]:
    verdicts = metrics["per_candidate_adversarial_verdict"]
    lines = [
        "| Candidate | Survives primary? | Subset win rate | Threshold stable? | LOO stable? | High-error-only overfit? | Verdict |",
        "| --- | --- | ---: | --- | --- | --- | --- |",
    ]
    for cid in EXECUTED_CANDIDATE_IDS:
        item = verdicts[cid]
        rate = item["subset_win_rate"]
        lines.append(
            "| `{cid}` | {sp} | {rate} | {ts} | {ls} | {ho} | `{verdict}` |".format(
                cid=cid,
                sp="yes" if item["survives_primary_subset"] else "**no**",
                rate="n/a" if rate is None else f"{rate:.3f}",
                ts="yes" if item["threshold_stable"] else "**no**",
                ls="yes" if item["loo_stable"] else "**no**",
                ho="**yes**" if item["high_error_only_overfit"] else "no",
                verdict=item["verdict"],
            )
        )
    return lines


def render_report(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    lines: list[str] = []
    lines.append("# Nuclear high-error cluster adversarial stability audit")
    lines.append("")
    lines.append(f"**Task:** `{metrics['task_id']}`  ")
    lines.append(f"**Agent run:** `{metrics['agent_run_id']}`  ")
    lines.append(
        f"**Predecessor:** `{metrics['predecessor_task_id']}` / "
        f"`{metrics['predecessor_agent_run_id']}`  "
    )
    lines.append(f"**Lane verdict:** `{summary['lane_verdict']}`  ")
    lines.append(
        f"**Primary survival margin (MeV):** {summary['primary_survival_margin_mev']:.2f}  "
    )
    lines.append(
        f"**Non-high-error regression threshold (MeV):** "
        f"{summary['non_high_error_regression_threshold_mev']:.2f}  "
    )
    lines.append(
        f"**LOO coefficient range limit:** {summary['loo_coefficient_range_limit']:.2f}"
    )
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append(
        "This run only uses committed repository datasets and the predecessor "
        "high-error cluster lane helpers. It writes no canonical RESULT-* "
        "artifact, no PRED-* entry, no claim, and no knowledge file. The lane "
        "verdict feeds maintainer review; it does not authorize claim promotion "
        "or future-measurement comparison."
    )
    lines.append("")
    lines.append("## Variants Evaluated")
    lines.append("")
    lines.append("| Candidate / control | Role | Family |")
    lines.append("| --- | --- | --- |")
    for item in metrics["variants"]:
        marker = " **(new)**" if item["candidate_id"] in NEW_ADVERSARIAL_CONTROL_IDS else ""
        lines.append(
            f"| `{item['candidate_id']}`{marker} | {item['role']} | {item['family']} |"
        )
    lines.append("")
    lines.append("## Per-Variant Subset Deltas (MeV)")
    lines.append("")
    lines.extend(_per_variant_table(metrics))
    lines.append("")
    lines.append("Negative deltas indicate lower MAE than the frozen semi-empirical baseline.")
    lines.append("")
    lines.append("## Candidate vs Strongest Control (Primary Subset)")
    lines.append("")
    lines.extend(_adversarial_table(metrics))
    lines.append("")
    lines.append("## Per-Candidate Subset Win-Rate vs Strongest Control")
    lines.append("")
    lines.extend(_win_rate_table(metrics))
    lines.append("")
    lines.append("## High-Error Threshold Perturbation")
    lines.append("")
    lines.extend(_threshold_table(metrics))
    lines.append("")
    lines.extend(_threshold_summary_table(metrics))
    lines.append("")
    lines.append("## Leave-One-Out Coefficient Stability")
    lines.append("")
    lines.extend(_loo_table(metrics))
    lines.append("")
    lines.append("## Per-Candidate Adversarial Verdict")
    lines.append("")
    lines.extend(_candidate_verdict_table(metrics))
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    if summary["lane_verdict"] == "PARTIALLY_VALID":
        lines.append(
            "- At least one candidate beats the strongest control on the primary "
            f"subset by at least `{summary['primary_survival_margin_mev']:.2f}` MeV, "
            "dominates the subset win-rate, and shows stable coefficients under "
            "both threshold perturbation and leave-one-out re-fits."
        )
        lines.append(
            "- The signal is preserved as sandbox evidence that survived "
            "stronger adversarial controls. It does not authorize a claim, a "
            "PRED-* entry, or a reveal."
        )
    elif summary["lane_verdict"] == "INCONCLUSIVE":
        lines.append(
            "- At least one candidate clears one of the adversarial gates but not "
            "all of them; the cluster signal is neither cleanly preserved nor "
            "cleanly falsified."
        )
        lines.append(
            "- Recommendation: keep the lane as sandbox diagnostic evidence and "
            "do not authorize predictive use. Maintainer review should weigh the "
            "per-candidate verdict table before any follow-up task."
        )
    elif summary["lane_verdict"] == "OVERFITTED":
        lines.append(
            "- At least one candidate improves only high-error rows while "
            f"materially regressing the rest of the surface by more than "
            f"`{summary['non_high_error_regression_threshold_mev']:.2f}` MeV; "
            "no candidate offsets that with a clean PARTIALLY_VALID verdict."
        )
        lines.append(
            "- Recommendation: preserve as overfit / cluster-targeting "
            "diagnostic. Do not promote, do not register, do not score against "
            "future measurements."
        )
    else:
        lines.append(
            "- No candidate beats the strongest control on the primary subset by "
            f"the required margin (`{summary['primary_survival_margin_mev']:.2f}` "
            "MeV), and none dominates the subset win-rate."
        )
        lines.append(
            "- Recommendation: preserve the lane as a falsified high-error cluster "
            "diagnostic. The original AGENT-RUN-0030 metrics remain visible as "
            "negative scientific memory; no claim promotion or PRED-* entry is "
            "authorized."
        )
    lines.append("")
    lines.append("## Limitations")
    lines.append("")
    lines.extend(f"- {item}" for item in metrics["limitations"])
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    lines.append(f"`{summary['lane_verdict']}`")
    lines.append("")
    return "\n".join(lines)


def render_review(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    lines: list[str] = []
    lines.append("# Nuclear high-error cluster adversarial stability review")
    lines.append("")
    lines.append(f"**Task:** `{metrics['task_id']}`  ")
    lines.append(f"**Agent run:** `{metrics['agent_run_id']}`  ")
    lines.append(
        f"**Predecessor:** `{metrics['predecessor_task_id']}` / "
        f"`{metrics['predecessor_agent_run_id']}` "
        "(high-error cluster hypothesis lane)  "
    )
    lines.append(f"**Lane verdict:** `{summary['lane_verdict']}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(
        "This review records the outcome of attacking the AGENT-RUN-0030 "
        "high-error cluster signal with three stronger adversarial controls and "
        "two stability diagnostics. It does not promote any claim, does not "
        "register a prediction-registry entry, does not rewrite the predecessor "
        "lane metrics, and does not authorize a reveal."
    )
    lines.append("")
    lines.append("## New Adversarial Controls")
    lines.append("")
    lines.append(
        "- **HIGHCLUSTER-ADV-001** — random-permutation cluster-label control. "
        "Uses a deterministic random permutation (seed 367) of the exclusive "
        "cluster labels across rows. Stronger than the predecessor cyclic-shift "
        "control because a random permutation cannot preserve any residual "
        "locality structure that a cyclic shift can keep accidentally."
    )
    lines.append(
        "- **HIGHCLUSTER-ADV-002** — pure local-density smoother. Uses the raw "
        "per-row local-density count without high-error gating. Competes "
        "directly with HIGHCLUSTER-003's density-gated feature; if HIGHCLUSTER-003 "
        "is dominated by smooth density structure, this control captures it "
        "without the cluster membership label."
    )
    lines.append(
        "- **HIGHCLUSTER-ADV-003** — near-null deterministic jitter. Uses a "
        f"per-row Normal(0, {NEAR_NULL_NOISE_STD_MEV:g} MeV) seeded with "
        f"{NEAR_NULL_NOISE_SEED}. Acts as the null floor: a candidate that does "
        "not beat this control by orders of magnitude is consistent with noise."
    )
    lines.append("")
    lines.append("## Stability Diagnostics")
    lines.append("")
    lines.append(
        "- **High-error threshold perturbation.** Re-fits each candidate at "
        "baseline-residual percentiles "
        f"{', '.join(f'{p:.0f}' for p in THRESHOLD_PERTURBATION_PERCENTILES)} and "
        "reports the full-known Δ MAE and fitted coefficient at each "
        "threshold. A genuine cluster signal should improve the surface at "
        "every nearby threshold and should not flip the coefficient sign."
    )
    lines.append(
        "- **Leave-one-out coefficient stability.** Re-fits each candidate on "
        f"every 10-of-{metrics['datasets']['training_row_count']} subset of the "
        "NMD-0002 training slice and reports the coefficient spread, sign-flip "
        "count, and full-known Δ MAE range. A LOO-stable candidate has no sign "
        f"flips and a coefficient range under "
        f"`{summary['loo_coefficient_range_limit']:.2f}`."
    )
    lines.append("")
    lines.append("## Headline Result")
    lines.append("")
    lines.append(f"- **Lane verdict:** `{summary['lane_verdict']}`.")
    lines.append(
        f"- **Best primary candidate:** `{summary['best_primary_delta_candidate_id']}` "
        f"with Δ MAE {_format_delta(summary['best_primary_delta_mae_mev'])} MeV."
    )
    lines.append(
        f"- **Primary survival margin:** "
        f"{summary['primary_survival_margin_mev']:.2f} MeV on the `full_known` "
        "subset."
    )
    lines.append("")
    lines.append("## Per-Candidate Verdict")
    lines.append("")
    lines.extend(_candidate_verdict_table(metrics))
    lines.append("")
    lines.append("## Candidate vs Strongest Control (Primary Subset)")
    lines.append("")
    lines.extend(_adversarial_table(metrics))
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    if summary["lane_verdict"] == "PARTIALLY_VALID":
        lines.append(
            "At least one candidate beats the strongest control on the primary "
            "subset by the required margin, dominates the subset win-rate, and "
            "is stable under both threshold perturbation and leave-one-out. The "
            "signal is preserved as sandbox evidence that survived adversarial "
            "controls. A future predictive implementation task remains gated by "
            "maintainer review and the no-leakage protocol; this review does "
            "not by itself unblock it."
        )
    elif summary["lane_verdict"] == "INCONCLUSIVE":
        lines.append(
            "The lane is mixed: at least one candidate clears one adversarial "
            "gate but not all of them. The signal is preserved as sandbox "
            "diagnostic evidence and does not authorize a predictive lane. "
            "Additional controls or a richer training slice may be needed before "
            "the verdict is revisited."
        )
    elif summary["lane_verdict"] == "OVERFITTED":
        lines.append(
            "At least one candidate improves only the high-error rows while "
            "materially regressing the rest of the surface, and no candidate "
            "offsets that with a clean PARTIALLY_VALID outcome. The lane is "
            "preserved as overfit / cluster-targeting diagnostic evidence. No "
            "predictive use, PRED-* entry, claim, or canonical result is "
            "authorized."
        )
    else:
        lines.append(
            "No candidate beats the strongest control on the primary subset by "
            "the required margin and no candidate dominates the subset "
            "win-rate. The lane is preserved as falsified high-error cluster "
            "diagnostic evidence. The original AGENT-RUN-0030 numbers remain "
            "visible as negative scientific memory; this review does not relax "
            "any existing protocol."
        )
    lines.append("")
    lines.append("## Limitations")
    lines.append("")
    lines.extend(f"- {item}" for item in metrics["limitations"])
    lines.append("")
    lines.append("## What This Review Did Not Do")
    lines.append("")
    lines.extend(
        f"- {item}"
        for item in (
            "It did not fetch live data, run reveal scoring, register a "
            "prediction-registry entry, edit a PRED-*.yaml, or promote a claim.",
            "It did not rewrite the predecessor AGENT-RUN-0030 metrics or "
            "verdict.",
            "It did not modify canonical RESULT-* artifacts.",
        )
    )
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    lines.append(f"`{summary['lane_verdict']}`")
    lines.append("")
    return "\n".join(lines)


def render_preflight(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Preflight",
            "",
            f"**Task:** `{metrics['task_id']}`",
            f"**Agent run:** `{metrics['agent_run_id']}`",
            "",
            "| Check | Status | Notes |",
            "| --- | --- | --- |",
            "| task_scope | PASS | TASK-0367 requests an adversarial-stability audit against AGENT-RUN-0030; this run produces only sandbox metrics. |",
            "| data_boundary | PASS | Only committed repository datasets and the predecessor lane helpers are used; no live external fetch. |",
            "| control_boundary | PASS | Three new adversarial controls (random-permutation cluster label, pure local-density smoother, near-null deterministic jitter) are evaluated alongside the original three controls. |",
            "| stability_boundary | PASS | High-error threshold perturbation (p65 / p70 / p75 / p80) and leave-one-out coefficient stability over the 11-row training slice are reported per executed candidate. |",
            "| promotion_boundary | PASS | No prediction registry, canonical result, claim, or knowledge file is written. |",
            "",
        ]
    )


def render_limitations(metrics: dict[str, Any]) -> str:
    lines = ["# Limitations", ""]
    lines.append(f"Task: `{metrics['task_id']}`  ")
    lines.append(f"Agent run: `{metrics['agent_run_id']}`")
    lines.append("")
    lines.extend(f"- {item}" for item in metrics["limitations"])
    lines.append("")
    return "\n".join(lines)


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
            "- Re-evaluated HIGHCLUSTER-001/002/003 with three new adversarial "
            "controls (random-permutation cluster label, pure local-density "
            "smoother, near-null deterministic jitter) on top of the three "
            "original controls.",
            "- Added a high-error threshold perturbation diagnostic at percentiles "
            f"{', '.join(f'{p:.0f}' for p in THRESHOLD_PERTURBATION_PERCENTILES)} and a "
            f"leave-one-out coefficient-stability diagnostic over the "
            f"{metrics['datasets']['training_row_count']}-row NMD-0002 training "
            "slice.",
            f"- Primary survival margin: {summary['primary_survival_margin_mev']:.2f} "
            "MeV on the `full_known` subset; high-error-only overfit guard at "
            f"{summary['non_high_error_regression_threshold_mev']:.2f} MeV on the "
            "non-high-error subset.",
            f"- Best primary candidate: `{summary['best_primary_delta_candidate_id']}` "
            f"with Δ MAE {_format_delta(summary['best_primary_delta_mae_mev'])} MeV.",
            "",
            "Sandbox-only retrospective evidence. No canonical result, claim, "
            "knowledge entry, or PRED-* entry was changed.",
            "",
        ]
    )


def render_agent_run_yaml(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    payload = {
        "id": metrics["agent_run_id"],
        "campaign_profile_id": metrics["campaign_profile_id"],
        "task_id": metrics["task_id"],
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {"contributor_id": "roman", "agent_id": "claude"},
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
                    "notes": "TASK-0367 requests an adversarial-stability audit of the AGENT-RUN-0030 high-error cluster signal; this run produces only sandbox metrics.",
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed repository datasets and the predecessor lane helpers are used; no live external fetch.",
                },
                {
                    "name": "control_boundary",
                    "status": "PASS",
                    "notes": "Three new adversarial controls are evaluated alongside the three original controls.",
                },
                {
                    "name": "stability_boundary",
                    "status": "PASS",
                    "notes": "High-error threshold perturbation and leave-one-out coefficient stability are reported per executed candidate.",
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No prediction registry, canonical result, claim, or knowledge file is written.",
                },
            ],
        },
        "limitations": metrics["limitations"],
        "verdict": _map_lane_verdict_to_agent_run_verdict(summary["lane_verdict"]),
        "promotion_boundary": metrics["promotion_boundary"],
    }
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=False)


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
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
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
