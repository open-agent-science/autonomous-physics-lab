"""TASK-0391 exoplanet neptunian residual matched-control audit.

Sandbox-only audit of the CK17 neptunian mass-class residual surface on the
committed PSCompPars snapshot. The runner keeps the frozen Chen-Kipping
baseline fixed, uses true-mass/transit-radius rows as the interpretable axis,
and compares the neptunian slice with matched controls before preserving any
positive, null, or control-sensitive outcome.

No live fetch, baseline refit, composition inference, atmospheric inference,
habitability wording, target-priority output, prediction entry, canonical
result, claim update, or knowledge edit is produced.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Callable

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

AGENT_RUN_ID = "AGENT-RUN-0037"
TASK_ID = "TASK-0391"
CAMPAIGN_PROFILE_ID = "exoplanet-mass-radius"
HYPOTHESIS_PATH = (
    "hypothesis_proposals/exoplanet-mass/"
    "HYP-PROPOSAL-0052-neptunian-residual-matched-control-audit.yaml"
)
EXPERIMENT_PATH = (
    "experiment_proposals/exoplanet-mass/"
    "EXP-PROPOSAL-0018-neptunian-residual-matched-control-audit.yaml"
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
    / "exoplanet-neptunian-residual-matched-control-audit.md"
)

MIN_SLICE_ROW_COUNT: int = 30
CONTROL_MARGIN_LOG10_RMSE: float = 0.022


def _is_positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value)) and value > 0


def _row_has_true_mass_and_transit_radius(entry: dict[str, Any]) -> bool:
    mass = entry.get("mass") or {}
    radius = entry.get("radius") or {}
    return (
        mass.get("mass_class") == "true_mass"
        and radius.get("radius_class") == "transit_radius"
        and _is_positive_number(mass.get("value"))
        and _is_positive_number(radius.get("value"))
    )


def _row_has_minimum_mass_and_transit_radius(entry: dict[str, Any]) -> bool:
    mass = entry.get("mass") or {}
    radius = entry.get("radius") or {}
    return (
        mass.get("mass_class") == "minimum_mass_msini"
        and radius.get("radius_class") == "transit_radius"
        and _is_positive_number(mass.get("value"))
        and _is_positive_number(radius.get("value"))
    )


def _mass_value(entry: dict[str, Any]) -> float:
    return float(entry["mass"]["value"])


def _radius_value(entry: dict[str, Any]) -> float:
    return float(entry["radius"]["value"])


def _host_teff(entry: dict[str, Any]) -> float | None:
    value = (entry.get("host_star") or {}).get("effective_temperature_K")
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
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


def _log_residual(entry: dict[str, Any]) -> float | None:
    mass = _mass_value(entry)
    radius = _radius_value(entry)
    pred = chen_kipping_predict_radius(mass)
    if not math.isfinite(pred) or pred <= 0.0:
        return None
    return math.log10(radius) - math.log10(pred)


def _rmse(values: list[float]) -> float | None:
    if not values:
        return None
    return math.sqrt(sum(v * v for v in values) / len(values))


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[midpoint]
    return 0.5 * (ordered[midpoint - 1] + ordered[midpoint])


def _stats(values: list[float]) -> dict[str, Any]:
    return {
        "count": len(values),
        "log10_rmse": _rmse(values),
        "log10_mae": _mean([abs(v) for v in values]),
        "log10_bias": _mean(values),
        "log10_median": _median(values),
    }


def _residual_map(entries: list[dict[str, Any]]) -> dict[str, float]:
    residuals: dict[str, float] = {}
    for entry in entries:
        value = _log_residual(entry)
        if value is not None and math.isfinite(value):
            residuals[entry["row_id"]] = value
    return residuals


def _residual_values(
    entries: list[dict[str, Any]], residuals: dict[str, float]
) -> list[float]:
    return [
        residuals[entry["row_id"]]
        for entry in entries
        if residuals.get(entry["row_id"]) is not None
    ]


def _is_neptunian(entry: dict[str, Any]) -> bool:
    return planet_class_for_mass(_mass_value(entry)) == "neptunian"


def _per_class_median_residuals(
    entries: list[dict[str, Any]], residuals: dict[str, float]
) -> dict[str, float]:
    by_class: dict[str, list[float]] = {}
    for entry in entries:
        residual = residuals.get(entry["row_id"])
        if residual is None:
            continue
        by_class.setdefault(planet_class_for_mass(_mass_value(entry)), []).append(residual)
    return {
        label: median
        for label, values in by_class.items()
        if (median := _median(values)) is not None
    }


def _per_class_median_control_residuals(
    target_entries: list[dict[str, Any]], per_class_medians: dict[str, float]
) -> list[float]:
    out: list[float] = []
    for entry in target_entries:
        mass = _mass_value(entry)
        radius = _radius_value(entry)
        pred = chen_kipping_predict_radius(mass)
        if not math.isfinite(pred) or pred <= 0.0:
            continue
        shift = per_class_medians.get(planet_class_for_mass(mass), 0.0)
        out.append(math.log10(radius) - (math.log10(pred) + shift))
    return out


def _greedy_match_without_replacement(
    target_entries: list[dict[str, Any]],
    candidate_entries: list[dict[str, Any]],
    target_key: Callable[[dict[str, Any]], float | None],
    candidate_key: Callable[[dict[str, Any]], float | None],
) -> list[dict[str, Any]]:
    """Match each target to the nearest available candidate for a scalar key."""

    available: list[tuple[int, dict[str, Any], float]] = []
    for index, candidate in enumerate(candidate_entries):
        value = candidate_key(candidate)
        if value is not None and math.isfinite(value):
            available.append((index, candidate, value))

    matched: list[dict[str, Any]] = []
    used: set[int] = set()
    for target in target_entries:
        target_value = target_key(target)
        if target_value is None or not math.isfinite(target_value):
            continue
        best_index = None
        best_candidate = None
        best_delta = float("inf")
        for index, candidate, candidate_value in available:
            if index in used:
                continue
            delta = abs(candidate_value - target_value)
            if delta < best_delta:
                best_delta = delta
                best_index = index
                best_candidate = candidate
        if best_index is not None and best_candidate is not None:
            used.add(best_index)
            matched.append(best_candidate)
    return matched


def _uncertainty_band_control(
    target_entries: list[dict[str, Any]],
    candidate_entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_band: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidate_entries:
        by_band.setdefault(_uncertainty_band(candidate), []).append(candidate)
    for rows in by_band.values():
        rows.sort(key=lambda row: (math.log10(_mass_value(row)), row["row_id"]))

    used: set[str] = set()
    matched: list[dict[str, Any]] = []
    for target in target_entries:
        band = _uncertainty_band(target)
        target_mass = math.log10(_mass_value(target))
        best = None
        best_delta = float("inf")
        for candidate in by_band.get(band, []):
            if candidate["row_id"] in used:
                continue
            delta = abs(math.log10(_mass_value(candidate)) - target_mass)
            if delta < best_delta:
                best_delta = delta
                best = candidate
        if best is not None:
            used.add(best["row_id"])
            matched.append(best)
    return matched


def _build_control(
    label: str,
    entries: list[dict[str, Any]],
    residuals: dict[str, float],
    *,
    target_count: int,
) -> dict[str, Any]:
    stats = _stats(_residual_values(entries, residuals))
    if stats["count"] < MIN_SLICE_ROW_COUNT:
        status = "underpowered"
        interpretation = (
            f"{label} has {stats['count']} rows (< {MIN_SLICE_ROW_COUNT}); "
            "do not use as an interpreted matched control."
        )
    elif stats["count"] < target_count:
        status = "partial_control"
        interpretation = (
            f"{label} has fewer rows than the neptunian target "
            f"({stats['count']} vs {target_count}); interpret as partial control."
        )
    else:
        status = "usable_control"
        interpretation = f"{label} meets the minimum count gate."
    return {
        "label": label,
        "status": status,
        "stats": stats,
        "interpretation": interpretation,
    }


def _classify_audit(
    neptunian_stats: dict[str, Any],
    eligible_stats: dict[str, Any],
    controls: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    count = neptunian_stats["count"]
    target_rmse = neptunian_stats["log10_rmse"]
    eligible_rmse = eligible_stats["log10_rmse"]
    if count < MIN_SLICE_ROW_COUNT:
        return {
            "outcome": "under_minimum_slice",
            "verdict": "INCONCLUSIVE",
            "adverse_control": None,
            "delta_log10_rmse_neptunian_minus_eligible": None,
            "delta_log10_rmse_neptunian_minus_adverse_control": None,
            "explanation": (
                f"Neptunian slice has {count} rows (< {MIN_SLICE_ROW_COUNT}); "
                "no residual interpretation is allowed."
            ),
        }

    usable_controls = {
        name: control
        for name, control in controls.items()
        if control["status"] in {"usable_control", "partial_control"}
        and control["stats"]["log10_rmse"] is not None
    }
    adverse_name = None
    adverse_rmse = None
    for name, control in usable_controls.items():
        rmse = control["stats"]["log10_rmse"]
        if adverse_rmse is None or rmse > adverse_rmse:
            adverse_name = name
            adverse_rmse = rmse

    delta_eligible = (
        None
        if target_rmse is None or eligible_rmse is None
        else float(target_rmse - eligible_rmse)
    )
    delta_control = (
        None
        if target_rmse is None or adverse_rmse is None
        else float(target_rmse - adverse_rmse)
    )

    if (
        delta_eligible is not None
        and delta_eligible > CONTROL_MARGIN_LOG10_RMSE
        and delta_control is not None
        and delta_control > CONTROL_MARGIN_LOG10_RMSE
    ):
        outcome = "neptunian_residual_above_eligible_and_controls"
        verdict = "SANDBOX_PASS"
    elif delta_eligible is not None and delta_eligible > CONTROL_MARGIN_LOG10_RMSE:
        outcome = "control_sensitive_residual_stress"
        verdict = "INCONCLUSIVE"
    elif delta_eligible is not None and abs(delta_eligible) <= CONTROL_MARGIN_LOG10_RMSE:
        outcome = "neptunian_residual_close_to_eligible"
        verdict = "INCONCLUSIVE"
    elif delta_eligible is not None and delta_eligible < -CONTROL_MARGIN_LOG10_RMSE:
        outcome = "neptunian_residual_below_eligible"
        verdict = "INCONCLUSIVE"
    else:
        outcome = "inconclusive"
        verdict = "INCONCLUSIVE"

    return {
        "outcome": outcome,
        "verdict": verdict,
        "adverse_control": adverse_name,
        "delta_log10_rmse_neptunian_minus_eligible": delta_eligible,
        "delta_log10_rmse_neptunian_minus_adverse_control": delta_control,
        "explanation": (
            f"neptunian log10 RMSE = {target_rmse}; eligible log10 RMSE = "
            f"{eligible_rmse}; adverse control = {adverse_name} "
            f"(log10 RMSE = {adverse_rmse}); margin = {CONTROL_MARGIN_LOG10_RMSE}."
        ),
    }


def _band_counts(entries: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        counts[_uncertainty_band(entry)] = counts.get(_uncertainty_band(entry), 0) + 1
    return dict(sorted(counts.items()))


def build_metrics(snapshot_path: Path) -> dict[str, Any]:
    payload = load_exoplanet_snapshot(snapshot_path)
    filtered = apply_inclusion_filters(payload)
    eligible = [
        entry
        for entry in filtered.included_rows
        if _row_has_true_mass_and_transit_radius(entry)
    ]
    residuals = _residual_map(eligible)
    eligible = [entry for entry in eligible if entry["row_id"] in residuals]
    neptunian = [entry for entry in eligible if _is_neptunian(entry)]
    non_neptunian = [entry for entry in eligible if not _is_neptunian(entry)]

    minimum_mass_entries = [
        entry
        for entry in filtered.included_rows
        if _row_has_minimum_mass_and_transit_radius(entry)
    ]
    minimum_mass_residuals = _residual_map(minimum_mass_entries)

    per_class_medians = _per_class_median_residuals(eligible, residuals)
    per_class_control = _per_class_median_control_residuals(neptunian, per_class_medians)
    nearest_radius_entries = _greedy_match_without_replacement(
        neptunian,
        non_neptunian,
        target_key=_radius_value,
        candidate_key=_radius_value,
    )
    host_target = [entry for entry in neptunian if _host_teff(entry) is not None]
    host_candidates = [
        entry for entry in non_neptunian if _host_teff(entry) is not None
    ]
    host_temperature_entries = _greedy_match_without_replacement(
        host_target,
        host_candidates,
        target_key=_host_teff,
        candidate_key=_host_teff,
    )
    uncertainty_entries = _uncertainty_band_control(neptunian, non_neptunian)

    neptunian_stats = _stats(_residual_values(neptunian, residuals))
    eligible_stats = _stats(_residual_values(eligible, residuals))
    controls = {
        "per_class_median": _build_control(
            "per_class_median", [], residuals, target_count=len(neptunian)
        ),
        "nearest_radius_non_neptunian": _build_control(
            "nearest_radius_non_neptunian",
            nearest_radius_entries,
            residuals,
            target_count=len(neptunian),
        ),
        "host_temperature_non_neptunian": _build_control(
            "host_temperature_non_neptunian",
            host_temperature_entries,
            residuals,
            target_count=len(host_target),
        ),
        "uncertainty_band_non_neptunian": _build_control(
            "uncertainty_band_non_neptunian",
            uncertainty_entries,
            residuals,
            target_count=len(neptunian),
        ),
    }
    controls["per_class_median"]["stats"] = _stats(per_class_control)
    controls["per_class_median"]["status"] = (
        "usable_control"
        if controls["per_class_median"]["stats"]["count"] >= MIN_SLICE_ROW_COUNT
        else "underpowered"
    )
    controls["per_class_median"]["interpretation"] = (
        "Per-class median residual shift on the target rows; this controls "
        "for neptunian class bias but is not an independent row slice."
    )

    classification = _classify_audit(neptunian_stats, eligible_stats, controls)

    metrics: dict[str, Any] = {
        "task_id": TASK_ID,
        "agent_run_id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "snapshot_path": snapshot_path.relative_to(REPO_ROOT).as_posix(),
        "data_boundary": {
            "live_external_fetch_performed": False,
            "baseline_refit_performed": False,
            "minimum_mass_rows_in_headline_metrics": False,
            "true_mass_axis_primary": True,
        },
        "loader_summary": {
            "total_rows": filtered.total_rows,
            "pre_filter_included_count": filtered.pre_filter_included_count,
            "post_filter_included_count": filtered.post_filter_included_count,
            "eligible_true_mass_with_transit_radius": len(eligible),
            "neptunian_true_mass_with_transit_radius": len(neptunian),
            "non_neptunian_true_mass_with_transit_radius": len(non_neptunian),
            "minimum_mass_with_transit_radius_diagnostic": len(minimum_mass_residuals),
        },
        "thresholds": {
            "min_slice_row_count": MIN_SLICE_ROW_COUNT,
            "control_margin_log10_rmse": CONTROL_MARGIN_LOG10_RMSE,
        },
        "eligible_true_mass_stats": eligible_stats,
        "neptunian_stats": neptunian_stats,
        "controls": controls,
        "diagnostics": {
            "per_class_medians_log10_residual": per_class_medians,
            "neptunian_uncertainty_band_counts": _band_counts(neptunian),
            "non_neptunian_uncertainty_band_counts": _band_counts(non_neptunian),
            "host_temperature_target_count": len(host_target),
            "host_temperature_candidate_count": len(host_candidates),
            "minimum_mass_sparse_diagnostic": _stats(
                list(minimum_mass_residuals.values())
            ),
        },
        "classification": classification,
        "verdict": classification["verdict"],
    }
    return metrics


def _fmt(value: float | None, places: int = 6) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{places}f}"


def _render_report(metrics: dict[str, Any]) -> str:
    loader = metrics["loader_summary"]
    neptunian = metrics["neptunian_stats"]
    eligible = metrics["eligible_true_mass_stats"]
    classification = metrics["classification"]
    lines = [
        f"# {AGENT_RUN_ID} - Exoplanet neptunian residual matched-control audit",
        "",
        f"- Task: {TASK_ID}",
        f"- Campaign profile: {CAMPAIGN_PROFILE_ID}",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        f"- Verdict: **{metrics['verdict']}**",
        "",
        "## Boundary",
        "",
        "Sandbox-only matched-control audit on committed snapshot rows. The "
        "primary axis is true-mass/transit-radius rows; minimum-mass rows are "
        "diagnostic-only. The frozen CK17 baseline is not refit.",
        "",
        "## Primary Slice",
        "",
        f"- Eligible true-mass/transit-radius rows: {loader['eligible_true_mass_with_transit_radius']}",
        f"- Neptunian true-mass/transit-radius rows: {loader['neptunian_true_mass_with_transit_radius']}",
        f"- Diagnostic minimum-mass/transit-radius rows: {loader['minimum_mass_with_transit_radius_diagnostic']}",
        (
            f"- Eligible RMSE: {_fmt(eligible['log10_rmse'])}; "
            f"neptunian RMSE: {_fmt(neptunian['log10_rmse'])}; "
            "delta: "
            f"{_fmt(classification['delta_log10_rmse_neptunian_minus_eligible'])}"
        ),
        "",
        "## Matched Controls",
        "",
        "| control | status | count | log10 RMSE | delta neptunian-control | notes |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for name, control in metrics["controls"].items():
        stats = control["stats"]
        delta = (
            None
            if neptunian["log10_rmse"] is None or stats["log10_rmse"] is None
            else neptunian["log10_rmse"] - stats["log10_rmse"]
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    control["status"],
                    str(stats["count"]),
                    _fmt(stats["log10_rmse"]),
                    _fmt(delta),
                    control["interpretation"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Classification",
            "",
            f"- Outcome: `{classification['outcome']}`",
            f"- Adverse control: `{classification['adverse_control']}`",
            f"- {classification['explanation']}",
            "",
            "## Output Routing",
            "",
            f"- Task verdict: `{metrics['verdict']}`.",
            "- Canonical destination: sandbox-only `agent_runs/AGENT-RUN-0037/` "
            "and review note.",
            "- Review tier: none.",
            "- Gate A: not attempted.",
            "- Gate B: not attempted.",
            "- Claim impact: no claim change.",
            "- Knowledge impact: no knowledge change.",
            "- Publication blocker: task scope authorizes sandbox evidence only.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_review(metrics: dict[str, Any]) -> str:
    classification = metrics["classification"]
    lines = [
        "# Exoplanet neptunian residual matched-control audit",
        "",
        f"- Agent run: `{AGENT_RUN_ID}`",
        f"- Task: `{TASK_ID}`",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        f"- Verdict: **{metrics['verdict']}**",
        "",
        "## Scope",
        "",
        "This review tests whether the neptunian true-mass/transit-radius "
        "residual stress remains visible after matched controls. It uses only "
        "the committed PSCompPars snapshot and frozen CK17 residuals.",
        "",
        "No live fetch, baseline refit, atmospheric-composition inference, "
        "inflation-physics claim, habitability wording, target-priority output, "
        "new mass-radius law, prediction entry, canonical result, claim update, "
        "or knowledge edit is authorized.",
        "",
        "## Result",
        "",
        f"- Outcome: `{classification['outcome']}`",
        f"- Adverse control: `{classification['adverse_control']}`",
        f"- {classification['explanation']}",
        "",
        "## Control Table",
        "",
        "| control | status | count | RMSE | interpretation |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for name, control in metrics["controls"].items():
        stats = control["stats"]
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    control["status"],
                    str(stats["count"]),
                    _fmt(stats["log10_rmse"]),
                    control["interpretation"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Output Routing",
            "",
            f"- Task verdict: `{metrics['verdict']}`.",
            "- Canonical destination: sandbox-only `agent_runs/AGENT-RUN-0037/` "
            "and this review note.",
            "- Review tier: none.",
            "- Gate A: not attempted.",
            "- Gate B: not attempted.",
            "- Claim impact: no claim change.",
            "- Knowledge impact: no knowledge change.",
            "- Publication blocker: sandbox-only validation task.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_limitations(metrics: dict[str, Any]) -> str:
    del metrics
    bullets = [
        "Controls use committed snapshot fields and frozen CK17 residuals only.",
        "Matched controls are diagnostic slices, not causal adjustments.",
        "Per-class median control is a target-row residual shift rather than an independent row slice.",
        "Host-temperature control excludes rows without host effective temperature.",
        "Minimum-mass rows are sparse diagnostics only.",
        "No composition, inflation-physics, habitability, target-priority, prediction, claim, or knowledge output is authorized.",
    ]
    return "# Limitations\n\n" + "\n".join(f"- {item}" for item in bullets) + "\n"


def _render_preflight(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Preflight",
            "",
            f"- Snapshot: `{metrics['snapshot_path']}`",
            "- Data boundary: only committed snapshot rows are read.",
            "- Baseline freeze: CK17 segments unchanged; no refit.",
            "- Primary axis: true-mass/transit-radius neptunian rows.",
            "- Controls: per-class median, nearest-radius, host-temperature, and uncertainty-band controls.",
            "- Promotion boundary: sandbox-only; no canonical result, prediction, claim, or knowledge output.",
            "",
            "## Checks",
            "",
            "| name | status | notes |",
            "| --- | --- | --- |",
            "| data_boundary | PASS | Only committed snapshot rows are read. |",
            "| baseline_freeze | PASS | CK17 frozen segments are reused without refit. |",
            "| control_floor | PASS | Required controls are reported with counts and gates. |",
            "| promotion_boundary | PASS | Sandbox-only output. |",
            "",
        ]
    )


def _render_review_summary(metrics: dict[str, Any]) -> str:
    classification = metrics["classification"]
    lines = [
        "# Review summary",
        "",
        f"- Verdict: **{metrics['verdict']}**",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        (
            "- Neptunian rows: "
            f"{metrics['loader_summary']['neptunian_true_mass_with_transit_radius']}"
        ),
        f"- Outcome: `{classification['outcome']}`",
        (
            "- Delta neptunian vs eligible RMSE: "
            f"{_fmt(classification['delta_log10_rmse_neptunian_minus_eligible'])}"
        ),
        (
            "- Delta neptunian vs adverse control RMSE: "
            f"{_fmt(classification['delta_log10_rmse_neptunian_minus_adverse_control'])}"
        ),
        "",
        "The audit preserves control-sensitive and underpowered outcomes; it does "
        "not promote a result, prediction, claim, or knowledge artifact.",
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
        "created_by": {
            "contributor_id": "master",
            "agent_id": "codex",
        },
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
                    "name": "control_floor",
                    "status": "PASS",
                    "notes": (
                        "Per-class, nearest-radius, host-temperature, and "
                        "uncertainty-band controls are reported."
                    ),
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No canonical result, prediction, claim, or knowledge output.",
                },
            ],
        },
        "limitations": [
            "Controls use committed snapshot fields and frozen CK17 residuals only.",
            "Matched controls are diagnostic slices, not causal adjustments.",
            "Per-class median control is a target-row residual shift rather than an independent row slice.",
            "Host-temperature control excludes rows without host effective temperature.",
            "Minimum-mass rows are sparse diagnostics only.",
            "No composition, inflation-physics, habitability, target-priority, prediction, claim, or knowledge output is authorized.",
        ],
        "verdict": metrics["verdict"],
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any canonical result, prediction "
                "registry entry, claim update, knowledge edit, or follow-up "
                "hypothesis lane treats the neptunian residual as physical structure."
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
    for path in (out, report, agent_run, limitations, preflight, review_summary, review):
        path.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2, sort_keys=True)
        handle.write("\n")
    report.write_text(_render_report(metrics), encoding="utf-8")
    limitations.write_text(_render_limitations(metrics), encoding="utf-8")
    preflight.write_text(_render_preflight(metrics), encoding="utf-8")
    review_summary.write_text(_render_review_summary(metrics), encoding="utf-8")
    review.write_text(_render_review(metrics), encoding="utf-8")
    with agent_run.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(_build_agent_run_payload(metrics), handle, sort_keys=False)


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


if __name__ == "__main__":
    raise SystemExit(main())
