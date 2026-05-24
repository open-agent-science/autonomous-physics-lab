"""Tests for the staleness-severity behavior of validate-repo (TASK-0358).

The post-merge Sync Active Board GitHub Action regenerates
``tasks/ACTIVE.md`` and ``docs/task-views/*.md`` automatically on
``main``. Agent PR branches therefore do not need to commit those
regenerated files. To keep ``validate-repo --strict --fail-on-warnings``
green on agent branches, the staleness checks for those generated
files emit ``INFO`` by default. Setting
``APL_ENFORCE_BOARD_STALENESS=1`` restores the historical ``ERROR``
severity for explicit maintainer audits.

Missing files (the file is gone entirely, not just stale) remain
``ERROR`` regardless of the env var because a missing generated file is
a real bug, not a normal post-merge state.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from unittest.mock import patch


import pytest

from physics_lab.registry import repository as repository_module
from physics_lab.registry.repository import (
    BOARD_STALENESS_ENV_VAR,
    _board_staleness_severity,
    _strict_generated_task_navigation_issues,
)
from physics_lab.registry.task_views import TASK_VIEW_PATHS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_active_board(repo: Path, body: str = "stale-content") -> Path:
    tasks_dir = repo / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    path = tasks_dir / "ACTIVE.md"
    path.write_text(body, encoding="utf-8")
    return path


def _write_task_view(repo: Path, relpath: str, body: str = "stale-view") -> Path:
    target = repo / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target


# ---------------------------------------------------------------------------
# _board_staleness_severity
# ---------------------------------------------------------------------------


class TestBoardStalenessSeverity:
    def test_default_severity_is_info(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(BOARD_STALENESS_ENV_VAR, raising=False)
        assert _board_staleness_severity() == "INFO"

    def test_enforced_via_env_var_returns_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(BOARD_STALENESS_ENV_VAR, "1")
        assert _board_staleness_severity() == "ERROR"

    def test_env_var_value_other_than_one_does_not_enforce(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        for value in ("0", "true", "yes", "ERROR", ""):
            monkeypatch.setenv(BOARD_STALENESS_ENV_VAR, value)
            assert (
                _board_staleness_severity() == "INFO"
            ), f"env value {value!r} unexpectedly enforced"

    def test_env_var_name_is_documented_constant(self) -> None:
        # Catch accidental rename of the env var that would silently
        # break callers and the GitHub Action contract.
        assert BOARD_STALENESS_ENV_VAR == "APL_ENFORCE_BOARD_STALENESS"


# ---------------------------------------------------------------------------
# _strict_generated_task_navigation_issues
# ---------------------------------------------------------------------------


class TestStalenessIssuesUseConfiguredSeverity:
    def test_stale_active_board_is_info_by_default(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.delenv(BOARD_STALENESS_ENV_VAR, raising=False)
        _write_active_board(tmp_path, body="not-in-sync-content")

        # active_board_is_synced reads canonical task files; we override it
        # via patch to simulate a stale state without building a full fixture
        # repository.
        with patch(
            "physics_lab.registry.repository.active_board_is_synced",
            return_value=False,
        ):
            issues = _strict_generated_task_navigation_issues(tmp_path)

        stale_issues = [issue for issue in issues if issue.code == "stale_active_board"]
        assert len(stale_issues) == 1
        assert stale_issues[0].severity == "INFO"
        assert "sync-active-board" in stale_issues[0].message.lower()

    def test_stale_active_board_is_error_when_enforced(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv(BOARD_STALENESS_ENV_VAR, "1")
        _write_active_board(tmp_path, body="not-in-sync-content")

        with patch(
            "physics_lab.registry.repository.active_board_is_synced",
            return_value=False,
        ):
            issues = _strict_generated_task_navigation_issues(tmp_path)

        stale_issues = [issue for issue in issues if issue.code == "stale_active_board"]
        assert len(stale_issues) == 1
        assert stale_issues[0].severity == "ERROR"

    def test_missing_active_board_stays_error_regardless_of_env(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A missing tasks/ACTIVE.md is a real bug; the env var must not
        downgrade it. The function still needs at least one generated task
        view to trigger its main path, so we create one to keep the
        early-return guard out of the way."""

        # Add at least one task view so the early-return guard does not fire.
        any_view = next(iter(TASK_VIEW_PATHS.values()))
        _write_task_view(tmp_path, any_view, body="placeholder")

        monkeypatch.delenv(BOARD_STALENESS_ENV_VAR, raising=False)
        with patch(
            "physics_lab.registry.repository.render_task_views",
            return_value={lane: "placeholder" for lane in TASK_VIEW_PATHS},
        ):
            issues_default = _strict_generated_task_navigation_issues(tmp_path)

        monkeypatch.setenv(BOARD_STALENESS_ENV_VAR, "1")
        with patch(
            "physics_lab.registry.repository.render_task_views",
            return_value={lane: "placeholder" for lane in TASK_VIEW_PATHS},
        ):
            issues_enforced = _strict_generated_task_navigation_issues(tmp_path)

        for issues in (issues_default, issues_enforced):
            missing = [issue for issue in issues if issue.code == "missing_active_board"]
            assert len(missing) == 1
            assert missing[0].severity == "ERROR"

    def test_stale_generated_task_view_severity_tracks_env(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _write_active_board(tmp_path, body="placeholder")
        any_view_relpath = next(iter(TASK_VIEW_PATHS.values()))
        any_view_lane = next(iter(TASK_VIEW_PATHS))
        _write_task_view(tmp_path, any_view_relpath, body="actual-content")

        rendered = {lane: "expected-content" for lane in TASK_VIEW_PATHS}
        # Make every view stale by having actual != expected.

        with patch(
            "physics_lab.registry.repository.active_board_is_synced",
            return_value=True,
        ), patch(
            "physics_lab.registry.repository.render_task_views",
            return_value=rendered,
        ):
            monkeypatch.delenv(BOARD_STALENESS_ENV_VAR, raising=False)
            default_issues = _strict_generated_task_navigation_issues(tmp_path)

            monkeypatch.setenv(BOARD_STALENESS_ENV_VAR, "1")
            enforced_issues = _strict_generated_task_navigation_issues(tmp_path)

        default_stale = [
            issue
            for issue in default_issues
            if issue.code == "stale_generated_task_view"
            and any_view_lane in issue.message
        ]
        enforced_stale = [
            issue
            for issue in enforced_issues
            if issue.code == "stale_generated_task_view"
            and any_view_lane in issue.message
        ]

        assert len(default_stale) == 1
        assert default_stale[0].severity == "INFO"
        assert "sync-active-board" in default_stale[0].message.lower()

        assert len(enforced_stale) == 1
        assert enforced_stale[0].severity == "ERROR"

    def test_missing_generated_task_view_stays_error(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _write_active_board(tmp_path, body="placeholder")
        any_view_relpath = next(iter(TASK_VIEW_PATHS.values()))
        other_view_relpath = list(TASK_VIEW_PATHS.values())[1]
        # Provide ONE view file so any_task_views_exist is True, then leave
        # the other missing so the missing branch fires.
        _write_task_view(tmp_path, any_view_relpath, body="placeholder")

        rendered = {lane: "placeholder" for lane in TASK_VIEW_PATHS}
        with patch(
            "physics_lab.registry.repository.active_board_is_synced",
            return_value=True,
        ), patch(
            "physics_lab.registry.repository.render_task_views",
            return_value=rendered,
        ):
            monkeypatch.delenv(BOARD_STALENESS_ENV_VAR, raising=False)
            issues_default = _strict_generated_task_navigation_issues(tmp_path)

            monkeypatch.setenv(BOARD_STALENESS_ENV_VAR, "1")
            issues_enforced = _strict_generated_task_navigation_issues(tmp_path)

        for issues in (issues_default, issues_enforced):
            missing = [
                issue
                for issue in issues
                if issue.code == "missing_generated_task_view"
                and other_view_relpath in str(issue.path)
            ]
            assert len(missing) == 1, missing
            assert missing[0].severity == "ERROR"


# ---------------------------------------------------------------------------
# Smoke check: env var name is also documented in repository module exports
# ---------------------------------------------------------------------------


def test_env_var_constant_is_exported_for_external_callers() -> None:
    """The env var name is part of the public protocol. Catch accidental
    renames at import time."""
    assert hasattr(repository_module, "BOARD_STALENESS_ENV_VAR")
    importlib.reload(repository_module)
    assert repository_module.BOARD_STALENESS_ENV_VAR == "APL_ENFORCE_BOARD_STALENESS"
