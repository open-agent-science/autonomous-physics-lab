"""Validate the synthetic MD-0002 loader/schema fixture."""

import pathlib
from copy import deepcopy

from physics_lab.datasets.materials_md0002 import (
    AXIS_UNITS,
    PLACEHOLDER_CHECKSUM,
    PLACEHOLDER_SOURCE_VERSION,
    load_md0002_dataset,
    summarize_md0002_dataset,
    validate_md0002_payload,
)

REPO = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = REPO / "data" / "materials" / "fixtures" / "md0002_schema_fixture.yaml"

FORBIDDEN_RESULT_KEYS = {
    "benchmark_metric",
    "benchmark_result",
    "claim",
    "mae",
    "metrics",
    "prediction",
    "residual",
    "rmse",
}


def _load_fixture():
    return load_md0002_dataset(FIXTURE)


def test_md0002_fixture_is_synthetic_and_pre_acquisition_only():
    dataset = _load_fixture()
    fixture = dataset.payload
    assert fixture["fixture_id"] == "MD-0002-SCHEMA-FIXTURE-0001"
    assert fixture["dataset_family"] == "MD-0002"
    assert fixture["fixture_only"] is True
    assert fixture["live_external_fetch_allowed"] is False
    assert fixture["source_version"] == PLACEHOLDER_SOURCE_VERSION
    assert fixture["snapshot_checksum_sha256"] == PLACEHOLDER_CHECKSUM
    assert fixture["row_count"] == len(dataset.rows)
    assert not (FORBIDDEN_RESULT_KEYS & set(fixture))
    assert "not source rows" in fixture["no_claim_boundary"]


def test_md0002_axis_policies_keep_properties_separate():
    fixture = _load_fixture().payload
    policies = {axis["property_kind"]: axis for axis in fixture["axis_policies"]}
    assert set(policies) == set(AXIS_UNITS)
    for property_kind, units in AXIS_UNITS.items():
        assert policies[property_kind]["units"] == units
        assert policies[property_kind]["provenance_class"] == "computed_dft"


def test_md0002_fixture_rows_represent_two_cation_oxides():
    dataset = _load_fixture()
    for row in dataset.rows:
        composition = row["composition"]
        non_oxygen = {element for element in composition if element != "O"}
        assert set(composition) == non_oxygen | {"O"}
        assert len(non_oxygen) == 2
        assert sorted(row["cations"]) == sorted(non_oxygen)
        assert row["composition_family"] == "ternary_oxide"
        assert row["source_id"] == "materials-project"
        assert str(row["material_id"]).startswith("mp-fixture-")
        assert row["record_locator"] == row["material_id"]
        assert row["fixture_value"] is True
        assert row["database_version"] == PLACEHOLDER_SOURCE_VERSION
        assert row["snapshot_checksum_sha256"] == PLACEHOLDER_CHECKSUM
        assert row["dft_functional"] == "GGA_or_GGA+U"
        assert row["property_kind"] in AXIS_UNITS
        assert row["units"] == AXIS_UNITS[row["property_kind"]]


def test_md0002_included_rows_are_computed_dft_stable_fixture_values():
    dataset = _load_fixture()
    included = [row for row in dataset.rows if row["inclusion_status"] == "included"]
    assert {row["property_kind"] for row in included} == set(AXIS_UNITS)
    for row in included:
        assert row["provenance_class"] == "computed_dft"
        assert row["value"] is not None
        assert row["energy_above_hull"] == 0.0
        assert row["is_stable"] is True
        assert row["exclusion_reason"] is None


def test_md0002_axis_specific_exclusions_stay_visible():
    dataset = _load_fixture()
    excluded = [row for row in dataset.rows if row["inclusion_status"] == "excluded"]
    assert excluded
    for row in excluded:
        assert row["provenance_class"] == "excluded"
        assert row["value"] is None
        assert row["exclusion_reason"]
        assert "axis-only exclusion" in row["exclusion_reason"]
        assert row["property_kind"] == "band_gap"
        assert row["units"] == "eV"


def test_md0002_loader_summary_keeps_axes_separate():
    dataset = _load_fixture()
    summary = summarize_md0002_dataset(dataset)
    assert set(summary["axes"]) == set(AXIS_UNITS)
    assert summary["axes"]["formation_energy_per_atom"] == {
        "units": "eV_per_atom",
        "rows": 1,
        "included": 1,
        "excluded": 0,
    }
    assert summary["axes"]["band_gap"] == {
        "units": "eV",
        "rows": 2,
        "included": 1,
        "excluded": 1,
    }
    assert "metrics" not in summary
    assert "residual" not in summary


def test_md0002_loader_rejects_duplicate_material_id_within_axis():
    payload = deepcopy(_load_fixture().payload)
    band_gap_rows = [row for row in payload["rows"] if row["property_kind"] == "band_gap"]
    band_gap_rows[1]["material_id"] = band_gap_rows[0]["material_id"]
    errors = validate_md0002_payload(payload)
    assert any("duplicate material_id mp-fixture-ternary-001 on axis band_gap" in error for error in errors)


def test_md0002_loader_rejects_unpinned_non_fixture_payload():
    payload = deepcopy(_load_fixture().payload)
    payload["fixture_only"] = False
    errors = validate_md0002_payload(payload)
    assert "non-fixture source_version must be pinned" in errors
    assert "non-fixture snapshot_checksum_sha256 must be pinned" in errors
