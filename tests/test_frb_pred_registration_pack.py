"""Guards for the TASK-0965 FRB sealed prediction-registration pack."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import yaml

from scripts.prepare_frb_pred_registration_pack import (
    COUNT_TO_HOURS,
    DECISION_STUB_PATH,
    FEATURE_TABLE_SHA256,
    INPUT_SURFACE_SHA256,
    PACK_PATH,
    PER_SOURCE_SCORES_SHA256,
    SCORING_RULE,
    SOURCE_CONTRACT_SHA256,
    SOURCE_MERGE_COMMIT,
    SOURCE_SURFACE_SHA256,
)

ROOT = Path(__file__).resolve().parents[1]
PACK_FILE = ROOT / PACK_PATH
DECISION_FILE = ROOT / DECISION_STUB_PATH
SURFACE_FILE = ROOT / "data" / "radio_transients" / "frb_pre_t_repeater_propensity_model_surface.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    assert isinstance(payload, dict)
    return payload


def _sha256_file(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def _stable_digest(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


def test_frb_pack_is_staged_not_registered_and_decision_stub_is_class_2() -> None:
    pack = _load_yaml(PACK_FILE)
    decision = _load_yaml(DECISION_FILE)

    assert pack["task_id"] == "TASK-0965"
    assert pack["status"] == "prepared_pending_maintainer_prediction_freeze"
    assert pack["registration_boundary"] == {
        "registration_executed": False,
        "prediction_registry_written": False,
        "required_decision_type": "prediction_freeze",
        "required_autonomy_class": "class_2_maintainer_only",
        "decision_stub_path": DECISION_STUB_PATH,
        "maintainer_approval_required": True,
        "no_claim_wording_required": True,
    }

    assert decision["decision_type"] == "prediction_freeze"
    assert decision["autonomy_class"] == "class_2_maintainer_only"
    assert decision["prepared_registration_pack"]["sha256"] == _sha256_file(PACK_FILE)
    assert decision["approval_boundary"]["registration_not_executed_by_this_stub"] is True
    assert decision["artifact_impact"]["prediction_change"] is False
    assert decision["artifact_impact"]["external_publication"] is False
    assert decision["decision_record"]["status"] == "dry_run_only"


def test_frb_pack_source_freeze_matches_task_0964_surface() -> None:
    pack = _load_yaml(PACK_FILE)
    surface = _load_yaml(SURFACE_FILE)
    source_freeze = pack["source_freeze"]

    assert _sha256_file(SURFACE_FILE) == SOURCE_SURFACE_SHA256
    assert source_freeze["source_task_id"] == "TASK-0964"
    assert source_freeze["source_merge_commit"] == SOURCE_MERGE_COMMIT
    assert source_freeze["frozen_surface"]["surface_id"] == surface["surface_id"]
    assert source_freeze["frozen_surface"]["sha256"] == SOURCE_SURFACE_SHA256
    assert source_freeze["frozen_surface"]["per_source_score_count"] == 479
    assert source_freeze["frozen_surface"]["per_source_scores_sha256"] == PER_SOURCE_SCORES_SHA256
    assert source_freeze["contract"]["sha256"] == SOURCE_CONTRACT_SHA256
    assert source_freeze["input_surface"]["sha256"] == INPUT_SURFACE_SHA256
    assert source_freeze["input_surface"]["feature_table_sha256"] == FEATURE_TABLE_SHA256
    assert source_freeze["frozen_scoring_rule"] == {
        "score_pre_t": SCORING_RULE,
        "count_to_hours": COUNT_TO_HOURS,
        "modification_allowed": False,
    }
    assert source_freeze["feature_boundary"]["label_contact"] is False


def test_frb_pack_targets_are_exactly_the_frozen_per_source_scores() -> None:
    pack = _load_yaml(PACK_FILE)
    surface = _load_yaml(SURFACE_FILE)

    entry = pack["sealed_registry_entries"][0]
    assert entry["registration_status"] == "staged_not_registered"
    assert entry["proposed_registry_path_on_approval"] == (
        "prediction_registry/radio_transients/PRED-0001.yaml"
    )

    would_register = entry["would_register_on_maintainer_approval"]
    assert would_register["registry_status"] == "REGISTERED"
    assert would_register["registered_at_utc"] == "SET_BY_MAINTAINER_PREDICTION_FREEZE_DECISION"
    assert would_register["source_state"]["git_commit"] == "SET_TO_APPROVED_FREEZE_COMMIT"
    assert would_register["source_state"]["live_external_fetch_allowed"] is False
    assert would_register["review_tier"] == "MAINTAINER_REVIEW_REQUIRED"

    targets = would_register["target_set"]["targets"]
    score_rows = surface["per_source_scores"]
    assert would_register["target_set"]["target_count"] == len(targets) == len(score_rows) == 479
    assert _stable_digest(score_rows) == PER_SOURCE_SCORES_SHA256
    assert _stable_digest(targets) == entry["payload_checksums"]["draft_entry_targets_sha256"]

    frozen_projection = [
        (row["source_id"], float(row["selected_model_score"]), int(row["rank_descending"]))
        for row in score_rows
    ]
    staged_projection = [
        (row["target_id"], float(row["predicted_score"]), int(row["rank_descending"]))
        for row in targets
    ]
    assert staged_projection == frozen_projection


def test_frb_pack_reveal_and_anchor_boundaries_are_explicit() -> None:
    pack = _load_yaml(PACK_FILE)
    entry = pack["sealed_registry_entries"][0]["would_register_on_maintainer_approval"]
    reveal = entry["reveal_conditions"]
    anchor = pack["external_anchor_plan"]
    limitations = "\n".join(pack["limitations"] + entry["limitations"]).lower()

    assert "strictly after T=2019-07-02" in reveal["label_rule"]
    assert "do not alter" in reveal["no_peek_rule"].lower()
    assert reveal["reveal_controlled_by"] == "maintainer"
    assert reveal["reveal_task_required"] is True
    assert anchor["anchor_status"] == "planned_not_executed"
    assert any("annotated tag" in item for item in anchor["registration_time_actions"])
    assert any("GitHub Release" in item for item in anchor["registration_time_actions"])
    assert any("archive capsule" in item for item in anchor["registration_time_actions"])
    assert "not a registration" in limitations
    assert "not calibrated probabilities" in limitations
    assert "claim" in entry["claim_ceiling"].lower()


def test_frb_pack_helper_reproduces_committed_artifacts(tmp_path: Path) -> None:
    tmp_pack = tmp_path / "pack.yaml"
    tmp_decision = tmp_path / "decision.yaml"
    tmp_note = tmp_path / "review.md"
    subprocess.run(
        [
            sys.executable,
            "scripts/prepare_frb_pred_registration_pack.py",
            "--pack",
            str(tmp_pack),
            "--decision-stub",
            str(tmp_decision),
            "--review-note",
            str(tmp_note),
        ],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert tmp_pack.read_bytes() == PACK_FILE.read_bytes()
    assert tmp_decision.read_bytes() == DECISION_FILE.read_bytes()
    assert tmp_note.read_bytes() == (ROOT / "docs/reviews/frb-sealed-prediction-registration-pack.md").read_bytes()
