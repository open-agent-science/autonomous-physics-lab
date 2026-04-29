"""Agent registry helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.validation import validate_document


def load_agent(path: str | Path) -> dict[str, Any]:
    """Load and validate an agent manifest file."""
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in agent file: {path}")
    return validate_document(data, kind="agent", source=path)
