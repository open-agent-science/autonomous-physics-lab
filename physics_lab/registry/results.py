"""Result registry helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import json

from physics_lab.registry.validation import validate_document


def validate_result_payload(payload: dict[str, Any], source: str | Path) -> dict[str, Any]:
    """Validate a result payload before writing it to disk."""
    return validate_document(payload, kind="result", source=source)


def load_result(path: str | Path) -> dict[str, Any]:
    """Load and validate a result artifact."""
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in result file: {path}")
    return validate_result_payload(data, source=path)
