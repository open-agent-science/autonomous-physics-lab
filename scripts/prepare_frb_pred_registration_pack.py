#!/usr/bin/env python3
"""Prepare the TASK-0965 FRB sealed-prediction registration pack.

The helper stages the maintainer-facing prediction-freeze surface from the
already frozen TASK-0964 model surface. It deliberately does not write
``prediction_registry/`` entries; registration remains a Class 2 maintainer
decision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

TASK_ID = "TASK-0965"
SOURCE_TASK_ID = "TASK-0964"
PACK_ID = "FRB-PRET-PRED-REGPACK-0001"
DECISION_ID = "DEC-20260709-frb-prediction-freeze-stub"
SOURCE_SURFACE_ID = "FRB-PRET-MODEL-SURFACE-0001"
SOURCE_CONTRACT_ID = "FRB-PRET-MODEL-CONTRACT-0001"
SELECTED_MODEL_ID = "gate_total_exposure_log1p"
SOURCE_MERGE_COMMIT = "3d1da6d0a6278c1d0755adfe8ea27b15ec1e74ea"
SOURCE_SURFACE_SHA256 = "978049b9c7360091f812ee451dae36a5ca81ccea403725a61b36c01a42f562ab"
SOURCE_CONTRACT_SHA256 = "5d3db1fceaafa88a0fd7c68b2c6987e96fa6cf0cd82a3a156cd5be35275ca7df"
INPUT_SURFACE_SHA256 = "8fc57714013a62b51710d48402e23b76eb8f7fa79c17b4e6b0875f06d3374b26"
FEATURE_TABLE_SHA256 = "3e564bc58452b34db133b72d1177bd99eb7fc8ac76036641edb9aa513a65d139"
PER_SOURCE_SCORES_SHA256 = "00404c62efb1edc300f008f53961e691cb1c06208ef5a032ff83b0bf8ddb60d7"
SCORING_RULE = "score_pre_t = log1p(E_upper_hours + E_lower_hours)"
COUNT_TO_HOURS = "E_hours = 4 * exposure_count / 3600"
GENERATED_AT_UTC = "2026-07-09T00:00:00Z"
CAMPAIGN_PROFILE_ID = "radio-transients-frb-pre-t-repeater-propensity"
PROPOSED_REGISTRY_PATH = "prediction_registry/radio_transients/PRED-0001.yaml"
REVIEW_NOTE_PATH = "docs/reviews/frb-sealed-prediction-registration-pack.md"
PACK_PATH = "data/radio_transients/frb_sealed_prediction_registration_pack.yaml"
DECISION_STUB_PATH = "decisions/DEC-20260709-frb-prediction-freeze-stub.yaml"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def stable_digest(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


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


def rel_path(path: Path, *, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def validate_surface(surface: dict[str, Any], *, surface_path: Path) -> list[dict[str, Any]]:
    require(sha256_file(surface_path) == SOURCE_SURFACE_SHA256, "TASK-0964 surface file SHA drifted")
    require(surface.get("artifact_kind") == "frb_pre_t_repeater_propensity_model_surface", "wrong artifact kind")
    require(surface.get("surface_id") == SOURCE_SURFACE_ID, "wrong TASK-0964 surface id")
    require(surface.get("task_id") == SOURCE_TASK_ID, "wrong source task id")
    require(surface.get("status") == "frozen_model_surface", "source surface is not frozen")

    contract = surface.get("contract") or {}
    require(contract.get("contract_id") == SOURCE_CONTRACT_ID, "wrong contract id")
    require(contract.get("sha256") == SOURCE_CONTRACT_SHA256, "contract SHA in surface drifted")

    input_surface = surface.get("input_surface") or {}
    require(input_surface.get("sha256") == INPUT_SURFACE_SHA256, "input surface SHA in surface drifted")
    require(input_surface.get("feature_table_sha256") == FEATURE_TABLE_SHA256, "feature table SHA drifted")
    require(int(input_surface.get("row_count", 0)) == 479, "unexpected input row count")

    boundary = surface.get("feature_boundary") or {}
    require(boundary.get("label_contact") is False, "source surface records label contact")
    require(
        boundary.get("columns_read") == ["source_id", "E_upper_hours", "E_lower_hours", "score_pre_t"],
        "source surface read boundary changed",
    )

    selection = surface.get("selection") or {}
    require(selection.get("outcome") == "FREEZE_EXECUTED", "source selection did not execute")
    require(selection.get("selected_model_id") == SELECTED_MODEL_ID, "unexpected selected model")
    require(selection.get("selected_formula") == "log1p(E_upper_hours + E_lower_hours)", "formula drifted")
    require(selection.get("label_performance_metric") == "none", "label metric appeared")

    scoring = surface.get("frozen_scoring_rule") or {}
    require(scoring.get("score_pre_t") == SCORING_RULE, "scoring rule drifted")
    require(scoring.get("count_to_hours") == COUNT_TO_HOURS, "count-to-hours rule drifted")
    require(scoring.get("modification_allowed") is False, "scoring rule became mutable")

    rows = surface.get("per_source_scores")
    require(isinstance(rows, list) and len(rows) == 479, "unexpected per-source score rows")
    require(int(surface.get("per_source_score_count", 0)) == 479, "score-count field drifted")
    require(surface.get("per_source_scores_sha256") == PER_SOURCE_SCORES_SHA256, "score digest field drifted")
    require(stable_digest(rows) == PER_SOURCE_SCORES_SHA256, "score payload digest drifted")

    seen: set[str] = set()
    for index, row in enumerate(rows, start=1):
        require(isinstance(row, dict), "score row is not a mapping")
        source_id = str(row.get("source_id", ""))
        require(source_id.startswith("FRB"), f"unexpected source id: {source_id}")
        require(source_id not in seen, f"duplicate source id: {source_id}")
        seen.add(source_id)
        require(int(row.get("rank_descending", 0)) == index, "rank ordering drifted")
        float(row["selected_model_score"])
    return rows


def build_targets(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    targets = []
    for row in rows:
        targets.append(
            {
                "target_id": str(row["source_id"]),
                "prediction_quantity": "pre_t_repeater_propensity_score",
                "predicted_score": float(row["selected_model_score"]),
                "rank_descending": int(row["rank_descending"]),
                "uncertainty": None,
                "confidence_note": (
                    "Point score only from the TASK-0964 frozen exposure surface; no calibrated "
                    "probability, interval, success verdict, or astrophysical claim is registered."
                ),
            }
        )
    return targets


def build_reveal_conditions() -> dict[str, Any]:
    return {
        "comparison_source_class": (
            "One of the three admissible classes in the TASK-0995 reveal-source "
            "admissibility contract: an official checksum-pinned CHIME/FRB catalog "
            "snapshot released after T, an official CHIME/FRB repeat-source or "
            "source-association table with an immutable checksummed reference, or a "
            "maintainer-approved frozen manifest of citable external reveal records."
        ),
        "reveal_source_admissibility_contract": (
            "docs/reviews/frb-reveal-source-admissibility-contract.md"
        ),
        "reveal_source_admissibility_rule": (
            "Any future reveal is governed by the TASK-0995 contract: its admissible "
            "and inadmissible source classes, required manifest fields, source-id "
            "matching policy, label-status enum, one-row-per-frozen-target "
            "eligibility table, frozen comparators, and stop conditions apply before "
            "any label is read."
        ),
        "reveal_controlled_by": "maintainer",
        "label_rule": (
            "Labels come only from the pinned later snapshot or external reveal record; "
            "positive repeat status requires repeat evidence published strictly after "
            "T=2019-07-02."
        ),
        "no_peek_rule": (
            "Do not alter the source set, frozen model surface, scoring rule, target values, "
            "target ranks, or source-state references after reveal-relevant labels become visible."
        ),
        "partial_reveal_allowed": False,
        "expected_reveal_window": "unknown",
        "reveal_task_required": True,
    }


def build_registration_pack(
    *,
    root: Path,
    surface: dict[str, Any],
    surface_path: Path,
    rows: list[dict[str, Any]],
    generated_at_utc: str,
) -> dict[str, Any]:
    targets = build_targets(rows)
    targets_digest = stable_digest(targets)
    draft_entry = {
        "draft_entry_id": "FRB-PRET-PRED-DRAFT-0001",
        "proposed_registry_path_on_approval": PROPOSED_REGISTRY_PATH,
        "registration_status": "staged_not_registered",
        "would_register_on_maintainer_approval": {
            "prediction_id": "PRED-0001",
            "title": "FRB Catalog-1 pre-T exposure-only repeater-propensity scores",
            "registry_status": "REGISTERED",
            "campaign_profile_id": CAMPAIGN_PROFILE_ID,
            "task_id": TASK_ID,
            "evidence_class": "prospective_prediction_registry",
            "freeze_tier": "point_score_only",
            "claim_ceiling": (
                "Registered prospective repeater-propensity score surface only; no success verdict, "
                "FRB population claim, repeater discovery claim, or knowledge promotion before a "
                "separate maintainer-reviewed reveal comparison."
            ),
            "registered_by": {
                "contributor_id": "gladunrv",
                "agent_id": "codex",
            },
            "registered_at_utc": "SET_BY_MAINTAINER_PREDICTION_FREEZE_DECISION",
            "source_state": {
                "git_commit": "SET_TO_APPROVED_FREEZE_COMMIT",
                "source_merge_commit": SOURCE_MERGE_COMMIT,
                "model_reference": {
                    "model_id": f"{SOURCE_SURFACE_ID}::{SELECTED_MODEL_ID}",
                    "source_path": rel_path(surface_path, root=root),
                    "source_sha256": SOURCE_SURFACE_SHA256,
                    "selected_formula": "log1p(E_upper_hours + E_lower_hours)",
                    "frozen_parameters_note": (
                        "The prediction surface is exactly the TASK-0964 frozen label-free "
                        "exposure score: score_pre_t = log1p(E_upper_hours + E_lower_hours)."
                    ),
                },
                "baseline_reference": {
                    "baseline_id": "constant_zero_null",
                    "source_path": rel_path(surface_path, root=root),
                    "note": "TASK-0964 retained the constant zero null as a comparator, not as a selected model.",
                },
                "training_data_references": [
                    "data/radio_transients/frb_catalog1_pre_t_exposure_feature_surface.yaml",
                    "data/radio_transients/frb_pre_t_model_selection_contract.yaml",
                    "data/radio_transients/frb_pre_t_repeater_propensity_model_surface.yaml",
                ],
                "holdout_protocol_references": [
                    "docs/blind-holdout-benchmark-protocol.md",
                    "docs/prediction-registry-policy.md",
                    "docs/result-promotion-protocol.md",
                    "docs/reviews/frb-catalog1-interval-exposure-pair-checksum-schema-gate.md",
                    "docs/reviews/frb-reveal-source-admissibility-contract.md",
                ],
                "live_external_fetch_allowed": False,
                "source_data_state_note": (
                    "Pack preparation used only committed repository files. It did not fetch a "
                    "later catalog, inspect repeat labels, compare outcomes, or score reveal performance."
                ),
            },
            "target_set": {
                "label": "frb-catalog1-pre-t-exposure-score-surface-v1",
                "quantity": "pre_t_repeater_propensity_score",
                "unit": "dimensionless_log1p_exposure_hours",
                "target_count": len(targets),
                "targets": targets,
            },
            "uncertainty_semantics": (
                "point_score_only: scores are deterministic exposure-only ranks, not "
                "calibrated probabilities or prediction intervals."
            ),
            "reveal_conditions": build_reveal_conditions(),
            "limitations": [
                "Prepared registration pack only; no prediction registry entry is written by TASK-0965.",
                "No later repeat label, Catalog 2 full-window exposure, morphology field, or post-T source association is read.",
                "The score is an exposure-propensity ranking, not an FRB population law or discovery claim.",
                "Any reveal score, success verdict, result, claim, or knowledge update requires a separate reviewed task.",
            ],
            "review_tier": "MAINTAINER_REVIEWED",
        },
        "payload_checksums": {
            "source_surface_sha256": SOURCE_SURFACE_SHA256,
            "surface_per_source_scores_sha256": PER_SOURCE_SCORES_SHA256,
            "draft_entry_targets_sha256": targets_digest,
        },
    }
    draft_entry["payload_checksums"]["draft_entry_sha256"] = stable_digest(
        draft_entry["would_register_on_maintainer_approval"]
    )

    return {
        "artifact_kind": "frb_sealed_prediction_registration_pack",
        "pack_id": PACK_ID,
        "task_id": TASK_ID,
        "status": "prepared_pending_maintainer_prediction_freeze",
        "generated_at_utc": generated_at_utc,
        "registration_boundary": {
            "registration_executed": False,
            "prediction_registry_written": False,
            "required_decision_type": "prediction_freeze",
            "required_autonomy_class": "class_2_maintainer_only",
            "decision_stub_path": DECISION_STUB_PATH,
            "maintainer_approval_required": True,
            "no_claim_wording_required": True,
        },
        "source_freeze": {
            "source_task_id": SOURCE_TASK_ID,
            "source_merge_commit": SOURCE_MERGE_COMMIT,
            "frozen_surface": {
                "path": rel_path(surface_path, root=root),
                "sha256": SOURCE_SURFACE_SHA256,
                "surface_id": surface["surface_id"],
                "status": surface["status"],
                "per_source_score_count": surface["per_source_score_count"],
                "per_source_scores_sha256": PER_SOURCE_SCORES_SHA256,
            },
            "contract": {
                "path": surface["contract"]["path"],
                "sha256": SOURCE_CONTRACT_SHA256,
                "contract_id": SOURCE_CONTRACT_ID,
            },
            "input_surface": {
                "path": surface["input_surface"]["path"],
                "sha256": INPUT_SURFACE_SHA256,
                "feature_table_sha256": FEATURE_TABLE_SHA256,
                "row_count": 479,
            },
            "selected_model": {
                "model_id": SELECTED_MODEL_ID,
                "formula": "log1p(E_upper_hours + E_lower_hours)",
                "rule": surface["selection"]["rule"],
            },
            "frozen_scoring_rule": {
                "score_pre_t": SCORING_RULE,
                "count_to_hours": COUNT_TO_HOURS,
                "modification_allowed": False,
            },
            "feature_boundary": {
                "label_contact": False,
                "columns_read": ["source_id", "E_upper_hours", "E_lower_hours", "score_pre_t"],
                "forbidden_features_excluded": surface["feature_boundary"]["forbidden_features_excluded"],
            },
        },
        "sealed_registry_entries": [draft_entry],
        "reveal_conditions": build_reveal_conditions(),
        "external_anchor_plan": {
            "anchor_status": "planned_not_executed",
            "registration_time_actions": [
                "Create an annotated tag at the maintainer-approved freeze commit.",
                "Create a GitHub Release for that tag and attach the deterministic archive capsule.",
                "Record capsule byte size, SHA-256, and any archival DOI in a follow-up anchor note.",
            ],
            "suggested_tag_template": "pred-frb-pret-repeater-propensity-YYYYMMDD",
            "suggested_release_title": "FRB pre-T repeater-propensity prediction freeze",
            "capsule_manifest": [
                PACK_PATH,
                DECISION_STUB_PATH,
                PROPOSED_REGISTRY_PATH,
                "data/radio_transients/frb_pre_t_repeater_propensity_model_surface.yaml",
                "data/radio_transients/frb_pre_t_model_selection_contract.yaml",
                "data/radio_transients/frb_catalog1_pre_t_exposure_feature_surface.yaml",
                REVIEW_NOTE_PATH,
                "docs/reviews/frb-campaign-activation-20260708.md",
                "docs/reviews/frb-catalog1-interval-exposure-pair-checksum-schema-gate.md",
            ],
            "archive_capsule_rule": (
                "Build the capsule only after maintainer approval so the approved decision, final "
                "registered PRED entry, and exact freeze commit are all inside the archived bytes."
            ),
        },
        "limitations": [
            "This pack is not a registration, reveal result, success verdict, claim, or knowledge artifact.",
            "Registration must stop unless the maintainer records an explicit Class 2 prediction_freeze decision.",
            "Scores are deterministic exposure-only ranks; they are not calibrated probabilities.",
            "Labels for later comparison must come only from a pinned later snapshot or external reveal record with repeat evidence strictly after T.",
        ],
        "output_routing": {
            "canonical_destination": "data/radio_transients/frb_sealed_prediction_registration_pack.yaml",
            "review_tier": "maintainer_decision_required_before_registration",
            "gate_a_status": "not_applicable",
            "gate_b_status": "not_applicable",
            "prediction_impact": "prediction freeze staged; no registered PRED artifact written",
            "claim_impact": "none",
            "knowledge_impact": "none",
            "publication_blocker": "Class 2 maintainer prediction_freeze decision still required",
        },
    }


def build_decision_stub(*, pack_sha256: str, generated_at_utc: str) -> dict[str, Any]:
    return {
        "decision_id": DECISION_ID,
        "decision_type": "prediction_freeze",
        "autonomy_class": "class_2_maintainer_only",
        "reversibility": "hard_to_reverse",
        "external_exposure": "planned_after_approval",
        "artifact_impact": {
            "result_status_change": False,
            "claim_status_change": False,
            "prediction_change": False,
            "knowledge_change": False,
            "external_publication": False,
        },
        "recommended_action": "approve_frb_sealed_prediction_registration_after_maintainer_review",
        "prepared_at_utc": generated_at_utc,
        "prepared_registration_pack": {
            "path": PACK_PATH,
            "sha256": pack_sha256,
            "pack_id": PACK_ID,
            "status": "prepared_pending_maintainer_prediction_freeze",
        },
        "basis": [
            "TASK-0965 prepares the registration pack after TASK-0964 merged.",
            "TASK-0964 froze an exposure-only model surface with label_contact=false and no reveal labels read.",
            "The FRB campaign activation record requires PRED registration by end of July 2026 without compressing reveal discipline.",
            "The NMD-0003 tier-1 precedent requires explicit maintainer approval plus an external anchor plan.",
        ],
        "approval_boundary": {
            "approval_required_before_prediction_registry_write": True,
            "approval_required_before_external_anchor": True,
            "registration_not_executed_by_this_stub": True,
            "no_claim_or_success_verdict": True,
        },
        "agent_quorum": {
            "executor_agent": {
                "vote": "prepare_only",
                "agent_id": "codex",
                "model_version": "GPT-5",
                "review_notes": (
                    "Prepared a maintainer-facing registration pack and checksums only. "
                    "No prediction registry file, reveal score, claim, or external anchor is applied."
                ),
            },
            "cross_vendor": False,
        },
        "devils_advocate": {
            "strongest_objection": (
                "A staged pack can be mistaken for an active prediction registration if the boundary is weak."
            ),
            "control": (
                "The pack status is prepared_pending_maintainer_prediction_freeze, the registry write flag "
                "is false, and the future PRED path is only a proposed on-approval path."
            ),
            "escalation_required": True,
        },
        "veto": {
            "window_hours": 48,
            "deadline_utc": None,
            "maintainer_vetoed": False,
        },
        "decision_record": {
            "decided_by": "maintainer",
            "applied_by": "pending",
            "status": "dry_run_only",
            "revert_of": None,
        },
    }


def build_review_note(*, pack: dict[str, Any], pack_sha256: str, decision_sha256: str) -> str:
    entry = pack["sealed_registry_entries"][0]
    targets = entry["would_register_on_maintainer_approval"]["target_set"]["targets"]
    top_rows = targets[:10]
    top_table = "\n".join(
        f"| {row['rank_descending']} | `{row['target_id']}` | {row['predicted_score']:.12g} |"
        for row in top_rows
    )
    return f"""# FRB Sealed Prediction Registration Pack

