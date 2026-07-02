"""Tests for the TASK-0908 deterministic MD-0002 archive helper."""

from __future__ import annotations

import json
from pathlib import Path
import zipfile

import pytest

from scripts.package_materials_md0002_archive import (
    DEFAULT_ARCHIVE_NAME,
    PACKAGE_FILES,
    FIXED_ZIP_TIMESTAMP,
    PackageFile,
    build_archive,
    sha256_file,
    verify_package_files,
)


def _write_file(repo_root: Path, relative_path: str, text: str) -> PackageFile:
    path = repo_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return PackageFile(
        order=1,
        path=relative_path,
        bytes=path.stat().st_size,
        sha256=sha256_file(path),
    )


def test_default_allowlist_preserves_task0900_order_and_hashes() -> None:
    assert len(PACKAGE_FILES) == 12
    assert [entry.order for entry in PACKAGE_FILES] == list(range(1, 13))
    assert PACKAGE_FILES[0].path == (
        "data/materials/md-0002-materials-project-stable-ternary-oxides.yaml"
    )
    assert PACKAGE_FILES[0].sha256 == (
        "516ed06f005157da93fb30490fea2d7a5026146129a4b56ed4c6d4159d81b1d1"
    )
    assert PACKAGE_FILES[-1].path == (
        "docs/reviews/materials-md0002-external-release-decision-packet.md"
    )


def test_build_archive_is_deterministic_and_writes_manifest(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    entry_a = _write_file(repo_root, "data/a.txt", "alpha\n")
    entry_b_path = repo_root / "docs" / "b.txt"
    entry_b_path.parent.mkdir(parents=True, exist_ok=True)
    entry_b_path.write_text("beta\n", encoding="utf-8")
    entry_b = PackageFile(
        order=2,
        path="docs/b.txt",
        bytes=entry_b_path.stat().st_size,
        sha256=sha256_file(entry_b_path),
    )
    entries = (entry_a, entry_b)

    manifest_1 = build_archive(
        repo_root,
        tmp_path / "out-1",
        entries=entries,
        allow_repo_output=True,
    )
    manifest_2 = build_archive(
        repo_root,
        tmp_path / "out-2",
        entries=entries,
        allow_repo_output=True,
    )

    assert manifest_1["archive"]["sha256"] == manifest_2["archive"]["sha256"]
    assert manifest_1["files"] == manifest_2["files"]
    assert manifest_1["policy"] == {
        "doi_minted_or_declined": False,
        "external_upload_attempted": False,
        "holdout_membership_changed": False,
        "md0002_rows_changed": False,
        "no_claim_boundary_preserved": True,
        "release_tag_created": False,
        "result_0021_changed": False,
    }

    archive_path = Path(manifest_1["archive"]["path"])
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.namelist() == ["data/a.txt", "docs/b.txt"]
        for info in archive.infolist():
            assert info.date_time == FIXED_ZIP_TIMESTAMP
            assert info.compress_type == zipfile.ZIP_STORED
            assert info.external_attr >> 16 == 0o644

    manifest_path = archive_path.with_name(
        "MD-0002-materials-project-stable-ternary-oxides-v0.1.0.manifest.json"
    )
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["archive"]["filename"] == DEFAULT_ARCHIVE_NAME
    assert payload["archive"]["committed_to_repository"] is False


def test_verify_package_files_rejects_hash_drift(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    entry = _write_file(repo_root, "data/a.txt", "alpha\n")
    drifted = PackageFile(entry.order, entry.path, entry.bytes, "0" * 64)

    with pytest.raises(ValueError, match="hash/size mismatch"):
        verify_package_files(repo_root, (drifted,))


def test_cli_guard_rejects_repository_output_without_override(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    entry = _write_file(repo_root, "data/a.txt", "alpha\n")

    with pytest.raises(ValueError, match="inside the repository"):
        build_archive(repo_root, repo_root / "_local-output", entries=(entry,))