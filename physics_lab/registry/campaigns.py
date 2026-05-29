"""Campaign portfolio registry helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.validation import validate_document


def load_campaign_catalog(path: str | Path) -> dict[str, Any]:
    """Load and validate the lightweight campaign catalog."""
    source = Path(path)
    with source.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in campaign catalog: {path}")
    catalog = validate_document(data, kind="campaign_catalog", source=source)
    _validate_unique_campaign_ids(catalog, source)
    return catalog


def _validate_unique_campaign_ids(catalog: dict[str, Any], source: Path) -> None:
    """Fail fast when two catalog entries use the same campaign id."""
    seen: set[str] = set()
    for campaign in catalog.get("campaigns", []):
        campaign_id = str(campaign.get("id", ""))
        if campaign_id in seen:
            raise ValueError(f"{source} contains duplicate campaign id: {campaign_id}")
        seen.add(campaign_id)
