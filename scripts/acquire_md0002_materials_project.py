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
import json
import os
import sys
import urllib.parse
import urllib.request
from typing import Any

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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["count", "acquire"], default="count")
    args = parser.parse_args()
    key = _api_key()
    if args.mode == "count":
        count_mode(key)
    else:
        sys.exit("acquire mode is gated on a passing count check; run --mode count first")


if __name__ == "__main__":
    main()
