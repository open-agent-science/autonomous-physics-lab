"""Guards for the TASK-0994 FRB anchor-capsule dry-run helper."""

from __future__ import annotations

from pathlib import Path
import zipfile

import yaml

from scripts.package_frb_prediction_anchor_dry_run import (
    DEFAULT_ARCHIVE_NAME,
    PACKAGE_FILES,
    STAGED_PRED_MEMBER_PATH,
    build_capsule,
    sha256_file,
)

ROOT = Path(__file__).resolve().parents[1]


def test_frb_anchor_dry_run_capsule_is_deterministic(tmp_path: Path) -> None:
    first = build_capsule(ROOT, tmp_path / "first")
    second = build_capsule(ROOT, tmp_path / "second")

    assert first["archive"]["bytes"] == 610063
    assert first["archive"]["sha256"] == "fb0343894b26211b1b0c38723f79d2009a9840e51986bd25a87b823e30a5487f"
    assert second["archive"]["sha256"] == first["archive"]["sha256"]
    assert (tmp_path / "first" / DEFAULT_ARCHIVE_NAME).read_bytes() == (
        tmp_path / "second" / DEFAULT_ARCHIVE_NAME
    ).read_bytes()
    assert sha256_file(tmp_path / "first" / DEFAULT_ARCHIVE_NAME) == first["archive"]["sha256"]


def test_frb_anchor_dry_run_manifest_preserves_no_publication_boundary(tmp_path: Path) -> None:
    manifest = build_capsule(ROOT, tmp_path / "capsule")

    assert manifest["task_id"] == "TASK-0994"
    assert manifest["dry_run"] is True
    assert manifest["archive"]["committed_to_repository"] is False
    assert manifest["archive"]["compression"] == "zip_stored"
    assert manifest["archive"]["fixed_zip_timestamp"] == "1980-01-01T00:00:00"
    assert manifest["policy"] == {
        "release_tag_created": False,
        "github_release_created": False,
        "external_upload_attempted": False,
        "doi_minted_or_declined": False,
        "prediction_registry_written": False,
        "registered_pred_payload_changed": False,
        "result_claim_knowledge_changed": False,
        "no_claim_boundary_preserved": True,
    }


def test_frb_anchor_dry_run_allowlist_matches_committed_pins(tmp_path: Path) -> None:
    manifest = build_capsule(ROOT, tmp_path / "capsule")
    files_by_path = {item["path"]: item for item in manifest["files"]}

    for entry in PACKAGE_FILES:
        item = files_by_path[entry.path]
        assert item["kind"] == "committed_file"
        assert item["role"] == entry.role
        assert item["bytes"] == entry.bytes
        assert item["sha256"] == entry.sha256

    staged = files_by_path[STAGED_PRED_MEMBER_PATH]
    assert staged["kind"] == "generated_staged_payload"
    assert staged["registration_status"] == "staged_not_registered"
    assert staged["target_count"] == 479
    assert staged["draft_entry_targets_sha256"] == (
        "b4b26d63b53866644332a7ffb325db30ba5f9ec5ced90833e9a4dc4d393ae2bf"
    )


def test_frb_anchor_dry_run_zip_members_are_stored_and_fixed_timestamp(tmp_path: Path) -> None:
    manifest = build_capsule(ROOT, tmp_path / "capsule")
    archive_path = Path(manifest["archive"]["path"])
    expected_names = [item["path"] for item in sorted(manifest["files"], key=lambda row: row["order"])]

    with zipfile.ZipFile(archive_path) as archive:
        assert archive.namelist() == expected_names
        for info in archive.infolist():
            assert info.compress_type == zipfile.ZIP_STORED
            assert info.date_time == (1980, 1, 1, 0, 0, 0)

        staged_payload = yaml.safe_load(archive.read(STAGED_PRED_MEMBER_PATH))
    assert staged_payload["prediction_id"] == "PRED-0001"
    assert staged_payload["registry_status"] == "REGISTERED"
    assert staged_payload["registered_at_utc"] == "SET_BY_MAINTAINER_PREDICTION_FREEZE_DECISION"
    assert staged_payload["source_state"]["git_commit"] == "SET_TO_APPROVED_FREEZE_COMMIT"
    assert len(staged_payload["target_set"]["targets"]) == 479
