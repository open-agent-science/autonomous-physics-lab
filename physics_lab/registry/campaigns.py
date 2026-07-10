"""Campaign portfolio registry helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from physics_lab.registry.validation import validate_document
from physics_lab.registry.yaml_io import load_yaml_mapping


CAMPAIGN_PORTFOLIO_INDEX_PATH = Path("campaign_profiles") / "_catalog.yaml"


def campaign_catalog_path(root: str | Path) -> Path:
    """Return the generated campaign portfolio index path under ``root``."""
    return Path(root) / CAMPAIGN_PORTFOLIO_INDEX_PATH


def load_campaign_catalog(path: str | Path) -> dict[str, Any]:
    """Load and validate the generated campaign portfolio index."""
    source = Path(path)
    data = load_yaml_mapping(source, expected="campaign catalog")
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
