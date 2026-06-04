"""Validation helpers for mission-currentness and recommendation freshness."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from physics_lab.registry.mission_control import load_current_missions
from physics_lab.registry.task_discovery import iter_canonical_task_files
from physics_lab.registry.tasks import load_task


CURRENT_ACTION_INACTIVE_STATUSES = {"done", "review_ready", "blocked", "review_required"}
DISALLOWED_TASK_STATUSES = {
    "DONE",
    "BLOCKED",
    "REJECTED",
    "SUPERSEDED",
    "PROPOSED",
}
# REVIEW_READY is a normal transient lifecycle state: an agent reaches it the
# moment it finishes a task, before maintainer closeout moves the task to DONE.
# A mission action that still references such a task is only transiently stale,
# so it is reported as INFO (non-failing under --fail-on-warnings) rather than
# blocking the agent's own REVIEW_READY transition. See TASK-0466.
INFO_TASK_STATUSES = {"REVIEW_READY"}
RECOMMENDED_MISSION_PATTERN = re.compile(
    r"## Recommended Mission Now(?P<section>.*?)(?:\n## |\Z)",
    re.DOTALL,
)
MISSION_TITLE_PATTERN = re.compile(r"\*\*(?P<title>[^*]+)\*\*")
CURATOR_DECISIONS = {"updated", "no_change"}


@dataclass(frozen=True)
class MissionFreshnessIssue:
    """Structured freshness issue for mission recommendation state."""

    severity: str
    code: str
    message: str
    path: str | None = None


def validate_mission_freshness(root: Path) -> tuple[MissionFreshnessIssue, ...]:
    """Return mission freshness issues derived from canonical state."""
    mission_path = root / "missions" / "current.yaml"
    if not mission_path.exists():
        return ()
    payload = load_current_missions(root)
    issues: list[MissionFreshnessIssue] = []
    issues.extend(_validate_curator_cycle(payload))
    issues.extend(_validate_current_task_references(root, payload))
    issues.extend(_validate_recommended_mission_title(root, payload))
    return tuple(issues)


def _validate_curator_cycle(payload: dict[str, Any]) -> list[MissionFreshnessIssue]:
    curator_cycle = payload.get("curator_cycle")
    if not isinstance(curator_cycle, dict):
        return [
            MissionFreshnessIssue(
                severity="WARNING",
                code="mission_missing_curator_cycle",
                message=(
                    "missions/current.yaml should record curator_cycle metadata with "
                    "decision, updated date, source, and note."
                ),
                path="missions/current.yaml",
            )
        ]
    issues: list[MissionFreshnessIssue] = []
    decision = str(curator_cycle.get("decision") or "").strip()
    updated = str(curator_cycle.get("updated") or "").strip()
    source = str(curator_cycle.get("source") or "").strip()
    note = str(curator_cycle.get("note") or "").strip()
    if decision not in CURATOR_DECISIONS:
        issues.append(
            MissionFreshnessIssue(
                severity="WARNING",
                code="mission_invalid_curator_decision",
                message=(
                    "curator_cycle.decision must be one of: "
                    + ", ".join(sorted(CURATOR_DECISIONS))
                ),
                path="missions/current.yaml",
            )
        )
    if not updated or not source or not note:
        issues.append(
            MissionFreshnessIssue(
                severity="WARNING",
                code="mission_incomplete_curator_cycle",
                message=(
                    "curator_cycle must include non-empty updated, source, and note fields."
                ),
                path="missions/current.yaml",
            )
        )
    return issues


def _validate_current_task_references(
    root: Path,
    payload: dict[str, Any],
) -> list[MissionFreshnessIssue]:
    issues: list[MissionFreshnessIssue] = []
    task_statuses = _task_statuses(root)

    for mission in payload.get("missions", []):
        if not isinstance(mission, dict):
            continue
        mission_id = str(mission.get("id") or "<unknown>")
        for action in mission.get("actions", []):
            if not isinstance(action, dict):
                continue
            action_status = str(action.get("status", "")).lower()
            is_current = bool(action.get("recommended")) or (
                action_status == "" or action_status == "ready"
            )
            if not is_current or action_status in CURRENT_ACTION_INACTIVE_STATUSES:
                continue
            task_id = str(action.get("task_id") or "").strip()
            if not task_id:
                continue
            issues.extend(
                _task_reference_issues(
                    task_statuses,
                    task_id=task_id,
                    owner=f"missions/current.yaml mission {mission_id} action {action.get('id')}",
                )
            )

    for section_name in ("support_actions", "maintainer_actions"):
        for action in payload.get(section_name, []):
            if not isinstance(action, dict):
                continue
            task_id = str(action.get("task_id") or "").strip()
            if not task_id:
                continue
            issues.extend(
                _task_reference_issues(
                    task_statuses,
                    task_id=task_id,
                    owner=f"missions/current.yaml {section_name} action {action.get('id')}",
                )
            )
    return issues


def _validate_recommended_mission_title(
    root: Path,
    payload: dict[str, Any],
) -> list[MissionFreshnessIssue]:
    missions = [
        mission
        for mission in payload.get("missions", [])
        if isinstance(mission, dict)
    ]
    if not missions:
        return []
    top_mission = min(missions, key=lambda mission: int(mission.get("rank", 999)))
    expected_title = str(top_mission.get("title") or "").strip()
    if not expected_title:
        return []

    doc_path = root / "docs" / "current-missions.md"
    if not doc_path.exists():
        return [
            MissionFreshnessIssue(
                severity="ERROR",
                code="mission_missing_current_missions_doc",
                message="docs/current-missions.md is missing while missions/current.yaml exists.",
                path="docs/current-missions.md",
            )
        ]
    content = doc_path.read_text(encoding="utf-8")
    section_match = RECOMMENDED_MISSION_PATTERN.search(content)
    if section_match is None:
        return [
            MissionFreshnessIssue(
                severity="ERROR",
                code="mission_missing_recommended_section",
                message=(
                    "docs/current-missions.md must contain a 'Recommended Mission Now' section."
                ),
                path="docs/current-missions.md",
            )
        ]
    title_match = MISSION_TITLE_PATTERN.search(section_match.group("section"))
    actual_title = title_match.group("title").strip() if title_match else ""
    if actual_title != expected_title:
        return [
            MissionFreshnessIssue(
                severity="ERROR",
                code="mission_flagship_mismatch",
                message=(
                    "Top-ranked mission title in missions/current.yaml does not match the "
                    "flagship named in docs/current-missions.md."
                ),
                path="docs/current-missions.md",
            )
        ]
    return []


def _task_statuses(root: Path) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for path in iter_canonical_task_files(root):
        payload = load_task(path)
        statuses[str(payload["id"])] = str(payload["status"])
    return statuses


def _task_reference_issues(
    task_statuses: dict[str, str],
    *,
    task_id: str,
    owner: str,
) -> list[MissionFreshnessIssue]:
    task_status = task_statuses.get(task_id)
    if task_status is None:
        return [
            MissionFreshnessIssue(
                severity="ERROR",
                code="mission_missing_task_reference",
                message=f"{owner} references missing canonical task {task_id}.",
                path="missions/current.yaml",
            )
        ]
    if task_status in INFO_TASK_STATUSES:
        return [
            MissionFreshnessIssue(
                severity="INFO",
                code="mission_review_ready_task_reference",
                message=(
                    f"{owner} references {task_id} with transient status {task_status}. "
                    "This is expected right after task handoff; the mission action can be "
                    "refreshed at maintainer closeout. Agents do not need to edit "
                    "missions/current.yaml for their own REVIEW_READY transition."
                ),
                path="missions/current.yaml",
            )
        ]
    if task_status in DISALLOWED_TASK_STATUSES:
        return [
            MissionFreshnessIssue(
                severity="ERROR",
                code="mission_stale_task_reference",
                message=(
                    f"{owner} references {task_id} with non-actionable status {task_status}. "
                    "Use a READY task, a command-only action, or live task candidates instead."
                ),
                path="missions/current.yaml",
            )
        ]
    return []
