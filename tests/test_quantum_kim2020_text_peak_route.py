from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / (
    "data/quantum_dots/source_artifacts/kim-2020-nanomaterials-cdse-optical/"
    "text_reported_peak_route_contract.yaml"
)
LEDGER = ROOT / (
    "data/quantum_dots/digitization/kim-2020-nanomaterials-cdse-optical/"
    "extraction_ledger.yaml"
)
ABSORPTION = ROOT / "data/quantum_dots/qd-0005-kim-2020-cdse-absorption.yaml"
EMISSION = ROOT / "data/quantum_dots/qd-0006-kim-2020-cdse-emission.yaml"

PDF_SHA256 = "2dab8a6b4db18af88f7175ac0773747fe1aeb15d88f951a4a8536cdc2dd73edb"
JATS_SHA256 = "6642fed609ad6540b61ca856d293d2b469c5ed7be9323479c9b76b023f668244"


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_text_route_has_all_eight_source_statements_and_zero_rows() -> None:
    contract = _load(CONTRACT)
    mappings = contract["sample_axis_mapping"]

    assert contract["verdict"] == "GO_TEXT_REPORTED_PEAK_ROUTE"
    assert contract["planning_only"] is True
    assert contract["measurement_rows_created"] == 0
    assert [row["sample_id"] for row in mappings] == [
        "CdSe-1",
        "CdSe-2",
        "CdSe-3",
        "CdSe-4",
    ]
    assert len(mappings) * 2 == contract["future_row_contract"]["required_rows"] == 8
    assert all(
        set(row) >= {
            "sample_id",
            "paragraph_particle_size_nm",
            "absorption_peak_eV",
            "fluorescence_peak_eV",
        }
        for row in mappings
    )


def test_future_schema_freezes_semantics_uncertainty_and_morphology() -> None:
    contract = _load(CONTRACT)
    future = contract["future_row_contract"]
    cross_check = contract["cross_check_policy"]

    assert future["required_property_kinds"] == [
        "absorption_peak_eV",
        "fluorescence_peak_eV",
    ]
    assert future["rounding_uncertainty_floor_eV"] == 0.005
    assert future["instrument_uncertainty"] == "not_reported"
    assert future["morphology"] == "unknown_non_spherical"
    assert future["equivalent_sphere_conversion_allowed"] is False
    assert future["bandgap_relabeling_allowed"] is False
    assert future["absorption_fluorescence_pooling_allowed"] is False
    assert cross_check["agreement_with_excluded_digitization_is_admission_criterion"] is False


def test_digitization_blocker_history_remains_excluded() -> None:
    contract = _load(CONTRACT)
    ledger = _load(LEDGER)

    assert ledger["verdict"] == "UNCERTAINTY_BLOCKED"
    assert ledger["completeness"]["admitted_optical_row_count"] == 0
    assert ledger["completeness"]["excluded_optical_observation_count"] == 8
    assert all(
        row["inclusion_status"] == "excluded"
        for row in ledger["optical_observations"]
    )
    assert contract["cross_check_policy"]["task_1052_ledger_mutable"] is False
    assert contract["future_task_shape"]["fresh_canonical_task_required"] is True
    assert contract["future_task_shape"]["scoring_allowed_in_extraction_task"] is False


def test_curated_rows_exactly_reproduce_frozen_text_mapping() -> None:
    contract = _load(CONTRACT)
    absorption = _load(ABSORPTION)
    emission = _load(EMISSION)
    expected = contract["sample_axis_mapping"]

    assert contract["source"]["doi"] == "10.3390/nano10081589"
    assert contract["source"]["version_of_record_sha256"] == PDF_SHA256
    assert contract["source"]["europe_pmc_jats_sha256"] == JATS_SHA256
    assert len(absorption["entries"]) == len(emission["entries"]) == 4

    for source_row, absorption_row, emission_row in zip(
        expected, absorption["entries"], emission["entries"], strict=True
    ):
        assert absorption_row["sample_id"] == emission_row["sample_id"] == source_row["sample_id"]
        assert absorption_row["diameter_nm"] == emission_row["diameter_nm"] == source_row["paragraph_particle_size_nm"]
        assert absorption_row["value_eV"] == source_row["absorption_peak_eV"]
        assert emission_row["value_eV"] == source_row["fluorescence_peak_eV"]


def test_curated_rows_preserve_property_and_provenance_boundaries() -> None:
    absorption = _load(ABSORPTION)
    emission = _load(EMISSION)

    assert absorption["property_kind_covered"] == "absorption_peak_eV"
    assert emission["property_kind_covered"] == "emission_peak_eV"
    assert {row["sample_id"] for row in absorption["entries"]} == {
        row["sample_id"] for row in emission["entries"]
    } == {"CdSe-1", "CdSe-2", "CdSe-3", "CdSe-4"}

    for row in absorption["entries"]:
        assert row["property_kind"] == "absorption_peak_eV"
        assert row["source_property_term"] == "absorption peak"
        assert row["measurement_type"] == "optical_absorption"
    for row in emission["entries"]:
        assert row["property_kind"] == "emission_peak_eV"
        assert row["source_property_term"] == "fluorescence peak"
        assert row["measurement_type"] == "photoluminescence"

    for row in absorption["entries"] + emission["entries"]:
        assert row["inclusion_status"] == "included"
        assert row["provenance_class"] == "text_stated_summary"
        assert row["source_artifact_sha256"] == PDF_SHA256
        assert row["printed_precision_eV"] == 0.01
        assert row["rounding_uncertainty_floor_eV"] == 0.005
        assert row["instrument_uncertainty"] == "not_reported"
        assert row["morphology"] == "unknown_non_spherical"
        assert "equivalent_diameter_nm" not in row
        assert "uncertainty_eV" not in row
        assert "Figure 3" in row["source_locator"]
