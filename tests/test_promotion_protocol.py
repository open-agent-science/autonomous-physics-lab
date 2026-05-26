"""Tests for the TASK-0406 multi-class promotion protocol.

These tests verify:
- the master protocol document exists and contains the seven canonical output classes;
- the verdict-to-class mapping rule is present;
- the multi-tier review model documents all three tiers;
- the generic prediction.schema.json validates a minimal in-memory fixture;
- existing per-domain policies cross-reference the master protocol.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = REPO_ROOT / "docs" / "result-promotion-protocol.md"
PRED_SCHEMA_PATH = (
    REPO_ROOT / "physics_lab" / "schemas" / "prediction.schema.json"
)
PRED_REGISTRY_README = REPO_ROOT / "prediction_registry" / "README.md"


# ---------------------------------------------------------------------------
# Master protocol document
# ---------------------------------------------------------------------------


class TestMasterProtocolDocument:
    def test_protocol_file_exists(self) -> None:
        assert PROTOCOL_PATH.exists(), PROTOCOL_PATH

    def test_protocol_lists_seven_output_classes(self) -> None:
        text = PROTOCOL_PATH.read_text(encoding="utf-8")
        # Each of the seven classes must be named in the document body.
        required_class_phrases = (
            "Benchmark result",
            "Validated-in-scope result",
            "Negative / falsification result",
            "Partially valid result",
            "Prediction awaiting reveal",
            "Claim",
            "Knowledge",
        )
        for phrase in required_class_phrases:
            assert phrase in text, phrase

    def test_protocol_documents_verdict_mapping_rule(self) -> None:
        text = PROTOCOL_PATH.read_text(encoding="utf-8")
        assert "Verdict-to-Class Mapping Rule" in text
        # Every verdict vocabulary item must appear at least once in the
        # mapping table.
        required_verdicts = (
            "VALID",
            "VALID_IN_RANGE",
            "PARTIALLY_VALID",
            "INCONCLUSIVE",
            "OVERFITTED",
            "FALSIFIED",
        )
        for verdict in required_verdicts:
            assert verdict in text, verdict

    def test_protocol_documents_three_review_tiers(self) -> None:
        text = PROTOCOL_PATH.read_text(encoding="utf-8")
        for tier in (
            "AGENT_PROPOSED",
            "MAINTAINER_REVIEWED",
            "EXTERNAL_REPLICATED",
        ):
            assert tier in text, tier

    def test_protocol_documents_self_evaluation_block(self) -> None:
        text = PROTOCOL_PATH.read_text(encoding="utf-8")
        assert "agent_proposal_evaluation" in text
        assert "gates_checked" in text

    def test_protocol_explains_pathway_to_new_knowledge(self) -> None:
        text = PROTOCOL_PATH.read_text(encoding="utf-8")
        # The document must explicitly explain how new scientific
        # knowledge is generated under the protocol.
        assert "Pathway to New Scientific Knowledge" in text
        assert "First Sprint" in text


# ---------------------------------------------------------------------------
# Generic prediction schema
# ---------------------------------------------------------------------------


def _load_schema() -> dict:
    return json.loads(PRED_SCHEMA_PATH.read_text(encoding="utf-8"))


def _minimal_valid_prediction() -> dict:
    """A minimal but valid generic prediction payload.

    All required top-level fields are present with the simplest legal
    content. Domain-specific extensions may add stricter target-set
    requirements.
    """
    return {
        "prediction_id": "PRED-9999",
        "title": "Test generic prediction",
        "registry_status": "REGISTERED",
        "campaign_profile_id": "test-campaign",
        "task_id": "TASK-9999",
        "evidence_class": "prospective_prediction_registry",
        "claim_ceiling": (
            "Registered prospective prediction only; no claim until later "
            "maintainer-reviewed comparison."
        ),
        "registered_by": {
            "contributor_id": "test",
            "agent_id": "test_agent",
        },
        "registered_at_utc": "2026-05-26T00:00:00Z",
        "source_state": {
            "git_commit": "deadbeefcafebabe",
            "model_reference": {"model_id": "TEST-MODEL-001"},
            "live_external_fetch_allowed": False,
        },
        "target_set": {
            "label": "test-targets",
            "quantity": "test_quantity",
            "unit": "test_unit",
        },
        "uncertainty_semantics": "Point estimate only.",
        "reveal_conditions": {
            "comparison_source_class": "future_reviewed_source",
            "reveal_controlled_by": "maintainer",
            "no_peek_rule": "No reveal-relevant measurement is read at registration time.",
        },
        "limitations": [
            "Generic schema test; not a real scientific prediction.",
        ],
    }


class TestPredictionSchema:
    def test_schema_file_exists(self) -> None:
        assert PRED_SCHEMA_PATH.exists(), PRED_SCHEMA_PATH

    def test_schema_parses_as_json(self) -> None:
        schema = _load_schema()
        assert isinstance(schema, dict)
        assert schema.get("title", "").startswith("Prediction")

    def test_minimal_valid_prediction_passes(self) -> None:
        schema = _load_schema()
        jsonschema.validate(instance=_minimal_valid_prediction(), schema=schema)

    def test_missing_required_field_fails(self) -> None:
        schema = _load_schema()
        invalid = _minimal_valid_prediction()
        del invalid["claim_ceiling"]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid, schema=schema)

    def test_bad_prediction_id_pattern_fails(self) -> None:
        schema = _load_schema()
        invalid = _minimal_valid_prediction()
        invalid["prediction_id"] = "PREDICTION-1"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid, schema=schema)

    def test_live_external_fetch_must_be_false(self) -> None:
        schema = _load_schema()
        invalid = _minimal_valid_prediction()
        invalid["source_state"]["live_external_fetch_allowed"] = True
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid, schema=schema)

    def test_review_tier_enum_accepted(self) -> None:
        schema = _load_schema()
        valid = _minimal_valid_prediction()
        valid["review_tier"] = "AGENT_PROPOSED"
        valid["agent_proposal_evaluation"] = {
            "review_tier_proposed": "AGENT_PROPOSED",
            "gates_checked": {"no_peek_state": True},
            "evidence_summary": "Agent self-evaluation block for test.",
        }
        jsonschema.validate(instance=valid, schema=schema)

    def test_review_tier_invalid_value_fails(self) -> None:
        schema = _load_schema()
        invalid = _minimal_valid_prediction()
        invalid["review_tier"] = "WHATEVER_TIER"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid, schema=schema)

    def test_agent_proposal_evaluation_requires_proposed_tier_value(self) -> None:
        schema = _load_schema()
        invalid = _minimal_valid_prediction()
        invalid["review_tier"] = "AGENT_PROPOSED"
        invalid["agent_proposal_evaluation"] = {
            "review_tier_proposed": "MAINTAINER_REVIEWED",
            "gates_checked": {"no_peek_state": True},
            "evidence_summary": "Mismatched tier value.",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid, schema=schema)


# ---------------------------------------------------------------------------
# Cross-references
# ---------------------------------------------------------------------------


class TestCrossReferences:
    def test_prediction_registry_readme_exists(self) -> None:
        assert PRED_REGISTRY_README.exists(), PRED_REGISTRY_README

    def test_prediction_registry_readme_references_master_protocol(self) -> None:
        text = PRED_REGISTRY_README.read_text(encoding="utf-8")
        assert "result-promotion-protocol.md" in text

    def test_agents_md_references_master_protocol(self) -> None:
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        assert "docs/result-promotion-protocol.md" in agents

    def test_claim_policy_references_master_protocol(self) -> None:
        text = (REPO_ROOT / "docs" / "claim-promotion-policy.md").read_text(
            encoding="utf-8"
        )
        assert "result-promotion-protocol.md" in text

    def test_prediction_policy_references_master_protocol(self) -> None:
        text = (REPO_ROOT / "docs" / "prediction-registry-policy.md").read_text(
            encoding="utf-8"
        )
        assert "result-promotion-protocol.md" in text
