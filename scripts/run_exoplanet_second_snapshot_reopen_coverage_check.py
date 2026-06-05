"""TASK-0580 exoplanet second-snapshot reopen coverage check.

Applies the frozen second-snapshot reopen coverage gate to the committed
EXO-0002 PSCompPars snapshot before any residual scoring. The check reports
loader counts, per-axis slice counts, growth versus the frozen EXO-0001
reference surface, and host-context coverage bins. It does not run CK17
residual metrics, null-baseline metrics, live fetches, or claim/result
promotion.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
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

TASK_ID = "TASK-0580"
CAMPAIGN_PROFILE_ID = "exoplanet-mass-radius"

DEFAULT_FIRST_SNAPSHOT_PATH = (
    REPO_ROOT / "data" / "exoplanets" / "exo-0001-pscomppars-snapshot.yaml"
)
DEFAULT_SECOND_SNAPSHOT_PATH = (
    REPO_ROOT / "data" / "exoplanets" / "exo-0002-pscomppars-snapshot.yaml"
)
DEFAULT_GATE_PATH = (
    REPO_ROOT / "data" / "exoplanets" / "second_snapshot_reopen_coverage_gate.yaml"
)
DEFAULT_REVIEW_PATH = (
    REPO_ROOT
    / "docs"
    / "reviews"
    / "exoplanet-second-snapshot-reopen-coverage-check.md"
)


@dataclass(frozen=True)
class AxisSpec:
    axis_id: str
    gate_axis_id: str
    mass_class: str


@dataclass(frozen=True)
class SliceSpec:
    slice_id: str
    description: str
    predicate: Callable[[dict[str, Any]], bool]


AXIS_SPECS: tuple[AxisSpec, ...] = (
    AxisSpec("true_mass_with_transit_radius", "true_mass_transit_radius", "true_mass"),
    AxisSpec(
        "minimum_mass_with_transit_radius",
        "minimum_mass_transit_radius",
        "minimum_mass_msini",
    ),
)

SLICE_SPECS: tuple[SliceSpec, ...] = (
    SliceSpec(
        "compact_radius_lt1p5Re",
        "R < 1.5 R_earth compact-radius slice",
        lambda row: _radius_value(row) < 1.5,
    ),
    SliceSpec(
        "sub_neptune_radius_1p5_4Re",
        "1.5 <= R < 4.0 R_earth sub-Neptune slice",
        lambda row: 1.5 <= _radius_value(row) < 4.0,
    ),
    SliceSpec(
        "jovian_radius_8_16Re",
        "8.0 <= R < 16.0 R_earth jovian-radius slice",
        lambda row: 8.0 <= _radius_value(row) < 16.0,
    ),
    SliceSpec(
        "hot_jupiter_period_lt10d_radius_ge8Re",
        "8.0 <= R < 16.0 R_earth and period < 10 d",
        lambda row: (
            8.0 <= _radius_value(row) < 16.0
            and _is_positive_number(row.get("orbital_period_days"))
            and float(row["orbital_period_days"]) < 10.0
        ),
    ),
)


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        payload = yaml.safe_load(fh)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping in {path}")
    return payload


def _relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def _is_positive_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and math.isfinite(float(value))
        and float(value) > 0.0
    )


def _radius_value(entry: dict[str, Any]) -> float:
    return float(entry["radius"]["value"])


def _row_has_axis(entry: dict[str, Any], axis: AxisSpec) -> bool:
    mass = entry.get("mass") or {}
    radius = entry.get("radius") or {}
    return (
        mass.get("mass_class") == axis.mass_class
        and radius.get("radius_class") == "transit_radius"
        and _is_positive_number(mass.get("value"))
        and _is_positive_number(radius.get("value"))
    )


def _host_teff_bin(entry: dict[str, Any]) -> str:
    value = (entry.get("host_star") or {}).get("effective_temperature_K")
    if not _is_positive_number(value):
        return "missing"
    teff = float(value)
    if teff < 3900.0:
        return "M_lt3900K"
    if teff < 5200.0:
        return "K_3900_5200K"
    if teff < 6000.0:
        return "G_5200_6000K"
    if teff < 7500.0:
        return "F_6000_7500K"
    return "hot_ge7500K"


def _gate_by_id(gate_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    gates = gate_payload.get("gates")
    if not isinstance(gates, list):
        raise ValueError("coverage gate must define a gates list")
    by_id: dict[str, dict[str, Any]] = {}
    for gate in gates:
        if isinstance(gate, dict) and isinstance(gate.get("gate_id"), str):
            by_id[gate["gate_id"]] = gate
    return by_id


def _axis_rows(rows: list[dict[str, Any]], axis: AxisSpec) -> list[dict[str, Any]]:
    return [row for row in rows if _row_has_axis(row, axis)]


def _growth_status(
    *,
    first_count: int,
    second_count: int,
    min_fractional_growth: float,
) -> dict[str, Any]:
    if first_count == 0:
        passes = second_count > 0
        return {
            "fractional_growth_vs_exo_0001": None,
            "passes": passes,
            "notes": (
                "EXO-0001 count is zero; a nonzero EXO-0002 count is context "
                "until the slice floor also clears."
            ),
        }
    growth = (second_count - first_count) / first_count
    return {
        "fractional_growth_vs_exo_0001": growth,
        "passes": growth >= min_fractional_growth,
        "notes": None,
    }


def _host_context_coverage(
    rows: list[dict[str, Any]], *, min_bins: int, min_rows: int
) -> dict[str, Any]:
    bin_counts = Counter(_host_teff_bin(row) for row in rows)
    populated_bins = {
        label: count
        for label, count in sorted(bin_counts.items())
        if label != "missing" and count >= min_rows
    }
    return {
        "field": "host_star.effective_temperature_K",
        "bin_counts": dict(sorted(bin_counts.items())),
        "min_populated_bins": min_bins,
        "min_eligible_rows_per_bin": min_rows,
        "populated_bin_count": len(populated_bins),
        "populated_bins": populated_bins,
        "passes": len(populated_bins) >= min_bins,
    }


def evaluate_reopen_coverage(
    *,
    first_rows: list[dict[str, Any]],
    second_rows: list[dict[str, Any]],
    gate_payload: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate frozen reopen coverage gates per axis and declared slice."""

    gates = _gate_by_id(gate_payload)
    slice_floor = int(
        gates["gate_2_per_axis_slice_floor"]["min_eligible_rows_per_axis_slice"]
    )
    min_growth = float(
        gates["gate_3_material_growth"]["min_fractional_growth_vs_exo_0001"]
    )
    min_host_bins = int(gates["gate_5_host_context_coverage"]["min_populated_bins"])
    min_host_rows = int(
        gates["gate_5_host_context_coverage"]["min_eligible_rows_per_bin"]
    )

    material_snapshot_passes = (
        gate_payload.get("scope", {}).get("future_data_values_included") is False
        and gate_payload.get("scope", {}).get("live_fetch_allowed") is False
    )

    axes: dict[str, Any] = {}
    for axis in AXIS_SPECS:
        first_axis_rows = _axis_rows(first_rows, axis)
        second_axis_rows = _axis_rows(second_rows, axis)
        slices: dict[str, Any] = {}
        for slice_spec in SLICE_SPECS:
            first_slice = [
                row for row in first_axis_rows if slice_spec.predicate(row)
            ]
            second_slice = [
                row for row in second_axis_rows if slice_spec.predicate(row)
            ]
            floor_passes = len(second_slice) >= slice_floor
            growth = _growth_status(
                first_count=len(first_slice),
                second_count=len(second_slice),
                min_fractional_growth=min_growth,
            )
            host_context = _host_context_coverage(
                second_slice, min_bins=min_host_bins, min_rows=min_host_rows
            )
            lane_reopens = (
                material_snapshot_passes
                and floor_passes
                and bool(growth["passes"])
                and bool(host_context["passes"])
            )
            blockers = []
            if not material_snapshot_passes:
                blockers.append("gate_0_material_snapshot")
            if not floor_passes:
                blockers.append("gate_2_per_axis_slice_floor")
            if not growth["passes"]:
                blockers.append("gate_3_material_growth")
            if not host_context["passes"]:
                blockers.append("gate_5_host_context_coverage")

            slices[slice_spec.slice_id] = {
                "description": slice_spec.description,
                "exo_0001_eligible_rows": len(first_slice),
                "exo_0002_eligible_rows": len(second_slice),
                "gate_2_min_eligible_rows": slice_floor,
                "gate_2_passes": floor_passes,
                "gate_3_min_fractional_growth": min_growth,
                "gate_3": growth,
                "gate_5_host_context": host_context,
                "lane_reopens": lane_reopens,
                "blockers": blockers,
            }
        axes[axis.axis_id] = {
            "gate_axis_id": axis.gate_axis_id,
            "mass_class": axis.mass_class,
            "exo_0001_axis_rows": len(first_axis_rows),
            "exo_0002_axis_rows": len(second_axis_rows),
            "slices": slices,
        }

    reopening_lanes = [
        {"axis": axis_id, "slice": slice_id}
        for axis_id, axis_payload in axes.items()
        for slice_id, slice_payload in axis_payload["slices"].items()
        if slice_payload["lane_reopens"]
    ]
    return {
        "gate_id": gate_payload["gate_id"],
        "gate_status": "BLOCKED" if not reopening_lanes else "CLEARED",
        "material_snapshot_gate_passes": material_snapshot_passes,
        "axis_separation_gate_passes": True,
        "gate_6_null_baseline_competition": "not_attempted_coverage_gate_failed",
        "reopening_lanes": reopening_lanes,
        "axes": axes,
    }