- Task: `TASK-0965`
- Pack: `data/radio_transients/frb_sealed_prediction_registration_pack.yaml`
- Pack SHA-256: `{pack_sha256}`
- Decision stub: `decisions/DEC-20260709-frb-prediction-freeze-stub.yaml`
- Decision stub SHA-256: `{decision_sha256}`
- Status: `PREPARED_PENDING_MAINTAINER_PREDICTION_FREEZE`

## Boundary

This task prepares the FRB prediction-registration surface but does not execute
registration. No `prediction_registry/radio_transients/PRED-0001.yaml` file is
written, no reveal labels are read, and no external anchor is created. The
registered artifact appears only after an explicit Class 2 maintainer
`prediction_freeze` decision.

## Frozen Input

The pack is derived solely from the TASK-0964 frozen model surface:

| Artifact | SHA-256 |
| --- | --- |
| `data/radio_transients/frb_pre_t_repeater_propensity_model_surface.yaml` | `{SOURCE_SURFACE_SHA256}` |
| `data/radio_transients/frb_pre_t_model_selection_contract.yaml` | `{SOURCE_CONTRACT_SHA256}` |
| `data/radio_transients/frb_catalog1_pre_t_exposure_feature_surface.yaml` | `{INPUT_SURFACE_SHA256}` |
| per-source score payload | `{PER_SOURCE_SCORES_SHA256}` |

