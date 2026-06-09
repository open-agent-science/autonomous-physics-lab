"""Validate the synthetic MD-0002 loader/schema fixture (TASK-0645)."""

import pathlib

import yaml

REPO = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = REPO / "data" / "materials" / "fixtures" / "md0002_schema_fixture.yaml"

AXIS_UNITS = {
    "formation_energy_per_atom": "eV_per_atom",
    "band_gap": "eV",
}

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
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))


def test_md0002_fixture_is_synthetic_and_pre_acquisition_only():
    fixture = _load_fixture()
    assert fixture["fixture_id"] == "MD-0002-SCHEMA-FIXTURE-0001"
    assert fixture["dataset_family"] == "MD-0002"
    assert fixture["fixture_only"] is True
    assert fixture["live_external_fetch_allowed"] is False
    assert fixture["source_version"] == "TO_BE_PINNED_BY_ACQUISITION"
    assert fixture["snapshot_checksum_sha256"] == "TO_BE_COMPUTED_BY_ACQUISITION"
    assert fixture["row_count"] == len(fixture["rows"])
    assert not (FORBIDDEN_RESULT_KEYS & set(fixture))
    assert "not source rows" in fixture["no_claim_boundary"]


def test_md0002_axis_policies_keep_properties_separate():
    fixture = _load_fixture()
    policies = {axis["property_kind"]: axis for axis in fixture["axis_policies"]}
    assert set(policies) == set(AXIS_UNITS)
    for property_kind, units in AXIS_UNITS.items():
        assert policies[property_kind]["units"] == units
        assert policies[property_kind]["provenance_class"] == "computed_dft"


def test_md0002_fixture_rows_represent_two_cation_oxides():
    fixture = _load_fixture()
    for row in fixture["rows"]:
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
        assert row["database_version"] == "TO_BE_PINNED_BY_ACQUISITION"
        assert row["snapshot_checksum_sha256"] == "TO_BE_COMPUTED_BY_ACQUISITION"
        assert row["dft_functional"] == "GGA_or_GGA+U"
        assert row["property_kind"] in AXIS_UNITS
        assert row["units"] == AXIS_UNITS[row["property_kind"]]


def test_md0002_included_rows_are_computed_dft_stable_fixture_values():
    fixture = _load_fixture()
    included = [row for row in fixture["rows"] if row["inclusion_status"] == "included"]
    assert {row["property_kind"] for row in included} == set(AXIS_UNITS)
    for row in included:
        assert row["provenance_class"] == "computed_dft"
        assert row["value"] is not None
        assert row["energy_above_hull"] == 0.0
        assert row["is_stable"] is True
        assert row["exclusion_reason"] is None


def test_md0002_axis_specific_exclusions_stay_visible():
    fixture = _load_fixture()
    excluded = [row for row in fixture["rows"] if row["inclusion_status"] == "excluded"]
    assert excluded
    for row in excluded:
        assert row["provenance_class"] == "excluded"
        assert row["value"] is None
        assert row["exclusion_reason"]
        assert "axis-only exclusion" in row["exclusion_reason"]
        assert row["property_kind"] == "band_gap"
        assert row["units"] == "eV"
