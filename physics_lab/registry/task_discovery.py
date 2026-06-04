"""Archive-aware discovery of canonical task files.

Single source of truth for locating canonical task YAML files so call sites do
not hardcode a flat ``tasks/*.yaml`` glob. Canonical task files are named
``TASK-NNNN-*.yaml`` and may live either flat under ``tasks/`` (today) or under
``tasks/archive/<bucket>/`` (future id-range buckets). See
``docs/task-archive-migration-plan.md``.

The discovery rule is a recursive glob for the canonical name pattern, so it is
layout-agnostic: it returns the same set on the current flat tree and on a
future archived layout. It deliberately excludes ``TASK-TEMPLATE.yaml`` and the
non-canonical ``tasks/proposals/`` and ``tasks/microtasks/`` subtrees, whose
files are not named ``TASK-NNNN-*``.
"""
from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

CANONICAL_TASK_GLOB = "TASK-[0-9][0-9][0-9][0-9]-*.yaml"
TASK_TEMPLATE_NAME = "TASK-TEMPLATE.yaml"
_TASK_ID_RE = re.compile(r"^(TASK-[0-9]{4,})-")


def tasks_root(repo_root: str | Path) -> Path:
    """Return the ``tasks/`` directory for a repository root."""
    return Path(repo_root) / "tasks"


def iter_canonical_task_files(repo_root: str | Path) -> Iterator[Path]:
    """Yield every canonical task file under ``tasks/``, flat or archived.

    Results are sorted by path. ``TASK-TEMPLATE.yaml`` is excluded; the
    ``proposals/`` and ``microtasks/`` subtrees are excluded by the name
    pattern.
    """
    root = tasks_root(repo_root)
    if not root.exists():
        return
    for path in sorted(root.rglob(CANONICAL_TASK_GLOB)):
        if path.name == TASK_TEMPLATE_NAME:
            continue
        yield path


def task_id_from_path(path: str | Path) -> str | None:
    """Extract the canonical task id (e.g. ``TASK-0559``) from a file path."""
    match = _TASK_ID_RE.match(Path(path).name)
    return match.group(1) if match else None


def find_task_file(repo_root: str | Path, task_id: str) -> Path | None:
    """Return the file for a canonical task id, or ``None`` if not found.

    Resolves whether the task is active (flat) or archived, so callers never
    need to know the on-disk layout. If more than one file matches (which the
    repository-wide uniqueness check forbids), the first by sorted path is
    returned; use :func:`find_task_files` when the caller needs to detect that.
    """
    files = find_task_files(repo_root, task_id)
    return files[0] if files else None


def find_task_files(repo_root: str | Path, task_id: str) -> list[Path]:
    """Return all canonical files matching a task id (sorted), flat or archived.

    Normally zero or one; returning a list lets callers preserve their existing
    "expected exactly one" / "multiple found" diagnostics during the archive
    migration. This is the archive-aware replacement for
    ``sorted((root / "tasks").glob(f"{task_id}-*.yaml"))``.
    """
    prefix = f"{task_id}-"
    return [
        path
        for path in iter_canonical_task_files(repo_root)
        if path.name.startswith(prefix)
    ]
