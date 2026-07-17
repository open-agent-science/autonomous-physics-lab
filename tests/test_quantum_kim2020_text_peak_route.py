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
