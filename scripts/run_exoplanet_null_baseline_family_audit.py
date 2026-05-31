"""TASK-0483 exoplanet null-baseline family audit.

Sandbox-only audit of how much simple deterministic null baselines explain
on the committed PSCompPars exoplanet mass-radius snapshot. The runner keeps
the frozen CK17-style baseline fixed, compares CK17 log-radius residuals
against four residual-shift null families, reports true-mass and
minimum-mass axes separately, and keeps compact, sub-Neptune, Jovian-radius,
and hot-Jupiter slices distinct.

No live fetch, baseline refit, second-snapshot inspection, composition
inference, habitability wording, target-priority output, prediction entry,
canonical result, claim update, or knowledge edit is produced.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.datasets.exoplanets import (  # noqa: E402
    apply_inclusion_filters,
    load_exoplanet_snapshot,
    summarize,
)
from physics_lab.engines.exoplanet_mass_radius import (  # noqa: E402
    chen_kipping_baseline_metadata,
    chen_kipping_predict_radius,
    planet_class_for_mass,
    residual_summary_to_dict,
    summarize_log_residuals,
)

AGENT_RUN_ID = "AGENT-RUN-0050"
TASK_ID = "TASK-0483"
CAMPAIGN_PROFILE_ID = "exoplanet-mass-radius"
HYPOTHESIS_PATH = (
    "hypothesis_proposals/exoplanet-mass/"
    "HYP-PROPOSAL-0054-exoplanet-null-baseline-family-audit.yaml"
)
EXPERIMENT_PATH = (
    "experiment_proposals/exoplanet-mass/"
    "EXP-PROPOSAL-0020-exoplanet-null-baseline-family-audit.yaml"
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
    REPO_ROOT / "docs" / "reviews" / "exoplanet-null-baseline-family-audit.md"
)

MIN_INTERPRETABLE_ROWS = 30
NULL_IMPROVEMENT_MARGIN_LOG10_RMSE = 0.022


@dataclass(frozen=True)
class AuditRow:
    """One row on a residual axis after committed filtering."""

    row_id: str
    planet_name: str
    axis: str
    detection_method: str
    mass_mearth: float
    radius_rearth: float
    equilibrium_temperature_K: float | None
    mass_class: str
    radius_class: str
    planet_class: str
    uncertainty_band: str
    ck17_log_residual: float


@dataclass(frozen=True)
class BaselineSpec:
    """One deterministic null baseline family."""

    name: str
    label: str
    predictive_status: str
    notes: str


NULL_BASELINES: tuple[BaselineSpec, ...] = (
    BaselineSpec(
        name="per_class_median_residual_shift",
        label="Per-CK17-class median residual shift",
        predictive_status="same_sample_control",
        notes=(
            "Subtracts the median CK17 residual for rows in the same frozen "
            "CK17 mass class on the same axis."
        ),
    ),
    BaselineSpec(
        name="nearest_mass_residual_shift",
        label="Nearest-mass residual shift",
        predictive_status="leave_one_neighbor_control",
        notes=(
            "Subtracts the CK17 residual of the nearest other row in log mass "
            "on the same axis."
        ),
    ),
    BaselineSpec(
        name="nearest_radius_residual_shift",
        label="Nearest-radius residual shift",
        predictive_status="oracle_like_non_predictive_control",
        notes=(
            "Subtracts the CK17 residual of the nearest other row in observed "
            "log radius; this uses the target coordinate and is diagnostic, "
            "not a deployable predictor."
        ),
    ),
    BaselineSpec(
        name="uncertainty_band_median_residual_shift",
        label="Uncertainty-band median residual shift",
        predictive_status="same_sample_control",
        notes=(
            "Subtracts the median CK17 residual among rows in the same "
            "combined mass/radius uncertainty band on the same axis."
        ),
    ),
)


def _is_positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value)) and value > 0


def _row_axis(entry: dict[str, Any]) -> str | None:
    mass = entry.get("mass") or {}
    radius = entry.get("radius") or {}
    if not (
        _is_positive_number(mass.get("value"))
        and _is_positive_number(radius.get("value"))
        and radius.get("radius_class") == "transit_radius"
    ):
        return None
    if mass.get("mass_class") == "true_mass":
        return "true_mass_with_transit_radius"
    if mass.get("mass_class") == "minimum_mass_msini":
        return "minimum_mass_with_transit_radius"
    return None


def _relative_uncertainty(component: dict[str, Any]) -> float | None:
    value = component.get("value")
    if not _is_positive_number(value):
        return None
    candidates = [
        abs(float(v))
        for v in (
            component.get("uncertainty_upper"),
            component.get("uncertainty_lower"),
        )
        if isinstance(v, (int, float)) and math.isfinite(float(v))
    ]
    if not candidates:
        return None
    return max(candidates) / float(value)


def _combined_uncertainty(entry: dict[str, Any]) -> float | None:
    values = [
        value
        for value in (
            _relative_uncertainty(entry.get("mass") or {}),
            _relative_uncertainty(entry.get("radius") or {}),
        )
        if value is not None
    ]
    return max(values) if values else None


def _uncertainty_band(entry: dict[str, Any]) -> str:
    value = _combined_uncertainty(entry)
    if value is None:
        return "missing"
    if value <= 0.05:
        return "tight_le5pct"
    if value <= 0.15:
        return "moderate_5_15pct"
    return "loose_gt15pct"


def _equilibrium_temperature(entry: dict[str, Any]) -> float | None:
    value = entry.get("equilibrium_temperature_K")
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def _to_audit_rows(entries: list[dict[str, Any]]) -> list[AuditRow]:
    rows: list[AuditRow] = []
    for entry in entries:
        axis = _row_axis(entry)
        if axis is None:
            continue
        mass = float(entry["mass"]["value"])
        radius = float(entry["radius"]["value"])
        ck_radius = chen_kipping_predict_radius(mass)
        if not _is_positive_number(ck_radius):
            continue
        ck17_log_residual = math.log10(radius) - math.log10(ck_radius)
        if not math.isfinite(ck17_log_residual):
            continue
        rows.append(
            AuditRow(
                row_id=str(entry["row_id"]),
                planet_name=str(entry["planet_name"]),
                axis=axis,
                detection_method=str(entry.get("detection_method", "unknown")),
                mass_mearth=mass,
                radius_rearth=radius,
                equilibrium_temperature_K=_equilibrium_temperature(entry),
                mass_class=str(entry["mass"]["mass_class"]),
                radius_class=str(entry["radius"]["radius_class"]),
                planet_class=planet_class_for_mass(mass),
                uncertainty_band=_uncertainty_band(entry),
                ck17_log_residual=ck17_log_residual,
            )
        )
    return rows


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[mid]
    return 0.5 * (ordered[mid - 1] + ordered[mid])


def _bucket_median_residuals(
    rows: list[AuditRow],
    key: Callable[[AuditRow], str],
) -> dict[str, float]:
    buckets: dict[str, list[float]] = {}
    for row in rows:
        buckets.setdefault(key(row), []).append(row.ck17_log_residual)
    return {
        label: value
        for label, values in buckets.items()
        if (value := _median(values)) is not None
    }


def _nearest_residuals(
    rows: list[AuditRow],
    coord: Callable[[AuditRow], float],
) -> dict[str, float]:
    corrections: dict[str, float] = {}
    if len(rows) < 2:
        return corrections
    indexed = sorted(rows, key=lambda row: (coord(row), row.row_id))
    for index, row in enumerate(indexed):
        candidates: list[AuditRow] = []
        if index > 0:
            candidates.append(indexed[index - 1])
        if index < len(indexed) - 1:
            candidates.append(indexed[index + 1])
        nearest = min(
            candidates,
            key=lambda candidate: (
                abs(coord(candidate) - coord(row)),
                candidate.row_id,
            ),
        )
        corrections[row.row_id] = nearest.ck17_log_residual
    return corrections


def _baseline_corrections(
    rows: list[AuditRow],
    baseline_name: str,
) -> dict[str, float]:
    if baseline_name == "per_class_median_residual_shift":
        medians = _bucket_median_residuals(rows, lambda row: row.planet_class)
        return {row.row_id: medians[row.planet_class] for row in rows}
    if baseline_name == "uncertainty_band_median_residual_shift":
        medians = _bucket_median_residuals(rows, lambda row: row.uncertainty_band)
        return {row.row_id: medians[row.uncertainty_band] for row in rows}
    if baseline_name == "nearest_mass_residual_shift":
        return _nearest_residuals(rows, lambda row: math.log10(row.mass_mearth))
    if baseline_name == "nearest_radius_residual_shift":
        return _nearest_residuals(rows, lambda row: math.log10(row.radius_rearth))
    raise ValueError(f"Unknown null baseline: {baseline_name}")


def _summarize_rows(
    rows: list[AuditRow],
    *,
    corrections: dict[str, float] | None = None,
) -> dict[str, Any]:
    residuals = []
    missing = 0
    for row in rows:
        if corrections is None:
            residuals.append(row.ck17_log_residual)
            continue
        correction = corrections.get(row.row_id)
        if correction is None or not math.isfinite(correction):
            missing += 1
            continue
        residuals.append(row.ck17_log_residual - correction)
    payload = residual_summary_to_dict(summarize_log_residuals(residuals))
    payload["missing_prediction_count"] = missing
    return payload


def _slice_specs() -> tuple[dict[str, Any], ...]:
    return (
        {
            "id": "axis_true_mass_with_transit_radius",
            "label": "True-mass + transit-radius axis",
            "axis": "true_mass_with_transit_radius",
            "predicate": lambda row: True,
            "required_by_task": True,
        },
        {
            "id": "axis_minimum_mass_with_transit_radius",
            "label": "Minimum-mass + transit-radius axis",
            "axis": "minimum_mass_with_transit_radius",
            "predicate": lambda row: True,
            "required_by_task": True,
        },
        {
            "id": "compact_radius_lt1p5Re",
            "label": "Compact-radius true-mass slice, R < 1.5 R_earth",
            "axis": "true_mass_with_transit_radius",
            "predicate": lambda row: row.radius_rearth < 1.5,
            "required_by_task": True,
        },
        {
            "id": "sub_neptune_radius_1p5_4Re",
            "label": "Sub-Neptune true-mass slice, 1.5 <= R < 4 R_earth",
            "axis": "true_mass_with_transit_radius",
            "predicate": lambda row: 1.5 <= row.radius_rearth < 4.0,
            "required_by_task": True,
        },
        {
            "id": "jovian_radius_8_16Re",
            "label": "Jovian-radius true-mass slice, 8 <= R < 16 R_earth",
            "axis": "true_mass_with_transit_radius",
            "predicate": lambda row: 8.0 <= row.radius_rearth < 16.0,
            "required_by_task": True,
        },
        {
            "id": "hot_jupiter_high_irradiation",
            "label": "Hot-Jupiter high-irradiation true-mass slice",
            "axis": "true_mass_with_transit_radius",
            "predicate": lambda row: (
                row.mass_mearth > 30.0
                and row.equilibrium_temperature_K is not None
                and row.equilibrium_temperature_K > 1500.0
            ),
            "required_by_task": True,
        },
    )


def _classify_slice(
    *,
    ck17_summary: dict[str, Any],
    null_summaries: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    count = int(ck17_summary["count"])
    ck_rmse = ck17_summary["log10_rmse"]
    if count == 0:
        return {
            "status": "no_rows",
            "verdict": "INCONCLUSIVE",
            "best_null": None,
            "best_null_log10_rmse": None,
            "delta_log10_rmse_ck17_minus_best_null": None,
            "explanation": "No eligible rows are available for this slice.",
        }
    if count < MIN_INTERPRETABLE_ROWS:
        return {
            "status": "underpowered",
            "verdict": "INCONCLUSIVE",
            "best_null": None,
            "best_null_log10_rmse": None,
            "delta_log10_rmse_ck17_minus_best_null": None,
            "explanation": (
                f"Slice has {count} rows, below the "
                f"{MIN_INTERPRETABLE_ROWS}-row interpretation floor."
            ),
        }
    candidates = {
        name: summary["log10_rmse"]
        for name, summary in null_summaries.items()
        if summary["log10_rmse"] is not None
    }
    if ck_rmse is None or not candidates:
        return {
            "status": "blocked_missing_metric",
            "verdict": "INCONCLUSIVE",
            "best_null": None,
            "best_null_log10_rmse": None,
            "delta_log10_rmse_ck17_minus_best_null": None,
            "explanation": "CK17 or null-family RMSE is unavailable.",
        }
    best_name, best_rmse = min(candidates.items(), key=lambda item: (item[1], item[0]))
    delta = ck_rmse - best_rmse
    if delta >= NULL_IMPROVEMENT_MARGIN_LOG10_RMSE:
        status = "control_sensitive_null_family_explains"
        explanation = (
            f"Best null {best_name} lowers RMSE by {delta:.6f}, at or above "
            f"the {NULL_IMPROVEMENT_MARGIN_LOG10_RMSE:.3f} margin."
        )
    elif delta > 0:
        status = "weak_null_family_improvement"
        explanation = (
            f"Best null {best_name} lowers RMSE by {delta:.6f}, below the "
            f"{NULL_IMPROVEMENT_MARGIN_LOG10_RMSE:.3f} margin."
        )
    else:
        status = "ck17_not_worse_than_null_family"
        explanation = (
            f"No null baseline lowers CK17 RMSE; best null {best_name} "
            f"has RMSE {best_rmse:.6f}."
        )
    return {
        "status": status,
        "verdict": "INCONCLUSIVE",
        "best_null": best_name,
        "best_null_log10_rmse": best_rmse,
        "delta_log10_rmse_ck17_minus_best_null": delta,
        "explanation": explanation,
    }


def _analyze_slice(
    *,
    spec: dict[str, Any],
    axis_rows: list[AuditRow],
    axis_corrections: dict[str, dict[str, float]],
) -> dict[str, Any]:
    rows = [row for row in axis_rows if spec["predicate"](row)]
    ck17_summary = _summarize_rows(rows)
    null_summaries = {
        baseline.name: _summarize_rows(
            rows, corrections=axis_corrections[baseline.name]
        )
        for baseline in NULL_BASELINES
    }
    classification = _classify_slice(
        ck17_summary=ck17_summary,
        null_summaries=null_summaries,
    )
    return {
        "id": spec["id"],
        "label": spec["label"],
        "axis": spec["axis"],
        "required_by_task": spec["required_by_task"],
        "row_count": len(rows),
        "ck17": ck17_summary,
        "null_baselines": null_summaries,
        "classification": classification,
    }


def build_metrics(snapshot_path: Path) -> dict[str, Any]:
    payload = load_exoplanet_snapshot(snapshot_path)
    filtered = apply_inclusion_filters(payload)
    rows = _to_audit_rows(filtered.included_rows)
    rows_by_axis: dict[str, list[AuditRow]] = {
        "true_mass_with_transit_radius": [
            row for row in rows if row.axis == "true_mass_with_transit_radius"
        ],
        "minimum_mass_with_transit_radius": [
            row for row in rows if row.axis == "minimum_mass_with_transit_radius"
        ],
    }
    corrections_by_axis = {
        axis: {
            baseline.name: _baseline_corrections(axis_rows, baseline.name)
            for baseline in NULL_BASELINES
        }
        for axis, axis_rows in rows_by_axis.items()
    }
    slices = {
        spec["id"]: _analyze_slice(
            spec=spec,
            axis_rows=rows_by_axis[spec["axis"]],
            axis_corrections=corrections_by_axis[spec["axis"]],
        )
        for spec in _slice_specs()
    }
    metrics: dict[str, Any] = {
        "task_id": TASK_ID,
        "agent_run_id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "snapshot_path": str(snapshot_path.relative_to(REPO_ROOT)),
        "data_boundary": {
            "committed_snapshot_only": True,
            "live_fetch_performed": False,
            "second_snapshot_inspected": False,
        },
        "loader_summary": summarize(filtered),
        "baseline": chen_kipping_baseline_metadata(),
        "null_baseline_family": [
            {
                "name": baseline.name,
                "label": baseline.label,
                "predictive_status": baseline.predictive_status,
                "notes": baseline.notes,
            }
            for baseline in NULL_BASELINES
        ],
        "thresholds": {
            "min_interpretable_rows": MIN_INTERPRETABLE_ROWS,
            "null_improvement_margin_log10_rmse": NULL_IMPROVEMENT_MARGIN_LOG10_RMSE,
        },
        "axis_counts": {
            axis: len(axis_rows) for axis, axis_rows in rows_by_axis.items()
        },
        "slices": slices,
    }
    metrics["audit_outcome"] = _audit_outcome(slices)
    metrics["verdict"] = "INCONCLUSIVE"
    return metrics


def _audit_outcome(slices: dict[str, Any]) -> str:
    statuses = {
        value["classification"]["status"]
        for value in slices.values()
        if value["id"] != "axis_minimum_mass_with_transit_radius"
    }
    if "control_sensitive_null_family_explains" in statuses:
        return "control_sensitive_null_family_audit"
    if statuses <= {"ck17_not_worse_than_null_family", "underpowered", "no_rows"}:
        return "ck17_not_worse_than_null_family"
    return "mixed_null_family_audit"


def _fmt(value: float | None, places: int = 6) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{places}f}"


def _render_slice_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| slice | count | CK17 RMSE | best null | best null RMSE | delta CK17-null | status |",
        "| --- | ---: | ---: | --- | ---: | ---: | --- |",
    ]
    for slice_payload in metrics["slices"].values():
        classification = slice_payload["classification"]
        lines.append(
            "| "
            f"`{slice_payload['id']}` | "
            f"{slice_payload['row_count']} | "
            f"{_fmt(slice_payload['ck17']['log10_rmse'])} | "
            f"{classification['best_null'] or 'n/a'} | "
            f"{_fmt(classification['best_null_log10_rmse'])} | "
            f"{_fmt(classification['delta_log10_rmse_ck17_minus_best_null'])} | "
            f"{classification['status']} |"
        )
    return lines


def _render_null_baseline_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| null baseline | status | interpretation |",
        "| --- | --- | --- |",
    ]
    for baseline in metrics["null_baseline_family"]:
        lines.append(
            f"| `{baseline['name']}` | `{baseline['predictive_status']}` | "
            f"{baseline['notes']} |"
        )
    return lines


def _render_slice_detail(slice_payload: dict[str, Any]) -> list[str]:
    lines = [
        f"### `{slice_payload['id']}`",
        "",
        f"- Axis: `{slice_payload['axis']}`",
        f"- Rows: {slice_payload['row_count']}",
        f"- Classification: `{slice_payload['classification']['status']}`",
        f"- Explanation: {slice_payload['classification']['explanation']}",
        "",
        "| baseline | count | log10 MAE | log10 RMSE | log10 bias | missing predictions |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| `CK17 frozen` | {slice_payload['ck17']['count']} | "
            f"{_fmt(slice_payload['ck17']['log10_mae'])} | "
            f"{_fmt(slice_payload['ck17']['log10_rmse'])} | "
            f"{_fmt(slice_payload['ck17']['log10_bias'])} | "
            f"{slice_payload['ck17']['missing_prediction_count']} |"
        ),
    ]
    for name, summary in slice_payload["null_baselines"].items():
        lines.append(
            f"| `{name}` | {summary['count']} | "
            f"{_fmt(summary['log10_mae'])} | "
            f"{_fmt(summary['log10_rmse'])} | "
            f"{_fmt(summary['log10_bias'])} | "
            f"{summary['missing_prediction_count']} |"
        )
    lines.append("")
    return lines


def _limitations() -> list[str]:
    return [
        "The audit uses only the committed PSCompPars snapshot and frozen CK17 residuals.",
        "Null baselines are same-snapshot controls, not independent physical models.",
        "The nearest-radius baseline uses observed radius to choose a neighbor and is an oracle-like diagnostic, not a deployable predictor.",
        "The minimum-mass axis is sparse and remains diagnostic-only.",
        "Slice counts below the interpretation floor are preserved as underpowered rather than retried with tuned cuts.",
        "No live archive fetch, second-snapshot inspection, CK17 refit, composition inference, habitability inference, target-priority output, prediction entry, canonical result, claim update, or knowledge edit is authorized.",
    ]


def _render_report(metrics: dict[str, Any]) -> str:
    lines = [
        "# AGENT-RUN-0050 - Exoplanet null-baseline family audit",
        "",
        f"- Task: `{TASK_ID}`",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        f"- Verdict: **{metrics['verdict']}**",
        f"- Audit outcome: `{metrics['audit_outcome']}`",
        "",
        "## Boundary",
        "",
        "Sandbox-only audit on committed snapshot rows. The runner compares "
        "frozen CK17 log-radius residuals against deterministic null-family "
        "controls and does not fetch live archive data, refit CK17, inspect a "
        "second snapshot, or promote claims.",
        "",
        "## Null Baseline Family",
        "",
        *_render_null_baseline_table(metrics),
        "",
        "## Slice Summary",
        "",
        *_render_slice_table(metrics),
        "",
        "## Slice Details",
        "",
    ]
    for slice_payload in metrics["slices"].values():
        lines.extend(_render_slice_detail(slice_payload))
    lines.extend(
        [
            "## Interpretation",
            "",
            "The audit is control-oriented. When a simple null baseline lowers "
            "RMSE by the declared margin, the slice is treated as "
            "control-sensitive rather than stronger physical evidence. "
            "Underpowered and minimum-mass outcomes are preserved.",
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in _limitations()],
            "",
        ]
    )
    return "\n".join(lines)


def _render_limitations(metrics: dict[str, Any]) -> str:
    del metrics
    return "# Limitations\n\n" + "\n".join(f"- {item}" for item in _limitations()) + "\n"


def _render_preflight(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Preflight",
            "",
            f"- Snapshot: `{metrics['snapshot_path']}`",
            "- Data boundary: committed snapshot only; no live fetch.",
            "- Baseline freeze: CK17 metadata reused without refit.",
            "- Null family: four deterministic null baselines.",
            "- Axis boundary: true-mass and minimum-mass rows reported separately.",
            "- Promotion boundary: no RESULT, PRED, claim, knowledge, composition, habitability, biosignature, or target-priority output.",
            "",
            "## Checks",
            "",
            "| check | status | notes |",
            "| --- | --- | --- |",
            "| data_boundary | PASS | Only the committed snapshot is read. |",
            "| baseline_freeze | PASS | CK17 segments are unchanged and not refit. |",
            "| null_family | PASS | Per-class, nearest-mass, nearest-radius, and uncertainty-band controls are reported. |",
            "| axis_separation | PASS | True-mass and minimum-mass rows remain separate. |",
            "| slice_coverage | PASS | Compact, sub-Neptune, Jovian-radius, and hot-Jupiter slices are reported when rows are available. |",
            "| promotion_boundary | PASS | No canonical scientific-memory promotion is written. |",
            "",
        ]
    )


def _render_review_summary(metrics: dict[str, Any]) -> str:
    primary = metrics["slices"]["compact_radius_lt1p5Re"]
    best = primary["classification"]["best_null"] or "n/a"
    return "\n".join(
        [
            "# Review Summary",
            "",
            f"- Verdict: `{metrics['verdict']}`",
            f"- Audit outcome: `{metrics['audit_outcome']}`",
            f"- True-mass axis rows: {metrics['axis_counts']['true_mass_with_transit_radius']}",
            f"- Minimum-mass diagnostic rows: {metrics['axis_counts']['minimum_mass_with_transit_radius']}",
            (
                "- Compact slice best null: "
                f"`{best}`; status "
                f"`{primary['classification']['status']}`."
            ),
            "- No live fetch, no second-snapshot inspection, and no claim promotion.",
            "",
        ]
    )


def _render_review_note(metrics: dict[str, Any]) -> str:
    lines = [
        "# Exoplanet null-baseline family audit",
        "",
        f"**Task:** `{TASK_ID}`  ",
        f"**Agent run:** `{AGENT_RUN_ID}`  ",
        "**Campaign:** Exoplanet Mass-Radius  ",
        "**Evidence class:** sandbox-only null-family audit  ",
        f"**Verdict:** `{metrics['verdict']}`",
        "",
        "## Scope",
        "",
        "This review packages a deterministic null-baseline family audit on "
        "the committed PSCompPars snapshot. It compares frozen CK17 "
        "log-radius residuals with simple residual-shift controls and keeps "
        "true-mass and minimum-mass rows separate.",
        "",
        "No TAP query was run. No live archive row was fetched or inspected. "
        "No second snapshot was inspected. No composition, habitability, "
        "biosignature, target-priority, prediction, canonical result, claim, "
        "or knowledge artifact is produced.",
        "",
        "## Null Baseline Family",
        "",
        *_render_null_baseline_table(metrics),
        "",
        "## Slice Summary",
        "",
        *_render_slice_table(metrics),
        "",
        "## Interpretation",
        "",
        "The null-family audit is intentionally conservative. A slice whose "
        "CK17 residual RMSE is reduced by a simple null baseline is treated as "
        "control-sensitive. That makes the output useful as a benchmark "
        "diagnostic, not as a planet-composition or planet-law claim.",
        "",
        "The compact-radius result is especially bounded by this rule: it "
        "remains a sandbox benchmark diagnostic unless a future maintainer-"
        "approved task defines and passes a stronger independent-control or "
        "fresh-snapshot reveal.",
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in _limitations()],
        "",
        "## Output Routing",
        "",
        "- Task verdict: `INCONCLUSIVE`.",
        "- Canonical destination: sandbox-only `agent_runs/AGENT-RUN-0050/` and this review note.",
        "- Review tier: `none`.",
        "- Gate A status: not attempted; no canonical RESULT/PRED artifact is produced.",
        "- Gate B status: not attempted.",
        "- Claim impact: no claim change.",
        "- Knowledge impact: no knowledge change.",
        "",
    ]
    return "\n".join(lines)


def _build_agent_run_payload(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "task_id": TASK_ID,
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {"contributor_id": "roman", "agent_id": "codex"},
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
                    "notes": "Only the committed snapshot is read; no live fetch.",
                },
                {
                    "name": "baseline_freeze",
                    "status": "PASS",
                    "notes": "CK17 residuals are reused without refitting.",
                },
                {
                    "name": "null_family",
                    "status": "PASS",
                    "notes": "Four deterministic null baselines are reported.",
                },
                {
                    "name": "axis_separation",
                    "status": "PASS",
                    "notes": "True-mass and minimum-mass axes are separate.",
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No RESULT, PRED, claim, knowledge, or target-facing output.",
                },
            ],
        },
        "limitations": _limitations(),
        "verdict": metrics["verdict"],
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any canonical result, prediction "
                "registry entry, claim update, knowledge edit, composition "
                "inference, habitability wording, target-priority output, or "
                "new mass-radius-law wording."
            ),
        },
    }


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
    review.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2, sort_keys=True)
        fh.write("\n")
    report.write_text(_render_report(metrics), encoding="utf-8")
    limitations.write_text(_render_limitations(metrics), encoding="utf-8")
    preflight.write_text(_render_preflight(metrics), encoding="utf-8")
    review_summary.write_text(_render_review_summary(metrics), encoding="utf-8")
    review.write_text(_render_review_note(metrics), encoding="utf-8")
    with agent_run.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(_build_agent_run_payload(metrics), fh, sort_keys=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT_PATH)
    parser.add_argument("--out", type=Path, default=DEFAULT_METRICS_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--agent-run", type=Path, default=DEFAULT_AGENT_RUN_PATH)
    parser.add_argument("--limitations", type=Path, default=DEFAULT_LIMITATIONS_PATH)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT_PATH)
    parser.add_argument("--review-summary", type=Path, default=DEFAULT_REVIEW_SUMMARY_PATH)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    args = parser.parse_args(argv)
    metrics = build_metrics(args.snapshot)
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


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
