from __future__ import annotations

from pathlib import Path

from unittest.mock import patch

from physics_lab.registry.maintainer_review import PullRequestMetadata, build_closeout_report as build_apply_closeout_report
from physics_lab.registry.task_closeout import build_closeout_report, render_closeout_report


def _write_task(
    root: Path,
    *,
    task_id: str,
    status: str,
    task_type: str = "documentation",
    requirements: tuple[str, ...] = ("Keep output deterministic",),
) -> None:
    (root / "tasks").mkdir(parents=True, exist_ok=True)
    rendered_requirements = "\n".join(f'  - "{item}"' for item in requirements)
    (root / "tasks" / f"{task_id}-example.yaml").write_text(
        "\n".join(
            [
                f"id: {task_id}",
                'title: "Example task"',
                f"type: {task_type}",
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
                rendered_requirements,
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

    report = build_closeout_report(tmp_path, "TASK-1234")

    assert report.task_file.name == "TASK-1234-example.yaml"
    assert report.status == "REVIEW_READY"
    assert report.accepted_outputs == ("docs/example.md", "tasks/ACTIVE.md")
    assert report.warnings == ()
    assert any("sync-active-board" in item for item in report.suggested_actions)
    assert any("Closeout publish reminder" in item for item in report.suggested_actions)


def test_build_closeout_report_warns_missing_result_policy_for_non_exempt_type(
    tmp_path: Path,
) -> None:
    # A non-exempt type with no result/PRED link and no policy must surface the
    # shift-left advisory before DONE (TASK-0727).
    _write_task(
        tmp_path,
        task_id="TASK-2727",
        status="REVIEW_READY",
        task_type="tooling_reliability",
    )

    report = build_closeout_report(tmp_path, "TASK-2727")

    assert any("result_artifact_policy" in item for item in report.warnings)


def test_build_closeout_report_no_policy_warning_for_exempt_type(tmp_path: Path) -> None:
    # documentation is on the no-result exemption list -> no policy advisory.
    _write_task(
        tmp_path,
        task_id="TASK-2728",
        status="REVIEW_READY",
        task_type="documentation",
    )

    report = build_closeout_report(tmp_path, "TASK-2728")

    assert not any("result_artifact_policy" in item for item in report.warnings)


def test_build_closeout_report_warns_when_not_review_ready(tmp_path: Path) -> None:
    _write_task(tmp_path, task_id="TASK-5678", status="DONE")

    report = build_closeout_report(tmp_path, "TASK-5678")
    rendered = render_closeout_report(report, suggest=True, root=tmp_path)

    assert "Task status is DONE, not REVIEW_READY." in report.warnings[0]
    assert "Suggested file updates (not applied):" in rendered
    assert "No direct file update is suggested until the task reaches REVIEW_READY" in rendered


def test_build_closeout_report_suggests_public_state_docs_for_science_task(
    tmp_path: Path,
) -> None:
    _write_task(tmp_path, task_id="TASK-9012", status="REVIEW_READY")
    task_path = tmp_path / "tasks" / "TASK-9012-example.yaml"
    text = task_path.read_text(encoding="utf-8")
    task_path.write_text(
        text.replace("type: documentation", "type: scientific_validation").replace(
            "related_domain: maintainer_review",
            "related_domain: nuclear_physics",
        ),
        encoding="utf-8",
    )
    (tmp_path / "tasks" / "ACTIVE.md").write_text(
        "\n".join(
            [
                "# Active Task Board",
                "",
                "## REVIEW_READY",
                "",
                "- `TASK-9012` — Example science task",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = build_closeout_report(tmp_path, "TASK-9012")

    assert any("Public docs drift checklist" in item for item in report.suggested_actions)
    assert any("docs/status.md" in item for item in report.suggested_actions)
    assert any("docs/mission-control.md" in item for item in report.suggested_actions)
    assert any("README.md" in item for item in report.suggested_actions)
    assert any("docs/next-steps.md" in item for item in report.suggested_actions)
    assert any("Closeout docs-sync policy" in item for item in report.suggested_actions)


def test_apply_closeout_report_safely_unblocks_explicit_done_dependencies(
    tmp_path: Path,
) -> None:
    _write_task(tmp_path, task_id="TASK-1234", status="REVIEW_READY")
    _write_task(tmp_path, task_id="TASK-1235", status="DONE")
    _write_task(
        tmp_path,
        task_id="TASK-1236",
        status="BLOCKED",
        requirements=(
            "Remain BLOCKED until TASK-1234 and TASK-1235 are DONE, "
            "or until the maintainer explicitly authorizes a manual unblock.",
        ),
    )
    _write_task(
        tmp_path,
        task_id="TASK-1237",
        status="BLOCKED",
        requirements=("Remain BLOCKED until TASK-1234 is DONE and a source artifact exists.",),
    )
    (tmp_path / "tasks" / "ACTIVE.md").write_text("# Active Task Board\n", encoding="utf-8")
    (tmp_path / "docs").mkdir(parents=True)
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
        changed_files=(),
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

    unblocked = tmp_path / "tasks" / "TASK-1236-example.yaml"
    still_blocked = tmp_path / "tasks" / "TASK-1237-example.yaml"
    assert report.outcome == "APPLIED"
    assert "status: READY" in unblocked.read_text(encoding="utf-8")
    assert "status: BLOCKED" in still_blocked.read_text(encoding="utf-8")
    assert any("Safely unblocked" in item and "TASK-1236" in item for item in report.applied_changes)


def test_closeout_report_suggests_safe_unblocks_without_applying(tmp_path: Path) -> None:
    _write_task(tmp_path, task_id="TASK-1234", status="DONE")
    _write_task(
        tmp_path,
        task_id="TASK-1235",
        status="BLOCKED",
        requirements=("Remain BLOCKED until TASK-1234 is DONE.",),
    )
    (tmp_path / "tasks" / "ACTIVE.md").write_text("# Active Task Board\n", encoding="utf-8")
    (tmp_path / "docs").mkdir(parents=True)
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
        changed_files=(),
    )

    with (
        patch("physics_lab.registry.maintainer_review.current_branch", return_value="main"),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=pr_metadata),
        patch("physics_lab.registry.maintainer_review.missing_expected_outputs", return_value=()),
    ):
        report = build_apply_closeout_report(
            tmp_path,
            task_id="TASK-1234",
            pull_request=18,
            apply=False,
        )

    assert any("Safe unblock candidate: TASK-1235" in item for item in report.suggested_actions)
    assert "status: BLOCKED" in (tmp_path / "tasks" / "TASK-1235-example.yaml").read_text(
        encoding="utf-8"
    )


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
        changed_files=(),
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
    assert any("Deferred generated task navigation sync" in item for item in report.applied_changes)
    assert not any("Synchronized generated task navigation" in item for item in report.applied_changes)
    assert any("Closeout publish reminder" in item for item in report.suggested_actions)


def test_apply_closeout_report_suggests_regenerating_context_bundle_for_source_changes(
    tmp_path: Path,
) -> None:
    _write_task(tmp_path, task_id="TASK-1234", status="REVIEW_READY")
    (tmp_path / "tasks" / "ACTIVE.md").write_text("# Active Task Board\n", encoding="utf-8")
    (tmp_path / "docs").mkdir(parents=True)
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
        changed_files=("docs/strategy.md",),
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

    assert any("Regenerate CONTEXT.md" in item for item in report.suggested_actions)


def test_apply_closeout_report_suggests_public_state_doc_review_for_result_changes(
    tmp_path: Path,
) -> None:
    _write_task(tmp_path, task_id="TASK-1234", status="REVIEW_READY")
    (tmp_path / "tasks" / "ACTIVE.md").write_text("# Active Task Board\n", encoding="utf-8")
    (tmp_path / "docs").mkdir(parents=True)
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
        changed_files=("results/EXP-0012/RUN-0001/result.yaml",),
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
            apply=False,
        )

    assert any("docs/status.md" in item for item in report.suggested_actions)
    assert any("docs/mission-control.md" in item for item in report.suggested_actions)
    assert any("README.md" in item for item in report.suggested_actions)
    assert any("docs/next-steps.md" in item for item in report.suggested_actions)
    assert any("Closeout docs-sync policy" in item for item in report.suggested_actions)
