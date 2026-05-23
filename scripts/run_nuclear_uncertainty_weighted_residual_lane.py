"""TASK-0342 nuclear uncertainty-weighted residual hypothesis lane.

This runner audits whether the committed EXP-0012 baseline residual surface is
stable under conservative uncertainty weighting and filtering. It is
retrospective, sandbox-only evidence: it does not fetch live data, score
prediction registry entries, write canonical RESULT-* artifacts, update
claims, or edit knowledge.
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
    SemiEmpiricalCoefficients,
    binding_energy_uncertainty_mev,
    evaluate_baseline,
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset  # noqa: E402

import scripts.run_nuclear_shell_axis_full_known_audit as full_known  # noqa: E402


AGENT_RUN_ID = "AGENT-RUN-0029"
TASK_ID = "TASK-0342"

NMD_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0002-curated-measured-slice.yaml"
POST_AME_PATH = REPO_ROOT / "data" / "nuclear_masses" / "post_ame2020_holdout.yaml"

DEFAULT_METRICS_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "metrics.json"
DEFAULT_REPORT_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "report.md"
DEFAULT_AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "agent_run.yaml"
DEFAULT_LIMITATIONS_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "limitations.md"
DEFAULT_PREFLIGHT_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "preflight.md"
DEFAULT_REVIEW_SUMMARY_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "review_summary.md"
DEFAULT_REVIEW_PATH = (
    REPO_ROOT / "docs" / "reviews" / "nuclear-uncertainty-weighted-residual-lane.md"
)

Selector = Callable[[dict[str, Any], dict[str, float]], bool]
WeightFn = Callable[[dict[str, Any], dict[str, float]], float | None]


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return float(np.mean(np.asarray(values, dtype=float)))


def _rmse(values: list[float]) -> float | None:
    if not values:
        return None
    arr = np.asarray(values, dtype=float)
    return float(np.sqrt(np.mean(arr * arr)))


def _weighted_mean(values: list[float], weights: list[float]) -> float | None:
    if not values:
        return None
    arr = np.asarray(values, dtype=float)
    weight_arr = np.asarray(weights, dtype=float)
    total = float(np.sum(weight_arr))
    if total <= 0.0:
        return None
    return float(np.sum(arr * weight_arr) / total)


def _weighted_rmse(residuals: list[float], weights: list[float]) -> float | None:
    if not residuals:
        return None
    arr = np.asarray(residuals, dtype=float)
    weight_arr = np.asarray(weights, dtype=float)
    total = float(np.sum(weight_arr))
    if total <= 0.0:
        return None
    return float(np.sqrt(np.sum(arr * arr * weight_arr) / total))


def _format_delta(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value == 0.0:
        return "+0.000000"
    return f"{'+' if value > 0 else '-'}{abs(value):.6f}"


def _training_rows(coefficients: SemiEmpiricalCoefficients) -> list[dict[str, Any]]:
    dataset = load_nuclear_mass_dataset(NMD_PATH)
    baseline_rows = evaluate_baseline(
        entries=dataset.entries,
        model_id="model_fitted_semi_empirical",
        coefficients=coefficients,
    )
    entries_by_id = {entry.nuclide_id: entry for entry in dataset.entries}
    rows: list[dict[str, Any]] = []
    for baseline_row in baseline_rows:
        entry = entries_by_id[baseline_row.nuclide_id]
        observed_uncertainty = binding_energy_uncertainty_mev(entry)
        rows.append(
            {
                "row_id": f"nmd-0002::{entry.nuclide_id}",
                "nuclide_id": entry.nuclide_id,
                "Z": int(entry.Z),
                "N": int(entry.N),
                "A": int(entry.A),
                "source_surface": "nmd_0002_training_slice",
                "observed_mev": float(entry.binding_energy_mev),
                "baseline_predicted_mev": float(baseline_row.predicted_binding_energy_mev),
                "baseline_residual_mev": float(baseline_row.residual_mev),
                "observed_uncertainty_mev": observed_uncertainty,
                "comparison_uncertainty_mev": None,
                "combined_uncertainty_mev": observed_uncertainty,
                "weight_uncertainty_mev": observed_uncertainty,
                "was_extrapolated": False,
                "uncertainty_semantics": "curated_atomic_mass_uncertainty_floor_review_only",
                "uncertainty_fit_grade": False,
            }
        )
    return rows


def _post_ame2020_rows(coefficients: SemiEmpiricalCoefficients) -> list[dict[str, Any]]:
    with POST_AME_PATH.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    rows: list[dict[str, Any]] = []
    for entry in payload["entries"]:
        if not bool(entry["included_in_time_split_holdout"]):
            continue
        z, n = int(entry["Z"]), int(entry["N"])
        observed = float(entry["new_measurement"]["value_mev"])
        predicted = semi_empirical_binding_energy(z=z, n=n, coefficients=coefficients)
        observed_uncertainty = float(entry["new_measurement"]["uncertainty_mev"])
        comparison_uncertainty = float(entry["ame2020_comparison"]["uncertainty_mev"])
        combined_uncertainty = float(
            np.sqrt(observed_uncertainty * observed_uncertainty + comparison_uncertainty * comparison_uncertainty)
        )
        rows.append(
            {
                "row_id": str(entry["row_id"]),
                "nuclide_id": str(entry["nuclide_id"]),
                "Z": z,
                "N": n,
                "A": int(entry["A"]),
                "source_surface": "post_ame2020_primary_holdout",
                "observed_mev": observed,
                "baseline_predicted_mev": predicted,
                "baseline_residual_mev": observed - predicted,
                "observed_uncertainty_mev": observed_uncertainty,
                "comparison_uncertainty_mev": comparison_uncertainty,
                "combined_uncertainty_mev": combined_uncertainty,
                "weight_uncertainty_mev": observed_uncertainty,
                "was_extrapolated": bool(entry["ame2020_comparison"]["was_extrapolated"]),
                "uncertainty_semantics": "published_new_measurement_uncertainty_review_only_for_baseline_residual",
                "uncertainty_fit_grade": False,
                "measurement_method_ids": tuple(entry.get("measurement_method_ids", ())),
            }
        )
    return rows


def build_uncertainty_audit_surface(
    coefficients: SemiEmpiricalCoefficients,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return unique full-known rows with conservative uncertainty metadata."""
    training_rows = _training_rows(coefficients)
    post_rows = _post_ame2020_rows(coefficients)
    training_ids = {row["nuclide_id"] for row in training_rows}
    duplicate_post_rows = [row["nuclide_id"] for row in post_rows if row["nuclide_id"] in training_ids]
    unique_rows = [*training_rows, *[row for row in post_rows if row["nuclide_id"] not in training_ids]]
    missing = [
        row["row_id"]
        for row in unique_rows
        if row["weight_uncertainty_mev"] is None or float(row["weight_uncertainty_mev"]) <= 0.0
    ]
    uncertainties = [float(row["weight_uncertainty_mev"]) for row in unique_rows if row["weight_uncertainty_mev"] is not None]
    metadata = {
        "training_row_count": len(training_rows),
        "post_ame2020_primary_holdout_row_count": len(post_rows),
        "full_known_unique_row_count": len(unique_rows),
        "duplicate_post_rows_excluded_from_full_known": duplicate_post_rows,
        "rows_with_positive_weight_uncertainty": len(uncertainties),
        "rows_missing_positive_weight_uncertainty": missing,
        "minimum_weight_uncertainty_mev": min(uncertainties) if uncertainties else None,
        "median_weight_uncertainty_mev": float(np.median(np.asarray(uncertainties, dtype=float))) if uncertainties else None,
        "maximum_weight_uncertainty_mev": max(uncertainties) if uncertainties else None,
        "uncertainty_field_grade": "review_only",
        "fit_grade_uncertainty_row_count": sum(1 for row in unique_rows if row["uncertainty_fit_grade"]),
        "review_only_uncertainty_row_count": sum(1 for row in unique_rows if not row["uncertainty_fit_grade"]),
    }
    return unique_rows, metadata


