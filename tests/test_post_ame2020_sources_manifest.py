from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
import yaml

from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset


def _load_manifest() -> dict[str, object]:
    repo_root = Path(__file__).resolve().parent.parent
    manifest_path = repo_root / "data" / "nuclear_masses" / "post_ame2020_sources.yaml"
    payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_post_ame2020_source_manifest_matches_schema() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    schema_path = repo_root / "physics_lab" / "schemas" / "post_ame2020_sources.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(_load_manifest()),
        key=lambda error: list(error.absolute_path),
    )
    assert errors == []


def test_post_ame2020_manifest_pins_stable_source_identifiers() -> None:
    manifest = _load_manifest()
    assert manifest["task_id"] == "TASK-0187"
    assert manifest["activation_status"]["row_level_holdout_dataset_committed"] is False
    assert manifest["activation_status"]["time_split_holdout_active"] is False
    assert manifest["source_policy"]["live_fetch_allowed_in_validation"] is False
    assert manifest["source_policy"]["row_values_committed"] is False

    sources = {source["source_id"]: source for source in manifest["sources"]}
    assert "post_ame2020_compilation_nst_2025" in sources
    assert "ame2020_amdc_reference" in sources
    assert sources["post_ame2020_compilation_nst_2025"]["stable_source_identifier"] == (
        "doi:10.1007/s41365-025-01821-1"
    )
    assert "296" in sources["post_ame2020_compilation_nst_2025"]["scope_summary"]
    assert "2021" in sources["post_ame2020_compilation_nst_2025"]["scope_summary"]
    assert "2024" in sources["post_ame2020_compilation_nst_2025"]["scope_summary"]


def test_post_ame2020_manifest_excludes_current_frozen_baseline_slice() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    dataset = load_nuclear_mass_dataset(
        repo_root / "data" / "nuclear_masses" / "nmd-0002-curated-measured-slice.yaml"
    )
    manifest = _load_manifest()
    excluded = set(manifest["baseline_boundary"]["excluded_frozen_baseline_nuclides"])
    current_slice = {entry.nuclide_id for entry in dataset.entries}

    assert current_slice <= excluded
    assert manifest["baseline_boundary"]["frozen_baseline_surface"] == "NMD-0002"
    assert any(
        "Exclude frozen NMD-0002 nuclides" in rule
        for rule in manifest["candidate_row_import_plan"]["required_row_filters"]
    )
