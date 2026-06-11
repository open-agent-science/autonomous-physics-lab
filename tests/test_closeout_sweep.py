from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from unittest.mock import patch

from physics_lab.registry.closeout_sweep import (
    CloseoutSweepCandidate,
    apply_closeout_sweep_report,
    CloseoutSweepReport,
    auto_closeout_blockers,
    build_closeout_sweep_report,
    classify_full_repo_signal,
    closeout_pr_binding_blockers,
    list_review_ready_tasks,
    load_merged_task_pull_requests,
    render_closeout_sweep_apply_report,
    render_closeout_sweep_report,
    task_closeout_policy,
    task_unblocks_others,
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


def test_load_merged_task_pull_requests_parses_squash_merge_subjects(
    tmp_path: Path,
) -> None:
    commands: list[list[str]] = []
    payload = "\n".join(
        [
            (
                "2026-06-11T07:22:08Z\x1f"
                "TASK-0717: Document closeout policy schema and helper examples (#1024)\x1f"
                "\x1e"
            ),
            (
                "2026-06-11T07:10:01Z\x1f"
                "TASK-QUEUE: Seed source-gated science cycle (#1022)\x1f"
                "\x1e"
            ),
        ]
    )

    def _fake_run_command(command, *, cwd, shell=False, timeout=60):  # noqa: ARG001
        commands.append(command)
        if command[:4] == ["git", "remote", "get-url", "origin"]:
            return CommandResult(
                returncode=0,
                stdout="git@github.com:open-agent-science/autonomous-physics-lab.git\n",
                stderr="",
            )
        if command[:2] == ["git", "log"]:
            return CommandResult(returncode=0, stdout=payload, stderr="")
        if command[1:3] == ["pr", "list"]:
            return CommandResult(returncode=1, stdout="", stderr="gh unavailable")
        return CommandResult(returncode=1, stdout="", stderr="unexpected command")

    with (
        patch("physics_lab.registry.closeout_sweep.find_gh_path", return_value="/custom/gh"),
        patch("physics_lab.registry.closeout_sweep.run_command", side_effect=_fake_run_command),
    ):
        result = load_merged_task_pull_requests(tmp_path)

    assert result["TASK-0717"].number == 1024
    assert result["TASK-0717"].title == (
        "TASK-0717: Document closeout policy schema and helper examples"
    )
    assert result["TASK-0717"].url.endswith("/pull/1024")
    assert "TASK-QUEUE" not in result
    git_log_command = next(command for command in commands if command[:2] == ["git", "log"])
    assert "--merges" not in git_log_command


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
        if command[1:3] == ["pr", "list"]:
            return CommandResult(returncode=0, stdout=gh_payload, stderr="")
        return CommandResult(returncode=1, stdout="", stderr="unexpected command")

    with (
        patch("physics_lab.registry.closeout_sweep.find_gh_path", return_value="/custom/gh"),
        patch("physics_lab.registry.closeout_sweep.run_command", side_effect=_fake_run_command),
    ):
        result = load_merged_task_pull_requests(tmp_path)

    assert result["TASK-1002"].number == 14
    assert result["TASK-1002"].url.endswith("/pull/14")
    assert "TASK-CLOSEOUT" not in result


def test_load_merged_task_pull_requests_uses_discovered_gh_path(
    tmp_path: Path,
) -> None:
    commands: list[list[str]] = []
    gh_payload = json.dumps(
        [
            {
                "number": 16,
                "title": "TASK-1003: Remote merged task",
                "mergedAt": "2026-05-04T16:00:00Z",
            },
        ]
    )

    def _fake_run_command(command, *, cwd, shell=False, timeout=60):  # noqa: ARG001
        commands.append(command)
        if command[:4] == ["git", "remote", "get-url", "origin"]:
            return CommandResult(
                returncode=0,
                stdout="https://github.com/gladunrv/autonomous-physics-lab.git\n",
                stderr="",
            )
        if command[:2] == ["git", "log"]:
            return CommandResult(returncode=0, stdout="", stderr="")
        if command[:3] == ["/custom/gh", "pr", "list"]:
            return CommandResult(returncode=0, stdout=gh_payload, stderr="")
        return CommandResult(returncode=1, stdout="", stderr="unexpected command")

    with (
        patch("physics_lab.registry.closeout_sweep.find_gh_path", return_value="/custom/gh"),
        patch("physics_lab.registry.closeout_sweep.run_command", side_effect=_fake_run_command),
    ):
        result = load_merged_task_pull_requests(tmp_path)

    assert result["TASK-1003"].number == 16
    assert any(command[:3] == ["/custom/gh", "pr", "list"] for command in commands)


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


def test_apply_closeout_sweep_report_updates_all_ready_tasks(tmp_path: Path) -> None:
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
    candidates = (
        CloseoutSweepCandidate(
            task_id="TASK-1000",
            task_title="Alpha",
            pull_request=10,
            pr_title="TASK-1000: Alpha",
            pr_url="https://example/10",
            outcome="READY_TO_APPLY",
            blockers=(),
            required_actions=(),
            recommended_apply_command=None,
        ),
        CloseoutSweepCandidate(
            task_id="TASK-1001",
            task_title="Beta",
            pull_request=11,
            pr_title="TASK-1001: Beta",
            pr_url="https://example/11",
            outcome="READY_TO_APPLY",
            blockers=(),
            required_actions=(),
            recommended_apply_command=None,
        ),
    )
    report = CloseoutSweepReport(
        branch="main",
        ready=candidates,
        blocked=(),
        skipped=(),
    )

    with patch("physics_lab.registry.closeout_sweep.git_status_clean", return_value=True):
        apply_report = apply_closeout_sweep_report(tmp_path, report)

    assert len(apply_report.applied) == 2
    assert "status: DONE" in (tasks_dir / "TASK-1000-alpha.yaml").read_text(encoding="utf-8")
    assert "status: DONE" in (tasks_dir / "TASK-1001-beta.yaml").read_text(encoding="utf-8")
    rendered = render_closeout_sweep_apply_report(apply_report)
    assert "TASK-1000 -> DONE" in rendered
    assert "TASK-1001 -> DONE" in rendered


def test_task_closeout_policy_defaults_to_auto_and_honors_opt_out() -> None:
    assert task_closeout_policy({}) == "auto"
    assert task_closeout_policy({"closeout": "auto"}) == "auto"
    assert task_closeout_policy({"closeout": "review"}) == "review"


def test_auto_closeout_blockers_is_empty_for_a_safe_task() -> None:
    blockers = auto_closeout_blockers(
        {"id": "TASK-2000"},
        pr_changed_files=("docs/reviews/some-gate.md", "tasks/TASK-2000-x.yaml"),
        unblocks_others=False,
    )
    assert blockers == ()


def test_auto_closeout_blockers_flags_review_opt_out() -> None:
    blockers = auto_closeout_blockers(
        {"closeout": "review"},
        pr_changed_files=("docs/reviews/some-gate.md",),
        unblocks_others=False,
    )
    assert any("closeout: review" in reason for reason in blockers)


def test_auto_closeout_blockers_flags_protected_artifacts() -> None:
    blockers = auto_closeout_blockers(
        {},
        pr_changed_files=("results/EXP-0001/RUN-0001/result.yaml", "tasks/TASK-2000-x.yaml"),
        unblocks_others=False,
    )
    assert any("protected scientific artifact" in reason for reason in blockers)
    assert any("results/EXP-0001/RUN-0001/result.yaml" in reason for reason in blockers)


def test_auto_closeout_blockers_flags_unblocking_task() -> None:
    blockers = auto_closeout_blockers(
        {},
        pr_changed_files=("docs/reviews/some-gate.md",),
        unblocks_others=True,
    )
    assert any("BLOCKED task" in reason for reason in blockers)


def test_task_unblocks_others_detects_a_blocked_dependent(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    _write_task(
        tasks_dir / "TASK-3000-self.yaml",
        task_id="TASK-3000",
        title="Self",
        status="REVIEW_READY",
    )
    blocked = tasks_dir / "TASK-3001-dependent.yaml"
    blocked.write_text(
        "id: TASK-3001\n"
        "status: BLOCKED\n"
        'planning_context: "Start only after TASK-3000 is merged."\n',
        encoding="utf-8",
    )

    assert task_unblocks_others(tmp_path, "TASK-3000") is True
    # A task that nobody references does not unblock anything.
    assert task_unblocks_others(tmp_path, "TASK-9999") is False
    # A task referenced only by its own (non-BLOCKED) file does not count.
    assert task_unblocks_others(tmp_path, "TASK-3001") is False


def test_classify_full_repo_signal_ok_for_fresh_success() -> None:
    now = datetime(2026, 6, 11, 12, 0, 0, tzinfo=timezone.utc)
    assert (
        classify_full_repo_signal("success", "2026-06-11T10:00:00Z", now=now) == "ok"
    )


def test_classify_full_repo_signal_red_for_failure() -> None:
    now = datetime(2026, 6, 11, 12, 0, 0, tzinfo=timezone.utc)
    assert (
        classify_full_repo_signal("failure", "2026-06-11T10:00:00Z", now=now) == "red"
    )
    assert (
        classify_full_repo_signal("cancelled", "2026-06-11T10:00:00Z", now=now)
        == "red"
    )


def test_classify_full_repo_signal_stale_when_too_old() -> None:
    now = datetime(2026, 6, 11, 12, 0, 0, tzinfo=timezone.utc)
    assert (
        classify_full_repo_signal("success", "2026-06-08T10:00:00Z", now=now)
        == "stale"
    )
    # A custom freshness window is honored.
    assert (
        classify_full_repo_signal(
            "success", "2026-06-11T08:00:00Z", now=now, max_age_hours=1.0
        )
        == "stale"
    )


def test_classify_full_repo_signal_unknown_for_missing_or_bad_fields() -> None:
    now = datetime(2026, 6, 11, 12, 0, 0, tzinfo=timezone.utc)
    assert classify_full_repo_signal(None, "2026-06-11T10:00:00Z", now=now) == "unknown"
    assert classify_full_repo_signal("", "2026-06-11T10:00:00Z", now=now) == "unknown"
    assert classify_full_repo_signal("success", None, now=now) == "unknown"
    assert classify_full_repo_signal("success", "not-a-date", now=now) == "unknown"