def _surface_subset_ids(row: dict[str, Any]) -> tuple[str, ...]:
    ids = list(full_known._surface_subset_ids(row))  # noqa: SLF001
    ids.append(
        "low_uncertainty_half"
        if row["uncertainty_bucket"] in {"low", "lowest_decile"}
        else "high_uncertainty_half"
    )
    ids.append("low_uncertainty_decile" if row["uncertainty_bucket"] == "lowest_decile" else "not_lowest_uncertainty_decile")
    ids.append("extrapolated_ame2020_comparison" if row["was_extrapolated"] else "measured_ame2020_comparison")
    return tuple(dict.fromkeys(ids))


def _annotate_uncertainty_buckets(rows: list[dict[str, Any]]) -> dict[str, float]:
    uncertainties = np.asarray([float(row["weight_uncertainty_mev"]) for row in rows], dtype=float)
    median = float(np.median(uncertainties))
    lowest_decile = float(np.percentile(uncertainties, 10.0, method="linear"))
    for row in rows:
        sigma = float(row["weight_uncertainty_mev"])
        row["uncertainty_bucket"] = "low" if sigma <= median else "high"
        if sigma <= lowest_decile:
            row["uncertainty_bucket"] = "lowest_decile"
    return {
        "median_weight_uncertainty_mev": median,
        "lowest_decile_weight_uncertainty_mev": lowest_decile,
    }


