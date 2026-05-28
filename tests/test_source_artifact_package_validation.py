from __future__ import annotations

from pathlib import Path
import shutil

import yaml

from physics_lab.registry.source_artifacts import (
    source_artifact_validation_json,
    validate_source_artifact_package,
)


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "templates" / "source_artifact_package"


def _copy_template(tmp_path: Path) -> Path:
    package_path = tmp_path / "source-package"
    shutil.copytree(TEMPLATE_PATH, package_path)
    return package_path


def _load_provenance(package_path: Path) -> dict[str, object]:
    payload = yaml.safe_load((package_path / "provenance.yaml").read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _write_provenance(package_path: Path, payload: dict[str, object]) -> None:
    (package_path / "provenance.yaml").write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )


def _valid_payload(package_path: Path) -> dict[str, object]:
    payload = _load_provenance(package_path)
    payload["package_id"] = "SRC-PKG-TEST-0001"
    payload["task_id"] = "TASK-9999"
    payload["package_status"] = "SOURCE_ARTIFACT_PINNED"
    payload["campaign_profile_id"] = "campaign-test"
    payload["source_id"] = "source-test"
    payload["source_title"] = "Reviewed Source Test"
    payload["source_family"] = "unit_test"
    payload["locators"] = {
        "doi": "10.0000/example",
        "arxiv_id": None,
        "archive_url": None,
        "source_url": "https://example.test/source",
        "citation": "Example Source, 2026.",
    }
    payload["artifact"] = {
        "artifact_type": "csv_snapshot",
        "artifact_path": "raw/source.csv",
        "artifact_locator": None,
        "retrieval_date_utc": "2026-05-25T00:00:00Z",
        "retrieved_by": "unit-test",
        "checksum_sha256": "a" * 64,
        "checksum_scope": "raw_artifact",
        "archive_policy": "committed_with_checksum",
        "value_bearing_artifact": True,
    }
    payload["redistribution"] = {
        "redistribution_status": "raw_artifact_redistributable_with_attribution",
        "license_note": "Unit-test package with explicit redistribution posture.",
        "citation_note": "Cite Example Source, 2026.",
        "raw_artifact_commit_allowed": True,
        "derived_artifact_commit_allowed": True,
    }
    payload["row_admissibility"] = {
        "row_class": "direct_measurement",
        "inclusion_status": "requires_review",
        "row_schema_kind": "unit_test_rows",
        "extraction_method": "csv_snapshot",
        "uncertainty_semantics": "total_uncertainty_reported",
        "accepted_for_benchmark": False,
        "blocker_reasons": ["EXTRACTION_NOT_REVIEWED"],
    }
    payload["review"] = {
        "review_status": "needs_source_review",
        "reviewed_by": None,
        "review_notes": "Unit-test package.",
        "allowed_next_step": "source_review",
    }
    return payload


def test_source_artifact_package_accepts_valid_package(tmp_path: Path) -> None:
    package_path = _copy_template(tmp_path)
    _write_provenance(package_path, _valid_payload(package_path))

    result = validate_source_artifact_package(package_path)

    assert result.ok
    assert result.error_count == 0


def test_source_artifact_package_accepts_checksum_sidecar(tmp_path: Path) -> None:
    package_path = _copy_template(tmp_path)
    payload = _valid_payload(package_path)
    artifact = payload["artifact"]
    assert isinstance(artifact, dict)
    artifact["checksum_sha256"] = None
    raw_dir = package_path / "raw"
    raw_dir.mkdir(exist_ok=True)
    (raw_dir / "source.csv.sha256").write_text("b" * 64 + "  source.csv\n", encoding="utf-8")
    _write_provenance(package_path, payload)

    result = validate_source_artifact_package(package_path)

    assert result.ok


def test_source_artifact_package_rejects_missing_checksum(tmp_path: Path) -> None:
    package_path = _copy_template(tmp_path)
    payload = _valid_payload(package_path)
    artifact = payload["artifact"]
    assert isinstance(artifact, dict)
    artifact["checksum_sha256"] = None
    artifact["archive_policy"] = "required_before_value_use"
    _write_provenance(package_path, payload)

    result = validate_source_artifact_package(package_path)

    assert not result.ok
    assert {issue.code for issue in result.issues} == {
        "CHECKSUM_OR_ARCHIVE_POLICY_MISSING"
    }


def test_source_artifact_package_rejects_missing_license_review(tmp_path: Path) -> None:
    package_path = _copy_template(tmp_path)
    payload = _valid_payload(package_path)
    redistribution = payload["redistribution"]
    assert isinstance(redistribution, dict)
    redistribution["redistribution_status"] = "not_reviewed"
    _write_provenance(package_path, payload)

    result = validate_source_artifact_package(package_path)

    assert not result.ok
    assert "LICENSE_REVIEW_MISSING" in {issue.code for issue in result.issues}


def test_source_artifact_package_rejects_missing_row_class(tmp_path: Path) -> None:
    package_path = _copy_template(tmp_path)
    payload = _valid_payload(package_path)
    row_admissibility = payload["row_admissibility"]
    assert isinstance(row_admissibility, dict)
    row_admissibility["row_class"] = None
    _write_provenance(package_path, payload)

    result = validate_source_artifact_package(package_path)

    assert not result.ok
    assert "ROW_CLASS_MISSING" in {issue.code for issue in result.issues}


def test_source_artifact_package_accepts_blocker_only_package(tmp_path: Path) -> None:
    package_path = _copy_template(tmp_path)
    payload = _valid_payload(package_path)
    payload["package_status"] = "METADATA_ONLY_BLOCKER"
    artifact = payload["artifact"]
    assert isinstance(artifact, dict)
    artifact["artifact_path"] = None
    artifact["value_bearing_artifact"] = False
    artifact["checksum_sha256"] = None
    artifact["checksum_scope"] = "not_applicable_metadata_only"
    artifact["archive_policy"] = "metadata_only_locator_preserved"
    redistribution = payload["redistribution"]
    assert isinstance(redistribution, dict)
    redistribution["redistribution_status"] = "metadata_only_allowed"
    row_admissibility = payload["row_admissibility"]
    assert isinstance(row_admissibility, dict)
    row_admissibility["row_class"] = "source_candidate_only"
    row_admissibility["inclusion_status"] = "metadata_only"
    row_admissibility["blocker_reasons"] = ["SOURCE_ARTIFACT_NOT_REDISTRIBUTABLE"]
    _write_provenance(package_path, payload)

    result = validate_source_artifact_package(package_path)

    assert result.ok


def test_source_artifact_package_rejects_blocker_without_blocker_fields(
    tmp_path: Path,
) -> None:
    package_path = _copy_template(tmp_path)
    payload = _valid_payload(package_path)
    payload["package_status"] = "METADATA_ONLY_BLOCKER"
    row_admissibility = payload["row_admissibility"]
    assert isinstance(row_admissibility, dict)
    row_admissibility["blocker_reasons"] = []
    _write_provenance(package_path, payload)

    result = validate_source_artifact_package(package_path)

    assert not result.ok
    assert "BLOCKER_FIELDS_MISSING" in {issue.code for issue in result.issues}


def test_source_artifact_package_json_report(tmp_path: Path) -> None:
    package_path = _copy_template(tmp_path)
    _write_provenance(package_path, _valid_payload(package_path))

    result = validate_source_artifact_package(package_path)
    report = source_artifact_validation_json(result)

    assert '"ok": true' in report
    assert '"package_id"' in report
