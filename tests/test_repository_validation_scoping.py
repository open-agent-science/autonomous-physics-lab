"""Validation scoping for archived tasks (TASK-0576).

Active tasks under tasks/ get full schema validation; archived tasks under
tasks/archive/<bucket>/ get only a minimal parse (mapping with an id), so an
evolving task schema never forces edits to frozen history.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from physics_lab.registry import repository
from physics_lab.registry.task_discovery import iter_canonical_task_files

REPO_ROOT = Path(__file__).resolve().parents[1]


def _copy_real_active_task(tasks_dir: Path) -> None:
    real = next(iter(iter_canonical_task_files(REPO_ROOT)))
    shutil.copy(real, tasks_dir / real.name)


def test_archived_schema_invalid_task_is_tolerated(tmp_path: Path):
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    _copy_real_active_task(tasks_dir)  # valid active task
    archive = tasks_dir / "archive" / "9000-9499"
    archive.mkdir(parents=True)
    # Parseable but NOT schema-valid (missing required fields). Frozen history.
    (archive / "TASK-9001-frozen.yaml").write_text(
        "id: TASK-9001\nstatus: DONE\nlegacy_field: whatever\n", encoding="utf-8"
    )
    loaded = {payload["id"] for _path, payload in repository._load_directory(tmp_path, "tasks")}
    assert "TASK-9001" in loaded  # archived task loaded without full schema failure


def test_active_schema_invalid_task_still_fails(tmp_path: Path):
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    # Active (flat) but schema-invalid -> full validation must still reject it.
    (tasks_dir / "TASK-9003-broken.yaml").write_text(
        "id: TASK-9003\nstatus: DONE\n", encoding="utf-8"
    )
    with pytest.raises(Exception):
        repository._load_directory(tmp_path, "tasks")


def test_archived_minimal_contract_requires_id(tmp_path: Path):
    tasks_dir = tmp_path / "tasks"
    archive = tasks_dir / "archive" / "9000-9499"
    archive.mkdir(parents=True)
    # Even the archive must parse to a mapping with an id.
    (archive / "TASK-9005-noid.yaml").write_text("status: DONE\n", encoding="utf-8")
    with pytest.raises(Exception):
        repository._load_directory(tmp_path, "tasks")
