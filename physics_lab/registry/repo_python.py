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

from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys


def venv_python_candidates(base: Path) -> tuple[Path, ...]:
    """Return the venv interpreter paths to probe under ``base`` (both platforms)."""
    return (
        base / ".venv" / "Scripts" / "python.exe",  # Windows
        base / ".venv" / "bin" / "python",  # macOS / Linux
    )


@dataclass(frozen=True)
class RepositoryPythonSelection:
    """Deterministic interpreter selection report for validation helpers."""

    selected_executable: str
    selected_source: str
    active_executable: str
    repository_venv_python: str | None
    active_python_matches_repository_venv: bool | None
    priority_order: tuple[str, ...]
    recommendations: tuple[str, ...]


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


def _normalize_existing_candidate(candidate: Path) -> Path | None:
    if not candidate.exists():
        return None
    return candidate.parent.resolve() / candidate.name


def _path_matches(left: Path | None, right: str) -> bool | None:
    if left is None:
        return None
    try:
        return left.resolve() == Path(right).resolve()
    except OSError:
        return str(left) == right


def _search_roots(root: Path, git_common_dir: Path | None) -> tuple[Path, ...]:
    common_dir = git_common_dir if git_common_dir is not None else _git_common_dir(root)
    roots: list[Path] = [root]
    if common_dir is not None and common_dir.name == ".git":
        roots.append(common_dir.parent)
    seen: set[Path] = set()
    unique_roots: list[Path] = []
    for search_root in roots:
        try:
            resolved_root = search_root.resolve()
        except OSError:
            resolved_root = search_root
        if resolved_root in seen:
            continue
        seen.add(resolved_root)
        unique_roots.append(search_root)
    return tuple(unique_roots)


def find_repo_python(root: Path, *, git_common_dir: Path | None = None) -> Path | None:
    """Return the repository ``.venv`` interpreter for ``root``, or ``None``.

    Searches the checkout itself and, for a git worktree, the main checkout that
    owns the shared ``.git`` directory — so a single repo venv installed in the
    main clone resolves from every worktree. Returns ``None`` when no repository
    venv interpreter exists.
    """
    for search_root in _search_roots(root, git_common_dir):
        for candidate in venv_python_candidates(search_root):
            normalized = _normalize_existing_candidate(candidate)
            if normalized is not None:
                # Normalize the parent but DO NOT resolve the interpreter symlink
                # itself: `.venv/bin/python` is a symlink to the base interpreter,
                # and following it (`.resolve()`) drops venv semantics so the
                # child process loses the project dependencies. Keep the venv path.
                return normalized
    return None


def select_validation_python(
    root: Path,
    *,
    git_common_dir: Path | None = None,
    active_executable: str | None = None,
) -> RepositoryPythonSelection:
    """Return the selected validation interpreter and diagnostics.

    Priority is intentionally cross-platform and deterministic:

    1. the active interpreter, when it is already the repository venv;
    2. the checkout-local ``.venv`` interpreter;
    3. the main-checkout ``.venv`` interpreter for git worktrees;
    4. the active interpreter as a compatibility fallback.
    """
    active = active_executable or sys.executable
    roots = _search_roots(root, git_common_dir)
    priority_items: list[str] = ["active interpreter when it matches repository .venv"]
    for index, search_root in enumerate(roots):
        root_label = "checkout" if index == 0 else "main checkout for git worktree"
        priority_items.extend(
            f"{root_label} {candidate.relative_to(search_root)}"
            for candidate in venv_python_candidates(search_root)
        )
    priority_items.append("active interpreter fallback")

    repository_venv = find_repo_python(root, git_common_dir=git_common_dir)
    active_matches = _path_matches(repository_venv, active)
    recommendations: list[str] = []
    if repository_venv is not None and active_matches:
        selected = active
        selected_source = "active_repository_venv"
    elif repository_venv is not None:
        selected = str(repository_venv)
        selected_source = "repository_venv"
        recommendations.append(f"Run validation with repository Python: {repository_venv}")
    else:
        selected = active
        selected_source = "active_fallback"
        recommendations.append(
            "Repository .venv Python was not found; using the active interpreter."
        )

    return RepositoryPythonSelection(
        selected_executable=selected,
        selected_source=selected_source,
        active_executable=active,
        repository_venv_python=str(repository_venv) if repository_venv is not None else None,
        active_python_matches_repository_venv=active_matches,
        priority_order=tuple(priority_items),
        recommendations=tuple(recommendations),
    )


def resolve_validation_python(root: Path, *, git_common_dir: Path | None = None) -> str:
    """Return the interpreter path to run task validation with.

    Prefers the repository venv interpreter; falls back to ``sys.executable`` so a
    checkout without a venv behaves exactly as it does today.
    """
    return select_validation_python(
        root,
        git_common_dir=git_common_dir,
    ).selected_executable
