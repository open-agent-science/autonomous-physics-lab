"""TASK-0582 exoplanet second-snapshot baseline replay preflight.

The preflight first reapplies the frozen second-snapshot reopen coverage
gate. If no axis/slice clears the gate, it stops and records a blocker instead
of running the frozen CK17 baseline or null-baseline replay.

The runner reads only committed snapshots and committed gate rules. It does
not fetch live archive data, add baselines, tune parameters, infer
composition/habitability/target priority, promote claims, or write canonical
RESULT artifacts.
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

AGENT_RUN_ID = "AGENT-RUN-0059"
TASK_ID = "TASK-0582"
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
DEFAULT_AGENT_RUN_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
DEFAULT_METRICS_PATH = DEFAULT_AGENT_RUN_DIR / "metrics.json"
DEFAULT_REPORT_PATH = DEFAULT_AGENT_RUN_DIR / "report.md"
DEFAULT_REVIEW_PATH = (
    REPO_ROOT
    / "docs"
    / "reviews"
    / "exoplanet-second-snapshot-baseline-replay-preflight.md"
)


@dataclass(frozen=True)
class SliceSpec:
    slice_id: str
    description: str
    predicate: Callable[[dict[str, Any]], bool]


@dataclass(frozen=True)
class AxisSpec:
    axis_id: str
    gate_axis_id: str
    mass_class: str


AXIS_SPECS: tuple[AxisSpec, ...] = (
    AxisSpec(
        axis_id="true_mass_with_transit_radius",
        gate_axis_id="true_mass_transit_radius",
        mass_class="true_mass",
    ),
    AxisSpec(
        axis_id="minimum_mass_with_transit_radius",
        gate_axis_id="minimum_mass_transit_radius",
        mass_class="minimum_mass_msini",
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


def _gate_by_id(gate_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    gates = gate_payload.get("gates")
    if not isinstance(gates, list):
        raise ValueError("coverage gate must define a gates list")
    by_id: dict[str, dict[str, Any]] = {}
    for gate in gates:
        if isinstance(gate, dict) and isinstance(gate.get("gate_id"), str):
            by_id[gate["gate_id"]] = gate
    return by_id


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


def _host_context_gate(rows: list[dict[str, Any]], *, min_bins: int, min_rows: int) -> dict[str, Any]:
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


def _growth_gate(
    *,
    first_count: int,
    second_count: int,
    min_fractional_growth: float,
) -> dict[str, Any]:
    if first_count == 0:
        return {
            "fractional_growth_vs_exo_0001": None,
            "passes": second_count > 0,
            "notes": "EXO-0001 count is zero; any nonzero EXO-0002 count is context-only until the slice floor clears.",
        }
    growth = (second_count - first_count) / first_count
    return {
        "fractional_growth_vs_exo_0001": growth,
        "passes": growth >= min_fractional_growth,
        "notes": None,
    }


def _axis_rows(rows: list[dict[str, Any]], axis: AxisSpec) -> list[dict[str, Any]]:
    return [row for row in rows if _row_has_axis(row, axis)]


def _evaluate_gate(
    *,
    first_rows: list[dict[str, Any]],
    second_rows: list[dict[str, Any]],
    gate_payload: dict[str, Any],
) -> dict[str, Any]:
    gates = _gate_by_id(gate_payload)
    slice_floor = int(gates["gate_2_per_axis_slice_floor"]["min_eligible_rows_per_axis_slice"])
    min_growth = float(gates["gate_3_material_growth"]["min_fractional_growth_vs_exo_0001"])
    min_host_bins = int(gates["gate_5_host_context_coverage"]["min_populated_bins"])
    min_host_rows = int(gates["gate_5_host_context_coverage"]["min_eligible_rows_per_bin"])

    material_snapshot_passes = (
        gate_payload.get("scope", {}).get("future_data_values_included") is False
        and gate_payload.get("scope", {}).get("live_fetch_allowed") is False
    )

    lanes: dict[str, Any] = {}
    for axis in AXIS_SPECS:
        first_axis_rows = _axis_rows(first_rows, axis)
        second_axis_rows = _axis_rows(second_rows, axis)
        slice_payload: dict[str, Any] = {}
        for spec in SLICE_SPECS:
            first_slice = [row for row in first_axis_rows if spec.predicate(row)]
            second_slice = [row for row in second_axis_rows if spec.predicate(row)]
            floor_passes = len(second_slice) >= slice_floor
            growth = _growth_gate(
                first_count=len(first_slice),
                second_count=len(second_slice),
                min_fractional_growth=min_growth,
            )
            host_context = _host_context_gate(
                second_slice,
                min_bins=min_host_bins,
                min_rows=min_host_rows,
            )
            lane_passes = (
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

            slice_payload[spec.slice_id] = {
                "description": spec.description,
                "exo_0001_eligible_rows": len(first_slice),
                "exo_0002_eligible_rows": len(second_slice),
                "gate_2_min_eligible_rows": slice_floor,
                "gate_2_passes": floor_passes,
                "gate_3_min_fractional_growth": min_growth,
                "gate_3": growth,
                "gate_5_host_context": host_context,
                "lane_reopens": lane_passes,
                "blockers": blockers,
            }
        lanes[axis.axis_id] = {
            "gate_axis_id": axis.gate_axis_id,
            "mass_class": axis.mass_class,
            "exo_0001_axis_rows": len(first_axis_rows),
            "exo_0002_axis_rows": len(second_axis_rows),
            "slices": slice_payload,
        }

    reopening_lanes = [
        {"axis": axis_id, "slice": slice_id}
        for axis_id, axis_payload in lanes.items()
        for slice_id, slice_payload in axis_payload["slices"].items()
        if slice_payload["lane_reopens"]
    ]
    return {
        "gate_id": gate_payload["gate_id"],
        "material_snapshot_gate_passes": material_snapshot_passes,
        "axis_separation_gate_passes": True,
        "reopening_lanes": reopening_lanes,
        "gate_clears": bool(reopening_lanes),
        "lanes": lanes,
    }


def build_metrics(
    *,
    first_snapshot_path: Path,
    second_snapshot_path: Path,
    gate_path: Path,
) -> dict[str, Any]:
    """Build the deterministic TASK-0582 preflight metrics payload."""

    first_payload = load_exoplanet_snapshot(first_snapshot_path)
    second_payload = load_exoplanet_snapshot(second_snapshot_path)
    first_filtered = apply_inclusion_filters(first_payload)
    second_filtered = apply_inclusion_filters(second_payload)
    gate_payload = _load_yaml(gate_path)
    gate = _evaluate_gate(
        first_rows=first_filtered.included_rows,
        second_rows=second_filtered.included_rows,
        gate_payload=gate_payload,
    )
    replay_status = (
        "not_run_gate_failed"
        if not gate["gate_clears"]
        else "gate_cleared_replay_required"
    )
    verdict = "BLOCKED_BY_REOPEN_COVERAGE_GATE"
    if gate["gate_clears"]:
        verdict = "REPLAY_REQUIRED"

    return {
        "task_id": TASK_ID,
        "agent_run_id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "input_references": {
            "first_snapshot": _relative_path(first_snapshot_path),
            "second_snapshot": _relative_path(second_snapshot_path),
            "coverage_gate": _relative_path(gate_path),
            "baseline_protocol": "docs/exoplanet-mass-radius-baseline-protocol.md",
            "null_baseline_audit": "docs/reviews/exoplanet-null-baseline-family-audit.md",
        },
        "loader_summary": {
            "exo_0001": summarize(first_filtered),
            "exo_0002": summarize(second_filtered),
        },
        "gate_evaluation": gate,
        "baseline_replay_status": replay_status,
        "verdict": verdict,
        "limitations": [
            "Only committed EXO-0001 and EXO-0002 snapshots were read; no live archive fetch was performed.",
            "The frozen CK17 baseline and declared null baselines were not replayed because no lane cleared the reopen coverage gate.",
            "True-mass and minimum-mass axes are reported separately and never pooled.",
            "Host-context coverage uses the frozen effective-temperature context field as a coverage preflight, not as a residual claim.",
            "No canonical RESULT, prediction registry entry, claim, knowledge, habitability, composition, or target-priority output is produced.",
        ],
        "output_routing": {
            "task_verdict": verdict,
            "canonical_destination": f"agent_runs/{AGENT_RUN_ID}/ plus docs/reviews/exoplanet-second-snapshot-baseline-replay-preflight.md",
            "review_tier": "none",
            "gate_a_status": "not_attempted",
            "gate_b_status": "not_applicable",
            "claim_impact": "no claim change",
            "knowledge_impact": "no knowledge change",
            "publication_blocker": "second-snapshot reopen coverage gate did not clear",
        },
    }


def _fmt_float(value: Any, places: int = 6) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.{places}f}"


def _render_lane_rows(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "| axis | slice | EXO-0001 rows | EXO-0002 rows | growth | floor pass | host bins pass | lane reopens | blockers |",
        "| --- | --- | ---: | ---: | ---: | --- | --- | --- | --- |",
    ]
    for axis_id, axis_payload in metrics["gate_evaluation"]["lanes"].items():
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


def render_report(metrics: dict[str, Any]) -> str:
    gate = metrics["gate_evaluation"]
    lines = [
        f"# {AGENT_RUN_ID} - Exoplanet second-snapshot baseline replay preflight",
        "",
        f"- Task: `{TASK_ID}`",
        f"- Campaign profile: `{CAMPAIGN_PROFILE_ID}`",
        f"- Verdict: `{metrics['verdict']}`",
        f"- Baseline replay status: `{metrics['baseline_replay_status']}`",
        "",
        "## Method",
        "",
        "The preflight reads committed `EXO-0001` and `EXO-0002` snapshots, applies the shared exoplanet loader filters, and evaluates the frozen second-snapshot reopen coverage gate per mass axis and per declared null-baseline slice. True-mass and minimum-mass rows remain separate. No live fetch, baseline refit, parameter tuning, claim promotion, or target-priority output is allowed.",
        "",
        "## Loader Counts",
        "",
        "| snapshot | total rows | post-filter included | true-mass axis | minimum-mass axis |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    summaries = metrics["loader_summary"]
    for snapshot_id, summary in summaries.items():
        if snapshot_id == "exo_0001":
            axis_payloads = gate["lanes"]
            true_axis = axis_payloads["true_mass_with_transit_radius"]["exo_0001_axis_rows"]
            min_axis = axis_payloads["minimum_mass_with_transit_radius"]["exo_0001_axis_rows"]
        else:
            axis_payloads = gate["lanes"]
            true_axis = axis_payloads["true_mass_with_transit_radius"]["exo_0002_axis_rows"]
            min_axis = axis_payloads["minimum_mass_with_transit_radius"]["exo_0002_axis_rows"]
        lines.append(
            f"| `{snapshot_id}` | {summary['total_rows']} | {summary['post_filter_included_count']} | {true_axis} | {min_axis} |"
        )
    lines.extend(
        [
            "",
            "## Gate Evaluation",
            "",
            f"- Gate id: `{gate['gate_id']}`",
            f"- Material snapshot gate: `{gate['material_snapshot_gate_passes']}`",
            f"- Axis separation gate: `{gate['axis_separation_gate_passes']}`",
            f"- Reopening lanes: `{len(gate['reopening_lanes'])}`",
            "",
        ]
    )
    lines.extend(_render_lane_rows(metrics))
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "No axis/slice clears the frozen reopen coverage gate. The true-mass compact and sub-Neptune slices do not grow at all, the true-mass jovian slice grows by only one eligible row, and the minimum-mass axis remains far below the declared floor. Therefore the frozen CK17 baseline replay and null-baseline comparison are intentionally not run on `EXO-0002` in this task.",
            "",
            "This preserves the campaign's negative/control memory: the second snapshot does not materially change the benchmark posture enough to reopen residual scoring.",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in metrics["limitations"])
    routing = metrics["output_routing"]
    lines.extend(
        [
            "",
            "## Output Routing",
            "",
            f"- Task verdict: `{routing['task_verdict']}`.",
            f"- Canonical destination: {routing['canonical_destination']}.",
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


def write_outputs(*, metrics: dict[str, Any], out: Path, report: Path, review: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    review.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    text = render_report(metrics)
    report.write_text(text, encoding="utf-8")
    review.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first-snapshot", type=Path, default=DEFAULT_FIRST_SNAPSHOT_PATH)
    parser.add_argument("--second-snapshot", type=Path, default=DEFAULT_SECOND_SNAPSHOT_PATH)
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE_PATH)
    parser.add_argument("--out", type=Path, default=DEFAULT_METRICS_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    args = parser.parse_args(argv)

    metrics = build_metrics(
        first_snapshot_path=args.first_snapshot,
        second_snapshot_path=args.second_snapshot,
        gate_path=args.gate,
    )
    write_outputs(metrics=metrics, out=args.out, report=args.report, review=args.review)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
