from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/materials/snapshots/oqmd_live_api_2026-07-14_page_0000.json"
NORMALIZED = ROOT / "data/materials/oqmd_live_api_2026-07-14_normalized.json"
MANIFEST = ROOT / "data/materials/oqmd_live_api_2026-07-14_manifest.yaml"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest() -> dict:
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))


def test_snapshot_hashes_api_identity_and_cap() -> None:
    manifest = _manifest()
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    normalized = json.loads(NORMALIZED.read_text(encoding="utf-8"))
    assert manifest["verdict"] == "SNAPSHOT_READY_FOR_SPLIT_FREEZE"
    assert _sha256(RAW) == manifest["raw_snapshot"]["sha256"]
    assert _sha256(NORMALIZED) == manifest["normalized_snapshot"]["sha256"]
    assert manifest["raw_snapshot"]["bytes"] == RAW.stat().st_size
    assert manifest["normalized_snapshot"]["bytes"] == NORMALIZED.stat().st_size
    assert raw["meta"]["api_version"] == "1.0"
    assert raw["meta"]["data_returned"] == len(raw["data"]) == 373
    assert raw["meta"]["data_available"] == 373
    assert raw["meta"]["more_data_available"] is False
    assert raw["links"]["next"] is None
    assert len(normalized["rows"]) == 172
    assert len(normalized["rows"]) <= manifest["normalized_snapshot"]["hard_cap"]


def test_raw_rows_obey_frozen_predicate_and_provider_dedup_semantics() -> None:
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    alkali_alkaline = set(_manifest()["predicate"]["alkali_or_alkaline_earth"])
    transition = set(_manifest()["predicate"]["first_row_transition"])
    entry_ids: list[int] = []
    for row in raw["data"]:
        elements = {
            part.rstrip("0123456789.")
            for part in row["composition"].split()
        }
        assert row["ntypes"] == 3
        assert row["stability"] == 0
        assert "O" in elements
        assert len(elements & alkali_alkaline) == 1
        assert len(elements & transition) == 1
        assert row["duplicate_entry_id"] == row["entry_id"]
        entry_ids.append(row["entry_id"])
    assert len(entry_ids) == len(set(entry_ids))


def test_overlap_exclusions_are_identifier_only_and_complete() -> None:
    manifest = _manifest()
    normalized = json.loads(NORMALIZED.read_text(encoding="utf-8"))
    included = {row["reduced_composition"] for row in normalized["rows"]}
    excluded = {
        row["reduced_composition"]
        for row in manifest["exclusion_ledger"]
        if row["reason"] == "md0002_reduced_composition_overlap"
    }
    assert included.isdisjoint(excluded)
    assert (
        manifest["overlap_policy"]["excluded_reduced_composition_overlap_count"]
        == 201
    )
    assert manifest["overlap_policy"]["composition_spacegroup_coincidence_count"] == 90
    assert manifest["overlap_policy"]["selection_used_target_values"] is False
    assert manifest["missingness"]["excluded_required_target_missing_count"] == 0


def test_normalized_rows_preserve_semantics_without_split_or_metrics() -> None:
    payload = json.loads(NORMALIZED.read_text(encoding="utf-8"))
    forbidden = {"split", "lane", "residual", "metric", "fit", "prediction"}
    entry_ids = []
    for row in payload["rows"]:
        assert row["provenance_class"] == "computed_dft"
        assert row["delta_e_units"] == "eV_per_atom_per_OQMD_canonical_definition"
        assert row["band_gap_units"] == "eV"
        assert forbidden.isdisjoint(row)
        entry_ids.append(row["entry_id"])
    assert entry_ids == sorted(entry_ids)
    assert len(entry_ids) == len(set(entry_ids))
    assert "split" not in payload
