"""TASK-0397 nuclear local-curvature negative-control expansion.

This deterministic runner extends the TASK-0351 adversarial-control lane for
the TASK-0339 local-curvature sandbox signal. It evaluates the same
local-curvature candidates with identical subset metrics, adds a broader
negative-control panel, and records whether any control explains the apparent
signal.

The output is sandbox-only retrospective evidence. It does not fetch live
data, score reveal predictions, write prediction-registry entries, write
canonical RESULT-* artifacts, update claims, or promote knowledge.
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

import scripts.run_nuclear_local_curvature_adversarial_controls as prior_controls  # noqa: E402
import scripts.run_nuclear_local_curvature_lane as lane  # noqa: E402
import scripts.run_nuclear_shell_axis_full_known_audit as full_known  # noqa: E402


AGENT_RUN_ID = "AGENT-RUN-0041"
TASK_ID = "TASK-0397"
PRIMARY_SURVIVAL_MARGIN_MEV = prior_controls.PRIMARY_SURVIVAL_MARGIN_MEV
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
    / "nuclear-local-curvature-negative-control-expansion.md"
)

MAGIC_NUMBERS = (2, 8, 20, 28, 50, 82, 126)


def _format_delta(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):+.6f}"


def _nearest_magic_distance(value: int) -> int:
    return min(abs(value - magic) for magic in MAGIC_NUMBERS)


def _mass_number_only_control(
    row: dict[str, Any],
    _index: lane.NeighborIndex,
) -> tuple[float, ...]:
    scaled_a = (float(row["A"]) - 100.0) / 100.0
    return (scaled_a, scaled_a * scaled_a)


def _magic_distance_only_control(
    row: dict[str, Any],
    _index: lane.NeighborIndex,
) -> tuple[float, ...]:
    z_distance = float(_nearest_magic_distance(int(row["Z"])))
    n_distance = float(_nearest_magic_distance(int(row["N"])))
    min_distance = min(z_distance, n_distance)
    return (
        np.exp(-(z_distance * z_distance) / 32.0),
        np.exp(-(n_distance * n_distance) / 32.0),
        np.exp(-(min_distance * min_distance) / 32.0),
    )


def _near_null_neighborhood_control(
    row: dict[str, Any],
    index: lane.NeighborIndex,
) -> tuple[float, ...]:
    # Touch the neighborhood surface but force a null correction after fitting.
    _ = index.smooth_a_neighbors(row)
    return (0.0,)


def _build_negative_control_variants() -> tuple[dict[str, Any], ...]:
    base = {
        item["candidate_id"]: dict(item)
        for item in lane.GENERATED_VARIANTS
        if item["fit_mode"] == "lstsq"
    }
    variants: list[dict[str, Any]] = [
        base["LOCAL-CURVATURE-001"],
        base["LOCAL-CURVATURE-002"],
        base["LOCAL-CURVATURE-003"],
    ]
    variants.extend(
        (
            {
                "candidate_id": "LOCAL-NEGCTRL-001",
                "name": "Cyclic same-Z chain-shuffled residual control",
                "family": "chain_shuffled_control",
                "formula": "r_corr = beta * cyclically shifted same-Z residual",
                "feature_names": ("chain_shuffled_isotope_residual",),
                "fit_mode": "lstsq",
                "complexity": 1,
                "role": "chain_shuffled_control",
                "control_category": "chain_shuffled",
                "feature_fn": lane._chain_shuffled_isotope_mean,  # noqa: SLF001
            },
            {
                "candidate_id": "LOCAL-NEGCTRL-002",
                "name": "Permuted-Z nearest-neighbor residual control",
                "family": "chain_label_permutation_control",
                "formula": "r_corr = beta * mean(nearest residuals from permuted Z chain)",
                "feature_names": ("label_permuted_isotope_residual",),
                "fit_mode": "lstsq",
                "complexity": 1,
                "role": "chain_label_permutation_control",
                "control_category": "chain_shuffled",
                "feature_fn": prior_controls._label_shuffled_isotope_mean,  # noqa: SLF001
            },
            {
                "candidate_id": "LOCAL-NEGCTRL-003",
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
                "candidate_id": "LOCAL-NEGCTRL-004",
                "name": "Magic-distance-only shell-proximity control",
                "family": "magic_distance_only_control",
                "formula": "r_corr = beta_z*exp(-dz^2/32) + beta_n*exp(-dn^2/32) + beta_min*exp(-dmin^2/32)",
                "feature_names": (
                    "magic_distance_z_kernel",
                    "magic_distance_n_kernel",
                    "magic_distance_min_kernel",
                ),
                "fit_mode": "lstsq",
                "complexity": 3,
                "role": "magic_distance_only_control",
                "control_category": "magic_distance_only",
                "feature_fn": _magic_distance_only_control,
            },
            {
                "candidate_id": "LOCAL-NEGCTRL-005",
                "name": "Smooth mass-window residual control",
                "family": "smooth_window_control",
                "formula": "r_corr = beta * mean(nearest A-window residuals)",
                "feature_names": ("smooth_a_window_residual",),
                "fit_mode": "lstsq",
                "complexity": 1,
                "role": "smooth_window_control",
                "control_category": "smooth_window",
                "feature_fn": lane._smooth_a_window_mean,  # noqa: SLF001
            },
            {
                "candidate_id": "LOCAL-NEGCTRL-006",
                "name": "Smooth local linear-regression residual control",
                "family": "smooth_local_regression_control",
                "formula": "r_corr = beta * predict(local linear regression over A-window)",
                "feature_names": ("local_linear_regression_residual",),
                "fit_mode": "lstsq",
                "complexity": 1,
                "role": "smooth_local_regression_control",
                "control_category": "smooth_window",
                "feature_fn": prior_controls._local_linear_regression_smoother,  # noqa: SLF001
            },
            {
                "candidate_id": "LOCAL-NEGCTRL-007",
                "name": "Closest-neighbor-only residual control",
                "family": "neighbor_availability_control",
                "formula": "r_corr = beta * closest same-Z neighbor residual",
                "feature_names": ("closest_neighbor_only_isotope_residual",),
                "fit_mode": "lstsq",
                "complexity": 1,
                "role": "neighbor_availability_control",
                "control_category": "neighbor_availability",
                "feature_fn": prior_controls._closest_neighbor_only_isotope_mean,  # noqa: SLF001
            },
            {
                "candidate_id": "LOCAL-NEGCTRL-008",
                "name": "Near-null local-neighborhood control",
                "family": "near_null_neighborhood_control",
                "formula": "r_corr = beta * 0 after deterministic neighborhood lookup",
                "feature_names": ("near_null_neighborhood",),
                "fit_mode": "lstsq",
                "complexity": 1,
                "role": "near_null_neighborhood_control",
                "control_category": "near_null_neighborhood",
                "feature_fn": _near_null_neighborhood_control,
            },
        )
    )
    return tuple(variants)


def _surface_context() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    np.ndarray,
    dict[str, Any],
    float,
    lane.NeighborIndex,
]:
    coefficients = full_known.load_frozen_baseline_coefficients()
    audit_rows, training_rows, training_residuals, surface = (
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
    return (
        audit_rows,
        training_rows,
        training_residuals,
        surface,
        threshold,
        lane.NeighborIndex(audit_rows),
    )


def _evaluate_variants(
    variants: tuple[dict[str, Any], ...],
    *,
    audit_rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    training_residuals: np.ndarray,
    high_error_threshold: float,
    index: lane.NeighborIndex,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, float | int | None]]]:
    baseline_metrics = lane._baseline_metrics(  # noqa: SLF001
        audit_rows,
        high_error_threshold=high_error_threshold,
    )
    items = [
        lane._evaluate_variant(  # noqa: SLF001
            variant,
            audit_rows=audit_rows,
            training_rows=training_rows,
            training_residuals=training_residuals,
            index=index,
            baseline_metrics=baseline_metrics,
            high_error_threshold=high_error_threshold,
        )
        for variant in variants
    ]
    return items, baseline_metrics


def _candidate_residuals_for_variant(
    item: dict[str, Any],
    rows: list[dict[str, Any]],
    *,
    variant: dict[str, Any],
    index: lane.NeighborIndex,
) -> list[float]:
    beta = np.asarray(
        [item["fitted_coefficients"][name] for name in variant["feature_names"]],
        dtype=float,
    )
    matrix = lane._feature_matrix(rows, variant=variant, index=index)  # noqa: SLF001
    out: list[float] = []
    for row, values in zip(rows, matrix):
        correction = float(values @ beta)
        out.append(
            float(row["observed_mev"])
            - (float(row["baseline_predicted_mev"]) + correction)
        )
    return out


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


def _group_indices(rows: list[dict[str, Any]], group_key: str) -> dict[str, list[int]]:
    grouped: dict[str, list[int]] = {}
    for idx, row in enumerate(rows):
        grouped.setdefault(f"{group_key}_{int(row[group_key]):03d}", []).append(idx)
    return grouped


def _transfer_summary(
    rows: list[dict[str, Any]],
    items: list[dict[str, Any]],
    *,
    variants_by_id: dict[str, dict[str, Any]],
    index: lane.NeighborIndex,
    group_key: str,
) -> dict[str, Any]:
    groups = _group_indices(rows, group_key)
    baseline_residuals = [float(row["baseline_residual_mev"]) for row in rows]
    residuals_by_id = {
        item["candidate_id"]: _candidate_residuals_for_variant(
            item,
            rows,
            variant=variants_by_id[item["candidate_id"]],
            index=index,
        )
        for item in items
    }
    group_items: list[dict[str, Any]] = []
    for group_id, indices in groups.items():
        deltas = {
            candidate_id: _mae_delta_for_indices(residuals, baseline_residuals, indices)
            for candidate_id, residuals in residuals_by_id.items()
        }
        valid = {key: value for key, value in deltas.items() if value is not None}
        best_id, best_delta = min(
            valid.items(),
            key=lambda pair: (float(pair[1]), pair[0]),
        )
        group_items.append(
            {
                "group_id": group_id,
                group_key: int(rows[indices[0]][group_key]),
                "row_count": len(indices),
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
        improved = sum(1 for value in deltas if float(value) < 0.0)
        by_candidate[candidate_id] = {
            "interpretable_group_count": len(deltas),
            "improved_group_count": improved,
            "improvement_rate": None if not deltas else improved / len(deltas),
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


def _candidate_vs_strongest_control(
    items: list[dict[str, Any]],
    *,
    baseline_metrics: dict[str, dict[str, float | int | None]],
) -> list[dict[str, Any]]:
    candidates = [item for item in items if item["role"] == "executed_candidate"]
    controls = [item for item in items if item["role"].endswith("_control")]
    table: list[dict[str, Any]] = []
    for candidate in candidates:
        subset_rows: list[dict[str, Any]] = []
        wins = 0
        for subset_id in sorted(baseline_metrics):
            candidate_delta = candidate["delta_mae_by_subset_mev"].get(subset_id)
            usable_controls = {
                control["candidate_id"]: control["delta_mae_by_subset_mev"].get(subset_id)
                for control in controls
                if control["delta_mae_by_subset_mev"].get(subset_id) is not None
            }
            if candidate_delta is None or not usable_controls:
                strongest_id = None
                strongest_delta = None
                margin = None
                beats = None
            else:
                strongest_id, strongest_delta = min(
                    usable_controls.items(), key=lambda pair: (float(pair[1]), pair[0])
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
        subset_win_rate = None if not comparable else wins / len(comparable)
        primary_margin = primary["control_minus_candidate_mev"]
        table.append(
            {
                "candidate_id": candidate["candidate_id"],
                "name": candidate["name"],
                "primary_strongest_control_id": primary["strongest_control_id"],
                "primary_candidate_delta_mae_mev": primary["candidate_delta_mae_mev"],
                "primary_strongest_control_delta_mae_mev": primary[
                    "strongest_control_delta_mae_mev"
                ],
                "primary_control_minus_candidate_mev": primary_margin,
                "primary_survives_negative_controls": bool(
                    primary_margin is not None
                    and primary_margin >= PRIMARY_SURVIVAL_MARGIN_MEV
                ),
                "candidate_wins_subset_count": wins,
                "comparable_subset_count": len(comparable),
                "subset_win_rate": subset_win_rate,
                "per_subset_comparison": subset_rows,
            }
        )
    return table


def _control_explanation_summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [item for item in items if item["role"] == "executed_candidate"]
    controls = [item for item in items if item["role"].endswith("_control")]
    best_candidate = min(
        candidates,
        key=lambda item: (
            float("inf")
            if item["primary_delta_mae_mev"] is None
            else float(item["primary_delta_mae_mev"]),
            item["candidate_id"],
        ),
    )
    strongest_control = min(
        controls,
        key=lambda item: (
            float("inf")
            if item["primary_delta_mae_mev"] is None
            else float(item["primary_delta_mae_mev"]),
            item["candidate_id"],
        ),
    )
    margin = (
        None
        if best_candidate["primary_delta_mae_mev"] is None
        or strongest_control["primary_delta_mae_mev"] is None
        else float(strongest_control["primary_delta_mae_mev"])
        - float(best_candidate["primary_delta_mae_mev"])
    )
    explanatory_controls = [
        control
        for control in controls
        if control["primary_delta_mae_mev"] is not None
        and best_candidate["primary_delta_mae_mev"] is not None
        and (
            float(control["primary_delta_mae_mev"])
            - float(best_candidate["primary_delta_mae_mev"])
        )
        <= PRIMARY_SURVIVAL_MARGIN_MEV
    ]
    if explanatory_controls:
        verdict = "CONTROL_EXPLAINS_OR_MATCHES"
    elif margin is not None and margin < PRIMARY_SURVIVAL_MARGIN_MEV:
        verdict = "INCONCLUSIVE"
    else:
        verdict = "NOT_EXPLAINED_BY_TESTED_CONTROLS"
    return {
        "best_candidate_id": best_candidate["candidate_id"],
        "best_candidate_primary_delta_mae_mev": best_candidate["primary_delta_mae_mev"],
        "strongest_control_id": strongest_control["candidate_id"],
        "strongest_control_primary_delta_mae_mev": strongest_control[
            "primary_delta_mae_mev"
        ],
        "control_minus_candidate_margin_mev": margin,
        "primary_survival_margin_mev": PRIMARY_SURVIVAL_MARGIN_MEV,
        "explanatory_control_ids": [
            control["candidate_id"] for control in explanatory_controls
        ],
        "explanation_verdict": verdict,
    }


def _lane_verdict(comparison_table: list[dict[str, Any]]) -> str:
    if not comparison_table:
        return "INCONCLUSIVE"
    for row in comparison_table:
        if (
            row["primary_survives_negative_controls"]
            and row["subset_win_rate"] is not None
            and row["subset_win_rate"] > 0.5
        ):
            return "PARTIALLY_VALID"
    if any(row["primary_survives_negative_controls"] for row in comparison_table):
        return "INCONCLUSIVE"
    return "FALSIFIED"


def build_metrics() -> dict[str, Any]:
    (
        audit_rows,
        training_rows,
        training_residuals,
        surface,
        high_error_threshold,
        index,
    ) = _surface_context()
    variants = _build_negative_control_variants()
    variants_by_id = {variant["candidate_id"]: variant for variant in variants}
    items, baseline_metrics = _evaluate_variants(
        variants,
        audit_rows=audit_rows,
        training_rows=training_rows,
        training_residuals=training_residuals,
        high_error_threshold=high_error_threshold,
        index=index,
    )
    comparison_table = _candidate_vs_strongest_control(
        items,
        baseline_metrics=baseline_metrics,
    )
    explanation = _control_explanation_summary(items)
    verdict = _lane_verdict(comparison_table)
    coefficients = full_known.load_frozen_baseline_coefficients()
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "predecessor_agent_run_id": prior_controls.AGENT_RUN_ID,
        "predecessor_task_id": prior_controls.TASK_ID,
        "root_lane_agent_run_id": lane.AGENT_RUN_ID,
        "root_lane_task_id": lane.TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "nuclear_local_curvature_negative_control_expansion",
        "sandbox_only": True,
        "evidence_class": "retrospective_full_known_local_curvature_negative_control_sandbox",
        "live_external_fetch_allowed": False,
        "summary": {
            "executed_variant_count": len(items),
            "executed_candidate_count": sum(
                1 for item in items if item["role"] == "executed_candidate"
            ),
            "executed_negative_control_count": sum(
                1 for item in items if item["role"].endswith("_control")
            ),
            "required_control_categories_present": sorted(
                {
                    variant["control_category"]
                    for variant in variants
                    if "control_category" in variant
                }
            ),
            "lane_verdict": verdict,
            "control_explanation_verdict": explanation["explanation_verdict"],
            "best_candidate_id": explanation["best_candidate_id"],
            "best_candidate_primary_delta_mae_mev": explanation[
                "best_candidate_primary_delta_mae_mev"
            ],
            "strongest_control_id": explanation["strongest_control_id"],
            "strongest_control_primary_delta_mae_mev": explanation[
                "strongest_control_primary_delta_mae_mev"
            ],
            "control_minus_candidate_margin_mev": explanation[
                "control_minus_candidate_margin_mev"
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
        "negative_control_panel": [
            {
                "candidate_id": variant["candidate_id"],
                "role": variant["role"],
                "family": variant["family"],
                "control_category": variant.get("control_category"),
                "feature_names": list(variant["feature_names"]),
            }
            for variant in variants
            if variant["role"].endswith("_control")
        ],
        "baseline_metrics_by_subset": baseline_metrics,
        "variants": items,
        "candidate_vs_strongest_control": comparison_table,
        "control_explanation": explanation,
        "isotope_chain_transfer": _transfer_summary(
            audit_rows,
            items,
            variants_by_id=variants_by_id,
            index=index,
            group_key="Z",
        ),
        "isotone_chain_transfer": _transfer_summary(
            audit_rows,
            items,
            variants_by_id=variants_by_id,
            index=index,
            group_key="N",
        ),
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
        "# Nuclear local-curvature negative-control expansion",
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
        f"- Control explanation verdict: `{summary['control_explanation_verdict']}`.",
        f"- Best candidate: `{summary['best_candidate_id']}` with full-known delta MAE {_format_delta(summary['best_candidate_primary_delta_mae_mev'])} MeV.",
        f"- Strongest control: `{summary['strongest_control_id']}` with full-known delta MAE {_format_delta(summary['strongest_control_primary_delta_mae_mev'])} MeV.",
        f"- Control-minus-candidate margin: {_format_delta(summary['control_minus_candidate_margin_mev'])} MeV.",
        "",
        "## Per-Variant Subset Deltas",
        "",
        "| Variant | Role | full-known | holdout | magic | neutron-rich | high-error |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in metrics["variants"]:
        lines.append(
            f"| `{item['candidate_id']}` | `{item['role']}` | "
            f"{_format_delta(item['primary_delta_mae_mev'])} | "
            f"{_format_delta(item['holdout_delta_mae_mev'])} | "
            f"{_format_delta(item['magic_region_delta_mae_mev'])} | "
            f"{_format_delta(item['neutron_rich_delta_mae_mev'])} | "
            f"{_format_delta(item['high_error_delta_mae_mev'])} |"
        )
    lines.extend(
        [
            "",
            "## Candidate vs Strongest Negative Control",
            "",
            "| Candidate | Strongest control | Margin | Subset win-rate | Survives? |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in metrics["candidate_vs_strongest_control"]:
        lines.append(
            f"| `{row['candidate_id']}` | `{row['primary_strongest_control_id']}` | "
            f"{_format_delta(row['primary_control_minus_candidate_mev'])} | "
            f"{row['subset_win_rate']:.3f} | "
            f"{row['primary_survives_negative_controls']} |"
        )
    lines.extend(
        [
            "",
            "## Chain Transfer",
            "",
            "| Candidate | Isotope groups | Isotope improvement rate | Isotone groups | Isotone improvement rate |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    isotope = metrics["isotope_chain_transfer"]["by_candidate"]
    isotone = metrics["isotone_chain_transfer"]["by_candidate"]
    for item in metrics["variants"]:
        if item["role"] != "executed_candidate":
            continue
        cid = item["candidate_id"]
        lines.append(
            f"| `{cid}` | {isotope[cid]['interpretable_group_count']} | "
            f"{isotope[cid]['improvement_rate']:.3f} | "
            f"{isotone[cid]['interpretable_group_count']} | "
            f"{isotone[cid]['improvement_rate']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Negative controls do not publish or promote a result. They only record whether the retrospective local-curvature signal is plausibly explained by chain shuffling, mass-number locality, shell proximity, generic smoothing, or near-null neighborhood structure.",
            "",
        ]
    )
    return "\n".join(lines)


def render_review(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    lines = [
        "# Nuclear local-curvature negative-control expansion review",
        "",
        f"**Task:** `{metrics['task_id']}`  ",
        f"**Agent run:** `{metrics['agent_run_id']}`  ",
        f"**Predecessor:** `{metrics['predecessor_task_id']}` / `{metrics['predecessor_agent_run_id']}`",
        "",
        "## Scope",
        "",
        "This review expands the local-curvature negative-control panel with chain-shuffled, mass-number-only, magic-distance-only, smooth-window, neighbor-availability, and near-null neighborhood controls. It keeps metric definitions aligned with the predecessor local-curvature lane.",
        "",
        "## Headline Result",
        "",
        f"- Lane verdict: `{summary['lane_verdict']}`.",
        f"- Control explanation verdict: `{summary['control_explanation_verdict']}`.",
        f"- Best candidate: `{summary['best_candidate_id']}`.",
        f"- Strongest control: `{summary['strongest_control_id']}`.",
        f"- Control-minus-candidate margin: {_format_delta(summary['control_minus_candidate_margin_mev'])} MeV.",
        "",
        "## Candidate vs Strongest Control",
        "",
        "| Candidate | Strongest control | Margin | Subset win-rate |",
        "| --- | --- | ---: | ---: |",
    ]
    for row in metrics["candidate_vs_strongest_control"]:
        lines.append(
            f"| `{row['candidate_id']}` | `{row['primary_strongest_control_id']}` | "
            f"{_format_delta(row['primary_control_minus_candidate_mev'])} | "
            f"{row['subset_win_rate']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- The audit is retrospective and uses committed full-known residual context.",
            "- The controls are deterministic but not exhaustive.",
            "- No live data, reveal scoring, registry entry, canonical result, claim, or knowledge update is produced.",
            "",
            "## Verdict",
            "",
            f"`{summary['lane_verdict']}`",
            "",
        ]
    )
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
            "| task_scope | PASS | TASK-0397 requests a negative-control expansion for the local-curvature lane. |",
            "| data_boundary | PASS | Only committed repository datasets and predecessor lane helpers are used. |",
            "| control_panel | PASS | Chain-shuffled, mass-number-only, magic-distance-only, smooth-window, neighbor-availability, and near-null controls are present. |",
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
            "- Retrospective full-known residual context is used; this is not blind prediction evidence.",
            "- The mass-number and magic-distance controls are low-dimensional controls, not full alternative nuclear models.",
            "- The near-null neighborhood control is a deterministic null check, not an explanatory model.",
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
            "- Re-ran the local-curvature candidates against an expanded negative-control panel.",
            f"- Strongest control: `{summary['strongest_control_id']}`.",
            f"- Control explanation verdict: `{summary['control_explanation_verdict']}`.",
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
            "contributor_id": "master",
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
                    "notes": "TASK-0397 requests a local-curvature negative-control expansion.",
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed repository data is used; no live external fetch is performed.",
                },
                {
                    "name": "control_panel",
                    "status": "PASS",
                    "notes": "Required negative-control categories are included.",
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No prediction registry, canonical result, claim, or knowledge file is written.",
                },
            ],
        },
        "limitations": [
            "Retrospective full-known residual context is used.",
            "Controls are deterministic but not exhaustive.",
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
