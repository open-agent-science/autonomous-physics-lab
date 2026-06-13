"""Fetch a source artifact and verify its expected SHA-256 checksum.

This helper is intentionally small and generic. It is for maintainer-approved
source acquisition or local re-checks, not for live fetching inside benchmark
runners.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import urllib.request


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_sidecar_checksum(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Checksum sidecar is empty: {path}")
    checksum = text.split()[0]
    if len(checksum) != 64 or any(
        char not in "0123456789abcdefABCDEF" for char in checksum
    ):
        raise ValueError(
            f"Checksum sidecar does not start with a SHA-256 hex digest: {path}"
        )
    return checksum.lower()


def fetch_and_verify(
    *,
    url: str,
    output_path: Path,
    expected_sha256: str,
    timeout_seconds: float,
    overwrite: bool,
) -> str:
    expected = expected_sha256.lower()
    if len(expected) != 64 or any(char not in "0123456789abcdef" for char in expected):
        raise ValueError("expected_sha256 must be a 64-character lowercase hex digest")
    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"Refusing to overwrite existing file without --force: {output_path}"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_name(f".{output_path.name}.tmp")
    try:
        with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
            with tmp_path.open("wb") as fh:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    fh.write(chunk)

        actual = sha256_file(tmp_path)
        if actual != expected:
            raise ValueError(
                f"Checksum mismatch for {url}: expected {expected}, got {actual}"
            )
        os.replace(tmp_path, output_path)
        return actual
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch one source artifact and verify a pinned SHA-256 checksum."
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Artifact URL or file:// locator.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Path to write after checksum verification.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sha256", help="Expected SHA-256 hex digest.")
    group.add_argument(
        "--sha256-file",
        type=Path,
        help="Sidecar file whose first token is the expected SHA-256.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Network timeout in seconds.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the output path if it already exists.",
    )
    args = parser.parse_args(argv)

    expected_sha256 = args.sha256 or read_sidecar_checksum(args.sha256_file)
    actual = fetch_and_verify(
        url=args.url,
        output_path=args.output,
        expected_sha256=expected_sha256,
        timeout_seconds=args.timeout,
        overwrite=args.force,
    )
    print("status=OK")
    print(f"output={args.output}")
    print(f"sha256={actual}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
