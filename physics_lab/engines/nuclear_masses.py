"""Pinned nuclear mass dataset loading and deterministic derived helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.validation import validate_document


ATOMIC_MASS_UNIT_MEV = 931.49410242
HYDROGEN_ATOM_MASS_U = 1.00782503223
NEUTRON_MASS_U = 1.00866491595


@dataclass(frozen=True)
class NuclearMassEntry:
    """Normalized nuclear mass entry with deterministic derived quantities."""

    nuclide_id: str
    element: str
    symbol: str
    Z: int
    N: int
    A: int
    evaluation: str
    source_entry: str
    notes: str
    atomic_mass_u: float
    atomic_mass_uncertainty_u: float | None
    mass_excess_keV: float
    mass_excess_uncertainty_keV: float | None

    @property
    def binding_energy_mev(self) -> float:
        """Return total binding energy derived from atomic mass."""
        return binding_energy_mev_from_atomic_mass_u(
            z=self.Z,
            n=self.N,
            atomic_mass_u=self.atomic_mass_u,
        )

    @property
    def binding_energy_per_nucleon_mev(self) -> float:
        """Return binding energy per nucleon."""
        return self.binding_energy_mev / float(self.A)

    def to_target_row(self) -> dict[str, Any]:
        """Return a baseline-ready row for later residual workflows."""
        return {
            "nuclide_id": self.nuclide_id,
            "element": self.element,
            "symbol": self.symbol,
            "Z": self.Z,
            "N": self.N,
            "A": self.A,
            "evaluation": self.evaluation,
            "atomic_mass_u": self.atomic_mass_u,
            "atomic_mass_uncertainty_u": self.atomic_mass_uncertainty_u,
            "mass_excess_keV": self.mass_excess_keV,
            "mass_excess_uncertainty_keV": self.mass_excess_uncertainty_keV,
            "binding_energy_mev": self.binding_energy_mev,
            "binding_energy_per_nucleon_mev": self.binding_energy_per_nucleon_mev,
            "source_entry": self.source_entry,
        }


@dataclass(frozen=True)
class NuclearMassDataset:
    """Schema-validated nuclear mass dataset."""

    dataset_id: str
    title: str
    status: str
    description: str
    source_policy: str
    source_dataset: dict[str, Any]
    entries: tuple[NuclearMassEntry, ...]

    def target_rows(self) -> list[dict[str, Any]]:
        """Return normalized rows for baseline and holdout workflows."""
        return [entry.to_target_row() for entry in self.entries]


def atomic_mass_u_from_mass_excess_keV(*, a: int, mass_excess_keV: float) -> float:
    """Convert mass excess in keV to atomic mass units."""
    return float(a) + (mass_excess_keV / 1000.0) / ATOMIC_MASS_UNIT_MEV


def mass_excess_keV_from_atomic_mass_u(*, a: int, atomic_mass_u: float) -> float:
    """Convert atomic mass units to mass excess in keV."""
    return (atomic_mass_u - float(a)) * ATOMIC_MASS_UNIT_MEV * 1000.0


def binding_energy_mev_from_atomic_mass_u(*, z: int, n: int, atomic_mass_u: float) -> float:
    """Compute total binding energy from atomic mass."""
    mass_defect_u = (z * HYDROGEN_ATOM_MASS_U) + (n * NEUTRON_MASS_U) - atomic_mass_u
    return mass_defect_u * ATOMIC_MASS_UNIT_MEV


def load_nuclear_mass_dataset(path: str | Path) -> NuclearMassDataset:
    """Load and normalize a schema-validated nuclear mass dataset."""
    dataset_path = Path(path)
    with dataset_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)

    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping in nuclear mass dataset: {dataset_path}")

    validate_document(payload, kind="nuclear_mass_dataset", source=dataset_path)
    entries = tuple(_normalize_entry(entry) for entry in payload["entries"])
    return NuclearMassDataset(
        dataset_id=str(payload["dataset_id"]),
        title=str(payload["title"]),
        status=str(payload["status"]),
        description=str(payload["description"]),
        source_policy=str(payload["source_policy"]),
        source_dataset=dict(payload["source_dataset"]),
        entries=entries,
    )


def _normalize_entry(entry: dict[str, Any]) -> NuclearMassEntry:
    z = int(entry["Z"])
    n = int(entry["N"])
    a = int(entry["A"])
    if z + n != a:
        raise ValueError(
            f"Nuclide {entry['nuclide_id']} has inconsistent nucleon counts: Z + N != A"
        )

    atomic_mass_u = entry.get("atomic_mass_u")
    mass_excess_keV = entry.get("mass_excess_keV")

    if atomic_mass_u is None and mass_excess_keV is None:
        raise ValueError(
            f"Nuclide {entry['nuclide_id']} must provide atomic mass or mass excess."
        )

    atomic_mass_uncertainty_u = entry.get("atomic_mass_uncertainty_u")
    mass_excess_uncertainty_keV = entry.get("mass_excess_uncertainty_keV")

    if atomic_mass_u is None:
        atomic_mass_u = atomic_mass_u_from_mass_excess_keV(
            a=a,
            mass_excess_keV=float(mass_excess_keV),
        )
        if mass_excess_uncertainty_keV is not None:
            atomic_mass_uncertainty_u = float(mass_excess_uncertainty_keV) / (
                1000.0 * ATOMIC_MASS_UNIT_MEV
            )

    if mass_excess_keV is None:
        mass_excess_keV = mass_excess_keV_from_atomic_mass_u(
            a=a,
            atomic_mass_u=float(atomic_mass_u),
        )
        if atomic_mass_uncertainty_u is not None:
            mass_excess_uncertainty_keV = (
                float(atomic_mass_uncertainty_u) * ATOMIC_MASS_UNIT_MEV * 1000.0
            )

    return NuclearMassEntry(
        nuclide_id=str(entry["nuclide_id"]),
        element=str(entry["element"]),
        symbol=str(entry["symbol"]),
        Z=z,
        N=n,
        A=a,
        evaluation=str(entry["evaluation"]),
        source_entry=str(entry["source_entry"]),
        notes=str(entry["notes"]),
        atomic_mass_u=float(atomic_mass_u),
        atomic_mass_uncertainty_u=(
            None if atomic_mass_uncertainty_u is None else float(atomic_mass_uncertainty_u)
        ),
        mass_excess_keV=float(mass_excess_keV),
        mass_excess_uncertainty_keV=(
            None
            if mass_excess_uncertainty_keV is None
            else float(mass_excess_uncertainty_keV)
        ),
    )
