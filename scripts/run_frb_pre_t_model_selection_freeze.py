#!/usr/bin/env python3
"""Freeze the TASK-0964 FRB pre-T exposure-only model surface.

This runner consumes the predeclared TASK-0964 contract and the committed
TASK-0963 feature surface. It does not read repeat labels, Catalog 2 full-window
exposure, morphology, or post-T association fields. Selection is label-free:
the winner is chosen by the contract's frozen coverage/rank-resolution rule.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import yaml

TASK_ID = "TASK-0964"
SURFACE_ID = "FRB-PRET-MODEL-SURFACE-0001"
CONTRACT_ID = "FRB-PRET-MODEL-CONTRACT-0001"
SELECTED_MODEL_ID = "gate_total_exposure_log1p"
REQUIRED_FEATURE_TABLE_SHA256 = "3e564bc58452b34db133b72d1177bd99eb7fc8ac76036641edb9aa513a65d139"
REQUIRED_INPUT_SURFACE_SHA256 = "8fc57714013a62b51710d48402e23b76eb8f7fa79c17b4e6b0875f06d3374b26"
SCORING_RULE = "score_pre_t = log1p(E_upper_hours + E_lower_hours)"
COUNT_TO_HOURS = "E_hours = 4 * exposure_count / 3600"
SCORE_IDENTITY_TOLERANCE = 1.1e-12
FORBIDDEN_LABEL_FIELDS = {
    "repeater_name",
    "repeat_label",
    "label",
    "exp_up",
    "exp_low",
    "morphology",
}
READ_FIELDS = ("source_id", "E_upper_hours", "E_lower_hours", "score_pre_t")


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
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def rel_path(path: Path, *, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def round12(value: float) -> float:
    return round(float(value), 12)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def validate_contract(contract: dict[str, Any], *, contract_path: Path, root: Path) -> Path:
    require(contract.get("contract_id") == CONTRACT_ID, "unexpected contract_id")
    require(contract.get("task_id") == TASK_ID, "unexpected contract task_id")
    require(contract.get("status") == "predeclared_contract", "contract is not predeclared")
    frozen = contract.get("frozen_scoring_rule") or {}
    require(frozen.get("score_pre_t") == SCORING_RULE, "scoring rule drifted from gate formula")
    require(frozen.get("count_to_hours") == COUNT_TO_HOURS, "count-to-hours rule drifted")
    boundary = contract.get("feature_boundary") or {}
    require(boundary.get("label_contact_allowed") is False, "contract permits label contact")
    require(boundary.get("label_columns_read") == [], "contract declares label columns")
    require(boundary.get("label_use_for_selection") == "none", "contract permits label selection")

    input_surface = contract.get("input_surface") or {}
    require(
        input_surface.get("feature_table_sha256") == REQUIRED_FEATURE_TABLE_SHA256,
        "input feature-table sha256 is not the TASK-0963 frozen value",
    )
    require(
        input_surface.get("file_sha256") == REQUIRED_INPUT_SURFACE_SHA256,
        "input surface file sha256 is not the TASK-0963 frozen value",
    )
    surface_path = root / str(input_surface.get("path", ""))
    require(surface_path.exists(), f"input surface missing: {surface_path}")
    require(sha256_file(surface_path) == REQUIRED_INPUT_SURFACE_SHA256, "input surface file sha256 mismatch")
    require(contract_path.exists(), "contract path missing")
    return surface_path


def validate_feature_surface(surface: dict[str, Any]) -> list[dict[str, Any]]:
    require(surface.get("task_id") == "TASK-0963", "input surface is not TASK-0963")
    require(surface.get("artifact_id") == "FRB-CAT1-PRET-EXPOSURE-0001", "unexpected input artifact")
    require(surface.get("status") == "constructed_feature_surface", "input surface is not constructed")
    require(surface.get("verdict") == "PRE_T_EXPOSURE_FEATURE_SURFACE_CONSTRUCTED", "unexpected verdict")
    require(surface.get("feature_table_sha256") == REQUIRED_FEATURE_TABLE_SHA256, "feature table sha mismatch")

    contract = surface.get("feature_contract") or {}
    require(contract.get("label_contact") is False, "input surface records label contact")
    require(contract.get("label_columns_read") == [], "input surface read label columns")
    require(contract.get("scoring_rule") == SCORING_RULE, "input scoring rule mismatch")
    require(contract.get("count_to_hours") == COUNT_TO_HOURS, "input count-to-hours rule mismatch")

    rows = surface.get("features")
    require(isinstance(rows, list) and rows, "input surface has no feature rows")
    for row in rows:
        require(isinstance(row, dict), "feature row is not a mapping")
        forbidden = sorted(FORBIDDEN_LABEL_FIELDS.intersection(row))
        require(not forbidden, f"feature row contains forbidden label/full-window fields: {forbidden}")
        for field in READ_FIELDS:
            require(field in row, f"feature row missing required field: {field}")
    return rows


def score_model(model_id: str, row: dict[str, Any]) -> float:
    upper = float(row["E_upper_hours"])
    lower = float(row["E_lower_hours"])
    if model_id == "gate_total_exposure_log1p":
        return float(row["score_pre_t"])
    if model_id == "upper_transit_only_log1p":
        return math.log1p(upper)
    if model_id == "lower_transit_only_log1p":
        return math.log1p(lower)
    if model_id == "constant_zero_null":
        return 0.0
    raise SystemExit(f"unknown model_id: {model_id}")


def evaluate_models(contract: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evaluations = []
    for model in contract["candidate_models"]:
        model_id = str(model["model_id"])
        scores = [round12(score_model(model_id, row)) for row in rows]
        if model.get("must_equal_fixture_field") == "score_pre_t":
            for row, score in zip(rows, scores, strict=True):
                recomputed = math.log1p(float(row["E_upper_hours"]) + float(row["E_lower_hours"]))
                require(
                    abs(recomputed - score) <= SCORE_IDENTITY_TOLERANCE,
                    "gate candidate no longer equals score_pre_t",
                )
        unique_scores = len(set(scores))
        nonzero_rows = sum(1 for score in scores if score > 0.0)
        evaluations.append(
            {
                "model_id": model_id,
                "role": model["role"],
                "formula": model["formula"],
                "uses_both_transits": bool(model.get("uses_upper_transit"))
                and bool(model.get("uses_lower_transit")),
                "uses_upper_transit": bool(model.get("uses_upper_transit")),
                "uses_lower_transit": bool(model.get("uses_lower_transit")),
                "selection_priority": int(model["selection_priority"]),
                "finite_score_rows": len(scores),
                "nonzero_score_rows": nonzero_rows,
                "unique_score_values": unique_scores,
                "min_score": min(scores),
                "max_score": max(scores),
                "mean_score": round12(sum(scores) / len(scores)),
                "score_vector_sha256": stable_digest(scores),
            }
        )
    return evaluations


def select_model(evaluations: list[dict[str, Any]]) -> dict[str, Any]:
    null = next(item for item in evaluations if item["model_id"] == "constant_zero_null")
    ranked = sorted(
        evaluations,
        key=lambda item: (
            item["uses_both_transits"],
            item["nonzero_score_rows"],
            item["unique_score_values"],
            -item["selection_priority"],
            item["model_id"],
        ),
        reverse=True,
    )
    winner = ranked[0]
    require(winner["model_id"] == SELECTED_MODEL_ID, f"unexpected selected model: {winner['model_id']}")
    require(
        winner["nonzero_score_rows"] > null["nonzero_score_rows"],
        "selected model does not beat constant null nonzero coverage",
    )
    require(
        winner["unique_score_values"] > null["unique_score_values"],
        "selected model does not beat constant null rank resolution",
    )
    return winner


def build_score_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored = [
        {
            "source_id": str(row["source_id"]),
            "selected_model_score": round12(score_model(SELECTED_MODEL_ID, row)),
        }
        for row in rows
    ]
    scored.sort(key=lambda item: (-item["selected_model_score"], item["source_id"]))
    for index, row in enumerate(scored, start=1):
        row["rank_descending"] = index
    return scored


def build_freeze(
    *,
    contract_path: Path,
    output_path: Path,
    review_note_path: Path,
    generated_at_utc: str,
) -> dict[str, Any]:
    root = repo_root()
    contract_path = contract_path if contract_path.is_absolute() else root / contract_path
    output_path = output_path if output_path.is_absolute() else root / output_path
    review_note_path = review_note_path if review_note_path.is_absolute() else root / review_note_path
    contract = load_yaml(contract_path)
    surface_path = validate_contract(contract, contract_path=contract_path, root=root)
    surface = load_yaml(surface_path)
    rows = validate_feature_surface(surface)
    evaluations = evaluate_models(contract, rows)
    selected = select_model(evaluations)
    score_rows = build_score_rows(rows)
    surface_rows_sha256 = stable_digest(score_rows)

    payload = {
        "artifact_kind": "frb_pre_t_repeater_propensity_model_surface",
        "surface_id": SURFACE_ID,
        "task_id": TASK_ID,
        "status": "frozen_model_surface",
        "generated_at_utc": generated_at_utc,
        "contract": {
            "path": rel_path(contract_path, root=root),
            "sha256": sha256_file(contract_path),
            "contract_id": CONTRACT_ID,
        },
        "input_surface": {
            "path": rel_path(surface_path, root=root),
            "sha256": sha256_file(surface_path),
            "feature_table_sha256": surface["feature_table_sha256"],
            "row_count": len(rows),
        },
        "feature_boundary": {
            "label_contact": False,
            "columns_read": list(READ_FIELDS),
            "forbidden_features_excluded": contract["feature_boundary"]["forbidden_features"],
        },
        "selection": {
            "outcome": "FREEZE_EXECUTED",
            "selected_model_id": selected["model_id"],
            "selected_formula": selected["formula"],
            "rule": contract["selection_rule"]["type"],
            "label_performance_metric": "none",
            "selected_model_nonzero_rows": selected["nonzero_score_rows"],
            "selected_model_unique_scores": selected["unique_score_values"],
            "constant_null_nonzero_rows": 0,
            "constant_null_unique_scores": 1,
            "model_evaluations": evaluations,
        },
        "frozen_scoring_rule": {
            "score_pre_t": SCORING_RULE,
            "count_to_hours": COUNT_TO_HOURS,
            "modification_allowed": False,
        },
        "per_source_score_count": len(score_rows),
        "per_source_scores_sha256": surface_rows_sha256,
        "per_source_scores": score_rows,
        "replay_command": contract["freeze_outputs"]["replay_command"],
        "output_routing": {
            "prediction_registry_entry": "none",
            "result_artifact": "none",
            "claim_impact": "none",
            "knowledge_impact": "none",
            "next_stage": "TASK-0965 sealed registration pack after TASK-0964 merge",
        },
        "limitations": [
            "Exposure-only propensity surface; no repeat-label performance is measured.",
            "No reveal label, Catalog 2 full-window exposure, morphology, or post-T association field is read.",
            "This is not a PRED registration and not a success verdict.",
        ],
        "verdict": "FRB_PRE_T_EXPOSURE_MODEL_SURFACE_FROZEN",
    }
    write_yaml(output_path, payload)
    write_text(review_note_path, render_review_note(payload, output_path=output_path))
    return payload


def render_review_note(payload: dict[str, Any], *, output_path: Path) -> str:
    selected = payload["selection"]
    return "\n".join(
        [
            "# FRB Pre-T Model Selection Freeze",
            "",
            "- Task: `TASK-0964`",
            "- Domain: radio transients astrophysics",
            "- Verdict: `FRB_PRE_T_EXPOSURE_MODEL_SURFACE_FROZEN`",
            f"- Frozen surface: `{rel_path(output_path, root=repo_root())}`",
            "",
            "## Scope",
            "",
            "This freezes the exposure-only pre-T repeater-propensity surface that the",
            "registration pack task can consume. It does not read repeat labels, score",
            "repeat outcomes, register a PRED entry, create a RESULT artifact, or promote",
            "a claim.",
            "",
            "## Frozen Selection",
            "",
            f"- Selected model: `{selected['selected_model_id']}`.",
            f"- Formula: `{selected['selected_formula']}`.",
            f"- Nonzero scored rows: `{selected['selected_model_nonzero_rows']}` of "
            f"`{payload['per_source_score_count']}`.",
            f"- Unique score values: `{selected['selected_model_unique_scores']}`.",
            f"- Per-source score digest: `{payload['per_source_scores_sha256']}`.",
            "",
            "The selected model beats the constant-null comparator on the predeclared",
            "label-free coverage and rank-resolution checks. No label-performance metric",
            "is computed.",
            "",
            "## Leakage Boundary",
            "",
            "- Columns read: `source_id`, `E_upper_hours`, `E_lower_hours`, `score_pre_t`.",
            "- Label contact: `false`.",
            "- Forbidden fields remain excluded: repeater labels, Catalog 2 full-window",
            "  exposure, morphology, and post-T source associations.",
            "- Scoring rule is the gate formula verbatim:",
            "  `score_pre_t = log1p(E_upper_hours + E_lower_hours)`.",
            "",
            "## Output Routing",
            "",
            "- Canonical destination: frozen model surface under `data/radio_transients/`",
            "  plus this review note.",
            "- Review tier: none.",
            "- Gate A / Gate B: not applicable.",
            "- Prediction impact: staged surface only; no PRED registered.",
            "- Claim impact: none.",
            "- Knowledge impact: none.",
            "- Next stage: `TASK-0965` prepares the maintainer-approved sealed prediction",
            "  registration pack after `TASK-0964` is merged.",
            "",
            "## Limitations",
            "",
            "- This is an exposure-only propensity ordering, not evidence that the model",
            "  predicts repeaters.",
            "- Registration and external anchoring are out of scope for this task.",
            "- Reveal scoring must use the later checksum-pinned label surface and the",
            "  frozen scoring rule without modification.",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contract",
        default="data/radio_transients/frb_pre_t_model_selection_contract.yaml",
    )
    parser.add_argument(
        "--output",
        default="data/radio_transients/frb_pre_t_repeater_propensity_model_surface.yaml",
    )
    parser.add_argument(
        "--review-note",
        default="docs/reviews/frb-pre-t-model-selection-freeze.md",
    )
    parser.add_argument("--generated-at-utc", default="2026-07-09T00:00:00Z")
    args = parser.parse_args(argv)
    payload = build_freeze(
        contract_path=Path(args.contract),
        output_path=Path(args.output),
        review_note_path=Path(args.review_note),
        generated_at_utc=args.generated_at_utc,
    )
    selected = payload["selection"]["selected_model_id"]
    print(f"verdict={payload['verdict']}")
    print(f"selected_model_id={selected}")
    print(f"per_source_score_count={payload['per_source_score_count']}")
    print(f"per_source_scores_sha256={payload['per_source_scores_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
