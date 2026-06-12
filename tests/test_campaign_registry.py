"""Tests for the generated campaign portfolio registry."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from physics_lab.registry.campaigns import load_campaign_catalog
from physics_lab.registry.repository import validate_repository
from physics_lab.registry.validation import infer_kind_from_path


REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = REPO_ROOT / "campaign_profiles" / "_catalog.yaml"
GENERATOR_PATH = REPO_ROOT / "scripts" / "generate_campaign_catalog.py"

_GENERATOR_SPEC = importlib.util.spec_from_file_location(
    "generate_campaign_catalog",
    GENERATOR_PATH,
)
if _GENERATOR_SPEC is None or _GENERATOR_SPEC.loader is None:
    raise RuntimeError(f"Could not load campaign catalog generator: {GENERATOR_PATH}")
_GENERATOR = importlib.util.module_from_spec(_GENERATOR_SPEC)
_GENERATOR_SPEC.loader.exec_module(_GENERATOR)
build_catalog = _GENERATOR.build_catalog
render_catalog = _GENERATOR.render_catalog


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
    surface_type: source_pinned_benchmark
    lifecycle_stage: scaffold
    activity_status: planning
    curator:
      primary_pool: source_data_benchmark
      secondary_pools:
        - verifier_quality_floor
      review_cadence: monthly
      transfer_requires:
        - scientific_director_or_maintainer_pr
        - updated_campaign_profile
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
      review_interval: quarterly_planning
      next_review_due: "2026-09-01"
      review_reason: planning_scaffold
      source: "test"
      notes: "Synthetic test catalog."
"""


def _minimal_profile(campaign_id: str = "example-campaign") -> str:
    return f"""
id: {campaign_id}
title: "Example Campaign"
source_docs:
  - docs/campaigns/example-campaign.md
portfolio:
  status: scaffold
  domain: example_domain
  surface_type: source_pinned_benchmark
  lifecycle_stage: scaffold
  activity_status: planning
  curator:
    primary_pool: source_data_benchmark
    secondary_pools:
      - verifier_quality_floor
    review_cadence: monthly
    transfer_requires:
      - scientific_director_or_maintainer_pr
      - updated_campaign_profile
  current_stage: "scaffold only"
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
    review_interval: quarterly_planning
    next_review_due: "2026-09-01"
    review_reason: planning_scaffold
    source: "test"
    notes: "Synthetic test profile."
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


def test_campaign_catalog_generator_ignores_service_files(tmp_path: Path) -> None:
    profile_dir = tmp_path / "campaign_profiles"
    profile_dir.mkdir()
    (profile_dir / "_catalog.yaml").write_text(_minimal_catalog("generated-index"), encoding="utf-8")
    (profile_dir / "example-campaign.yaml").write_text(_minimal_profile(), encoding="utf-8")

    catalog = build_catalog(tmp_path)

    assert [campaign["id"] for campaign in catalog["campaigns"]] == ["example-campaign"]


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


def test_campaign_catalog_generator_rejects_invalid_curator_review_cadence(
    tmp_path: Path,
) -> None:
    profile_dir = tmp_path / "campaign_profiles"
    profile_dir.mkdir()
    profile_text = _minimal_profile().replace(
        "review_interval: quarterly_planning",
        "review_interval: weekly",
    )
    (profile_dir / "example-campaign.yaml").write_text(profile_text, encoding="utf-8")

    with pytest.raises(ValueError, match="invalid review_interval"):
        build_catalog(tmp_path)


def test_campaign_catalog_generator_rejects_invalid_curator_pool(
    tmp_path: Path,
) -> None:
    profile_dir = tmp_path / "campaign_profiles"
    profile_dir.mkdir()
    profile_text = _minimal_profile().replace(
        "primary_pool: source_data_benchmark",
        "primary_pool: group_b",
    )
    (profile_dir / "example-campaign.yaml").write_text(profile_text, encoding="utf-8")

    with pytest.raises(ValueError, match="invalid curator.primary_pool"):
        build_catalog(tmp_path)


def test_validate_repository_counts_campaign_catalog(tmp_path: Path) -> None:
    profile_dir = tmp_path / "campaign_profiles"
    profile_dir.mkdir()
    (profile_dir / "_catalog.yaml").write_text(_minimal_catalog(), encoding="utf-8")

    summary = validate_repository(tmp_path)

    assert summary.counts["campaigns"] == 1


def test_infer_kind_from_campaign_catalog_path() -> None:
    assert infer_kind_from_path("campaign_profiles/_catalog.yaml") == "campaign_catalog"
