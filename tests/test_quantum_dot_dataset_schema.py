"""Schema validation tests for quantum-dot size-effect dataset files.

Covers:
- Minimal valid entry accepted by the schema
- Both diameter_nm and radius_nm present on the same entry → rejected
- Invalid property_kind rejected
- excluded entry without exclusion_reason → rejected
- Valid excluded entry with exclusion_reason → accepted
- Missing required top-level fields → rejected
- Missing required entry fields → rejected
- Invalid status value → rejected
- property_kind_covered optional field accepts valid values
- source_manifest.yaml structural sanity (YAML loads, has expected keys)
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from physics_lab.registry.validation import infer_kind_from_path, validate_document


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _minimal_entry() -> dict[str, object]:
    return {
        "entry_id": "cdse-001",
        "material": "CdSe",
        "diameter_nm": 3.5,
        "property_kind": "absorption_peak_eV",
        "value_eV": 2.1,
        "source_id": "yu-2003-jpc",
        "inclusion_status": "included",
    }


def _minimal_payload() -> dict[str, object]:
    return {
        "dataset_id": "qd-0001-cdse-absorption",
        "title": "CdSe absorption peak vs. diameter",
        "status": "draft",
        "description": "Minimal test dataset for schema validation.",
        "source_policy": "Pinned fixture for tests only. No redistribution.",
        "entries": [_minimal_entry()],
    }


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_schema_accepts_minimal_valid_payload() -> None:
    payload = _minimal_payload()
    result = validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")
    assert result is payload


def test_schema_accepts_radius_nm_instead_of_diameter() -> None:
    payload = _minimal_payload()
    entry = payload["entries"][0]  # type: ignore[index]
    del entry["diameter_nm"]
    entry["radius_nm"] = 1.75
    validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")


def test_schema_accepts_all_property_kind_values() -> None:
    for kind in ("absorption_peak_eV", "emission_peak_eV", "bandgap_eV"):
        payload = _minimal_payload()
        payload["entries"][0]["property_kind"] = kind  # type: ignore[index]
        validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")


def test_schema_accepts_all_status_values() -> None:
    for status in ("draft", "curated", "frozen"):
        payload = _minimal_payload()
        payload["status"] = status
        validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")


def test_schema_accepts_excluded_entry_with_exclusion_reason() -> None:
    payload = _minimal_payload()
    entry = payload["entries"][0]  # type: ignore[index]
    entry["inclusion_status"] = "excluded"
    entry["exclusion_reason"] = "Outlier: synthesis batch contaminated."
    validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")


def test_schema_accepts_optional_fields() -> None:
    payload = _minimal_payload()
    entry = payload["entries"][0]  # type: ignore[index]
    entry["uncertainty_eV"] = 0.02
    entry["temperature_K"] = 300.0
    entry["measurement_type"] = "optical_absorption"
    entry["composition_note"] = "ZnS shell 1 monolayer"
    entry["source_table_ref"] = "Table 2, row 4"
    entry["notes"] = "Value read from digitised figure."
    payload["property_kind_covered"] = "absorption_peak_eV"
    validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")


def test_schema_accepts_entry_without_size_field() -> None:
    """Size fields (diameter_nm / radius_nm) are optional at the schema level."""
    payload = _minimal_payload()
    entry = payload["entries"][0]  # type: ignore[index]
    del entry["diameter_nm"]
    validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")


# ---------------------------------------------------------------------------
# Rejection tests
# ---------------------------------------------------------------------------


def test_schema_rejects_both_diameter_and_radius_on_same_entry() -> None:
    payload = _minimal_payload()
    entry = payload["entries"][0]  # type: ignore[index]
    entry["radius_nm"] = 1.75  # diameter_nm already present → violation
    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")


def test_schema_rejects_invalid_property_kind() -> None:
    payload = _minimal_payload()
    payload["entries"][0]["property_kind"] = "energy_eV"  # type: ignore[index]
    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")


def test_schema_rejects_excluded_entry_without_exclusion_reason() -> None:
    payload = _minimal_payload()
    payload["entries"][0]["inclusion_status"] = "excluded"  # type: ignore[index]
    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")


def test_schema_rejects_invalid_status() -> None:
    payload = _minimal_payload()
    payload["status"] = "published"
    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")


def test_schema_rejects_missing_dataset_id() -> None:
    payload = _minimal_payload()
    del payload["dataset_id"]
    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")


def test_schema_rejects_missing_entries() -> None:
    payload = _minimal_payload()
    del payload["entries"]
    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")


def test_schema_rejects_empty_entries_array() -> None:
    payload = _minimal_payload()
    payload["entries"] = []
    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")


def test_schema_rejects_entry_missing_required_field() -> None:
    payload = _minimal_payload()
    entry = copy.deepcopy(_minimal_entry())
    del entry["source_id"]
    payload["entries"] = [entry]
    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")


def test_schema_rejects_invalid_measurement_type() -> None:
    payload = _minimal_payload()
    payload["entries"][0]["measurement_type"] = "xray_diffraction"  # type: ignore[index]
    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")


def test_schema_rejects_invalid_property_kind_covered() -> None:
    payload = _minimal_payload()
    payload["property_kind_covered"] = "energy_eV"
    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")


def test_schema_rejects_zero_diameter() -> None:
    payload = _minimal_payload()
    payload["entries"][0]["diameter_nm"] = 0.0  # type: ignore[index]
    with pytest.raises(ValueError, match="schema validation"):
        validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-test.yaml")


# ---------------------------------------------------------------------------
# Path-inference test
# ---------------------------------------------------------------------------


def test_infer_kind_from_quantum_dots_path() -> None:
    kind = infer_kind_from_path("data/quantum_dots/qd-0001-cdse-absorption.yaml")
    assert kind == "quantum_dot_size_effect"


# ---------------------------------------------------------------------------
# source_manifest.yaml structural sanity
# ---------------------------------------------------------------------------


def test_source_manifest_loads_and_has_expected_keys() -> None:
    manifest_path = (
        Path(__file__).resolve().parent.parent / "data" / "quantum_dots" / "source_manifest.yaml"
    )
    assert manifest_path.exists(), "source_manifest.yaml must exist"
    with manifest_path.open("r", encoding="utf-8") as fh:
        manifest = yaml.safe_load(fh)
    assert "manifest_version" in manifest
    assert "campaign_id" in manifest
    assert "live_external_fetch_allowed" in manifest
    assert manifest["live_external_fetch_allowed"] is False
    assert "sources" in manifest
    assert isinstance(manifest["sources"], list)
