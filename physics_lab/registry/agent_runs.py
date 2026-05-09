"""Autonomous sandbox agent-run registry helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.research_proposals import (
    load_experiment_proposal,
    load_hypothesis_proposal,
)
from physics_lab.registry.validation import validate_document

CANONICAL_MEMORY_ROOTS = {
    "claims",
    "experiments",
    "hypotheses",
    "knowledge",
    "results",
}


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in agent run file: {path}")
    return data


def _resolve_repo_path(root: Path, path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else root / path


def _assert_sandbox_relative_path(path_value: str, *, source: str | Path) -> None:
    path = Path(path_value)
    if path.is_absolute():
        raise ValueError(f"{source} must use repository-relative sandbox paths, not {path_value}")
    if ".." in path.parts:
        raise ValueError(f"{source} must not use parent-directory sandbox paths: {path_value}")
    if path.parts and path.parts[0] in CANONICAL_MEMORY_ROOTS:
        raise ValueError(f"{source} points sandbox output at canonical memory path: {path_value}")


def validate_agent_run_payload(
    payload: dict[str, Any],
    *,
    source: str | Path,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Validate a sandbox agent-run manifest and its local layout."""
    validate_document(payload, kind="agent_run", source=source)
    if payload["sandbox_only"] is not True:
        raise ValueError(f"{source} must keep sandbox_only: true")
    boundary = payload["promotion_boundary"]
    if boundary.get("writes_canonical_result") is not False:
        raise ValueError(f"{source} must not write canonical results")
    if boundary.get("claim_promotion_allowed") is not False:
        raise ValueError(f"{source} must not allow claim promotion")

    root_path = Path(root).resolve() if root is not None else Path(source).resolve().parent
    source_path = Path(source)
    if root is not None:
        try:
            relative_source = source_path.resolve().relative_to(root_path)
        except ValueError as exc:
            raise ValueError(f"{source} must live under repository root {root_path}") from exc
        if not relative_source.parts or relative_source.parts[0] != "agent_runs":
            raise ValueError(f"{source} must live under agent_runs/")

    proposal_paths = payload["proposal_paths"]
    hypothesis_path = str(proposal_paths["hypothesis"])
    experiment_path = str(proposal_paths["experiment"])
    _assert_sandbox_relative_path(hypothesis_path, source=source)
    _assert_sandbox_relative_path(experiment_path, source=source)
    if root is not None:
        load_hypothesis_proposal(_resolve_repo_path(root_path, hypothesis_path), root=root_path)
        load_experiment_proposal(_resolve_repo_path(root_path, experiment_path), root=root_path)

    artifacts = payload["artifacts"]
    required_artifacts = ("metrics", "report", "limitations", "preflight", "review_summary")
    for artifact_name in required_artifacts:
        artifact_path = str(artifacts[artifact_name])
        _assert_sandbox_relative_path(artifact_path, source=source)
        if not artifact_path.startswith("agent_runs/"):
            raise ValueError(
                f"{source} artifact {artifact_name} must live under agent_runs/: {artifact_path}"
            )
        if root is not None and not _resolve_repo_path(root_path, artifact_path).exists():
            raise ValueError(f"{source} references missing agent-run artifact: {artifact_path}")

    return payload


def load_agent_run(
    path: str | Path,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Load and validate an autonomous sandbox agent-run manifest."""
    payload = _load_yaml_mapping(path)
    return validate_agent_run_payload(payload, source=path, root=root)
