"""Guards the first pinned Materials Project dataset (TASK-0548).

Checks required fields, units, provenance, attribution, and that the committed
snapshot's SHA-256 matches what the dataset files and manifest record.
"""
import hashlib
import pathlib

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parents[1]
MATERIALS = REPO / "data" / "materials"
SNAPSHOT = MATERIALS / "snapshots" / "materials_project_binary_oxides_2025-09-25.json"

DATASETS = {
    "formation_energy_per_atom": (MATERIALS / "md-0001-materials-project-formation-energy.yaml", "eV_per_atom"),
    "band_gap": (MATERIALS / "md-0001-materials-project-band-gap.yaml", "eV"),
}

REQUIRED_ROW_FIELDS = {
    "row_id", "material_id", "formula_pretty", "composition", "property_kind",
    "value", "units", "method", "provenance_class", "inclusion_status",
}


def _load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_snapshot_present_and_checksum_matches():
    assert SNAPSHOT.is_file(), "pinned snapshot file missing"
    actual = hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest()
    for kind, (path, _units) in DATASETS.items():
        doc = _load(path)
        assert doc["snapshot_checksum_sha256"] == actual, f"checksum drift in {path.name}"
    manifest = _load(MATERIALS / "materials_snapshot_manifest.yaml")
    assert manifest["acquisition"]["checksum_sha256"] == actual


@pytest.mark.parametrize("kind", list(DATASETS))
def test_dataset_header_is_pinned_and_attributed(kind):
    path, units = DATASETS[kind]
    doc = _load(path)
    assert doc["property_kind"] == kind
    assert doc["units"] == units
    assert doc["provenance_class"] == "computed_dft"
    assert doc["database_version"]  # pinned, non-empty
    assert "CC BY 4.0" in doc["license"]
    assert "Materials Project" in doc["attribution"]
    assert doc["row_count"] == len(doc["rows"])
    assert doc["row_count"] > 0


@pytest.mark.parametrize("kind", list(DATASETS))
def test_rows_well_formed(kind):
    path, units = DATASETS[kind]
    doc = _load(path)
    seen_ids = set()
    for row in doc["rows"]:
        missing = REQUIRED_ROW_FIELDS - set(row)
        assert not missing, f"{path.name} row {row.get('row_id')} missing {missing}"
        assert row["row_id"] not in seen_ids, f"duplicate row_id {row['row_id']}"
        seen_ids.add(row["row_id"])
        assert row["units"] == units
        assert row["property_kind"] == kind
        assert row["provenance_class"] == "computed_dft"
        assert isinstance(row["value"], (int, float)), f"non-numeric value in {row['row_id']}"
        assert str(row["material_id"]).startswith("mp-")


def test_axes_are_not_pooled():
    fe = _load(DATASETS["formation_energy_per_atom"][0])
    bg = _load(DATASETS["band_gap"][0])
    assert fe["property_kind"] != bg["property_kind"]
    assert fe["units"] != bg["units"]
