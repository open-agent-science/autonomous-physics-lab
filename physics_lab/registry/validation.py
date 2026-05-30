"""Shared schema validation utilities for public scientific memory."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


SCHEMA_DIRECTORY = Path(__file__).resolve().parent.parent / "schemas"
SCHEMA_FILE_BY_KIND = {
    "claim": "claim.schema.json",
    "example_config": "example_config.schema.json",
    "hypothesis": "hypothesis.schema.json",
    "experiment": "experiment.schema.json",
    "knowledge": "knowledge.schema.json",
    "task": "task.schema.json",
    "task_proposal": "task_proposal.schema.json",
    "agent": "agent.schema.json",
    "campaign_catalog": "campaign_catalog.schema.json",
    "result": "result.schema.json",
    "prediction": "prediction.schema.json",
    "review_metadata": "review_metadata.schema.json",
    "result_candidate_review": "result_candidate_review.schema.json",
    "constant_verification": "constant_verification.schema.json",
    "hypothesis_register_entry": "hypothesis_register_entry.schema.json",
    "approximation_probe": "approximation_probe.schema.json",
    "hypothesis_proposal": "hypothesis_proposal.schema.json",
    "experiment_proposal": "experiment_proposal.schema.json",
    "agent_run": "agent_run.schema.json",
    "microtask_run": "microtask_run.schema.json",
    "nuclear_mass_dataset": "nuclear_mass_dataset.schema.json",
    "nuclear_mass_prediction": "nuclear_mass_prediction.schema.json",
    "post_ame2020_holdout": "post_ame2020_holdout.schema.json",
    "post_ame2020_sources": "post_ame2020_sources.schema.json",
    "quantum_dot_size_effect": "quantum_dot_size_effect.schema.json",
    "exoplanet_mass_radius": "exoplanet_mass_radius.schema.json",
    "source_manifest_minimum": "source_manifest_minimum.schema.json",
}
REVIEW_TIERS_REQUIRING_AGENT_EVALUATION = frozenset(
    {"AGENT_PUBLISHED", "AGENT_VALIDATED"}
)
KIND_BY_DIRECTORY = {
    "claims": "claim",
    "hypotheses": "hypothesis",
    "constants_verification": "constant_verification",
    "hypothesis_register": "hypothesis_register_entry",
    "experiments": "experiment",
    "knowledge": "knowledge",
    "proposals": "task_proposal",
    "tasks": "task",
    "agents": "agent",
    "campaigns": "campaign_catalog",
    "results": "result",
    "examples": "example_config",
    "approximation_probes": "approximation_probe",
    "hypothesis_proposals": "hypothesis_proposal",
    "experiment_proposals": "experiment_proposal",
    "agent_runs": "agent_run",
    "microtask_runs": "microtask_run",
    "nuclear_masses": "nuclear_mass_dataset",
    "prediction_registry": "nuclear_mass_prediction",
    "quantum_dots": "quantum_dot_size_effect",
}


def schema_path(kind: str) -> Path:
    """Return the filesystem path for a schema kind."""
    try:
        schema_filename = SCHEMA_FILE_BY_KIND[kind]
    except KeyError as exc:
        raise ValueError(f"Unknown schema kind: {kind}") from exc
    return SCHEMA_DIRECTORY / schema_filename


@lru_cache(maxsize=None)
def load_schema(kind: str) -> dict[str, Any]:
    """Load a JSON schema from disk."""
    with schema_path(kind).open("r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=None)
def get_validator(kind: str) -> Draft202012Validator:
    """Build a validator for a schema kind."""
    return Draft202012Validator(load_schema(kind))


def _error_path(error: ValidationError) -> str:
    return ".".join(str(part) for part in error.absolute_path) or "<root>"


def _describe_error(error: ValidationError) -> str:
    """Render a schema error, drilling into oneOf/anyOf branches when present.

    A bare ``oneOf``/``anyOf`` failure reports only "is not valid under any of
    the given schemas", which hides the actual missing or invalid field. When
    the error carries sub-errors (``error.context``), group them by branch and
    surface the closest branch (the one with the fewest sub-errors) so authors
    can see, for example, that ``planning_context`` is the required property
    that is missing.
    """
    description = f"{_error_path(error)}: {error.message}"
    if not error.context:
        return description
    by_branch: dict[Any, list[ValidationError]] = {}
    for sub in error.context:
        branch_key = sub.schema_path[0] if sub.schema_path else None
        by_branch.setdefault(branch_key, []).append(sub)
    if not by_branch:
        return description
    closest_branch = min(by_branch.values(), key=len)
    parts = [
        f"{('.'.join(str(part) for part in sub.absolute_path) or _error_path(error))}: {sub.message}"
        for sub in closest_branch
    ]
    return f"{description} (closest match — {'; '.join(parts)})"


def validate_document(data: dict[str, Any], kind: str, source: str | Path) -> dict[str, Any]:
    """Validate a structured document and return it unchanged on success."""
    validator = get_validator(kind)
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.absolute_path))
    if errors:
        details = "; ".join(_describe_error(error) for error in errors)
        raise ValueError(f"{source} failed {kind} schema validation: {details}")
    validate_review_tier_metadata(data, kind, source)
    return data


def validate_review_tier_metadata(
    data: dict[str, Any], kind: str, source: str | Path
) -> None:
    """Enforce review-tier audit metadata only when a tier is explicitly set."""
    review_tier = data.get("review_tier")
    if review_tier not in REVIEW_TIERS_REQUIRING_AGENT_EVALUATION:
        return

    evaluation = data.get("agent_proposal_evaluation")
    if not isinstance(evaluation, dict):
        raise ValueError(
            f"{source} sets review_tier: {review_tier} but is missing "
            "agent_proposal_evaluation"
        )

    proposed_tier = evaluation.get("review_tier_proposed")
    if proposed_tier != review_tier:
        raise ValueError(
            f"{source} sets review_tier: {review_tier} but "
            f"agent_proposal_evaluation.review_tier_proposed is {proposed_tier!r}"
        )

    gates_checked = evaluation.get("gates_checked")
    if not isinstance(gates_checked, dict) or not gates_checked:
        raise ValueError(
            f"{source} sets review_tier: {review_tier} but has no populated "
            "agent_proposal_evaluation.gates_checked"
        )

    evidence_summary = evaluation.get("evidence_summary")
    if not isinstance(evidence_summary, str) or not evidence_summary.strip():
        raise ValueError(
            f"{source} sets review_tier: {review_tier} but has no "
            "agent_proposal_evaluation.evidence_summary"
        )


FILENAME_KIND_MAP: dict[str, str] = {
    "review_metadata.yaml": "review_metadata",
    "result_candidate_review.yaml": "result_candidate_review",
    "agent_run.yaml": "agent_run",
    "MICROTASK-RUN-TEMPLATE.yaml": "microtask_run",
    "PRED-TEMPLATE.yaml": "nuclear_mass_prediction",
    "post_ame2020_holdout.yaml": "post_ame2020_holdout",
    "post_ame2020_sources.yaml": "post_ame2020_sources",
}


def infer_kind_from_path(path: str | Path) -> str:
    """Infer schema kind from a repository-relative path.

    Filename-based mappings take precedence over directory-based ones so that
    files such as ``review_metadata.yaml`` (which live under a ``results/``
    directory) are not misclassified as ``result`` artifacts.
    """
    resolved = Path(path)
    if resolved.name in FILENAME_KIND_MAP:
        return FILENAME_KIND_MAP[resolved.name]
    if "prediction_registry" in resolved.parts:
        return "nuclear_mass_prediction"
    for part in reversed(resolved.parts):
        if part in KIND_BY_DIRECTORY:
            return KIND_BY_DIRECTORY[part]
    raise ValueError(f"Unable to infer schema kind from path: {path}")
