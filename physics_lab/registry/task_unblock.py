"""Conservative helpers for closeout-time task unblocking."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from physics_lab.registry.tasks import load_task


TASK_ID_PATTERN = re.compile(r"TASK-[0-9]{4}")
SAFE_REMAIN_BLOCKED_PATTERN = re.compile(
    r"^\s*Remain\s+BLOCKED\s+until\s+(?P<clause>.+?)(?:,\s+or\s+until\b|$)",
    re.IGNORECASE,
)
SAFE_CLAUSE_ALLOWED_PATTERN = re.compile(
    r"^(?:\s|TASK-[0-9]{4}|and|is|are|DONE|\.|,)+$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SafeUnblockCandidate:
    """One BLOCKED task evaluated for deterministic closeout unblocking."""

    task_id: str
    task_title: str
    task_file: Path
    dependencies: tuple[str, ...]
    missing_dependencies: tuple[str, ...]
    safe_to_unblock: bool
    reason: str


def safe_unblock_candidates(root: Path) -> tuple[SafeUnblockCandidate, ...]:
    """Return BLOCKED tasks whose explicit task dependencies can be evaluated.

    This intentionally recognizes only a narrow opt-in wording:
    ``Remain BLOCKED until TASK-XXXX and TASK-YYYY are DONE``. Broader wording
    often hides scientific, source-access, maintainer-waiver, or artifact
    existence decisions, so it is left for human review rather than automated
    closeout unblocking.
    """
    statuses = _task_statuses(root)
    candidates: list[SafeUnblockCandidate] = []
    for task_file in sorted((root / "tasks").glob("TASK-*.yaml")):
        if task_file.name == "TASK-TEMPLATE.yaml":
            continue
        payload = load_task(task_file)
        if str(payload["status"]) != "BLOCKED":
            continue

        dependencies = _safe_done_dependencies(payload)
        if dependencies is None:
            continue

        missing = tuple(task_id for task_id in dependencies if statuses.get(task_id) != "DONE")
        if missing:
            reason = "Still blocked because dependency task(s) are not DONE: " + ", ".join(missing) + "."
        else:
            reason = (
                "Safe to unblock: explicit `Remain BLOCKED until ... are DONE` "
                "dependency clause is satisfied."
            )
        candidates.append(
            SafeUnblockCandidate(
                task_id=str(payload["id"]),
                task_title=str(payload["title"]),
                task_file=task_file,
                dependencies=dependencies,
                missing_dependencies=missing,
                safe_to_unblock=not missing,
                reason=reason,
            )
        )
    return tuple(candidates)


def _task_statuses(root: Path) -> dict[str, str]:
    """Load canonical task statuses keyed by task id."""
    statuses: dict[str, str] = {}
    for task_file in sorted((root / "tasks").glob("TASK-*.yaml")):
        if task_file.name == "TASK-TEMPLATE.yaml":
            continue
        payload = load_task(task_file)
        statuses[str(payload["id"])] = str(payload["status"])
    return statuses


def _safe_done_dependencies(payload: dict) -> tuple[str, ...] | None:
    """Extract explicit DONE dependencies from conservative blocker wording."""
    dependencies: list[str] = []
    for requirement in payload.get("requirements", []):
        match = SAFE_REMAIN_BLOCKED_PATTERN.match(str(requirement).strip())
        if match is None:
            continue
        clause = match.group("clause").strip()
        task_ids = TASK_ID_PATTERN.findall(clause)
        if not task_ids:
            return None
        if " or " in clause.lower():
            return None
        if SAFE_CLAUSE_ALLOWED_PATTERN.fullmatch(clause) is None:
            return None
        if "DONE" not in clause.upper():
            return None
        dependencies.extend(task_ids)

    if not dependencies:
        return None
    return tuple(dict.fromkeys(dependencies))
