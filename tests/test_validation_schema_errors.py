"""Schema-error rendering tests (TASK-0467, P2)."""

from __future__ import annotations

import pytest

from physics_lab.registry.validation import validate_document


def _planning_only_proposal_missing_context() -> dict:
    return {
        "proposal_id": "20260530-roman-x",
        "title": "x",
        "status": "PROPOSED",
        "type": "maintainer_workflow",
        "priority": "medium",
        "proposed_by": {"contributor_id": "roman", "agent_id": "claude"},
        "strategy_alignment": ["x"],
        "summary": "x",
        "rationale": "x",
        # planning_context intentionally omitted -> fails the input oneOf
        "input": {
            "mode": "planning_only",
            "related_domain": "cross_campaign_quality",
            "related_objects": [],
        },
        "requirements": ["x"],
        "accepted_outputs": ["x"],
    }


def test_oneof_input_error_names_missing_field() -> None:
    with pytest.raises(ValueError) as excinfo:
        validate_document(
            _planning_only_proposal_missing_context(),
            kind="task_proposal",
            source="test.yaml",
        )
    message = str(excinfo.value)
    # The generic oneOf line is still present, but the closest branch must be
    # surfaced so the author sees the actual missing field.
    assert "closest match" in message
    assert "planning_context" in message


def test_simple_required_error_still_rendered() -> None:
    payload = _planning_only_proposal_missing_context()
    payload["input"]["planning_context"] = "ctx"
    del payload["title"]  # a plain top-level required-field violation
    with pytest.raises(ValueError) as excinfo:
        validate_document(payload, kind="task_proposal", source="test.yaml")
    assert "title" in str(excinfo.value)
