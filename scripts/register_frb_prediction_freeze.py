#!/usr/bin/env python3
"""Register the approved TASK-0996 FRB prediction freeze.

This helper executes the repository part of the maintainer-approved Class 2
GO_REGISTER decision. It copies the staged TASK-0965 payload, substitutes only
the approval timestamp and approved freeze commit, writes the radio-transients
prediction-registry entry, records the maintainer decision, and builds a local
deterministic anchor capsule for checksum record-back.

It deliberately does not create git tags, GitHub releases, external uploads,
DOIs, results, claims, or reveal scores.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any
import zipfile

import yaml

ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORTS))

from physics_lab.registry.validation import validate_document
from scripts.prepare_frb_pred_registration_pack import (
    DECISION_STUB_PATH,
    PACK_ID,
    PACK_PATH,
    PROPOSED_REGISTRY_PATH,
    stable_digest,
)


TASK_ID = "TASK-0996"
DECISION_PACKET_PATH = "docs/reviews/frb/frb-register-or-hold-decision-packet.md"
REGISTRATION_NOTE_PATH = "docs/reviews/frb/frb-prediction-freeze-registration.md"
EXPECTED_PACK_SHA256 = "0b64202b9bf8ccd37bf23bd4304e374bc10baf17f09498ad5635725eccca75e5"
EXPECTED_TARGETS_SHA256 = "b4b26d63b53866644332a7ffb325db30ba5f9ec5ced90833e9a4dc4d393ae2bf"
EXPECTED_STAGED_ENTRY_SHA256 = "23c2a685fef0b141d3605fb9a89e38f5409cc78a6b5b1e0efd841a9d8cd67014"
MAINTAINER_APPROVAL_CONTEXT = "Codex conversation, 2026-07-10: maintainer selected GO_REGISTER for FRB."
FINAL_CAPSULE_NAME = "frb-pret-repeater-propensity-freeze-anchor-v1.0.0.zip"
FINAL_CAPSULE_MANIFEST_NAME = "frb-pret-repeater-propensity-freeze-anchor-v1.0.0.manifest.json"
FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
ISO_Z_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class CapsuleMember:
    order: int
    path: str
    role: str


FINAL_CAPSULE_MEMBERS = (
    CapsuleMember(1, PACK_PATH, "task_0965_registration_pack"),
    CapsuleMember(2, DECISION_STUB_PATH, "approved_class_2_prediction_freeze_decision"),
    CapsuleMember(3, PROPOSED_REGISTRY_PATH, "registered_radio_transients_pred_entry"),
    CapsuleMember(
        4,
        "data/radio_transients/frb_pre_t_repeater_propensity_model_surface.yaml",
        "task_0964_frozen_model_surface",
    ),
    CapsuleMember(
        5,
        "data/radio_transients/frb_pre_t_model_selection_contract.yaml",
        "task_0964_model_selection_contract",
    ),
    CapsuleMember(
        6,
        "data/radio_transients/frb_catalog1_pre_t_exposure_feature_surface.yaml",
        "task_0963_pre_t_input_surface",
    ),
    CapsuleMember(7, "docs/reviews/frb-sealed-prediction-registration-pack.md", "task_0965_pack_note"),
    CapsuleMember(8, "docs/reviews/frb-campaign-activation-20260708.md", "campaign_activation_note"),
    CapsuleMember(
        9,
        "docs/reviews/frb-catalog1-interval-exposure-pair-checksum-schema-gate.md",
        "catalog1_pair_gate_note",
    ),
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


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
        raise SystemExit(f"{path}: expected YAML mapping")
    return payload


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=False, width=100),
        encoding="utf-8",
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def rel_path(path: Path, *, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _zip_info(path: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(path, date_time=FIXED_ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o644 << 16
    return info


def load_staged_payload(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    pack_path = root / PACK_PATH
    pack_sha = sha256_file(pack_path)
    require(pack_sha == EXPECTED_PACK_SHA256, f"Registration pack SHA drifted: {pack_sha}")

    pack = load_yaml(pack_path)
    require(pack.get("pack_id") == PACK_ID, f"Unexpected pack id: {pack.get('pack_id')}")
    require(pack.get("status") == "prepared_pending_maintainer_prediction_freeze", "Pack is not staged")
    boundary = pack.get("registration_boundary") or {}
    require(boundary.get("registration_executed") is False, "Pack already records registration")
    require(boundary.get("prediction_registry_written") is False, "Pack already records registry write")

    entries = pack.get("sealed_registry_entries")
    require(isinstance(entries, list) and len(entries) == 1, "Expected exactly one sealed entry")
    entry = entries[0]
    require(entry.get("registration_status") == "staged_not_registered", "Entry is not staged")
    require(
        entry.get("proposed_registry_path_on_approval") == PROPOSED_REGISTRY_PATH,
        "Unexpected registry path",
    )

    checksums = entry.get("payload_checksums") or {}
    require(checksums.get("draft_entry_targets_sha256") == EXPECTED_TARGETS_SHA256, "Target digest drifted")
    require(checksums.get("draft_entry_sha256") == EXPECTED_STAGED_ENTRY_SHA256, "Staged entry digest drifted")

    payload = entry.get("would_register_on_maintainer_approval")
    require(isinstance(payload, dict), "Missing staged PRED payload")
    targets = ((payload.get("target_set") or {}).get("targets")) or []
    require(len(targets) == 479, f"Expected 479 FRB targets, found {len(targets)}")
    require(stable_digest(targets) == EXPECTED_TARGETS_SHA256, "Target payload digest drifted")
    require(
        payload.get("registered_at_utc") == "SET_BY_MAINTAINER_PREDICTION_FREEZE_DECISION",
        "Timestamp placeholder missing",
    )
    source_state = payload.get("source_state") or {}
    require(
        source_state.get("git_commit") == "SET_TO_APPROVED_FREEZE_COMMIT",
        "Approved freeze commit placeholder missing",
    )
    return pack, entry, payload


def build_registered_payload(
    *,
    staged_payload: dict[str, Any],
    approved_freeze_commit: str,
    registered_at_utc: str,
) -> dict[str, Any]:
    require(ISO_Z_RE.match(registered_at_utc) is not None, "registered_at_utc must be ISO UTC Z")
    require(COMMIT_RE.match(approved_freeze_commit) is not None, "approved freeze commit must be 40 hex")

    registered = deepcopy(staged_payload)
    registered["registered_at_utc"] = registered_at_utc
    registered["source_state"]["git_commit"] = approved_freeze_commit
    registered["approval_record"] = {
        "decision_id": "DEC-20260709-frb-prediction-freeze-stub",
        "decision_packet": DECISION_PACKET_PATH,
        "selected_option": "GO_REGISTER",
        "approved_by": "maintainer",
        "approved_at_utc": registered_at_utc,
        "approval_context": MAINTAINER_APPROVAL_CONTEXT,
        "approval_task": TASK_ID,
        "approved_freeze_commit": approved_freeze_commit,
        "approved_pack_sha256": EXPECTED_PACK_SHA256,
        "approved_target_payload_sha256": EXPECTED_TARGETS_SHA256,
        "frozen_source_count": 479,
        "prediction_scope": "point_score_and_rank_only",
        "no_uncertainty_claim": True,
        "no_frb_population_claim": True,
        "no_morphology_claim": True,
        "no_label_boundary_confirmed": True,
        "no_claim_or_success_wording": True,
    }
    registered["anchor_record"] = {
        "external_anchor_status": "planned_after_merge",
        "agent_created_git_tag": False,
        "agent_created_github_release": False,
        "reason_external_anchor_pending": (
            "Repository agents do not create git tags or GitHub Releases; the deterministic "
            "capsule checksum is recorded in the TASK-0996 review note for maintainer execution after merge."
        ),
        "final_capsule_manifest_policy": (
            "Use the approved registration pack's nine-path capsule_manifest. The earlier "
            "eleven-member TASK-0994 dry-run capsule was an audit-rich pre-approval package "
            "where the generated staged PRED draft was not a registered artifact."
        ),
    }
    validate_document(registered, "prediction", PROPOSED_REGISTRY_PATH)
    return registered


def build_decision_record(
    *,
    decision: dict[str, Any],
    approved_freeze_commit: str,
    registered_at_utc: str,
    pred_sha256: str,
) -> dict[str, Any]:
    updated = deepcopy(decision)
    updated["artifact_impact"]["prediction_change"] = True
    updated["prepared_registration_pack"]["status"] = "approved_go_register"
    updated["approval_boundary"]["approval_satisfied_for_task_0996"] = True
    updated["approval_boundary"]["registration_not_executed_by_this_stub"] = False
    updated["decision_record"] = {
        "decided_by": "maintainer",
        "applied_by": "codex",
        "status": "go_register_approved",
        "selected_option": "GO_REGISTER",
        "approved_at_utc": registered_at_utc,
        "approval_context": MAINTAINER_APPROVAL_CONTEXT,
        "decision_packet": DECISION_PACKET_PATH,
        "approved_freeze_commit": approved_freeze_commit,
        "approved_pack_sha256": EXPECTED_PACK_SHA256,
        "approved_target_payload_sha256": EXPECTED_TARGETS_SHA256,
        "frozen_source_count": 479,
        "prediction_scope": "point_score_and_rank_only",
        "no_uncertainty_claim": True,
        "no_frb_population_claim": True,
        "no_morphology_claim": True,
        "registered_prediction_path": PROPOSED_REGISTRY_PATH,
        "registered_prediction_sha256": pred_sha256,
        "external_anchor_status": "planned_after_merge",
        "final_capsule_manifest_members": len(FINAL_CAPSULE_MEMBERS),
        "final_capsule_manifest_source": "approved_registration_pack_capsule_manifest",
        "historical_dry_run_capsule_members": 11,
        "revert_of": None,
    }
    return updated


def build_anchor_capsule(root: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / FINAL_CAPSULE_NAME
    manifest_path = output_dir / FINAL_CAPSULE_MANIFEST_NAME
    for path in (archive_path, manifest_path):
        if path.exists():
            path.unlink()

    files: list[dict[str, Any]] = []
    with zipfile.ZipFile(archive_path, "w") as archive:
        for member in FINAL_CAPSULE_MEMBERS:
            source_path = root / member.path
            require(source_path.is_file(), f"Capsule member missing: {member.path}")
            payload = source_path.read_bytes()
            archive.writestr(_zip_info(member.path), payload)
            files.append(
                {
                    "order": member.order,
                    "path": member.path,
                    "role": member.role,
                    "bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                }
            )

    manifest = {
        "schema_version": "1",
        "task_id": TASK_ID,
        "capsule_id": "FRB-PRET-repeater-propensity-freeze-anchor",
        "capsule_version": "1.0.0",
        "dry_run": False,
        "archive": {
            "filename": FINAL_CAPSULE_NAME,
            "path": str(archive_path),
            "bytes": archive_path.stat().st_size,
            "sha256": sha256_file(archive_path),
            "committed_to_repository": False,
            "compression": "zip_stored",
            "fixed_zip_timestamp": "1980-01-01T00:00:00",
        },
        "files": files,
        "policy": {
            "release_tag_created_by_agent": False,
            "github_release_created_by_agent": False,
            "external_upload_attempted_by_agent": False,
            "doi_minted_or_declined_by_agent": False,
            "prediction_registry_written": True,
            "registered_pred_payload_changed_from_approved_targets": False,
            "result_claim_knowledge_changed": False,
            "no_claim_boundary_preserved": True,
        },
        "post_merge_maintainer_actions": [
            "Create the annotated external tag after the TASK-0996 PR merges.",
            "Attach the deterministic capsule bytes whose checksum is recorded in the TASK-0996 note.",
            "Record GitHub Release and optional DOI URLs in a follow-up record-back PR if created.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def build_registration_note(
    *,
    registered_at_utc: str,
    approved_freeze_commit: str,
    pred_sha256: str,
    decision_sha256: str,
    capsule_manifest: dict[str, Any],
) -> str:
    files_table = "\n".join(
        "| {order} | `{path}` | {bytes} | `{sha256}` | {role} |".format(**item)
        for item in capsule_manifest["files"]
    )
    archive = capsule_manifest["archive"]
    return f"""# FRB Prediction Freeze Registration