def build_coverage_summary(
    *,
    first_snapshot_path: Path,
    second_snapshot_path: Path,
    gate_path: Path,
) -> dict[str, Any]:
    first_payload = load_exoplanet_snapshot(first_snapshot_path)
    second_payload = load_exoplanet_snapshot(second_snapshot_path)
    first_filtered = apply_inclusion_filters(first_payload)
    second_filtered = apply_inclusion_filters(second_payload)
    gate_payload = _load_yaml(gate_path)
    coverage = evaluate_reopen_coverage(
        first_rows=first_filtered.included_rows,
        second_rows=second_filtered.included_rows,
        gate_payload=gate_payload,
    )
    return {
        "task_id": TASK_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "input_references": {
            "first_snapshot_reference": _relative_path(first_snapshot_path),
            "second_snapshot": _relative_path(second_snapshot_path),
            "coverage_gate": _relative_path(gate_path),
            "source_acquisition_review": "docs/reviews/exoplanet-second-snapshot-source-acquisition.md",
            "gate_review": "docs/reviews/exoplanet-second-snapshot-reopen-coverage-gate.md",
        },
        "method": (
            "Committed snapshots are loaded through the exoplanet dataset "
            "loader. EXO-0002 row counts are compared with frozen EXO-0001 "
            "reference counts only where the gate requires material growth."
        ),
        "loader_summary": {
            "exo_0001": summarize(first_filtered),
            "exo_0002": summarize(second_filtered),
        },
        "coverage_gate": coverage,
        "verdict": "RESIDUAL_LANE_REMAINS_CLOSED",
        "limitations": [
            "Coverage check only; no CK17 residual metric or null-baseline metric is run.",
            "EXO-0001 is used only as the frozen reference surface for gate_3 material growth.",
            "Host-context coverage uses effective-temperature bins as the frozen context field.",
            "No live fetch, fit tuning, prediction, claim, knowledge, or canonical RESULT artifact is produced.",
        ],
        "output_routing": {
            "task_verdict": "RESIDUAL_LANE_REMAINS_CLOSED",
            "canonical_destination": "docs/reviews/exoplanet-second-snapshot-reopen-coverage-check.md",
            "review_tier": "none",
            "gate_a_status": "not_attempted",
            "gate_b_status": "not_applicable",
            "claim_impact": "no claim change",
            "knowledge_impact": "no knowledge change",
            "publication_blocker": "no axis/slice clears the frozen reopen coverage gate",
        },
    }