def _row_weight(row: dict[str, Any], *, floor: float, uncertainty_key: str) -> float:
    sigma = max(float(row[uncertainty_key]), floor)
    return 1.0 / (sigma * sigma)


def _summarize_rows(
    rows: list[dict[str, Any]],
    *,
    selected_rows: list[dict[str, Any]],
    weights: list[float],
) -> dict[str, float | int | None]:
    residuals = [float(row["baseline_residual_mev"]) for row in selected_rows]
    abs_errors = [abs(value) for value in residuals]
    sigmas = [float(row["weight_uncertainty_mev"]) for row in selected_rows]
    normalized = [
        abs(float(row["baseline_residual_mev"])) / float(row["weight_uncertainty_mev"])
        for row in selected_rows
        if float(row["weight_uncertainty_mev"]) > 0.0
    ]
    return {
        "count": len(selected_rows),
        "row_fraction": len(selected_rows) / len(rows) if rows else None,
        "mae_mev": _mean(abs_errors),
        "rmse_mev": _rmse(residuals),
        "weighted_mae_mev": _weighted_mean(abs_errors, weights),
        "weighted_rmse_mev": _weighted_rmse(residuals, weights),
        "mean_error_mev": _mean(residuals),
        "mean_abs_uncertainty_normalized_error": _mean(normalized),
        "max_abs_uncertainty_normalized_error": max(normalized) if normalized else None,
        "median_weight_uncertainty_mev": float(np.median(np.asarray(sigmas, dtype=float))) if sigmas else None,
        "max_weight_uncertainty_mev": max(sigmas) if sigmas else None,
        "extrapolated_comparison_count": sum(1 for row in selected_rows if row["was_extrapolated"]),
        "training_slice_count": sum(1 for row in selected_rows if row["source_surface"] == "nmd_0002_training_slice"),
        "post_ame2020_count": sum(1 for row in selected_rows if row["source_surface"] == "post_ame2020_primary_holdout"),
    }


def _variant_rows(
    rows: list[dict[str, Any]],
    *,
    selector: Selector,
    weight_fn: WeightFn,
    thresholds: dict[str, float],
) -> tuple[list[dict[str, Any]], list[float]]:
    selected = [row for row in rows if selector(row, thresholds)]
    weights = [
        1.0 if (weight := weight_fn(row, thresholds)) is None else float(weight)
        for row in selected
    ]
    return selected, weights


