from __future__ import annotations

from pathlib import Path

from unittest.mock import patch

from physics_lab.registry.maintainer_review import PullRequestMetadata, build_closeout_report as build_apply_closeout_report
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


def test_apply_closeout_report_defers_board_sync_by_default(tmp_path: Path) -> None:
    _write_task(tmp_path, task_id="TASK-1234", status="REVIEW_READY")
    (tmp_path / "tasks" / "ACTIVE.md").write_text("# Active Task Board\n", encoding="utf-8")
    (tmp_path / "docs").mkdir(parents=True)
    (tmp_path / "docs" / "multi-agent-dry-run.md").write_text("# dry run\n", encoding="utf-8")
    (tmp_path / "docs" / "example.md").write_text("done\n", encoding="utf-8")

    pr_metadata = PullRequestMetadata(
        number=18,
        title="TASK-1234: Example task",
        body="",
        branch="agent/roman/codex/task-1234-example-task",
        base_branch="main",
        state="MERGED",
        merged=True,
        status_checks_passed=True,
        status_checks_pending=False,
    )

    with (
        patch("physics_lab.registry.maintainer_review.current_branch", return_value="main"),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=pr_metadata),
        patch("physics_lab.registry.maintainer_review.missing_expected_outputs", return_value=()),
        patch("physics_lab.registry.maintainer_review.should_append_dry_run_entry", return_value=False),
    ):
        report = build_apply_closeout_report(
            tmp_path,
            task_id="TASK-1234",
            pull_request=18,
            apply=True,
        )

    assert report.outcome == "APPLIED"
    assert any("Deferred tasks/ACTIVE.md synchronization" in item for item in report.applied_changes)
    assert not any("Synchronized tasks/ACTIVE.md" in item for item in report.applied_changes)