- Task: `TASK-0996`
- Decision: `GO_REGISTER`
- Decision packet: `{DECISION_PACKET_PATH}`
- Registered prediction: `{PROPOSED_REGISTRY_PATH}`
- Task verdict: `PRED_REGISTERED_AND_ANCHORED`

## Maintainer Approval

The maintainer approved `GO_REGISTER` for the FRB Class 2 prediction freeze in
the active Codex conversation on 2026-07-10. The approval is scoped to the
repaired TASK-0965 registration pack and the TASK-1014 decision packet.

This is a point-score-only prediction registration. It is not a reveal result,
success verdict, calibrated probability, FRB population claim, repeater
discovery claim, result promotion, claim promotion, or knowledge update.

## Registered Payload

| Field | Value |
| --- | --- |
| Registered at UTC | `{registered_at_utc}` |
| Approved freeze commit | `{approved_freeze_commit}` |
| Registration pack SHA-256 | `{EXPECTED_PACK_SHA256}` |
| Target payload SHA-256 | `{EXPECTED_TARGETS_SHA256}` |
| Registered PRED SHA-256 | `{pred_sha256}` |
| Decision record SHA-256 | `{decision_sha256}` |

The registered PRED entry is copied from the staged
`would_register_on_maintainer_approval` payload. Only the maintainer decision
timestamp, approved freeze commit, and approval/anchor record-back fields were
added. The 479 targets, scores, ranks, source set, scoring rule, and target
payload digest remain unchanged.

