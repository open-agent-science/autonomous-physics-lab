"""Tests for review git safe-directory handling."""

from __future__ import annotations

from pathlib import Path

from physics_lab.registry.review_git import git_safe_directory_flags


def test_git_safe_directory_flags_include_repo_and_worktree() -> None:
    repo = Path("/tmp/apl-main")
    worktree = Path("/tmp/apl-main/.worktrees/_reviews/pr-1234")

    flags = git_safe_directory_flags(repo, worktree)

    assert flags == [
        "-c",
        f"safe.directory={repo.resolve()}",
        "-c",
        f"safe.directory={worktree.resolve()}",
    ]


def test_git_safe_directory_flags_deduplicate_paths() -> None:
    repo = Path("/tmp/apl-main")

    flags = git_safe_directory_flags(repo, repo)

    assert flags == ["-c", f"safe.directory={repo.resolve()}"]
