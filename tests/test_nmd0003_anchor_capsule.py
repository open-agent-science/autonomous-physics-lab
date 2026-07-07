"""Tests for the deterministic NMD-0003 tier-1 anchor capsule helper."""

from __future__ import annotations

from pathlib import Path

from scripts.package_nmd0003_tier1_anchor_capsule import (
    DEFAULT_ARCHIVE_NAME,
    FREEZE_COMMIT,
    build_capsule,
)


ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_CAPSULE_BYTES = 127_617
PUBLISHED_CAPSULE_SHA256 = (
    "82e3a872ad5e3fb1cd7841d29ed53ef3223945a73ba64e71866f0de209804272"
)


def test_build_capsule_reads_freeze_commit_for_published_bytes(tmp_path: Path) -> None:
    manifest = build_capsule(ROOT, tmp_path)

    assert manifest["freeze_commit"] == FREEZE_COMMIT
    assert manifest["source_ref"] == FREEZE_COMMIT
    assert manifest["archive"]["filename"] == DEFAULT_ARCHIVE_NAME
    assert manifest["archive"]["bytes"] == PUBLISHED_CAPSULE_BYTES
    assert manifest["archive"]["sha256"] == PUBLISHED_CAPSULE_SHA256
    assert len(manifest["files"]) == 5
    assert Path(manifest["archive"]["path"]).is_file()
