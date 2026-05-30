"""Generated repository state synchronized from canonical task and mission data."""

from __future__ import annotations

from pathlib import Path

from physics_lab.registry.task_views import sync_task_views


def sync_generated_task_state(root: Path) -> tuple[Path, ...]:
    """Refresh generated task navigation (docs/task-views/*.md) from task YAML.

    tasks/ACTIVE.md was retired (TASK-0470 decision B2 / TASK-0473); the task
    views are the generated human navigation surface.
    """
    return tuple(sync_task_views(root))
