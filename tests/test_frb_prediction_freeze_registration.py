"""Guards for the TASK-0996 approved FRB prediction registration."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import zipfile

import yaml

from physics_lab.registry.validation import infer_kind_from_path, validate_document
from scripts.prepare_frb_pred_registration_pack import stable_digest
from scripts.register_frb_prediction_freeze import (
    DECISION_STUB_PATH,
    EXPECTED_PACK_SHA256,
    EXPECTED_STAGED_ENTRY_SHA256,
    EXPECTED_TARGETS_SHA256,
    FINAL_CAPSULE_MEMBERS,
    PACK_PATH,
    PROPOSED_REGISTRY_PATH,
    REGISTRATION_NOTE_PATH,
    build_registered_payload,
    load_staged_payload,
    register_prediction,
)


ROOT = Path(__file__).resolve().parents[1]
PRED_FILE = ROOT / PROPOSED_REGISTRY_PATH
DECISION_FILE = ROOT / DECISION_STUB_PATH
PACK_FILE = ROOT / PACK_PATH
APPROVED_FREEZE_COMMIT = "83eca7501aea3e4f9869324b5ec2cd722fd7e676"
REGISTERED_AT = "2026-07-10T21:00:36Z"


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    assert isinstance(payload, dict)
    return payload


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_frb_registered_pred_preserves_approved_targets_and_no_claim_boundary() -> None:
    pred = _load_yaml(PRED_FILE)
    pack = _load_yaml(PACK_FILE)
    staged_entry = pack["sealed_registry_entries"][0]
    staged_payload = staged_entry["would_register_on_maintainer_approval"]

    assert _sha256_file(PACK_FILE) == EXPECTED_PACK_SHA256
    assert infer_kind_from_path(PROPOSED_REGISTRY_PATH) == "prediction"
    validate_document(pred, "prediction", PROPOSED_REGISTRY_PATH)

    assert pred["prediction_id"] == "PRED-0001"
    assert pred["registry_status"] == "REGISTERED"
    assert pred["review_tier"] == "MAINTAINER_REVIEWED"
    assert pred["registered_at_utc"] == REGISTERED_AT
    assert pred["source_state"]["git_commit"] == APPROVED_FREEZE_COMMIT

    assert pred["target_set"] == staged_payload["target_set"]
    assert stable_digest(pred["target_set"]["targets"]) == EXPECTED_TARGETS_SHA256
    assert staged_entry["payload_checksums"]["draft_entry_sha256"] == EXPECTED_STAGED_ENTRY_SHA256

    joined = json.dumps(pred, sort_keys=True).lower()
    assert "success verdict" in joined
    assert "no calibrated probability" in joined
    assert "discovery claim" in joined
    assert "reveal labels" not in joined


def test_frb_registration_decision_records_go_register_without_external_publication() -> None:
    decision = _load_yaml(DECISION_FILE)

    assert decision["decision_type"] == "prediction_freeze"
    assert decision["autonomy_class"] == "class_2_maintainer_only"
    assert decision["artifact_impact"]["prediction_change"] is True
    assert decision["artifact_impact"]["external_publication"] is False
    assert decision["decision_record"]["status"] == "go_register_approved"
    assert decision["decision_record"]["selected_option"] == "GO_REGISTER"
    assert decision["decision_record"]["approved_freeze_commit"] == APPROVED_FREEZE_COMMIT
    assert decision["decision_record"]["approved_pack_sha256"] == EXPECTED_PACK_SHA256
    assert decision["decision_record"]["approved_target_payload_sha256"] == EXPECTED_TARGETS_SHA256
    assert decision["decision_record"]["frozen_source_count"] == 479
    assert decision["decision_record"]["prediction_scope"] == "point_score_and_rank_only"
    assert decision["decision_record"]["no_uncertainty_claim"] is True
    assert decision["decision_record"]["no_frb_population_claim"] is True
    assert decision["decision_record"]["no_morphology_claim"] is True
    assert decision["decision_record"]["registered_prediction_path"] == PROPOSED_REGISTRY_PATH
    assert decision["decision_record"]["external_anchor_status"] == "planned_after_merge"
    assert decision["decision_record"]["final_capsule_manifest_members"] == 9
    assert decision["decision_record"]["final_capsule_manifest_source"] == (
        "approved_registration_pack_capsule_manifest"
    )
    assert decision["decision_record"]["historical_dry_run_capsule_members"] == 11


def test_frb_registration_note_records_final_nine_member_capsule() -> None:
    note = (ROOT / REGISTRATION_NOTE_PATH).read_text(encoding="utf-8")

    assert "Task verdict: `PRED_REGISTERED_AND_ANCHORED`" in note
    assert "approved registration pack's nine-path" in note
    assert "TASK-0994 dry-run capsule had eleven members" in note
    assert "completed the GitHub Release" in note
    assert "DOI status | `not_minted`" in note
    assert "The external anchor does not change the registered PRED payload" in note
    for member in FINAL_CAPSULE_MEMBERS:
        assert f"`{member.path}`" in note


def test_frb_registration_helper_is_reproducible(tmp_path: Path) -> None:
    _, _, staged_payload = load_staged_payload(ROOT)
    built = build_registered_payload(
        staged_payload=staged_payload,
        approved_freeze_commit=APPROVED_FREEZE_COMMIT,
        registered_at_utc=REGISTERED_AT,
    )
    assert built == _load_yaml(PRED_FILE)

    # register_prediction writes canonical files. Keep it inside an isolated
    # fixture so xdist workers can never observe transient repository state.
    isolated_root = tmp_path / "repo"
    for member in FINAL_CAPSULE_MEMBERS:
        source = ROOT / member.path
        destination = isolated_root / member.path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    capsule_dir = tmp_path / "capsule"
    summary = register_prediction(
        root=isolated_root,
        registered_at_utc=REGISTERED_AT,
        approved_freeze_commit=APPROVED_FREEZE_COMMIT,
        capsule_output_dir=capsule_dir,
    )
    assert summary["registered_prediction"]["sha256"] == _sha256_file(PRED_FILE)
    assert summary["decision_record"]["sha256"] == _sha256_file(DECISION_FILE)

    archive_path = Path(summary["anchor_capsule"]["path"])
    assert archive_path.is_file()
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.namelist() == [member.path for member in FINAL_CAPSULE_MEMBERS]
        for info in archive.infolist():
            assert info.compress_type == zipfile.ZIP_STORED
            assert info.date_time == (1980, 1, 1, 0, 0, 0)
