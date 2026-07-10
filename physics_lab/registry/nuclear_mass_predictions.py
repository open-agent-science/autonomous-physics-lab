"""Prediction-registry helpers for prospective nuclear-mass forecasts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from physics_lab.registry.validation import validate_document
from physics_lab.registry.yaml_io import load_yaml_mapping


def load_nuclear_mass_prediction(path: str | Path) -> dict[str, Any]:
    """Load and validate a nuclear-mass prediction registry entry."""
    data = load_yaml_mapping(path, expected="nuclear mass prediction file")
    return validate_document(data, kind="nuclear_mass_prediction", source=path)
