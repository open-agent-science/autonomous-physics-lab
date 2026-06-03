"""Advisory mission-drift checker (TASK-0497).

Detects when ``missions/current.yaml`` routes agents into work that canonical
state no longer supports: recommended actions pointing at DONE / BLOCKED /
REJECTED / SUPERSEDED / PROPOSED tasks, references to missing tasks, and mission
campaign recommendations that conflict with the generated campaign catalog.

This is a deliberately advisory layer built on top of the existing
``mission_freshness`` validation (which already flags non-actionable task
references during ``validate-repo --strict``). It does not duplicate that
validation into a second strict gate; it provides a standalone report and adds
the campaign-conflict dimension. It never rewrites ``missions/current.yaml``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.campaigns import campaign_catalog_path
from physics_lab.registry.mission_control import load_current_missions
from physics_lab.registry.mission_freshness import (
    DISALLOWED_TASK_STATUSES,
    INFO_TASK_STATUSES,
    _task_statuses,
)


# Catalog statuses that mean a campaign is not an actionable recommendation
# target. Kept conservative to avoid noisy false positives.
NON_ACTIONABLE_CAMPAIGN_STATUSES = frozenset(
    {"blocked", "superseded", "retired", "archived", "deprecated"}
)


@dataclass(frozen=True)
class MissionDriftItem:
    """One advisory mission-drift finding."""

    kind: str  # stale_task_reference | missing_task_reference | transient_task_reference | campaign_conflict | dangling_campaign
    owner: str
    detail: str
    advisory_only: bool = False  # True for transient (REVIEW_READY) notices


@dataclass(frozen=True)
class MissionDriftReport:
    """Result of a mission-drift scan."""

    items: tuple[MissionDriftItem, ...]

    def drift_items(self) -> tuple[MissionDriftItem, ...]:
        return tuple(item for item in self.items if not item.advisory_only)

    def of_kind(self, kind: str) -> tuple[MissionDriftItem, ...]:
        return tuple(item for item in self.items if item.kind == kind)

    @property
    def has_drift(self) -> bool:
        return bool(self.drift_items())


def _iter_action_task_refs(payload: dict[str, Any]):
    """Yield (owner, task_id) for mission/support/maintainer actions to check.

    Mirrors mission_freshness: mission-level actions are checked when they are a
    current recommendation (recommended, or empty/ready status); support and
    maintainer actions are always checked.
    """
    inactive = {"done", "review_ready", "blocked", "review_required"}
    for mission in payload.get("missions", []) or []:
        if not isinstance(mission, dict):
            continue
        mission_id = str(mission.get("id") or "<unknown>")
        for action in mission.get("actions", []) or []:
            if not isinstance(action, dict):
                continue
            action_status = str(action.get("status", "")).lower()
            is_current = bool(action.get("recommended")) or action_status in {"", "ready"}
            if not is_current or action_status in inactive:
                continue
            task_id = str(action.get("task_id") or "").strip()
            if task_id:
                yield (f"mission {mission_id} action {action.get('id')}", task_id)
    for section in ("support_actions", "maintainer_actions"):
        for action in payload.get(section, []) or []:
            if not isinstance(action, dict):
                continue
            task_id = str(action.get("task_id") or "").strip()
            if task_id:
                yield (f"{section} action {action.get('id')}", task_id)


def _task_reference_items(payload, statuses) -> list[MissionDriftItem]:
    items: list[MissionDriftItem] = []
    for owner, task_id in _iter_action_task_refs(payload):
        status = statuses.get(task_id)
        if status is None:
            items.append(
                MissionDriftItem(
                    kind="missing_task_reference",
                    owner=owner,
                    detail=f"references missing canonical task {task_id}",
                )
            )
        elif status in INFO_TASK_STATUSES:
            items.append(
                MissionDriftItem(
                    kind="transient_task_reference",
                    owner=owner,
                    detail=f"references {task_id} with transient status {status} "
                    "(expected right after handoff; refresh at closeout)",
                    advisory_only=True,
                )
            )
        elif status in DISALLOWED_TASK_STATUSES:
            items.append(
                MissionDriftItem(
                    kind="stale_task_reference",
                    owner=owner,
                    detail=f"routes agents into {task_id} which is {status}; "
                    "use a READY task, command-only action, or live candidates",
                )
            )
    return items


def _load_catalog_statuses(root: Path) -> dict[str, str]:
    path = campaign_catalog_path(root)
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    statuses: dict[str, str] = {}
    for campaign in data.get("campaigns", []) or []:
        if isinstance(campaign, dict) and campaign.get("id"):
            statuses[str(campaign["id"])] = str(campaign.get("status", "")).lower()
    return statuses


def _campaign_conflict_items(payload, catalog_statuses) -> list[MissionDriftItem]:
    items: list[MissionDriftItem] = []
    if not catalog_statuses:
        return items
    for mission in payload.get("missions", []) or []:
        if not isinstance(mission, dict):
            continue
        mission_id = str(mission.get("id") or "").strip()
        if not mission_id:
            continue
        if mission_id not in catalog_statuses:
            items.append(
                MissionDriftItem(
                    kind="dangling_campaign",
                    owner=f"mission {mission_id}",
                    detail=f"mission references campaign id {mission_id!r} not present "
                    "in campaign_profiles/_catalog.yaml",
                )
            )
            continue
        catalog_status = catalog_statuses[mission_id]
        if catalog_status in NON_ACTIONABLE_CAMPAIGN_STATUSES:
            items.append(
                MissionDriftItem(
                    kind="campaign_conflict",
                    owner=f"mission {mission_id}",
                    detail=f"mission still lists campaign {mission_id!r} while the catalog "
                    f"marks it {catalog_status!r}",
                )
            )
    return items


def check_mission_drift(root: str | Path) -> MissionDriftReport:
    """Return an advisory mission-drift report for missions/current.yaml."""
    root_path = Path(root)
    mission_path = root_path / "missions" / "current.yaml"
    if not mission_path.exists():
        return MissionDriftReport(items=())
    payload = load_current_missions(root_path)
    statuses = _task_statuses(root_path)
    catalog_statuses = _load_catalog_statuses(root_path)
    items = _task_reference_items(payload, statuses)
    items.extend(_campaign_conflict_items(payload, catalog_statuses))
    return MissionDriftReport(items=tuple(items))
