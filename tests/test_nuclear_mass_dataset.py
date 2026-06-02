from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from physics_lab.engines.nuclear_masses import (
    NuclearMassDataset,
    atomic_mass_u_from_mass_excess_keV,
    binding_energy_mev_from_atomic_mass_u,
    load_nuclear_mass_dataset,
    mass_excess_keV_from_atomic_mass_u,
)
from physics_lab.registry.validation import validate_document


def _sample_payload() -> dict[str, object]:
    return {
        "dataset_id": "NMD-0001",
        "title": "Sample nuclear mass dataset",
        "status": "draft",
        "description": "Two-entry sample covering atomic-mass and mass-excess encodings.",
        "source_policy": "Pinned sample for loader and schema tests only.",
        "source_dataset": {
            "authority": "Atomic Mass Evaluation",
            "version": "AME-test",
            "citation": "Synthetic fixture for repository tests.",
            "url": "https://example.org/ame-test",
            "accessed_on": "2026-05-10",
            "checksum_sha256": "0" * 64,
            "checksum_scope": "synthetic fixture payload",
            "license_note": "Test-only synthetic payload.",
        },
        "entries": [
            {
                "nuclide_id": "He-4",
                "element": "helium",
                "symbol": "He",
                "Z": 2,
                "N": 2,
                "A": 4,
                "evaluation": "measured",
                "source_entry": "synthetic-helium-row",
                "notes": "Atomic-mass encoded sample entry.",
                "atomic_mass_u": 4.00260325413,
                "atomic_mass_uncertainty_u": 0.00000000006,
            },
            {
                "nuclide_id": "C-12",
                "element": "carbon",
                "symbol": "C",
                "Z": 6,
                "N": 6,
                "A": 12,
                "evaluation": "measured",
                "source_entry": "synthetic-carbon-row",
                "notes": "Mass-excess encoded sample entry.",
                "mass_excess_keV": 0.0,
                "mass_excess_uncertainty_keV": 0.0001,
            },
        ],
    }


def _write_dataset(tmp_path: Path, payload: dict[str, object]) -> Path:
    path = tmp_path / "sample_nuclear_masses.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def test_nuclear_mass_dataset_schema_accepts_atomic_mass_and_mass_excess_entries() -> None:
    payload = _sample_payload()
    assert (
        validate_document(
            payload,
            "nuclear_mass_dataset",
            "data/nuclear_masses/sample_nuclear_masses.yaml",
        )
        == payload
    )


def test_load_nuclear_mass_dataset_normalizes_derived_fields(tmp_path: Path) -> None:
    dataset = load_nuclear_mass_dataset(_write_dataset(tmp_path, _sample_payload()))
    assert isinstance(dataset, NuclearMassDataset)
    assert dataset.dataset_id == "NMD-0001"
    assert len(dataset.entries) == 2

    helium = dataset.entries[0]
    carbon = dataset.entries[1]

    assert helium.nuclide_id == "He-4"
    assert helium.mass_excess_keV == pytest.approx(
        mass_excess_keV_from_atomic_mass_u(a=4, atomic_mass_u=4.00260325413),
        rel=0,
        abs=1e-6,
    )
    assert helium.binding_energy_mev == pytest.approx(28.2957, abs=5e-4)
    assert helium.binding_energy_per_nucleon_mev == pytest.approx(7.0739, abs=5e-4)

    assert carbon.atomic_mass_u == pytest.approx(12.0, rel=0, abs=1e-12)
    assert carbon.mass_excess_keV == pytest.approx(0.0, rel=0, abs=1e-12)
    assert carbon.binding_energy_mev == pytest.approx(92.162, abs=5e-3)
    assert carbon.atomic_mass_uncertainty_u is not None
    assert carbon.mass_excess_uncertainty_keV == pytest.approx(0.0001, rel=0, abs=1e-12)

    target_row = helium.to_target_row()
    assert target_row["binding_energy_mev"] == pytest.approx(helium.binding_energy_mev)
    assert target_row["binding_energy_per_nucleon_mev"] == pytest.approx(
        helium.binding_energy_per_nucleon_mev
    )
    assert "binding_energy_meV" not in target_row


def test_nuclear_mass_conversion_helpers_are_consistent() -> None:
    mass_excess_keV = 2424.9156
    atomic_mass_u = atomic_mass_u_from_mass_excess_keV(a=4, mass_excess_keV=mass_excess_keV)
    assert mass_excess_keV_from_atomic_mass_u(a=4, atomic_mass_u=atomic_mass_u) == pytest.approx(
        mass_excess_keV,
        rel=0,
        abs=1e-9,
    )


def test_binding_energy_helper_matches_carbon_twelve_reference_scale() -> None:
    binding_energy_mev = binding_energy_mev_from_atomic_mass_u(
        z=6,
        n=6,
        atomic_mass_u=12.0,
    )
    assert binding_energy_mev == pytest.approx(92.162, abs=5e-3)


def test_loader_rejects_inconsistent_nucleon_counts(tmp_path: Path) -> None:
    payload = _sample_payload()
    payload["entries"][0]["A"] = 5
    path = _write_dataset(tmp_path, payload)

    with pytest.raises(ValueError, match="Z \\+ N != A"):
        load_nuclear_mass_dataset(path)


