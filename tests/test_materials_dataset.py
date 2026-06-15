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
CITATION = MATERIALS / "md-0001-citation.yaml"
HOLDOUT_MANIFEST = MATERIALS / "holdout_manifest.yaml"
MD0002_HOLDOUT_MANIFEST = MATERIALS / "md0002_holdout_manifest.yaml"
MD0002_DATASET = MATERIALS / "md-0002-materials-project-stable-ternary-oxides.yaml"
MD0002_SNAPSHOT = MATERIALS / "snapshots" / "materials_project_md0002_2026.04.13.json"

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
    assert doc["dataset_version"] == "0.1.0"
    assert doc["changelog"], "dataset changelog is required for reusable datasets"
    assert doc["property_kind"] == kind
    assert doc["units"] == units
    assert doc["provenance_class"] == "computed_dft"
    assert doc["database_version"]  # pinned, non-empty
    assert doc["uncertainty"]["basis"] == "absent_in_source_snapshot"
    assert "no benchmark metric" in doc["no_claim_boundary"]
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


def test_md0001_citation_metadata_preserves_reuse_boundary():
    citation = _load(CITATION)
    assert citation["metadata_id"] == "MD-0001-CITATION-0001"
    assert citation["dataset"]["dataset_family_id"] == "MD-0001"
    assert citation["dataset"]["dataset_version"] == "0.1.0"
    assert citation["source_attribution"]["source_license"] == "CC BY 4.0"
    assert "Materials Project" in citation["source_attribution"]["required_attribution"]
    maintainer = citation["apl_citation_planning"]["maintainer"]
    assert maintainer["name"] == "Roman Hladun"
    assert maintainer["orcid"] == "https://orcid.org/0009-0004-4853-5212"
    external_org = citation["apl_citation_planning"]["current_external_organization"]
    assert external_org["url"] == "https://github.com/open-agent-science"
    assert citation["reuse_boundary"]["internal_reuse_allowed"] is True
    assert citation["reuse_boundary"]["external_publication_allowed_by_this_file"] is False
    assert citation["reuse_boundary"]["zenodo_release_allowed_by_this_file"] is False
    assert citation["reuse_boundary"]["benchmark_result"] is False
    assert citation["reuse_boundary"]["scientific_claim"] is False


def test_holdout_manifest_preserves_no_peek_boundaries():
    manifest = _load(HOLDOUT_MANIFEST)
    assert manifest["manifest_id"] == "MD-0001-HOLDOUT-NOPEEK-0001"
    assert manifest["promotion_boundary"]["benchmark_allowed_by_this_manifest"] is False
    assert manifest["promotion_boundary"]["claims_allowed"] is False
    assert set(manifest["holdout_schema"]["allowed_split_values"]) == {
        "train",
        "validation",
        "holdout",
        "stress",
        "excluded",
    }
    axes = {axis["property_kind"]: axis for axis in manifest["axis_policies"]}
    assert set(axes) == {"formation_energy_per_atom", "band_gap"}
    assert axes["formation_energy_per_atom"]["units"] == "eV_per_atom"
    assert axes["band_gap"]["units"] == "eV"
    assert "property_range" in manifest["pre_score_split_axes"]


def test_md0002_holdout_manifest_records_acquired_pinned_no_peek_boundaries():
    manifest = _load(MD0002_HOLDOUT_MANIFEST)
    dataset = _load(MD0002_DATASET)
    snapshot_checksum = hashlib.sha256(MD0002_SNAPSHOT.read_bytes()).hexdigest()
    assert manifest["manifest_id"] == "MD-0002-HOLDOUT-NOPEEK-SCAFFOLD-0001"
    assert manifest["status"] == "acquired_pinned_pending_holdout_freeze_validation"
    assert manifest["scope"]["dataset_family"] == "MD-0002"
    assert manifest["scope"]["material_scope"] == "stable_ternary_oxides"
    assert manifest["scope"]["database_version"] == "2026.04.13"
    assert manifest["scope"]["database_version"] == dataset["source_version"]
    assert manifest["scope"]["snapshot_checksum_sha256"] == snapshot_checksum
    assert manifest["scope"]["snapshot_checksum_sha256"] == dataset["snapshot_checksum_sha256"]
    assert manifest["scope"]["row_count_per_axis"] == 362
    assert manifest["scope"]["frozen_split_counts_per_axis"] == {
        "train": 253,
        "validation": 55,
        "holdout": 54,
    }
    assert manifest["promotion_boundary"]["live_fetch_allowed"] is False
    assert manifest["promotion_boundary"]["results_allowed"] is False
    assert manifest["promotion_boundary"]["claims_allowed"] is False
    axes = {axis["property_kind"]: axis for axis in manifest["axis_policies"]}
    assert set(axes) == {"formation_energy_per_atom", "band_gap"}
    assert axes["formation_energy_per_atom"]["units"] == "eV_per_atom"
    assert axes["band_gap"]["units"] == "eV"
    split_axes = set(manifest["pre_score_split_axes"])
    assert {
        "material_id_modulo",
        "seeded_random",
        "cation_pair_family",
        "spacegroup_or_prototype",
        "property_range_bins",
        "source_version",
    } <= split_axes
    blocked = "\n".join(manifest["blocked_actions"])
    assert "Run baseline metrics or residual maps" in blocked
    assert "Change value-bearing MD-0002 row ids" in blocked
    assert "Pool formation_energy_per_atom with band_gap" in blocked
