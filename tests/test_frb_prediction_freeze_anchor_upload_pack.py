"""Guards for the TASK-1020 FRB prediction-freeze anchor upload pack."""

from __future__ import annotations

from pathlib import Path
import zipfile

from scripts.package_frb_prediction_freeze_anchor_capsule import (
    BOARD_SYNC_MAIN_COMMIT,
    DEFAULT_ARCHIVE_NAME,
    PACKAGE_FILES,
    REGISTRATION_MERGE_COMMIT,
    SOURCE_FREEZE_COMMIT,
    SUGGESTED_TAG,
    build_capsule,
    sha256_file,
    verify_pack_manifest_matches_allowlist,
)


ROOT = Path(__file__).resolve().parents[1]


def test_frb_anchor_upload_pack_capsule_is_deterministic(tmp_path: Path) -> None:
    first = build_capsule(ROOT, tmp_path / "first")
    second = build_capsule(ROOT, tmp_path / "second")

    assert first["archive"]["bytes"] == 608_067
    assert first["archive"]["sha256"] == (
        "7f7f44e83dca50b84ba5f2ce310b305172140c04fcf7ae9484fbab0dfa8e1039"
    )
    assert first["archive"]["md5"] == "bfaa5aa17006c4f6b1697267d96fef8b"
    assert second["archive"]["sha256"] == first["archive"]["sha256"]
    assert (tmp_path / "first" / DEFAULT_ARCHIVE_NAME).read_bytes() == (
        tmp_path / "second" / DEFAULT_ARCHIVE_NAME
    ).read_bytes()
    assert sha256_file(tmp_path / "first" / DEFAULT_ARCHIVE_NAME) == first["archive"]["sha256"]


def test_frb_anchor_upload_pack_uses_approved_nine_path_manifest(tmp_path: Path) -> None:
    verify_pack_manifest_matches_allowlist(ROOT)
    manifest = build_capsule(ROOT, tmp_path / "capsule")
    files_by_path = {item["path"]: item for item in manifest["files"]}

    assert len(PACKAGE_FILES) == 9
    assert manifest["source_freeze_commit"] == SOURCE_FREEZE_COMMIT
    assert manifest["registration_merge_commit"] == REGISTRATION_MERGE_COMMIT
    assert manifest["board_sync_main_commit"] == BOARD_SYNC_MAIN_COMMIT
    assert manifest["suggested_tag"] == SUGGESTED_TAG

    for entry in PACKAGE_FILES:
        item = files_by_path[entry.path]
        assert item["role"] == entry.role
        assert item["bytes"] == entry.bytes
        assert item["sha256"] == entry.sha256


def test_frb_anchor_upload_pack_zip_members_are_stored_and_fixed_timestamp(tmp_path: Path) -> None:
    manifest = build_capsule(ROOT, tmp_path / "capsule")
    archive_path = Path(manifest["archive"]["path"])
    expected_names = [entry.path for entry in PACKAGE_FILES]

    with zipfile.ZipFile(archive_path) as archive:
        assert archive.namelist() == expected_names
        for info in archive.infolist():
            assert info.compress_type == zipfile.ZIP_STORED
            assert info.date_time == (1980, 1, 1, 0, 0, 0)


def test_frb_anchor_upload_pack_preserves_no_publication_boundary(tmp_path: Path) -> None:
    manifest = build_capsule(ROOT, tmp_path / "capsule")

    assert manifest["task_id"] == "TASK-1020"
    assert manifest["archive"]["committed_to_repository"] is False
    assert manifest["policy"] == {
        "release_tag_created_by_agent": False,
        "github_release_created_by_agent": False,
        "external_upload_attempted_by_agent": False,
        "doi_minted_or_declined_by_agent": False,
        "prediction_payload_changed": False,
        "result_claim_knowledge_changed": False,
        "reveal_labels_inspected": False,
        "no_claim_boundary_preserved": True,
    }
