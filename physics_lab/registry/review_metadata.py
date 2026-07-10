"""Review metadata registry helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from physics_lab.registry.validation import validate_document
from physics_lab.registry.yaml_io import load_yaml_mapping


def load_review_metadata(path: str | Path) -> dict[str, Any]:
    """Load and validate a review_metadata.yaml artifact against its JSON schema."""
    path = Path(path)
    data = load_yaml_mapping(path, expected="review_metadata file")
    return validate_document(data, kind="review_metadata", source=path)
