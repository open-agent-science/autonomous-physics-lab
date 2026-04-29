"""Shared schema validation utilities for public scientific memory."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


SCHEMA_DIRECTORY = Path(__file__).resolve().parent.parent / "schemas"
SCHEMA_FILE_BY_KIND = {
    "hypothesis": "hypothesis.schema.json",
    "experiment": "experiment.schema.json",
    "task": "task.schema.json",
    "agent": "agent.schema.json",
    "result": "result.schema.json",
}
KIND_BY_DIRECTORY = {
    "hypotheses": "hypothesis",
    "experiments": "experiment",
    "tasks": "task",
    "agents": "agent",
    "results": "result",
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


def validate_document(data: dict[str, Any], kind: str, source: str | Path) -> dict[str, Any]:
    """Validate a structured document and return it unchanged on success."""
    validator = get_validator(kind)
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.absolute_path))
    if errors:
        details = "; ".join(
            f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
            for error in errors
        )
        raise ValueError(f"{source} failed {kind} schema validation: {details}")
    return data


def infer_kind_from_path(path: str | Path) -> str:
    """Infer schema kind from a repository-relative path."""
    resolved = Path(path)
    for part in reversed(resolved.parts):
        if part in KIND_BY_DIRECTORY:
            return KIND_BY_DIRECTORY[part]
    raise ValueError(f"Unable to infer schema kind from path: {path}")
