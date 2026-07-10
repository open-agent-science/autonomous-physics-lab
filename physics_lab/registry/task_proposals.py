"""Task proposal registry helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from physics_lab.registry.validation import validate_document
from physics_lab.registry.yaml_io import load_yaml_mapping


def load_task_proposal(path: str | Path) -> dict[str, Any]:
    """Load and validate a task proposal file."""
    data = load_yaml_mapping(path, expected="task proposal file")
    return validate_document(data, kind="task_proposal", source=path)
