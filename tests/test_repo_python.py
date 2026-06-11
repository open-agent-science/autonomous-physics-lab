"""Tests for the repository-venv interpreter resolver (TASK-0725)."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from physics_lab.registry.repo_python import (
    find_repo_python,
    resolve_validation_python,
    venv_python_candidates,
)

# A non-".git" sentinel keeps find_repo_python from shelling out to git in the
# hermetic unit tests; only the real-worktree test exercises git discovery.
NO_COMMON_DIR = Path("/__no_common_dir__")


def _make_venv_python(base: Path) -> Path:
    """Create a fake venv interpreter for the current platform under ``base``."""
    if sys.platform.startswith("win"):
        target = base / ".venv" / "Scripts" / "python.exe"
    else:
        target = base / ".venv" / "bin" / "python"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("", encoding="utf-8")
    return target


def test_candidates_cover_both_platforms(tmp_path: Path) -> None:
    candidates = venv_python_candidates(tmp_path)
    names = {c.name for c in candidates}
    assert names == {"python.exe", "python"}


def test_find_repo_python_in_checkout(tmp_path: Path) -> None:
    target = _make_venv_python(tmp_path)

    found = find_repo_python(tmp_path, git_common_dir=NO_COMMON_DIR)

    assert found == target.resolve()


def test_find_repo_python_returns_none_without_venv(tmp_path: Path) -> None:
    assert find_repo_python(tmp_path, git_common_dir=NO_COMMON_DIR) is None


def test_find_repo_python_worktree_common_dir_fallback(tmp_path: Path) -> None:
    main = tmp_path / "main"
    main.mkdir()
    target = _make_venv_python(main)
    worktree = tmp_path / "wt"
    worktree.mkdir()
    common_dir = main / ".git"
    common_dir.mkdir()

    # The worktree has no venv of its own; discovery falls back to the main
    # checkout that owns the shared .git directory.
    found = find_repo_python(worktree, git_common_dir=common_dir)

    assert found == target.resolve()


def test_resolve_validation_python_falls_back_to_sys_executable(tmp_path: Path) -> None:
    assert resolve_validation_python(tmp_path, git_common_dir=NO_COMMON_DIR) == sys.executable


def test_resolve_validation_python_prefers_repo_venv(tmp_path: Path) -> None:
    target = _make_venv_python(tmp_path)

    resolved = resolve_validation_python(tmp_path, git_common_dir=NO_COMMON_DIR)

    assert resolved == str(target.resolve())
    assert resolved != sys.executable


def test_find_repo_python_resolves_from_real_worktree(tmp_path: Path) -> None:
    if shutil.which("git") is None:  # pragma: no cover - environment guard
        pytest.skip("git is required for the real-worktree discovery test")

    def _git(repo: Path, *args: str) -> None:
        subprocess.run(
            ["git", *args], cwd=repo, check=True, capture_output=True, text=True
        )

    main = tmp_path / "main"
    main.mkdir()
    _git(main, "init", "-b", "main")
    _git(main, "config", "user.email", "test@example.com")
    _git(main, "config", "user.name", "Test Runner")
    (main / ".gitignore").write_text(".venv/\n.worktrees/\n", encoding="utf-8")
    _git(main, "add", ".gitignore")
    _git(main, "commit", "-m", "init")
    target = _make_venv_python(main)
    worktree = main / ".worktrees" / "wt"
    worktree.parent.mkdir(parents=True, exist_ok=True)
    _git(main, "worktree", "add", "--detach", str(worktree), "HEAD")

    # No explicit common dir: the resolver shells out to git from the worktree.
    found = find_repo_python(worktree)

    assert found == target.resolve()
