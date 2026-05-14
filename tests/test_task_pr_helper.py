from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from physics_lab.registry.task_pr_helper import (
    preflight_task_pr,
    task_branch,
    task_pr_body,
    task_title,
)


def test_task_branch_and_title_build_canonical_shape() -> None:
    assert (
        task_branch("roman", "codex", "TASK-0247", "pr-lifecycle-guardrails")
        == "agent/roman/codex/task-0247-pr-lifecycle-guardrails"
    )
    assert (
        task_title("TASK-0247", "add PR lifecycle guardrails")
        == "TASK-0247: add PR lifecycle guardrails"
    )


def test_task_pr_body_mentions_template_sections_and_metadata() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    branch = "agent/roman/codex/task-0247-pr-lifecycle-guardrails"
    title = "TASK-0247: add PR lifecycle guardrails"
    body = task_pr_body(
        task_id="TASK-0247",
        branch=branch,
        title=title,
        contributor_id="roman",
        github_username="gladunrv",
        agent_tool="Codex",
        human_reviewer="gladunrv",
        summary="Add PR lifecycle checks for agents.",
        changed_files=("scripts/apl_pr_capability_check.py",),
        validation_commands=("python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings",),
        scientific_claim_impact="No claim promotion.",
        result_artifact_impact="No committed result artifacts changed.",
        root=repo_root,
    )

    assert "## PR Kind" in body
    assert "- [x] Canonical task PR" in body
    assert "manual PR creation commands provided" in body
    assert "manual ready command provided" in body
    assert "tasks/TASK-0247-add-pr-lifecycle-guardrails.yaml" in body
    assert "- Contributor ID: `roman`" in body
    assert "Agent session ID" not in body


def test_preflight_task_pr_flags_short_body_and_mismatched_task(tmp_path: Path) -> None:
    body = "## Summary\n\nShort body only.\n"
    report = preflight_task_pr(
        tmp_path,
        branch="agent/roman/codex/task-0247-pr-lifecycle-guardrails",
        title="TASK-0246: wrong task id",
        body_text=body,
    )

    assert not report.ok
    assert any("does not match PR title task id" in item for item in report.errors)
    assert any("missing required template sections" in item for item in report.errors)


def test_preflight_task_pr_accepts_clean_shape() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    branch = "agent/roman/codex/task-0247-pr-lifecycle-guardrails"
    title = "TASK-0247: add PR lifecycle guardrails"
    body = task_pr_body(
        task_id="TASK-0247",
        branch=branch,
        title=title,
        contributor_id="roman",
        github_username="gladunrv",
        agent_tool="Codex",
        human_reviewer="gladunrv",
        summary="Add PR lifecycle checks for agents.",
        changed_files=("scripts/apl_task_pr_helper.py",),
        validation_commands=(
            "python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings",
            "./scripts/apl_review_bundle.sh",
        ),
        scientific_claim_impact="No claim promotion.",
        result_artifact_impact="No committed result artifacts changed.",
        root=repo_root,
    )

    report = preflight_task_pr(repo_root, branch=branch, title=title, body_text=body)

    assert report.ok
    assert report.warnings == ()


def test_cli_scaffold_runs_from_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_task_pr_helper.py",
            "scaffold",
            "--task-id",
            "TASK-0247",
            "--contributor-id",
            "roman",
            "--github-username",
            "gladunrv",
            "--agent-id",
            "codex",
            "--human-reviewer",
            "gladunrv",
            "--slug",
            "pr-lifecycle-guardrails",
            "--description",
            "add PR lifecycle guardrails",
            "--summary",
            "Add PR lifecycle checks for agents.",
            "--validation-command",
            "python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings",
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "agent/roman/codex/task-0247-pr-lifecycle-guardrails" in result.stdout
    assert "TASK-0247: add PR lifecycle guardrails" in result.stdout
