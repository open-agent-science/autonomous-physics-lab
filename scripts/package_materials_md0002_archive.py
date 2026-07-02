#!/usr/bin/env python3
"""Build the deterministic local MD-0002 archive package.

This helper verifies the TASK-0900 allowlist, writes a deterministic ZIP archive
to an explicit local output directory, and records an archive manifest beside it.
It does not create release tags, upload externally, mint or decline a DOI, or
modify MD-0002 rows, holdout membership, source snapshots, or RESULT-0021.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any
import zipfile


DATASET_ID = "MD-0002-materials-project-stable-ternary-oxides"
DATASET_VERSION = "0.1.0"
DEFAULT_ARCHIVE_NAME = "MD-0002-materials-project-stable-ternary-oxides-v0.1.0.zip"
DEFAULT_MANIFEST_NAME = "MD-0002-materials-project-stable-ternary-oxides-v0.1.0.manifest.json"
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
        "data/materials/md-0002-materials-project-stable-ternary-oxides.yaml",
        515_699,
        "516ed06f005157da93fb30490fea2d7a5026146129a4b56ed4c6d4159d81b1d1",
    ),
    PackageFile(
        2,
        "data/materials/md0002_holdout_manifest.yaml",
        7_627,
        "c98c6e699d5fd0146f3456c4726bf71adbd5aeea2cff6aada9190671095e5451",
    ),
    PackageFile(
        3,
        "data/materials/materials_md0002_snapshot_manifest.yaml",
        5_392,
        "a5644ad51128cf94097ffd1f4673346bdf003a7cc6cbbaeea9a2a3d645f9a691",
    ),
    PackageFile(
        4,
        "data/materials/snapshots/materials_project_md0002_2026.04.13.json",
        249_272,
        "5bfb3e7f86c0afcdfa7e7898a47e05e063226758eeabeae0c95c246660349567",
    ),
    PackageFile(
        5,
        "data/materials/README.md",
        4_256,
        "343880f2cc2971af79758b44dc27c352cee808f7b2d40d8dc48701787db55fe2",
    ),
    PackageFile(
        6,
        "data/materials/schema.md",
        5_366,
        "75031c10aaeece15e1eba569478dbd16c2ccc2b3d17d5cd597fcbea6f715b6ed",
    ),
    PackageFile(
        7,
        "data/materials/fixtures/md0002_schema_fixture.yaml",
        3_678,
        "a02d19553888ecd65d5e89de295b052580733b4d6830ed930185b305716b50f8",
    ),
    PackageFile(
        8,
        "data/DATA_LICENSES.yaml",
        17_713,
        "75bbd5230d83c037bb64b39e2b4b35c154c56551bc9b99d48747c81a36da813f",
    ),
    PackageFile(
        9,
        "results/EXP-0014/RUN-0001/report.md",
        603,
        "accf7f33e77a8bf1003e1e086e0b54291b3371aba8e625f8b81de8d220ec5e81",
    ),
    PackageFile(
        10,
        "results/EXP-0014/RUN-0001/result.yaml",
        7_573,
        "9765a4d07792dbcca02267fd59170c6a51ab028a9fdfd499ce721eb1689c1bf2",
    ),
    PackageFile(
        11,
        "docs/reviews/materials-md0002-release-metadata-closeout.md",
        3_553,
        "c02b2676f729771487a97152cbc7fe8f714e769114aebe88b863a14d472e1b1f",
    ),
    PackageFile(
        12,
        "docs/reviews/materials-md0002-external-release-decision-packet.md",
        9_758,
        "02207f3d956170f6021a145a5c68f2fd093d04e3838ff835ea4ce0f463d1c967",
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
    seen_paths: set[str] = set()
    seen_orders: set[int] = set()
    verified: list[dict[str, Any]] = []
    for entry in entries:
        if entry.order in seen_orders:
            raise ValueError(f"Duplicate package order: {entry.order}")
        if entry.path in seen_paths:
            raise ValueError(f"Duplicate package path: {entry.path}")
        seen_orders.add(entry.order)
        seen_paths.add(entry.path)

        path = _repo_relative_path(repo_root, entry.path)
        if not path.is_file():
            raise FileNotFoundError(f"Package file missing: {entry.path}")
        actual_size = path.stat().st_size
        actual_sha = sha256_file(path)
        if actual_size != entry.bytes or actual_sha != entry.sha256:
            raise ValueError(
                "Package file hash/size mismatch for "
                f"{entry.path}: bytes={actual_size}, sha256={actual_sha}"
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


def build_archive(
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
            "Refusing to write package output inside the repository. "
            "Use an external output directory such as C:/tmp/... or pass "
            "--allow-repo-output for disposable local testing."
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
        "task_id": "TASK-0908",
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
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
            "md0002_rows_changed": False,
            "holdout_membership_changed": False,
            "result_0021_changed": False,
            "no_claim_boundary_preserved": True,
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--archive-name", default=DEFAULT_ARCHIVE_NAME)
    parser.add_argument("--manifest-name", default=DEFAULT_MANIFEST_NAME)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--allow-repo-output", action="store_true")
    args = parser.parse_args()

    manifest = build_archive(
        args.repo_root,
        args.output_dir,
        archive_name=args.archive_name,
        manifest_name=args.manifest_name,
        force=args.force,
        allow_repo_output=args.allow_repo_output,
    )
    print(
        json.dumps(
            {
                "archive_filename": manifest["archive"]["filename"],
                "archive_bytes": manifest["archive"]["bytes"],
                "archive_sha256": manifest["archive"]["sha256"],
                "file_count": len(manifest["files"]),
                "manifest_path": str(Path(args.output_dir).resolve() / args.manifest_name),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())