"""Validation coverage for the pinned PSCompPars exoplanet snapshot."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

from physics_lab.datasets.exoplanets import apply_inclusion_filters, load_exoplanet_snapshot, summarize
from physics_lab.registry.validation import validate_document


ROOT = Path(__file__).resolve().parents[1]
pytestmark = [
    pytest.mark.resource_sensitive,
    pytest.mark.xdist_group(name="exoplanet_snapshot"),
]
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


@pytest.fixture(scope="module")
def snapshot_payload() -> dict:
    return load_exoplanet_snapshot(SNAPSHOT_PATH)


@pytest.fixture(scope="module")
def snapshot_summary(snapshot_payload: dict) -> dict:
    return summarize(apply_inclusion_filters(snapshot_payload))


def test_pscomppars_snapshot_validates_against_schema_and_loader(snapshot_payload: dict) -> None:
    validate_document(snapshot_payload, "exoplanet_mass_radius", SNAPSHOT_PATH)

    assert snapshot_payload["dataset_id"] == "exo-0001-pscomppars-snapshot"
    assert snapshot_payload["status"] == "curated"
    assert (
        snapshot_payload["snapshot_provenance"]["snapshot_kind"]
        == "composite_catalog_snapshot"
    )
    assert snapshot_payload["snapshot_provenance"]["live_external_fetch_allowed"] is False
    assert len(snapshot_payload["entries"]) == 6291


def test_pscomppars_snapshot_filter_counts_are_pinned(snapshot_summary: dict) -> None:
    assert snapshot_summary["total_rows"] == 6291
    assert snapshot_summary["pre_filter_included_count"] == 6157
    assert snapshot_summary["post_filter_included_count"] == 4301
    assert snapshot_summary["mass_class_counts"] == {
        "minimum_mass_msini": 986,
        "not_measured": 3202,
        "true_mass": 2103,
    }
    assert snapshot_summary["exclusion_reason_counts"] == {
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


def test_pscomppars_snapshot_preserves_separate_row_classes(snapshot_payload: dict) -> None:
    classes = set(snapshot_payload["row_class_coverage"])

    assert classes == {
        "direct_mass_radius_measurement",
        "model_inferred",
        "rv_minimum_mass_only",
        "transit_radius_only",
        "transit_radius_with_rv_minimum_mass",
    }
    assert all(
        entry["source_id"] == "EXO-SRC-CLASS-001" for entry in snapshot_payload["entries"]
    )

def test_pscomppars_normalized_checksum_semantics_are_documented() -> None:
    readme = (ROOT / "data" / "exoplanets" / "README.md").read_text(encoding="utf-8")

    assert "## Normalized Snapshot Checksum" in readme
    assert "normalized_checksum_sha256" in readme
    assert "committed normalized YAML snapshot file exactly as stored in git" in readme
    assert "sha256sum data/exoplanets/exo-0001-pscomppars-snapshot.yaml" in readme
    assert (
        "Get-FileHash data\\exoplanets\\exo-0001-pscomppars-snapshot.yaml -Algorithm SHA256"
        in readme
    )
    assert "not a canonical\nre-serialization of selected rows" in readme
    assert "source-provenance guard only" in readme