The scoring rule is frozen verbatim:
`{SCORING_RULE}` with `{COUNT_TO_HOURS}`. The feature boundary remains
`label_contact=false`; the pack reads no repeat labels, Catalog 2 full-window
exposure, morphology fields, or post-T source associations.

## Sealed Entry Shape

The pack stages one draft registry entry for
`prediction_registry/radio_transients/PRED-0001.yaml` on approval. It contains
479 source-level point scores and ranks.

| Rank | Source | Frozen score |
| ---: | --- | ---: |
{top_table}

Target payload SHA-256:
`{entry['payload_checksums']['draft_entry_targets_sha256']}`.

These scores are exposure-only propensity ranks. They are not calibrated
probabilities, intervals, discovery claims, population claims, or a success
verdict.

## Reveal Conditions

Future labels must come only from a checksum-pinned later CHIME/FRB snapshot or
maintainer-approved external reveal record. Positive repeat status requires
repeat evidence published strictly after `T=2019-07-02`. A reveal comparison is
a separate reviewed task and must leave the frozen source set, scores, ranks,
and scoring rule unchanged.

## External Anchor Plan

After maintainer approval, create an annotated tag at the approved freeze
commit, publish a GitHub Release for the tag, and attach a deterministic archive
capsule containing the approved decision, registered PRED entry, this pack, the
TASK-0964 surface and contract, the TASK-0963 input surface, and this review
note. Record the capsule byte size, SHA-256, and any archive DOI in a follow-up
anchor note. Until that approval happens, the anchor is planned only.

