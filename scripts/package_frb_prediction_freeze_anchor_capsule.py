#!/usr/bin/env python3
"""Build the deterministic FRB prediction-freeze anchor capsule (TASK-1020).

This helper verifies the approved nine-path capsule manifest for the registered
FRB pre-T repeater-propensity prediction, writes a deterministic ZIP capsule to
an explicit local output directory, and records a JSON manifest beside it. It
does not create tags, GitHub Releases, external uploads, DOIs, results, claims,
knowledge artifacts, reveal scores, or prediction-payload edits.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any
import zipfile

import yaml


TASK_ID = "TASK-1020"
CAPSULE_ID = "FRB-PRET-repeater-propensity-freeze-anchor"
CAPSULE_VERSION = "1.0.0"
SOURCE_FREEZE_COMMIT = "83eca7501aea3e4f9869324b5ec2cd722fd7e676"
REGISTRATION_MERGE_COMMIT = "059227ba0fcb6c0601bd4c70cf312c6f094aee48"
BOARD_SYNC_MAIN_COMMIT = "b82f80f382f3b97e2229df0b2885a6faae9d1b4e"
SUGGESTED_TAG = "pred-frb-pret-repeater-propensity-20260710"
DEFAULT_ARCHIVE_NAME = "frb-pret-repeater-propensity-freeze-anchor-v1.0.0.zip"
DEFAULT_MANIFEST_NAME = "frb-pret-repeater-propensity-freeze-anchor-v1.0.0.manifest.json"
FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


@dataclass(frozen=True)
class PackageFile:
    order: int
    path: str
    bytes: int
    sha256: str
    role: str


PACKAGE_FILES = (
    PackageFile(
        1,
        "data/radio_transients/frb_sealed_prediction_registration_pack.yaml",
        190_860,
        "0b64202b9bf8ccd37bf23bd4304e374bc10baf17f09498ad5635725eccca75e5",
        "task_0965_registration_pack",
    ),
    PackageFile(
        2,
        "decisions/DEC-20260709-frb-prediction-freeze-stub.yaml",
        3_243,
        "ff99cd7055796a811711d1887a25a1d6fa3d1493c335a337151834221aec8a28",
        "approved_class_2_prediction_freeze_decision",
    ),
    PackageFile(
        3,
        "prediction_registry/radio_transients/PRED-0001.yaml",
        172_220,
        "442323fe63c1170fecae042e3f5612c1177069e74a39632e92c37fa04f7f3c80",
        "registered_radio_transients_pred_entry",
    ),
    PackageFile(
        4,
        "data/radio_transients/frb_pre_t_repeater_propensity_model_surface.yaml",
        46_200,
        "978049b9c7360091f812ee451dae36a5ca81ccea403725a61b36c01a42f562ab",
        "task_0964_frozen_model_surface",
    ),
    PackageFile(
        5,
        "data/radio_transients/frb_pre_t_model_selection_contract.yaml",
        4_253,
        "5d3db1fceaafa88a0fd7c68b2c6987e96fa6cf0cd82a3a156cd5be35275ca7df",
        "task_0964_model_selection_contract",
    ),
    PackageFile(
        6,
        "data/radio_transients/frb_catalog1_pre_t_exposure_feature_surface.yaml",
        177_389,
        "8fc57714013a62b51710d48402e23b76eb8f7fa79c17b4e6b0875f06d3374b26",
        "task_0963_pre_t_input_surface",
    ),
    PackageFile(
        7,
        "docs/reviews/frb-sealed-prediction-registration-pack.md",
        3_876,
        "9f38ae2aa7b5de6950af367b02de188fc7850a7b7fa942624c9c4c4716f9ad63",
        "task_0965_pack_note",
    ),
    PackageFile(
        8,
        "docs/reviews/frb-campaign-activation-20260708.md",
        2_045,
        "c4deb4e4182fefa218ec7e101c8ed8006bc806f5480ce5b55d71e0013d72a5b7",
        "campaign_activation_note",
    ),
    PackageFile(
        9,
        "docs/reviews/frb-catalog1-interval-exposure-pair-checksum-schema-gate.md",
        6_181,
        "81cd0fbc983c6160a52ff80fd85985a06dd395bdc5f5c8d831839b9db4dda4f2",
        "catalog1_pair_gate_note",
    ),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def md5_file(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected YAML mapping")
    return payload


def _repo_relative_path(repo_root: Path, relative_path: str) -> Path:
    normalized = relative_path.replace("\\", "/")
    if normalized.startswith("/") or ".." in Path(normalized).parts:
        raise ValueError(f"Package path is not repository-relative: {relative_path}")
    return repo_root / normalized


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def verify_pack_manifest_matches_allowlist(repo_root: Path) -> None:
    pack = load_yaml(repo_root / "data/radio_transients/frb_sealed_prediction_registration_pack.yaml")
    manifest = ((pack.get("external_anchor_plan") or {}).get("capsule_manifest")) or []
    if manifest != [entry.path for entry in PACKAGE_FILES]:
        raise ValueError("FRB approved pack capsule_manifest no longer matches TASK-1020 allowlist")


def verify_package_files(
    repo_root: Path, entries: tuple[PackageFile, ...] = PACKAGE_FILES
) -> list[dict[str, Any]]:
    verify_pack_manifest_matches_allowlist(repo_root)
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
                "The pins freeze the registered FRB prediction anchor package; "
                "refreshing them is a new capsule version, not a silent edit."
            )
        verified.append(
            {
                "order": entry.order,
                "path": entry.path,
                "role": entry.role,
                "bytes": actual_size,
                "sha256": actual_sha,
            }
        )
    return verified


def _zip_info(path: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(path, date_time=FIXED_ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o644 << 16
    return info


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
            "Use an external output directory or pass --allow-repo-output for disposable local testing."
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
    archive_md5 = md5_file(archive_path)
    manifest = {
        "schema_version": "1",
        "task_id": TASK_ID,
        "capsule_id": CAPSULE_ID,
        "capsule_version": CAPSULE_VERSION,
        "source_freeze_commit": SOURCE_FREEZE_COMMIT,
        "registration_merge_commit": REGISTRATION_MERGE_COMMIT,
        "board_sync_main_commit": BOARD_SYNC_MAIN_COMMIT,
        "suggested_tag": SUGGESTED_TAG,
        "archive": {
            "filename": archive_name,
            "path": str(archive_path),
            "bytes": archive_size,
            "sha256": archive_sha,
            "md5": archive_md5,
            "committed_to_repository": False,
            "compression": "zip_stored",
            "fixed_zip_timestamp": "1980-01-01T00:00:00",
        },
        "files": verified_files,
        "policy": {
            "release_tag_created_by_agent": False,
            "github_release_created_by_agent": False,
            "external_upload_attempted_by_agent": False,
            "doi_minted_or_declined_by_agent": False,
            "prediction_payload_changed": False,
            "result_claim_knowledge_changed": False,
            "reveal_labels_inspected": False,
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
