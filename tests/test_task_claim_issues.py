from __future__ import annotations

from pathlib import Path
import subprocess
from unittest.mock import Mock, patch

from physics_lab.registry.github_readonly import GitHubReadResult
from physics_lab.registry.task_claim_issues import (
    classify_task_claim_issues,
    close_task_claim_issue,
    extract_branch,
    extract_task_id,
    is_task_claim_like,
    load_open_github_issues,
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


def test_load_open_github_issues_uses_shared_read_client(tmp_path: Path) -> None:
    payload = [
        {
            "number": 1619,
            "title": "Task claim: TASK-1071 external freeze",
            "body": "Task ID: TASK-1071",
            "labels": [],
            "url": "https://github.com/example/issues/1619",
        }
    ]
    client = Mock()
    client.list_task_claims.return_value = GitHubReadResult(
        payload=payload,
        source="public_rest",
        diagnostics=("gh returned 401",),
    )

    result = load_open_github_issues(tmp_path, client=client)

    assert result.payload == payload
    assert result.source == "public_rest"
    assert result.diagnostics == ("gh returned 401",)
    client.list_task_claims.assert_called_once_with(limit=100)


def test_load_open_github_issues_rejects_noncanonical_repo(tmp_path: Path) -> None:
    result = load_open_github_issues(
        tmp_path,
        repo="someone/another-repository",
    )

    assert result.available is False
    assert "canonical APL repository" in result.diagnostics[0]


def test_close_task_claim_issue_discovers_windows_gh_path_without_shell(
    tmp_path: Path,
) -> None:
    gh_path = "C:\\Program Files\\GitHub CLI\\gh.exe"
    completed = subprocess.CompletedProcess(
        args=[], returncode=0, stdout="", stderr=""
    )

    with (
        patch(
            "physics_lab.registry.task_claim_issues.find_gh_path",
            return_value=gh_path,
        ),
        patch(
            "physics_lab.registry.task_claim_issues.subprocess.run",
            return_value=completed,
        ) as run_mock,
    ):
        close_task_claim_issue(
            1619,
            root=tmp_path,
            env={"PATH": ""},
        )

    command = run_mock.call_args.args[0]
    assert command[0] == gh_path
    assert command[1:4] == ["issue", "close", "1619"]
    assert run_mock.call_args.kwargs["shell"] is False
    assert run_mock.call_args.kwargs["cwd"] == tmp_path
