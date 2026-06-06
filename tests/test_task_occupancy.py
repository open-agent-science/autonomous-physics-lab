"""Unit tests for live task PR occupancy classification.

Regression coverage for TASK-0662: a merged TASK-QUEUE (or TASK-PROPOSAL) PR
that *creates* tasks lists their ids in its body, but must not mark those
newly created READY tasks as occupied or merged-pending-closeout.
"""

from __future__ import annotations

from physics_lab.registry.task_occupancy import (
    classify_task_pr_occupancy,
    implementation_task_ids,
    occupancy_by_task_id,
)


def test_merged_task_queue_pr_does_not_occupy_seeded_tasks() -> None:
    seeded = ["TASK-0635", "TASK-0640", "TASK-0641", "TASK-0657"]
    queue_pr = {
        "number": 928,
        "title": "TASK-QUEUE: Seed science director next wave",
        "body": "Queues " + ", ".join(seeded) + " as READY.",
        "state": "MERGED",
        "mergedAt": "2026-06-06T18:10:52Z",
        "headRefName": "agent/roman/codex/task-queue-science-director-next-wave",
    }

    occupancy = occupancy_by_task_id(seeded, [queue_pr])

    assert [occupancy[task_id].classification for task_id in seeded] == [
        "apparently_free"
    ] * len(seeded)
    assert all(occupancy[task_id].is_available for task_id in seeded)


def test_merged_task_proposal_pr_does_not_occupy_referenced_task() -> None:
    proposal_pr = {
        "number": 929,
        "title": "TASK-PROPOSAL: Fix task occupancy false positive",
        "body": "Scopes a future fix related to TASK-0617.",
        "state": "MERGED",
        "mergedAt": "2026-06-06T19:00:00Z",
        "headRefName": "agent/roman/claude/propose-task-fix-occupancy-false-positive",
    }

    (occupancy,) = classify_task_pr_occupancy(["TASK-0617"], [proposal_pr])

    assert occupancy.classification == "apparently_free"
    assert occupancy.is_available


def test_open_implementation_pr_marks_task_occupied() -> None:
    impl_pr = {
        "number": 10,
        "title": "TASK-0005: open implementation",
        "body": "",
        "state": "OPEN",
        "mergedAt": None,
        "headRefName": "agent/roman/codex/task-0005-open",
    }

    (occupancy,) = classify_task_pr_occupancy(["TASK-0005"], [impl_pr])

    assert occupancy.classification == "occupied"
    assert occupancy.reasons == ("open PR #10",)


def test_merged_implementation_pr_marks_pending_closeout_via_branch_only() -> None:
    # Title omits the id; the canonical branch alone must still be detected.
    impl_pr = {
        "number": 11,
        "title": "Implement the thing",
        "body": "",
        "state": "MERGED",
        "mergedAt": "2026-06-01T00:00:00Z",
        "headRefName": "agent/roman/codex/task-0006-merged",
    }

    (occupancy,) = classify_task_pr_occupancy(["TASK-0006"], [impl_pr])

    assert occupancy.classification == "merged_pending_closeout"
    assert occupancy.reasons == ("merged PR #11 pending local closeout",)


def test_open_implementation_pr_outranks_merged_queue_mention() -> None:
    records = [
        {
            "number": 11,
            "title": "TASK-QUEUE: seed wave",
            "body": "Queues TASK-0005.",
            "state": "MERGED",
            "mergedAt": "2026-06-01T00:00:00Z",
            "headRefName": "agent/roman/codex/task-queue-seed-wave",
        },
        {
            "number": 12,
            "title": "TASK-0005: real implementation",
            "body": "",
            "state": "OPEN",
            "mergedAt": None,
            "headRefName": "agent/roman/codex/task-0005-impl",
        },
    ]

    (occupancy,) = classify_task_pr_occupancy(["TASK-0005"], records)

    assert occupancy.classification == "occupied"
    assert occupancy.reasons == ("open PR #12",)


def test_implementation_task_ids_uses_title_and_branch_only() -> None:
    assert implementation_task_ids("TASK-0005: thing", "") == ("TASK-0005",)
    assert implementation_task_ids("", "agent/roman/codex/task-0006-slug") == (
        "TASK-0006",
    )
    assert implementation_task_ids(
        "TASK-0007: thing", "agent/roman/codex/task-0007-slug"
    ) == ("TASK-0007",)
    # Task-creation/reference shapes contribute nothing.
    assert implementation_task_ids("TASK-QUEUE: seed", "agent/x/y/task-queue-seed") == ()
    assert (
        implementation_task_ids(
            "TASK-PROPOSAL: idea", "agent/x/y/propose-task-idea"
        )
        == ()
    )
    assert implementation_task_ids(None, None) == ()
