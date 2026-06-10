"""Portability coverage for Exoplanet source-acquisition checksums."""

from __future__ import annotations

from pathlib import Path

import pytest

from physics_lab.checksums import (
    sha256_bytes,
    sha256_file,
    sha256_lf_canonical_file,
    sha256_lf_canonical_text,
)


ROOT = Path(__file__).resolve().parents[1]
QUERY_PATH = ROOT / "data" / "exoplanets" / "snapshot_plans" / "pscomppars_query.adql"
MANIFEST_PATH = ROOT / "data" / "exoplanets" / "second_snapshot_manifest.yaml"
SNAPSHOT_PATH = ROOT / "data" / "exoplanets" / "exo-0002-pscomppars-snapshot.yaml"
EXPECTED_QUERY_SHA256 = "28b8baf9f14e4ba544658fccbad5ef1271a21f91228afe8afff4db968512acf8"


def test_lf_canonical_text_matches_windows_and_unix_line_endings() -> None:
    unix_text = "SELECT *\nFROM ps\nWHERE default_flag = 1\n"
    windows_text = "SELECT *\r\nFROM ps\r\nWHERE default_flag = 1\r\n"

    assert sha256_lf_canonical_text(unix_text) == sha256_lf_canonical_text(windows_text)


def test_raw_byte_checksum_differs_when_crlf_is_present(tmp_path: Path) -> None:
    path = tmp_path / "sample.adql"
    path.write_text("line one\r\nline two\r\n", encoding="utf-8")

    assert sha256_file(path) != sha256_lf_canonical_file(path)


def test_committed_exoplanet_text_artifacts_use_lf_canonical_checksums() -> None:
    assert sha256_lf_canonical_file(QUERY_PATH) == EXPECTED_QUERY_SHA256
    assert sha256_lf_canonical_file(MANIFEST_PATH)
    assert sha256_lf_canonical_file(SNAPSHOT_PATH)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        ("a\n", "87428fc522803d31065e7bce3cf03fe475096631e5e07bbd7a0fde60c4cf25c7"),
    ],
)
def test_sha256_bytes_matches_hashlib_reference(text: str, expected: str) -> None:
    assert sha256_bytes(text.encode("utf-8")) == expected