def test_nmd0003_ame2020_training_dataset_is_source_gated() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    dataset_path = (
        repo_root / "data" / "nuclear_masses" / "nmd-0003-ame2020-measured-training.yaml"
    )
    source_manifest_path = repo_root / "data" / "nuclear_masses" / "nmd-0003-source-manifest.yaml"

    dataset = load_nuclear_mass_dataset(dataset_path)
    source_manifest = yaml.safe_load(source_manifest_path.read_text(encoding="utf-8"))

    assert dataset.dataset_id == "NMD-0003"
    assert len(dataset.entries) == 2309
    assert dataset.source_dataset["checksum_sha256"] == (
        "e8599c6d7f724fac91934e59f1b9de8fb8f63e820f4b39456b790665ed2a3307"
    )
    assert source_manifest["filtering"]["committed_training_row_count"] == len(dataset.entries)
    assert source_manifest["filtering"]["estimated_or_missing_rows_excluded"] == 1008

    seen: set[str] = set()
    for entry in dataset.entries:
        assert entry.evaluation == "measured"
        assert entry.Z > 0
        assert entry.A == entry.Z + entry.N
        assert entry.nuclide_id not in seen
        seen.add(entry.nuclide_id)
        assert entry.atomic_mass_uncertainty_u is not None
        assert entry.mass_excess_uncertainty_keV is not None


def test_nmd0003_split_manifest_excludes_primary_post_ame2020_holdout() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    split_path = repo_root / "data" / "nuclear_masses" / "nmd-0003-split-manifest.yaml"
    holdout_path = repo_root / "data" / "nuclear_masses" / "post_ame2020_holdout.yaml"
    nmd0002_path = repo_root / "data" / "nuclear_masses" / "nmd-0002-curated-measured-slice.yaml"

    split = yaml.safe_load(split_path.read_text(encoding="utf-8"))
    holdout = yaml.safe_load(holdout_path.read_text(encoding="utf-8"))
    nmd0002 = load_nuclear_mass_dataset(nmd0002_path)

    training_ids = set(split["training_split"]["nuclide_ids"])
    primary_holdout_ids = {
        entry["nuclide_id"]
        for entry in holdout["entries"]
        if entry["included_in_time_split_holdout"]
    }
    nmd0002_ids = {entry.nuclide_id for entry in nmd0002.entries}

    assert split["training_split"]["row_count"] == 2309
    assert len(primary_holdout_ids) == 295
    assert training_ids.isdisjoint(primary_holdout_ids)
    assert nmd0002_ids <= training_ids


def test_f2_bin_assignment_is_z_n_a_only_and_ordered() -> None:
    from physics_lab.engines.nuclear_f2_coverage import (
        F2_MAGIC_NUMBERS,
        assign_f2_bin,
    )

    # 184 is part of the F2 magic list (and absent from the baseline list).
    assert 184 in F2_MAGIC_NUMBERS
    # doubly magic: Z=8 (magic), N=8 (magic) -> dZ=0, dN=0.
    assert assign_f2_bin(8, 8, 16) == "doubly_magic_near"
    # magic Z only: Z=20 (magic), N=27 (dN=1 from 28) would be magic_n; use N=24.
    assert assign_f2_bin(20, 24, 44) == "magic_z_near"
    # magic N only: N=28 (magic), Z=24 (dZ=4) -> magic_n_near.
    assert assign_f2_bin(24, 28, 52) == "magic_n_near"
    # neutron-rich mid-shell: eta >= 0.18, not near magic.
    assert assign_f2_bin(40, 65, 105) == "mid_shell_neutron_rich"
    # balanced mid-shell heavy: eta < 0.18, A >= 50, not near magic.
    assert assign_f2_bin(46, 60, 106) == "mid_shell_balanced"
    # light: A < 50, not near magic, eta < 0.18.
    assert assign_f2_bin(15, 16, 31) == "light_a_lt_50"


def test_f2_bin_assignment_rejects_invalid_coordinates() -> None:
    from physics_lab.engines.nuclear_f2_coverage import assign_f2_bin

    with pytest.raises(ValueError):
        assign_f2_bin(-1, 5, 4)
    with pytest.raises(ValueError):
        assign_f2_bin(2, 2, 0)


def test_nmd0003_clears_f2_coverage_gate() -> None:
    from physics_lab.engines.nuclear_f2_coverage import (
        F2_TAXONOMY,
        evaluate_f2_coverage_for_dataset,
    )

    coverage = evaluate_f2_coverage_for_dataset(
        "data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml"
    )
    gate = coverage["gate"]

    # Every declared bin is populated above the per-cell floor on NMD-0003.
    assert set(gate["bins"]) == set(F2_TAXONOMY)
    assert all(info["clears_per_cell_floor"] for info in gate["bins"].values())

    # The three TASK-0478 floors are all satisfied.
    assert gate["gate_criteria"]["multi_cell_floor_met"] is True
    assert gate["gate_criteria"]["outside_near_magic_floor_met"] is True
    assert gate["gate_criteria"]["total_scored_floor_met"] is True
    assert gate["gate_clears"] is True

    # At least two scored bins are outside the dominant near-magic family.
    assert len(gate["scored_bins_outside_near_magic"]) >= 2
    assert gate["row_count"] == 2309


def test_f2_coverage_selection_manifest_matches_engine() -> None:
    manifest_path = Path("data/nuclear_masses/f2-coverage-selection-manifest.yaml")
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    from physics_lab.engines.nuclear_f2_coverage import evaluate_f2_coverage_for_dataset

    coverage = evaluate_f2_coverage_for_dataset(manifest["source_dataset"])
    gate = coverage["gate"]

    assert manifest["gate_result"]["gate_clears"] == gate["gate_clears"]
    assert manifest["gate_result"]["total_scored_rows"] == gate["total_scored_rows"]
    manifest_counts = {row["bin"]: row["count"] for row in manifest["bins"]}
    engine_counts = {bin_id: info["count"] for bin_id, info in gate["bins"].items()}
    assert manifest_counts == engine_counts
