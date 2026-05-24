from __future__ import annotations

import copy

import pytest

from physics_lab.registry.validation import infer_kind_from_path, validate_document


def _valid_review() -> dict[str, object]:
    return {
        "schema_version": "1",
        "artifact_type": "result_candidate_review",
        "review_id": "RESULT-CANDIDATE-REVIEW-0001",
        "campaign_id": "nuclear_mass_surface",
        "task_id": "TASK-0380",
        "result_refs": ["docs/reviews/example-sandbox-signal.md"],
        "candidate_scope": "sandbox_followup",
        "scores": {
            "baseline_strength": "PARTIAL",
            "source_provenance": "PASS",
            "artifact_checksums": "NOT_APPLICABLE",
            "holdout_or_reveal_quality": "PARTIAL",
            "uncertainty_handling": "PARTIAL",
            "negative_controls": "PASS",
            "leakage_risk": "PARTIAL",
            "reproducibility": "PASS",
            "external_comparability": "PARTIAL",
            "public_wording_risk": "FAIL",
        },
        "eligibility": {
            "sandbox_followup": "ALLOW",
            "public_summary": "BLOCK",
            "claim_candidate": "BLOCK",
        },
        "final_verdict": "SANDBOX_FOLLOWUP_ONLY",
        "human_review_required": True,
        "claim_promotion_allowed": False,
        "limitations": ["Retrospective sandbox evidence only."],
        "reviewer": "maintainer",
    }


def test_result_candidate_review_schema_accepts_valid_scorecard() -> None:
    payload = _valid_review()
    result = validate_document(
        payload,
        "result_candidate_review",
        "docs/reviews/result_candidate_review.yaml",
    )

    assert result is payload


def test_result_candidate_review_schema_rejects_missing_required_score() -> None:
    payload = _valid_review()
    del payload["scores"]["leakage_risk"]  # type: ignore[index]

    with pytest.raises(ValueError, match="schema validation"):
        validate_document(
            payload,
            "result_candidate_review",
            "docs/reviews/result_candidate_review.yaml",
        )


def test_result_candidate_review_schema_requires_human_review() -> None:
    payload = _valid_review()
    payload["human_review_required"] = False

    with pytest.raises(ValueError, match="schema validation"):
        validate_document(
            payload,
            "result_candidate_review",
            "docs/reviews/result_candidate_review.yaml",
        )


def test_result_candidate_review_schema_rejects_claim_promotion_without_claim_verdict() -> None:
    payload = _valid_review()
    payload["claim_promotion_allowed"] = True

    with pytest.raises(ValueError, match="schema validation"):
        validate_document(
            payload,
            "result_candidate_review",
            "docs/reviews/result_candidate_review.yaml",
        )


def test_result_candidate_review_schema_accepts_claim_candidate_gate_shape() -> None:
    payload = copy.deepcopy(_valid_review())
    payload["candidate_scope"] = "claim_candidate"
    payload["eligibility"]["claim_candidate"] = "MAINTAINER_REVIEW_REQUIRED"  # type: ignore[index]
    payload["final_verdict"] = "CLAIM_CANDIDATE_WITH_MAINTAINER_REVIEW"
    payload["claim_promotion_allowed"] = True

    validate_document(
        payload,
        "result_candidate_review",
        "docs/reviews/result_candidate_review.yaml",
    )


def test_result_candidate_review_schema_rejects_extra_properties() -> None:
    payload = _valid_review()
    payload["auto_promote_claim"] = True

    with pytest.raises(ValueError, match="schema validation"):
        validate_document(
            payload,
            "result_candidate_review",
            "docs/reviews/result_candidate_review.yaml",
        )


def test_result_candidate_review_filename_infers_schema_kind() -> None:
    assert (
        infer_kind_from_path("docs/reviews/result_candidate_review.yaml")
        == "result_candidate_review"
    )
