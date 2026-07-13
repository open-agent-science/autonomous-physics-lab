#!/usr/bin/env python3
"""Build the deterministic reduced FRB pre-registration anchor capsule.

The reduced capsule contains only APL-authored decision and review metadata.
Source-derived prediction, feature, model, and score/rank surfaces remain
excluded and are represented by their frozen path, size, checksum, commit, and
tag identity. The helper writes local archive bytes only; it never uploads,
mints a DOI, reads reveal labels, scores a reveal, or mutates PRED-0001.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
from typing import Any
import zipfile

REPO_ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
if str(REPO_ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT_FOR_IMPORTS))

from scripts.package_frb_prediction_freeze_anchor_capsule import (  # noqa: E402
    DEFAULT_ARCHIVE_NAME as FULL_ARCHIVE_NAME,
    REGISTRATION_MERGE_COMMIT,
    SOURCE_FREEZE_COMMIT,
    SUGGESTED_TAG,
    load_yaml,
    sha256_file,
    verify_package_files as verify_full_package_files,
)


TASK_ID = "TASK-1024"
CAPSULE_ID = "FRB-PRET-reduced-pre-registration-checksum-anchor"
CAPSULE_VERSION = "1.0.0"
DECISION_PATH = "decisions/DEC-20260712-frb-reduced-anchor-publication.yaml"
DECISION_MERGE_COMMIT = "c4fafb79cf1acc0554f063d985457394349a1270"
CONTENT_BASIS_COMMIT = "329b79db51da946bd6df2aaa9ec85ae54a18e734"
FULL_ARCHIVE_BYTES = 608_067
FULL_ARCHIVE_SHA256 = "7f7f44e83dca50b84ba5f2ce310b305172140c04fcf7ae9484fbab0dfa8e1039"
FULL_RELEASE_URL = (
    "https://github.com/open-agent-science/autonomous-physics-lab/releases/tag/"
    "pred-frb-pret-repeater-propensity-20260710"
)
DEFAULT_ARCHIVE_NAME = "frb-pret-reduced-pre-registration-anchor-v1.0.0.zip"
DEFAULT_MANIFEST_NAME = "frb-pret-reduced-pre-registration-anchor-v1.0.0.manifest.json"
README_MEMBER_PATH = "README.md"
MANIFEST_MEMBER_PATH = "FRB_REDUCED_ANCHOR_MANIFEST.json"
FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
PRED_PATH = "prediction_registry/radio_transients/PRED-0001.yaml"


@dataclass(frozen=True)
class IncludedFile:
    order: int
    path: str
    bytes: int
    sha256: str
    role: str


INCLUDED_FILES = (
    IncludedFile(
        1,
        "decisions/DEC-20260709-frb-prediction-freeze-stub.yaml",
        3_243,
        "ff99cd7055796a811711d1887a25a1d6fa3d1493c335a337151834221aec8a28",
        "approved_prediction_freeze_decision",
    ),
    IncludedFile(
        2,
        DECISION_PATH,
        4_200,
        "46f7ca507303f7547f8b760415f1dd53dc1f3b859a76642771b1efe34355c022",
        "approved_reduced_capsule_rights_decision",
    ),
    IncludedFile(
        3,
        "docs/reviews/frb/frb-prediction-freeze-registration.md",
        6_355,
        "84a383789395932b2b1833ddfbc7c1402f9d18d6577a213490647e527a72214e",
        "prediction_registration_record",
    ),
    IncludedFile(
        4,
        "docs/reviews/frb/frb-prediction-freeze-anchor-upload-pack.md",
        6_215,
        "bacbdda03a53d19cc313ae797305e1676069d71e3fa33638ca62cb8334b499ca",
        "full_anchor_upload_pack_record",
    ),
    IncludedFile(
        5,
        "docs/reviews/frb/frb-prediction-freeze-external-anchor-record-back.md",
        3_325,
        "04e4e2288e72ccc54f8bf6160becbe48f08bb287bef2afb9367f53f18d0f4cb0",
        "github_release_anchor_record",
    ),
    IncludedFile(
        6,
        "docs/reviews/frb/frb-anchor-zenodo-rights-publication-review.md",
        11_128,
        "936914e39bc8247accdf7df90acfb71328dd0ad1caf145bdcdd69ed271ae196b",
        "reduced_capsule_rights_review",
    ),
    IncludedFile(
        7,
        "LICENSE",
        1_092,
        "2cf9341bcca6f0eebd532362132d41b2abc8250b6af5cf0e2035e4aabc67f61d",
        "repository_mit_license_notice",
    ),
)


EXCLUSION_POLICY = {
    "data/radio_transients/frb_sealed_prediction_registration_pack.yaml": (
        "rights_blocked_value_bearing",
        "Mixed registration pack with source-level scores, ranks, and target digest; "
        "represented by checksum only.",
    ),
    PRED_PATH: (
        "rights_blocked_value_bearing",
        "Registered source-level point scores and ranks; represented by checksum and "
        "public repository pointer only.",
    ),
    "data/radio_transients/frb_pre_t_repeater_propensity_model_surface.yaml": (
        "rights_blocked_value_bearing",
        "Source-derived model and score surface; represented by checksum only.",
    ),
    "data/radio_transients/frb_pre_t_model_selection_contract.yaml": (
        "minimality_context_omitted",
        "Method contract is coupled to source-surface hashes and is unnecessary for "
        "the minimal metadata anchor.",
    ),
    "data/radio_transients/frb_catalog1_pre_t_exposure_feature_surface.yaml": (
        "rights_blocked_value_bearing",
        "Source-derived per-source exposure features have no recorded bulk "
        "redistribution license.",
    ),
    "docs/reviews/frb-sealed-prediction-registration-pack.md": (
        "rights_blocked_value_bearing_narrative",
        "Narrative includes top-score examples; replaced by the reduced README.",
    ),
    "docs/reviews/frb-campaign-activation-20260708.md": (
        "minimality_context_omitted",
        "Optional campaign context is not required for the minimal checksum anchor.",
    ),
    "docs/reviews/frb-catalog1-interval-exposure-pair-checksum-schema-gate.md": (
        "minimality_context_omitted",
        "Optional source-gate context remains available in the public repository.",
    ),
}


ZENODO_DESCRIPTION = (
    "This is a reduced checksum anchor for a sealed prospective Autonomous Physics "
    "Lab prediction registration. It is not an open reusable FRB dataset, not a "
    "reveal result, not a success verdict, not a calibrated repeater probability, "
    "and not an FRB population, morphology, or discovery claim. Source-derived "
    "sealed prediction, feature, model, score, and rank surfaces are represented "
    "by checksum and public repository pointers only; they are not redistributed "
    "or licensed by this record."
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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


def _zip_info(path: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(path, date_time=FIXED_ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o644 << 16
    return info


def verify_go_reduced_capsule_decision(repo_root: Path) -> dict[str, Any]:
    decision = load_yaml(repo_root / DECISION_PATH)
    approved = decision.get("approved_scope") or {}
    record = decision.get("decision_record") or {}
    veto = decision.get("veto") or {}
    required = {
        "selected_option": "GO_REDUCED_CAPSULE",
        "publication_route": "reduced_metadata_checksum_capsule",
        "excluded_members_represented_by_checksum_only": True,
        "reduced_capsule_builder_allowed": True,
        "deterministic_local_archive_build_allowed": True,
        "automatic_external_upload_allowed": False,
        "doi_minting_by_implementation_task_allowed": False,
        "required_doi_readiness_verdict": "REDUCED_CAPSULE_REQUIRED",
        "required_implementation_verdict": "REDUCED_CAPSULE_READY_FOR_MAINTAINER_UPLOAD",
    }
    mismatches = {
        key: {"expected": expected, "actual": approved.get(key)}
        for key, expected in required.items()
        if approved.get(key) != expected
    }
    if mismatches:
        raise ValueError(f"GO_REDUCED_CAPSULE approved scope mismatch: {mismatches}")
    if veto.get("maintainer_vetoed") is not False:
        raise ValueError("GO_REDUCED_CAPSULE has been vetoed")
    if record.get("status") != "go_reduced_capsule_approved":
        raise ValueError("GO_REDUCED_CAPSULE decision is not approved")
    if record.get("revert_of") is not None:
        raise ValueError("GO_REDUCED_CAPSULE decision records a revert")
    return decision


def verify_included_files(repo_root: Path) -> list[dict[str, Any]]:
    verified: list[dict[str, Any]] = []
    for entry in INCLUDED_FILES:
        path = _repo_relative_path(repo_root, entry.path)
        if not path.is_file():
            raise FileNotFoundError(f"Reduced capsule file missing: {entry.path}")
        actual_size = path.stat().st_size
        actual_sha = sha256_file(path)
        if actual_size != entry.bytes or actual_sha != entry.sha256:
            raise ValueError(
                "Reduced capsule file hash/size mismatch for "
                f"{entry.path}: bytes={actual_size}, sha256={actual_sha}. "
                "Refresh through a reviewed capsule version, not a silent pin edit."
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


def build_excluded_member_manifest(repo_root: Path) -> list[dict[str, Any]]:
    full_files = verify_full_package_files(repo_root)
    included_original_paths = {INCLUDED_FILES[0].path}
    excluded: list[dict[str, Any]] = []
    for item in full_files:
        path = str(item["path"])
        if path in included_original_paths:
            continue
        if path not in EXCLUSION_POLICY:
            raise ValueError(f"Missing reduced-capsule exclusion policy for {path}")
        exclusion_class, reason = EXCLUSION_POLICY[path]
        source_commit = (
            REGISTRATION_MERGE_COMMIT if path == PRED_PATH else SOURCE_FREEZE_COMMIT
        )
        excluded.append(
            {
                "original_order": item["order"],
                "path": path,
                "role": item["role"],
                "bytes": item["bytes"],
                "sha256": item["sha256"],
                "source_commit": source_commit,
                "source_tag": SUGGESTED_TAG,
                "exclusion_class": exclusion_class,
                "exclusion_reason": reason,
                "redistributed_in_reduced_capsule": False,
            }
        )
    if len(excluded) != 8 or {item["path"] for item in excluded} != set(EXCLUSION_POLICY):
        raise ValueError("Reduced-capsule excluded-member manifest is incomplete")
    return excluded


def build_readme() -> bytes:
    text = f"""# FRB Reduced Pre-Registration Checksum Anchor

