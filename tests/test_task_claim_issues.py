from __future__ import annotations

from pathlib import Path

from physics_lab.registry.task_claim_issues import (
    classify_task_claim_issues,
    extract_branch,
    extract_task_id,
    is_task_claim_like,
    render_task_claim_issue_report,
)


def _write_task(root: Path, task_id: str, status: str) -> None:
    tasks_dir = root / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    (tasks_dir / f"{task_id}-fixture.yaml").write_text(
        "\n".join(
            [
                f"id: {task_id}",
                'title: "Fixture task"',
                "type: maintainer_tooling",
                f"status: {status}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_extract_task_id_and_branch_from_claim_text() -> None:
    body = "Task ID: TASK-0530\nBranch: agent/roman/codex/task-0530-example\n"

    assert extract_task_id("Task claim", body) == "TASK-0530"
    assert extract_branch(body) == "agent/roman/codex/task-0530-example"


def test_is_task_claim_like_accepts_label_or_claim_text() -> None:
    assert is_task_claim_like(
        {
            "title": "plain issue",
            "body": "",
            "labels": [{"name": "task-claim"}],
        }
    )
    assert is_task_claim_like(
        {
            "title": "TASK-0528 claim: fill checksum gap",
            "body": "Task ID: TASK-0528",
            "labels": [],
        }
    )
    assert not is_task_claim_like({"title": "bug report", "body": "TASK-0528", "labels": []})


def test_classify_task_claim_issues_uses_canonical_task_status(tmp_path: Path) -> None:
    _write_task(tmp_path, "TASK-0491", "DONE")
    _write_task(tmp_path, "TASK-0527", "REVIEW_READY")
    _write_task(tmp_path, "TASK-0530", "READY")

    report = classify_task_claim_issues(
        tmp_path,
        [
            {
                "number": 748,
                "title": "Task claim: TASK-0491 scorecard",
                "body": "Task ID: TASK-0491\nBranch: agent/roman/codex/task-0491-scorecard\n",
                "labels": [{"name": "task-claim"}],
                "url": "https://example/748",
            },
            {
                "number": 763,
                "title": "TASK-0527 claim: fixture",
                "body": "Task ID: TASK-0527\nBranch: agent/roman/codex/task-0527-fixture\n",
                "labels": [],
                "url": "https://example/763",
            },
            {
                "number": 753,
                "title": "Task claim: TASK-0530 onboarding",
                "body": "Task ID: TASK-0530",
                "labels": [{"name": "task-claim"}],
                "url": "https://example/753",
            },
            {
                "number": 999,
                "title": "non-claim issue",
                "body": "TASK-0491",
                "labels": [],
                "url": "https://example/999",
            },
        ],
    )

    assert [issue.number for issue in report.closeable] == [748]
    assert [issue.number for issue in report.needs_task_closeout] == [763]
    assert [issue.number for issue in report.ignored] == [753, 999]

    rendered = render_task_claim_issue_report(report)
    assert "Closeable task-claim issues: 1" in rendered
    assert "Need task closeout first: 1" in rendered
    assert "#748 TASK-0491" in rendered
    assert "#763 TASK-0527" in rendered
