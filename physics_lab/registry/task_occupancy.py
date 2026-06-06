"""Live advisory task occupancy classification from GitHub PR metadata."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping


TASK_ID_PATTERN = re.compile(r"\bTASK-\d{4}\b", re.IGNORECASE)
OCCUPIED_PR_STATES = frozenset({"OPEN"})
MERGED_PENDING_CLOSEOUT_STATES = frozenset({"MERGED"})


@dataclass(frozen=True)
class TaskOccupancy:
    task_id: str
    classification: str
    reasons: tuple[str, ...]

    @property
    def is_available(self) -> bool:
        return self.classification == "apparently_free"

    def to_json(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "classification": self.classification,
            "available": self.is_available,
            "reasons": list(self.reasons),
        }


def task_ids_from_text(*values: object) -> tuple[str, ...]:
    combined = " ".join(str(value or "") for value in values)
    return tuple(sorted({task_id.upper() for task_id in TASK_ID_PATTERN.findall(combined)}))


def classify_task_pr_occupancy(
    task_ids: Iterable[str],
    pr_records: Iterable[Mapping[str, Any]],
) -> tuple[TaskOccupancy, ...]:
    """Classify selected task ids using GitHub PR JSON records.

    The helper is intentionally advisory. It only needs enough PR metadata to
    prevent accidental duplicate task execution, so it scans title, body, and
    headRefName for task ids and leaves final routing to the maintainer.
    """

    normalized_task_ids = tuple(dict.fromkeys(str(task_id).strip() for task_id in task_ids))
    reasons: dict[str, list[str]] = {task_id: [] for task_id in normalized_task_ids}
    classifications: dict[str, str] = {
        task_id: "apparently_free" for task_id in normalized_task_ids
    }

    for record in pr_records:
        state = str(record.get("state") or "").upper()
        if state not in OCCUPIED_PR_STATES | MERGED_PENDING_CLOSEOUT_STATES:
            continue
        number = record.get("number")
        pr_task_ids = task_ids_from_text(
            record.get("title"),
            record.get("body"),
            record.get("headRefName"),
        )
        for task_id in pr_task_ids:
            if task_id not in reasons:
                continue
            if state in OCCUPIED_PR_STATES:
                classifications[task_id] = "occupied"
                reasons[task_id].append(f"open PR #{number}")
            elif classifications[task_id] != "occupied":
                classifications[task_id] = "merged_pending_closeout"
                reasons[task_id].append(f"merged PR #{number} pending local closeout")

    return tuple(
        TaskOccupancy(
            task_id=task_id,
            classification=classifications[task_id],
            reasons=tuple(dict.fromkeys(reasons[task_id])),
        )
        for task_id in normalized_task_ids
    )


def occupancy_by_task_id(
    task_ids: Iterable[str],
    pr_records: Iterable[Mapping[str, Any]],
) -> dict[str, TaskOccupancy]:
    return {
        item.task_id: item
        for item in classify_task_pr_occupancy(task_ids, pr_records)
    }
