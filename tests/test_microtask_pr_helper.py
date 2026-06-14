from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from physics_lab.registry.microtask_pr_helper import (
    microtask_branch,
    microtask_pr_body,
    microtask_title,
    preflight_microtask_pr,
)


def test_microtask_branch_builds_single_and_batch_variants() -> None:
    assert (
        microtask_branch(
            "roman",
            "codex",
            "audit-electron-mass",
            microtask_id="PMR-001",
        )
        == "agent/roman/codex/microtask-PMR-001-audit-electron-mass"
    )
    assert (
        microtask_branch(
            "roman",
            "codex",
            "challenge-entries",
            queue_id="dimensional-analysis-validator",
        )
        == "agent/roman/codex/microtask-batch-dimensional-analysis-validator--challenge-entries"
    )


def test_microtask_branch_normalizes_github_username_contributor_id() -> None:
    assert (
        microtask_branch(
            "GladunRV",
            "codex",
            "challenge-entries",
            queue_id="dimensional-analysis-validator",
        )
        == "agent/gladunrv/codex/microtask-batch-dimensional-analysis-validator--challenge-entries"
    )


def test_microtask_pr_body_mentions_review_bundle_and_queue() -> None:
    branch = "agent/roman/codex/microtask-batch-dimensional-analysis-validator--challenge-entries"
    title = microtask_title(
        "dimensional-analysis-validator",
        "add DAV-003 DAV-004 DAV-008 challenge entries",
    )
    body = microtask_pr_body(
        queue_id="dimensional-analysis-validator",
        branch=branch,
        title=title,
        microtask_ids=("DAV-003", "DAV-004", "DAV-008"),
    )

    assert "tasks/microtasks/dimensional-analysis-validator.yaml" in body
    assert "## PR Kind" in body
    assert "## Primary Reference" in body
    assert "./scripts/apl_review_bundle.sh" in body
    assert "DAV-003, DAV-004, DAV-008" in body
    assert "Agent session ID" not in body


def test_preflight_microtask_pr_flags_placeholders_and_mismatch(tmp_path: Path) -> None:
    body = "\n".join(
        [
            "## Task ID",
            "",
            "- `TASK-XXXX`",
        ]
    )
    report = preflight_microtask_pr(
        tmp_path,
        branch="agent/roman/codex/microtask-batch-particle-mass-relations--batch-note",
        title="microtask(dimensional-analysis-validator): add batch note",
        body_text=body,
    )

    assert not report.ok
    assert any("placeholder text" in item for item in report.errors)
    assert any("does not match PR title queue id" in item for item in report.errors)


def test_preflight_microtask_pr_accepts_clean_batch_shape(tmp_path: Path) -> None:
    snapshots = tmp_path / "_snapshots"
    snapshots.mkdir()
    branch = "agent/roman/codex/microtask-batch-dimensional-analysis-validator--challenge-entries"
    (snapshots / "review_agent-roman-codex-microtask-batch-dimensional-analysis-validator--challenge-entries_20260508_000000.md").write_text(
        f"- branch: `{branch}`\n",
        encoding="utf-8",
    )
    title = "microtask(dimensional-analysis-validator): add DAV-003 DAV-004 DAV-008 challenge entries"
    body = microtask_pr_body(
        queue_id="dimensional-analysis-validator",
        branch=branch,
        title=title,
        microtask_ids=("DAV-003", "DAV-004", "DAV-008"),
    )

    report = preflight_microtask_pr(tmp_path, branch=branch, title=title, body_text=body)

    assert report.ok
    assert report.warnings == ()


def test_cli_scaffold_runs_from_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_microtask_pr_helper.py",
            "scaffold",
            "--queue-id",
            "dimensional-analysis-validator",
            "--contributor-id",
            "roman",
            "--agent-id",
            "codex",
            "--slug",
            "challenge-entries",
            "--description",
            "add challenge entries",
            "--microtask-ids",
            "DAV-003",
            "DAV-004",
            "DAV-008",
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "microtask-batch-dimensional-analysis-validator--challenge-entries" in result.stdout


def test_cli_status_lists_available_microtasks_from_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_microtask_pr_helper.py",
            "status",
            "--queue-id",
            "pendulum-formula-falsification",
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Microtask availability for pendulum-formula-falsification" in result.stdout
    assert "`pendulum-formula-falsification`" in result.stdout
