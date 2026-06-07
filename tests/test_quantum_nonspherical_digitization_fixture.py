from __future__ import annotations

from pathlib import Path

import yaml

from physics_lab.registry.validation import validate_document


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data/quantum_dots/fixtures/nonspherical_digitization_fixture.yaml"
SIZE_AXES = ("edge_length_nm", "volume_nm3", "equivalent_diameter_nm")


def _load_fixture() -> dict:
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))


def _fixture_point_to_schema_entry(point: dict, context: dict) -> dict[str, object]:
    entry: dict[str, object] = {
        "entry_id": point["point_id"].replace("-", "_").lower(),
        "material": point["material"],
        "property_kind": point["property_kind"],
        "value_eV": point["value_eV"],
        "source_id": point["primary_source_id"],
        "inclusion_status": point["inclusion_status"],
        "source_table_ref": context["figure_ref"],
        "notes": point["notes"],
    }
    if measurement_type := point.get("measurement_type"):
        entry["measurement_type"] = measurement_type
    if morphology := point.get("morphology", context.get("morphology")):
        entry["morphology"] = morphology

    uncertainty = point.get("coordinate_uncertainty", {})
    if value_uncertainty := uncertainty.get("value_eV"):
        entry["uncertainty_eV"] = value_uncertainty

    if "edge_length_nm" in point:
        entry["edge_length_nm"] = point["edge_length_nm"]
    elif "volume_nm3" in point:
        entry["volume_nm3"] = point["volume_nm3"]
    elif "equivalent_diameter_nm" in point:
        entry["equivalent_diameter_nm"] = point["equivalent_diameter_nm"]
        entry["size_conversion"] = point["size_conversion"]

    if point["inclusion_status"] == "excluded":
        entry["exclusion_reason"] = point["exclusion_reason"]

    return entry


def _schema_entry_to_fixture_fields(entry: dict[str, object]) -> dict[str, object]:
    fields: dict[str, object] = {
        "material": entry["material"],
        "property_kind": entry["property_kind"],
        "value_eV": entry["value_eV"],
        "primary_source_id": entry["source_id"],
        "inclusion_status": entry["inclusion_status"],
    }
    for axis in SIZE_AXES:
        if axis in entry:
            fields[axis] = entry[axis]
    if "size_conversion" in entry:
        fields["size_conversion"] = entry["size_conversion"]
    if "morphology" in entry:
        fields["morphology"] = entry["morphology"]
    if "uncertainty_eV" in entry:
        fields["coordinate_uncertainty"] = {"value_eV": entry["uncertainty_eV"]}
    if entry["inclusion_status"] == "excluded":
        fields["exclusion_reason"] = entry["exclusion_reason"]
    return fields


def _build_dataset_payload(entries: list[dict[str, object]], fixture: dict) -> dict[str, object]:
    context = fixture["digitization_context"]
    return {
        "dataset_id": "qd-fixture-nonspherical-roundtrip",
        "title": "Synthetic non-spherical digitization round-trip payload",
        "status": "draft",
        "description": "Ephemeral test payload; not a committed measurement dataset.",
        "source_policy": fixture["source_policy"],
        "property_kind_covered": context["property_kind"],
        "entries": entries,
    }


def test_nonspherical_fixture_is_synthetic_only() -> None:
    fixture = _load_fixture()

    assert fixture["task_id"] == "TASK-0655"
    assert fixture["synthetic"] is True
    assert fixture["non_spherical"] is True
    assert fixture["contains_real_measurement_rows"] is False
    assert fixture["baseline_metrics_allowed"] is False
    assert fixture["claim_promotion_allowed"] is False
    assert fixture["calibration_quality"]["raw_figure_asset_committed"] is False
    assert "Almeida" in fixture["source_policy"]


def test_axis_calibration_declares_source_axis_conversion_metadata() -> None:
    fixture = _load_fixture()
    x_axis = fixture["axis_calibration"]["x_axis"]
    alternate = fixture["axis_calibration"]["alternate_size_axis"]

    assert x_axis["label"] == "edge_length_nm"
    assert x_axis["source_axis_conversion"]["schema_size_axis"] == "edge_length_nm"
    assert x_axis["source_axis_conversion"]["morphology"] == "tetrahedral"
    assert alternate["label"] == "volume_nm3"
    assert alternate["source_axis_conversion"]["schema_size_axis"] == "volume_nm3"

    anchors = x_axis["anchors"] + fixture["axis_calibration"]["y_axis"]["anchors"]
    assert len(anchors) >= fixture["calibration_quality"]["minimum_anchor_count"]


def test_extracted_points_cover_non_spherical_size_routes() -> None:
    fixture = _load_fixture()
    included = [
        point for point in fixture["extracted_points"] if point["inclusion_status"] == "included"
    ]

    assert len(included) == 3
    assert any("edge_length_nm" in point for point in included)
    assert any("volume_nm3" in point for point in included)
    assert any("equivalent_diameter_nm" in point and "size_conversion" in point for point in included)

    for point in fixture["extracted_points"]:
        uncertainty = point["coordinate_uncertainty"]
        assert uncertainty["value_eV"] > 0
        assert point["property_kind"] == fixture["digitization_context"]["property_kind"]
        assert point["material"] == fixture["digitization_context"]["material"]


def test_included_points_round_trip_through_quantum_schema() -> None:
    fixture = _load_fixture()
    context = fixture["digitization_context"]
    included_points = [
        point for point in fixture["extracted_points"] if point["inclusion_status"] == "included"
    ]

    entries = [_fixture_point_to_schema_entry(point, context) for point in included_points]
    payload = _build_dataset_payload(entries, fixture)
    validate_document(payload, "quantum_dot_size_effect", "data/quantum_dots/qd-fixture-test.yaml")

    assert len(included_points) == len(entries)
    for point, entry in zip(included_points, entries):
        round_tripped = _schema_entry_to_fixture_fields(entry)
        for key in ("material", "property_kind", "value_eV", "primary_source_id", "inclusion_status"):
            assert round_tripped[key] == point[key]
        for axis in SIZE_AXES:
            if axis in point:
                assert round_tripped[axis] == point[axis]
        if "size_conversion" in point:
            assert round_tripped["size_conversion"] == point["size_conversion"]
        assert round_tripped["coordinate_uncertainty"]["value_eV"] == point["coordinate_uncertainty"]["value_eV"]


def test_excluded_points_have_reasons_and_fixture_does_not_authorize_qd_rows() -> None:
    fixture = _load_fixture()

    excluded = [
        point for point in fixture["extracted_points"] if point["inclusion_status"] == "excluded"
    ]
    assert excluded
    assert all(point.get("exclusion_reason") for point in excluded)
    assert fixture["future_row_mapping"]["qd_yaml_allowed_from_fixture"] is False
