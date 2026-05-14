"""Generated repository state synchronized from canonical task and mission data."""

from __future__ import annotations

from pathlib import Path

from physics_lab.registry.active_board import sync_active_board
from physics_lab.registry.task_views import sync_task_views


def sync_generated_task_state(root: Path) -> tuple[Path, ...]:
    """Refresh generated task navigation artifacts from canonical task YAML files."""
    active_board_path = sync_active_board(root)
    task_view_paths = sync_task_views(root)
    return (active_board_path, *task_view_paths)
