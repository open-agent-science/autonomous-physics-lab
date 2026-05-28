from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from physics_lab.cli import app
from physics_lab.registry.active_board import (
    active_board_is_synced,
    render_active_board_snapshot,
    sync_active_board,
)


def _write_task(
    root: Path,
    *,
    task_id: str,
    title: str,
    status: str,
    task_type: str = "documentation",
    priority: str = "medium",
    difficulty: str = "low",
) -> None:
    (root / "tasks").mkdir(parents=True, exist_ok=True)
    (root / "tasks" / f"{task_id}-example.yaml").write_text(
        "\n".join(
            [
                f"id: {task_id}",
                f'title: "{title}"',
                f"type: {task_type}",
                f"status: {status}",
                f"difficulty: {difficulty}",
                f"priority: {priority}",
                "",
                "input:",
                "  mode: workflow",
                "  related_objects: []",
                '  planning_context: "Example workflow task"',
                "",
                "requirements:",
                '  - "Keep output deterministic"',
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


def test_render_active_board_snapshot_groups_task_statuses(tmp_path: Path) -> None:
    _write_task(tmp_path, task_id="TASK-0002", title="Review task", status="REVIEW_READY")
    _write_task(tmp_path, task_id="TASK-0001", title="Ready task", status="READY")
    _write_task(tmp_path, task_id="TASK-0003", title="Done task", status="DONE")
    _write_task(tmp_path, task_id="TASK-0004", title="Old task", status="SUPERSEDED")

    rendered = render_active_board_snapshot(tmp_path)

    assert "## READY" in rendered
    assert "- `TASK-0001` — Ready task (`documentation`, priority `medium`, difficulty `low`)" in rendered
    assert "## REVIEW_READY" in rendered
    assert "- `TASK-0002` — Review task (`documentation`, priority `medium`, difficulty `low`)" in rendered
    assert "## DONE RECENTLY" in rendered
    assert "- `TASK-0003` — Done task (merged)" in rendered
    assert "## SUPERSEDED" in rendered
    assert "- `TASK-0004` — Old task (`documentation`, priority `medium`, difficulty `low`)" in rendered


def test_sync_active_board_replaces_generated_block(tmp_path: Path) -> None:
    _write_task(tmp_path, task_id="TASK-0001", title="Ready task", status="READY")
    (tmp_path / "tasks" / "ACTIVE.md").write_text(
        "\n".join(
            [
                "# Active Task Board",
                "",
                "<!-- BEGIN AUTO TASK STATUS BOARD -->",
                "stale",
                "<!-- END AUTO TASK STATUS BOARD -->",
                "",
                "## DO NOT START YET",
                "",
                "- dashboard",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    sync_active_board(tmp_path)
    content = (tmp_path / "tasks" / "ACTIVE.md").read_text(encoding="utf-8")

    assert "stale" not in content
    assert "- `TASK-0001` — Ready task (`documentation`, priority `medium`, difficulty `low`)" in content
    assert "## DO NOT START YET" in content


def test_sync_active_board_cli_command(tmp_path: Path) -> None:
    _write_task(tmp_path, task_id="TASK-0001", title="Ready task", status="READY")
    (tmp_path / "tasks" / "ACTIVE.md").write_text(
        "\n".join(
            [
                "# Active Task Board",
                "",
                "<!-- BEGIN AUTO TASK STATUS BOARD -->",
                "stale",
                "<!-- END AUTO TASK STATUS BOARD -->",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "missions").mkdir(exist_ok=True)
    (tmp_path / "missions" / "current.yaml").write_text(
        "\n".join(
            [
                "default_mode: research",
                "curator_cycle:",
                "  decision: updated",
                '  updated: "2026-05-14"',
                '  source: "TASK-0001"',
                '  note: "test sync"',
                "missions:",
                "  - id: demo",
                '    title: "Demo Mission"',
                "    rank: 1",
                "    actions: []",
                "support_actions: []",
                "maintainer_actions: []",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / "docs" / "current-missions.md").write_text(
        "# Current Missions\n\n## Recommended Mission Now\n\n**Demo Mission** is active.\n",
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(app, ["sync-active-board", str(tmp_path)])

    assert result.exit_code == 0
    assert "Synchronized generated task state:" in result.stdout
    assert "docs/task-views/research.md" in result.stdout
    assert active_board_is_synced(tmp_path) is True