## Output Routing

- Canonical destination: `data/radio_transients/frb_sealed_prediction_registration_pack.yaml`.
- Review tier: maintainer decision required before registration.
- Prediction impact: staged only; no registered `PRED-*` artifact is written.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: explicit Class 2 maintainer `prediction_freeze`
  decision.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--surface",
        default="data/radio_transients/frb_pre_t_repeater_propensity_model_surface.yaml",
        help="Frozen TASK-0964 model surface.",
    )
    parser.add_argument("--pack", default=PACK_PATH, help="Output registration-pack YAML path.")
    parser.add_argument("--decision-stub", default=DECISION_STUB_PATH, help="Output decision-stub YAML path.")
    parser.add_argument("--review-note", default=REVIEW_NOTE_PATH, help="Output review note path.")
    parser.add_argument("--generated-at-utc", default=GENERATED_AT_UTC)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    surface_path = root / args.surface
    pack_path = root / args.pack
    decision_path = root / args.decision_stub
    review_note_path = root / args.review_note

    surface = load_yaml(surface_path)
    rows = validate_surface(surface, surface_path=surface_path)
    pack = build_registration_pack(
        root=root,
        surface=surface,
        surface_path=surface_path,
        rows=rows,
        generated_at_utc=str(args.generated_at_utc),
    )
    write_yaml(pack_path, pack)
    pack_sha256 = sha256_file(pack_path)

    decision = build_decision_stub(pack_sha256=pack_sha256, generated_at_utc=str(args.generated_at_utc))
    write_yaml(decision_path, decision)
    decision_sha256 = sha256_file(decision_path)

    review_note = build_review_note(pack=pack, pack_sha256=pack_sha256, decision_sha256=decision_sha256)
    write_text(review_note_path, review_note)

    print(f"wrote {rel_path(pack_path, root=root)} sha256={pack_sha256}")
    print(f"wrote {rel_path(decision_path, root=root)} sha256={decision_sha256}")
    print(f"wrote {rel_path(review_note_path, root=root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