def _variant_definitions() -> tuple[dict[str, Any], ...]:
    return (
        {
            "variant_id": "UNCERTAINTY-BASELINE-001",
            "name": "Unweighted full-known baseline reference",
            "role": "unweighted_reference",
            "selection": "all unique committed rows",
            "weighting": "uniform",
            "selector": lambda row, thresholds: True,
            "weight_fn": lambda row, thresholds: None,
        },
        {
            "variant_id": "UNCERTAINTY-WEIGHT-001",
            "name": "Observed-uncertainty inverse-variance weighting",
            "role": "uncertainty_weighted_diagnostic",
            "selection": "all unique committed rows",
            "weighting": "1 / max(observed_sigma, median_sigma)^2",
            "selector": lambda row, thresholds: True,
            "weight_fn": lambda row, thresholds: _row_weight(
                row,
                floor=thresholds["median_weight_uncertainty_mev"],
                uncertainty_key="weight_uncertainty_mev",
            ),
        },
        {
            "variant_id": "UNCERTAINTY-WEIGHT-002",
            "name": "Combined new-vs-AME inverse-variance weighting",
            "role": "uncertainty_weighted_diagnostic",
            "selection": "post-AME2020 rows use combined new and AME2020 uncertainty; NMD rows use observed uncertainty",
            "weighting": "1 / max(combined_sigma, median_sigma)^2",
            "selector": lambda row, thresholds: True,
            "weight_fn": lambda row, thresholds: _row_weight(
                row,
                floor=thresholds["median_weight_uncertainty_mev"],
                uncertainty_key="combined_uncertainty_mev",
            ),
        },
        {
            "variant_id": "UNCERTAINTY-FILTER-001",
            "name": "Low-uncertainty half filter",
            "role": "uncertainty_filter_diagnostic",
            "selection": "rows at or below median observed uncertainty",
            "weighting": "uniform within selected rows",
            "selector": lambda row, thresholds: float(row["weight_uncertainty_mev"])
            <= thresholds["median_weight_uncertainty_mev"],
            "weight_fn": lambda row, thresholds: None,
        },
        {
            "variant_id": "UNCERTAINTY-FILTER-002",
            "name": "High-uncertainty half filter",
            "role": "uncertainty_filter_diagnostic",
            "selection": "rows above median observed uncertainty",
            "weighting": "uniform within selected rows",
            "selector": lambda row, thresholds: float(row["weight_uncertainty_mev"])
            > thresholds["median_weight_uncertainty_mev"],
            "weight_fn": lambda row, thresholds: None,
        },
    )


