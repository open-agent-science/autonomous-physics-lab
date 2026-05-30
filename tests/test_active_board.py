from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from physics_lab.cli import app
from physics_lab.registry.active_board import load_board_entries


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


def test_load_board_entries_parses_statuses(tmp_path: Path) -> None:
    _write_task(tmp_path, task_id="TASK-0002", title="Review task", status="REVIEW_READY")
    _write_task(tmp_path, task_id="TASK-0001", title="Ready task", status="READY")
    _write_task(tmp_path, task_id="TASK-0003", title="Done task", status="DONE")

    entries = load_board_entries(tmp_path)
    by_id = {entry.task_id: entry for entry in entries}

    assert set(by_id) == {"TASK-0001", "TASK-0002", "TASK-0003"}
    assert by_id["TASK-0001"].status == "READY"
    assert by_id["TASK-0002"].status == "REVIEW_READY"
    assert by_id["TASK-0003"].title == "Done task"
    assert by_id["TASK-0001"].task_number == 1


def test_load_board_entries_normalizes_status_aliases(tmp_path: Path) -> None:
    _write_task(tmp_path, task_id="TASK-0005", title="Claimed task", status="CLAIMED")

    entries = load_board_entries(tmp_path)

    assert entries[0].status == "IN_PROGRESS"


def test_sync_active_board_cli_syncs_task_views(tmp_path: Path) -> None:
    _write_task(tmp_path, task_id="TASK-0001", title="Ready task", status="READY")
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
    # tasks/ACTIVE.md is retired: the command must not recreate it.
    assert not (tmp_path / "tasks" / "ACTIVE.md").exists()
