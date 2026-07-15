from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SURFACE = ROOT / "knowledge" / "challenge_sets" / "dimensional_analysis_challenge_set_v2.yaml"


def _load() -> dict:
    return yaml.safe_load(SURFACE.read_text(encoding="utf-8"))


def test_v2_freeze_contract_is_role_bounded_and_unscored() -> None:
    data = _load()
    curation = data["curation"]
    no_score = data["no_score_declaration"]

    assert data["scoring_contract_id"] == "label_blind_exact_v2"
    assert curation["benchmark_authorship_independence"] == "same_owner_role_disjoint_agent"
    assert curation["bounded_verdict"] == "CALIBRATION_ONLY_ROLE_LIMIT"
    assert curation["contributor_id"]
    assert curation["agent_tool"]
    assert curation["session_id"]
    assert curation["inspected_task_1038_implementation"] is False
    assert curation["inspected_validator_outputs"] is False
    assert no_score["validator_executed"] is False
    assert no_score["computed_output_inspected"] is False
    assert no_score["tuned_against_engine_behavior"] is False
    assert no_score["curator_session_id"] == curation["session_id"]


def test_v2_items_have_native_labels_balance_and_provenance() -> None:
    data = _load()
    items = data["items"]
    source_ids = {source["source_id"] for source in data["source_ledger"]}

    assert data["total_items"] == len(items) == 80
    assert len({item["id"] for item in items}) == len(items)
    assert len({item["formula"] for item in items}) == len(items)
    assert len({item["domain"] for item in items}) >= 5

    labels = Counter(item["expected_verdict"] for item in items)
    assert set(labels) <= {"VALID", "INVALID", "INCONCLUSIVE"}
    assert labels["VALID"] == 40
    assert labels["INVALID"] == 40
    assert labels["INCONCLUSIVE"] / len(items) <= data["freeze_contract"]["inconclusive_ceiling"]
    assert 0.40 <= labels["VALID"] / len(items) <= 0.60
    assert 0.40 <= labels["INVALID"] / len(items) <= 0.60

    for item in items:
        assert item["variables"]
        assert item["rationale"]
        assert item["source_note"]
        assert item["source_id"] in source_ids
        assert item["dimension_reference"] == "SRC-BIPM-SI"
        assert item["reuse_classification"] == "bounded_factual_formula_metadata"
        assert set(item["annotations"]) == {
            "known_limit",
            "semantic_suspicion",
            "numerical_correctness",
            "regime",
        }


def test_v2_order_digest_thresholds_and_overlap_audit_are_frozen() -> None:
    data = _load()
    freeze = data["freeze_contract"]
    items = data["items"]
    payload = "\n".join(
        f'{item["id"]}|{item["formula"]}|{item["expected_verdict"]}' for item in items
    ).encode("utf-8")

    assert hashlib.sha256(payload).hexdigest() == freeze["item_order_digest"]
    assert freeze["exact_agreement_threshold"] >= 0.90
    assert freeze["valid_recall_floor"] >= 0.85
    assert freeze["invalid_recall_floor"] >= 0.85
    overlap = freeze["historical_overlap_audit"]
    assert overlap["exact_duplicate_count"] + overlap["conceptual_near_duplicate_count"] <= overlap[
        "maximum_allowed_count"
    ]
    assert freeze["duplicate_policy"]
    assert freeze["parser_scope_exclusions"]
    assert set(freeze["stop_go_routing"]) == {"PASS", "FAIL", "CONTAMINATED"}
