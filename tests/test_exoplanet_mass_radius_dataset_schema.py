"""Validation coverage for the pinned PSCompPars exoplanet snapshot."""

from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

from physics_lab.datasets.exoplanets import load_and_filter, load_exoplanet_snapshot, summarize
from physics_lab.registry.validation import validate_document


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "data" / "exoplanets" / "exo-0001-pscomppars-snapshot.yaml"
SOURCE_MANIFEST_PATH = ROOT / "data" / "exoplanets" / "source_manifest.yaml"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        payload = yaml.safe_load(fh)
    assert isinstance(payload, dict)
    return payload


def test_pscomppars_snapshot_validates_against_schema_and_loader() -> None:
    payload = _load_yaml(SNAPSHOT_PATH)

    validate_document(payload, "exoplanet_mass_radius", SNAPSHOT_PATH)
    loaded = load_exoplanet_snapshot(SNAPSHOT_PATH)

    assert loaded["dataset_id"] == "exo-0001-pscomppars-snapshot"
    assert loaded["status"] == "curated"
    assert loaded["snapshot_provenance"]["snapshot_kind"] == "composite_catalog_snapshot"
    assert loaded["snapshot_provenance"]["live_external_fetch_allowed"] is False
    assert len(loaded["entries"]) == 6291


def test_pscomppars_snapshot_filter_counts_are_pinned() -> None:
    summary = summarize(load_and_filter(SNAPSHOT_PATH))

    assert summary["total_rows"] == 6291
    assert summary["pre_filter_included_count"] == 6157
    assert summary["post_filter_included_count"] == 4301
    assert summary["mass_class_counts"] == {
        "minimum_mass_msini": 986,
        "not_measured": 3202,
        "true_mass": 2103,
    }
    assert summary["exclusion_reason_counts"] == {
        "mass_and_radius_absent": 16,
        "mass_provenance_requires_source_specific_review": 10,
        "mass_relative_uncertainty_above_threshold": 578,
        "radius_inferred_from_non_transit_method": 34,
        "radius_relative_uncertainty_above_threshold": 1278,
        "solution_type_not_confirmed": 74,
    }


def test_pscomppars_manifest_checksums_match_committed_files() -> None:
    manifest = _load_yaml(SOURCE_MANIFEST_PATH)
    source = manifest["sources"][0]

    raw_path = ROOT / source["raw_snapshot_path"]
    normalized_path = ROOT / source["normalized_snapshot_path"]

    assert raw_path == ROOT / "data" / "exoplanets" / "raw" / "exo-pscomppars-20260523T171549Z.csv"
    assert normalized_path == SNAPSHOT_PATH
    assert source["raw_checksum_sha256"] == _sha256(raw_path)
    assert source["normalized_checksum_sha256"] == _sha256(normalized_path)
    assert source["row_count"] == 6291
    assert source["included_post_filter_count"] == 4301
    assert source["excluded_count"] == 1990


def test_pscomppars_snapshot_preserves_separate_row_classes() -> None:
    payload = load_exoplanet_snapshot(SNAPSHOT_PATH)
    classes = set(payload["row_class_coverage"])

    assert classes == {
        "direct_mass_radius_measurement",
        "model_inferred",
        "rv_minimum_mass_only",
        "transit_radius_only",
        "transit_radius_with_rv_minimum_mass",
    }
    assert all(entry["source_id"] == "EXO-SRC-CLASS-001" for entry in payload["entries"])
