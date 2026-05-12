from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import yaml

from physics_lab.registry.post_ame2020_holdout import load_post_ame2020_holdout_dataset


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _holdout_path() -> Path:
    return _repo_root() / "data" / "nuclear_masses" / "post_ame2020_holdout.yaml"


def _load_holdout() -> dict[str, object]:
    return load_post_ame2020_holdout_dataset(_holdout_path())


def test_post_ame2020_holdout_matches_schema() -> None:
    repo_root = _repo_root()
    schema_path = repo_root / "physics_lab" / "schemas" / "post_ame2020_holdout.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    payload = yaml.safe_load(_holdout_path().read_text(encoding="utf-8"))

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.absolute_path))

    assert errors == []


def test_post_ame2020_holdout_preserves_source_scope_and_claim_boundary() -> None:
    payload = _load_holdout()

    assert payload["task_id"] == "TASK-0196"
    assert payload["source_policy"]["live_fetch_allowed_in_validation"] is False
    assert payload["source_policy"]["row_values_committed"] is True
    assert payload["source_policy"]["benchmark_metrics_committed"] is False
    assert "No benchmark metrics" in payload["claim_ceiling"]
    assert "doi:10.1007/s41365-025-01821-1" == payload["source_dataset"][
        "stable_source_identifier"
    ]

    artifact_ids = {artifact["artifact_id"] for artifact in payload["source_artifacts"]}
    assert "nst_publisher_html_2026_05_12" in artifact_ids
    assert "nst_embedded_jats_xml_2026_05_12" in artifact_ids
    assert not any("chinaxiv" in artifact_id for artifact_id in artifact_ids)


def test_post_ame2020_holdout_row_counts_and_flags_are_reviewed() -> None:
    payload = _load_holdout()
    entries = payload["entries"]
    row_scope = payload["row_scope"]

    assert len(entries) == 296
    assert row_scope["published_row_count"] == 296
    assert row_scope["committed_row_count"] == 296
    assert row_scope["new_measurement_publication_years"] == [2021, 2022, 2023, 2024]
    assert row_scope["ame2020_extrapolated_comparison_count"] == 55
    assert row_scope["primary_holdout_row_count"] == 295
    assert row_scope["excluded_row_count"] == 1
    assert row_scope["frozen_baseline_overlap_exclusions"] == ["U-238"]

    extrapolated = [
        entry for entry in entries if entry["ame2020_comparison"]["was_extrapolated"]
    ]
    excluded = [entry for entry in entries if not entry["included_in_time_split_holdout"]]
    assert len(extrapolated) == 55
    assert [entry["nuclide_id"] for entry in excluded] == ["U-238"]
    assert "NMD-0002" in excluded[0]["exclusion_reason"]


def test_post_ame2020_holdout_rows_have_physical_ids_and_provenance() -> None:
    payload = _load_holdout()
    source_references = payload["source_references"]
    known_method_ids = {
        assignment["method_id"] for assignment in payload["measurement_method_assignments"]
    }

    seen_row_ids: set[str] = set()
    for entry in payload["entries"]:
        assert entry["row_id"] not in seen_row_ids
        seen_row_ids.add(entry["row_id"])
        assert entry["A"] == entry["Z"] + entry["N"]
        assert entry["nuclide_id"] == f"{entry['symbol']}-{entry['A']}"
        assert entry["measurement_status"] == "measured"
        assert entry["publication_year"] in {2021, 2022, 2023, 2024}
        assert entry["source_reference_id"] in source_references
        assert entry["source_reference_number"] == source_references[entry["source_reference_id"]][
            "reference_number"
        ]
        assert set(entry["measurement_method_ids"]) <= known_method_ids
        assert entry["new_measurement"]["source_unit_as_published"] == "MeV"
        assert entry["new_measurement"]["uncertainty_mev"] >= 0.0
        assert entry["ame2020_comparison"]["source_unit_as_published"] == "MeV"
        assert entry["ame2020_comparison"]["uncertainty_mev"] >= 0.0
        assert isinstance(entry["ame2020_comparison"]["was_extrapolated"], bool)


def test_post_ame2020_holdout_checksum_record_matches_committed_dataset() -> None:
    dataset_path = _holdout_path()
    checksums_path = _repo_root() / "data" / "nuclear_masses" / "post_ame2020_checksums.md"
    digest = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
    checksums = checksums_path.read_text(encoding="utf-8")

    assert digest in checksums
    assert "Tests must not live-fetch" in checksums
    assert "not used for row extraction" in checksums
