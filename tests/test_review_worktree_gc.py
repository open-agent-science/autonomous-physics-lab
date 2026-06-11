"""Regression tests for review-worktree GC (TASK-0724).

Covers the conservative cleanup contract: dry-run deletes nothing, only detached
review worktrees older than the TTL are reclaimed, a branch-checked-out review
worktree and a normal task worktree are never touched, and a review run's own
worktree is torn down regardless of age.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import time

import pytest

from physics_lab.registry.review_worktree_gc import (
    gc_review_worktrees,
    list_review_worktrees,
    review_worktree_disk_report,
    review_worktrees_root,
    teardown_own_worktree,
)


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    if shutil.which("git") is None:
        pytest.skip("git is required for review-worktree GC tests")
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test Runner")
    (root / ".gitignore").write_text(".worktrees/\n", encoding="utf-8")
    _git(root, "add", ".gitignore")
    _git(root, "commit", "-m", "init")
    return root


def _head_sha(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _add_detached_review_worktree(repo: Path, name: str) -> Path:
    path = review_worktrees_root(repo) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    _git(repo, "worktree", "add", "--detach", str(path), _head_sha(repo))
    return path


def _add_branch_review_worktree(repo: Path, name: str, branch: str) -> Path:
    path = review_worktrees_root(repo) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    _git(repo, "worktree", "add", "-b", branch, str(path), "main")
    return path


def _backdate(path: Path, hours: float) -> None:
    old = time.time() - hours * 3600.0
    os.utime(path, (old, old))


def test_list_only_sees_review_worktrees(repo: Path) -> None:
    review = _add_detached_review_worktree(repo, "pr-1-aaaaaaaaaaaa")
    task = repo / ".worktrees" / "task-x"
    task.parent.mkdir(parents=True, exist_ok=True)
    _git(repo, "worktree", "add", "--detach", str(task), _head_sha(repo))

    listed = {wt.path.resolve() for wt in list_review_worktrees(repo)}

    assert review.resolve() in listed
    assert task.resolve() not in listed


def test_dry_run_removes_nothing(repo: Path) -> None:
    path = _add_detached_review_worktree(repo, "pr-1-aaaaaaaaaaaa")
    _backdate(path, hours=100)

    report = gc_review_worktrees(repo, older_than_hours=48, dry_run=True)

    assert path.exists()
    assert report.removed == ()
    assert any(o.reason == "dry_run" for o in report.skipped)


def test_age_filter_keeps_recent_removes_old(repo: Path) -> None:
    old = _add_detached_review_worktree(repo, "pr-1-old000000000")
    recent = _add_detached_review_worktree(repo, "pr-2-recent000000")
    _backdate(old, hours=100)
    _backdate(recent, hours=1)

    report = gc_review_worktrees(repo, older_than_hours=48)

    assert not old.exists()
    assert recent.exists()
    removed_paths = {o.path.resolve() for o in report.removed}
    assert old.resolve() in removed_paths
    assert recent.resolve() not in removed_paths


def test_branch_checked_out_review_worktree_is_never_removed(repo: Path) -> None:
    branch_wt = _add_branch_review_worktree(repo, "pr-3-branch000000", "review-branch")
    _backdate(branch_wt, hours=1000)

    report = gc_review_worktrees(repo, older_than_hours=48)

    assert branch_wt.exists()
    assert any(o.reason == "branch_checked_out" for o in report.skipped)


def test_normal_task_worktree_is_never_listed_or_removed(repo: Path) -> None:
    task = repo / ".worktrees" / "task-y"
    task.parent.mkdir(parents=True, exist_ok=True)
    _git(repo, "worktree", "add", "--detach", str(task), _head_sha(repo))
    _backdate(task, hours=1000)

    gc_review_worktrees(repo, older_than_hours=48)

    assert task.exists()


def test_teardown_own_worktree_removes_regardless_of_age(repo: Path) -> None:
    path = _add_detached_review_worktree(repo, "pr-4-own000000000")
    # Freshly created (age ~0) but the current run owns it, so it must go.

    outcome = teardown_own_worktree(repo, path)

    assert outcome.removed
    assert not path.exists()


def test_teardown_refuses_branch_worktree(repo: Path) -> None:
    branch_wt = _add_branch_review_worktree(repo, "pr-5-branch000000", "owned-branch")

    outcome = teardown_own_worktree(repo, branch_wt)

    assert not outcome.removed
    assert outcome.reason == "branch_checked_out"
    assert branch_wt.exists()


def test_teardown_refuses_non_review_path(repo: Path) -> None:
    task = repo / ".worktrees" / "task-z"
    task.parent.mkdir(parents=True, exist_ok=True)
    _git(repo, "worktree", "add", "--detach", str(task), _head_sha(repo))

    outcome = teardown_own_worktree(repo, task)

    assert not outcome.removed
    assert outcome.reason == "not_review_worktree"
    assert task.exists()


def test_keep_paths_protects_specific_worktree(repo: Path) -> None:
    keep = _add_detached_review_worktree(repo, "pr-6-keep00000000")
    drop = _add_detached_review_worktree(repo, "pr-7-drop00000000")
    _backdate(keep, hours=100)
    _backdate(drop, hours=100)

    gc_review_worktrees(repo, older_than_hours=48, keep_paths=(keep,))

    assert keep.exists()
    assert not drop.exists()


def test_disk_report_recommends_gc_on_buildup(repo: Path) -> None:
    _add_detached_review_worktree(repo, "pr-8-buildup00000")

    report = review_worktree_disk_report(repo, count_threshold=1)

    assert report.review_worktree_count >= 1
    assert report.recommend_gc
    assert report.reasons


def test_disk_report_quiet_when_no_buildup(repo: Path) -> None:
    report = review_worktree_disk_report(repo, count_threshold=5)

    assert report.review_worktree_count == 0
    assert not report.recommend_gc
