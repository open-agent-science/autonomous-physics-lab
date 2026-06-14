from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

from physics_lab.registry.task_pr_helper import (
    commit_subject_errors_for_task,
    prepare_current_task_pr,
    preflight_task_pr,
    task_branch,
    task_pr_body,
    task_slug_from_title,
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


def test_task_branch_normalizes_github_username_contributor_id() -> None:
    assert (
        task_branch("GladunRV", "codex", "TASK-0247", "pr-lifecycle-guardrails")
        == "agent/gladunrv/codex/task-0247-pr-lifecycle-guardrails"
    )
    assert (
        task_branch("RomanHladun24-Dot", "claude", "TASK-0247", "pr-lifecycle-guardrails")
        == "agent/romanhladun24-dot/claude/task-0247-pr-lifecycle-guardrails"
    )


def test_task_slug_from_title_builds_portable_ascii_slug() -> None:
    assert (
        task_slug_from_title(
            "Harden Windows agent bootstrap and PR publication diagnostics",
            fallback="task-0519",
        )
        == "harden-windows-agent-bootstrap-and-pr-publication-diagnostics"
    )
    assert task_slug_from_title("Задача", fallback="task-0609") == "task-0609"


def test_commit_subject_errors_for_task_enforces_task_scoped_format() -> None:
    assert (
        commit_subject_errors_for_task(
            "TASK-0747",
            (
                "fix(task-0747): prefer GitHub usernames for contributor IDs",
                "docs(task-0747): document contributor identity policy",
            ),
        )
        == ()
    )

    errors = commit_subject_errors_for_task(
        "TASK-0747",
        (
            "fix: prefer GitHub usernames for contributor IDs",
            "fix(task-0746): update wrong task",
        ),
    )

    assert len(errors) == 2
    assert "fix: prefer GitHub usernames" in errors[0]
    assert "<type>(task-0747): <short summary>" in errors[0]


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
    assert "- [ ] Branch pushed" in body
    assert "- [ ] Draft PR opened" in body
    assert "manual PR creation commands provided" in body
    assert "manual ready command provided" in body
    # Location-independent: the helper resolves the path at runtime (flat or archived).
    assert "TASK-0247-add-pr-lifecycle-guardrails.yaml" in body
    assert "- Contributor ID: `roman`" in body
    assert "Agent session ID" not in body
    assert "## Output Routing" in body
    assert "AGENT_PUBLISHED" in body
    assert "Gate A/Gate B status" in body


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


def test_prepare_current_task_pr_generates_body_from_task_and_current_branch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]

    monkeypatch.setattr(
        "physics_lab.registry.task_pr_helper.current_branch",
        lambda root: "agent/roman/codex/task-0247-add-pr-lifecycle-guardrails-for-autonomous-agents",
    )
    monkeypatch.setattr(
        "physics_lab.registry.task_pr_helper.changed_files_vs_main",
        lambda root, branch, base_ref="main": (
            "scripts/apl_task_pr_helper.py",
            "tests/test_task_pr_helper.py",
        ),
    )

    prepared = prepare_current_task_pr(
        repo_root,
        task_id="TASK-0247",
        contributor_id="roman",
        github_username="gladunrv",
        agent_id="codex",
        human_reviewer="gladunrv",
        summary="Add PR lifecycle checks for agents.",
    )

    assert prepared.preflight.ok
    assert prepared.current_branch == prepared.expected_branch
    assert prepared.title == "TASK-0247: Add PR lifecycle guardrails for autonomous agents"
    assert "scripts/apl_task_pr_helper.py" in prepared.body
    assert "tests/test_task_pr_helper.py" in prepared.body
    assert any(
        "validate-repo . --strict --fail-on-warnings" in command
        for command in prepared.validation_commands
    )


def test_prepare_current_task_pr_omits_local_body_file_artifact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]

    monkeypatch.setattr(
        "physics_lab.registry.task_pr_helper.current_branch",
        lambda root: "agent/roman/codex/task-0247-add-pr-lifecycle-guardrails-for-autonomous-agents",
    )
    monkeypatch.setattr(
        "physics_lab.registry.task_pr_helper.changed_files_vs_main",
        lambda root, branch, base_ref="main": (
            "scripts/apl_task_pr_helper.py",
            ".apl-pr-body.md",
        ),
    )

    prepared = prepare_current_task_pr(
        repo_root,
        task_id="TASK-0247",
        contributor_id="roman",
        github_username="gladunrv",
        agent_id="codex",
        human_reviewer="gladunrv",
        summary="Add PR lifecycle checks for agents.",
        local_artifact_paths=(".apl-pr-body.md",),
    )

    assert "scripts/apl_task_pr_helper.py" in prepared.changed_files
    assert ".apl-pr-body.md" not in prepared.changed_files
    assert ".apl-pr-body.md" not in prepared.body


def test_prepare_current_task_pr_rejects_wrong_current_branch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]

    monkeypatch.setattr(
        "physics_lab.registry.task_pr_helper.current_branch",
        lambda root: "feature/task-0247-pr-lifecycle-guardrails",
    )
    monkeypatch.setattr(
        "physics_lab.registry.task_pr_helper.changed_files_vs_main",
        lambda root, branch, base_ref="main": ("scripts/apl_task_pr_helper.py",),
    )

    prepared = prepare_current_task_pr(
        repo_root,
        task_id="TASK-0247",
        contributor_id="roman",
        github_username="gladunrv",
        agent_id="codex",
        human_reviewer="gladunrv",
        summary="Add PR lifecycle checks for agents.",
    )

    assert not prepared.preflight.ok
    assert any("Branch must follow" in item for item in prepared.preflight.errors)
    assert any("Current branch differs" in item for item in prepared.preflight.warnings)


