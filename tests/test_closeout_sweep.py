from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from physics_lab.registry.closeout_sweep import (
    CloseoutSweepReport,
    build_closeout_sweep_report,
    closeout_pr_binding_blockers,
    list_review_ready_tasks,
    load_merged_task_pull_requests,
    render_closeout_sweep_report,
)
from physics_lab.registry.maintainer_review import CloseoutReport, PullRequestMetadata
from physics_lab.registry.review_git import CommandResult


def _write_task(path: Path, *, task_id: str, title: str, status: str) -> None:
    path.write_text(
        "\n".join(
            [
                f"id: {task_id}",
                f'title: "{title}"',
                "type: documentation",
                f"status: {status}",
                "difficulty: low",
                "priority: medium",
                "strategy_alignment:",
                '  - "test fixture"',
                "input:",
                "  mode: workflow",
                '  related_domain: "testing"',
                "  related_objects: []",
                '  planning_context: "fixture"',
                "requirements:",
                '  - "fixture requirement"',
                "accepted_outputs:",
                '  - "fixture output"',
                "validation:",
                "  commands:",
                '    - "python3 -m physics_lab.cli validate-repo ."',
                "can_be_done_by: [human]",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_list_review_ready_tasks_filters_status(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    _write_task(
        tasks_dir / "TASK-1000-alpha.yaml",
        task_id="TASK-1000",
        title="Alpha",
        status="REVIEW_READY",
    )
    _write_task(
        tasks_dir / "TASK-1001-beta.yaml",
        task_id="TASK-1001",
        title="Beta",
        status="DONE",
    )

    assert list_review_ready_tasks(tmp_path) == (("TASK-1000", "Alpha"),)


def test_load_merged_task_pull_requests_parses_latest_by_task(tmp_path: Path) -> None:
    payload = "\n".join(
        [
            "2026-05-04T10:00:00Z\x1fMerge pull request #10 from gladunrv/branch-one\x1fTASK-1000: First\n\x1e",
            "2026-05-04T12:00:00Z\x1fMerge pull request #12 from gladunrv/branch-two\x1fTASK-1000: Second\n\x1e",
            "2026-05-04T13:00:00Z\x1fMerge pull request #13 from gladunrv/closeout\x1fTASK-CLOSEOUT: Batch\n\x1e",
        ]
    )

    def _fake_run_command(command, *, cwd, shell=False, timeout=60):  # noqa: ARG001
        if command[:4] == ["git", "remote", "get-url", "origin"]:
            return CommandResult(returncode=0, stdout="git@github.com:gladunrv/autonomous-physics-lab.git\n", stderr="")
        return CommandResult(returncode=0, stdout=payload, stderr="")

    with patch("physics_lab.registry.closeout_sweep.run_command", side_effect=_fake_run_command):
        result = load_merged_task_pull_requests(tmp_path)

    assert result["TASK-1000"].number == 12
    assert "TASK-CLOSEOUT" not in result
    assert result["TASK-1000"].url.endswith("/pull/12")


def test_load_merged_task_pull_requests_falls_back_to_gh_pr_list(
    tmp_path: Path,
) -> None:
    gh_payload = json.dumps(
        [
            {
                "number": 14,
                "title": "TASK-1002: Remote merged task",
                "mergedAt": "2026-05-04T14:00:00Z",
            },
            {
                "number": 15,
                "title": "TASK-CLOSEOUT: Ignore closeout PR",
                "mergedAt": "2026-05-04T15:00:00Z",
            },
        ]
    )

    def _fake_run_command(command, *, cwd, shell=False, timeout=60):  # noqa: ARG001
        if command[:4] == ["git", "remote", "get-url", "origin"]:
            return CommandResult(
                returncode=0,
                stdout="https://github.com/gladunrv/autonomous-physics-lab.git\n",
                stderr="",
            )
        if command[:2] == ["git", "log"]:
            return CommandResult(returncode=0, stdout="", stderr="")
        if command[:3] == ["gh", "pr", "list"]:
            return CommandResult(returncode=0, stdout=gh_payload, stderr="")
        return CommandResult(returncode=1, stdout="", stderr="unexpected command")

    with patch("physics_lab.registry.closeout_sweep.run_command", side_effect=_fake_run_command):
        result = load_merged_task_pull_requests(tmp_path)

    assert result["TASK-1002"].number == 14
    assert result["TASK-1002"].url.endswith("/pull/14")
    assert "TASK-CLOSEOUT" not in result


def test_build_closeout_sweep_report_separates_ready_blocked_and_skipped(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    _write_task(
        tasks_dir / "TASK-1000-alpha.yaml",
        task_id="TASK-1000",
        title="Alpha",
        status="REVIEW_READY",
    )
    _write_task(
        tasks_dir / "TASK-1001-beta.yaml",
        task_id="TASK-1001",
        title="Beta",
        status="REVIEW_READY",
    )
    _write_task(
        tasks_dir / "TASK-1002-gamma.yaml",
        task_id="TASK-1002",
        title="Gamma",
        status="REVIEW_READY",
    )

    merged_payload = {
        "TASK-1000": {
            "number": 10,
            "title": "TASK-1000: Alpha",
            "merged_at": "2026-05-04T10:00:00Z",
            "url": "https://example/10",
        },
        "TASK-1001": {
            "number": 11,
            "title": "TASK-1001: Beta",
            "merged_at": "2026-05-04T11:00:00Z",
            "url": "https://example/11",
        },
    }

    def _fake_prs(_root: Path, *, limit: int = 200):  # noqa: ARG001
        from physics_lab.registry.closeout_sweep import MergedTaskPullRequest

        return {
            task_id: MergedTaskPullRequest(task_id=task_id, **values)
            for task_id, values in merged_payload.items()
        }

    def _fake_closeout_report(root: Path, *, task_id: str, pull_request: int, apply: bool):  # noqa: ARG001
        if task_id == "TASK-1000":
            return CloseoutReport(
                outcome="READY_TO_APPLY",
                task_id=task_id,
                pull_request=pull_request,
                branch="main",
                task_status="REVIEW_READY",
                merged="yes",
                accepted_outputs="pass",
                ci_status="pass",
                blockers=(),
                required_actions=(),
                suggested_actions=(),
                applied_changes=(),
            )
        return CloseoutReport(
            outcome="BLOCKED",
            task_id=task_id,
            pull_request=pull_request,
            branch="main",
            task_status="REVIEW_READY",
            merged="yes",
            accepted_outputs="fail",
            ci_status="pass",
            blockers=("Accepted outputs are missing in main: x.",),
            required_actions=(),
            suggested_actions=(),
            applied_changes=(),
        )

    with (
        patch("physics_lab.registry.closeout_sweep.load_merged_task_pull_requests", side_effect=_fake_prs),
        patch("physics_lab.registry.closeout_sweep.build_closeout_report", side_effect=_fake_closeout_report),
        patch("physics_lab.registry.closeout_sweep.load_pr_metadata", return_value=None),
        patch("physics_lab.registry.closeout_sweep.current_branch", return_value="main"),
    ):
        report = build_closeout_sweep_report(tmp_path)

    assert len(report.ready) == 1
    assert report.ready[0].task_id == "TASK-1000"
    assert len(report.blocked) == 1
    assert report.blocked[0].task_id == "TASK-1001"
    assert len(report.skipped) == 1
    assert report.skipped[0].task_id == "TASK-1002"


def test_closeout_pr_binding_blockers_flags_mismatched_pr_metadata(tmp_path: Path) -> None:
    pr_metadata = PullRequestMetadata(
        number=10,
        title="TASK-1001: Different task",
        body="",
        branch="agent/roman/codex/task-1001-different-task",
        base_branch="main",
        state="MERGED",
        merged=True,
        status_checks_passed=True,
        status_checks_pending=False,
        changed_files=(),
    )

    with patch("physics_lab.registry.closeout_sweep.load_pr_metadata", return_value=pr_metadata):
        blockers = closeout_pr_binding_blockers(
            tmp_path,
            task_id="TASK-1000",
            pull_request=10,
        )

    assert blockers == (
        "Merged PR metadata does not match canonical task id: title task id is TASK-1001, "
        "branch task id is TASK-1001.",
    )


def test_build_closeout_sweep_report_blocks_ready_candidate_on_pr_binding_mismatch(
    tmp_path: Path,
) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    _write_task(
        tasks_dir / "TASK-1000-alpha.yaml",
        task_id="TASK-1000",
        title="Alpha",
        status="REVIEW_READY",
    )

    merged_payload = {
        "TASK-1000": {
            "number": 10,
            "title": "TASK-1000: Alpha",
            "merged_at": "2026-05-04T10:00:00Z",
            "url": "https://example/10",
        },
    }

    def _fake_prs(_root: Path, *, limit: int = 200):  # noqa: ARG001
        from physics_lab.registry.closeout_sweep import MergedTaskPullRequest

        return {
            task_id: MergedTaskPullRequest(task_id=task_id, **values)
            for task_id, values in merged_payload.items()
        }

    ready_closeout = CloseoutReport(
        outcome="READY_TO_APPLY",
        task_id="TASK-1000",
        pull_request=10,
        branch="main",
        task_status="REVIEW_READY",
        merged="yes",
        accepted_outputs="pass",
        ci_status="pass",
        blockers=(),
        required_actions=(),
        suggested_actions=(),
        applied_changes=(),
    )
    mismatched_pr = PullRequestMetadata(
        number=10,
        title="TASK-1001: Different task",
        body="",
        branch="agent/roman/codex/task-1001-different-task",
        base_branch="main",
        state="MERGED",
        merged=True,
        status_checks_passed=True,
        status_checks_pending=False,
        changed_files=(),
    )

    with (
        patch("physics_lab.registry.closeout_sweep.load_merged_task_pull_requests", side_effect=_fake_prs),
        patch("physics_lab.registry.closeout_sweep.build_closeout_report", return_value=ready_closeout),
        patch("physics_lab.registry.closeout_sweep.load_pr_metadata", return_value=mismatched_pr),
        patch("physics_lab.registry.closeout_sweep.current_branch", return_value="main"),
    ):
        report = build_closeout_sweep_report(tmp_path)

    assert len(report.ready) == 0
    assert len(report.blocked) == 1
    assert report.blocked[0].task_id == "TASK-1000"
    assert report.blocked[0].outcome == "BLOCKED"
    assert report.blocked[0].recommended_apply_command is None
    assert report.blocked[0].blockers == (
        "Merged PR metadata does not match canonical task id: title task id is TASK-1001, "
        "branch task id is TASK-1001.",
    )


def test_render_closeout_sweep_report_lists_sections() -> None:
    report = CloseoutSweepReport(branch="main", ready=(), blocked=(), skipped=())

    rendered = render_closeout_sweep_report(report)

    assert "Ready closeout candidates:" in rendered
    assert "Blocked closeout candidates:" in rendered
    assert "Skipped REVIEW_READY tasks:" in rendered
