"""Claim registry helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.validation import validate_document


def load_claim(path: str | Path) -> dict[str, Any]:
    """Load and validate a claim Markdown file with YAML front matter."""
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"Claim file is missing YAML front matter: {path}")

    try:
        _, front_matter, body = text.split("---\n", 2)
    except ValueError as exc:
        raise ValueError(f"Claim file has invalid front matter delimiters: {path}") from exc

    data = yaml.safe_load(front_matter)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in claim front matter: {path}")

    payload = {**data, "body": body.strip()}
    return validate_document(payload, kind="claim", source=path)