## Boundary Checks

- No reveal labels were fetched, inspected, scored, summarized, or compared.
- No target id, score, rank, source path, source SHA, formula, or scoring rule
  was edited.
- `data/radio_transients/frb_sealed_prediction_registration_pack.yaml` remains
  byte-identical to the TASK-1014 hash.
- Future reveal scoring remains a separate maintainer-reviewed task governed by
  `docs/reviews/frb-reveal-source-admissibility-contract.md`.

## Anchor Record-Back

The final anchor manifest uses the approved registration pack's nine-path
`capsule_manifest`. The earlier TASK-0994 dry-run capsule had eleven members:
it included a generated staged PRED draft plus two extra pre-approval review
notes for audit context. This registration follows the approved pack manifest as
the governing non-dry-run anchor contract.

The deterministic capsule was built locally for checksum record-back only. This
agent did not create a git tag, GitHub Release, external upload, or DOI.

| Capsule Field | Value |
| --- | --- |
| Archive filename | `{archive["filename"]}` |
| Archive bytes | `{archive["bytes"]}` |
| Archive SHA-256 | `{archive["sha256"]}` |
| Compression | `{archive["compression"]}` |
| Fixed ZIP timestamp | `{archive["fixed_zip_timestamp"]}` |

| Order | Path | Bytes | SHA-256 | Role |
| ---: | --- | ---: | --- | --- |
{files_table}

