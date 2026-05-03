"""Git subprocess helpers for maintainer review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class CommandResult:
    """Captured subprocess result."""

    returncode: int
    stdout: str
    stderr: str


def run_command(
    command: str | list[str],
    *,
    cwd: Path,
    shell: bool = False,
    timeout: int = 60,
) -> CommandResult:
    """Run a command and return captured output without raising."""
    completed = subprocess.run(
        command,
        cwd=cwd,
        shell=shell,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return CommandResult(
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def current_branch(root: Path) -> str:
    """Return the current git branch name."""
    result = run_command(["git", "branch", "--show-current"], cwd=root)
    return result.stdout.strip()


def git_status_clean(root: Path) -> bool:
    """Return whether the worktree is clean."""
    result = run_command(["git", "status", "--short"], cwd=root)
    return result.returncode == 0 and result.stdout.strip() == ""


def local_branch_exists(root: Path, branch: str) -> bool:
    """Return whether a local branch exists."""
    result = run_command(
        ["git", "rev-parse", "--verify", branch],
        cwd=root,
    )
    return result.returncode == 0


def working_tree_changed_files(root: Path) -> tuple[str, ...]:
    """Return changed files from git status for the current worktree."""
    result = run_command(["git", "status", "--short"], cwd=root)
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        entry = line[3:] if len(line) > 3 else line
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1]
        paths.append(entry.strip())
    return tuple(paths)


def parse_added_lines(
    diff_text: str,
    *,
    include_prefixes: tuple[str, ...] | None = None,
    exclude_prefixes: tuple[str, ...] = (),
) -> tuple[str, ...]:
    """Extract added diff lines from unified diff text."""
    added_lines: list[str] = []
    current_path: str | None = None
    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            current_path = line.removeprefix("+++ b/").strip()
            continue
        if line.startswith("+++ "):
            current_path = None
            continue
        if line.startswith("+++ ") or line.startswith("@@"):
            continue
        if line.startswith("+"):
            if current_path is None:
                continue
            if include_prefixes is not None and not any(
                current_path.startswith(prefix) for prefix in include_prefixes
            ):
                continue
            if any(current_path.startswith(prefix) for prefix in exclude_prefixes):
                continue
            added_lines.append(line[1:])
    return tuple(added_lines)


def changed_files_vs_main(root: Path, branch: str) -> tuple[str, ...]:
    """Return changed files for a branch relative to main."""
    result = run_command(
        ["git", "diff", "--name-only", f"main...{branch}"],
        cwd=root,
    )
    changed = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if branch == current_branch(root):
        changed.extend(working_tree_changed_files(root))
    return tuple(dict.fromkeys(changed))


def added_lines_vs_main(root: Path, branch: str) -> tuple[str, ...]:
    """Return added diff lines for a branch relative to main."""
    result = run_command(
        ["git", "diff", "--unified=0", f"main...{branch}"],
        cwd=root,
        timeout=120,
    )
    added_lines = list(parse_added_lines(result.stdout))
    if branch == current_branch(root):
        worktree_result = run_command(
            ["git", "diff", "--unified=0"],
            cwd=root,
            timeout=120,
        )
        added_lines.extend(parse_added_lines(worktree_result.stdout))
    return tuple(added_lines)
