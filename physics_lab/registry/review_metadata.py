"""Review metadata registry helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.validation import validate_document


def load_review_metadata(path: str | Path) -> dict[str, Any]:
    """Load and validate a review_metadata.yaml artifact against its JSON schema."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in review_metadata file: {path}")
    return validate_document(data, kind="review_metadata", source=path)
