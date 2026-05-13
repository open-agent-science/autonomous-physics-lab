"""Deterministic synchronization for the human-readable active task board."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from physics_lab.registry.tasks import load_task


AUTO_START = "<!-- BEGIN AUTO TASK STATUS BOARD -->"
AUTO_END = "<!-- END AUTO TASK STATUS BOARD -->"

STATUS_SECTION_ORDER = (
    ("READY", "READY"),
    ("IN_PROGRESS", "IN_PROGRESS"),
    ("REVIEW_READY", "REVIEW_READY"),
    ("DONE", "DONE RECENTLY"),
    ("PROPOSED", "PROPOSED"),
    ("BLOCKED", "BLOCKED"),
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
    for path in sorted((root / "tasks").glob("TASK-[0-9][0-9][0-9][0-9]-*.yaml")):
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


def render_active_board_snapshot(root: Path) -> str:
    """Render the generated status block for tasks/ACTIVE.md."""
    entries = load_board_entries(root)
    lines = [
        AUTO_START,
        "",
        "> This task-status snapshot is generated from canonical task YAML files.",
        "> Use `docs/task-views/*.md` for lighter READY/blocked/watchlist navigation;",
        "> `tasks/ACTIVE.md` remains the full generated status board, including DONE history.",
        "> Edit `tasks/TASK-*.yaml` for routine status transitions, then run",
        "> `python3 -m physics_lab.cli sync-active-board .` on the maintainer branch.",
        "",
    ]
    for status, header in STATUS_SECTION_ORDER:
        lines.append(f"## {header}")
        lines.append("")
        section_entries = _entries_for_status(entries, status)
        if section_entries:
            lines.extend(_render_entry(entry, status) for entry in section_entries)
        else:
            lines.append("None.")
        lines.append("")
    lines.append(AUTO_END)
    return "\n".join(lines)


def sync_active_board(root: Path) -> Path:
    """Replace the generated block inside tasks/ACTIVE.md with a fresh snapshot."""
    active_path = root / "tasks" / "ACTIVE.md"
    updated_lines = _updated_active_board_lines(active_path, root)
    active_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
    return active_path


def active_board_is_synced(root: Path) -> bool:
    """Return whether the generated ACTIVE.md block matches canonical task YAML files."""
    active_path = root / "tasks" / "ACTIVE.md"
    original_lines = active_path.read_text(encoding="utf-8").splitlines()
    expected_lines = _updated_active_board_lines(active_path, root)
    return original_lines == expected_lines


def _updated_active_board_lines(active_path: Path, root: Path) -> list[str]:
    """Return ACTIVE.md lines with a freshly rendered generated block."""
    original_lines = active_path.read_text(encoding="utf-8").splitlines()
    try:
        start_index = original_lines.index(AUTO_START)
        end_index = original_lines.index(AUTO_END)
    except ValueError as exc:
        raise ValueError("tasks/ACTIVE.md is missing auto-sync markers.") from exc
    if end_index < start_index:
        raise ValueError("tasks/ACTIVE.md auto-sync markers are out of order.")
    generated_lines = render_active_board_snapshot(root).splitlines()
    updated_lines = (
        original_lines[:start_index]
        + generated_lines
        + original_lines[end_index + 1 :]
    )
    return updated_lines


def _entries_for_status(
    entries: tuple[TaskBoardEntry, ...],
    status: str,
) -> tuple[TaskBoardEntry, ...]:
    filtered = [entry for entry in entries if entry.status == status]
    reverse = status == "DONE"
    return tuple(sorted(filtered, key=lambda entry: entry.task_number, reverse=reverse))


def _render_entry(entry: TaskBoardEntry, status: str) -> str:
    if status == "DONE":
        return f"- `{entry.task_id}` — {entry.title} (merged)"
    return (
        f"- `{entry.task_id}` — {entry.title} "
        f"(`{entry.type}`, priority `{entry.priority}`, difficulty `{entry.difficulty}`)"
    )