def _evaluate_variants(rows: list[dict[str, Any]], thresholds: dict[str, float]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    baseline_summary: dict[str, Any] | None = None
    for variant in _variant_definitions():
        selected, weights = _variant_rows(
            rows,
            selector=variant["selector"],
            weight_fn=variant["weight_fn"],
            thresholds=thresholds,
        )
        summary = _summarize_rows(rows, selected_rows=selected, weights=weights)
        if baseline_summary is None:
            baseline_summary = summary
        baseline_mae = None if baseline_summary is None else baseline_summary["mae_mev"]
        baseline_rmse = None if baseline_summary is None else baseline_summary["rmse_mev"]
        baseline_weighted_mae = (
            None if baseline_summary is None else baseline_summary["weighted_mae_mev"]
        )
        baseline_weighted_rmse = (
            None if baseline_summary is None else baseline_summary["weighted_rmse_mev"]
        )
        items.append(
            {
                "variant_id": variant["variant_id"],
                "name": variant["name"],
                "role": variant["role"],
                "selection": variant["selection"],
                "weighting": variant["weighting"],
                "metrics": summary,
                "delta_mae_vs_unweighted_full_known_mev": (
                    None
                    if baseline_mae is None or summary["mae_mev"] is None
                    else float(summary["mae_mev"]) - float(baseline_mae)
                ),
                "delta_rmse_vs_unweighted_full_known_mev": (
                    None
                    if baseline_rmse is None or summary["rmse_mev"] is None
                    else float(summary["rmse_mev"]) - float(baseline_rmse)
                ),
                "delta_weighted_mae_vs_unweighted_full_known_mev": (
                    None
                    if baseline_weighted_mae is None or summary["weighted_mae_mev"] is None
                    else float(summary["weighted_mae_mev"]) - float(baseline_weighted_mae)
                ),
                "delta_weighted_rmse_vs_unweighted_full_known_mev": (
                    None
                    if baseline_weighted_rmse is None or summary["weighted_rmse_mev"] is None
                    else float(summary["weighted_rmse_mev"]) - float(baseline_weighted_rmse)
                ),
                "effective_weight_share_top_10_rows": _top_weight_share(weights, top_n=10),
            }
        )
    return items


def _top_weight_share(weights: list[float], *, top_n: int) -> float | None:
    if not weights:
        return None
    total = float(sum(weights))
    if total <= 0.0:
        return None
    return float(sum(sorted(weights, reverse=True)[:top_n]) / total)


def _baseline_metrics_by_subset(rows: list[dict[str, Any]]) -> dict[str, dict[str, float | int | None]]:
    subset_rows: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        for subset_id in _surface_subset_ids(row):
            subset_rows.setdefault(subset_id, []).append(row)
    return {
        subset_id: _summarize_rows(
            rows,
            selected_rows=selected_rows,
            weights=[1.0] * len(selected_rows),
        )
        for subset_id, selected_rows in sorted(subset_rows.items())
    }


def _largest_normalized_rows(rows: list[dict[str, Any]], *, limit: int = 10) -> list[dict[str, Any]]:
    items = []
    for row in rows:
        sigma = float(row["weight_uncertainty_mev"])
        items.append(
            {
                "row_id": row["row_id"],
                "nuclide_id": row["nuclide_id"],
                "source_surface": row["source_surface"],
                "baseline_residual_mev": float(row["baseline_residual_mev"]),
                "weight_uncertainty_mev": sigma,
                "abs_uncertainty_normalized_error": abs(float(row["baseline_residual_mev"])) / sigma,
                "was_extrapolated": bool(row["was_extrapolated"]),
            }
        )
    return sorted(
        items,
        key=lambda item: float(item["abs_uncertainty_normalized_error"]),
        reverse=True,
    )[:limit]


def _prior_lane_sensitivity(
    variant_items: list[dict[str, Any]],
    subset_metrics: dict[str, dict[str, float | int | None]],
) -> dict[str, Any]:
    low = subset_metrics["low_uncertainty_half"]["mae_mev"]
    high = subset_metrics["high_uncertainty_half"]["mae_mev"]
    low_high_gap = None if low is None or high is None else float(high) - float(low)
    weighted = next(item for item in variant_items if item["variant_id"] == "UNCERTAINTY-WEIGHT-001")
    weighted_delta = weighted["delta_weighted_mae_vs_unweighted_full_known_mev"]
    sensitive = (
        (low_high_gap is not None and abs(low_high_gap) >= 1.0)
        or (weighted_delta is not None and abs(float(weighted_delta)) >= 1.0)
    )
    return {
        "status": "sensitive_review_gate" if sensitive else "not_material_at_1_mev_gate",
        "low_minus_high_uncertainty_mae_gap_mev": low_high_gap,
        "observed_uncertainty_weighted_delta_mae_mev": weighted_delta,
        "lanes_requiring_caution": [
            "docs/reviews/nuclear-deformation-proxy-hypothesis-lane.md",
            "docs/reviews/nuclear-local-curvature-hypothesis-lane.md",
            "docs/reviews/nuclear-odd-even-shell-interaction-lane.md",
        ],
        "interpretation": (
            "Prior unweighted retrospective lanes should treat uncertainty handling as "
            "a review gate before any follow-up because the committed residual surface "
            "changes materially under the conservative uncertainty split."
            if sensitive
            else "The 1 MeV review gate did not find material aggregate sensitivity, but prior lanes remain sandbox-only."
        ),
    }


def build_metrics() -> dict[str, Any]:
    coefficients = full_known.load_frozen_baseline_coefficients()
    rows, metadata = build_uncertainty_audit_surface(coefficients)
    thresholds = _annotate_uncertainty_buckets(rows)
    metadata.update(thresholds)
    variant_items = _evaluate_variants(rows, thresholds)
    subset_metrics = _baseline_metrics_by_subset(rows)
    prior_sensitivity = _prior_lane_sensitivity(variant_items, subset_metrics)
    lane_verdict = "INCONCLUSIVE"
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "nuclear_uncertainty_weighted_residual_hypothesis_lane",
        "sandbox_only": True,
        "evidence_class": "retrospective_uncertainty_weighted_residual_diagnostic",
        "live_external_fetch_allowed": False,
        "summary": {
            "lane_verdict": lane_verdict,
            "variant_count": len(variant_items),
            "uncertainty_field_grade": metadata["uncertainty_field_grade"],
            "fit_grade_uncertainty_row_count": metadata["fit_grade_uncertainty_row_count"],
            "review_only_uncertainty_row_count": metadata["review_only_uncertainty_row_count"],
            "rows_missing_positive_weight_uncertainty": len(metadata["rows_missing_positive_weight_uncertainty"]),
            "prior_lane_uncertainty_sensitivity": prior_sensitivity["status"],
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
            **metadata,
        },
        "uncertainty_audit": {
            "field_status": "usable_for_review_weighting_not_fit_grade",
            "notes": [
                "NMD-0002 uses a coarse curated atomic-mass uncertainty floor.",
                "Post-AME2020 rows expose published New and AME2020 comparison uncertainties.",
                "The baseline model uncertainty is not represented, so inverse-variance summaries are diagnostics rather than fit-grade likelihoods.",
            ],
        },
        "variant_items": variant_items,
        "baseline_metrics_by_subset": subset_metrics,
        "largest_uncertainty_normalized_rows": _largest_normalized_rows(rows),
        "prior_lane_sensitivity_review": prior_sensitivity,
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any uncertainty-weighted follow-up, reveal scoring, "
                "RESULT-* artifact, claim, or knowledge update."
            ),
        },
        "limitations": [
            "Uncertainty fields are review-only for this lane because baseline model uncertainty is not represented.",
            "The NMD-0002 training slice uses a coarse curated uncertainty floor and must not be treated as a fit-grade likelihood surface.",
            "Inverse-variance weighting can concentrate effective weight on small-uncertainty rows even with a median-sigma floor.",
            "The lane audits baseline residual stability only; it does not re-score or promote prior candidate lanes.",
            "No source fetch, canonical result rewrite, PRED entry, claim update, or public-facing physics claim is authorized.",
        ],
    }


