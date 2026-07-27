from __future__ import annotations

from collections import Counter
import hashlib
from pathlib import Path

import pytest
import yaml

from scripts.extract_thermoml_tb_feasible_expansion_fixture import (
    EXPECTED_ARCHIVE_SHA256,
    EXPECTED_CONFLICT_ROW_IDS,
    MAX_ROWS_PER_ARTICLE,
    SELECTED_FAMILIES,
    quantile_target_indices,
    select_additions,
    verify_archive,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data/thermophysical/thermoml_tb_feasible_expansion_fixture.yaml"
RELEASE = ROOT / "data/thermophysical/thermoml_tb_feasible_expansion_release.yaml"
CONTRACT = ROOT / "data/thermophysical/thermoml_tb_feasible_expansion_contract.yaml"
LEGACY_FIXTURE = ROOT / "data/thermophysical/thermoml_tb_audit_fixture.yaml"
EXTRACTOR = ROOT / "scripts/extract_thermoml_tb_feasible_expansion_fixture.py"
TASK = ROOT / "tasks/TASK-1091-extract-thermoml-tb-feasible-expansion-fixture.yaml"

EXPECTED_FAMILY_COUNTS = {
    "acids": 6,
    "esters/lactones": 10,
    "ketones": 8,
    "alcohols/phenols": 10,
    "ethers": 10,
    "halocarbons": 10,
    "aromatic hydrocarbons": 10,
    "alkanes/cycloalkanes": 10,
}


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_fixture_clears_frozen_information_and_rights_gates() -> None:
    fixture = _load(FIXTURE)
    rows = fixture["rows"]
    extraction = fixture["extraction"]
    rights = fixture["rights"]

    assert fixture["task_id"] == "TASK-1091"
    assert fixture["verdict"] == "FIXTURE_EXTRACTION_PASS"
    assert len(rows) == extraction["total_rows"] == 74
    assert extraction["retained_existing_rows"] == 38
    assert extraction["new_identity_rows"] == 36
    assert extraction["family_order"] == list(SELECTED_FAMILIES)
    assert extraction["family_counts"] == EXPECTED_FAMILY_COUNTS
    assert extraction["equal_family_weighted_effective_row_count"] == pytest.approx(
        71.775701,
        abs=1e-6,
    )
    assert extraction["max_rows_per_source_article"] <= MAX_ROWS_PER_ARTICLE
    assert extraction["selection_is_value_blind_to_tb_and_model_outcomes"] is True

    assert rights["reuse_status"] == "limited_factual_extract_with_attribution"
    assert rights["covered_by_repo_license"] is False
    assert rights["max_public_rows_total"] == 80
    assert rights["max_rows_per_source_article"] == 5
    assert rights["source_bytes_redistribution"] is False
    assert rights["raw_archive_or_xml_json_committed"] is False
    assert rights["normalized_corpus_committed"] is False
    assert rights["external_dataset_release_allowed"] is False


def test_fixture_preserves_eligible_rows_and_excludes_legacy_identities_from_additions() -> None:
    fixture = _load(FIXTURE)
    legacy = _load(LEGACY_FIXTURE)
    old_by_id = {row["row_id"]: row for row in legacy["rows"]}
    old_identities = {row["inchi_key"] for row in legacy["rows"]}
    retained = [
        row for row in fixture["rows"] if row["fixture_origin"] == "retained_task0851"
    ]
    additions = [
        row for row in fixture["rows"] if row["fixture_origin"] == "task1091_addition"
    ]

    assert len(retained) == 38
    assert len(additions) == 36
    assert {row["legacy_row_id"] for row in retained}.isdisjoint(
        EXPECTED_CONFLICT_ROW_IDS
    )
    for row in retained:
        expected = dict(old_by_id[row["legacy_row_id"]])
        expected.pop("row_id")
        observed = dict(row)
        observed.pop("row_id")
        observed.pop("fixture_origin")
        observed.pop("legacy_row_id")
        assert observed == expected
    assert {row["inchi_key"] for row in additions}.isdisjoint(old_identities)
    assert len({row["inchi_key"] for row in fixture["rows"]}) == len(fixture["rows"])
    assert len({row["row_id"] for row in fixture["rows"]}) == len(fixture["rows"])


def test_fixture_article_cap_attribution_and_selection_trace_are_complete() -> None:
    fixture = _load(FIXTURE)
    rows = fixture["rows"]
    article_counts = Counter(row["source_doi"] for row in rows)

    assert max(article_counts.values()) == 4
    assert all(row["source_doi"] and row["source_member"] for row in rows)
    assert all(row["expanded_uncertainty_k"] is not None for row in rows)
    assert all(row["conflicting_observations"] is False for row in rows)
    assert all(
        step["forward_steps"] == 0
        for trace in fixture["extraction"]["selection_trace"].values()
        for step in trace
    )


def test_release_manifest_pins_inputs_and_contains_no_machine_path() -> None:
    release = _load(RELEASE)
    fixture = _load(FIXTURE)
    serialized = RELEASE.read_text(encoding="utf-8")

    assert release["verdict"] == "FIXTURE_EXTRACTION_PASS"
    assert release["fixture"]["path"] == (
        "data/thermophysical/thermoml_tb_feasible_expansion_fixture.yaml"
    )
    assert release["fixture"]["sha256"] == _sha256(FIXTURE)
    assert release["fixture"]["row_count"] == len(fixture["rows"]) == 74
    assert release["frozen_inputs"]["contract_sha256"] == _sha256(CONTRACT)
    assert release["frozen_inputs"]["existing_fixture_sha256"] == _sha256(
        LEGACY_FIXTURE
    )
    assert release["frozen_inputs"]["source_archive_sha256"] == (
        EXPECTED_ARCHIVE_SHA256
    )
    assert release["implementation"]["extractor_sha256"] == _sha256(EXTRACTOR)
    assert "/Users/" not in serialized
    assert "/private/" not in serialized


def test_quantile_selection_uses_deterministic_article_cap_fallback() -> None:
    candidates = [
        {
            "molecular_weight_g_mol": float(index),
            "inchi_key": f"identity-{index:02d}",
            "source_doi": "10.example/capped" if index == 4 else f"10.example/{index}",
        }
        for index in range(8)
    ]
    article_counts = Counter({"10.example/capped": MAX_ROWS_PER_ARTICLE})

    selected, trace = select_additions(candidates, 3, article_counts)

    assert quantile_target_indices(8, 3) == [0, 4, 7]
    assert quantile_target_indices(6, 1) == [2]
    assert [row["inchi_key"] for row in selected] == [
        "identity-00",
        "identity-05",
        "identity-07",
    ]
    assert trace == [
        {"target_index": 0, "selected_index": 0, "forward_steps": 0},
        {"target_index": 4, "selected_index": 5, "forward_steps": 1},
        {"target_index": 7, "selected_index": 7, "forward_steps": 0},
    ]


def test_archive_pin_and_task_lifecycle_fail_closed(tmp_path: Path) -> None:
    wrong_archive = tmp_path / "ThermoML.v2020-09-30.tgz"
    wrong_archive.write_bytes(b"not-the-pinned-archive")

    with pytest.raises(ValueError, match="archive pin mismatch"):
        verify_archive(wrong_archive)

    assert _load(TASK)["status"] == "REVIEW_READY"