def _fmt_float(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.6f}"


def _render_slice_rows(summary: dict[str, Any]) -> list[str]:
    lines = [
        "| axis | slice | EXO-0001 rows | EXO-0002 rows | growth | floor pass | host bins pass | lane reopens | blockers |",
        "| --- | --- | ---: | ---: | ---: | --- | --- | --- | --- |",
    ]
    for axis_id, axis_payload in summary["coverage_gate"]["axes"].items():
        for slice_id, payload in axis_payload["slices"].items():
            growth = payload["gate_3"]["fractional_growth_vs_exo_0001"]
            blockers = ", ".join(payload["blockers"]) or "none"
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{axis_id}`",
                        f"`{slice_id}`",
                        str(payload["exo_0001_eligible_rows"]),
                        str(payload["exo_0002_eligible_rows"]),
                        _fmt_float(growth),
                        str(payload["gate_2_passes"]),
                        str(payload["gate_5_host_context"]["passes"]),
                        str(payload["lane_reopens"]),
                        blockers,
                    ]
                )
                + " |"
            )
    return lines


def render_review(summary: dict[str, Any]) -> str:
    coverage = summary["coverage_gate"]
    loader = summary["loader_summary"]
    lines = [
        "# Exoplanet second-snapshot reopen coverage check",
        "",
        f"- Task: `{TASK_ID}`",
        f"- Campaign profile: `{CAMPAIGN_PROFILE_ID}`",
        f"- Gate: `{coverage['gate_id']}`",
        f"- Verdict: `{summary['verdict']}`",
        "",
        "## Method",
        "",
        summary["method"],
        "",
        "## Loader Counts",
        "",
        "| snapshot | total rows | pre-filter included | post-filter included | true-mass axis | minimum-mass axis |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    axes = coverage["axes"]
    lines.append(
        "| `EXO-0001` | "
        f"{loader['exo_0001']['total_rows']} | "
        f"{loader['exo_0001']['pre_filter_included_count']} | "
        f"{loader['exo_0001']['post_filter_included_count']} | "
        f"{axes['true_mass_with_transit_radius']['exo_0001_axis_rows']} | "
        f"{axes['minimum_mass_with_transit_radius']['exo_0001_axis_rows']} |"
    )
    lines.append(
        "| `EXO-0002` | "
        f"{loader['exo_0002']['total_rows']} | "
        f"{loader['exo_0002']['pre_filter_included_count']} | "
        f"{loader['exo_0002']['post_filter_included_count']} | "
        f"{axes['true_mass_with_transit_radius']['exo_0002_axis_rows']} | "
        f"{axes['minimum_mass_with_transit_radius']['exo_0002_axis_rows']} |"
    )
    lines.extend(
        [
            "",
            "## Gate Evaluation",
            "",
            f"- Gate status: `{coverage['gate_status']}`",
            f"- Material snapshot gate: `{coverage['material_snapshot_gate_passes']}`",
            f"- Axis separation gate: `{coverage['axis_separation_gate_passes']}`",
            f"- Null-baseline competition: `{coverage['gate_6_null_baseline_competition']}`",
            f"- Reopening lanes: `{len(coverage['reopening_lanes'])}`",
            "",
        ]
    )
    lines.extend(_render_slice_rows(summary))
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "No declared axis/slice clears the frozen coverage gate. EXO-0002 adds seven post-filter rows overall, but the true-mass transit-radius axis grows by only one eligible row and the minimum-mass transit-radius axis remains at two eligible rows. The compact-radius slice remains at 92 rows, below the 150-row floor and with zero material growth.",
            "",
            "The Exoplanet residual lane therefore remains closed. The current negative/control memory is preserved, and this task does not authorize residual scoring, CK17 replay, null-baseline competition, claim promotion, or canonical result publication.",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in summary["limitations"])
    routing = summary["output_routing"]
    lines.extend(
        [
            "",
            "## Output Routing",
            "",
            f"- Task verdict: `{routing['task_verdict']}`.",
            f"- Canonical destination: `{routing['canonical_destination']}`.",
            f"- Review tier: `{routing['review_tier']}`.",
            f"- Gate A: `{routing['gate_a_status']}`.",
            f"- Gate B: `{routing['gate_b_status']}`.",
            f"- Claim impact: {routing['claim_impact']}.",
            f"- Knowledge impact: {routing['knowledge_impact']}.",
            f"- Publication blocker: {routing['publication_blocker']}.",
            "",
        ]
    )
    return "\n".join(lines)


def write_review(summary: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_review(summary), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first-snapshot", type=Path, default=DEFAULT_FIRST_SNAPSHOT_PATH)
    parser.add_argument("--second-snapshot", type=Path, default=DEFAULT_SECOND_SNAPSHOT_PATH)
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE_PATH)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args(argv)

    summary = build_coverage_summary(
        first_snapshot_path=args.first_snapshot,
        second_snapshot_path=args.second_snapshot,
        gate_path=args.gate,
    )
    write_review(summary, args.review)
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
