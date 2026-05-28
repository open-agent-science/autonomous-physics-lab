"""TASK-0341 nuclear extrapolated/measured boundary hypothesis lane.

This runner audits committed source-status structure around the
measured-versus-AME2020-extrapolated comparison boundary. It is retrospective,
sandbox-only diagnostic evidence: it does not fetch live data, score
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

from physics_lab.engines.nuclear_mass_baselines import MAGIC_NUMBERS  # noqa: E402

import scripts.run_nuclear_shell_axis_full_known_audit as full_known  # noqa: E402


AGENT_RUN_ID = "AGENT-RUN-0028"
TASK_ID = "TASK-0341"
SHUFFLE_OFFSET = 11

DEFAULT_METRICS_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "metrics.json"
DEFAULT_REPORT_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "report.md"
DEFAULT_AGENT_RUN_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "agent_run.yaml"
DEFAULT_LIMITATIONS_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "limitations.md"
DEFAULT_PREFLIGHT_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "preflight.md"
DEFAULT_REVIEW_SUMMARY_PATH = REPO_ROOT / "agent_runs" / AGENT_RUN_ID / "review_summary.md"
DEFAULT_REVIEW_PATH = (
    REPO_ROOT / "docs" / "reviews" / "nuclear-extrapolated-measured-boundary-lane.md"
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


def _neutron_excess(row: dict[str, Any]) -> float:
    a = int(row["A"])
    if a <= 0:
        return 0.0
    return float(int(row["N"]) - int(row["Z"])) / float(a)


def _scaled_a_squared(row: dict[str, Any]) -> float:
    scaled = (float(row["A"]) - 100.0) / 100.0
    return scaled * scaled


def _post_boundary_sign(row: dict[str, Any]) -> float:
    if row["source_surface"] != "post_ame2020_primary_holdout":
        return 0.0
    return 1.0 if bool(row["was_extrapolated"]) else -1.0


def _post_measured_only(row: dict[str, Any]) -> float:
    return (
        1.0
        if row["source_surface"] == "post_ame2020_primary_holdout"
        and not bool(row["was_extrapolated"])
        else 0.0
    )


def _post_extrapolated_only(row: dict[str, Any]) -> float:
    return (
        1.0
        if row["source_surface"] == "post_ame2020_primary_holdout"
        and bool(row["was_extrapolated"])
        else 0.0
    )


def _boundary_contrast(row: dict[str, Any]) -> tuple[float, ...]:
    return (_post_boundary_sign(row),)


def _uncertainty_weighted_boundary(row: dict[str, Any]) -> tuple[float, ...]:
    sign = _post_boundary_sign(row)
    if sign == 0.0:
        return (0.0,)
    uncertainty = float(row.get("comparison_uncertainty_mev") or 0.0)
    return (sign * float(np.log1p(10.0 * uncertainty)),)


def _edge_weighted_boundary(row: dict[str, Any]) -> tuple[float, ...]:
    sign = _post_boundary_sign(row)
    if sign == 0.0:
        return (0.0,)
    return (sign * float(row.get("edge_distance_scaled") or 0.0),)


def _measured_only_control(row: dict[str, Any]) -> tuple[float, ...]:
    return (_post_measured_only(row),)


def _extrapolated_only_control(row: dict[str, Any]) -> tuple[float, ...]:
    return (_post_extrapolated_only(row),)


def _smooth_a_control(row: dict[str, Any]) -> tuple[float, ...]:
    return (_scaled_a_squared(row),)


GENERATED_VARIANTS: tuple[dict[str, Any], ...] = (
    {
        "candidate_id": "BOUNDARY-001",
        "name": "AME2020 extrapolated-versus-measured comparison contrast",
        "family": "source_status_boundary",
        "formula": "r_corr = beta * (+1 if AME2020 comparison is extrapolated, -1 if measured)",
        "feature_names": ("ame2020_extrapolated_measured_contrast",),
        "fit_mode": "retrospective_full_known_lstsq",
        "complexity": 1,
        "role": "executed_boundary_candidate",
        "feature_fn": _boundary_contrast,
    },
    {
        "candidate_id": "BOUNDARY-002",
        "name": "Uncertainty-weighted source-status boundary contrast",
        "family": "source_uncertainty_boundary",
        "formula": "r_corr = beta * boundary_contrast * log1p(10 * comparison_uncertainty_mev)",
        "feature_names": ("uncertainty_weighted_boundary",),
        "fit_mode": "retrospective_full_known_lstsq",
        "complexity": 1,
        "role": "executed_boundary_candidate",
        "feature_fn": _uncertainty_weighted_boundary,
    },
    {
        "candidate_id": "BOUNDARY-003",
        "name": "Edge-of-known-surface weighted boundary contrast",
        "family": "edge_weighted_boundary",
        "formula": "r_corr = beta * boundary_contrast * nearest_training_distance_scaled",
        "feature_names": ("edge_weighted_boundary",),
        "fit_mode": "retrospective_full_known_lstsq",
        "complexity": 1,
        "role": "executed_boundary_candidate",
        "feature_fn": _edge_weighted_boundary,
    },
    {
        "candidate_id": "BOUNDARY-004",
        "name": "Source-reference fixed effects",
        "family": "source_reference_fixed_effects",
        "formula": "r_corr = beta_ref[source_reference_id]",
        "feature_names": ("source_reference_fixed_effects",),
        "fit_mode": "not_executed",
        "complexity": 40,
        "role": "rejected_before_execution",
        "rejection_reason": (
            "Rejected before execution because per-reference fixed effects would "
            "turn the lane into a sparse source memorization exercise."
        ),
    },
    {
        "candidate_id": "BOUNDARY-005",
        "name": "Measurement-method family offsets",
        "family": "measurement_method_offsets",
        "formula": "r_corr = beta_method[measurement_method_family]",
        "feature_names": ("measurement_method_family_offsets",),
        "fit_mode": "not_executed",
        "complexity": 6,
        "role": "rejected_before_execution",
        "rejection_reason": (
            "Rejected before execution because method families are unevenly "
            "represented and should be reviewed as provenance diagnostics before "
            "being used as correction terms."
        ),
    },
    {
        "candidate_id": "BOUNDARY-006",
        "name": "Neutron-rich extrapolated-boundary interaction",
        "family": "source_status_by_neutron_rich_interaction",
        "formula": "r_corr = beta * I[AME2020 extrapolated] * ((N-Z)/A)",
        "feature_names": ("extrapolated_neutron_rich_interaction",),
        "fit_mode": "not_executed",
        "complexity": 1,
        "role": "rejected_before_execution",
        "rejection_reason": (
            "Rejected before execution because the task boundary is source-status "
            "diagnostics; neutron-rich interactions risk being overread as a "
            "physical correction."
        ),
    },
    {
        "candidate_id": "BOUNDARY-CONTROL-001",
        "name": "Measured-comparison only offset control",
        "family": "measured_comparison_control",
        "formula": "r_corr = beta * I[post-AME2020 row with measured AME2020 comparison]",
        "feature_names": ("measured_comparison_only",),
        "fit_mode": "retrospective_full_known_lstsq",
        "complexity": 1,
        "role": "measured_only_control",
        "feature_fn": _measured_only_control,
    },
    {
        "candidate_id": "BOUNDARY-CONTROL-002",
        "name": "Extrapolated-comparison only offset control",
        "family": "extrapolated_comparison_control",
        "formula": "r_corr = beta * I[post-AME2020 row with extrapolated AME2020 comparison]",
        "feature_names": ("extrapolated_comparison_only",),
        "fit_mode": "retrospective_full_known_lstsq",
        "complexity": 1,
        "role": "extrapolated_only_control",
        "feature_fn": _extrapolated_only_control,
    },
    {
        "candidate_id": "BOUNDARY-CONTROL-003",
        "name": "Cyclically shuffled source-status contrast control",
        "family": "source_status_shuffled_control",
        "formula": "r_corr = beta * shuffled(boundary_contrast)",
        "feature_names": ("shuffled_boundary_contrast",),
        "fit_mode": "retrospective_full_known_lstsq_shuffled",
        "complexity": 1,
        "role": "source_shuffled_control",
        "feature_fn": _boundary_contrast,
        "shuffle_scheme": "cyclic-shift-11",
        "shuffle_seed": SHUFFLE_OFFSET,
    },
    {
        "candidate_id": "BOUNDARY-CONTROL-004",
        "name": "Smooth-A matched-complexity control",
        "family": "smooth_a_control",
        "formula": "r_corr = beta * ((A - 100) / 100)^2",
        "feature_names": ("smooth_a_squared",),
        "fit_mode": "retrospective_full_known_lstsq",
        "complexity": 1,
        "role": "smooth_a_control",
        "feature_fn": _smooth_a_control,
    },
)


def _load_post_ame2020_metadata() -> dict[str, dict[str, Any]]:
    with full_known.POST_AME_PATH.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    metadata: dict[str, dict[str, Any]] = {}
    for entry in payload["entries"]:
        method_ids = tuple(str(item) for item in entry.get("measurement_method_ids", ()))
        metadata[str(entry["row_id"])] = {
            "measurement_status": str(entry.get("measurement_status", "")),
            "comparison_uncertainty_mev": float(
                entry["ame2020_comparison"]["uncertainty_mev"]
            ),
            "comparison_was_extrapolated": bool(
                entry["ame2020_comparison"]["was_extrapolated"]
            ),
            "source_reference_id": str(entry.get("source_reference_id", "")),
            "measurement_method_ids": method_ids,
            "measurement_method_family": _method_family(method_ids),
        }
    return metadata


def _method_family(method_ids: tuple[str, ...]) -> str:
    if not method_ids:
        return "unknown"
    joined = " ".join(method_ids)
    if "ion_trap" in joined:
        return "ion_trap"
    if "mr_tof" in joined:
        return "mr_tof"
    if "brho" in joined:
        return "brho"
    if "storage_ring" in joined:
        return "storage_ring"
    return "other"


def _annotate_rows(rows: list[dict[str, Any]], training_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    post_metadata = _load_post_ame2020_metadata()
    training_points = [(int(row["Z"]), int(row["N"])) for row in training_rows]
    annotated: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        if item["source_surface"] == "post_ame2020_primary_holdout":
            meta = post_metadata[item["row_id"]]
            item.update(meta)
        else:
            item.update(
                {
                    "measurement_status": "measured",
                    "comparison_uncertainty_mev": 0.0,
                    "comparison_was_extrapolated": False,
                    "source_reference_id": "nmd-0002-curated",
                    "measurement_method_ids": (),
                    "measurement_method_family": "curated_training_slice",
                }
            )
        z, n = int(item["Z"]), int(item["N"])
        nearest = min(abs(z - tz) + abs(n - tn) for tz, tn in training_points)
        item["nearest_training_l1_distance"] = int(nearest)
        annotated.append(item)

    post_distances = [
        float(row["nearest_training_l1_distance"])
        for row in annotated
        if row["source_surface"] == "post_ame2020_primary_holdout"
    ]
    edge_threshold = float(np.quantile(np.asarray(post_distances, dtype=float), 0.75))
    max_distance = max(post_distances) if post_distances else 1.0
    abs_errors = [abs(float(row["baseline_residual_mev"])) for row in annotated]
    high_error_threshold = float(np.quantile(np.asarray(abs_errors, dtype=float), 0.90))
    for row in annotated:
        row["edge_distance_scaled"] = (
            float(row["nearest_training_l1_distance"]) / max_distance
            if max_distance > 0.0
            else 0.0
        )
        row["edge_of_known_surface"] = (
            row["source_surface"] == "post_ame2020_primary_holdout"
            and float(row["nearest_training_l1_distance"]) >= edge_threshold
        )
        row["high_error_reference"] = (
            abs(float(row["baseline_residual_mev"])) >= high_error_threshold
        )
    return annotated


def _boundary_preflight(rows: list[dict[str, Any]]) -> dict[str, Any]:
    training_rows = [row for row in rows if row["source_surface"] == "nmd_0002_training_slice"]
    holdout_rows = [
        row for row in rows if row["source_surface"] == "post_ame2020_primary_holdout"
    ]
    measured_comparison = [row for row in holdout_rows if not bool(row["was_extrapolated"])]
    extrapolated_comparison = [row for row in holdout_rows if bool(row["was_extrapolated"])]
    method_families = sorted({str(row["measurement_method_family"]) for row in holdout_rows})
    usable = bool(training_rows and measured_comparison and extrapolated_comparison)
    return {
        "passed": usable,
        "training_measured_row_count": len(training_rows),
        "post_ame2020_holdout_row_count": len(holdout_rows),
        "post_ame2020_measured_comparison_count": len(measured_comparison),
        "post_ame2020_extrapolated_comparison_count": len(extrapolated_comparison),
        "measurement_method_family_count": len(method_families),
        "measurement_method_families": method_families,
        "fit_surface": "retrospective_full_known_diagnostic",
        "reason": (
            "Usable for retrospective source-status diagnostics; not sufficient "
            "for a prospective physical correction because training rows are "
            "curated measured-only."
            if usable
            else "Insufficient measured/extrapolated class coverage for candidate execution."
        ),
    }


def _subset_ids(row: dict[str, Any]) -> tuple[str, ...]:
    ids = list(full_known._surface_subset_ids(row))  # noqa: SLF001
    if row["source_surface"] == "post_ame2020_primary_holdout":
        ids.append("measured_extrapolated_boundary_panel")
        if bool(row["was_extrapolated"]):
            ids.append("extrapolated_comparison")
        else:
            ids.append("measured_comparison")
    if bool(row.get("edge_of_known_surface")):
        ids.append("edge_of_known_surface")
    if _neutron_excess(row) >= 0.25:
        ids.append("neutron_rich")
    if (
        int(row["Z"]) in MAGIC_NUMBERS
        or int(row["N"]) in MAGIC_NUMBERS
        or _nearest_magic_distance(int(row["Z"])) <= 2
        or _nearest_magic_distance(int(row["N"])) <= 2
    ):
        ids.append("magic_region")
    if bool(row.get("high_error_reference")):
        ids.append("high_error_reference")
    return tuple(dict.fromkeys(ids))


def _summarize_errors(errors: list[float]) -> dict[str, float | int | None]:
    abs_errors = [abs(value) for value in errors]
    return {
        "count": len(errors),
        "mae_mev": _mean(abs_errors),
        "rmse_mev": _rmse(errors),
        "mean_signed_error_mev": _mean(errors),
    }


def _feature_matrix(
    variant: dict[str, Any],
    rows: list[dict[str, Any]],
) -> np.ndarray:
    feature_fn = variant["feature_fn"]
    vectors = [feature_fn(row) for row in rows]
    if variant.get("shuffle_seed") is not None:
        count = len(vectors)
        offset = int(variant["shuffle_seed"])
        vectors = [vectors[(idx + offset) % count] for idx in range(count)]
    return np.asarray(vectors, dtype=float)


def _fit_variant(
    variant: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    residuals = np.asarray([float(row["baseline_residual_mev"]) for row in rows], dtype=float)
    matrix = _feature_matrix(variant, rows)
    if matrix.size == 0 or not np.any(matrix):
        beta = np.zeros(matrix.shape[1] if matrix.ndim == 2 else 0, dtype=float)
        correction = np.zeros(len(rows), dtype=float)
    else:
        beta, *_ = np.linalg.lstsq(matrix, residuals, rcond=None)
        correction = matrix @ beta
    corrected = residuals - correction
    return {
        "coefficients": [float(value) for value in beta],
        "corrected_residuals": [float(value) for value in corrected],
        "corrections": [float(value) for value in correction],
    }


def _metrics_by_subset(rows: list[dict[str, Any]], residuals: list[float]) -> dict[str, Any]:
    if len(rows) != len(residuals):
        raise ValueError("rows and residuals must have the same length")
    buckets: dict[str, list[float]] = {}
    for row, residual in zip(rows, residuals):
        for subset_id in _subset_ids(row):
            buckets.setdefault(subset_id, []).append(float(residual))
    return {key: _summarize_errors(value) for key, value in sorted(buckets.items())}


def _delta_mae(candidate: dict[str, Any] | None, baseline: dict[str, Any] | None) -> float | None:
    if candidate is None or baseline is None:
        return None
    if candidate["mae_mev"] is None or baseline["mae_mev"] is None:
        return None
    return float(candidate["mae_mev"]) - float(baseline["mae_mev"])


def _delta_rmse(candidate: dict[str, Any] | None, baseline: dict[str, Any] | None) -> float | None:
    if candidate is None or baseline is None:
        return None
    if candidate["rmse_mev"] is None or baseline["rmse_mev"] is None:
        return None
    return float(candidate["rmse_mev"]) - float(baseline["rmse_mev"])


def _row_examples(
    rows: list[dict[str, Any]],
    baseline_residuals: list[float],
    corrected_residuals: list[float],
    *,
    reverse: bool,
    limit: int = 5,
) -> list[dict[str, Any]]:
    if len(rows) != len(baseline_residuals) or len(rows) != len(corrected_residuals):
        raise ValueError("rows, baseline_residuals, and corrected_residuals must have the same length")
    scored = []
    for row, baseline, corrected in zip(rows, baseline_residuals, corrected_residuals):
        delta_abs = abs(float(corrected)) - abs(float(baseline))
        scored.append(
            {
                "row_id": row["row_id"],
                "nuclide_id": row["nuclide_id"],
                "source_surface": row["source_surface"],
                "was_extrapolated": bool(row["was_extrapolated"]),
                "delta_abs_error_mev": float(delta_abs),
            }
        )
    if reverse:
        return sorted(
            scored,
            key=lambda item: (-round(float(item["delta_abs_error_mev"]), 12), str(item["row_id"])),
        )[:limit]
    return sorted(
        scored,
        key=lambda item: (round(float(item["delta_abs_error_mev"]), 12), str(item["row_id"])),
    )[:limit]


def _candidate_item(
    variant: dict[str, Any],
    rows: list[dict[str, Any]],
    baseline_metrics: dict[str, Any],
) -> dict[str, Any]:
    fitted = _fit_variant(variant, rows)
    baseline_residuals = [float(row["baseline_residual_mev"]) for row in rows]
    corrected_residuals = fitted["corrected_residuals"]
    candidate_metrics = _metrics_by_subset(rows, corrected_residuals)
    baseline_primary = baseline_metrics.get("full_known")
    candidate_primary = candidate_metrics.get("full_known")
    candidate_id = str(variant["candidate_id"])
    item: dict[str, Any] = {
        "candidate_id": candidate_id,
        "name": variant["name"],
        "role": variant["role"],
        "family": variant["family"],
        "formula": variant["formula"],
        "fit_mode": variant["fit_mode"],
        "feature_names": list(variant["feature_names"]),
        "complexity": int(variant["complexity"]),
        "coefficients": fitted["coefficients"],
        "primary_delta_mae_mev": _delta_mae(candidate_primary, baseline_primary),
        "primary_delta_rmse_mev": _delta_rmse(candidate_primary, baseline_primary),
        "holdout_delta_mae_mev": _delta_mae(
            candidate_metrics.get("primary_holdout"),
            baseline_metrics.get("primary_holdout"),
        ),
        "measured_comparison_delta_mae_mev": _delta_mae(
            candidate_metrics.get("measured_comparison"),
            baseline_metrics.get("measured_comparison"),
        ),
        "extrapolated_comparison_delta_mae_mev": _delta_mae(
            candidate_metrics.get("extrapolated_comparison"),
            baseline_metrics.get("extrapolated_comparison"),
        ),
        "edge_of_known_surface_delta_mae_mev": _delta_mae(
            candidate_metrics.get("edge_of_known_surface"),
            baseline_metrics.get("edge_of_known_surface"),
        ),
        "neutron_rich_delta_mae_mev": _delta_mae(
            candidate_metrics.get("neutron_rich"),
            baseline_metrics.get("neutron_rich"),
        ),
        "magic_region_delta_mae_mev": _delta_mae(
            candidate_metrics.get("magic_region"),
            baseline_metrics.get("magic_region"),
        ),
        "high_error_delta_mae_mev": _delta_mae(
            candidate_metrics.get("high_error_reference"),
            baseline_metrics.get("high_error_reference"),
        ),
        "subset_metrics": candidate_metrics,
        "largest_regressions": _row_examples(
            rows,
            baseline_residuals,
            corrected_residuals,
            reverse=True,
        ),
        "largest_improvements": _row_examples(
            rows,
            baseline_residuals,
            corrected_residuals,
            reverse=False,
        ),
    }
    if variant.get("shuffle_scheme"):
        item["shuffle_scheme"] = variant["shuffle_scheme"]
        item["shuffle_seed"] = int(variant["shuffle_seed"])
    return item


def _rejected_items() -> list[dict[str, Any]]:
    return [
        {
            key: value
            for key, value in variant.items()
            if key
            in {
                "candidate_id",
                "name",
                "role",
                "family",
                "formula",
                "feature_names",
                "fit_mode",
                "complexity",
                "rejection_reason",
            }
        }
        for variant in GENERATED_VARIANTS
        if variant["role"] == "rejected_before_execution"
    ]


def _control_gate(candidate_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    controls = [
        item
        for item in candidate_items
        if item["role"]
        in {
            "measured_only_control",
            "extrapolated_only_control",
            "source_shuffled_control",
            "smooth_a_control",
        }
    ]
    if not controls:
        return []
    best_control = min(
        controls,
        key=lambda item: float("inf")
        if item["primary_delta_mae_mev"] is None
        else float(item["primary_delta_mae_mev"]),
    )
    rows = []
    for item in candidate_items:
        if item["role"] != "executed_boundary_candidate":
            continue
        candidate_delta = item["primary_delta_mae_mev"]
        control_delta = best_control["primary_delta_mae_mev"]
        beats_controls = (
            candidate_delta is not None
            and control_delta is not None
            and float(candidate_delta) < float(control_delta) - 0.02
        )
        rows.append(
            {
                "candidate_id": item["candidate_id"],
                "best_control_id": best_control["candidate_id"],
                "candidate_primary_delta_mae_mev": candidate_delta,
                "best_control_primary_delta_mae_mev": control_delta,
                "beats_controls": bool(beats_controls),
            }
        )
    return rows


def build_metrics() -> dict[str, Any]:
    coefficients = full_known.load_frozen_baseline_coefficients()
    rows_raw, training_rows, _training_residuals, full_known_baseline = (
        full_known.build_audit_surface(coefficients)
    )
    rows = _annotate_rows(rows_raw, training_rows)
    preflight = _boundary_preflight(rows)
    baseline_residuals = [float(row["baseline_residual_mev"]) for row in rows]
    baseline_metrics = _metrics_by_subset(rows, baseline_residuals)
    executed_variants = [
        variant
        for variant in GENERATED_VARIANTS
        if variant["role"] != "rejected_before_execution"
    ]
    candidate_items = [
        _candidate_item(variant, rows, baseline_metrics)
        for variant in executed_variants
    ]
    control_gate = _control_gate(candidate_items)
    best_item = min(
        candidate_items,
        key=lambda item: float("inf")
        if item["primary_delta_mae_mev"] is None
        else float(item["primary_delta_mae_mev"]),
    )
    summary = {
        "lane_verdict": "INCONCLUSIVE",
        "generated_boundary_candidate_count": 6,
        "executed_boundary_candidate_count": 3,
        "executed_control_count": 4,
        "best_primary_delta_candidate_id": best_item["candidate_id"],
        "best_primary_delta_mae_mev": best_item["primary_delta_mae_mev"],
        "best_primary_delta_rmse_mev": best_item["primary_delta_rmse_mev"],
        "preflight_passed": bool(preflight["passed"]),
        "canonical_results_changed": False,
        "canonical_claims_changed": False,
        "prediction_registry_changed": False,
        "claim_promotion_allowed": False,
    }
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "sandbox_only": True,
        "analysis_scope": "retrospective_source_status_boundary_diagnostic",
        "datasets": {
            "training_slice": "data/nuclear_masses/nmd-0002-curated-measured-slice.yaml",
            "post_ame2020_holdout": "data/nuclear_masses/post_ame2020_holdout.yaml",
            "frozen_baseline_result": "results/EXP-0012/RUN-0001/result.yaml",
        },
        "full_known_metadata": full_known_baseline["metadata"],
        "source_status_preflight": preflight,
        "baseline_metrics": baseline_metrics,
        "candidate_items": candidate_items,
        "rejected_before_execution": _rejected_items(),
        "control_gate": control_gate,
        "summary": summary,
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any measured/extrapolated boundary "
                "follow-up, reveal scoring, RESULT-* artifact, claim, or "
                "knowledge update."
            ),
        },
        "limitations": [
            "The NMD-0002 fit slice is curated measured-only, so source-status terms are retrospective diagnostics, not prospective correction evidence.",
            "The extrapolated flag describes the AME2020 comparison column for new measured rows, not an extrapolated new measurement.",
            "Candidate coefficients are fit on the full committed surface and must not be treated as holdout validation.",
            "Measured/extrapolated and source-shuffled controls are included because status features can track provenance or sample composition.",
            "No source fetch, canonical result rewrite, PRED entry, claim update, or public-facing physics claim is authorized.",
        ],
    }


def render_report(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    preflight = metrics["source_status_preflight"]
    lines = [
        "# Nuclear extrapolated/measured boundary lane",
        "",
        f"**Task:** `{TASK_ID}`",
        f"**Agent run:** `{AGENT_RUN_ID}`",
        "**Evidence class:** sandbox-only retrospective source-status diagnostic",
        f"**Verdict:** `{summary['lane_verdict']}`",
        "",
        "## Boundary",
        "",
        "This run uses only committed repository rows and row-level source-status metadata. "
        "The boundary flag is the AME2020 comparison-column extrapolation marker on "
        "post-AME2020 measured rows. It writes no prediction registry entries, "
        "canonical results, claims, or knowledge artifacts.",
        "",
        "## Source-Status Preflight",
        "",
        f"- Training measured rows: `{preflight['training_measured_row_count']}`.",
        f"- Post-AME2020 holdout rows: `{preflight['post_ame2020_holdout_row_count']}`.",
        f"- AME2020 measured-comparison rows: `{preflight['post_ame2020_measured_comparison_count']}`.",
        f"- AME2020 extrapolated-comparison rows: `{preflight['post_ame2020_extrapolated_comparison_count']}`.",
        f"- Measurement-method families: `{preflight['measurement_method_family_count']}`.",
        f"- Fit surface: `{preflight['fit_surface']}`.",
        f"- Preflight note: {preflight['reason']}",
        "",
        "## Candidate And Control Results",
        "",
        "| Candidate | Role | Full-known MAE | Holdout | Measured comparison | Extrapolated comparison | Edge | Neutron-rich | Magic region | High-error |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in metrics["candidate_items"]:
        lines.append(
            "| {candidate_id} | {role} | {primary} | {holdout} | {measured} | "
            "{extrapolated} | {edge} | {neutron} | {magic} | {high_error} |".format(
                candidate_id=item["candidate_id"],
                role=item["role"],
                primary=_format_delta(item["primary_delta_mae_mev"]),
                holdout=_format_delta(item["holdout_delta_mae_mev"]),
                measured=_format_delta(item["measured_comparison_delta_mae_mev"]),
                extrapolated=_format_delta(item["extrapolated_comparison_delta_mae_mev"]),
                edge=_format_delta(item["edge_of_known_surface_delta_mae_mev"]),
                neutron=_format_delta(item["neutron_rich_delta_mae_mev"]),
                magic=_format_delta(item["magic_region_delta_mae_mev"]),
                high_error=_format_delta(item["high_error_delta_mae_mev"]),
            )
        )
    lines.extend(
        [
            "",
            "Negative deltas mean lower MAE than the frozen semi-empirical baseline on that subset. Positive deltas are regressions and remain visible.",
            "",
            "## Control Gate",
            "",
            "| Candidate | Best control | Candidate primary | Best control primary | Beats controls |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in metrics["control_gate"]:
        lines.append(
            "| {candidate_id} | {best_control_id} | {candidate} | {control} | {beats} |".format(
                candidate_id=row["candidate_id"],
                best_control_id=row["best_control_id"],
                candidate=_format_delta(row["candidate_primary_delta_mae_mev"]),
                control=_format_delta(row["best_control_primary_delta_mae_mev"]),
                beats="yes" if row["beats_controls"] else "no",
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Generated boundary candidates: `{summary['generated_boundary_candidate_count']}`.",
            f"- Executed boundary candidates: `{summary['executed_boundary_candidate_count']}`.",
            f"- Executed controls: `{summary['executed_control_count']}`.",
            f"- Best full-known delta: `{summary['best_primary_delta_candidate_id']}` ({_format_delta(summary['best_primary_delta_mae_mev'])} MeV MAE).",
            "- The verdict stays conservative because the source-status terms are fit retrospectively on the committed surface.",
            "- Any positive status signal is data-boundary diagnostic evidence only, not a physical-law or reveal-scoring result.",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in metrics["limitations"])
    lines.append("")
    return "\n".join(lines)


def render_limitations(metrics: dict[str, Any]) -> str:
    return "\n".join(["# Limitations", "", *[f"- {item}" for item in metrics["limitations"]], ""])


def render_preflight(metrics: dict[str, Any]) -> str:
    preflight = metrics["source_status_preflight"]
    lines = [
        "# Preflight",
        "",
        f"- `source_status_flags`: `{'PASS' if preflight['passed'] else 'FAIL'}` - {preflight['reason']}",
        "- `task_scope`: `PASS` - TASK-0341 requests source-status diagnostics, not reveal scoring.",
        "- `promotion_boundary`: `PASS` - No prediction registry, canonical result, claim, or knowledge file is written.",
        "",
    ]
    return "\n".join(lines)


def render_review_summary(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    lines = [
        "# Review Summary",
        "",
        f"`{summary['lane_verdict']}` for claim promotion: measured/extrapolated boundary diagnostics are deterministic and reviewable, but retrospective fitting and controls keep the lane sandbox-only.",
        "",
        f"- Best full-known delta: `{summary['best_primary_delta_candidate_id']}` ({_format_delta(summary['best_primary_delta_mae_mev'])} MeV MAE).",
        "- No live fetch, prediction-registry write, canonical RESULT artifact, claim update, or knowledge update.",
        "",
    ]
    return "\n".join(lines)


def render_agent_run(metrics: dict[str, Any]) -> str:
    preflight = metrics["source_status_preflight"]
    payload = {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "task_id": TASK_ID,
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {"contributor_id": "master", "agent_id": "codex"},
        "proposal_paths": {
            "hypothesis": "hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0048-extrapolated-measured-boundary-scout-batch.yaml",
            "experiment": "experiment_proposals/nuclear-mass/EXP-PROPOSAL-0014-nuclear-boundary-scout.yaml",
        },
        "artifacts": {
            "metrics": f"agent_runs/{AGENT_RUN_ID}/metrics.json",
            "report": f"agent_runs/{AGENT_RUN_ID}/report.md",
            "limitations": f"agent_runs/{AGENT_RUN_ID}/limitations.md",
            "preflight": f"agent_runs/{AGENT_RUN_ID}/preflight.md",
            "review_summary": f"agent_runs/{AGENT_RUN_ID}/review_summary.md",
        },
        "preflight": {
            "passed": bool(preflight["passed"]),
            "checks": [
                {
                    "name": "source_status_flags",
                    "status": "PASS" if preflight["passed"] else "FAIL",
                    "notes": preflight["reason"],
                },
                {
                    "name": "task_scope",
                    "status": "PASS",
                    "notes": "TASK-0341 requests source-status boundary diagnostics, not reveal scoring.",
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No prediction registry, canonical result, claim, or knowledge file is written.",
                },
            ],
        },
        "limitations": metrics["limitations"],
        "verdict": "INCONCLUSIVE",
        "promotion_boundary": metrics["promotion_boundary"],
    }
    return yaml.safe_dump(payload, sort_keys=False)


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
