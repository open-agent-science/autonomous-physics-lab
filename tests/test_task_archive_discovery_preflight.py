"""Preflight for the task-archive migration (TASK-0559).

Demonstrates the recommended archive-aware discovery rule on a temporary fixture,
without moving any real task files. The rule is a recursive glob for canonical
task ids, which is layout-agnostic: it returns the same set on today's flat
``tasks/*.yaml`` tree and on a future ``tasks/archive/<bucket>/`` layout, while
excluding proposals, microtasks, and the template.

If a later migration PR changes task discovery, this test guards the four
invariants the migration plan (docs/task-archive-migration-plan.md) must keep.
"""
from __future__ import annotations

from pathlib import Path

import pytest

CANONICAL_GLOB = "TASK-[0-9][0-9][0-9][0-9]-*.yaml"
TEMPLATE_NAME = "TASK-TEMPLATE.yaml"
ARCHIVE_BUCKET_SIZE = 500


def iter_canonical_task_files(tasks_root: Path):
    """Recommended discovery: recursive, canonical-id-only, template excluded."""
    for path in sorted(tasks_root.rglob(CANONICAL_GLOB)):
        if path.name == TEMPLATE_NAME:
            continue
        yield path


def find_task_file(tasks_root: Path, task_id: str) -> Path | None:
    """Find-one-by-id across flat + archive."""
    for path in iter_canonical_task_files(tasks_root):
        if path.name.startswith(f"{task_id}-"):
            return path
    return None


def archive_bucket(task_id: str) -> str:
    """Pure function of the immutable id -> id-range bucket dir name."""
    number = int(task_id.split("-")[1])
    lo = (number // ARCHIVE_BUCKET_SIZE) * ARCHIVE_BUCKET_SIZE
    hi = lo + ARCHIVE_BUCKET_SIZE - 1
    return f"{lo:04d}-{hi:04d}"


def _write(path: Path, task_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"id: {task_id}\nstatus: DONE\n", encoding="utf-8")


@pytest.fixture()
def hybrid_tree(tmp_path: Path) -> Path:
    tasks = tmp_path / "tasks"
    # active, flat
    _write(tasks / "TASK-0600-active-one.yaml", "TASK-0600")
    _write(tasks / "TASK-0601-active-two.yaml", "TASK-0601")
    # template (must be excluded)
    (tasks / TEMPLATE_NAME).write_text("id: TASK-TEMPLATE\n", encoding="utf-8")
    # archived, in id-range buckets
    _write(tasks / "archive" / "0000-0499" / "TASK-0001-old.yaml", "TASK-0001")
    _write(tasks / "archive" / "0500-0999" / "TASK-0559-self.yaml", "TASK-0559")
    # non-canonical siblings that must NOT be picked up
    _write(tasks / "proposals" / "20260101-roman-some-idea.yaml", "PROP")
    _write(tasks / "microtasks" / "queue-alpha.yaml", "MT")
    return tasks


def test_discovery_finds_flat_and_archived_only(hybrid_tree: Path):
    found = {p.name.split("-", 2)[0] + "-" + p.name.split("-")[1]
             for p in iter_canonical_task_files(hybrid_tree)}
    assert found == {"TASK-0600", "TASK-0601", "TASK-0001", "TASK-0559"}


def test_discovery_excludes_proposals_microtasks_template(hybrid_tree: Path):
    names = [p.name for p in iter_canonical_task_files(hybrid_tree)]
    assert TEMPLATE_NAME not in names
    assert not any("proposals" in str(p) for p in iter_canonical_task_files(hybrid_tree))
    assert not any("microtasks" in str(p) for p in iter_canonical_task_files(hybrid_tree))


def test_find_by_id_resolves_archived(hybrid_tree: Path):
    assert find_task_file(hybrid_tree, "TASK-0001") is not None  # archived
    assert find_task_file(hybrid_tree, "TASK-0600") is not None  # active
    assert find_task_file(hybrid_tree, "TASK-9999") is None


def test_id_uniqueness_scan_catches_duplicate_across_archive(hybrid_tree: Path):
    # simulate a careless new task reusing an archived id
    _write(hybrid_tree / "TASK-0001-accidental-reuse.yaml", "TASK-0001")
    seen: dict[str, Path] = {}
    duplicates = []
    for path in iter_canonical_task_files(hybrid_tree):
        task_id = path.name.split("-")[0] + "-" + path.name.split("-")[1]
        if task_id in seen:
            duplicates.append(task_id)
        seen[task_id] = path
    assert "TASK-0001" in duplicates


def test_archive_bucket_is_pure_function_of_id():
    assert archive_bucket("TASK-0001") == "0000-0499"
    assert archive_bucket("TASK-0499") == "0000-0499"
    assert archive_bucket("TASK-0500") == "0500-0999"
    assert archive_bucket("TASK-0559") == "0500-0999"
    assert archive_bucket("TASK-1000") == "1000-1499"
