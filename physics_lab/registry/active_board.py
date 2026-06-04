"""Canonical task-entry loader shared by generated navigation and reports.

Historically this module also rendered and synchronized ``tasks/ACTIVE.md``.
That full-board file was retired (TASK-0470 decision B2 / TASK-0473) because no
agent or human consumed it: agents enter through ``apl_mission.py``, humans use
``docs/task-views/*.md``, and history lives in ``git log``. The task-entry
loader (``TaskBoardEntry``, ``load_board_entries``, ``STATUS_SECTION_ORDER``)
remains here because the task views, snapshot, mission control, and campaign
curator all build on it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from physics_lab.registry.task_discovery import iter_canonical_task_files
from physics_lab.registry.tasks import load_task


STATUS_SECTION_ORDER = (
    ("READY", "READY"),
    ("IN_PROGRESS", "IN_PROGRESS"),
    ("REVIEW_READY", "REVIEW_READY"),
    ("DONE", "DONE RECENTLY"),
    ("PROPOSED", "PROPOSED"),
    ("BLOCKED", "BLOCKED"),
    ("SUPERSEDED", "SUPERSEDED"),
    ("REJECTED", "REJECTED"),
)
STATUS_ALIASES = {
    "CLAIMED": "IN_PROGRESS",
    "OPEN": "IN_PROGRESS",
}


@dataclass(frozen=True)
class TaskBoardEntry:
    """Compact task metadata for the generated board snapshot."""

    task_id: str
    title: str
    type: str
    priority: str
    difficulty: str
    status: str

    @property
    def task_number(self) -> int:
        return int(self.task_id.removeprefix("TASK-"))


def load_board_entries(root: Path) -> tuple[TaskBoardEntry, ...]:
    """Load all canonical task files as compact board entries."""
    entries: list[TaskBoardEntry] = []
    for path in iter_canonical_task_files(root):
        payload = load_task(path)
        status = STATUS_ALIASES.get(str(payload["status"]), str(payload["status"]))
        entries.append(
            TaskBoardEntry(
                task_id=str(payload["id"]),
                title=str(payload["title"]),
                type=str(payload["type"]),
                priority=str(payload["priority"]),
                difficulty=str(payload["difficulty"]),
                status=status,
            )
        )
    return tuple(entries)