## Post-Merge Maintainer Actions

After this PR is merged, the maintainer may create the external annotated tag
and GitHub Release using the recorded capsule bytes/checksum above. Any external
release URL or DOI should be recorded in a follow-up record-back PR. The
external anchor must not change the registered PRED payload.

## Output Routing

- Canonical destination: registered `PRED-0001` plus this registration note.
- Review tier: `MAINTAINER_REVIEWED` prediction registration, because the
  Class 2 maintainer approval is the precondition for writing the PRED entry.
- Gate A / Gate B: not applicable.
- Prediction impact: `prediction_registry/radio_transients/PRED-0001.yaml`
  registered.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: no reveal result exists; future reveal scoring requires a
  separate maintainer-reviewed task.
"""


def register_prediction(
    *,
    root: Path,
    registered_at_utc: str,
    approved_freeze_commit: str,
    capsule_output_dir: Path,
) -> dict[str, Any]:
    _pack, _entry, staged_payload = load_staged_payload(root)

    pred_path = root / PROPOSED_REGISTRY_PATH
    registered_payload = build_registered_payload(
        staged_payload=staged_payload,
        approved_freeze_commit=approved_freeze_commit,
        registered_at_utc=registered_at_utc,
    )
    write_yaml(pred_path, registered_payload)
    pred_sha = sha256_file(pred_path)

    decision_path = root / DECISION_STUB_PATH
    decision = load_yaml(decision_path)
    updated_decision = build_decision_record(
        decision=decision,
        approved_freeze_commit=approved_freeze_commit,
        registered_at_utc=registered_at_utc,
        pred_sha256=pred_sha,
    )
    write_yaml(decision_path, updated_decision)
    decision_sha = sha256_file(decision_path)

    capsule_manifest = build_anchor_capsule(root, capsule_output_dir)
    note = build_registration_note(
        registered_at_utc=registered_at_utc,
        approved_freeze_commit=approved_freeze_commit,
        pred_sha256=pred_sha,
        decision_sha256=decision_sha,
        capsule_manifest=capsule_manifest,
    )
    write_text(root / REGISTRATION_NOTE_PATH, note)

    return {
        "registered_prediction": {
            "path": PROPOSED_REGISTRY_PATH,
            "sha256": pred_sha,
        },
        "decision_record": {
            "path": DECISION_STUB_PATH,
            "sha256": decision_sha,
        },
        "anchor_capsule": capsule_manifest["archive"],
        "registration_note": REGISTRATION_NOTE_PATH,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registered-at-utc", required=True)
    parser.add_argument("--approved-freeze-commit", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--capsule-output-dir", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = register_prediction(
        root=Path(args.repo_root).resolve(),
        registered_at_utc=args.registered_at_utc,
        approved_freeze_commit=args.approved_freeze_commit,
        capsule_output_dir=Path(args.capsule_output_dir),
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
