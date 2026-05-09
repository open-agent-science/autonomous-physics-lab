"""Autonomous research proposal registry helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.validation import validate_document

SANDBOX_VERDICTS = {
    "SANDBOX_PASS",
    "SANDBOX_FAIL",
    "FALSIFIED",
    "INCONCLUSIVE",
    "OVERFITTED",
    "REVIEW_NEEDED",
}
FORMULA_SEARCH_MARKERS = ("formula", "fit", "candidate", "relation", "search")
BASELINE_MARKERS = ("baseline", "null", "random", "exact reference", "negative comparison")


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in research proposal file: {path}")
    return data


def _as_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(_as_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_as_text(item) for item in value)
    return str(value)


def _require_nonempty_sequence(payload: dict[str, Any], path: str, source: str | Path) -> None:
    current: Any = payload
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise ValueError(f"{source} is missing required preflight field: {path}")
        current = current[part]
    if not isinstance(current, list) or not current:
        raise ValueError(f"{source} must provide at least one entry for {path}")


def _validate_campaign_profile_id(
    payload: dict[str, Any],
    *,
    source: str | Path,
    root: str | Path | None,
) -> None:
    if root is None:
        return
    profile_id = str(payload["campaign_profile_id"])
    profile_path = Path(root) / "campaign_profiles" / f"{profile_id}.yaml"
    if not profile_path.exists():
        raise ValueError(
            f"{source} references missing campaign profile: campaign_profiles/{profile_id}.yaml"
        )
    profile = _load_yaml_mapping(profile_path)
    if str(profile.get("id")) != profile_id:
        raise ValueError(f"{profile_path} id does not match filename campaign id: {profile_id}")
    if str(profile.get("autonomy_status")) == "EXCLUDED":
        raise ValueError(f"{source} references excluded campaign profile: {profile_id}")


def _validate_promotion_boundary(
    payload: dict[str, Any],
    *,
    source: str | Path,
) -> None:
    boundary = payload["promotion_boundary"]
    forbidden_true_fields = (
        "canonical_result_allowed",
        "claim_promotion_allowed",
        "writes_canonical_result",
        "writes_claim_update",
    )
    for field in forbidden_true_fields:
        if boundary.get(field) is True:
            raise ValueError(f"{source} may not enable promotion boundary field: {field}")


def _validate_overclaim_risk(payload: dict[str, Any], *, source: str | Path) -> None:
    risk = payload["overclaim_risk"]
    if risk.get("public_claim_allowed") is not False:
        raise ValueError(f"{source} must set overclaim_risk.public_claim_allowed to false")
    forbidden = risk.get("forbidden_language", [])
    mitigations = risk.get("mitigations", [])
    if not forbidden or not mitigations:
        raise ValueError(f"{source} must state forbidden overclaim language and mitigations")


def _validate_formula_search_baseline(payload: dict[str, Any], *, source: str | Path) -> None:
    kind = str(payload.get("proposal_kind", "")).lower()
    combined_text = _as_text(payload).lower()
    is_formula_search = kind == "formula_search" or any(
        marker in combined_text for marker in FORMULA_SEARCH_MARKERS
    )
    if not is_formula_search:
        return
    baseline_text = " ".join(
        str(value)
        for value in (
            payload.get("falsification_plan", {}).get("baseline_or_reference"),
            payload.get("validation", {}).get("baseline_or_reference"),
        )
        if value is not None
    ).lower()
    if not any(marker in baseline_text for marker in BASELINE_MARKERS):
        raise ValueError(
            f"{source} looks like a formula-search proposal but lacks a null, random, or exact-reference baseline plan"
        )


def validate_hypothesis_proposal_payload(
    payload: dict[str, Any],
    *,
    source: str | Path,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Run repository preflight checks for a hypothesis proposal."""
    validate_document(payload, kind="hypothesis_proposal", source=source)
    _validate_campaign_profile_id(payload, source=source, root=root)
    _validate_promotion_boundary(payload, source=source)
    _validate_overclaim_risk(payload, source=source)
    _require_nonempty_sequence(payload, "hypothesis.assumptions", source)
    _require_nonempty_sequence(payload, "hypothesis.variables", source)
    _require_nonempty_sequence(payload, "limitations", source)
    _validate_formula_search_baseline(payload, source=source)
    return payload


def validate_experiment_proposal_payload(
    payload: dict[str, Any],
    *,
    source: str | Path,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Run repository preflight checks for an experiment proposal."""
    validate_document(payload, kind="experiment_proposal", source=source)
    _validate_campaign_profile_id(payload, source=source, root=root)
    _validate_promotion_boundary(payload, source=source)
    _validate_overclaim_risk(payload, source=source)
    _require_nonempty_sequence(payload, "inputs.assumptions", source)
    _require_nonempty_sequence(payload, "limitations", source)
    _validate_formula_search_baseline(payload, source=source)
    return payload


def load_hypothesis_proposal(
    path: str | Path,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Load and preflight a hypothesis proposal file."""
    payload = _load_yaml_mapping(path)
    return validate_hypothesis_proposal_payload(payload, source=path, root=root)


def load_experiment_proposal(
    path: str | Path,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Load and preflight an experiment proposal file."""
    payload = _load_yaml_mapping(path)
    return validate_experiment_proposal_payload(payload, source=path, root=root)


def infer_research_proposal_kind(path: str | Path) -> str:
    """Infer the research proposal schema kind from its repository path."""
    parts = Path(path).parts
    if "hypothesis_proposals" in parts:
        return "hypothesis_proposal"
    if "experiment_proposals" in parts:
        return "experiment_proposal"
    raise ValueError(f"Unable to infer research proposal kind from path: {path}")
