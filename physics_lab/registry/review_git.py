"""Git subprocess helpers for maintainer review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import fnmatch
import subprocess
import time


# Paths that may appear as untracked in `git status --short` but are pure
# harness/local-session state and must not block maintainer review.
# Keep this list short. Add to `.gitignore` first whenever possible; this
# tuple is the defense-in-depth fallback for environments where the
# repository's `.gitignore` is out of sync.
HARNESS_IGNORE_PATHS: tuple[str, ...] = (
    ".claude/scheduled_tasks.lock",
)

# Generated aggregates that may drift locally during review or pytest without
# indicating a task-PR problem. See docs/notes/context-bundle-architecture-decision.md
# and docs/notes/generated-task-navigation-architecture-decision.md.
GENERATED_EPHEMERAL_IGNORE_PATHS: tuple[str, ...] = (
    "CONTEXT.md",
    "docs/task-views/*",
)

REVIEW_IGNORE_PATHS: tuple[str, ...] = (
    HARNESS_IGNORE_PATHS + GENERATED_EPHEMERAL_IGNORE_PATHS
)


def _path_matches_ignore(path: str, patterns: tuple[str, ...]) -> bool:
    """Return True if path matches any of the fnmatch-style ignore patterns."""
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


@dataclass(frozen=True)
class CommandResult:
    """Captured subprocess result."""

    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False
    elapsed_seconds: float = 0.0


def run_command(
    command: str | list[str],
    *,
    cwd: Path,
    shell: bool = False,
    timeout: int = 60,
) -> CommandResult:
    """Run a command and return captured output without raising."""
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            shell=shell,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - started
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return CommandResult(
            returncode=-1,
            stdout=stdout,
            stderr=stderr or f"Command timed out after {timeout} seconds.",
            timed_out=True,
            elapsed_seconds=elapsed,
        )
    elapsed = time.monotonic() - started
    return CommandResult(
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        elapsed_seconds=elapsed,
    )


def git_safe_directory_flags(*paths: Path) -> list[str]:
    """Return per-invocation ``safe.directory`` flags for disposable worktrees.

    Codex and other container agents may own review worktrees under a different
    UID than the main repository checkout. Passing these flags avoids mutating
    global git config while still allowing ``git worktree`` commands to run.
    """

    flags: list[str] = []
    seen: set[str] = set()
    for path in paths:
        resolved = str(path.resolve())
        if resolved in seen:
            continue
        seen.add(resolved)
        flags.extend(["-c", f"safe.directory={resolved}"])
    return flags


def run_git_command(
    args: list[str],
    *,
    cwd: Path,
    extra_safe_directories: tuple[Path, ...] = (),
    timeout: int = 60,
) -> CommandResult:
    """Run a git subcommand with narrow ``safe.directory`` flags for ``cwd``."""

    safe_flags = git_safe_directory_flags(cwd, *extra_safe_directories)
    return run_command(["git", *safe_flags, *args], cwd=cwd, timeout=timeout)


def branch_exists(root: Path, ref: str) -> bool:
    """Return whether a git ref exists locally or as a remote-tracking ref."""
    result = run_git_command(["rev-parse", "--verify", ref], cwd=root)
    return result.returncode == 0


def current_branch(root: Path) -> str:
    """Return the current git branch name."""
    result = run_git_command(["branch", "--show-current"], cwd=root)
    return result.stdout.strip()


def git_status_clean(
    root: Path,
    *,
    ignore_paths: tuple[str, ...] = REVIEW_IGNORE_PATHS,
) -> bool:
    """Return whether the worktree is clean.

    Paths matching ``ignore_paths`` are excluded from the cleanliness check.
    The default ignore list covers harness/local-session artifacts and
    generated ephemeral aggregates that should not block maintainer review
    (see ``REVIEW_IGNORE_PATHS``). Pass ``ignore_paths=()`` to disable
    filtering and require a strictly empty ``git status --short``.
    """
    paths = working_tree_changed_files(root, ignore_paths=ignore_paths)
    return len(paths) == 0


def local_branch_exists(root: Path, branch: str) -> bool:
    """Return whether a local branch exists."""
    return branch_exists(root, branch)


def working_tree_changed_files(
    root: Path,
    *,
    ignore_paths: tuple[str, ...] = REVIEW_IGNORE_PATHS,
) -> tuple[str, ...]:
    """Return changed files from git status for the current worktree.

    Paths matching ``ignore_paths`` are omitted from the result. Pass
    ``ignore_paths=()`` to get the unfiltered list.
    """
    result = run_git_command(["status", "--short"], cwd=root)
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        status = line[:2]
        entry = line[3:] if len(line) > 3 else line
        if " -> " in entry and any(code in status for code in ("R", "C")):
            entry = entry.split(" -> ", 1)[1]
        path = entry.strip()
        if _path_matches_ignore(path, ignore_paths):
            continue
        paths.append(path)
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


def changed_files_vs_main(
    root: Path,
    branch: str,
    *,
    base_ref: str = "main",
) -> tuple[str, ...]:
    """Return changed files for a branch relative to the chosen base ref."""
    result = run_git_command(
        ["diff", "--name-only", f"{base_ref}...{branch}"],
        cwd=root,
    )
    changed = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if branch == current_branch(root):
        changed.extend(working_tree_changed_files(root))
    return tuple(dict.fromkeys(changed))


def added_lines_vs_main(
    root: Path,
    branch: str,
    *,
    base_ref: str = "main",
) -> tuple[str, ...]:
    """Return added diff lines for a branch relative to the chosen base ref."""
    result = run_git_command(
        ["diff", "--unified=0", f"{base_ref}...{branch}"],
        cwd=root,
        timeout=120,
    )
    added_lines = list(parse_added_lines(result.stdout))
    if branch == current_branch(root):
        worktree_result = run_git_command(
            ["diff", "--unified=0"],
            cwd=root,
            timeout=120,
        )
        added_lines.extend(parse_added_lines(worktree_result.stdout))
    return tuple(added_lines)
