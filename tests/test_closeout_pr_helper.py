from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from physics_lab.registry.closeout_pr_helper import (
    closeout_branch,
    closeout_pr_body,
    closeout_title,
    preflight_closeout_pr,
)


def test_closeout_branch_and_title_build_canonical_shape() -> None:
    assert (
        closeout_branch("roman", "codex", "task-0244-snapshot-fix")
        == "agent/roman/codex/closeout-task-0244-snapshot-fix"
    )
    assert closeout_title("mark task-0244 done") == "TASK-CLOSEOUT: mark task-0244 done"


def test_closeout_pr_body_mentions_closed_task_files_and_metadata() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    branch = "agent/roman/codex/closeout-task-0244-snapshot-fix"
    title = "TASK-CLOSEOUT: mark task-0244 done"
    body = closeout_pr_body(
        task_ids=("TASK-0244",),
        branch=branch,
        title=title,
        contributor_id="roman",
        github_username="gladunrv",
        agent_tool="Codex",
        human_reviewer="gladunrv",
        include_active_board=True,
        include_context=True,
        root=repo_root,
    )

    assert "## PR Kind" in body
    assert "Closed Task Files" in body
    assert "tasks/TASK-0244-fix-snapshot-canonical-experiment-list.yaml" in body
    assert "- Contributor ID: `roman`" in body
    assert "Agent session ID" not in body


def test_preflight_closeout_pr_flags_short_body_and_placeholders(tmp_path: Path) -> None:
    body = "\n".join(
        [
            "## Summary",
            "",
            "Short body only.",
            "",
            "## Validation",
            "",
            "- `python3 -m pytest`",
            "",
            "- Contributor ID:",
        ]
    )
    report = preflight_closeout_pr(
        tmp_path,
        branch="agent/roman/codex/closeout-task-0244-snapshot-fix",
        title="TASK-CLOSEOUT: mark task-0244 done",
        body_text=body,
    )

    assert not report.ok
    assert any("missing required template sections" in item for item in report.errors)
    assert any("missing required metadata fields or values" in item for item in report.errors)


def test_preflight_closeout_pr_accepts_clean_shape(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    branch = "agent/roman/codex/closeout-task-0244-snapshot-fix"
    title = "TASK-CLOSEOUT: mark task-0244 done"
    body = closeout_pr_body(
        task_ids=("TASK-0244",),
        branch=branch,
        title=title,
        contributor_id="roman",
        github_username="gladunrv",
        agent_tool="Codex",
        human_reviewer="gladunrv",
        include_active_board=True,
        include_context=True,
        root=repo_root,
    )

    report = preflight_closeout_pr(tmp_path, branch=branch, title=title, body_text=body)

    assert report.ok
    assert report.warnings == ()


def test_cli_scaffold_runs_from_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_closeout_pr_helper.py",
            "scaffold",
            "--task-id",
            "TASK-0244",
            "--contributor-id",
            "roman",
            "--github-username",
            "gladunrv",
            "--agent-id",
            "codex",
            "--human-reviewer",
            "gladunrv",
            "--slug",
            "task-0244-snapshot-fix",
            "--description",
            "mark task-0244 done",
            "--include-active-board",
            "--include-context",
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "agent/roman/codex/closeout-task-0244-snapshot-fix" in result.stdout
    assert "TASK-CLOSEOUT: mark task-0244 done" in result.stdout


def test_cli_scaffold_body_only_omits_branch_heading() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_closeout_pr_helper.py",
            "scaffold",
            "--task-id",
            "TASK-0244",
            "--contributor-id",
            "roman",
            "--github-username",
            "gladunrv",
            "--agent-id",
            "codex",
            "--human-reviewer",
            "gladunrv",
            "--slug",
            "task-0244-snapshot-fix",
            "--description",
            "mark task-0244 done",
            "--include-active-board",
            "--include-context",
            "--body-only",
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout.startswith("## PR Kind")
    assert not result.stdout.startswith("Branch:")
