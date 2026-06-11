"""Resolve the repository virtual-environment interpreter (TASK-0725).

APL requires Python 3.11+. Tools such as the maintainer review helper run task
validation through a child python; if that child is a bare system interpreter
older than the minimum (for example macOS ``python3`` 3.9.6), pytest aborts on the
runtime guard and the review returns a false ``BLOCKED`` unrelated to the diff.

The agent doctor already locates the repository ``.venv`` interpreter. This module
is the shared, cross-platform home for that discovery so review-time validation
can prefer it, with a safe fallback to the launching interpreter when no repo venv
exists (behavior then matches a plain ``sys.executable`` run).
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


def venv_python_candidates(base: Path) -> tuple[Path, ...]:
    """Return the venv interpreter paths to probe under ``base`` (both platforms)."""
    return (
        base / ".venv" / "Scripts" / "python.exe",  # Windows
        base / ".venv" / "bin" / "python",  # macOS / Linux
    )


def _git_common_dir(root: Path) -> Path | None:
    """Return the git common dir for ``root`` (the main checkout for a worktree)."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = (root / path).resolve()
    return path


def find_repo_python(root: Path, *, git_common_dir: Path | None = None) -> Path | None:
    """Return the repository ``.venv`` interpreter for ``root``, or ``None``.

    Searches the checkout itself and, for a git worktree, the main checkout that
    owns the shared ``.git`` directory — so a single repo venv installed in the
    main clone resolves from every worktree. Returns ``None`` when no repository
    venv interpreter exists.
    """
    common_dir = git_common_dir if git_common_dir is not None else _git_common_dir(root)
    search_roots: list[Path] = [root]
    if common_dir is not None and common_dir.name == ".git":
        search_roots.append(common_dir.parent)
    seen: set[Path] = set()
    for search_root in search_roots:
        try:
            resolved_root = search_root.resolve()
        except OSError:
            resolved_root = search_root
        if resolved_root in seen:
            continue
        seen.add(resolved_root)
        for candidate in venv_python_candidates(search_root):
            if candidate.exists():
                # Normalize the parent but DO NOT resolve the interpreter symlink
                # itself: `.venv/bin/python` is a symlink to the base interpreter,
                # and following it (`.resolve()`) drops venv semantics so the
                # child process loses the project dependencies. Keep the venv path.
                return candidate.parent.resolve() / candidate.name
    return None


def resolve_validation_python(root: Path, *, git_common_dir: Path | None = None) -> str:
    """Return the interpreter path to run task validation with.

    Prefers the repository venv interpreter; falls back to ``sys.executable`` so a
    checkout without a venv behaves exactly as it does today.
    """
    repo_python = find_repo_python(root, git_common_dir=git_common_dir)
    return str(repo_python) if repo_python is not None else sys.executable
