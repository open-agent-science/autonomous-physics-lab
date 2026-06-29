"""Tests for the validate-repo --auto-sync flag (TASK-0262)."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from physics_lab.cli import app
from physics_lab.registry.repository import (
    RepositoryValidationSummary,
    ValidationIssue,
)


def _empty_summary(root: Path) -> RepositoryValidationSummary:
    """Build a passing summary with no issues."""
    return RepositoryValidationSummary(
        root=root,
        counts={},
        strict=True,
        issues=(),
    )


def _stale_summary(root: Path) -> RepositoryValidationSummary:
    """Build a strict failing summary mimicking a stale board."""
    return RepositoryValidationSummary(
        root=root,
        counts={},
        strict=True,
        issues=(
            ValidationIssue(
                severity="ERROR",
                code="stale_active_board",
                message="tasks/ACTIVE.md is stale; run sync-active-board.",
                path="tasks/ACTIVE.md",
            ),
        ),
    )


# ── Default behaviour (no --auto-sync) ────────────────────────────────────


def test_validate_repo_default_does_not_call_sync(tmp_path: Path) -> None:
    """Without --auto-sync, sync_generated_task_state must not be called."""
    runner = CliRunner()
    with patch(
        "physics_lab.cli.sync_generated_task_state"
    ) as sync_mock, patch(
        "physics_lab.cli.validate_repository",
        return_value=_empty_summary(tmp_path),
    ):
        result = runner.invoke(app, ["validate-repo", str(tmp_path)])

    assert result.exit_code == 0
    sync_mock.assert_not_called()
    assert "Auto-synced" not in result.stdout


def test_validate_repo_default_strict_fails_on_stale_summary(tmp_path: Path) -> None:
    """Default --strict still surfaces stale_active_board errors."""
    runner = CliRunner()
    with patch(
        "physics_lab.cli.sync_generated_task_state"
    ) as sync_mock, patch(
        "physics_lab.cli.validate_repository",
        return_value=_stale_summary(tmp_path),
    ):
        result = runner.invoke(app, ["validate-repo", str(tmp_path), "--strict"])

    assert result.exit_code == 1
    sync_mock.assert_not_called()
    assert "stale_active_board" in result.stdout
    assert "Strict validation: FAIL" in result.stdout


# ── --auto-sync wires the sync call in ───────────────────────────────────


def test_auto_sync_calls_sync_before_validation(tmp_path: Path) -> None:
    """With --auto-sync the sync helper must run, then validate_repository."""
    call_order: list[str] = []

    def fake_sync(root: Path) -> list[Path]:
        call_order.append("sync")
        return [tmp_path / "tasks" / "ACTIVE.md"]

    def fake_validate(root: Path, **_: Any) -> RepositoryValidationSummary:
        call_order.append("validate")
        return _empty_summary(tmp_path)

    runner = CliRunner()
    with patch("physics_lab.cli.sync_generated_task_state", side_effect=fake_sync), patch(
        "physics_lab.cli.validate_repository", side_effect=fake_validate
    ):
        result = runner.invoke(
            app, ["validate-repo", str(tmp_path), "--strict", "--auto-sync"]
        )

    assert result.exit_code == 0
    assert call_order == ["sync", "validate"]
    assert "Auto-synced generated task navigation:" in result.stdout
    assert "tasks/ACTIVE.md" in result.stdout


def test_auto_sync_no_op_when_sync_returns_nothing(tmp_path: Path) -> None:
    """If sync produces no paths the header line should be skipped."""
    runner = CliRunner()
    with patch(
        "physics_lab.cli.sync_generated_task_state", return_value=[]
    ) as sync_mock, patch(
        "physics_lab.cli.validate_repository",
        return_value=_empty_summary(tmp_path),
    ):
        result = runner.invoke(
            app, ["validate-repo", str(tmp_path), "--auto-sync"]
        )

    assert result.exit_code == 0
    sync_mock.assert_called_once()
    assert "Auto-synced" not in result.stdout


def test_auto_sync_works_without_strict(tmp_path: Path) -> None:
    """--auto-sync does not require --strict."""
    runner = CliRunner()
    with patch(
        "physics_lab.cli.sync_generated_task_state",
        return_value=[tmp_path / "tasks" / "ACTIVE.md"],
    ) as sync_mock, patch(
        "physics_lab.cli.validate_repository",
        return_value=_empty_summary(tmp_path),
    ):
        result = runner.invoke(
            app, ["validate-repo", str(tmp_path), "--auto-sync"]
        )

    assert result.exit_code == 0
    sync_mock.assert_called_once()


def test_auto_sync_with_strict_and_fail_on_warnings_succeeds(tmp_path: Path) -> None:
    """All three flags compose without breaking the sync-then-validate flow."""
    runner = CliRunner()
    with patch(
        "physics_lab.cli.sync_generated_task_state",
        return_value=[tmp_path / "tasks" / "ACTIVE.md"],
    ), patch(
        "physics_lab.cli.validate_repository",
        return_value=_empty_summary(tmp_path),
    ):
        result = runner.invoke(
            app,
            [
                "validate-repo",
                str(tmp_path),
                "--strict",
                "--fail-on-warnings",
                "--auto-sync",
            ],
        )

    assert result.exit_code == 0
    assert "Strict validation: PASS" in result.stdout


def test_fail_on_warnings_still_requires_strict_even_with_auto_sync() -> None:
    """The pre-existing constraint between --fail-on-warnings and --strict must hold.

    Typer raises BadParameter for this case; the runner returns a non-zero
    exit code via SystemExit. The error message is written to stderr which
    CliRunner does not capture by default, so verifying the exit code is
    sufficient.
    """
    runner = CliRunner()
    with patch("physics_lab.cli.sync_generated_task_state") as sync_mock, patch(
        "physics_lab.cli.validate_repository"
    ) as validate_mock:
        result = runner.invoke(
            app, ["validate-repo", ".", "--fail-on-warnings", "--auto-sync"]
        )

    assert result.exit_code != 0
    sync_mock.assert_not_called()
    validate_mock.assert_not_called()


def test_sync_active_board_workflow_uses_app_direct_push_guardrails() -> None:
    """Post-merge board sync should use the narrow App direct-push architecture."""
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "sync-active-board.yml"
    ).read_text(encoding="utf-8")

    assert "actions/create-github-app-token@v3" in workflow
    assert "permission-contents: write" in workflow
    assert "permission-pull-requests: write" not in workflow
    assert "pull-requests: read" in workflow
    assert "persist-credentials: false" in workflow
    assert "unexpected_paths" in workflow
    assert "docs/task-views/*.md|tasks/TASK-*.yaml" in workflow
    assert "git push origin HEAD:main" in workflow
    assert "gh pr create" not in workflow


# ── Live smoke (real repo, must remain green) ─────────────────────────────


@pytest.mark.full_repo
def test_cli_validate_repo_auto_sync_live_smoke() -> None:
    """Real-repo smoke: passing --auto-sync on a healthy state still passes.

    --auto-sync regenerates the tracked task views (docs/task-views/*.md). On a
    branch whose task YAML changed, that regeneration differs from the committed
    content and would otherwise leave the working tree dirty, which then blocks
    the review tool. The smoke test only needs to confirm the command runs and
    passes, so it snapshots and restores those views instead of persisting the
    regeneration. See TASK-0466 (F2) and TASK-0473 (ACTIVE.md retirement).
    """
    repo_root = Path(__file__).resolve().parents[1]
    board_files = sorted((repo_root / "docs" / "task-views").glob("*.md"))
    original = {p: p.read_text(encoding="utf-8") for p in board_files if p.exists()}

    runner = CliRunner()
    try:
        result = runner.invoke(app, ["validate-repo", ".", "--strict", "--auto-sync"])

        if result.exit_code != 0:
            pytest.fail(f"validate-repo --strict --auto-sync failed: {result.stdout}")
        assert "Strict validation: PASS" in result.stdout
    finally:
        for path, text in original.items():
            if path.read_text(encoding="utf-8") != text:
                path.write_text(text, encoding="utf-8")
