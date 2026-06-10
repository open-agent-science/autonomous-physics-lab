"""Validation coverage for the TASK-0565 second PSCompPars acquisition."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from physics_lab.checksums import sha256_file, sha256_lf_canonical_file
from physics_lab.datasets.exoplanets import (
    apply_inclusion_filters,
    load_exoplanet_snapshot,
    normalized_snapshot_checksum,
    summarize,
)
from physics_lab.registry.validation import validate_document


ROOT = Path(__file__).resolve().parents[1]
pytestmark = [
    pytest.mark.resource_sensitive,
    pytest.mark.xdist_group(name="exoplanet_snapshot"),
]
MANIFEST_PATH = ROOT / "data" / "exoplanets" / "second_snapshot_manifest.yaml"
SNAPSHOT_PATH = ROOT / "data" / "exoplanets" / "exo-0002-pscomppars-snapshot.yaml"
QUERY_PATH = ROOT / "data" / "exoplanets" / "snapshot_plans" / "pscomppars_query.adql"
EXPECTED_QUERY_SHA256 = "28b8baf9f14e4ba544658fccbad5ef1271a21f91228afe8afff4db968512acf8"


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        payload = yaml.safe_load(fh)
    assert isinstance(payload, dict)
    return payload


def test_second_snapshot_query_contract_remains_frozen() -> None:
    assert sha256_lf_canonical_file(QUERY_PATH) == EXPECTED_QUERY_SHA256


def test_second_snapshot_manifest_records_acquisition_without_scoring() -> None:
    manifest = _load_yaml(MANIFEST_PATH)
    scope = manifest["scope"]
    acquisition = manifest["planned_acquisition"]
    checksum_policy = manifest["checksum_policy"]

    assert manifest["task_id"] == "TASK-0565"
    assert manifest["status"] == "pinned_snapshot_acquired"
    assert scope["live_fetch_performed"] is True
    assert scope["raw_snapshot_committed"] is True
    assert scope["normalized_snapshot_committed"] is True
    assert scope["benchmark_allowed"] is False
    assert scope["prediction_registry_allowed"] is False
    assert scope["claim_promotion_allowed"] is False
    assert scope["result_artifact_allowed"] is False
    assert acquisition["response_format"] == "csv"
    assert acquisition["normalized_artifact_path"] == (
        "data/exoplanets/exo-0002-pscomppars-snapshot.yaml"
    )
    assert checksum_policy["algorithm"] == "sha256"
    assert manifest["blocked_until_filled"] == []
    assert "no_peek_attestation_by_approved_actor" in manifest


def test_second_snapshot_committed_checksums_replay() -> None:
    manifest = _load_yaml(MANIFEST_PATH)
    acquisition = manifest["planned_acquisition"]
    checksum_policy = manifest["checksum_policy"]
    raw_path = ROOT / acquisition["raw_artifact_path"]
    normalized_path = ROOT / acquisition["normalized_artifact_path"]

    assert raw_path.exists()
    assert normalized_path == SNAPSHOT_PATH
    assert checksum_policy["raw_checksum_sha256"] == sha256_file(raw_path)
    assert checksum_policy["normalized_file_checksum_sha256"] == sha256_lf_canonical_file(
        normalized_path
    )

    payload = load_exoplanet_snapshot(normalized_path)
    assert (
        checksum_policy["normalized_payload_checksum_sha256"]
        == normalized_snapshot_checksum(payload)
    )


def test_second_snapshot_validates_and_loader_counts_match_manifest() -> None:
    manifest = _load_yaml(MANIFEST_PATH)
    acquisition = manifest["planned_acquisition"]
    payload = load_exoplanet_snapshot(SNAPSHOT_PATH)
    summary = summarize(apply_inclusion_filters(payload))

    validate_document(payload, "exoplanet_mass_radius", SNAPSHOT_PATH)
    assert payload["dataset_id"] == "exo-0002-pscomppars-snapshot"
    assert payload["snapshot_provenance"]["live_external_fetch_allowed"] is False
    assert all(str(entry["row_id"]).startswith("EXO-0002-") for entry in payload["entries"])
    assert acquisition["normalized_row_count"] == len(payload["entries"])
    assert acquisition["raw_row_count"] == len(payload["entries"])
    assert acquisition["included_post_filter_count"] == summary[
        "post_filter_included_count"
    ]
    assert acquisition["excluded_count"] == len(payload["entries"]) - summary[
        "post_filter_included_count"
    ]
    assert {
        "direct_mass_radius_measurement",
        "transit_radius_with_rv_minimum_mass",
        "rv_minimum_mass_only",
        "transit_radius_only",
    }.issubset(set(summary["row_class_counts"]))
