#!/usr/bin/env python3
"""Build the deterministic FRB prediction-freeze anchor dry-run capsule.

This TASK-0994 helper prepares the local archive shape that a maintainer could
reuse after a Class 2 FRB prediction-freeze approval. It writes only to an
explicit output directory, verifies committed allowlist pins, generates a staged
draft PRED payload from the TASK-0965 pack, and does not create tags, releases,
DOIs, registry entries, results, claims, or knowledge artifacts.
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


TASK_ID = "TASK-0994"
CAPSULE_ID = "FRB-PRET-repeater-propensity-freeze-anchor-dry-run"
CAPSULE_VERSION = "0.1.0-dry-run"
SOURCE_PACK_ID = "FRB-PRET-PRED-REGPACK-0001"
DEFAULT_ARCHIVE_NAME = "frb-pret-prediction-freeze-anchor-dry-run-v0.1.0.zip"
DEFAULT_MANIFEST_NAME = "frb-pret-prediction-freeze-anchor-dry-run-v0.1.0.manifest.json"
FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
STAGED_PRED_MEMBER_PATH = "staged_payloads/prediction_registry/radio_transients/PRED-0001.draft.yaml"


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
        "decisions/DEC-20260709-frb-prediction-freeze-stub.yaml",
        2_181,
        "2554cc15eda2e12ec08dcc5ba44e240d135fd915c8f8ebbdb67c7c2c6ea725b5",
        "class_2_prediction_freeze_decision_stub",
    ),
    PackageFile(
        3,
        "data/radio_transients/frb_sealed_prediction_registration_pack.yaml",
        190_860,
        "0b64202b9bf8ccd37bf23bd4304e374bc10baf17f09498ad5635725eccca75e5",
        "task_0965_registration_pack",
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
        "task_0965_pack_review_note",
    ),
    PackageFile(
        8,
        "docs/reviews/frb-pre-t-model-selection-freeze.md",
        2_007,
        "7e789554c6c3156e8a73ddd3d8527b7ea16f1eafbfd60248590663e2b691ad3e",
        "task_0964_model_freeze_review_note",
    ),
    PackageFile(
        9,
        "docs/reviews/frb-catalog1-pre-t-exposure-feature-surface.md",
        4_242,
        "477fdad7b5ba46c67003f6e4c1d61ec477e013d7f8c0205d7cde3a9cbd4921bf",
        "task_0963_feature_surface_review_note",
    ),
    PackageFile(
        10,
        "docs/reviews/frb-campaign-activation-20260708.md",
        2_045,
        "c4deb4e4182fefa218ec7e101c8ed8006bc806f5480ce5b55d71e0013d72a5b7",
        "campaign_activation_review_note",
    ),
    PackageFile(
        11,
        "docs/reviews/frb-catalog1-interval-exposure-pair-checksum-schema-gate.md",
        6_181,
        "81cd0fbc983c6160a52ff80fd85985a06dd395bdc5f5c8d831839b9db4dda4f2",
        "catalog1_pair_gate_review_note",
    ),
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
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
                "Refresh this dry-run capsule only through a reviewed TASK-0994 "
                "successor, not by silently shadowing the pins."
            )
        verified.append(
            {
                "order": entry.order,
                "kind": "committed_file",
                "role": entry.role,
                "path": entry.path,
                "bytes": actual_size,
                "sha256": actual_sha,
            }
        )
    return verified


def staged_pred_payload_bytes(repo_root: Path) -> tuple[bytes, dict[str, Any]]:
    pack_path = repo_root / "data/radio_transients/frb_sealed_prediction_registration_pack.yaml"
    pack = load_yaml(pack_path)
    if pack.get("pack_id") != SOURCE_PACK_ID:
        raise ValueError(f"Unexpected FRB pack id: {pack.get('pack_id')}")
    boundary = pack.get("registration_boundary") or {}
    if boundary.get("registration_executed") is not False:
        raise ValueError("FRB pack no longer records registration_executed=false")
    if boundary.get("prediction_registry_written") is not False:
        raise ValueError("FRB pack no longer records prediction_registry_written=false")

    entries = pack.get("sealed_registry_entries")
    if not isinstance(entries, list) or len(entries) != 1:
        raise ValueError("Expected exactly one staged FRB sealed registry entry")
    entry = entries[0]
    if entry.get("registration_status") != "staged_not_registered":
        raise ValueError("Staged FRB entry no longer has registration_status=staged_not_registered")
    payload = entry.get("would_register_on_maintainer_approval")
    if not isinstance(payload, dict):
        raise ValueError("Staged FRB entry is missing the future PRED payload")
    targets = ((payload.get("target_set") or {}).get("targets")) or []
    if len(targets) != 479:
        raise ValueError(f"Expected 479 staged FRB targets, found {len(targets)}")
    if payload.get("registered_at_utc") != "SET_BY_MAINTAINER_PREDICTION_FREEZE_DECISION":
        raise ValueError("Staged payload no longer carries maintainer-decision timestamp placeholder")
    if (payload.get("source_state") or {}).get("git_commit") != "SET_TO_APPROVED_FREEZE_COMMIT":
        raise ValueError("Staged payload no longer carries approved-freeze commit placeholder")

    rendered = yaml.safe_dump(payload, sort_keys=False, allow_unicode=False, width=100).encode("utf-8")
    metadata = {
        "order": 2,
        "kind": "generated_staged_payload",
        "role": "staged_pred_payload_from_task_0965_pack",
        "path": STAGED_PRED_MEMBER_PATH,
        "bytes": len(rendered),
        "sha256": sha256_bytes(rendered),
        "source_pack_path": "data/radio_transients/frb_sealed_prediction_registration_pack.yaml",
        "source_pack_id": SOURCE_PACK_ID,
        "source_draft_entry_id": entry.get("draft_entry_id"),
        "registration_status": entry.get("registration_status"),
        "target_count": len(targets),
        "draft_entry_targets_sha256": (entry.get("payload_checksums") or {}).get(
            "draft_entry_targets_sha256"
        ),
        "draft_entry_sha256": (entry.get("payload_checksums") or {}).get("draft_entry_sha256"),
    }
    return rendered, metadata


def _zip_info(archive_path: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(archive_path, date_time=FIXED_ZIP_TIMESTAMP)
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
    force: bool = False,
    allow_repo_output: bool = False,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    if _is_relative_to(output_dir, repo_root) and not allow_repo_output:
        raise ValueError(
            "Refusing to write dry-run capsule output inside the repository. "
            "Use an external output directory or pass --allow-repo-output for disposable local testing."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / archive_name
    manifest_path = output_dir / manifest_name
    if not force:
        for path in (archive_path, manifest_path):
            if path.exists():
                raise FileExistsError(f"Output already exists; pass --force to replace: {path}")

    verified_files = verify_package_files(repo_root)
    staged_payload, staged_metadata = staged_pred_payload_bytes(repo_root)
    all_files = sorted([*verified_files, staged_metadata], key=lambda item: int(item["order"]))

    with zipfile.ZipFile(archive_path, "w") as archive:
        for item in all_files:
            archive_path_name = str(item["path"])
            if item["kind"] == "generated_staged_payload":
                archive.writestr(_zip_info(archive_path_name), staged_payload)
            else:
                source_path = _repo_relative_path(repo_root, archive_path_name)
                archive.writestr(_zip_info(archive_path_name), source_path.read_bytes())

    archive_size = archive_path.stat().st_size
    archive_sha = sha256_file(archive_path)
    manifest = {
        "schema_version": "1",
        "task_id": TASK_ID,
        "capsule_id": CAPSULE_ID,
        "capsule_version": CAPSULE_VERSION,
        "dry_run": True,
        "archive": {
            "filename": archive_name,
            "path": str(archive_path),
            "bytes": archive_size,
            "sha256": archive_sha,
            "committed_to_repository": False,
            "compression": "zip_stored",
            "fixed_zip_timestamp": "1980-01-01T00:00:00",
        },
        "files": all_files,
        "policy": {
            "release_tag_created": False,
            "github_release_created": False,
            "external_upload_attempted": False,
            "doi_minted_or_declined": False,
            "prediction_registry_written": False,
            "registered_pred_payload_changed": False,
            "result_claim_knowledge_changed": False,
            "no_claim_boundary_preserved": True,
        },
        "post_approval_notes": [
            "Replace the decision stub with the maintainer-approved Class 2 prediction_freeze decision.",
            "Replace the generated draft PRED member with the committed registered PRED entry.",
            "Set the tag target to the approved freeze commit and rebuild a non-dry-run capsule.",
            "Record release asset checksum and optional DOI only after the maintainer executes publication.",
        ],
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
