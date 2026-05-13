from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
import yaml

from physics_lab.registry.nuclear_mass_predictions import load_nuclear_mass_prediction
from physics_lab.registry.validation import infer_kind_from_path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _template_path() -> Path:
    return _repo_root() / "prediction_registry" / "nuclear_masses" / "PRED-TEMPLATE.yaml"


def _template_payload() -> dict[str, object]:
    raw_text = _template_path().read_text(encoding="utf-8")
    normalized = (
        raw_text.replace("PRED-XXXX", "PRED-0000")
        .replace("TASK-XXXX", "TASK-0000")
        .replace("REPLACE_WITH_COMMIT_SHA", "abcdef0")
    )
    payload = yaml.safe_load(normalized)
    assert isinstance(payload, dict)
    return payload


def test_prediction_template_matches_schema() -> None:
    repo_root = _repo_root()
    schema_path = repo_root / "physics_lab" / "schemas" / "nuclear_mass_prediction.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    payload = _template_payload()

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.absolute_path))

    assert errors == []


def test_prediction_template_preserves_claim_and_reveal_boundary() -> None:
    payload = _template_payload()

    assert payload["campaign_profile_id"] == "nuclear-mass-surface"
    assert payload["evidence_class"] == "prospective_prediction_registry"
    assert payload["source_state"]["live_external_fetch_allowed"] is False
    assert payload["review_boundary"]["retrospective_equivalence_forbidden"] is True
    assert payload["review_boundary"]["pre_reveal_claim_promotion_allowed"] is False
    assert payload["review_boundary"]["canonical_result_allowed_pre_reveal"] is False
    assert "no claim" in payload["claim_ceiling"].lower()
    assert "before later maintainer-reviewed comparison" in payload["claim_ceiling"]


def test_prediction_template_target_rows_are_structurally_consistent() -> None:
    payload = _template_payload()
    targets = payload["target_set"]["target_nuclides"]

    assert len(targets) == 1
    target = targets[0]
    assert target["A"] == target["Z"] + target["N"]
    assert target["uncertainty_mev"] is None
    assert payload["uncertainty_semantics"]["type"] == "point_estimate_only"


def test_prediction_registry_kind_inference_supports_template_and_entries() -> None:
    assert (
        infer_kind_from_path("prediction_registry/nuclear_masses/PRED-TEMPLATE.yaml")
        == "nuclear_mass_prediction"
    )
    assert (
        infer_kind_from_path("prediction_registry/nuclear_masses/PRED-0001.yaml")
        == "nuclear_mass_prediction"
    )


def test_loader_validates_realistic_prediction_payload() -> None:
    repo_root = _repo_root()
    entry_path = repo_root / "prediction_registry" / "nuclear_masses" / "PRED-0001.yaml"
    entry_path.write_text(
        _template_path()
        .read_text(encoding="utf-8")
        .replace("PRED-XXXX", "PRED-0001")
        .replace("TASK-XXXX", "TASK-0189")
        .replace("REPLACE_WITH_COMMIT_SHA", "abcdef0"),
        encoding="utf-8",
    )
    try:
        payload = load_nuclear_mass_prediction(entry_path)
        assert payload["prediction_id"] == "PRED-0001"
    finally:
        entry_path.unlink()
