"""Task registry helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml

from physics_lab.registry.validation import validate_document


TaskInputMode = Literal["science_execution", "planning_only", "workflow"]


def load_task(path: str | Path) -> dict[str, Any]:
    """Load and validate a task file."""
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in task file: {path}")
    return validate_document(data, kind="task", source=path)


def load_task_minimal(path: str | Path) -> dict[str, Any]:
    """Parse an archived task file without full schema validation.

    Archived (historical, terminal) task files are frozen records. Re-validating
    them against an evolving task schema would force edits to history, so the
    archive is held to a minimal contract: the file must parse to a mapping with
    a non-empty string ``id``. All other fields are read as-is. Active tasks
    still go through the full :func:`load_task` schema validation.
    """
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    task_id = data.get("id") if isinstance(data, dict) else None
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError(
            f"Expected mapping with a non-empty string 'id' in archived task file: {path}"
        )
    return data


def task_input_mode(payload: dict[str, Any]) -> TaskInputMode:
    """Return the semantic input mode for a validated task payload."""
    input_payload = payload["input"]
    return str(input_payload.get("mode", "science_execution"))  # type: ignore[return-value]
