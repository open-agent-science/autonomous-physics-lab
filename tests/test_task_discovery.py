"""Tests for the archive-aware task discovery helper (TASK-0571).

Includes a parity test proving the helper returns the exact same set as today's
flat enumeration on the real repository, so adopting it is behavior-neutral.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from physics_lab.registry import task_closeout
from physics_lab.registry.task_discovery import (
    find_task_file,
    find_task_files,
    iter_canonical_task_files,
    task_id_from_path,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FLAT_GLOB = "TASK-[0-9][0-9][0-9][0-9]-*.yaml"
TEMPLATE = "TASK-TEMPLATE.yaml"


def test_parity_with_current_flat_enumeration():
    """On today's flat tree the helper matches the legacy glob exactly."""
    legacy = {
        p.resolve()
        for p in (REPO_ROOT / "tasks").glob(FLAT_GLOB)
        if p.name != TEMPLATE
    }
    helper = {p.resolve() for p in iter_canonical_task_files(REPO_ROOT)}
    assert helper == legacy
    assert len(helper) > 100  # sanity: the real repo has many canonical tasks


def test_find_task_file_resolves_real_id():
    # TASK-0559 (this migration's preflight) exists on the real repo
    found = find_task_file(REPO_ROOT, "TASK-0559")
    assert found is not None
    assert found.name.startswith("TASK-0559-")
    assert find_task_file(REPO_ROOT, "TASK-9999") is None


def test_task_id_from_path():
    assert task_id_from_path("tasks/TASK-0559-foo.yaml") == "TASK-0559"
    assert task_id_from_path("tasks/archive/0500-0999/TASK-0559-foo.yaml") == "TASK-0559"
    assert task_id_from_path("tasks/proposals/20260101-x.yaml") is None
    assert task_id_from_path("TASK-TEMPLATE.yaml") is None


def _write(path: Path, task_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"id: {task_id}\nstatus: DONE\n", encoding="utf-8")


@pytest.fixture()
def hybrid_repo(tmp_path: Path) -> Path:
    tasks = tmp_path / "tasks"
    _write(tasks / "TASK-0600-active.yaml", "TASK-0600")
    (tasks / TEMPLATE).write_text("id: TASK-TEMPLATE\n", encoding="utf-8")
    _write(tasks / "archive" / "0000-0499" / "TASK-0001-old.yaml", "TASK-0001")
    _write(tasks / "archive" / "0500-0999" / "TASK-0559-self.yaml", "TASK-0559")
    _write(tasks / "proposals" / "20260101-idea.yaml", "PROP")
    _write(tasks / "microtasks" / "queue.yaml", "MT")
    return tmp_path


def test_discovers_flat_and_archived_excludes_noncanonical(hybrid_repo: Path):
    ids = {task_id_from_path(p) for p in iter_canonical_task_files(hybrid_repo)}
    assert ids == {"TASK-0600", "TASK-0001", "TASK-0559"}
    assert find_task_file(hybrid_repo, "TASK-0001").parent.name == "0000-0499"
    assert find_task_file(hybrid_repo, "TASK-0600") is not None


def test_id_uniqueness_scan_catches_duplicate_across_archive(hybrid_repo: Path):
    """A careless new task reusing an archived id is detectable across flat+archive."""
    _write(hybrid_repo / "tasks" / "TASK-0001-accidental-reuse.yaml", "TASK-0001")
    seen: dict[str, Path] = {}
    duplicates = []
    for path in iter_canonical_task_files(hybrid_repo):
        task_id = task_id_from_path(path)
        if task_id in seen:
            duplicates.append(task_id)
        seen[task_id] = path
    assert "TASK-0001" in duplicates


def test_find_task_files_returns_all_matches(hybrid_repo: Path):
    assert [p.name for p in find_task_files(hybrid_repo, "TASK-0559")] == ["TASK-0559-self.yaml"]
    assert find_task_files(hybrid_repo, "TASK-9999") == []
    # detect an accidental duplicate id across flat + archive
    _write(hybrid_repo / "tasks" / "TASK-0559-dup.yaml", "TASK-0559")
    assert len(find_task_files(hybrid_repo, "TASK-0559")) == 2


def test_migrated_closeout_resolver_finds_archived_task(hybrid_repo: Path):
    """A call site routed through the helper now resolves an archived task."""
    resolved = task_closeout.find_task_file(hybrid_repo, "TASK-0559")
    assert resolved.name == "TASK-0559-self.yaml"
    assert resolved.parent.name == "0500-0999"


def test_resolver_cli_smoke(hybrid_repo: Path):
    script = REPO_ROOT / "scripts" / "apl_task_path.py"
    # bare number is normalized to TASK-0559 and resolves into the archive
    ok = subprocess.run(
        [sys.executable, str(script), "559", "--root", str(hybrid_repo)],
        capture_output=True, text=True,
    )
    assert ok.returncode == 0
    assert "TASK-0559-self.yaml" in ok.stdout
    # missing id exits non-zero
    missing = subprocess.run(
        [sys.executable, str(script), "TASK-9999", "--root", str(hybrid_repo)],
        capture_output=True, text=True,
    )
    assert missing.returncode == 1
