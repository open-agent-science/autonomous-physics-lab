"""The repository task loader is archive-aware (TASK-0575).

Making `_load_directory(root, "tasks")` use the shared discovery helper means
validate-repo, the task-id uniqueness check, and scientific-memory-integrity all
see tasks whether they are flat under tasks/ or in tasks/archive/<bucket>/.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from physics_lab.registry import repository
from physics_lab.registry.task_discovery import iter_canonical_task_files

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_loader_parity_on_flat_tree():
    """On today's flat tree the loader matches the discovery helper exactly."""
    loaded = {payload["id"] for _path, payload in repository._load_directory(REPO_ROOT, "tasks")}
    helper = {
        path.name.split("-")[0] + "-" + path.name.split("-")[1]
        for path in iter_canonical_task_files(REPO_ROOT)
    }
    assert loaded == helper
    assert len(loaded) > 100


def test_loader_picks_up_archived_task(tmp_path: Path):
    """A task under tasks/archive/<bucket>/ is loaded by the repository loader."""
    real_files = list(iter_canonical_task_files(REPO_ROOT))[:2]
    assert len(real_files) == 2

    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    # one flat, one archived (distinct real files => distinct ids)
    shutil.copy(real_files[0], tasks_dir / real_files[0].name)
    archive_dir = tasks_dir / "archive" / "0000-0499"
    archive_dir.mkdir(parents=True)
    shutil.copy(real_files[1], archive_dir / real_files[1].name)

    loaded = {payload["id"] for _path, payload in repository._load_directory(tmp_path, "tasks")}
    assert len(loaded) == 2

    archived_paths = [
        path for path, _payload in repository._load_directory(tmp_path, "tasks")
        if "archive" in path.parts
    ]
    assert len(archived_paths) == 1


def test_template_still_excluded(tmp_path: Path):
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    real = next(iter(iter_canonical_task_files(REPO_ROOT)))
    shutil.copy(real, tasks_dir / real.name)
    (tasks_dir / "TASK-TEMPLATE.yaml").write_text("id: TASK-TEMPLATE\n", encoding="utf-8")
    loaded = [payload["id"] for _path, payload in repository._load_directory(tmp_path, "tasks")]
    assert "TASK-TEMPLATE" not in loaded
    assert len(loaded) == 1
