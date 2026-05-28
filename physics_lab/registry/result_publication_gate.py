"""Gate A checks for agent-published RESULT and PRED artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.review_checks import overclaim_hits
from physics_lab.registry.validation import validate_document


RESULT_GATE_KEYS = (
    "deterministic_run",
    "verification_block_populated",
    "input_hashes_recorded",
    "limitations_listed",
    "engine_version_and_commit_pinned",
    "schema_validation_passes",
    "no_protected_artifact_rewrite",
    "no_forbidden_overclaim_wording",
    "dataset_provenance_valid",
)
PREDICTION_GATE_KEYS = (
    "no_peek_state",
    "frozen_model_reference",
    "named_target_set",
    "reveal_conditions_explicit",
    "non_claim_ceiling",
    "live_external_fetch_disabled",
    "schema_validation_passes",
    "no_forbidden_overclaim_wording",
)
PLACEHOLDER_MARKERS = ("REPLACE_WITH", "replace-with", "replace/with", "PLACEHOLDER")


@dataclass(frozen=True)
class GateIssue:
    """A single Gate A issue."""

    code: str
    message: str
    severity: str = "error"


@dataclass(frozen=True)
class GateReport:
    """Gate A result for one artifact."""

    artifact_path: str
    artifact_kind: str
    review_tier: str | None
    issues: tuple[GateIssue, ...]

    @property
    def ok(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)


def check_artifact(path: str | Path, *, root: str | Path = ".") -> GateReport:
    """Check a YAML artifact file against the Gate A publication rules."""
    artifact_path = Path(path)
    with artifact_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        return GateReport(
            artifact_path=str(artifact_path),
            artifact_kind="unknown",
            review_tier=None,
            issues=(GateIssue("invalid-yaml", "Artifact must be a YAML mapping."),),
        )
    return check_payload(payload, artifact_path=str(artifact_path), root=root)


def check_payload(
    payload: dict[str, Any],
    *,
    artifact_path: str = "<memory>",
    root: str | Path = ".",
) -> GateReport:
    """Check an in-memory RESULT or PRED payload against Gate A."""
    kind = _infer_artifact_kind(payload)
    issues: list[GateIssue] = []
    review_tier = payload.get("review_tier")

    if kind == "result":
        _extend_schema_errors(issues, payload, kind="result", artifact_path=artifact_path)
        _check_common_agent_published_fields(
            issues,
            payload,
            gate_keys=RESULT_GATE_KEYS,
            artifact_label="RESULT",
        )
        _check_result_gate(issues, payload, root=Path(root))
    elif kind == "prediction":
        _extend_schema_errors(issues, payload, kind="prediction", artifact_path=artifact_path)
        _check_common_agent_published_fields(
            issues,
            payload,
            gate_keys=PREDICTION_GATE_KEYS,
            artifact_label="PRED",
        )
        _check_prediction_gate(issues, payload)
    else:
        issues.append(
            GateIssue(
                "unknown-artifact-kind",
                "Gate A checker expects a RESULT-* or PRED-* artifact.",
            )
        )

    _check_overclaim_wording(issues, payload)
    return GateReport(
        artifact_path=artifact_path,
        artifact_kind=kind,
        review_tier=review_tier if isinstance(review_tier, str) else None,
        issues=tuple(issues),
    )


def _infer_artifact_kind(payload: dict[str, Any]) -> str:
    if isinstance(payload.get("result_id"), str):
        return "result"
    if isinstance(payload.get("prediction_id"), str):
        return "prediction"
    return "unknown"


def _extend_schema_errors(
    issues: list[GateIssue],
    payload: dict[str, Any],
    *,
    kind: str,
    artifact_path: str,
) -> None:
    try:
        validate_document(payload, kind, artifact_path)
    except ValueError as exc:
        issues.append(GateIssue("schema-validation", str(exc)))


def _check_common_agent_published_fields(
    issues: list[GateIssue],
    payload: dict[str, Any],
    *,
    gate_keys: tuple[str, ...],
    artifact_label: str,
) -> None:
    review_tier = payload.get("review_tier")
    if review_tier != "AGENT_PUBLISHED":
        issues.append(
            GateIssue(
                "review-tier",
                f"{artifact_label} Gate A artifacts must set review_tier: AGENT_PUBLISHED.",
            )
        )

    evaluation = payload.get("agent_proposal_evaluation")
    if not isinstance(evaluation, dict):
        issues.append(
            GateIssue(
                "agent-evaluation",
                "Missing agent_proposal_evaluation audit block.",
            )
        )
        return

    gates = evaluation.get("gates_checked")
    if not isinstance(gates, dict):
        issues.append(
            GateIssue("gate-list", "agent_proposal_evaluation.gates_checked is missing.")
        )
        return

    for key in gate_keys:
        if gates.get(key) is not True:
            issues.append(
                GateIssue(
                    f"gate-{key}",
                    f"Gate A key {key!r} must be present and true.",
                )
            )

    summary = evaluation.get("evidence_summary")
    if not isinstance(summary, str) or _is_empty_or_placeholder(summary):
        issues.append(
            GateIssue(
                "evidence-summary",
                "agent_proposal_evaluation.evidence_summary must be non-placeholder text.",
            )
        )


def _check_result_gate(
    issues: list[GateIssue],
    payload: dict[str, Any],
    *,
    root: Path,
) -> None:
    for field in ("command", "code_reference", "engine_version", "git_commit"):
        if _is_empty_or_placeholder(payload.get(field)):
            issues.append(GateIssue(f"result-{field}", f"RESULT field {field!r} is empty."))

    if not isinstance(payload.get("limitations"), list) or not payload["limitations"]:
        issues.append(GateIssue("result-limitations", "RESULT limitations must be non-empty."))

    if _is_empty_or_placeholder(payload.get("best_verdict")):
        issues.append(GateIssue("result-verdict", "RESULT best_verdict must be populated."))

    verification = payload.get("verification")
    checks = verification.get("checks") if isinstance(verification, dict) else None
    if not isinstance(checks, list) or not checks:
        issues.append(
            GateIssue(
                "result-verification",
                "RESULT verification.checks must contain at least one deterministic check.",
            )
        )
    else:
        for index, check in enumerate(checks, start=1):
            if not isinstance(check, dict):
                issues.append(
                    GateIssue(
                        "result-verification-check",
                        f"RESULT verification check #{index} must be a mapping.",
                    )
                )
                continue
            for field in ("name", "status", "details"):
                if _is_empty_or_placeholder(check.get(field)):
                    issues.append(
                        GateIssue(
                            "result-verification-check",
                            f"RESULT verification check #{index} has empty {field!r}.",
                        )
                    )

    hashes = payload.get("input_file_hashes")
    if not isinstance(hashes, dict):
        issues.append(
            GateIssue("result-input-hashes", "RESULT input_file_hashes must be populated.")
        )
    else:
        for label, file_hash in hashes.items():
            if not isinstance(file_hash, dict):
                issues.append(
                    GateIssue(
                        "result-input-hashes",
                        f"Input hash {label!r} must be a mapping.",
                    )
                )
                continue
            if _is_empty_or_placeholder(file_hash.get("path")):
                issues.append(
                    GateIssue(
                        "result-input-hashes",
                        f"Input hash {label!r} must include a source path.",
                    )
                )
            sha256 = file_hash.get("sha256")
            if not isinstance(sha256, str) or len(sha256) != 64 or not _is_hex(sha256):
                issues.append(
                    GateIssue(
                        "result-input-hashes",
                        f"Input hash {label!r} must include a 64-character sha256.",
                    )
                )

    protected_ids = _protected_result_ids(root)
    result_id = payload.get("result_id")
    if isinstance(result_id, str) and result_id in protected_ids:
        issues.append(
            GateIssue(
                "protected-result",
                f"{result_id} is already pinned in results/golden-results.yaml.",
            )
        )


def _check_prediction_gate(issues: list[GateIssue], payload: dict[str, Any]) -> None:
    source_state = payload.get("source_state")
    if not isinstance(source_state, dict):
        issues.append(GateIssue("pred-source-state", "PRED source_state is missing."))
        return

    if _is_empty_or_placeholder(source_state.get("git_commit")):
        issues.append(GateIssue("pred-git-commit", "PRED source_state.git_commit is empty."))

    if source_state.get("live_external_fetch_allowed") is not False:
        issues.append(
            GateIssue(
                "pred-live-fetch",
                "PRED source_state.live_external_fetch_allowed must be false.",
            )
        )

    model_reference = source_state.get("model_reference")
    if not isinstance(model_reference, dict):
        issues.append(
            GateIssue("pred-model-reference", "PRED source_state.model_reference is missing.")
        )
    else:
        for field in ("model_id", "source_path", "frozen_parameters_note"):
            if _is_empty_or_placeholder(model_reference.get(field)):
                issues.append(
                    GateIssue(
                        "pred-model-reference",
                        f"PRED model_reference.{field} must be populated.",
                    )
                )

    if _is_empty_or_placeholder(source_state.get("source_data_state_note")):
        issues.append(
            GateIssue(
                "pred-source-note",
                "PRED source_data_state_note must explain the no-peek state.",
            )
        )

    target_set = payload.get("target_set")
    if not isinstance(target_set, dict):
        issues.append(GateIssue("pred-target-set", "PRED target_set is missing."))
    else:
        for field in ("label", "quantity", "unit"):
            if _is_empty_or_placeholder(target_set.get(field)):
                issues.append(
                    GateIssue("pred-target-set", f"PRED target_set.{field} is empty.")
                )

    reveal_conditions = payload.get("reveal_conditions")
    if not isinstance(reveal_conditions, dict):
        issues.append(
            GateIssue("pred-reveal-conditions", "PRED reveal_conditions are missing.")
        )
    else:
        for field in ("comparison_source_class", "reveal_controlled_by", "no_peek_rule"):
            if _is_empty_or_placeholder(reveal_conditions.get(field)):
                issues.append(
                    GateIssue(
                        "pred-reveal-conditions",
                        f"PRED reveal_conditions.{field} is empty.",
                    )
                )

    claim_ceiling = payload.get("claim_ceiling")
    if _is_empty_or_placeholder(claim_ceiling) or "no claim" not in str(claim_ceiling).lower():
        issues.append(
            GateIssue(
                "pred-claim-ceiling",
                "PRED claim_ceiling must explicitly state the no-claim boundary.",
            )
        )

    if not isinstance(payload.get("limitations"), list) or not payload["limitations"]:
        issues.append(GateIssue("pred-limitations", "PRED limitations must be non-empty."))


def _check_overclaim_wording(issues: list[GateIssue], payload: dict[str, Any]) -> None:
    lines = tuple(_string_values(payload))
    hits = overclaim_hits(lines)
    if hits:
        issues.append(
            GateIssue(
                "overclaim-wording",
                "Forbidden overclaim wording in positive context: " + ", ".join(hits),
            )
        )


def _string_values(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, dict):
        lines: list[str] = []
        for item in value.values():
            lines.extend(_string_values(item))
        return tuple(lines)
    if isinstance(value, list):
        lines = []
        for item in value:
            lines.extend(_string_values(item))
        return tuple(lines)
    return ()


def _protected_result_ids(root: Path) -> frozenset[str]:
    path = root / "results" / "golden-results.yaml"
    if not path.exists():
        return frozenset()
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    rows = payload.get("golden_results", [])
    if not isinstance(rows, list):
        return frozenset()
    return frozenset(
        str(row["result_id"])
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("result_id"), str)
    )


def _is_empty_or_placeholder(value: Any) -> bool:
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    stripped = value.strip()
    if not stripped:
        return True
    return any(marker in stripped for marker in PLACEHOLDER_MARKERS)


def _is_hex(value: str) -> bool:
    return all(character in "0123456789abcdefABCDEF" for character in value)
