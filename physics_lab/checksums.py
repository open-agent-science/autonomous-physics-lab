"""Portable checksum helpers for source-acquisition artifacts."""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    """Return the SHA-256 hex digest of raw bytes."""

    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file's raw on-disk bytes.

    Use this for binary or value-bearing source artifacts such as CSV snapshots.
    """

    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_lf_canonical_text(text: str) -> str:
    """Return the SHA-256 hex digest of UTF-8 text normalized to LF line endings."""

    normalized = text.replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def sha256_lf_canonical_file(path: Path) -> str:
    """Return the LF-canonical SHA-256 digest for a committed text artifact."""

    return sha256_lf_canonical_text(path.read_text(encoding="utf-8"))
