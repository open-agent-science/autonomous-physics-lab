"""Tests for the task-to-campaign lane index (TASK-0460)."""

from __future__ import annotations

from pathlib import Path

import yaml

from physics_lab.registry.task_campaign_index import (
    artifact_surface,
    build_index,
    is_parallel_safe,
    map_lane,
    render_yaml,
)

CAMPAIGNS = ("nuclear-mass-surface", "quantum-size-effects", "exoplanet-mass-radius")


def test_map_lane_by_related_domain_exact_match() -> None:
    payload = {"input": {"related_domain": "nuclear_mass_surface"}, "type": "scientific_dataset"}
    lane, basis = map_lane(payload, CAMPAIGNS)
    assert lane == "nuclear-mass-surface"
    assert "related_domain" in basis


def test_map_lane_by_campaign_reference_in_related_objects() -> None:
    payload = {
        "input": {
            "related_domain": "something_unknown",
            "related_objects": ["docs/campaigns/quantum-size-effects.md"],
        },
        "type": "scientific_validation",
    }
    lane, basis = map_lane(payload, CAMPAIGNS)
    assert lane == "quantum-size-effects"
    assert "campaign reference" in basis


def test_map_lane_support_domain() -> None:
    payload = {"input": {"related_domain": "maintainer_review"}, "type": "maintainer_workflow"}
    lane, _basis = map_lane(payload, CAMPAIGNS)
    assert lane == "support"


def test_map_lane_support_type_fallback() -> None:
    payload = {"input": {"related_domain": "novel_thing"}, "type": "workflow_protocol"}
    lane, _basis = map_lane(payload, CAMPAIGNS)
    assert lane == "support"


def test_map_lane_unmapped_when_no_signal() -> None:
    payload = {"input": {"related_domain": "mystery_domain"}, "type": "scientific_dataset"}
    lane, basis = map_lane(payload, CAMPAIGNS)
    assert lane == "UNMAPPED"
    assert "no confident" in basis


def test_artifact_surface_extracts_top_level_paths_only() -> None:
    payload = {
        "accepted_outputs": [
            "docs/notes/foo.md",
            "results/EXP-0001/RUN-0001/result.yaml",
            "a prose accepted output with no path",
        ]
    }
    assert artifact_surface(payload) == ("docs/", "results/")


def test_is_parallel_safe_flags_shared_mutable_surface() -> None:
    assert is_parallel_safe(("docs/", "tasks/")) is True
    assert is_parallel_safe(("results/",)) is False
    assert is_parallel_safe(("missions/",)) is False


def test_build_index_smoke(tmp_path: Path) -> None:
    # Minimal synthetic repo: a catalog and two tasks (one mapped, one unmapped).
    (tmp_path / "campaigns").mkdir()
    (tmp_path / "campaigns" / "catalog.yaml").write_text(
        yaml.safe_dump({"campaigns": [{"id": "nuclear-mass-surface"}]}),
        encoding="utf-8",
    )
    (tmp_path / "tasks").mkdir()
    (tmp_path / "tasks" / "TASK-0001-mapped.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "TASK-0001",
                "title": "Mapped task",
                "type": "scientific_dataset",
                "status": "READY",
                "input": {"related_domain": "nuclear_mass_surface"},
                "accepted_outputs": ["docs/notes/n.md"],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "tasks" / "TASK-0002-unmapped.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "TASK-0002",
                "title": "Unmapped task",
                "type": "scientific_dataset",
                "status": "READY",
                "input": {"related_domain": "mystery"},
                "accepted_outputs": ["results/EXP-0001/RUN-0001/result.yaml"],
            }
        ),
        encoding="utf-8",
    )
    index = build_index(tmp_path)
    assert index["summary"]["active_tasks"] == 2
    assert index["summary"]["unmapped"] == 1
    assert index["summary"]["needs_curator_review"] == ["TASK-0002"]
    assert index["lanes"]["nuclear-mass-surface"] == ["TASK-0001"]
    by_id = {t["task_id"]: t for t in index["tasks"]}
    assert by_id["TASK-0001"]["parallel_safe"] is True
    assert by_id["TASK-0002"]["parallel_safe"] is False
    # render_yaml is deterministic and round-trips.
    assert yaml.safe_load(render_yaml(index))["summary"]["active_tasks"] == 2


def test_build_index_detects_output_path_conflict(tmp_path: Path) -> None:
    (tmp_path / "campaigns").mkdir()
    (tmp_path / "campaigns" / "catalog.yaml").write_text(
        yaml.safe_dump({"campaigns": []}), encoding="utf-8"
    )
    (tmp_path / "tasks").mkdir()
    for n in (1, 2):
        (tmp_path / "tasks" / f"TASK-000{n}-x.yaml").write_text(
            yaml.safe_dump(
                {
                    "id": f"TASK-000{n}",
                    "title": "x",
                    "type": "maintainer_workflow",
                    "status": "READY",
                    "input": {"related_domain": "maintainer_review"},
                    "accepted_outputs": ["docs/shared-target.md"],
                }
            ),
            encoding="utf-8",
        )
    index = build_index(tmp_path)
    assert index["path_conflicts"] == [
        {"path": "docs/shared-target.md", "tasks": ["TASK-0001", "TASK-0002"]}
    ]
