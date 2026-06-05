"""TASK-0581 EXO-0001 vs EXO-0002 snapshot delta audit.

Compares committed normalized exoplanet snapshot YAML files only. The audit
reports row-count, row-class, identifier, field-drift, and previous-slice
overlap diagnostics. It does not fetch live data, compute residuals, refit
baselines, infer planet composition, or promote claims.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.datasets.exoplanets import (  # noqa: E402
    apply_inclusion_filters,
    load_exoplanet_snapshot,
    summarize,
)

TASK_ID = "TASK-0581"
DEFAULT_FIRST = REPO_ROOT / "data/exoplanets/exo-0001-pscomppars-snapshot.yaml"
DEFAULT_SECOND = REPO_ROOT / "data/exoplanets/exo-0002-pscomppars-snapshot.yaml"


def _positive(value: Any) -> bool:
    return isinstance(value, (int, float)) and float(value) > 0.0


def _radius(entry: dict[str, Any]) -> float:
    return float(entry["radius"]["value"])


def _true_mass_transit_radius(entry: dict[str, Any]) -> bool:
    return (
        entry["mass"]["mass_class"] == "true_mass"
        and entry["radius"]["radius_class"] == "transit_radius"
        and _positive(entry["mass"]["value"])
        and _positive(entry["radius"]["value"])
    )


def _minimum_mass_transit_radius(entry: dict[str, Any]) -> bool:
    return (
        entry["mass"]["mass_class"] == "minimum_mass_msini"
        and entry["radius"]["radius_class"] == "transit_radius"
        and _positive(entry["mass"]["value"])
        and _positive(entry["radius"]["value"])
    )


def _slice_predicates() -> dict[str, Callable[[dict[str, Any]], bool]]:
    return {
        "compact_radius_lt1p5Re_true_mass": lambda row: (
            _true_mass_transit_radius(row) and _radius(row) < 1.5
        ),
        "sub_neptune_radius_1p5_4Re_true_mass": lambda row: (
            _true_mass_transit_radius(row) and 1.5 <= _radius(row) < 4.0
        ),
        "jovian_radius_8_16Re_true_mass": lambda row: (
            _true_mass_transit_radius(row) and 8.0 <= _radius(row) < 16.0
        ),
        "hot_jupiter_period_lt10d_radius_8_16Re_true_mass": lambda row: (
            _true_mass_transit_radius(row)
            and 8.0 <= _radius(row) < 16.0
            and _positive(row.get("orbital_period_days"))
            and float(row["orbital_period_days"]) < 10.0
        ),
        "minimum_mass_transit_radius_axis": _minimum_mass_transit_radius,
    }


def _by_planet(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_name: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    for entry in entries:
        name = str(entry["planet_name"])
        if name in by_name:
            duplicates.append(name)
            continue
        by_name[name] = entry
    if duplicates:
        joined = ", ".join(sorted(duplicates)[:5])
        raise ValueError(f"Duplicate planet_name values prevent set delta: {joined}")
    return by_name


def _class_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(str(row["row_class"]) for row in rows).items()))


def _mass_class_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(str(row["mass"]["mass_class"]) for row in rows).items()))


def _changed_field_counts(
    first_by_name: dict[str, dict[str, Any]],
    second_by_name: dict[str, dict[str, Any]],
    overlap: set[str],
) -> dict[str, int]:
    fields: dict[str, Callable[[dict[str, Any]], Any]] = {
        "row_class": lambda row: row["row_class"],
        "mass_class": lambda row: row["mass"]["mass_class"],
        "radius_class": lambda row: row["radius"]["radius_class"],
        "inclusion_status": lambda row: row.get("inclusion_status"),
        "detection_method": lambda row: row.get("detection_method"),
        "host_name": lambda row: (row.get("host_star") or {}).get("name"),
        "source_table_ref": lambda row: row.get("source_table_ref"),
        "mass_value_presence": lambda row: row["mass"].get("value") is not None,
        "radius_value_presence": lambda row: row["radius"].get("value") is not None,
    }
    counts: dict[str, int] = {}
    for field_id, getter in fields.items():
        counts[field_id] = sum(
            1
            for name in overlap
            if getter(first_by_name[name]) != getter(second_by_name[name])
        )
    return dict(sorted(counts.items()))


def _slice_overlap(
    first_rows: list[dict[str, Any]],
    second_rows: list[dict[str, Any]],
) -> dict[str, dict[str, int]]:
    first_by_slice = {
        slice_id: {row["planet_name"] for row in first_rows if predicate(row)}
        for slice_id, predicate in _slice_predicates().items()
    }
    second_by_slice = {
        slice_id: {row["planet_name"] for row in second_rows if predicate(row)}
        for slice_id, predicate in _slice_predicates().items()
    }
    output: dict[str, dict[str, int]] = {}
    for slice_id in _slice_predicates():
        first_names = first_by_slice[slice_id]
        second_names = second_by_slice[slice_id]
        output[slice_id] = {
            "exo0001_count": len(first_names),
            "exo0002_count": len(second_names),
            "overlap_count": len(first_names & second_names),
            "new_in_exo0002": len(second_names - first_names),
            "removed_from_exo0001": len(first_names - second_names),
        }
    return output


def compare_snapshots(first_path: Path, second_path: Path) -> dict[str, Any]:
    first_path = first_path.resolve()
    second_path = second_path.resolve()
    first = load_exoplanet_snapshot(first_path)
    second = load_exoplanet_snapshot(second_path)
    first_filtered = apply_inclusion_filters(first)
    second_filtered = apply_inclusion_filters(second)

    first_entries = list(first["entries"])
    second_entries = list(second["entries"])
    first_by_name = _by_planet(first_entries)
    second_by_name = _by_planet(second_entries)
    first_names = set(first_by_name)
    second_names = set(second_by_name)
    overlap = first_names & second_names

    first_included_by_name = _by_planet(first_filtered.included_rows)
    second_included_by_name = _by_planet(second_filtered.included_rows)
    included_overlap = set(first_included_by_name) & set(second_included_by_name)

    return {
        "task_id": TASK_ID,
        "inputs": {
            "exo0001": str(first_path.relative_to(REPO_ROOT).as_posix()),
            "exo0002": str(second_path.relative_to(REPO_ROOT).as_posix()),
        },
        "snapshot_summaries": {
            "exo0001": summarize(first_filtered),
            "exo0002": summarize(second_filtered),
        },
        "planet_identifier_delta": {
            "exo0001_planet_names": len(first_names),
            "exo0002_planet_names": len(second_names),
            "overlap_planet_names": len(overlap),
            "new_planet_names_in_exo0002": len(second_names - first_names),
            "removed_planet_names_from_exo0001": len(first_names - second_names),
            "post_filter_included_overlap_planet_names": len(included_overlap),
            "new_post_filter_included_in_exo0002": len(
                set(second_included_by_name) - set(first_included_by_name)
            ),
            "removed_post_filter_included_from_exo0001": len(
                set(first_included_by_name) - set(second_included_by_name)
            ),
        },
        "overlap_changed_field_counts": _changed_field_counts(
            first_by_name,
            second_by_name,
            overlap,
        ),
        "overlap_row_class_delta": {
            "exo0001_overlap": _class_counts([first_by_name[name] for name in overlap]),
            "exo0002_overlap": _class_counts([second_by_name[name] for name in overlap]),
        },
        "overlap_mass_class_delta": {
            "exo0001_overlap": _mass_class_counts(
                [first_by_name[name] for name in overlap]
            ),
            "exo0002_overlap": _mass_class_counts(
                [second_by_name[name] for name in overlap]
            ),
        },
        "previous_audit_slice_overlap": _slice_overlap(
            first_filtered.included_rows,
            second_filtered.included_rows,
        ),
        "interpretation_boundary": {
            "residual_metrics_computed": False,
            "baseline_refit_performed": False,
            "live_fetch_performed": False,
            "claim_or_prediction_promotion": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first", type=Path, default=DEFAULT_FIRST)
    parser.add_argument("--second", type=Path, default=DEFAULT_SECOND)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args(argv)

    payload = compare_snapshots(args.first, args.second)
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
