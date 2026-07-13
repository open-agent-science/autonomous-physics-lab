"""Regression tests for the shared prospective-reveal source-admissibility policy (TASK-1036)."""

from copy import deepcopy
import json
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY = REPO_ROOT / "docs" / "prospective-reveal-source-admissibility.md"
TASK_SCHEMA = REPO_ROOT / "physics_lab" / "schemas" / "task.schema.json"

REQUIRED_INVARIANTS = (
    "official metadata surfaces",
    "search-result snippets",
    "forbidden** for target-aware scouting",
    "BLOCKED_NO_PEEK_AUDIT",
    "source_discovery_mode: official_metadata_only",
    "search_result_snippets_allowed: false",
    "target_matching_requires_manifest_approval: true",
    "value_access_requires_reveal_task: true",
    "no_peek_context_status: contaminated",
    "prospective_reveal_eligibility: false",
    "maintainer-reviewed",
)

BACKLINKED_DOCS = (
    "docs/nuclear-prediction-reveal-protocol.md",
    "docs/nuclear-reveal-source-readiness-checklist.md",
    "docs/reviews/frb-reveal-source-admissibility-contract.md",
)


def test_shared_policy_exists_with_invariants():
    text = POLICY.read_text(encoding="utf-8")
    for invariant in REQUIRED_INVARIANTS:
        assert invariant in text, f"policy missing invariant: {invariant!r}"


def test_domain_protocols_reference_shared_policy():
    for rel in BACKLINKED_DOCS:
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert "prospective-reveal-source-admissibility.md" in text, rel


def test_task_template_carries_reveal_scout_fields():
    text = (REPO_ROOT / "tasks" / "TASK-TEMPLATE.yaml").read_text(encoding="utf-8")
    for field in (
        "source_discovery_mode: official_metadata_only",
        "search_result_snippets_allowed: false",
        "no_peek_context_status: clean",
    ):
        assert field in text, f"template missing reveal-scout field: {field}"


def _reveal_scout_task(*, mode: str) -> dict:
    input_payload = {
        "mode": mode,
        "related_domain": "nuclear_physics",
        "related_objects": ["PRED-0069"],
        "planning_context": "Locate official metadata without accessing values.",
        "source_discovery_mode": "official_metadata_only",
        "search_result_snippets_allowed": False,
        "target_matching_requires_manifest_approval": True,
        "value_access_requires_reveal_task": True,
        "no_peek_context_status": "clean",
        "prospective_reveal_eligibility": True,
    }
    return {
        "id": "TASK-9999",
        "title": "Prospective reveal scout fixture",
        "type": "scientific_source_curation",
        "status": "READY",
        "difficulty": "medium",
        "priority": "high",
        "input": input_payload,
        "requirements": ["Preserve no-peek eligibility."],
        "accepted_outputs": ["An approved source manifest."],
        "can_be_done_by": ["human", "agent"],
    }


@pytest.mark.parametrize("mode", ["planning_only", "workflow"])
def test_task_schema_accepts_enforced_reveal_scout_contract(mode: str):
    schema = json.loads(TASK_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(instance=_reveal_scout_task(mode=mode), schema=schema)


@pytest.mark.parametrize(
    ("field", "unsafe_value"),
    [
        ("source_discovery_mode", "open_web_search"),
        ("search_result_snippets_allowed", True),
        ("target_matching_requires_manifest_approval", False),
        ("value_access_requires_reveal_task", False),
        ("no_peek_context_status", "unknown"),
    ],
)
def test_task_schema_rejects_weakened_reveal_scout_contract(
    field: str, unsafe_value: object
):
    schema = json.loads(TASK_SCHEMA.read_text(encoding="utf-8"))
    task = deepcopy(_reveal_scout_task(mode="planning_only"))
    task["input"][field] = unsafe_value

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=task, schema=schema)