Capsule: `{CAPSULE_ID}` v{CAPSULE_VERSION}

{ZENODO_DESCRIPTION}

The included files are APL-authored decision and audit metadata. The manifest
records every omitted member of the original nine-file sealed capsule by path,
role, byte size, SHA-256, source commit, source tag, and exclusion reason. The
excluded bytes remain available through the public repository and existing
GitHub Release; this reduced archive does not redistribute or relicense them.

The archive is prepared for a maintainer-controlled external checksum anchor.
Building it does not upload externally, mint a DOI, inspect reveal labels,
score a reveal, change `PRED-0001`, or create a RESULT, CLAIM, or KNOW artifact.

License scope: the included APL-authored and generated metadata remain under the
repository MIT License, whose copyright and permission notice is included as
`LICENSE`. That license does not apply to checksum-referenced excluded
prediction, feature, model, score, rank, or source-derived surfaces.
"""
    return text.encode("utf-8")


def build_content_manifest(repo_root: Path) -> tuple[dict[str, Any], bytes, bytes]:
    verify_go_reduced_capsule_decision(repo_root)
    included = verify_included_files(repo_root)
    excluded = build_excluded_member_manifest(repo_root)
    readme = build_readme()
    member_allowlist = [
        README_MEMBER_PATH,
        MANIFEST_MEMBER_PATH,
        *[item["path"] for item in included],
    ]
    manifest = {
        "schema_version": "1",
        "task_id": TASK_ID,
        "capsule_id": CAPSULE_ID,
        "capsule_version": CAPSULE_VERSION,
        "implementation_verdict": "REDUCED_CAPSULE_READY_FOR_MAINTAINER_UPLOAD",
        "doi_readiness_verdict": "REDUCED_CAPSULE_REQUIRED",
        "decision": {
            "path": DECISION_PATH,
            "merge_commit": DECISION_MERGE_COMMIT,
            "selected_option": "GO_REDUCED_CAPSULE",
            "vetoed_or_reverted": False,
        },
        "content_basis_commit": CONTENT_BASIS_COMMIT,
        "original_full_anchor": {
            "archive_filename": FULL_ARCHIVE_NAME,
            "archive_bytes": FULL_ARCHIVE_BYTES,
            "archive_sha256": FULL_ARCHIVE_SHA256,
            "release_tag": SUGGESTED_TAG,
            "release_url": FULL_RELEASE_URL,
            "registration_merge_commit": REGISTRATION_MERGE_COMMIT,
            "source_freeze_commit": SOURCE_FREEZE_COMMIT,
        },
        "archive_member_allowlist": member_allowlist,
        "generated_members": [
            {
                "path": README_MEMBER_PATH,
                "role": "reduced_capsule_readme",
                "bytes": len(readme),
                "sha256": sha256_bytes(readme),
            },
            {
                "path": MANIFEST_MEMBER_PATH,
                "role": "reduced_capsule_manifest",
                "self_hash": "omitted_to_avoid_circular_manifest_hash",
            },
        ],
        "included_files": included,
        "excluded_sealed_members": excluded,
        "registered_prediction_identity": {
            "path": PRED_PATH,
            "target_count": 479,
            "target_payload_sha256": (
                "b4b26d63b53866644332a7ffb325db30ba5f9ec5ced90833e9a4dc4d393ae2bf"
            ),
            "pred_file_sha256": (
                "442323fe63c1170fecae042e3f5612c1177069e74a39632e92c37fa04f7f3c80"
            ),
            "payload_redistributed": False,
        },
        "zenodo_metadata": {
            "title": "APL FRB sealed prediction pre-registration checksum anchor (reduced capsule)",
            "upload_type": "other",
            "access_right": "open",
            "license": "MIT",
            "license_scope": (
                "Included APL-authored and generated reduced metadata only; the "
                "MIT notice is included in the archive, and no license grant is "
                "made for checksum-referenced excluded members."
            ),
            "version": CAPSULE_VERSION,
            "creators": [
                {"name": "Hladun, Roman", "orcid": "0009-0004-4853-5212"},
                {"name": "Autonomous Physics Lab contributors"},
            ],
            "description": ZENODO_DESCRIPTION,
            "keywords": [
                "sealed prediction",
                "pre-registration",
                "checksum anchor",
                "fast radio bursts",
                "open agent science",
                "reproducibility",
            ],
            "related_identifiers": [
                {
                    "relation": "isSupplementTo",
                    "identifier": FULL_RELEASE_URL,
                    "resource_type": "other",
                },
                {
                    "relation": "isSupplementTo",
                    "identifier": (
                        "https://github.com/open-agent-science/autonomous-physics-lab"
                    ),
                    "resource_type": "software",
                },
            ],
        },
        "policy": {
            "open_reusable_dataset_framing": False,
            "source_derived_value_bearing_members_included": False,
            "external_upload_attempted_by_agent": False,
            "doi_minted_by_agent": False,
            "github_release_asset_changed": False,
            "reveal_labels_inspected": False,
            "reveal_scoring_performed": False,
            "prediction_payload_changed": False,
            "result_claim_knowledge_changed": False,
            "maintainer_upload_and_publish_required": True,
        },
    }
    manifest_bytes = (
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")
    return manifest, readme, manifest_bytes


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
            "Refusing to write capsule output inside the repository. Use an external "
            "output directory or pass --allow-repo-output for disposable local testing."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / archive_name
    sidecar_path = output_dir / manifest_name
    if not force:
        for path in (archive_path, sidecar_path):
            if path.exists():
                raise FileExistsError(f"Output already exists; pass --force to replace: {path}")

    manifest, readme, manifest_bytes = build_content_manifest(repo_root)
    included_by_path = {entry.path: entry for entry in INCLUDED_FILES}
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(_zip_info(README_MEMBER_PATH), readme)
        archive.writestr(_zip_info(MANIFEST_MEMBER_PATH), manifest_bytes)
        for path in manifest["archive_member_allowlist"][2:]:
            entry = included_by_path[str(path)]
            source = _repo_relative_path(repo_root, entry.path)
            archive.writestr(_zip_info(entry.path), source.read_bytes())

    archive_record = {
        "filename": archive_name,
        "path": str(archive_path),
        "bytes": archive_path.stat().st_size,
        "sha256": sha256_file(archive_path),
        "committed_to_repository": False,
        "compression": "zip_stored",
        "fixed_zip_timestamp": "1980-01-01T00:00:00",
    }
    sidecar = dict(manifest)
    sidecar["archive"] = archive_record
    sidecar_path.write_text(
        json.dumps(sidecar, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return sidecar


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
