import hashlib
import json
from functools import reduce
from math import gcd
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/materials/oqmd_live_api_2026-07-14_manifest.yaml"
RAW = ROOT / "data/materials/snapshots/oqmd_live_api_2026-07-14_page_0000.json"
NORMALIZED = ROOT / "data/materials/oqmd_live_api_2026-07-14_normalized.json"
MD0002 = ROOT / "data/materials/md-0002-materials-project-stable-ternary-oxides.yaml"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reduced_composition(composition: dict[str, int]) -> str:
    divisor = reduce(gcd, (int(value) for value in composition.values()))
    return "-".join(
        f"{element}{int(composition[element]) // divisor}"
        for element in sorted(composition)
    )


def test_pinned_oqmd_bytes_and_api_page_replay() -> None:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    raw = json.loads(RAW.read_text(encoding="utf-8"))

    assert RAW.stat().st_size == manifest["raw_snapshot"]["bytes"] == 94115
    assert _sha256(RAW) == manifest["raw_snapshot"]["sha256"]
    assert len(raw["data"]) == raw["meta"]["data_returned"] == 373
    assert raw["meta"]["data_available"] == 373
    assert raw["meta"]["more_data_available"] is False
    assert len({row["entry_id"] for row in raw["data"]}) == 373
    assert all(row["ntypes"] == 3 and row["stability"] == 0 for row in raw["data"])


def test_independent_overlap_and_normalized_count_replay() -> None:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    raw = json.loads(RAW.read_text(encoding="utf-8"))["data"]
    normalized = json.loads(NORMALIZED.read_text(encoding="utf-8"))
    md0002 = yaml.safe_load(MD0002.read_text(encoding="utf-8"))

    md_compositions = {
        _reduced_composition(row["composition"]) for row in md0002["rows"]
    }
    normalized_compositions = {
        row["reduced_composition"] for row in normalized["rows"]
    }
    raw_by_id = {row["entry_id"]: row for row in raw}
    excluded_ids = {row["entry_id"] for row in manifest["exclusion_ledger"]}

    assert len(md_compositions) == 360
    assert len(excluded_ids) == 201
    assert len(raw_by_id) - len(excluded_ids) == len(normalized["rows"]) == 172
    assert normalized_compositions.isdisjoint(md_compositions)
    assert {row["entry_id"] for row in normalized["rows"]} == (
        set(raw_by_id) - excluded_ids
    )


def test_normalized_hash_schema_semantics_and_rights() -> None:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    normalized = json.loads(NORMALIZED.read_text(encoding="utf-8"))

    assert NORMALIZED.stat().st_size == 114834
    assert _sha256(NORMALIZED) == (
        "af8991aefda6f408a3ad33251aa5564f5fed37a7d527b696d68442971bc978a4"
    )
    assert manifest["semantics"]["cross_source_value_comparison_allowed"] is False
    assert manifest["missingness"]["no_target_summary_computed"] is True
    assert len(normalized["rows"]) <= manifest["normalized_snapshot"]["hard_cap"]
    assert all(
        row["delta_e_units"] == "eV_per_atom_per_OQMD_canonical_definition"
        and row["band_gap_units"] == "eV"
        and row["provenance_class"] == "computed_dft"
        and row["source_snapshot_id"] == manifest["snapshot_id"]
        for row in normalized["rows"]
    )
