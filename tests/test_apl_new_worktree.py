from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "apl_new_worktree.sh"


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def git_repo_with_helper(tmp_path: Path) -> Path:
    if shutil.which("bash") is None:
        pytest.skip("bash is required to exercise apl_new_worktree.sh")

    repo = tmp_path / "repo"
    repo.mkdir()
    _run(["git", "init", "-b", "main"], repo)
    _run(["git", "config", "user.email", "test@example.com"], repo)
    _run(["git", "config", "user.name", "Test Runner"], repo)

    (repo / ".gitignore").write_text(".worktrees/\n", encoding="utf-8")
    scripts = repo / "scripts"
    scripts.mkdir()
    shutil.copy2(SCRIPT_PATH, scripts / "apl_new_worktree.sh")
    _run(["git", "add", ".gitignore", "scripts/apl_new_worktree.sh"], repo)
    _run(["git", "commit", "-m", "init"], repo)
    return repo


def test_new_worktree_defaults_inside_gitignored_worktrees_dir(
    git_repo_with_helper: Path,
) -> None:
    branch = "agent/roman/codex/task-0271-default-path"

    result = _run(["bash", "scripts/apl_new_worktree.sh", branch], git_repo_with_helper)

    expected_path = ".worktrees/agent_roman_codex_task-0271-default-path"
    assert f"path:   {expected_path}" in result.stdout
    assert (git_repo_with_helper / expected_path / ".git").exists()
    status = _run(["git", "status", "--short"], git_repo_with_helper)
    assert status.stdout == ""


def test_new_worktree_explicit_path_still_overrides_default(
    git_repo_with_helper: Path,
    tmp_path: Path,
) -> None:
    branch = "agent/roman/codex/task-0271-explicit-path"
    explicit_path = tmp_path / "outside-worktree"

    result = _run(
        ["bash", "scripts/apl_new_worktree.sh", branch, str(explicit_path)],
        git_repo_with_helper,
    )

    assert f"path:   {explicit_path}" in result.stdout
    assert (explicit_path / ".git").exists()
    assert not (
        git_repo_with_helper
        / ".worktrees"
        / "agent_roman_codex_task-0271-explicit-path"
    ).exists()
