"""Helpers for maintainer task closeout checks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from physics_lab.registry.tasks import load_task


SECTION_HEADER_PATTERN = re.compile(r"^##\s+(?P<name>.+?)\s*$")
TASK_LINE_PATTERN = re.compile(r"TASK-[0-9]{4}")


@dataclass(frozen=True)
class ActiveBoardMatch:
    """Location of a task mention inside the human-readable task board."""

    present: bool
    section: str | None = None
    line_number: int | None = None


@dataclass(frozen=True)
class TaskCloseoutReport:
    """Deterministic snapshot for maintainer closeout review."""

    task_id: str
    task_file: Path
    status: str
    active_board_match: ActiveBoardMatch
    accepted_outputs: tuple[str, ...]
    warnings: tuple[str, ...]
    suggested_actions: tuple[str, ...]


def find_task_file(root: Path, task_id: str) -> Path:
    """Resolve a repository task id to its single task YAML file."""
    matches = sorted((root / "tasks").glob(f"{task_id}-*.yaml"))
    if not matches:
        raise FileNotFoundError(
            f"No task file found for {task_id} under {root / 'tasks'}"
        )
    if len(matches) > 1:
        rendered_matches = ", ".join(str(path) for path in matches)
        raise ValueError(f"Multiple task files found for {task_id}: {rendered_matches}")
    return matches[0]


def find_task_in_active_board(active_board_path: Path, task_id: str) -> ActiveBoardMatch:
    """Return whether the task appears in ACTIVE.md and under which section."""
    current_section: str | None = None
    board_lines = active_board_path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(board_lines, start=1):
        header_match = SECTION_HEADER_PATTERN.match(line.strip())
        if header_match:
            current_section = header_match.group("name")
            continue
        if task_id in line and TASK_LINE_PATTERN.search(line):
            return ActiveBoardMatch(present=True, section=current_section, line_number=index)
    return ActiveBoardMatch(present=False)


def build_closeout_report(root: Path, task_id: str) -> TaskCloseoutReport:
    """Build a deterministic closeout review snapshot for one task."""
    task_file = find_task_file(root, task_id)
    payload = load_task(task_file)
    status = str(payload["status"])
    active_board_path = root / "tasks" / "ACTIVE.md"
    board_match = find_task_in_active_board(active_board_path, task_id)
    accepted_outputs = tuple(str(item) for item in payload.get("accepted_outputs", []))

    warnings: list[str] = []
    suggested_actions: list[str] = []
    expected_sections = _expected_board_sections(status)

    if status != "REVIEW_READY":
        warnings.append(
            "Task status is "
            f"{status}, not REVIEW_READY. Closeout normally starts from "
            "REVIEW_READY after merge."
        )
    if not board_match.present:
        warnings.append("Task does not appear in tasks/ACTIVE.md.")
    elif board_match.section not in expected_sections:
        rendered_sections = ", ".join(repr(section) for section in sorted(expected_sections))
        warnings.append(
            "Task appears in tasks/ACTIVE.md under "
            f"{board_match.section!r}, which does not match expected section(s) {rendered_sections}."
        )

    if status == "REVIEW_READY":
        suggested_actions.append(
            "Confirm the PR was merged and CI passed before setting the task to DONE."
        )
        suggested_actions.append(
            "Verify accepted outputs exist in main before updating the task file."
        )
        suggested_actions.append(
            "Move the task from REVIEW_READY to DONE RECENTLY in tasks/ACTIVE.md "
            "after closeout."
        )
    elif status == "DONE":
        suggested_actions.append(
            "Confirm the ACTIVE board and any dry-run notes reflect the merged task."
        )
    else:
        suggested_actions.append(
            "Return the task to REVIEW_READY before maintainer closeout if "
            "implementation is complete."
        )

    suggested_actions.append(
        "Create a follow-up task instead of forcing DONE when accepted outputs "
        "are only partially complete."
    )
    suggested_actions.append(
        "Add a docs/multi-agent-dry-run.md entry only when the merged PR "
        "belongs to a dry run or contributor pilot."
    )

    return TaskCloseoutReport(
        task_id=task_id,
        task_file=task_file,
        status=status,
        active_board_match=board_match,
        accepted_outputs=accepted_outputs,
        warnings=tuple(warnings),
        suggested_actions=tuple(suggested_actions),
    )


def _expected_board_sections(status: str) -> set[str]:
    """Return acceptable ACTIVE.md section labels for a task status."""
    if status == "DONE":
        return {"DONE", "DONE RECENTLY"}
    return {status}


def render_closeout_report(
    report: TaskCloseoutReport,
    *,
    suggest: bool = False,
    root: Path | None = None,
) -> str:
    """Render a stable text report for CLI or script usage."""
    root_path = root.resolve() if root is not None else None
    try:
        task_file_display = (
            report.task_file.resolve().relative_to(root_path).as_posix()
            if root_path
            else str(report.task_file)
        )
    except ValueError:
        task_file_display = str(report.task_file.resolve())

    board_presence = "yes" if report.active_board_match.present else "no"
    board_section = report.active_board_match.section or "n/a"
    lines = [
        f"Task: {report.task_id}",
        f"Task file: {task_file_display}",
        f"Current status: {report.status}",
        f"Appears in tasks/ACTIVE.md: {board_presence}",
        f"ACTIVE.md section: {board_section}",
        "Accepted outputs:",
    ]

    if report.accepted_outputs:
        lines.extend(f"- {item}" for item in report.accepted_outputs)
    else:
        lines.append("- <none parsed>")

    lines.append("Warnings:")
    if report.warnings:
        lines.extend(f"- {item}" for item in report.warnings)
    else:
        lines.append("- none")

    lines.append("Suggested closeout actions:")
    lines.extend(f"- {item}" for item in report.suggested_actions)

    if suggest:
        lines.append("Suggested file updates (not applied):")
        if report.status == "REVIEW_READY":
            lines.append("- Change task status from REVIEW_READY to DONE after merge verification.")
            lines.append("- Move the task entry from REVIEW_READY to DONE RECENTLY in tasks/ACTIVE.md.")
        else:
            lines.append(
                "- No direct file update is suggested until the task reaches "
                "REVIEW_READY and merge is confirmed."
            )

    return "\n".join(lines)
