"""Semi-empirical nuclear-mass baseline helpers."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np

from physics_lab.engines.nuclear_masses import ATOMIC_MASS_UNIT_MEV, NuclearMassEntry


MAGIC_NUMBERS = (2, 8, 20, 28, 50, 82, 126)


@dataclass(frozen=True)
class SemiEmpiricalCoefficients:
    """Coefficient set for a semi-empirical binding-energy baseline."""

    volume: float
    surface: float
    coulomb: float
    asymmetry: float
    pairing: float

    def to_dict(self) -> dict[str, float]:
        return {
            "volume": self.volume,
            "surface": self.surface,
            "coulomb": self.coulomb,
            "asymmetry": self.asymmetry,
            "pairing": self.pairing,
        }


REFERENCE_SEMI_EMPIRICAL_COEFFICIENTS = SemiEmpiricalCoefficients(
    volume=15.8,
    surface=18.3,
    coulomb=0.714,
    asymmetry=23.2,
    pairing=12.0,
)


@dataclass(frozen=True)
class BaselineResidualRow:
    """Per-nuclide baseline residual and diagnostic flags."""

    model_id: str
    nuclide_id: str
    Z: int
    N: int
    A: int
    pairing_class: str
    observed_binding_energy_mev: float
    predicted_binding_energy_mev: float
    residual_mev: float
    normalized_residual: float | None
    is_magic_z: bool
    is_magic_n: bool
    is_magic_any: bool
    near_magic: bool
    neutron_rich: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "model_id": self.model_id,
            "nuclide_id": self.nuclide_id,
            "Z": self.Z,
            "N": self.N,
            "A": self.A,
            "pairing_class": self.pairing_class,
            "observed_binding_energy_mev": self.observed_binding_energy_mev,
            "predicted_binding_energy_mev": self.predicted_binding_energy_mev,
            "residual_mev": self.residual_mev,
            "normalized_residual": self.normalized_residual,
            "is_magic_z": self.is_magic_z,
            "is_magic_n": self.is_magic_n,
            "is_magic_any": self.is_magic_any,
            "near_magic": self.near_magic,
            "neutron_rich": self.neutron_rich,
        }


def pairing_sign(z: int, n: int) -> int:
    """Return the canonical pairing sign for the semi-empirical formula."""
    if z % 2 == 0 and n % 2 == 0:
        return 1
    if z % 2 == 1 and n % 2 == 1:
        return -1
    return 0


def pairing_class(z: int, n: int) -> str:
    """Return the odd-even class for a nuclide."""
    sign = pairing_sign(z, n)
    if sign > 0:
        return "even_even"
    if sign < 0:
        return "odd_odd"
    return "odd_a"


def semi_empirical_binding_energy(
    *,
    z: int,
    n: int,
    coefficients: SemiEmpiricalCoefficients,
) -> float:
    """Compute the semi-empirical binding energy in MeV."""
    a = z + n
    a_float = float(a)
    surface_term = coefficients.surface * (a_float ** (2.0 / 3.0))
    coulomb_term = coefficients.coulomb * (z * (z - 1)) / (a_float ** (1.0 / 3.0))
    asymmetry_term = coefficients.asymmetry * ((n - z) ** 2) / a_float
    pairing_term = pairing_sign(z, n) * coefficients.pairing / math.sqrt(a_float)
    return (
        coefficients.volume * a_float
        - surface_term
        - coulomb_term
        - asymmetry_term
        + pairing_term
    )


def semi_empirical_atomic_mass_u(
    *,
    z: int,
    n: int,
    coefficients: SemiEmpiricalCoefficients,
) -> float:
    """Convert the baseline binding-energy prediction into atomic mass units."""
    from physics_lab.engines.nuclear_masses import HYDROGEN_ATOM_MASS_U, NEUTRON_MASS_U

    binding_energy = semi_empirical_binding_energy(z=z, n=n, coefficients=coefficients)
    mass_defect_u = binding_energy / ATOMIC_MASS_UNIT_MEV
    return (z * HYDROGEN_ATOM_MASS_U) + (n * NEUTRON_MASS_U) - mass_defect_u


def fit_semi_empirical_coefficients(
    entries: Iterable[NuclearMassEntry],
) -> SemiEmpiricalCoefficients:
    """Fit semi-empirical coefficients by least squares on observed binding energy."""
    rows = list(entries)
    design_matrix = np.asarray([_design_row(entry.Z, entry.N) for entry in rows], dtype=float)
    targets = np.asarray([entry.binding_energy_mev for entry in rows], dtype=float)
    solution, *_ = np.linalg.lstsq(design_matrix, targets, rcond=None)
    return SemiEmpiricalCoefficients(
        volume=float(solution[0]),
        surface=float(solution[1]),
        coulomb=float(solution[2]),
        asymmetry=float(solution[3]),
        pairing=float(solution[4]),
    )


def evaluate_baseline(
    *,
    entries: Iterable[NuclearMassEntry],
    model_id: str,
    coefficients: SemiEmpiricalCoefficients,
) -> list[BaselineResidualRow]:
    """Evaluate one coefficient set on a nuclear-mass dataset."""
    rows: list[BaselineResidualRow] = []
    for entry in entries:
        predicted_binding_energy = semi_empirical_binding_energy(
            z=entry.Z,
            n=entry.N,
            coefficients=coefficients,
        )
        residual_mev = entry.binding_energy_mev - predicted_binding_energy
        sigma_mev = binding_energy_uncertainty_mev(entry)
        rows.append(
            BaselineResidualRow(
                model_id=model_id,
                nuclide_id=entry.nuclide_id,
                Z=entry.Z,
                N=entry.N,
                A=entry.A,
                pairing_class=pairing_class(entry.Z, entry.N),
                observed_binding_energy_mev=entry.binding_energy_mev,
                predicted_binding_energy_mev=predicted_binding_energy,
                residual_mev=residual_mev,
                normalized_residual=(
                    None if sigma_mev is None or sigma_mev <= 0 else residual_mev / sigma_mev
                ),
                is_magic_z=entry.Z in MAGIC_NUMBERS,
                is_magic_n=entry.N in MAGIC_NUMBERS,
                is_magic_any=(entry.Z in MAGIC_NUMBERS) or (entry.N in MAGIC_NUMBERS),
                near_magic=_nearest_magic_distance(entry.Z) <= 2 or _nearest_magic_distance(entry.N) <= 2,
                neutron_rich=(entry.N - entry.Z) >= 20,
            )
        )
    rows.sort(key=lambda row: (row.A, row.Z, row.N, row.nuclide_id))
    return rows


def binding_energy_uncertainty_mev(entry: NuclearMassEntry) -> float | None:
    """Propagate atomic-mass uncertainty into binding-energy uncertainty."""
    if entry.atomic_mass_uncertainty_u is None:
        return None
    return entry.atomic_mass_uncertainty_u * ATOMIC_MASS_UNIT_MEV


def summarize_absolute_metrics(rows: Iterable[BaselineResidualRow]) -> dict[str, float | None]:
    """Compute absolute residual summaries for one subset."""
    row_list = list(rows)
    residuals = np.asarray([row.residual_mev for row in row_list], dtype=float)
    normalized = [abs(row.normalized_residual) for row in row_list if row.normalized_residual is not None]
    return {
        "count": float(len(row_list)),
        "mean_residual_mev": float(np.mean(residuals)) if len(residuals) else None,
        "mae_mev": float(np.mean(np.abs(residuals))) if len(residuals) else None,
        "rmse_mev": float(np.sqrt(np.mean(residuals**2))) if len(residuals) else None,
        "max_abs_residual_mev": float(np.max(np.abs(residuals))) if len(residuals) else None,
        "mean_abs_normalized_residual": float(np.mean(normalized)) if normalized else None,
        "max_abs_normalized_residual": float(np.max(normalized)) if normalized else None,
    }


def top_residual_rows(
    rows: Iterable[BaselineResidualRow],
    *,
    limit: int = 5,
) -> list[BaselineResidualRow]:
    """Return the largest absolute residual rows."""
    return sorted(rows, key=lambda row: abs(row.residual_mev), reverse=True)[:limit]


def _design_row(z: int, n: int) -> tuple[float, float, float, float, float]:
    a = z + n
    a_float = float(a)
    return (
        a_float,
        -(a_float ** (2.0 / 3.0)),
        -(z * (z - 1)) / (a_float ** (1.0 / 3.0)),
        -((n - z) ** 2) / a_float,
        pairing_sign(z, n) / math.sqrt(a_float),
    )


def _nearest_magic_distance(value: int) -> int:
    return min(abs(value - magic) for magic in MAGIC_NUMBERS)

