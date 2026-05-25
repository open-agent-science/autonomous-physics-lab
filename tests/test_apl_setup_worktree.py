from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "apl_setup_worktree.sh"


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def git_repo_with_setup_helper(tmp_path: Path) -> Path:
    if shutil.which("bash") is None:
        pytest.skip("bash is required to exercise apl_setup_worktree.sh")

    repo = tmp_path / "repo"
    repo.mkdir()
    _run(["git", "init", "-b", "main"], repo)
    _run(["git", "config", "user.email", "test@example.com"], repo)
    _run(["git", "config", "user.name", "Test Runner"], repo)

    scripts = repo / "scripts"
    scripts.mkdir()
    shutil.copy2(SCRIPT_PATH, scripts / "apl_setup_worktree.sh")
    _run(["git", "add", "scripts/apl_setup_worktree.sh"], repo)
    _run(["git", "commit", "-m", "init"], repo)
    return repo


def test_setup_worktree_is_noop_without_local_claude_settings(
    git_repo_with_setup_helper: Path,
) -> None:
    result = _run(["bash", "scripts/apl_setup_worktree.sh"], git_repo_with_setup_helper)

    assert result.returncode == 0
    assert "Optional source not found:" in result.stdout
    assert "continuing without worktree-local settings" in result.stdout


def test_setup_worktree_copies_local_claude_settings_when_available(
    git_repo_with_setup_helper: Path,
    tmp_path: Path,
) -> None:
    source_settings = git_repo_with_setup_helper / ".claude" / "settings.local.json"
    source_settings.parent.mkdir()
    source_settings.write_text('{"permissions":{"allow":["Bash(echo *)"]}}\n', encoding="utf-8")
    worktree_path = tmp_path / "task-worktree"
    _run(
        ["git", "worktree", "add", "-b", "agent/test/setup-helper", str(worktree_path)],
        git_repo_with_setup_helper,
    )

    result = _run(["bash", "scripts/apl_setup_worktree.sh"], worktree_path)

    copied_settings = worktree_path / ".claude" / "settings.local.json"
    assert "Copied:" in result.stdout
    assert copied_settings.read_text(encoding="utf-8") == source_settings.read_text(
        encoding="utf-8"
    )