def _variant_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| Variant | Role | Count | MAE | RMSE | Weighted MAE | Mean sigma-norm err | Delta weighted MAE | Top-10 weight share |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in metrics["variant_items"]:
        m = item["metrics"]
        lines.append(
            "| {variant_id} | {role} | {count} | {mae:.6f} | {rmse:.6f} | {wmae:.6f} | {norm:.3f} | {delta} | {share:.3f} |".format(
                variant_id=item["variant_id"],
                role=item["role"],
                count=m["count"],
                mae=float(m["mae_mev"]),
                rmse=float(m["rmse_mev"]),
                wmae=float(m["weighted_mae_mev"]),
                norm=float(m["mean_abs_uncertainty_normalized_error"]),
                delta=_format_delta(item["delta_weighted_mae_vs_unweighted_full_known_mev"]),
                share=float(item["effective_weight_share_top_10_rows"]),
            )
        )
    return lines


def _subset_table(metrics: dict[str, Any]) -> list[str]:
    wanted = (
        "full_known",
        "training_slice",
        "primary_holdout",
        "low_uncertainty_half",
        "high_uncertainty_half",
        "post_ame2020_measured_comparison",
        "post_ame2020_extrapolated_comparison",
        "magic_any",
        "neutron_rich_high",
    )
    lines = [
        "| Subset | Count | MAE | RMSE | Median sigma | Mean sigma-norm err |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    subset_metrics = metrics["baseline_metrics_by_subset"]
    for subset_id in wanted:
        item = subset_metrics.get(subset_id)
        if item is None:
            continue
        lines.append(
            "| {subset_id} | {count} | {mae:.6f} | {rmse:.6f} | {sigma:.6f} | {norm:.3f} |".format(
                subset_id=subset_id,
                count=item["count"],
                mae=float(item["mae_mev"]),
                rmse=float(item["rmse_mev"]),
                sigma=float(item["median_weight_uncertainty_mev"]),
                norm=float(item["mean_abs_uncertainty_normalized_error"]),
            )
        )
    return lines


def render_report(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    sensitivity = metrics["prior_lane_sensitivity_review"]
    lines = [
        "# Nuclear uncertainty-weighted residual hypothesis lane",
        "",
        f"**Task:** `{TASK_ID}`",
        f"**Agent run:** `{AGENT_RUN_ID}`",
        "**Evidence class:** sandbox-only retrospective uncertainty diagnostic",
        f"**Verdict:** `{summary['lane_verdict']}`",
        "",
        "## Boundary",
        "",
        "This run uses only repository-pinned rows. It writes no canonical results, "
        "prediction-registry entries, claims, or knowledge artifacts. The uncertainty "
        "fields are treated as review-only weighting/filtering metadata, not as a "
        "fit-grade likelihood surface.",
        "",
        "## Uncertainty Audit",
        "",
        f"- Field grade: `{summary['uncertainty_field_grade']}`.",
        f"- Rows with positive uncertainty: `{metrics['datasets']['rows_with_positive_weight_uncertainty']}`.",
        f"- Fit-grade uncertainty rows: `{summary['fit_grade_uncertainty_row_count']}`.",
        f"- Review-only uncertainty rows: `{summary['review_only_uncertainty_row_count']}`.",
        f"- Missing positive uncertainty rows: `{summary['rows_missing_positive_weight_uncertainty']}`.",
        "",
        "## Variant Results",
        "",
        *_variant_table(metrics),
        "",
        "Negative delta MAE means the selected/weighted view has lower unweighted MAE "
        "than the full-known unweighted baseline reference. This is a diagnostic "
        "stability check, not a candidate improvement.",
        "",
        "## Subset Diagnostics",
        "",
        *_subset_table(metrics),
        "",
        "## Prior Lane Sensitivity",
        "",
        f"- Gate status: `{sensitivity['status']}`.",
        f"- High-minus-low uncertainty MAE gap: `{_format_delta(sensitivity['low_minus_high_uncertainty_mae_gap_mev'])}` MeV.",
        f"- Observed-uncertainty weighted delta MAE: `{_format_delta(sensitivity['observed_uncertainty_weighted_delta_mae_mev'])}` MeV.",
        f"- Interpretation: {sensitivity['interpretation']}",
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
            "hypothesis": "hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0049-uncertainty-weighted-residual-review.yaml",
            "experiment": "experiment_proposals/nuclear-mass/EXP-PROPOSAL-0015-nuclear-uncertainty-weighted-residual-review.yaml",
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
                    "notes": "TASK-0342 requests a sandbox uncertainty-weighted residual lane, not reveal scoring.",
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed NMD-0002 and post-AME2020 rows are used; no live external fetch is performed.",
                },
                {
                    "name": "uncertainty_boundary",
                    "status": "PASS",
                    "notes": "Uncertainty fields are recorded as review-only diagnostics, not fit-grade likelihood weights.",
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
        "**Lane:** nuclear uncertainty-weighted residual hypothesis lane",
        "",
    ]
    for check in manifest["preflight"]["checks"]:
        lines.append(f"- `{check['name']}`: `{check['status']}` - {check['notes']}")
    lines.append("")
    return "\n".join(lines)


def render_review_summary(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    sensitivity = metrics["prior_lane_sensitivity_review"]
    lines = [
        "# Review Summary",
        "",
        f"`{summary['lane_verdict']}` for claim promotion: uncertainty fields are "
        "usable for review-only weighting and filtering, but not for fit-grade "
        "likelihood claims.",
        "",
        f"- Prior lane uncertainty gate: `{sensitivity['status']}`.",
        f"- Variants executed: `{summary['variant_count']}`.",
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
