"""Tests for ``physics_lab.engines.dimensions``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from physics_lab.engines.dimensions import (
    DIMENSIONLESS,
    SCORING_CONTRACT_LABEL_BLIND_V2,
    SCORING_CONTRACT_LEGACY_V1,
    Dimension,
    DimensionError,
    evaluate_expression_dimension,
    infer_item,
    parse_dimension_string,
    validate_challenge_set,
    validate_item,
)
from physics_lab.workflows.dimensional_validator import (
    run_dimensional_validator_with_output,
)

# ── Unit parsing ─────────────────────────────────────────────────────────── #


def test_parse_dimensionless_empty() -> None:
    assert parse_dimension_string("") == DIMENSIONLESS


def test_parse_dimensionless_one() -> None:
    assert parse_dimension_string("1") == DIMENSIONLESS


def test_parse_single_base_unit() -> None:
    d = parse_dimension_string("kg")
    assert d == Dimension(M=1)


def test_parse_compound_unit() -> None:
    d = parse_dimension_string("kg m s^-2")
    assert d == Dimension(M=1, L=1, T=-2)


def test_parse_derived_unit_newton() -> None:
    assert parse_dimension_string("N") == Dimension(M=1, L=1, T=-2)


def test_parse_unknown_unit_raises() -> None:
    with pytest.raises(DimensionError, match="Unknown unit symbol"):
        parse_dimension_string("Qb")


# ── Dimension arithmetic ──────────────────────────────────────────────────── #


def test_dimension_multiply() -> None:
    kg = Dimension(M=1)
    m_s2 = Dimension(L=1, T=-2)
    assert kg * m_s2 == Dimension(M=1, L=1, T=-2)


def test_dimension_divide() -> None:
    m = Dimension(L=1)
    s = Dimension(T=1)
    assert m / s == Dimension(L=1, T=-1)


def test_dimension_power_integer() -> None:
    m = Dimension(L=1)
    assert m**2 == Dimension(L=2)


def test_dimension_power_half() -> None:
    m2 = Dimension(L=2)
    assert m2**0.5 == Dimension(L=1)


def test_dimensionless_is_dimensionless() -> None:
    assert DIMENSIONLESS.is_dimensionless()
    assert not Dimension(M=1).is_dimensionless()


# ── Expression evaluation ─────────────────────────────────────────────────── #


def test_eval_simple_multiply() -> None:
    dims = {"m": parse_dimension_string("kg"), "a": parse_dimension_string("m s^-2")}
    result = evaluate_expression_dimension("m * a", dims)
    assert result == Dimension(M=1, L=1, T=-2)


def test_eval_power() -> None:
    dims = {"v": parse_dimension_string("m s^-1")}
    result = evaluate_expression_dimension("v**2", dims)
    assert result == Dimension(L=2, T=-2)


def test_eval_division() -> None:
    dims = {"d": parse_dimension_string("m"), "t": parse_dimension_string("s")}
    result = evaluate_expression_dimension("d / t", dims)
    assert result == Dimension(L=1, T=-1)


def test_eval_compatible_addition() -> None:
    dims = {"a": parse_dimension_string("m s^-2"), "b": parse_dimension_string("m s^-2")}
    result = evaluate_expression_dimension("a + b", dims)
    assert result == Dimension(L=1, T=-2)


def test_eval_incompatible_addition_raises() -> None:
    dims = {"a": parse_dimension_string("kg"), "b": parse_dimension_string("m")}
    with pytest.raises(DimensionError, match="incompatible dimensions"):
        evaluate_expression_dimension("a + b", dims)


def test_eval_sqrt_dimensionless() -> None:
    dims = {"x": DIMENSIONLESS}
    result = evaluate_expression_dimension("sqrt(x)", dims)
    assert result == DIMENSIONLESS


def test_eval_dimensionless_pi_constant() -> None:
    dims = {"r": parse_dimension_string("m")}
    result = evaluate_expression_dimension("2 * pi * r", dims)
    assert result == parse_dimension_string("m")


def test_eval_sqrt_dimensional() -> None:
    dims = {"v": parse_dimension_string("m^2 s^-2")}
    result = evaluate_expression_dimension("sqrt(v)", dims)
    assert result == Dimension(L=1, T=-1)


def test_eval_lambda_reserved_word() -> None:
    dims = {
        "v_wave": parse_dimension_string("m s^-1"),
        "f": parse_dimension_string("s^-1"),
        "lambda": parse_dimension_string("m"),
    }
    result = evaluate_expression_dimension("f * lambda", dims)
    assert result == Dimension(L=1, T=-1)


# ── validate_item ─────────────────────────────────────────────────────────── #


def test_validate_valid_formula() -> None:
    item = {
        "id": "TEST-001",
        "formula": "F = m * a",
        "variables": {"F": "kg m s^-2", "m": "kg", "a": "m s^-2"},
        "expected_verdict": "VALID",
    }
    result = validate_item(item)
    assert result.computed_verdict == "VALID"
    assert result.agrees


def test_validate_invalid_formula() -> None:
    item = {
        "id": "TEST-002",
        "formula": "E = m * v",
        "variables": {"E": "kg m^2 s^-2", "m": "kg", "v": "m s^-1"},
        "expected_verdict": "INVALID",
    }
    result = validate_item(item)
    assert result.computed_verdict == "INVALID"
    assert result.agrees


def test_validate_multiterm_lhs() -> None:
    item = {
        "id": "TEST-003",
        "formula": "p * V = n * R_gas * T",
        "variables": {
            "p": "kg m^-1 s^-2",
            "V": "m^3",
            "n": "mol",
            "R_gas": "kg m^2 s^-2 mol^-1 K^-1",
            "T": "K",
        },
        "expected_verdict": "VALID",
    }
    result = validate_item(item)
    assert result.computed_verdict == "VALID"
    assert result.agrees


def test_inference_is_independent_of_labels_and_curated_policy_metadata() -> None:
    base = {
        "id": "TEST-LABEL-BLIND",
        "formula": "F = m * a",
        "variables": {"F": "kg m s^-2", "m": "kg", "a": "m s^-2"},
    }
    labelled_valid = {
        **base,
        "expected_verdict": "VALID",
        "curated_dimensionally_balanced_verdict": "SUSPICIOUS",
    }
    labelled_invalid = {
        **base,
        "expected_verdict": "INVALID",
        "dimensionless_relation_policy": "accepted_textbook_identity",
    }

    assert infer_item(labelled_valid) == infer_item(labelled_invalid)
    assert infer_item(labelled_valid).computed_verdict == "VALID"


def test_dimensionless_structure_is_warning_not_v2_verdict() -> None:
    item = {
        "id": "TEST-DIMENSIONLESS",
        "formula": "ratio = x / y",
        "variables": {
            "ratio": "dimensionless",
            "x": "dimensionless",
            "y": "dimensionless",
        },
        "expected_verdict": "VALID",
    }

    inference = infer_item(item)

    assert inference.computed_verdict == "VALID"
    assert inference.warnings == ("all_variables_dimensionless",)


def test_legacy_contract_is_explicit_and_separate_from_v2() -> None:
    item = {
        "id": "TEST-CURATED-SUSPICIOUS",
        "formula": "ratio = x / y",
        "variables": {"ratio": "1", "x": "1", "y": "1"},
        "expected_verdict": "SUSPICIOUS",
        "curated_dimensionally_balanced_verdict": "SUSPICIOUS",
    }

    v2 = validate_item(item, scoring_contract=SCORING_CONTRACT_LABEL_BLIND_V2)
    legacy = validate_item(item, scoring_contract=SCORING_CONTRACT_LEGACY_V1)

    assert v2.computed_verdict == "VALID"
    assert not v2.exact_match
    assert legacy.computed_verdict == "SUSPICIOUS"
    assert legacy.exact_match


# ── Full challenge-set integration ────────────────────────────────────────── #


CHALLENGE_SET_PATH = (
    Path(__file__).resolve().parent.parent
    / "knowledge"
    / "challenge_sets"
    / "dimensional_analysis_challenge_set.yaml"
)
FROZEN_MVP_CHALLENGE_SET_PATH = (
    Path(__file__).resolve().parent.parent
    / "knowledge"
    / "challenge_sets"
    / "dimensional_analysis_challenge_set_mvp_50.yaml"
)


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.mark.skipif(
    not CHALLENGE_SET_PATH.exists(),
    reason="Challenge set not available",
)
def test_challenge_set_agreement_above_threshold() -> None:
    _, summary = validate_challenge_set(CHALLENGE_SET_PATH)
    assert summary.total >= 50, (
        f"Expected the curated challenge set to retain at least 50 items, got {summary.total}"
    )
    assert summary.agreement_fraction >= 0.90, (
        f"Expected ≥90% agreement, got {summary.agreement_fraction:.1%}"
    )


@pytest.mark.skipif(
    not CHALLENGE_SET_PATH.exists(),
    reason="Challenge set not available",
)
def test_challenge_set_no_inconclusive() -> None:
    _, summary = validate_challenge_set(CHALLENGE_SET_PATH)
    assert summary.inconclusive_count <= 1, (
        f"Expected at most 1 INCONCLUSIVE, got {summary.inconclusive_count}"
    )


def test_boundary_expansion_handles_dimensionless_constants_and_textbook_identity() -> None:
    challenge_set = _load_yaml(CHALLENGE_SET_PATH)
    items = {item["id"]: item for item in challenge_set["items"]}

    assert validate_item(items["DA-022"]).computed_verdict == "VALID"
    da312 = validate_item(items["DA-312"])
    assert da312.computed_verdict == "VALID"
    assert da312.warnings == ("all_variables_dimensionless",)
    assert validate_item(items["DA-408"]).agrees is True


def test_live_boundary_disagreements_are_explicitly_handled() -> None:
    challenge_set = _load_yaml(CHALLENGE_SET_PATH)
    items = {item["id"]: item for item in challenge_set["items"]}

    da310 = validate_item(items["DA-310"])
    da311 = validate_item(items["DA-311"])
    da406 = validate_item(items["DA-406"])

    assert da310.computed_verdict == "VALID"
    assert da310.agrees is False
    assert da311.computed_verdict == "VALID"
    assert da311.agrees is False
    assert da406.computed_verdict == "VALID"
    assert da406.agrees is True


def test_live_challenge_set_reports_v2_exact_and_policy_metrics_separately() -> None:
    results, summary = validate_challenge_set(CHALLENGE_SET_PATH)

    assert summary.total == 74
    assert summary.exact_agree == 62
    assert summary.policy_agree == 72
    assert [result.item_id for result in results if not result.policy_match] == [
        "DA-310",
        "DA-311",
    ]
    assert sum(
        result.policy_match and not result.exact_match for result in results
    ) == 10


def test_dimensional_validator_mvp_scope_is_frozen_apart_from_live_curation() -> None:
    live_challenge_set = _load_yaml(CHALLENGE_SET_PATH)
    frozen_challenge_set = _load_yaml(FROZEN_MVP_CHALLENGE_SET_PATH)

    assert frozen_challenge_set["status"] == "frozen"
    assert frozen_challenge_set["total_items"] == 50
    assert len(frozen_challenge_set["items"]) == 50
    assert live_challenge_set["total_items"] > frozen_challenge_set["total_items"]
    assert len(live_challenge_set["items"]) > len(frozen_challenge_set["items"])


def test_dimensional_validator_replay_uses_frozen_mvp_scope(tmp_path: Path) -> None:
    outcome = run_dimensional_validator_with_output(
        "examples/dimensional_analysis.yaml",
        output_dir=tmp_path,
    )

    metrics = json.loads(outcome.artifacts.metrics_path.read_text(encoding="utf-8"))
    challenge_snapshot = _load_yaml(tmp_path / "inputs" / "challenge_set.yaml")
    result_payload = yaml.safe_load(outcome.artifacts.result_path.read_text(encoding="utf-8"))
    check_names = {check["name"] for check in result_payload["verification"]["checks"]}

    assert metrics["benchmark_scope"] == "frozen_mvp_50"
    assert metrics["expected_item_count"] == 50
    assert metrics["total_items"] == 50
    assert metrics["scoring_contract"] == SCORING_CONTRACT_LEGACY_V1
    assert metrics["primary_metric"] == "policy_adjusted_agreement_fraction"
    assert metrics["agree"] == 49
    assert metrics["agreement_fraction"] == 0.98
    assert metrics["exact_agree"] == 42
    assert metrics["exact_agreement_fraction"] == 0.84
    assert metrics["policy_adjusted_agree"] == 49
    assert metrics["policy_adjusted_agreement_fraction"] == 0.98
    assert challenge_snapshot["total_items"] == 50
    assert len(challenge_snapshot["items"]) == 50
    assert "zero_disagreement_ledger" not in check_names
    assert "frozen_input_checksum" not in check_names
    assert "protected_result_not_rewritten" not in check_names


def test_dimensional_validator_replay_accepts_frozen_scope_override(
    tmp_path: Path,
) -> None:
    outcome = run_dimensional_validator_with_output(
        "examples/dimensional_analysis_live_74.yaml",
        output_dir=tmp_path / "run",
    )

    metrics = json.loads(outcome.artifacts.metrics_path.read_text(encoding="utf-8"))
    result_payload = yaml.safe_load(outcome.artifacts.result_path.read_text(encoding="utf-8"))
    checks = {check["name"]: check for check in result_payload["verification"]["checks"]}

    assert metrics["benchmark_scope"] == "frozen_live_74"
    assert metrics["total_items"] == 74
    assert metrics["scoring_contract"] == SCORING_CONTRACT_LEGACY_V1
    assert metrics["primary_metric"] == "policy_adjusted_agreement_fraction"
    assert metrics["agree"] == 74
    assert metrics["agreement_fraction"] == 1.0
    assert metrics["exact_agree"] == 64
    assert metrics["exact_agreement_fraction"] == pytest.approx(64 / 74, abs=1e-6)
    assert metrics["policy_adjusted_agree"] == 74
    assert metrics["policy_adjusted_agreement_fraction"] == 1.0
    assert metrics["non_exact_policy_acceptance_count"] == 10
    assert metrics["disagreement_count"] == 0
    assert metrics["disagreement_ids"] == []
    assert result_payload["title"] == "Dimensional Analysis Validator Live 74-Item Replay"
    fixture_hash_path = Path(result_payload["input_file_hashes"]["fixture"]["path"])
    assert fixture_hash_path.name == "fixture.yaml"
    assert fixture_hash_path.parent.name == "inputs"
    assert checks["zero_disagreement_ledger"]["metrics"]["disagreement_count"] == 0
    assert checks["zero_disagreement_ledger"]["metrics"]["disagreement_ids"] == "none"
    assert checks["frozen_input_checksum"]["metrics"]["fixture_sha256"] == (
        checks["frozen_input_checksum"]["metrics"]["source_sha256_at_freeze"]
    )
    assert checks["protected_result_not_rewritten"]["metrics"] == {
        "protected_result_rewrite": False
    }


def test_dimensional_validator_v2_calibration_uses_exact_primary_metric(
    tmp_path: Path,
) -> None:
    outcome = run_dimensional_validator_with_output(
        "examples/dimensional_analysis_live_74.yaml",
        output_dir=tmp_path / "run-v2",
        scoring_contract_override=SCORING_CONTRACT_LABEL_BLIND_V2,
    )

    metrics = json.loads(outcome.artifacts.metrics_path.read_text(encoding="utf-8"))
    result_payload = yaml.safe_load(outcome.artifacts.result_path.read_text(encoding="utf-8"))
    check_names = {check["name"] for check in result_payload["verification"]["checks"]}

    assert metrics["scoring_contract"] == SCORING_CONTRACT_LABEL_BLIND_V2
    assert metrics["primary_metric"] == "exact_agreement_fraction"
    assert metrics["exact_agree"] == 62
    assert metrics["agreement_fraction"] == pytest.approx(62 / 74, abs=1e-6)
    assert metrics["policy_adjusted_agree"] == 72
    assert metrics["non_exact_policy_acceptance_count"] == 10
    assert metrics["disagreement_ids"] == [
        "DA-306",
        "DA-307",
        "DA-310",
        "DA-311",
        "DA-401",
        "DA-402",
        "DA-403",
        "DA-404",
        "DA-405",
        "DA-406",
        "DA-407",
        "DA-408",
    ]
    assert result_payload["best_verdict"] == "INCONCLUSIVE"
    assert "zero_disagreement_ledger" not in check_names
    assert "frozen_input_checksum" not in check_names


@pytest.mark.skipif(
    not CHALLENGE_SET_PATH.exists(),
    reason="Challenge set not available",
)
def test_dimensional_validator_result_schema_accepts_inconclusive_tolerance(
    tmp_path: Path,
) -> None:
    outcome = run_dimensional_validator_with_output(
        "examples/dimensional_analysis.yaml",
        output_dir=tmp_path,
    )

    result_payload = yaml.safe_load(outcome.artifacts.result_path.read_text())
    inconclusive_check = next(
        check
        for check in result_payload["verification"]["checks"]
        if check["name"] == "inconclusive_items_within_mvp_tolerance"
    )

    assert inconclusive_check["status"] == "PASS"
    assert (
        inconclusive_check["metrics"]["inconclusive_count"]
        <= inconclusive_check["metrics"]["inconclusive_limit"]
    )
