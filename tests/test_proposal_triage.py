"""Tests for proposal-pool triage logic (TASK-0468)."""

from __future__ import annotations

import pytest

from physics_lab.registry.proposal_triage import (
    DuplicateCandidate,
    compute_proposal_state,
    duplicate_candidates,
    triage_pool,
    _is_science,
)


def _payload(
    *,
    proposal_id: str = "20260530-roman-demo-slug",
    status: str = "PROPOSED",
    proposal_type: str = "maintainer_workflow",
    related_domain: str = "cross_campaign_quality",
    promotion: dict | None = None,
) -> dict:
    payload = {
        "proposal_id": proposal_id,
        "title": "Demo",
        "status": status,
        "type": proposal_type,
        "input": {"related_domain": related_domain},
    }
    if promotion is not None:
        payload["promotion"] = promotion
    return payload


def _state(payload, statuses=None, references=None, rel_path="tasks/proposals/p.yaml"):
    return compute_proposal_state(rel_path, payload, statuses or {}, references or {})


def test_pending_when_no_link() -> None:
    state = _state(_payload())
    assert state.effective_state == "pending"
    assert state.drift == ()
    assert state.routing_target == "architect"  # infra default


def test_accepted_via_promotion_drifts_when_declared_proposed() -> None:
    state = _state(
        _payload(promotion={"canonical_task_id": "TASK-0001", "decision": "accepted"}),
        statuses={"TASK-0001": "READY"},
    )
    assert state.effective_state == "accepted"
    assert state.has_drift
    assert state.routing_target == "review-agent"


def test_resolved_when_canonical_task_done() -> None:
    state = _state(
        _payload(promotion={"canonical_task_id": "TASK-0001"}),
        statuses={"TASK-0001": "DONE"},
    )
    assert state.effective_state == "resolved"
    assert state.has_drift  # declared PROPOSED but delivered


def test_accepted_by_reference_without_promotion_block() -> None:
    # The stellar case: a canonical task references the proposal in
    # related_objects but the proposal has no promotion block.
    state = _state(
        _payload(promotion=None),
        statuses={"TASK-0444": "REVIEW_READY"},
        references={"p.yaml": ["TASK-0444"]},
    )
    assert state.linked_task_id == "TASK-0444"
    assert state.effective_state == "accepted"
    assert state.has_drift


def test_dangling_canonical_task_id_is_drift() -> None:
    state = _state(
        _payload(promotion={"canonical_task_id": "TASK-9999"}),
        statuses={},
    )
    assert any("does not exist" in reason for reason in state.drift)
    assert state.routing_target == "review-agent"


def test_clean_accepted_has_no_drift_and_no_routing() -> None:
    state = _state(
        _payload(status="ACCEPTED", promotion={"canonical_task_id": "TASK-0001"}),
        statuses={"TASK-0001": "READY"},
    )
    assert state.effective_state == "accepted"
    assert not state.has_drift
    assert state.routing_target == "none"


def test_science_proposal_routes_to_director() -> None:
    state = _state(_payload(proposal_type="scientific_dataset", related_domain="nuclear_mass_surface"))
    assert state.is_science
    assert state.routing_target == "scientific-director"


def test_ambiguous_proposal_is_unrouted() -> None:
    # Both a science and an infra signal -> cannot decide -> unrouted.
    state = _state(_payload(proposal_type="scientific_tooling", related_domain="methodology_workflow"))
    assert state.routing_target == "unrouted"
    # Neither signal -> also unrouted.
    blank = _state(_payload(proposal_type="idea", related_domain="general"))
    assert blank.routing_target == "unrouted"


def test_is_science_token_match_not_substring() -> None:
    # 'ci' must not match inside 'scientific'; this stays science, not infra.
    assert _is_science(_payload(proposal_type="knowledge_update", related_domain="scientific_memory"))
    # genuine infra
    assert not _is_science(_payload(proposal_type="tooling", related_domain="tooling"))
    assert not _is_science(_payload(proposal_type="maintainer_workflow", related_domain="cross_campaign_quality"))


def test_duplicate_candidates_flag_shared_slug_tokens() -> None:
    a = _state(_payload(proposal_id="20260530-roman-symmetry-discovery-validator"))
    b = _state(_payload(proposal_id="20260530-roman-symmetry-discovery-helper"))
    c = _state(_payload(proposal_id="20260530-roman-unrelated-idea"))
    candidates = duplicate_candidates((a, b, c))
    assert any(
        isinstance(cand, DuplicateCandidate)
        and "symmetry" in cand.shared
        and "discovery" in cand.shared
        for cand in candidates
    )
    # the unrelated one is not paired
    assert all("unrelated" not in c.left and "unrelated" not in c.right for c in candidates)


@pytest.mark.full_repo
def test_triage_pool_runs_on_live_repo() -> None:
    report = triage_pool(".")
    assert report.states  # the repo has proposals
    counts = report.counts()
    assert set(counts).issubset({"pending", "accepted", "resolved", "rejected", "superseded"})
