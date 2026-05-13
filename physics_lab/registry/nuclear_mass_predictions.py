"""Prediction-registry helpers for prospective nuclear-mass forecasts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.validation import validate_document


def load_nuclear_mass_prediction(path: str | Path) -> dict[str, Any]:
    """Load and validate a nuclear-mass prediction registry entry."""
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in nuclear mass prediction file: {path}")
    return validate_document(data, kind="nuclear_mass_prediction", source=path)
