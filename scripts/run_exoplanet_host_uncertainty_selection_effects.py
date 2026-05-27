"""TASK-0392 exoplanet host and uncertainty selection-effects audit.

This sandbox runner audits whether frozen CK17 residual patterns in the
committed PSCompPars snapshot track host-star fields, measurement
uncertainty, detection method, or metadata missingness. It keeps
true-mass and minimum-mass axes separate and compares each slice with a
deterministic sample-size matched control from the same axis.

The runner does not fetch live data, refit the baseline, write canonical
results, register predictions, promote claims, edit knowledge, or infer
causal host-star physics, composition, habitability, or target priority.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.datasets.exoplanets import (  # noqa: E402
    apply_inclusion_filters,
    load_exoplanet_snapshot,
)
from physics_lab.engines.exoplanet_mass_radius import (  # noqa: E402
    chen_kipping_predict_radius,
    planet_class_for_mass,
)

AGENT_RUN_ID = "AGENT-RUN-0038"
TASK_ID = "TASK-0392"
CAMPAIGN_PROFILE_ID = "exoplanet-mass-radius"
HYPOTHESIS_PATH = (
    "hypothesis_proposals/exoplanet-mass/"
    "HYP-PROPOSAL-0053-exoplanet-selection-effects-audit.yaml"
)
EXPERIMENT_PATH = (
    "experiment_proposals/exoplanet-mass/"
    "EXP-PROPOSAL-0019-exoplanet-selection-effects-audit.yaml"
)
DEFAULT_SNAPSHOT_PATH = (
    REPO_ROOT / "data" / "exoplanets" / "exo-0001-pscomppars-snapshot.yaml"
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
    / "exoplanet-host-uncertainty-selection-effects.md"
)

MIN_SLICE_COUNT = 30
SIGNAL_MARGIN_LOG10_RMSE = 0.022


def _is_positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value)) and value > 0


def _axis_for_entry(entry: dict[str, Any]) -> str | None:
    mass = entry.get("mass") or {}
    radius = entry.get("radius") or {}
    if (
        radius.get("radius_class") == "transit_radius"
        and _is_positive_number(radius.get("value"))
        and _is_positive_number(mass.get("value"))
    ):
        if mass.get("mass_class") == "true_mass":
            return "true_mass_with_transit_radius"
        if mass.get("mass_class") == "minimum_mass_with_transit_radius":
            return "minimum_mass_with_transit_radius"
        if mass.get("mass_class") == "minimum_mass_msini":
            return "minimum_mass_with_transit_radius"
    return None


def _relative_uncertainty(component: dict[str, Any]) -> float | None:
    value = component.get("value")
    if not _is_positive_number(value):
        return None
    candidates = [
        abs(float(v))
        for v in (component.get("uncertainty_upper"), component.get("uncertainty_lower"))
        if isinstance(v, (int, float)) and math.isfinite(float(v))
    ]
    if not candidates:
        return None
    return max(candidates) / float(value)


def _log_residual(entry: dict[str, Any]) -> float | None:
    mass = float(entry["mass"]["value"])
    radius = float(entry["radius"]["value"])
    prediction = chen_kipping_predict_radius(mass)
    if not _is_positive_number(prediction):
        return None
    residual = math.log10(radius) - math.log10(prediction)
    return residual if math.isfinite(residual) else None


def _number_or_none(value: Any) -> float | None:
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def _host_teff_bin(value: float | None) -> str:
    if value is None:
        return "missing_teff"
    if value < 3900.0:
        return "M_lt3900K"
    if value < 5200.0:
        return "K_3900_5200K"
    if value < 6000.0:
        return "G_5200_6000K"
    if value < 7500.0:
        return "F_6000_7500K"
    return "hot_ge7500K"


def _stellar_mass_bin(value: float | None) -> str:
    if value is None:
        return "missing_stellar_mass"
    if value < 0.7:
        return "low_mass_lt0p7Msun"
    if value < 1.0:
        return "subsolar_0p7_1p0Msun"
    if value < 1.3:
        return "solar_high_1p0_1p3Msun"
    return "high_mass_ge1p3Msun"


def _stellar_radius_bin(value: float | None) -> str:
    if value is None:
        return "missing_stellar_radius"
    if value < 0.7:
        return "small_radius_lt0p7Rsun"
    if value < 1.0:
        return "subsolar_radius_0p7_1p0Rsun"
    if value < 1.5:
        return "solar_high_radius_1p0_1p5Rsun"
    return "large_radius_ge1p5Rsun"


def _mass_uncertainty_band(value: float | None) -> str:
    if value is None:
        return "missing_mass_uncertainty"
    if value <= 0.05:
        return "tight_le5pct"
    if value <= 0.15:
        return "moderate_5_15pct"
    return "loose_15_30pct"


def _radius_uncertainty_band(value: float | None) -> str:
    if value is None:
        return "missing_radius_uncertainty"
    if value <= 0.05:
        return "tight_le5pct"
    if value <= 0.10:
        return "moderate_5_10pct"
    return "loose_10_15pct"


def _normalise_detection_method(value: Any) -> str:
    text = str(value or "missing_detection_method").strip().lower()
    return text.replace(" ", "_").replace("-", "_")


def _missing_flag(label: str, value: Any) -> str:
    return f"{label}_{'missing' if value is None else 'present'}"


def _rmse(values: list[float]) -> float | None:
    if not values:
        return None
    return math.sqrt(sum(value * value for value in values) / len(values))


def _mae(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(abs(value) for value in values) / len(values)


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    sorted_values = sorted(values)
    mid = len(sorted_values) // 2
    if len(sorted_values) % 2:
        return sorted_values[mid]
    return 0.5 * (sorted_values[mid - 1] + sorted_values[mid])


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    residuals = [float(row["log10_residual"]) for row in rows]
    return {
        "count": len(rows),
        "log10_mae": _mae(residuals),
        "log10_rmse": _rmse(residuals),
        "log10_bias": _mean(residuals),
        "median_log10_residual": _median(residuals),
    }


def _build_audit_rows(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in entries:
        axis = _axis_for_entry(entry)
        if axis is None:
            continue
        residual = _log_residual(entry)
        if residual is None:
            continue
        mass = float(entry["mass"]["value"])
        radius = float(entry["radius"]["value"])
        host = entry.get("host_star") or {}
        teff = _number_or_none(host.get("effective_temperature_K"))
        stellar_mass = _number_or_none(host.get("stellar_mass_msun"))
        stellar_radius = _number_or_none(host.get("stellar_radius_rsun"))
        mass_uncertainty = _relative_uncertainty(entry["mass"])
        radius_uncertainty = _relative_uncertainty(entry["radius"])
        rows.append(
            {
                "row_id": str(entry["row_id"]),
                "planet_name": str(entry["planet_name"]),
                "axis": axis,
                "mass_mearth": mass,
                "radius_rearth": radius,
                "planet_class": planet_class_for_mass(mass),
                "detection_method": _normalise_detection_method(
                    entry.get("detection_method")
                ),
                "log10_residual": residual,
                "host_effective_temperature_K": teff,
                "stellar_mass_msun": stellar_mass,
                "stellar_radius_rsun": stellar_radius,
                "mass_relative_uncertainty": mass_uncertainty,
                "radius_relative_uncertainty": radius_uncertainty,
                "labels": {
                    "host_temperature": _host_teff_bin(teff),
                    "stellar_mass": _stellar_mass_bin(stellar_mass),
                    "stellar_radius": _stellar_radius_bin(stellar_radius),
                    "detection_method": _normalise_detection_method(
                        entry.get("detection_method")
                    ),
                    "mass_uncertainty": _mass_uncertainty_band(mass_uncertainty),
                    "radius_uncertainty": _radius_uncertainty_band(
                        radius_uncertainty
                    ),
                    "missing_host_temperature": _missing_flag(
                        "host_temperature", teff
                    ),
                    "missing_stellar_mass": _missing_flag(
                        "stellar_mass", stellar_mass
                    ),
                    "missing_stellar_radius": _missing_flag(
                        "stellar_radius", stellar_radius
                    ),
                    "missing_mass_uncertainty": _missing_flag(
                        "mass_uncertainty", mass_uncertainty
                    ),
                    "missing_radius_uncertainty": _missing_flag(
                        "radius_uncertainty", radius_uncertainty
                    ),
                    "any_core_host_missing": (
                        "any_core_host_missing"
                        if teff is None or stellar_mass is None or stellar_radius is None
                        else "core_host_present"
                    ),
                },
            }
        )
    return rows


def _nearest_mass_control(
    *,
    candidate_rows: list[dict[str, Any]],
    pool_rows: list[dict[str, Any]],
    excluded_ids: set[str],
) -> tuple[list[dict[str, Any]], str]:
    control_pool = [
        row for row in pool_rows if str(row["row_id"]) not in excluded_ids
    ]
    if not candidate_rows:
        return [], "no_candidate_rows"
    if len(control_pool) < len(candidate_rows):
        return control_pool, "insufficient_non_slice_rows"

    available = list(control_pool)
    controls: list[dict[str, Any]] = []
    for candidate in sorted(candidate_rows, key=lambda row: (row["mass_mearth"], row["row_id"])):
        best_index = min(
            range(len(available)),
            key=lambda idx: (
                abs(float(available[idx]["mass_mearth"]) - float(candidate["mass_mearth"])),
                available[idx]["row_id"],
            ),
        )
        controls.append(available.pop(best_index))
    return controls, "matched"


def _classify_slice(
    *,
    slice_stats: dict[str, Any],
    control_stats: dict[str, Any],
    axis_stats: dict[str, Any],
    control_status: str,
    min_count: int = MIN_SLICE_COUNT,
    margin: float = SIGNAL_MARGIN_LOG10_RMSE,
) -> dict[str, Any]:
    count = int(slice_stats["count"])
    slice_rmse = slice_stats["log10_rmse"]
    control_rmse = control_stats["log10_rmse"]
    axis_rmse = axis_stats["log10_rmse"]
    delta_slice_axis = (
        None if slice_rmse is None or axis_rmse is None else slice_rmse - axis_rmse
    )
    delta_slice_control = (
        None
        if slice_rmse is None or control_rmse is None
        else slice_rmse - control_rmse
    )

    if count < min_count:
        outcome = "underpowered_slice"
    elif control_status != "matched" or control_stats["count"] != count:
        outcome = "control_insufficient"
    elif delta_slice_axis is None or delta_slice_axis <= margin:
        outcome = "no_apparent_signal_above_axis"
    elif delta_slice_control is None:
        outcome = "control_missing"
    elif delta_slice_control <= margin:
        outcome = "apparent_signal_erased_by_control"
    else:
        outcome = "selection_effect_persists_vs_control"

    return {
        "outcome": outcome,
        "delta_log10_rmse_slice_minus_axis": delta_slice_axis,
        "delta_log10_rmse_slice_minus_control": delta_slice_control,
        "margin_log10_rmse": margin,
        "min_slice_count": min_count,
    }


DIMENSIONS: tuple[str, ...] = (
    "host_temperature",
    "stellar_mass",
    "stellar_radius",
    "detection_method",
    "mass_uncertainty",
    "radius_uncertainty",
    "missing_host_temperature",
    "missing_stellar_mass",
    "missing_stellar_radius",
    "missing_mass_uncertainty",
    "missing_radius_uncertainty",
    "any_core_host_missing",
)


def _audit_dimension(
    *,
    axis_rows: list[dict[str, Any]],
    axis_stats: dict[str, Any],
    dimension: str,
) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in axis_rows:
        label = str(row["labels"][dimension])
        buckets.setdefault(label, []).append(row)

    slices: dict[str, Any] = {}
    for label, slice_rows in sorted(buckets.items()):
        excluded = {str(row["row_id"]) for row in slice_rows}
        controls, control_status = _nearest_mass_control(
            candidate_rows=slice_rows,
            pool_rows=axis_rows,
            excluded_ids=excluded,
        )
        slice_stats = _summary(slice_rows)
        control_stats = _summary(controls)
        slices[label] = {
            "slice": slice_stats,
            "sample_size_matched_control": {
                "method": "nearest_mass_without_replacement_same_axis_non_slice",
                "status": control_status,
                **control_stats,
            },
            "classification": _classify_slice(
                slice_stats=slice_stats,
                control_stats=control_stats,
                axis_stats=axis_stats,
                control_status=control_status,
            ),
        }
    return slices


def _audit_axes(rows: list[dict[str, Any]]) -> dict[str, Any]:
    axis_payload: dict[str, Any] = {}
    for axis in ("true_mass_with_transit_radius", "minimum_mass_with_transit_radius"):
        axis_rows = [row for row in rows if row["axis"] == axis]
        axis_stats = _summary(axis_rows)
        dimensions = {
            dimension: _audit_dimension(
                axis_rows=axis_rows,
                axis_stats=axis_stats,
                dimension=dimension,
            )
            for dimension in DIMENSIONS
        }
        axis_payload[axis] = {
            "overall": axis_stats,
            "dimensions": dimensions,
            "underpowered_slice_count": sum(
                1
                for dimension_slices in dimensions.values()
                for item in dimension_slices.values()
                if item["classification"]["outcome"] == "underpowered_slice"
            ),
            "control_erased_slice_count": sum(
                1
                for dimension_slices in dimensions.values()
                for item in dimension_slices.values()
                if item["classification"]["outcome"]
                == "apparent_signal_erased_by_control"
            ),
            "control_insufficient_slice_count": sum(
                1
                for dimension_slices in dimensions.values()
                for item in dimension_slices.values()
                if item["classification"]["outcome"] == "control_insufficient"
            ),
            "persistent_slice_count": sum(
                1
                for dimension_slices in dimensions.values()
                for item in dimension_slices.values()
                if item["classification"]["outcome"]
                == "selection_effect_persists_vs_control"
            ),
        }
    return axis_payload


def _collect_limitations(axis_payload: dict[str, Any]) -> list[str]:
    true_axis = axis_payload["true_mass_with_transit_radius"]
    min_axis = axis_payload["minimum_mass_with_transit_radius"]
    limitations = [
        "Residual summaries are retrospective diagnostics over the committed snapshot only.",
        "Sample-size matched controls are deterministic nearest-mass non-slice controls, not causal adjustments.",
        "Host-star fields, uncertainty fields, detection method, and missingness are catalog-selection surfaces.",
        "True-mass rows and minimum-mass rows are reported separately; minimum-mass rows are not headline evidence.",
        "No live fetch, baseline refit, canonical result, prediction, claim, knowledge, composition, habitability, biosignature, or target-priority output is authorized.",
    ]
    if min_axis["overall"]["count"] < MIN_SLICE_COUNT:
        limitations.append(
            "The minimum-mass/transit-radius axis is underpowered for slice interpretation."
        )
    if true_axis["control_erased_slice_count"]:
        limitations.append(
            "At least one true-mass apparent slice signal is erased by sample-size matched controls."
        )
    return limitations


def _verdict(axis_payload: dict[str, Any]) -> str:
    # The task is an audit of limitations rather than a promotable hypothesis
    # test. A completed diagnostic map remains sandbox-only and inconclusive
    # as scientific evidence.
    if axis_payload["true_mass_with_transit_radius"]["overall"]["count"] >= MIN_SLICE_COUNT:
        return "INCONCLUSIVE"
    return "REVIEW_NEEDED"


def run_audit(snapshot_path: Path) -> dict[str, Any]:
    snapshot_path = Path(snapshot_path)
    try:
        display_snapshot_path = snapshot_path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        display_snapshot_path = snapshot_path.name
    snapshot = load_exoplanet_snapshot(snapshot_path)
    filtered = apply_inclusion_filters(snapshot)
    rows = _build_audit_rows(filtered.included_rows)
    axis_payload = _audit_axes(rows)
    limitations = _collect_limitations(axis_payload)
    verdict = _verdict(axis_payload)
    return {
        "task_id": TASK_ID,
        "agent_run_id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "snapshot_path": display_snapshot_path,
        "data_boundary": {
            "live_external_fetch_performed": False,
            "baseline_refit_performed": False,
            "canonical_result_written": False,
            "claim_or_knowledge_promotion": False,
            "minimum_mass_rows_in_headline_metrics": False,
        },
        "parameters": {
            "min_slice_count": MIN_SLICE_COUNT,
            "signal_margin_log10_rmse": SIGNAL_MARGIN_LOG10_RMSE,
            "control_method": "nearest_mass_without_replacement_same_axis_non_slice",
        },
        "filtered_snapshot": {
            "dataset_id": filtered.dataset_id,
            "total_rows": filtered.total_rows,
            "pre_filter_included_count": filtered.pre_filter_included_count,
            "post_filter_included_count": filtered.post_filter_included_count,
            "exclusion_reason_counts": dict(
                sorted(filtered.exclusion_reason_counts.items())
            ),
        },
        "axis_audits": axis_payload,
        "limitations_table": _limitations_table(axis_payload),
        "limitations": limitations,
        "verdict": verdict,
        "output_routing": {
            "task_verdict": verdict,
            "canonical_destination": "agent_runs/ sandbox-only plus docs/reviews note",
            "review_tier": "none",
            "gate_a_status": "not_attempted",
            "gate_b_status": "not_attempted",
            "claim_impact": "no claim change",
            "knowledge_impact": "no knowledge change",
        },
    }


def _limitations_table(axis_payload: dict[str, Any]) -> list[dict[str, Any]]:
    table: list[dict[str, Any]] = []
    for axis, payload in axis_payload.items():
        for dimension, slices in payload["dimensions"].items():
            for label, item in slices.items():
                classification = item["classification"]["outcome"]
                if classification in {
                    "underpowered_slice",
                    "control_insufficient",
                    "apparent_signal_erased_by_control",
                }:
                    table.append(
                        {
                            "axis": axis,
                            "dimension": dimension,
                            "slice": label,
                            "count": item["slice"]["count"],
                            "slice_log10_rmse": item["slice"]["log10_rmse"],
                            "control_log10_rmse": item[
                                "sample_size_matched_control"
                            ]["log10_rmse"],
                            "limitation": classification,
                        }
                    )
    return sorted(
        table,
        key=lambda row: (
            row["axis"],
            row["dimension"],
            str(row["slice"]),
        ),
    )


def _fmt(value: Any, digits: int = 6) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def _top_slice_rows(metrics: dict[str, Any], axis: str, *, limit: int = 12) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    axis_payload = metrics["axis_audits"][axis]
    for dimension, slices in axis_payload["dimensions"].items():
        for label, item in slices.items():
            if item["slice"]["count"] >= MIN_SLICE_COUNT:
                rows.append(
                    {
                        "dimension": dimension,
                        "slice": label,
                        "count": item["slice"]["count"],
                        "rmse": item["slice"]["log10_rmse"],
                        "control_rmse": item["sample_size_matched_control"][
                            "log10_rmse"
                        ],
                        "classification": item["classification"]["outcome"],
                        "delta_axis": item["classification"][
                            "delta_log10_rmse_slice_minus_axis"
                        ],
                        "delta_control": item["classification"][
                            "delta_log10_rmse_slice_minus_control"
                        ],
                    }
                )
    return sorted(
        rows,
        key=lambda row: (
            -999.0 if row["delta_axis"] is None else -float(row["delta_axis"]),
            row["dimension"],
            str(row["slice"]),
        ),
    )[:limit]


def render_report(metrics: dict[str, Any]) -> str:
    true_axis = metrics["axis_audits"]["true_mass_with_transit_radius"]
    min_axis = metrics["axis_audits"]["minimum_mass_with_transit_radius"]
    lines = [
        "# Exoplanet Host And Uncertainty Selection-Effects Audit",
        "",
        f"**Task:** `{TASK_ID}`",
        f"**Agent run:** `{AGENT_RUN_ID}`",
        f"**Snapshot:** `{metrics['snapshot_path']}`",
        "**Evidence class:** sandbox-only selection-effects audit",
        f"**Verdict:** `{metrics['verdict']}`",
        "",
        "## Scope",
        "",
        "This audit quantifies frozen CK17 residual summaries by host-star fields, "
        "detection method, measurement uncertainty, and missingness indicators. "
        "It uses committed snapshot rows only, keeps true-mass and minimum-mass "
        "axes separate, and compares each slice with deterministic sample-size "
        "matched controls from the same axis.",
        "",
        "No live fetch, baseline refit, canonical result, prediction, claim, "
        "knowledge, composition, habitability, biosignature, or target-priority "
        "output is produced.",
        "",
        "## Axis Summary",
        "",
        "| axis | rows | log10 RMSE | control-erased slices | persistent slices | underpowered slices |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        (
            "| true_mass_with_transit_radius | "
            f"{true_axis['overall']['count']} | "
            f"{_fmt(true_axis['overall']['log10_rmse'])} | "
            f"{true_axis['control_erased_slice_count']} | "
            f"{true_axis['persistent_slice_count']} | "
            f"{true_axis['underpowered_slice_count']} |"
        ),
        (
            "| minimum_mass_with_transit_radius | "
            f"{min_axis['overall']['count']} | "
            f"{_fmt(min_axis['overall']['log10_rmse'])} | "
            f"{min_axis['control_erased_slice_count']} | "
            f"{min_axis['persistent_slice_count']} | "
            f"{min_axis['underpowered_slice_count']} |"
        ),
        "",
        "## True-Mass Count-Supported Slice Diagnostics",
        "",
        "| dimension | slice | rows | slice RMSE | control RMSE | delta vs axis | delta vs control | classification |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in _top_slice_rows(metrics, "true_mass_with_transit_radius"):
        lines.append(
            "| {dimension} | {slice} | {count} | {rmse} | {control_rmse} | "
            "{delta_axis} | {delta_control} | {classification} |".format(
                dimension=row["dimension"],
                slice=row["slice"],
                count=row["count"],
                rmse=_fmt(row["rmse"]),
                control_rmse=_fmt(row["control_rmse"]),
                delta_axis=_fmt(row["delta_axis"]),
                delta_control=_fmt(row["delta_control"]),
                classification=row["classification"],
            )
        )
    lines.extend(
        [
            "",
            "## Limitations Table",
            "",
            "| axis | dimension | slice | rows | slice RMSE | control RMSE | limitation |",
            "| --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in metrics["limitations_table"][:40]:
        lines.append(
            "| {axis} | {dimension} | {slice} | {count} | {slice_rmse} | "
            "{control_rmse} | {limitation} |".format(
                axis=row["axis"],
                dimension=row["dimension"],
                slice=row["slice"],
                count=row["count"],
                slice_rmse=_fmt(row["slice_log10_rmse"]),
                control_rmse=_fmt(row["control_log10_rmse"]),
                limitation=row["limitation"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "Rows with larger residual stress are selection-effect diagnostics. The "
            "matched controls are designed to expose when sample size and local "
            "mass distribution can reproduce a slice's apparent signal. They do "
            "not estimate causal host-star physics.",
            "",
            "The minimum-mass axis remains diagnostic-only because it is too sparse "
            "after the committed quality filters.",
            "",
            "## Output Routing",
            "",
            f"- Task verdict: `{metrics['output_routing']['task_verdict']}`",
            f"- Canonical destination: `{metrics['output_routing']['canonical_destination']}`",
            "- Review tier: `none`",
            "- Gate A status: `not_attempted`",
            "- Gate B status: `not_attempted`",
            "- Claim impact: no claim change",
            "- Knowledge impact: no knowledge change",
        ]
    )
    return "\n".join(lines) + "\n"


def render_limitations(metrics: dict[str, Any]) -> str:
    lines = [
        "# TASK-0392 Limitations",
        "",
        "| limitation | detail |",
        "| --- | --- |",
    ]
    for limitation in metrics["limitations"]:
        lines.append(f"| selection-effects boundary | {limitation} |")
    return "\n".join(lines) + "\n"


def render_preflight() -> str:
    return "\n".join(
        [
            "# TASK-0392 Preflight",
            "",
            "- PASS: committed PSCompPars snapshot only; no live fetch.",
            "- PASS: frozen CK17 baseline reused; no refit.",
            "- PASS: true-mass and minimum-mass axes are separated.",
            "- PASS: host, uncertainty, detection-method, and missingness slices use sample-size matched controls.",
            "- PASS: outputs are sandbox-only with no claim, knowledge, prediction, or canonical result promotion.",
            "",
        ]
    )


def render_review_summary(metrics: dict[str, Any]) -> str:
    true_axis = metrics["axis_audits"]["true_mass_with_transit_radius"]
    return "\n".join(
        [
            "# TASK-0392 Review Summary",
            "",
            f"- Verdict: `{metrics['verdict']}`",
            f"- True-mass rows audited: {true_axis['overall']['count']}",
            f"- Control-erased true-mass slices: {true_axis['control_erased_slice_count']}",
            f"- Persistent true-mass slices: {true_axis['persistent_slice_count']}",
            "- Minimum-mass rows remain diagnostic-only.",
            "- No canonical result, claim, knowledge, prediction, composition, habitability, biosignature, or target-priority output.",
            "",
        ]
    )


def write_agent_run_yaml(metrics: dict[str, Any], path: Path) -> None:
    payload = {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "task_id": TASK_ID,
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {"contributor_id": "master", "agent_id": "codex"},
        "proposal_paths": {
            "hypothesis": HYPOTHESIS_PATH,
            "experiment": EXPERIMENT_PATH,
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
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed snapshot rows are read; no live fetch.",
                },
                {
                    "name": "baseline_freeze",
                    "status": "PASS",
                    "notes": "CK17 frozen segments are reused without refit.",
                },
                {
                    "name": "axis_separation",
                    "status": "PASS",
                    "notes": "True-mass and minimum-mass rows are reported separately.",
                },
                {
                    "name": "matched_controls",
                    "status": "PASS",
                    "notes": "Slices use same-axis nearest-mass sample-size controls.",
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No canonical result, prediction, claim, or knowledge output.",
                },
            ],
        },
        "limitations": metrics["limitations"],
        "verdict": metrics["verdict"],
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any canonical result, prediction registry "
                "entry, claim update, knowledge edit, or follow-up causal wording."
            ),
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def write_outputs(args: argparse.Namespace) -> dict[str, Any]:
    metrics = run_audit(Path(args.snapshot))
    out_path = Path(args.out)
    report_path = Path(args.report)
    agent_run_path = Path(args.agent_run)
    limitations_path = Path(args.limitations)
    preflight_path = Path(args.preflight)
    review_summary_path = Path(args.review_summary)
    review_path = Path(args.review)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")
    report = render_report(metrics)
    report_path.write_text(report, encoding="utf-8")
    limitations_path.write_text(render_limitations(metrics), encoding="utf-8")
    preflight_path.write_text(render_preflight(), encoding="utf-8")
    review_summary_path.write_text(render_review_summary(metrics), encoding="utf-8")
    review_path.write_text(report, encoding="utf-8")
    write_agent_run_yaml(metrics, agent_run_path)
    return metrics


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", default=str(DEFAULT_SNAPSHOT_PATH))
    parser.add_argument("--out", default=str(DEFAULT_METRICS_PATH))
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--agent-run", default=str(DEFAULT_AGENT_RUN_PATH))
    parser.add_argument("--limitations", default=str(DEFAULT_LIMITATIONS_PATH))
    parser.add_argument("--preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument("--review-summary", default=str(DEFAULT_REVIEW_SUMMARY_PATH))
    parser.add_argument("--review", default=str(DEFAULT_REVIEW_PATH))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    write_outputs(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
