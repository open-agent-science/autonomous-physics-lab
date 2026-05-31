from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data/quantum_dots/digitization_fixture.yaml"


def _load_fixture() -> dict:
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))


def test_digitization_fixture_is_synthetic_only() -> None:
    fixture = _load_fixture()

    assert fixture["task_id"] == "TASK-0490"
    assert fixture["synthetic"] is True
    assert fixture["contains_real_measurement_rows"] is False
    assert fixture["baseline_metrics_allowed"] is False
    assert fixture["claim_promotion_allowed"] is False
    assert fixture["calibration_quality"]["raw_figure_asset_committed"] is False


def test_axis_calibration_has_four_anchors_with_units() -> None:
    fixture = _load_fixture()
    calibration = fixture["axis_calibration"]
    anchors = calibration["x_axis"]["anchors"] + calibration["y_axis"]["anchors"]

    assert calibration["x_axis"]["label"] == "diameter_nm"
    assert calibration["x_axis"]["units"] == "nm"
    assert calibration["y_axis"]["label"] == "absorption_peak_eV"
    assert calibration["y_axis"]["units"] == "eV"
    assert len(anchors) >= fixture["calibration_quality"]["minimum_anchor_count"]
    assert all({"pixel_x", "pixel_y", "axis_value"} <= set(anchor) for anchor in anchors)


def test_extracted_points_have_provenance_uncertainty_and_cross_checks() -> None:
    fixture = _load_fixture()
    points = fixture["extracted_points"]

    assert len(points) >= 3
    for point in points:
        assert point["axis_calibration_ref"] == "QD-DIGITIZATION-FIXTURE-0001.axis_calibration"
        assert point["property_kind"] == fixture["digitization_context"]["property_kind"]
        assert point["material"] == fixture["digitization_context"]["material"]
        assert point["coordinate_uncertainty"]["diameter_nm"] > 0
        assert point["coordinate_uncertainty"]["value_eV"] > 0
        assert "formula_value_eV" in point["formula_cross_check"]
        assert "residual_eV" in point["formula_cross_check"]
        assert isinstance(point["formula_cross_check"]["inside_uncertainty_band"], bool)


def test_excluded_points_have_reasons_and_no_qd_rows_are_authorized() -> None:
    fixture = _load_fixture()

    excluded = [point for point in fixture["extracted_points"] if point["inclusion_status"] == "excluded"]
    assert excluded
    assert all(point.get("exclusion_reason") for point in excluded)
    assert fixture["future_row_mapping"]["qd_yaml_allowed_from_fixture"] is False
