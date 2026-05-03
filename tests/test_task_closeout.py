from __future__ import annotations

from pathlib import Path

from physics_lab.registry.task_closeout import build_closeout_report, render_closeout_report


def _write_task(root: Path, *, task_id: str, status: str) -> None:
    (root / "tasks").mkdir(parents=True, exist_ok=True)
    (root / "tasks" / f"{task_id}-example.yaml").write_text(
        "\n".join(
            [
                f"id: {task_id}",
                'title: "Example task"',
                "type: documentation",
                f"status: {status}",
                "difficulty: low",
                "priority: medium",
                "",
                "input:",
                "  mode: workflow",
                "  related_domain: maintainer_review",
                "  related_objects:",
                '    - "tasks/ACTIVE.md"',
                '  planning_context: "Example workflow task"',
                "",
                "requirements:",
                '  - "Keep output deterministic"',
                "",
                "accepted_outputs:",
                '  - "docs/example.md"',
                '  - "tasks/ACTIVE.md"',
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


def test_build_closeout_report_for_review_ready_task(tmp_path: Path) -> None:
    _write_task(tmp_path, task_id="TASK-1234", status="REVIEW_READY")
    (tmp_path / "tasks" / "ACTIVE.md").write_text(
        "\n".join(
            [
                "# Active Task Board",
                "",
                "## REVIEW_READY",
                "",
                "### TASK-1234 — Example task",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = build_closeout_report(tmp_path, "TASK-1234")

    assert report.task_file.name == "TASK-1234-example.yaml"
    assert report.status == "REVIEW_READY"
    assert report.active_board_match.present is True
    assert report.active_board_match.section == "REVIEW_READY"
    assert report.accepted_outputs == ("docs/example.md", "tasks/ACTIVE.md")
    assert report.warnings == ()
    assert any("sync-active-board" in item for item in report.suggested_actions)


def test_build_closeout_report_warns_when_not_review_ready(tmp_path: Path) -> None:
    _write_task(tmp_path, task_id="TASK-5678", status="DONE")
    (tmp_path / "tasks" / "ACTIVE.md").write_text(
        "\n".join(
            [
                "# Active Task Board",
                "",
                "## DONE RECENTLY",
                "",
                "- `TASK-5678` — Example task (merged)",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = build_closeout_report(tmp_path, "TASK-5678")
    rendered = render_closeout_report(report, suggest=True, root=tmp_path)

    assert report.active_board_match.present is True
    assert "Task status is DONE, not REVIEW_READY." in report.warnings[0]
    assert "Suggested file updates (not applied):" in rendered
    assert "No direct file update is suggested until the task reaches REVIEW_READY" in rendered
