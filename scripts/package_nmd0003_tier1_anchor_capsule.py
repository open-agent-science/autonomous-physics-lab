#!/usr/bin/env python3
"""Build the deterministic NMD-0003 tier-1 freeze anchor capsule (TASK-0945).

This helper verifies the pinned anchor allowlist (the four tier-1 point-only
PRED entries plus the freeze review note), writes a deterministic ZIP capsule
to an explicit local output directory, and records a capsule manifest beside
it. It does not create tags, upload externally, mint a DOI, or modify any
PRED, registry, RESULT, or CLAIM artifact.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any
import zipfile


CAPSULE_ID = "NMD-0003-tier1-point-only-freeze-anchor"
CAPSULE_VERSION = "1.0.0"
FREEZE_COMMIT = "f1eba9a2"
DEFAULT_ARCHIVE_NAME = "nmd0003-tier1-anchor-v1.0.0.zip"
DEFAULT_MANIFEST_NAME = "nmd0003-tier1-anchor-v1.0.0.manifest.json"
FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


@dataclass(frozen=True)
class PackageFile:
    order: int
    path: str
    bytes: int
    sha256: str


PACKAGE_FILES = (
    PackageFile(
        1,
        "prediction_registry/nuclear_masses/PRED-0069.yaml",
        26_856,
        "1f25c093d18fe7076ae4ac8fb49266b0a93089b37379743ce7497658e6d585d9",
    ),
    PackageFile(
        2,
        "prediction_registry/nuclear_masses/PRED-0070.yaml",
        27_076,
        "04a9072f5f6836d63c623271b9addd1a25ee94b94574e4a378973ff77cc50de1",
    ),
    PackageFile(
        3,
        "prediction_registry/nuclear_masses/PRED-0071.yaml",
        27_467,
        "a8e685f5c863797ea93e8564dac314ca368b8961d3a15f378ff5451931065eca",
    ),
    PackageFile(
        4,
        "prediction_registry/nuclear_masses/PRED-0072.yaml",
        26_450,
        "9aa16f6b676b093138471f5f8755d5e90ee385208624e39eb32e64924a17322c",
    ),
    PackageFile(
        5,
        "docs/reviews/nmd0003-tier1-point-only-frontier-freeze.md",
        18_862,
        "360ac6dba379d96c07fea65b56f64e5d5911a4b1f0a0791f4cb0ac6ff04159c3",
    ),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_relative_path(repo_root: Path, relative_path: str) -> Path:
    normalized = relative_path.replace("\\", "/")
    if normalized.startswith("/") or ".." in Path(normalized).parts:
        raise ValueError(f"Package path is not repository-relative: {relative_path}")
    return repo_root / normalized


def verify_package_files(
    repo_root: Path, entries: tuple[PackageFile, ...] = PACKAGE_FILES
) -> list[dict[str, Any]]:
    verified: list[dict[str, Any]] = []
    for entry in entries:
        path = _repo_relative_path(repo_root, entry.path)
        if not path.is_file():
            raise FileNotFoundError(f"Package file missing: {entry.path}")
        actual_size = path.stat().st_size
        actual_sha = sha256_file(path)
        if actual_size != entry.bytes or actual_sha != entry.sha256:
            raise ValueError(
                "Package file hash/size mismatch for "
                f"{entry.path}: bytes={actual_size}, sha256={actual_sha}. "
                "The pins freeze the anchored state at commit "
                f"{FREEZE_COMMIT}; if the repo files moved on, rebuild is a "
                "new capsule version with refreshed pins, not a silent edit."
            )
        verified.append(
            {
                "order": entry.order,
                "path": entry.path,
                "bytes": actual_size,
                "sha256": actual_sha,
            }
        )
    return verified


def _zip_info(archive_path: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(archive_path, date_time=FIXED_ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o644 << 16
    return info


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def build_capsule(
    repo_root: Path,
    output_dir: Path,
    *,
    archive_name: str = DEFAULT_ARCHIVE_NAME,
    manifest_name: str = DEFAULT_MANIFEST_NAME,
    entries: tuple[PackageFile, ...] = PACKAGE_FILES,
    force: bool = False,
    allow_repo_output: bool = False,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    if _is_relative_to(output_dir, repo_root) and not allow_repo_output:
        raise ValueError(
            "Refusing to write capsule output inside the repository. "
            "Use an external output directory or pass --allow-repo-output "
            "for disposable local testing."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / archive_name
    manifest_path = output_dir / manifest_name
    if not force:
        for path in (archive_path, manifest_path):
            if path.exists():
                raise FileExistsError(f"Output already exists; pass --force to replace: {path}")

    verified_files = verify_package_files(repo_root, entries)
    with zipfile.ZipFile(archive_path, "w") as archive:
        for item in verified_files:
            source_path = _repo_relative_path(repo_root, str(item["path"]))
            archive.writestr(_zip_info(str(item["path"])), source_path.read_bytes())

    archive_size = archive_path.stat().st_size
    archive_sha = sha256_file(archive_path)
    manifest = {
        "schema_version": "1",
        "task_id": "TASK-0945",
        "capsule_id": CAPSULE_ID,
        "capsule_version": CAPSULE_VERSION,
        "freeze_commit": FREEZE_COMMIT,
        "archive": {
            "filename": archive_name,
            "path": str(archive_path),
            "bytes": archive_size,
            "sha256": archive_sha,
            "committed_to_repository": False,
            "compression": "zip_stored",
            "fixed_zip_timestamp": "1980-01-01T00:00:00",
        },
        "files": verified_files,
        "policy": {
            "release_tag_created": False,
            "external_upload_attempted": False,
            "doi_minted_or_declined": False,
            "pred_payloads_changed": False,
            "registry_entries_changed": False,
            "no_claim_boundary_preserved": True,
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--allow-repo-output", action="store_true")
    args = parser.parse_args()
    manifest = build_capsule(
        Path(args.repo_root),
        Path(args.output_dir),
        force=args.force,
        allow_repo_output=args.allow_repo_output,
    )
    print(json.dumps(manifest["archive"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
