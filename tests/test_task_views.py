from __future__ import annotations

from pathlib import Path

from physics_lab.registry.task_views import render_task_views, sync_task_views


def _write_task(
    root: Path,
    *,
    task_id: str,
    title: str,
    status: str,
    task_type: str,
    related_domain: str = "",
) -> None:
    (root / "tasks").mkdir(parents=True, exist_ok=True)
    (root / "tasks" / f"{task_id}-example.yaml").write_text(
        "\n".join(
            [
                f"id: {task_id}",
                f'title: "{title}"',
                f"type: {task_type}",
                f"status: {status}",
                "difficulty: medium",
                "priority: high",
                "",
                "input:",
                "  mode: workflow",
                f'  related_domain: "{related_domain}"',
                "  related_objects: []",
                f'  planning_context: "{title}"',
                "",
                "requirements:",
                '  - "Keep work deterministic"',
                "",
                "accepted_outputs:",
                '  - "docs/example.md"',
                "",
                "validation:",
                "  commands:",
                '    - "python3 -m physics_lab.cli validate-repo ."',
                "",
                "can_be_done_by:",
                "  - human",
                "  - codex",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_render_task_views_groups_tasks_by_lane_and_status(tmp_path: Path) -> None:
    _write_task(
        tmp_path,
        task_id="TASK-0001",
        title="Nuclear benchmark follow-up",
        status="READY",
        task_type="scientific_validation",
        related_domain="nuclear_physics",
    )
    _write_task(
        tmp_path,
        task_id="TASK-0002",
        title="Release signoff pass",
        status="IN_PROGRESS",
        task_type="release_review",
        related_domain="public_release",
    )
    _write_task(
        tmp_path,
        task_id="TASK-0003",
        title="Coverage helper",
        status="REVIEW_READY",
        task_type="code_quality_refactor",
        related_domain="repository_validation",
    )
    _write_task(
        tmp_path,
        task_id="TASK-0004",
        title="Blocked quantum pilot",
        status="BLOCKED",
        task_type="autonomous_research_pilot",
        related_domain="quantum_physics",
    )
    _write_task(
        tmp_path,
        task_id="TASK-0005",
        title="Future hype track",
        status="PROPOSED",
        task_type="benchmark_planning",
        related_domain="particle_physics",
    )
    _write_task(
        tmp_path,
        task_id="TASK-0006",
        title="Old manual lane",
        status="SUPERSEDED",
        task_type="scientific_validation",
        related_domain="nuclear_physics",
    )

    rendered = render_task_views(tmp_path)

    assert "`TASK-0001` - Nuclear benchmark follow-up" in rendered["research"]
    assert "## READY" in rendered["research"]
    assert "`TASK-0002` - Release signoff pass" in rendered["release"]
    assert "## IN_PROGRESS" in rendered["release"]
    assert "`TASK-0003` - Coverage helper" in rendered["support"]
    assert "## REVIEW_READY" in rendered["support"]
    assert "`TASK-0004` - Blocked quantum pilot" in rendered["blocked"]
    assert "`TASK-0005` - Future hype track" in rendered["watchlist"]
    assert "## SUPERSEDED" in rendered["watchlist"]
    assert "`TASK-0006` - Old manual lane" in rendered["watchlist"]


def test_sync_task_views_writes_expected_files(tmp_path: Path) -> None:
    _write_task(
        tmp_path,
        task_id="TASK-0001",
        title="Docs hygiene",
        status="READY",
        task_type="documentation",
        related_domain="contributor_workflow",
    )

    written_paths = sync_task_views(tmp_path)

    assert len(written_paths) == 5
    assert (tmp_path / "docs" / "task-views" / "support.md").exists()
    content = (tmp_path / "docs" / "task-views" / "support.md").read_text(
        encoding="utf-8"
    )
    assert "Generated support-lane view" in content
    assert "`TASK-0001` - Docs hygiene" in content
