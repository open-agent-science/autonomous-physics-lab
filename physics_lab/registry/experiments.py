"""Experiment registry helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.validation import validate_document


def load_experiment(path: str | Path) -> dict[str, Any]:
    """Load and validate an experiment file."""
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in experiment file: {path}")
    return validate_document(data, kind="experiment", source=path)
