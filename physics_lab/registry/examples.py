"""Example configuration helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.validation import validate_document


def load_example_config(path: str | Path) -> dict[str, Any]:
    """Load and validate an example experiment config."""
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in example config file: {path}")
    return validate_document(data, kind="example_config", source=path)
