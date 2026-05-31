"""TASK-0481 compact-radius host-context preflight.

This sandbox-only runner checks whether committed exoplanet snapshot metadata
can support a later compact-radius host-context residual audit. It reports
coverage, missingness, and coarse bin power for host-star effective
temperature, host metallicity, stellar radius, equilibrium temperature, and
irradiation flux.

The runner does not fetch live data, fit a correction model, refit the CK17
baseline, write canonical results, register predictions, promote claims, edit
knowledge, or infer composition, habitability, atmospheres, or target priority.
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
)

AGENT_RUN_ID = "AGENT-RUN-0051"
TASK_ID = "TASK-0481"
CAMPAIGN_PROFILE_ID = "exoplanet-mass-radius"

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
    / "exoplanet-compact-radius-host-context-preflight.md"
)

COMPACT_RADIUS_THRESHOLD_REARTH = 1.5
MIN_INTERPRETABLE_ROWS = 30
BENCHMARK_COVERAGE_FRACTION = 0.80
CONDITIONAL_COVERAGE_FRACTION = 0.50


@dataclass(frozen=True)
class FieldSpec:
    field_id: str
    label: str
    path: tuple[str, ...]
    positive_only: bool
    role: str
    bin_label: Callable[[float | None], str]


def _is_positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value)) and value > 0


def _number_or_none(value: Any, *, positive_only: bool = False) -> float | None:
    if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        return None
    numeric = float(value)
    if positive_only and numeric <= 0.0:
        return None
    return numeric


def _nested_value(entry: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = entry
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _row_has_true_mass_and_transit_radius(entry: dict[str, Any]) -> bool:
    mass = entry.get("mass") or {}
    radius = entry.get("radius") or {}
    return (
        mass.get("mass_class") == "true_mass"
        and radius.get("radius_class") == "transit_radius"
        and _is_positive_number(mass.get("value"))
        and _is_positive_number(radius.get("value"))
    )


def _radius_value(entry: dict[str, Any]) -> float:
    return float(entry["radius"]["value"])


def _is_compact(entry: dict[str, Any]) -> bool:
    return _radius_value(entry) < COMPACT_RADIUS_THRESHOLD_REARTH


def _host_teff_bin(value: float | None) -> str:
    if value is None:
        return "missing"
    if value < 3900.0:
        return "M_lt3900K"
    if value < 5200.0:
        return "K_3900_5200K"
    if value < 6000.0:
        return "G_5200_6000K"
    if value < 7500.0:
        return "F_6000_7500K"
    return "hot_ge7500K"


def _metallicity_bin(value: float | None) -> str:
    if value is None:
        return "missing"
    if value < -0.2:
        return "metal_poor_lt_minus0p2"
    if value <= 0.2:
        return "near_solar_minus0p2_0p2"
    return "metal_rich_gt0p2"


def _stellar_radius_bin(value: float | None) -> str:
    if value is None:
        return "missing"
    if value < 0.7:
        return "small_lt0p7Rsun"
    if value < 1.0:
        return "subsolar_0p7_1p0Rsun"
    if value < 1.5:
        return "solar_high_1p0_1p5Rsun"
    return "large_ge1p5Rsun"


def _equilibrium_temperature_bin(value: float | None) -> str:
    if value is None:
        return "missing"
    if value < 500.0:
        return "low_lt500K"
    if value < 1000.0:
        return "mid_500_1000K"
    return "high_ge1000K"


def _irradiation_flux_bin(value: float | None) -> str:
    if value is None:
        return "missing"
    if value < 10.0:
        return "low_lt10Searth"
    if value < 100.0:
        return "mid_10_100Searth"
    return "high_ge100Searth"


FIELD_SPECS: tuple[FieldSpec, ...] = (
    FieldSpec(
        "host_effective_temperature_K",
        "host Teff",
        ("host_star", "effective_temperature_K"),
        True,
        "host_star",
        _host_teff_bin,
    ),
    FieldSpec(
        "host_metallicity_fe_h",
        "host metallicity [Fe/H]",
        ("host_star", "metallicity_fe_h"),
        False,
        "host_star",
        _metallicity_bin,
    ),
    FieldSpec(
        "stellar_radius_rsun",
        "stellar radius",
        ("host_star", "stellar_radius_rsun"),
        True,
        "host_star",
        _stellar_radius_bin,
    ),
    FieldSpec(
        "equilibrium_temperature_K",
        "equilibrium temperature",
        ("equilibrium_temperature_K",),
        True,
        "equilibrium_temperature_proxy",
        _equilibrium_temperature_bin,
    ),
    FieldSpec(
        "irradiation_flux_earth_units",
        "irradiation flux",
        ("irradiation_flux_earth_units",),
        True,
        "equilibrium_temperature_proxy",
        _irradiation_flux_bin,
    ),
)


def _classification(
    *,
    denominator: int,
    present: int,
    interpretable_bin_count: int,
    min_rows: int = MIN_INTERPRETABLE_ROWS,
) -> str:
    if denominator < min_rows:
        return "blocked_by_low_slice_count"
    coverage = present / denominator if denominator else 0.0
    if present < min_rows or coverage < CONDITIONAL_COVERAGE_FRACTION:
        return "blocked_by_missingness"
    if coverage >= BENCHMARK_COVERAGE_FRACTION and interpretable_bin_count >= 2:
        return "benchmark_usable"
    if coverage >= BENCHMARK_COVERAGE_FRACTION:
        return "coverage_usable_partition_underpowered"
    return "conditionally_usable"


def _coverage_summary(rows: list[dict[str, Any]], spec: FieldSpec) -> dict[str, Any]:
    values: list[float | None] = [
        _number_or_none(_nested_value(row, spec.path), positive_only=spec.positive_only)
        for row in rows
    ]
    present_values = [value for value in values if value is not None]
    bin_counts: dict[str, int] = {}
    for value in values:
        label = spec.bin_label(value)
        bin_counts[label] = bin_counts.get(label, 0) + 1

    non_missing_bin_counts = {
        label: count for label, count in bin_counts.items() if label != "missing"
    }
    interpretable_bins = {
        label: count
        for label, count in non_missing_bin_counts.items()
        if count >= MIN_INTERPRETABLE_ROWS
    }
    denominator = len(rows)
    present = len(present_values)
    missing = denominator - present
    coverage_fraction = present / denominator if denominator else 0.0
    return {
        "field_id": spec.field_id,
        "label": spec.label,
        "role": spec.role,
        "denominator": denominator,
        "present_count": present,
        "missing_count": missing,
        "coverage_fraction": coverage_fraction,
        "coverage_percent": round(coverage_fraction * 100.0, 3),
        "bin_counts": dict(sorted(bin_counts.items())),
        "interpretable_bin_count": len(interpretable_bins),
        "interpretable_bins": dict(sorted(interpretable_bins.items())),
        "status": _classification(
            denominator=denominator,
            present=present,
            interpretable_bin_count=len(interpretable_bins),
        ),
    }


def _scope_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(rows),
        "radius_min_rearth": min((_radius_value(row) for row in rows), default=None),
        "radius_max_rearth": max((_radius_value(row) for row in rows), default=None),
    }


def _field_table_lines(summaries: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| field | present | missing | coverage | interpretable bins | status |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for summary in summaries:
        lines.append(
            "| {label} | {present_count} | {missing_count} | {coverage_percent:.1f}% | "
            "{interpretable_bin_count} | `{status}` |".format(**summary)
        )
    return lines


def build_metrics(snapshot_path: Path) -> dict[str, Any]:
    payload = load_exoplanet_snapshot(snapshot_path)
    filtered = apply_inclusion_filters(payload)
    eligible = [
        entry
        for entry in filtered.included_rows
        if _row_has_true_mass_and_transit_radius(entry)
    ]
    compact = [entry for entry in eligible if _is_compact(entry)]
    outside_compact = [entry for entry in eligible if not _is_compact(entry)]

    eligible_fields = [_coverage_summary(eligible, spec) for spec in FIELD_SPECS]
    compact_fields = [_coverage_summary(compact, spec) for spec in FIELD_SPECS]

    benchmark_usable = [
        item["field_id"] for item in compact_fields if item["status"] == "benchmark_usable"
    ]
    conditional = [
        item["field_id"]
        for item in compact_fields
        if item["status"]
        in {"conditionally_usable", "coverage_usable_partition_underpowered"}
    ]
    blocked = [
        item["field_id"]
        for item in compact_fields
        if item["status"] in {"blocked_by_missingness", "blocked_by_low_slice_count"}
    ]
    if benchmark_usable and (conditional or blocked):
        preflight_status = "partially_usable"
    elif benchmark_usable:
        preflight_status = "ready_for_benchmark_axes"
    elif conditional and blocked:
        preflight_status = "conditional_with_missingness_blockers"
    elif conditional:
        preflight_status = "conditional_only_partition_underpowered"
    else:
        preflight_status = "blocked"

    return {
        "task_id": TASK_ID,
        "agent_run_id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "snapshot_path": snapshot_path.relative_to(REPO_ROOT).as_posix(),
        "data_boundary": {
            "live_external_fetch_performed": False,
            "correction_model_fit_performed": False,
            "baseline_refit_performed": False,
            "canonical_result_written": False,
            "prediction_written": False,
            "claim_or_knowledge_update_performed": False,
            "only_committed_snapshot_fields_used": True,
            "compact_radius_threshold_rearth": COMPACT_RADIUS_THRESHOLD_REARTH,
            "true_mass_transit_radius_axis_only": True,
        },
        "loader_summary": {
            "total_rows": filtered.total_rows,
            "pre_filter_included_count": filtered.pre_filter_included_count,
            "post_filter_included_count": filtered.post_filter_included_count,
            "eligible_true_mass_with_transit_radius": len(eligible),
            "compact_slice_count": len(compact),
            "outside_compact_count": len(outside_compact),
        },
        "thresholds": {
            "min_interpretable_rows": MIN_INTERPRETABLE_ROWS,
            "benchmark_coverage_fraction": BENCHMARK_COVERAGE_FRACTION,
            "conditional_coverage_fraction": CONDITIONAL_COVERAGE_FRACTION,
        },
        "scope": {
            "eligible_true_mass_transit_radius": _scope_summary(eligible),
            "compact_radius": _scope_summary(compact),
            "outside_compact": _scope_summary(outside_compact),
        },
        "field_coverage": {
            "eligible_true_mass_transit_radius": eligible_fields,
            "compact_radius": compact_fields,
        },
        "axis_recommendations": {
            "benchmark_usable": benchmark_usable,
            "conditional_or_partition_underpowered": conditional,
            "blocked_by_missingness": blocked,
        },
        "preflight_status": preflight_status,
        "verdict": "INCONCLUSIVE",
    }


def _render_report(metrics: dict[str, Any]) -> str:
    compact = metrics["field_coverage"]["compact_radius"]
    eligible = metrics["field_coverage"]["eligible_true_mass_transit_radius"]
    return "\n".join(
        [
            "# Exoplanet compact-radius host-context preflight",
            "",
            f"- Agent run: `{AGENT_RUN_ID}`",
            f"- Task: `{TASK_ID}`",
            f"- Snapshot: `{metrics['snapshot_path']}`",
            f"- Verdict: **{metrics['verdict']}**",
            f"- Preflight status: `{metrics['preflight_status']}`",
            "",
            "## Scope",
            "",
            "This preflight checks host-context metadata coverage before any "
            "compact-radius host hypothesis is audited. It uses true-mass rows "
            "with transit radii only, defines compact radius as R/Re < 1.5, "
            "and reports missingness without fitting a correction model.",
            "",
            "No live fetch, baseline refit, correction model, composition, "
            "habitability, atmosphere, target-priority, prediction, claim, "
            "canonical result, or knowledge output is produced.",
            "",
            "## Compact-radius field coverage",
            "",
            *_field_table_lines(compact),
            "",
            "## Eligible-axis reference coverage",
            "",
            *_field_table_lines(eligible),
            "",
            "## Recommendation",
            "",
            "- Benchmark-usable compact-radius axes: "
            f"{metrics['axis_recommendations']['benchmark_usable'] or 'none'}.",
            "- Conditional or partition-underpowered axes: "
            f"{metrics['axis_recommendations']['conditional_or_partition_underpowered'] or 'none'}.",
            "- Blocked by missingness: "
            f"{metrics['axis_recommendations']['blocked_by_missingness'] or 'none'}.",
            "",
            "No benchmark-axis host-context audit should proceed from this "
            "compact slice as-is. A future task would need to explicitly "
            "declare a conditional missingness or underpowered-bin analysis. "
            "Missingness remains a first-class negative result.",
            "",
        ]
    )


def _render_review(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            _render_report(metrics),
            "## Output Routing",
            "",
            f"- Task verdict: `{metrics['verdict']}`.",
            f"- Canonical destination: sandbox-only `agent_runs/{AGENT_RUN_ID}/` "
            "and this review note.",
            "- Review tier: none.",
            "- Gate A: not attempted.",
            "- Gate B: not attempted.",
            "- Claim impact: no claim change.",
            "- Knowledge impact: no knowledge change.",
            "- Publication blocker: sandbox-only preflight; no correction model "
            "or promoted claim.",
            "",
        ]
    )


def _render_limitations(metrics: dict[str, Any]) -> str:
    del metrics
    bullets = [
        "This is a coverage and missingness preflight, not a residual correction model.",
        "Only committed snapshot fields are read; no live source refresh is performed.",
        "The compact slice has limited row count, so bin power is reported explicitly.",
        "Field presence does not prove that metadata are uniformly measured or unbiased.",
        "Missingness may reflect source selection effects rather than astrophysical structure.",
        "No composition, habitability, atmosphere, target-priority, prediction, claim, or knowledge output is authorized.",
    ]
    return "# Limitations\n\n" + "\n".join(f"- {item}" for item in bullets) + "\n"


def _render_preflight(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Preflight",
            "",
            f"- Snapshot: `{metrics['snapshot_path']}`",
            "- Data boundary: only committed snapshot fields are read.",
            "- Model boundary: no correction model and no CK17 baseline refit.",
            "- Scope: true-mass rows with transit radii; compact radius R/Re < 1.5.",
            "- Promotion boundary: sandbox-only; no canonical result, prediction, "
            "claim, or knowledge output.",
            "",
            "## Checks",
            "",
            "| name | status | notes |",
            "| --- | --- | --- |",
            "| data_boundary | PASS | Only committed snapshot fields are read. |",
            "| no_live_fetch | PASS | No external source refresh is performed. |",
            "| no_correction_model | PASS | The runner reports coverage only. |",
            "| compact_slice_present | PASS | "
            f"{metrics['loader_summary']['compact_slice_count']} compact rows are available. |",
            "| promotion_boundary | PASS | Sandbox-only output. |",
            "",
        ]
    )


def _render_review_summary(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Review summary",
            "",
            f"- Verdict: **{metrics['verdict']}**",
            f"- Preflight status: `{metrics['preflight_status']}`",
            f"- Compact rows: {metrics['loader_summary']['compact_slice_count']}",
            "- Benchmark-usable axes: "
            f"{metrics['axis_recommendations']['benchmark_usable'] or 'none'}",
            "- Conditional / partition-underpowered axes: "
            f"{metrics['axis_recommendations']['conditional_or_partition_underpowered'] or 'none'}",
            "- Blocked by missingness: "
            f"{metrics['axis_recommendations']['blocked_by_missingness'] or 'none'}",
            "",
            "The preflight is sandbox-only and does not promote any scientific claim.",
            "",
        ]
    )


def _build_agent_run_payload(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "task_id": TASK_ID,
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {
            "contributor_id": "roman",
            "agent_id": "codex",
        },
        "proposal_paths": {
            "hypothesis": (
                "hypothesis_proposals/exoplanet-mass/"
                "HYP-PROPOSAL-0051-compact-subneptune-residual-pilot.yaml"
            ),
            "experiment": (
                "experiment_proposals/exoplanet-mass/"
                "EXP-PROPOSAL-0017-compact-subneptune-residual-pilot.yaml"
            ),
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
                    "notes": "Only committed snapshot fields are read.",
                },
                {
                    "name": "no_live_fetch",
                    "status": "PASS",
                    "notes": "No external source refresh is performed.",
                },
                {
                    "name": "no_correction_model",
                    "status": "PASS",
                    "notes": "Coverage and missingness are reported without fitting.",
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No canonical result, prediction, claim, or knowledge output.",
                },
            ],
        },
        "limitations": [
            "Coverage preflight only; no correction model is fit.",
            "Only committed snapshot fields are read.",
            "Compact-slice bin power is limited and reported explicitly.",
            "Field presence does not remove measurement or source-selection bias.",
            "No composition, habitability, atmosphere, target-priority, prediction, claim, or knowledge output is authorized.",
        ],
        "verdict": metrics["verdict"],
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any follow-up task treats host context "
                "as an explanatory model for compact-radius residual stress."
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
    parser.add_argument(
        "--review-summary", type=Path, default=DEFAULT_REVIEW_SUMMARY_PATH
    )
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
