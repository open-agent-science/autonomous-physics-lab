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
