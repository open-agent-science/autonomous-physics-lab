"""Tests for the factory_summary artifact schema (TASK-0505)."""

from __future__ import annotations

import copy

import pytest

from physics_lab.registry.validation import validate_document

SOURCE = "agent_runs/AGENT-RUN-0001/factory_summary.yaml"


def _valid_summary() -> dict[str, object]:
    return {
        "schema_version": "1",
        "factory_id": "nuclear-residual-factory",
        "campaign_id": "nuclear-mass-surface",
        "adapter_id": "nuclear_residual_factory",
        "adapter_version": "0.1",
        "task_id": "TASK-0507",
        "dataset": {
            "snapshot_ref": "data/nuclear_masses/ame2020-snapshot.yaml",
            "retrieval_policy": "no_live_fetch",
            "checksum_policy": "sha256 recorded in source manifest",
        },
        "baseline": {"baseline_id": "nuclear-frozen-residual-surface", "baseline_type": "frozen"},
        "candidate_cap": 100,
        "candidate_counts": {
            "generated": 100,
            "preflight_rejected": 10,
            "executed": 90,
            "shortlisted": 2,
            "rejected_by_control": 60,
        },
        "controls": [
            {"name": "null_baseline", "outcome": "applied"},
            {"name": "shuffled_shell", "outcome": "applied"},
        ],
        "candidates": [
            {
                "candidate_id": "CAND-0001",
                "family": "shell_distance",
                "parameters": {"order": 2},
                "metrics": {"train": 0.12, "holdout": 0.19},
                "control_outcomes": [{"name": "shuffled_shell", "outcome": "beaten"}],
                "complexity": 2,
                "leakage_status": "CHECKED_CLEAN",
                "candidate_state": "REJECTED_BY_CONTROL",
                "route_verdict": "REJECTED_BY_CONTROL",
            },
            {
                "candidate_id": "CAND-0002",
                "family": "odd_even_pairing",
                "complexity": 1,
                "leakage_status": "CHECKED_CLEAN",
                "candidate_state": "SHORTLISTED",
                "route_verdict": "SHORTLIST_CANDIDATE",
            },
        ],
        "route_verdict_summary": {
            "REJECTED_BY_CONTROL": 60,
            "NEGATIVE_RESULT": 28,
            "SHORTLIST_CANDIDATE": 2,
        },
        "limitations": ["Sandbox factory run; no claim, prediction, or result promotion."],
        "reproducibility": {
            "code_reference": "physics_lab/factories/nuclear_residual.py",
            "command": "python3 scripts/run_research_factory.py --spec nuclear-residual",
            "run_date": "2026-06-01",
        },
    }


def test_factory_summary_accepts_valid_payload() -> None:
    payload = _valid_summary()
    assert validate_document(payload, "factory_summary", SOURCE) is payload


def test_factory_summary_requires_candidate_state_distinction() -> None:
    payload = _valid_summary()
    del payload["candidate_counts"]["rejected_by_control"]  # type: ignore[index]
    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "factory_summary", SOURCE)


def test_factory_summary_rejects_unknown_route_verdict() -> None:
    payload = copy.deepcopy(_valid_summary())
    payload["candidates"][0]["route_verdict"] = "DISCOVERY"  # type: ignore[index]
    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "factory_summary", SOURCE)


def test_factory_summary_rejects_unknown_candidate_state() -> None:
    payload = copy.deepcopy(_valid_summary())
    payload["candidates"][1]["candidate_state"] = "PROMOTED"  # type: ignore[index]
    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "factory_summary", SOURCE)


def test_factory_summary_requires_limitations() -> None:
    payload = _valid_summary()
    payload["limitations"] = []
    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "factory_summary", SOURCE)


def test_factory_summary_rejects_extra_top_level_property() -> None:
    payload = _valid_summary()
    payload["promoted_claim"] = True
    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "factory_summary", SOURCE)


def test_factory_summary_allows_campaign_specific_block() -> None:
    payload = _valid_summary()
    payload["campaign_specific"] = {"shell_region": "Z=50", "no_leakage_contract": "applied"}
    assert validate_document(payload, "factory_summary", SOURCE) is payload
