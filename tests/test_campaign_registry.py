"""Tests for the generated campaign portfolio registry."""

from __future__ import annotations

from pathlib import Path

import pytest

from physics_lab.registry.campaigns import load_campaign_catalog
from physics_lab.registry.repository import validate_repository
from physics_lab.registry.validation import infer_kind_from_path
from scripts.generate_campaign_catalog import build_catalog, render_catalog


REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = REPO_ROOT / "campaigns" / "catalog.yaml"


def _minimal_catalog(campaign_id: str = "example-campaign") -> str:
    return f"""
registry_version: 1
updated: "2026-05-29"
generated_by: scripts/generate_campaign_catalog.py
source_roots:
  - campaign_profiles/
purpose: "Lightweight generated campaign registry for test coverage."
relationship_to_missions: "missions/current.yaml remains the live recommendation surface; this catalog is only a compact portfolio view."
campaigns:
  - id: {campaign_id}
    title: "Example Campaign"
    status: scaffold
    domain: example_domain
    current_stage: "scaffold only"
    agent_capacity:
      recommended_parallel_agents: 1
      coordination_notes: "Use one test agent."
    best_next_actions:
      - task_id: null
        label: "Define source surface"
    required_gates:
      - "Source gate"
    allowed_work:
      - "Planning"
    forbidden_work:
      - "Unsupported claims"
    current_results: []
    open_questions:
      - "What source is usable?"
    curator_review:
      status: current
      last_reviewed: "2026-05-29"
      source: "test"
      notes: "Synthetic test catalog."
"""


def test_campaign_catalog_loads_current_generated_file() -> None:
    catalog = load_campaign_catalog(CATALOG_PATH)
    ids = {campaign["id"] for campaign in catalog["campaigns"]}

    assert "nuclear-mass-surface" in ids
    assert "exoplanet-mass-radius" in ids
    assert "atomic-clock-residuals" in ids
    assert catalog["generated_by"] == "scripts/generate_campaign_catalog.py"


def test_campaign_catalog_is_synced_with_profiles() -> None:
    expected = render_catalog(build_catalog(REPO_ROOT))
    assert CATALOG_PATH.read_text(encoding="utf-8") == expected


def test_campaign_catalog_rejects_duplicate_ids(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.yaml"
    catalog_text = _minimal_catalog("duplicate-campaign")
    duplicate_entry = catalog_text.split("campaigns:\n", 1)[1]
    catalog_path.write_text(
        f"{catalog_text}{duplicate_entry}",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate campaign id"):
        load_campaign_catalog(catalog_path)


def test_campaign_catalog_rejects_missing_required_fields(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.yaml"
    catalog_path.write_text(
        _minimal_catalog().replace("    forbidden_work:\n      - \"Unsupported claims\"\n", ""),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="required property"):
        load_campaign_catalog(catalog_path)


def test_validate_repository_counts_campaign_catalog(tmp_path: Path) -> None:
    campaign_dir = tmp_path / "campaigns"
    campaign_dir.mkdir()
    (campaign_dir / "catalog.yaml").write_text(_minimal_catalog(), encoding="utf-8")

    summary = validate_repository(tmp_path)

    assert summary.counts["campaigns"] == 1


def test_infer_kind_from_campaign_catalog_path() -> None:
    assert infer_kind_from_path("campaigns/catalog.yaml") == "campaign_catalog"