def test_prepare_current_task_pr_rejects_bad_commit_subject_before_pr_creation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]

    monkeypatch.setattr(
        "physics_lab.registry.task_pr_helper.current_branch",
        lambda root: "agent/roman/codex/task-0247-add-pr-lifecycle-guardrails-for-autonomous-agents",
    )
    monkeypatch.setattr(
        "physics_lab.registry.task_pr_helper.changed_files_vs_main",
        lambda root, branch, base_ref="main": ("scripts/apl_task_pr_helper.py",),
    )
    monkeypatch.setattr(
        "physics_lab.registry.task_pr_helper.commit_subjects_vs_base",
        lambda root, branch, base_ref="main": ("fix: add PR lifecycle guardrails",),
    )

    prepared = prepare_current_task_pr(
        repo_root,
        task_id="TASK-0247",
        contributor_id="roman",
        github_username="gladunrv",
        agent_id="codex",
        human_reviewer="gladunrv",
        summary="Add PR lifecycle checks for agents.",
    )

    assert not prepared.preflight.ok
    assert any(
        "does not follow '<type>(task-0247): <short summary>'" in item
        for item in prepared.preflight.errors
    )


@pytest.mark.parametrize(
    "strict_command",
    (
        r"..\..\.venv\Scripts\python.exe -m physics_lab.cli validate-repo . --strict --fail-on-warnings",
        ".venv/bin/python -m physics_lab.cli validate-repo . --strict --fail-on-warnings",
        r'"C:\Program Files\Python312\python.exe" -m physics_lab.cli validate-repo . --strict --fail-on-warnings',
    ),
)
def test_preflight_task_pr_accepts_bom_and_portable_venv_validation(
    strict_command: str,
) -> None:
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
        validation_commands=(strict_command,),
        scientific_claim_impact="No claim promotion.",
        result_artifact_impact="No committed result artifacts changed.",
        root=repo_root,
    )

    report = preflight_task_pr(
        repo_root,
        branch=branch,
        title=title,
        body_text="\ufeff" + body,
    )

    assert report.ok
    assert report.warnings == ()


def test_task_pr_body_accepts_explicit_output_routing() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    body = task_pr_body(
        task_id="TASK-0247",
        branch="agent/roman/codex/task-0247-pr-lifecycle-guardrails",
        title="TASK-0247: add PR lifecycle guardrails",
        contributor_id="roman",
        github_username="gladunrv",
        agent_tool="Codex",
        human_reviewer="gladunrv",
        summary="Add PR lifecycle checks for agents.",
        changed_files=("scripts/apl_task_pr_helper.py",),
        validation_commands=(),
        scientific_claim_impact="No claim promotion.",
        result_artifact_impact="No committed result artifacts changed.",
        task_verdict="REVIEW_READY",
        canonical_destination="docs/reviews/example.md",
        limitations_blockers="Offline fallback remains advisory.",
        root=repo_root,
    )

    assert "- Task verdict: `REVIEW_READY`" in body
    assert "- Canonical destination: `docs/reviews/example.md`" in body
    assert "- Limitations / blockers: Offline fallback remains advisory." in body


def test_preflight_task_pr_flags_agent_tool_mismatch() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    branch = "agent/roman/claude/task-0247-pr-lifecycle-guardrails"
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

    assert not report.ok
    assert any("does not match branch agent id `claude`" in item for item in report.errors)


def test_preflight_task_pr_flags_contributor_metadata_mismatch() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    branch = "agent/gladunrv/codex/task-0247-pr-lifecycle-guardrails"
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
        ),
        scientific_claim_impact="No claim promotion.",
        result_artifact_impact="No committed result artifacts changed.",
        root=repo_root,
    )

    report = preflight_task_pr(repo_root, branch=branch, title=title, body_text=body)

    assert not report.ok
    assert any(
        "Contributor ID metadata `roman` does not match branch contributor id `gladunrv`"
        in item
        for item in report.errors
    )


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


def test_cli_scaffold_normalizes_contributor_id_from_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_task_pr_helper.py",
            "scaffold",
            "--task-id",
            "TASK-0247",
            "--contributor-id",
            "GladunRV",
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
    assert "agent/gladunrv/codex/task-0247-pr-lifecycle-guardrails" in result.stdout
    assert "- Contributor ID: `gladunrv`" in result.stdout


def test_cli_scaffold_infers_claude_agent_tool_from_agent_id() -> None:
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
            "claude",
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
    assert "agent/roman/claude/task-0247-pr-lifecycle-guardrails" in result.stdout
    assert "- Agent tool: `Claude Code`" in result.stdout


def test_cli_prepare_current_rejects_noncanonical_current_branch(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    body_file = tmp_path / "body.md"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_task_pr_helper.py",
            "prepare-current",
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
            "--summary",
            "Add PR lifecycle checks for agents.",
            "--body-file",
            str(body_file),
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert (
        "Expected branch: agent/roman/codex/task-0247-add-pr-lifecycle-guardrails-for-autonomous-agents"
        in result.stdout
    )
    assert "Current branch differs" in result.stdout
    assert body_file.exists()
