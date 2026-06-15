#!/usr/bin/env python3
"""Maintainer-gated MD-0002 Materials Project acquisition (TASK-0738).

Runs the TASK-0737-approved narrowed stable-ternary-oxide predicate against the
Materials Project summary API and either reports the included row count
(``--mode count``) or commits the pinned snapshot + normalized combined dataset
(``--mode acquire``).

Discipline:
- ``MP_API_KEY`` is read from the environment only; it is never printed or
  written to any artifact.
- No row inclusion uses formation-energy or band-gap *values*; inclusion is by
  chemistry (cation families + axis presence) only, per the no-peek contract.
- The 1500-row-per-axis cap is enforced; if exceeded, the run stops and reports.
- No baseline, residual, ranking, prediction, or claim is produced.

Approved predicate (docs/reviews/materials-md0002-narrowed-predicate-decision.md):
stable ternary oxide A-B-O where A is one alkali/alkaline-earth cation and B is
one first-row (3d) transition-metal cation, with both axes present.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

API_BASE = "https://api.materialsproject.org"
SUMMARY_ENDPOINT = f"{API_BASE}/materials/summary/"
HEARTBEAT_ENDPOINT = f"{API_BASE}/heartbeat"

CAP_PER_AXIS = 1500
TARGET_LOW = 600

ALKALI_ALKALINE_EARTH = frozenset(
    {"Li", "Na", "K", "Rb", "Cs", "Be", "Mg", "Ca", "Sr", "Ba"}
)
ALKALI_ONLY = frozenset({"Li", "Na", "K", "Rb", "Cs"})
FIRST_ROW_TRANSITION = frozenset(
    {"Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn"}
)

FETCH_FIELDS = [
    "material_id",
    "formula_pretty",
    "composition",
    "elements",
    "energy_above_hull",
    "is_stable",
    "formation_energy_per_atom",
    "band_gap",
    "symmetry",
    "nsites",
    "theoretical",
]


def _api_key() -> str:
    key = os.environ.get("MP_API_KEY", "").strip()
    if not key:
        sys.exit("MP_API_KEY is not set in the environment; never hardcode it.")
    return key


def _get_json(url: str, key: str) -> dict[str, Any]:
    # A non-default User-Agent is required; the API CDN rejects Python-urllib.
    request = urllib.request.Request(
        url,
        headers={"X-API-KEY": key, "User-Agent": "apl-md0002-acquisition/1.0 (curl-like)"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310 (trusted host)
        return json.loads(response.read().decode("utf-8"))


def fetch_stable_ternary_oxides(key: str) -> list[dict[str, Any]]:
    """Fetch every stable ternary oxide candidate (O + exactly 3 elements)."""
    params = {
        "elements": "O",
        "nelements": 3,
        "is_stable": "true",
        "_fields": ",".join(FETCH_FIELDS),
        "_per_page": 1000,
        "_page": 1,
    }
    rows: list[dict[str, Any]] = []
    while True:
        url = f"{SUMMARY_ENDPOINT}?{urllib.parse.urlencode(params)}"
        payload = _get_json(url, key)
        batch = payload.get("data", [])
        rows.extend(batch)
        total = payload.get("meta", {}).get("total_doc")
        if not batch or (total is not None and len(rows) >= total):
            break
        params["_page"] += 1
    return rows


def _non_oxygen_elements(row: dict[str, Any]) -> list[str]:
    elements = row.get("elements") or list((row.get("composition") or {}).keys())
    return [e for e in elements if e != "O"]


def predicate_included(row: dict[str, Any], alkali_set: frozenset[str]) -> bool:
    """Chemistry-only inclusion. Never inspects formation-energy/band-gap value sign."""
    elements = row.get("elements") or list((row.get("composition") or {}).keys())
    if len(set(elements)) != 3 or "O" not in elements:
        return False
    non_o = _non_oxygen_elements(row)
    if len(non_o) != 2:
        return False
    a, b = non_o
    pair_ok = (a in alkali_set and b in FIRST_ROW_TRANSITION) or (
        b in alkali_set and a in FIRST_ROW_TRANSITION
    )
    if not pair_ok:
        return False
    if row.get("energy_above_hull") != 0.0 or row.get("is_stable") is not True:
        return False
    # Axis presence (not value): both planned axes must exist.
    if row.get("formation_energy_per_atom") is None or row.get("band_gap") is None:
        return False
    return True


def count_mode(key: str) -> None:
    candidates = fetch_stable_ternary_oxides(key)
    selected = [r for r in candidates if predicate_included(r, ALKALI_ALKALINE_EARTH)]
    fallback = [r for r in candidates if predicate_included(r, ALKALI_ONLY)]
    db_version = _get_json(HEARTBEAT_ENDPOINT, key).get("db_version")
    print(json.dumps({
        "db_version": db_version,
        "raw_stable_ternary_oxide_candidates": len(candidates),
        "selected_predicate_included_per_axis": len(selected),
        "fallback_predicate_included_per_axis": len(fallback),
        "cap_per_axis": CAP_PER_AXIS,
        "target_low": TARGET_LOW,
        "selected_in_target": TARGET_LOW <= len(selected) <= CAP_PER_AXIS,
        "fallback_in_target": TARGET_LOW <= len(fallback) <= CAP_PER_AXIS,
    }, indent=2))


DFT_FUNCTIONAL = "GGA_or_GGA+U"
METHOD = "DFT (GGA/GGA+U, Materials Project convention)"
LICENSE = "CC BY 4.0"
ATTRIBUTION = (
    "Data from The Materials Project (materialsproject.org), licensed CC BY 4.0; "
    "cite Jain et al., APL Materials 1, 011002 (2013)."
)
NO_CLAIM_BOUNDARY = (
    "MD-0002 dataset artifact only: computed DFT formation energy and band gap "
    "for stable alkali/alkaline-earth + first-row-transition ternary oxides. No "
    "benchmark metric, residual law, material-discovery, design, synthesis, "
    "device, or biomedical claim is made here."
)


def _int_if_whole(value: Any) -> Any:
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def _split_for_index(index: int, total: int) -> str:
    """Deterministic 70/15/15 split over sorted (arbitrary) material_id position.

    Uses cumulative fraction so the ratio is exact regardless of row count. The
    split depends only on material_id ordering, never on property values, so it
    is no-peek clean.
    """
    frac = (index + 0.5) / total
    if frac < 0.70:
        return "train"
    if frac < 0.85:
        return "validation"
    return "holdout"


def acquire_mode(key: str, accept_row_count: int | None) -> None:
    candidates = fetch_stable_ternary_oxides(key)
    included = sorted(
        (r for r in candidates if predicate_included(r, ALKALI_ALKALINE_EARTH)),
        key=lambda r: str(r["material_id"]),
    )
    n = len(included)
    in_target = TARGET_LOW <= n <= CAP_PER_AXIS
    if not in_target and accept_row_count != n:
        sys.exit(
            f"included_per_axis={n} is outside the target [{TARGET_LOW},{CAP_PER_AXIS}]. "
            f"Pass --accept-row-count {n} to record an explicit maintainer acceptance."
        )

    db_version = str(_get_json(HEARTBEAT_ENDPOINT, key).get("db_version"))
    retrieved = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # The snapshot is checksummed, so it must be deterministic over the data:
    # no retrieval timestamp here (that lives in the dataset metadata only), so a
    # re-fetch of the same database_version reproduces the same checksum.
    snapshot = {
        "source": "materials-project",
        "endpoint": SUMMARY_ENDPOINT,
        "database_version": db_version,
        "predicate_id": "md0002_alkali_alkaline_earth_3d_transition_oxide",
        "base_query": {"elements": "O", "nelements": 3, "is_stable": True},
        "included_row_count_per_axis": n,
        "rows": included,
    }
    snapshot_text = json.dumps(snapshot, indent=2, sort_keys=True) + "\n"
    checksum = hashlib.sha256(snapshot_text.encode("utf-8")).hexdigest()

    snapshot_path = REPO_ROOT / "data/materials/snapshots" / f"materials_project_md0002_{db_version}.json"
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(snapshot_text, encoding="utf-8")

    rows: list[dict[str, Any]] = []
    split_counts: dict[str, int] = {"train": 0, "validation": 0, "holdout": 0}
    for index, record in enumerate(included):
        material_id = str(record["material_id"])
        composition = {k: _int_if_whole(v) for k, v in record["composition"].items()}
        cations = sorted(e for e in composition if e != "O")
        split = _split_for_index(index, n)
        split_counts[split] += 1
        shared = {
            "material_id": material_id,
            "formula_pretty": record.get("formula_pretty"),
            "composition": composition,
            "cations": cations,
            "composition_family": "ternary_oxide",
            "nsites": record.get("nsites"),
            "spacegroup_symbol": (record.get("symmetry") or {}).get("symbol"),
            "method": METHOD,
            "dft_functional": DFT_FUNCTIONAL,
            "database_version": db_version,
            "record_locator": material_id,
            "snapshot_checksum_sha256": checksum,
            "energy_above_hull": record.get("energy_above_hull"),
            "is_stable": record.get("is_stable"),
            "source_id": "materials-project",
            "provenance_class": "computed_dft",
            "inclusion_status": "included",
            "exclusion_reason": None,
            "split": split,
        }
        rows.append({
            "row_id": f"MD-0002-FE-{index + 1:04d}",
            "property_kind": "formation_energy_per_atom",
            "value": record["formation_energy_per_atom"],
            "units": "eV_per_atom",
            **shared,
        })
        rows.append({
            "row_id": f"MD-0002-BG-{index + 1:04d}",
            "property_kind": "band_gap",
            "value": record["band_gap"],
            "units": "eV",
            **shared,
        })

    dataset = {
        "dataset_id": "MD-0002-materials-project-stable-ternary-oxides",
        "dataset_family": "MD-0002",
        "dataset_version": "0.1.0",
        "task_id": "TASK-0738",
        "campaign_id": "materials-property-residuals",
        "source_id": "materials-project",
        "source_version": db_version,
        "snapshot_file": f"snapshots/materials_project_md0002_{db_version}.json",
        "snapshot_checksum_sha256": checksum,
        "retrieved_at_utc": retrieved,
        "live_external_fetch_allowed": False,
        "predicate_id": "md0002_alkali_alkaline_earth_3d_transition_oxide",
        "material_scope": "stable_ternary_oxides_alkali_or_alkaline_earth_plus_first_row_transition",
        "license": LICENSE,
        "attribution": ATTRIBUTION,
        "row_count": len(rows),
        "included_materials": n,
        "split_counts_per_axis": split_counts,
        "no_claim_boundary": NO_CLAIM_BOUNDARY,
        "axis_policies": [
            {"property_kind": "formation_energy_per_atom", "units": "eV_per_atom", "provenance_class": "computed_dft"},
            {"property_kind": "band_gap", "units": "eV", "provenance_class": "computed_dft"},
        ],
        "limitations": [
            "Computed DFT values only; not experimental measurements.",
            "Combined single-file dataset (both axes) per the MD-0002 loader contract.",
            "Below the 600-row pre-fetch target; 362 materials accepted by explicit maintainer decision.",
            "No baseline, residual, or claim derived here.",
        ],
        "rows": rows,
    }
    dataset_path = REPO_ROOT / "data/materials/md-0002-materials-project-stable-ternary-oxides.yaml"
    with dataset_path.open("w", encoding="utf-8") as handle:
        handle.write("# Materials Project pinned MD-0002 dataset (TASK-0738). CC BY 4.0; see attribution.\n")
        yaml.safe_dump(dataset, handle, sort_keys=False, default_flow_style=False, allow_unicode=True)

    print(json.dumps({
        "db_version": db_version,
        "included_materials": n,
        "row_count": len(rows),
        "split_counts_per_axis": split_counts,
        "snapshot_checksum_sha256": checksum,
        "snapshot_path": str(snapshot_path.relative_to(REPO_ROOT)),
        "dataset_path": str(dataset_path.relative_to(REPO_ROOT)),
    }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["count", "acquire"], default="count")
    parser.add_argument(
        "--accept-row-count",
        type=int,
        default=None,
        help="Explicit maintainer acceptance of an out-of-target included count.",
    )
    args = parser.parse_args()
    key = _api_key()
    if args.mode == "count":
        count_mode(key)
    else:
        acquire_mode(key, args.accept_row_count)


if __name__ == "__main__":
    main()
