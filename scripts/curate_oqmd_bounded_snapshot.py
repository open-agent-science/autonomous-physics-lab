#!/usr/bin/env python3
"""Normalize the TASK-1042 OQMD snapshot without target-based selection."""

from __future__ import annotations

import argparse
from fractions import Fraction
from functools import reduce
import hashlib
import json
from math import gcd, lcm
from pathlib import Path
import re

import yaml


ALKALI_ALKALINE = {"Li", "Na", "K", "Rb", "Cs", "Be", "Mg", "Ca", "Sr", "Ba"}
FIRST_ROW_TRANSITION = {"Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn"}
FORMULA_PART = re.compile(r"([A-Z][a-z]?)\s*([0-9]+(?:\.[0-9]+)?)")
QUERY_URL = (
    "https://oqmd.org/oqmdapi/formationenergy?"
    "fields=name,entry_id,icsd_id,duplicate_entry_id,prototype,spacegroup,"
    "ntypes,natoms,volume,composition,delta_e,band_gap,stability"
    "&limit=1000&offset=0&noduplicate=True&format=json"
    "&filter=element_set=(Li-Na-K-Rb-Cs-Be-Mg-Ca-Sr-Ba),"
    "(Sc-Ti-V-Cr-Mn-Fe-Co-Ni-Cu-Zn),O%20AND%20ntypes=3%20AND%20stability=0"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reduce_composition(composition: dict[str, object]) -> str:
    fractions = {key: Fraction(str(value)) for key, value in composition.items()}
    denominator = reduce(lcm, (value.denominator for value in fractions.values()), 1)
    integers = {
        key: int(value * denominator) for key, value in fractions.items()
    }
    divisor = reduce(gcd, integers.values())
    return "-".join(f"{key}{integers[key] // divisor}" for key in sorted(integers))


def _parse_oqmd_composition(value: str) -> dict[str, Fraction]:
    matches = FORMULA_PART.findall(value)
    parsed = {element: Fraction(count) for element, count in matches}
    if len(parsed) != 3:
        raise ValueError(f"expected ternary composition, got {value!r}")
    return parsed


def _source_predicate_holds(row: dict[str, object]) -> bool:
    composition = _parse_oqmd_composition(str(row["composition"]))
    elements = set(composition)
    return (
        int(row["ntypes"]) == 3
        and float(row["stability"]) == 0.0
        and "O" in elements
        and len(elements & ALKALI_ALKALINE) == 1
        and len(elements & FIRST_ROW_TRANSITION) == 1
    )


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def curate(
    raw_path: Path,
    md0002_path: Path,
    normalized_path: Path,
    manifest_path: Path,
    fetch_start_utc: str,
    fetch_end_utc: str,
) -> None:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    rows = raw["data"]
    meta = raw["meta"]
    if meta["data_returned"] != len(rows):
        raise ValueError("OQMD meta/data row-count mismatch")
    if meta["data_available"] > 2000 or len(rows) > 2000:
        raise ValueError("CAP_EXCEEDED")
    if meta["more_data_available"] or raw["links"].get("next"):
        raise ValueError("unexpected pagination for bounded snapshot")
    if not all(_source_predicate_holds(row) for row in rows):
        raise ValueError("source predicate mismatch")

    entry_ids = [int(row["entry_id"]) for row in rows]
    if len(entry_ids) != len(set(entry_ids)):
        raise ValueError("duplicate OQMD entry_id in noduplicate snapshot")

    md0002 = yaml.safe_load(md0002_path.read_text(encoding="utf-8"))
    md_rows = [
        row for row in md0002["rows"]
        if row["inclusion_status"] == "included"
    ]
    md_compositions = {
        _reduce_composition(row["composition"]) for row in md_rows
    }
    md_composition_spacegroups = {
        (_reduce_composition(row["composition"]), row["spacegroup_symbol"])
        for row in md_rows
    }

    normalized_rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    composition_spacegroup_coincidences: list[dict[str, object]] = []
    for row in sorted(rows, key=lambda item: int(item["entry_id"])):
        composition = _reduce_composition(_parse_oqmd_composition(row["composition"]))
        identity = {
            "entry_id": int(row["entry_id"]),
            "name": row["name"],
            "reduced_composition": composition,
            "spacegroup": row["spacegroup"],
            "duplicate_entry_id": row["duplicate_entry_id"],
        }
        if composition in md_compositions:
            exclusions.append({**identity, "reason": "md0002_reduced_composition_overlap"})
            if (composition, row["spacegroup"]) in md_composition_spacegroups:
                composition_spacegroup_coincidences.append(identity)
            continue
        if row["delta_e"] is None or row["band_gap"] is None:
            exclusions.append({**identity, "reason": "required_target_field_missing"})
            continue
        normalized_rows.append(
            {
                "entry_id": int(row["entry_id"]),
                "name": row["name"],
                "reduced_composition": composition,
                "composition": row["composition"],
                "icsd_id": row["icsd_id"],
                "duplicate_entry_id": row["duplicate_entry_id"],
                "prototype": row["prototype"],
                "spacegroup": row["spacegroup"],
                "ntypes": int(row["ntypes"]),
                "natoms": int(row["natoms"]),
                "volume": row["volume"],
                "delta_e": row["delta_e"],
                "delta_e_units": "eV_per_atom_per_OQMD_canonical_definition",
                "band_gap": row["band_gap"],
                "band_gap_units": "eV",
                "stability": row["stability"],
                "stability_definition": "OQMD_convex_hull_distance",
                "provenance_class": "computed_dft",
                "source_snapshot_id": "oqmd-live-api-2026-07-14",
            }
        )

    normalized = {
        "schema_version": "1",
        "task_id": "TASK-1042",
        "campaign_id": "materials-property-residuals",
        "snapshot_id": "oqmd-live-api-2026-07-14",
        "source_release_context": "post-OQMD-v1.8-live-API-snapshot",
        "provenance_class": "computed_dft",
        "no_claim_boundary": (
            "Bounded computed-DFT source snapshot; not an experimental "
            "replication or a materials-design dataset."
        ),
        "selection_policy": (
            "Predeclared chemistry identifiers, stability=0, ntypes=3, "
            "noduplicate=True, MD-0002 reduced-composition exclusion, and "
            "required-field completeness only; no target-value threshold."
        ),
        "rows": normalized_rows,
    }
    _write_json(normalized_path, normalized)

    raw_hash = _sha256(raw_path)
    normalized_hash = _sha256(normalized_path)
    manifest = {
        "schema_version": "1",
        "task_id": "TASK-1042",
        "campaign_id": "materials-property-residuals",
        "snapshot_id": "oqmd-live-api-2026-07-14",
        "verdict": "SNAPSHOT_READY_FOR_SPLIT_FREEZE",
        "query_url": QUERY_URL,
        "fetch_window_utc": {
            "start": fetch_start_utc,
            "end": fetch_end_utc,
        },
        "api_meta": {
            "api_version": str(meta["api_version"]),
            "time_stamp": str(meta["time_stamp"]),
            "data_returned": int(meta["data_returned"]),
            "data_available": int(meta["data_available"]),
            "more_data_available": bool(meta["more_data_available"]),
        },
        "raw_snapshot": {
            "path": raw_path.as_posix(),
            "bytes": raw_path.stat().st_size,
            "sha256": raw_hash,
            "raw_concatenated_sha256": raw_hash,
            "page_count": 1,
            "pagination_offsets": [0],
            "raw_artifact_vendored": True,
        },
        "normalized_snapshot": {
            "path": normalized_path.as_posix(),
            "bytes": normalized_path.stat().st_size,
            "sha256": normalized_hash,
            "row_count": len(normalized_rows),
            "hard_cap": 2000,
        },
        "predicate": {
            "alkali_or_alkaline_earth": sorted(ALKALI_ALKALINE),
            "first_row_transition": sorted(FIRST_ROW_TRANSITION),
            "required_element": "O",
            "ntypes": 3,
            "stability": 0,
            "noduplicate": True,
        },
        "semantics": {
            "delta_e": "OQMD computed formation energy; eV/atom per canonical OQMD definition",
            "band_gap": "OQMD DFT-PBE band gap in eV",
            "stability": "OQMD convex-hull distance",
            "cross_source_value_comparison_allowed": False,
            "md0002_field_equivalence_claimed": False,
        },
        "overlap_policy": {
            "md0002_path": md0002_path.as_posix(),
            "md0002_sha256": _sha256(md0002_path),
            "md0002_unique_reduced_compositions": len(md_compositions),
            "excluded_reduced_composition_overlap_count": sum(
                item["reason"] == "md0002_reduced_composition_overlap"
                for item in exclusions
            ),
            "composition_spacegroup_coincidence_count": len(
                composition_spacegroup_coincidences
            ),
            "selection_used_target_values": False,
        },
        "missingness": {
            "excluded_required_target_missing_count": sum(
                item["reason"] == "required_target_field_missing"
                for item in exclusions
            ),
            "no_target_summary_computed": True,
        },
        "exclusion_ledger": exclusions,
        "composition_spacegroup_coincidences": composition_spacegroup_coincidences,
        "routing": {
            "split_assigned": False,
            "metrics_computed": False,
            "result_created": False,
            "claim_or_prediction_created": False,
        },
    }
    manifest_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--md0002", type=Path, required=True)
    parser.add_argument("--normalized", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--fetch-start-utc", required=True)
    parser.add_argument("--fetch-end-utc", required=True)
    args = parser.parse_args()
    curate(
        args.raw,
        args.md0002,
        args.normalized,
        args.manifest,
        args.fetch_start_utc,
        args.fetch_end_utc,
    )


if __name__ == "__main__":
    main()
