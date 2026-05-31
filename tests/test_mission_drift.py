"""Tests for the advisory mission-drift checker (TASK-0497)."""

from __future__ import annotations

from physics_lab.registry.mission_drift import (
    MissionDriftItem,
    _campaign_conflict_items,
    _task_reference_items,
    check_mission_drift,
)


def _payload(actions=None, support=None, missions_extra=None):
    mission = {"id": "demo", "actions": actions or []}
    if missions_extra:
        mission.update(missions_extra)
    return {"missions": [mission], "support_actions": support or [], "maintainer_actions": []}


def test_stale_task_reference_flags_done_blocked_superseded() -> None:
    payload = _payload(
        actions=[
            {"id": "a1", "recommended": True, "task_id": "TASK-0001"},
            {"id": "a2", "recommended": True, "task_id": "TASK-0002"},
            {"id": "a3", "recommended": True, "task_id": "TASK-0003"},
        ]
    )
    statuses = {"TASK-0001": "DONE", "TASK-0002": "BLOCKED", "TASK-0003": "SUPERSEDED"}
    items = _task_reference_items(payload, statuses)
    kinds = {i.kind for i in items}
    assert kinds == {"stale_task_reference"}
    assert len(items) == 3
    assert all(not i.advisory_only for i in items)


def test_missing_task_reference_is_drift() -> None:
    payload = _payload(actions=[{"id": "a1", "recommended": True, "task_id": "TASK-9999"}])
    items = _task_reference_items(payload, {})
    assert len(items) == 1
    assert items[0].kind == "missing_task_reference"


def test_review_ready_reference_is_advisory_only() -> None:
    payload = _payload(actions=[{"id": "a1", "recommended": True, "task_id": "TASK-0001"}])
    items = _task_reference_items(payload, {"TASK-0001": "REVIEW_READY"})
    assert len(items) == 1
    assert items[0].kind == "transient_task_reference"
    assert items[0].advisory_only is True


def test_ready_reference_is_not_flagged() -> None:
    payload = _payload(actions=[{"id": "a1", "recommended": True, "task_id": "TASK-0001"}])
    assert _task_reference_items(payload, {"TASK-0001": "READY"}) == []


def test_non_current_action_is_skipped() -> None:
    # status 'done' action is not a current recommendation -> not checked.
    payload = _payload(actions=[{"id": "a1", "status": "done", "task_id": "TASK-0001"}])
    assert _task_reference_items(payload, {"TASK-0001": "DONE"}) == []


def test_support_action_is_always_checked() -> None:
    payload = _payload(support=[{"id": "s1", "task_id": "TASK-0001"}])
    items = _task_reference_items(payload, {"TASK-0001": "DONE"})
    assert len(items) == 1 and items[0].kind == "stale_task_reference"


def test_campaign_conflict_flags_non_actionable_catalog_status() -> None:
    payload = {"missions": [{"id": "nuclear-mass-surface"}]}
    items = _campaign_conflict_items(payload, {"nuclear-mass-surface": "superseded"})
    assert len(items) == 1 and items[0].kind == "campaign_conflict"


def test_dangling_campaign_flagged_when_absent_from_catalog() -> None:
    payload = {"missions": [{"id": "ghost-campaign"}]}
    items = _campaign_conflict_items(payload, {"nuclear-mass-surface": "flagship_validation"})
    assert len(items) == 1 and items[0].kind == "dangling_campaign"


def test_campaign_in_catalog_with_active_status_is_clean() -> None:
    payload = {"missions": [{"id": "nuclear-mass-surface"}]}
    assert _campaign_conflict_items(payload, {"nuclear-mass-surface": "flagship_validation"}) == []


def test_check_mission_drift_runs_on_live_repo() -> None:
    report = check_mission_drift(".")
    assert isinstance(report.items, tuple)
    for item in report.items:
        assert isinstance(item, MissionDriftItem)
