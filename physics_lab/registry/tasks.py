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


def task_input_mode(payload: dict[str, Any]) -> TaskInputMode:
    """Return the semantic input mode for a validated task payload."""
    input_payload = payload["input"]
    return str(input_payload.get("mode", "science_execution"))  # type: ignore[return-value]
