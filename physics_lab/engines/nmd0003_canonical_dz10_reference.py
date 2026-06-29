"""Metadata-only wrapper for the canonical AMDC DZ10 reference table.

The AMDC DZ10 numeric table is an external source artifact whose bytes are not
vendored in this repository. This module records the accepted locator/checksum
metadata from the TASK-0853 scout, parses a local copy when one is supplied, and
keeps a tiny smoke fixture for deterministic parser/parity checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from physics_lab.engines.nmd0003_duflo_zuker_baseline import (
    PUBLISHED_DZ10_FULL_COEFFICIENTS,
    predict_duflo_zuker_binding_energy,
)
from physics_lab.engines.nuclear_masses import (
    ATOMIC_MASS_UNIT_MEV,
    HYDROGEN_ATOM_MASS_U,
    NEUTRON_MASS_U,
    mass_excess_keV_from_atomic_mass_u,
)

DZ10_AMDC_METADATA = {
    "source_id": "amdc-dz10-feb96",
    "page_url": "https://www-nds.iaea.org/amdc/web/dz.html",
    "table_url": "https://www-nds.iaea.org/amdc/theory/du_zu_10.feb96",
    "fortran_url": "https://www-nds.iaea.org/amdc/theory/du_zu_10.feb96fort",
    "table_sha256": "b80d64caf878ed837b5544d22920e4499d4869053d934d0068c5aab0bcc7ea7b",
    "table_byte_size": 196049,
    "fortran_sha256": "cccc8406cfdd0fb79c11ace0dcae2b06df443fa4c4fc852f3114b657a125a25a",
    "fortran_byte_size": 12231,
    "table_format": "i5, i5, f10.3: Z A Mass-Excess (MeV)",
    "source_bytes_redistribution": "not_cleared",
    "source_bytes_policy": "metadata_only_locator_and_checksum_default",
    "fixture_reference": "docs/reviews/canonical-dz-parity-reference-scout.md",
}


@dataclass(frozen=True)
class Dz10MassExcessPoint:
    """One canonical DZ10 mass-excess row from the AMDC table."""

    z: int
    a: int
    mass_excess_mev: float

    @property
    def n(self) -> int:
        """Return neutron number."""
        return self.a - self.z

    def key(self) -> tuple[int, int]:
        """Return the table lookup key, keyed by (Z, A)."""
        return (self.z, self.a)


DZ10_SMOKE_FIXTURE = (
    Dz10MassExcessPoint(z=8, a=16, mass_excess_mev=-5.150),
    Dz10MassExcessPoint(z=37, a=90, mass_excess_mev=-78.959),
    Dz10MassExcessPoint(z=50, a=132, mass_excess_mev=-76.052),
    Dz10MassExcessPoint(z=82, a=208, mass_excess_mev=-22.621),
    Dz10MassExcessPoint(z=92, a=238, mass_excess_mev=47.483),
    Dz10MassExcessPoint(z=122, a=297, mass_excess_mev=223.211),
)


def parse_dz10_mass_excess_table(text: str) -> tuple[Dz10MassExcessPoint, ...]:
    """Parse an AMDC DZ10 mass-excess table or fixture excerpt.

    Header lines are skipped. Data rows are expected to contain at least three
    whitespace-separated fields: Z, A, and mass excess in MeV. The official table
    advertises fixed-width format ``i5, i5, f10.3``; whitespace parsing preserves
    the same values without depending on exact column offsets.
    """
    rows: list[Dz10MassExcessPoint] = []
    seen: set[tuple[int, int]] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        parts = line.strip().split()
        if len(parts) < 3:
            continue
        try:
            z = int(parts[0])
            a = int(parts[1])
            mass_excess_mev = float(parts[2])
        except ValueError:
            continue
        if z < 0 or a < z:
            raise ValueError(f"Invalid DZ10 row at line {line_number}: {line!r}")
        key = (z, a)
        if key in seen:
            raise ValueError(f"Duplicate DZ10 row for Z={z}, A={a}")
        seen.add(key)
        rows.append(
            Dz10MassExcessPoint(
                z=z,
                a=a,
                mass_excess_mev=mass_excess_mev,
            )
        )
    if not rows:
        raise ValueError("No DZ10 mass-excess rows parsed.")
    return tuple(rows)


def load_dz10_mass_excess_table(path: str | Path) -> tuple[Dz10MassExcessPoint, ...]:
    """Load a local, externally supplied DZ10 table copy."""
    return parse_dz10_mass_excess_table(Path(path).read_text(encoding="utf-8"))


def format_dz10_fixture_text(rows: Iterable[Dz10MassExcessPoint]) -> str:
    """Return fixed-width fixture text matching the advertised AMDC row format."""
    return "\n".join(
        f"{row.z:5d}{row.a:5d}{row.mass_excess_mev:10.3f}" for row in rows
    )


def index_dz10_rows(
    rows: Iterable[Dz10MassExcessPoint],
) -> dict[tuple[int, int], Dz10MassExcessPoint]:
    """Build a strict (Z, A) index for DZ10 table rows."""
    index: dict[tuple[int, int], Dz10MassExcessPoint] = {}
    for row in rows:
        key = row.key()
        if key in index:
            raise ValueError(f"Duplicate DZ10 row for Z={row.z}, A={row.a}")
        index[key] = row
    return index


def lookup_dz10_mass_excess_mev(
    rows: Iterable[Dz10MassExcessPoint],
    *,
    z: int,
    a: int,
) -> float:
    """Return a canonical DZ10 table mass excess in MeV."""
    index = index_dz10_rows(rows)
    try:
        return index[(z, a)].mass_excess_mev
    except KeyError as exc:
        raise KeyError(f"DZ10 mass excess not found for Z={z}, A={a}") from exc


def validate_dz10_smoke_fixture(
    rows: Iterable[Dz10MassExcessPoint],
    *,
    tolerance_mev: float = 5.0e-4,
) -> dict[str, object]:
    """Validate parsed rows against the accepted TASK-0853 smoke fixture."""
    index = index_dz10_rows(rows)
    deltas: list[float] = []
    missing: list[str] = []
    for expected in DZ10_SMOKE_FIXTURE:
        actual = index.get(expected.key())
        if actual is None:
            missing.append(f"Z={expected.z},A={expected.a}")
            continue
        deltas.append(abs(actual.mass_excess_mev - expected.mass_excess_mev))
    max_abs_delta = max(deltas) if deltas else float("inf")
    return {
        "checked_count": len(deltas),
        "expected_count": len(DZ10_SMOKE_FIXTURE),
        "missing": tuple(missing),
        "max_abs_delta_mev": round(float(max_abs_delta), 12),
        "tolerance_mev": tolerance_mev,
        "passed": not missing and max_abs_delta <= tolerance_mev,
    }


def mass_excess_mev_from_binding_energy(*, z: int, n: int, binding_energy_mev: float) -> float:
    """Convert a binding-energy prediction to atomic mass excess in MeV."""
    atomic_mass_u = (
        z * HYDROGEN_ATOM_MASS_U
        + n * NEUTRON_MASS_U
        - binding_energy_mev / ATOMIC_MASS_UNIT_MEV
    )
    return mass_excess_keV_from_atomic_mass_u(
        a=z + n,
        atomic_mass_u=atomic_mass_u,
    ) / 1000.0


def published_variant_mass_excess_diagnostic(
    rows: Iterable[Dz10MassExcessPoint],
) -> dict[str, object]:
    """Compare the existing published-equation variant to DZ10 table rows.

    This diagnostic deliberately does not claim canonical parity. It only records
    how far the existing TASK-0823 published-equation variant is from the AMDC
    fixture on supplied rows after converting its binding-energy prediction to
    mass excess.
    """
    comparisons: list[dict[str, float | int]] = []
    for row in rows:
        predicted_binding = predict_duflo_zuker_binding_energy(
            z=row.z,
            n=row.n,
            coefficients=PUBLISHED_DZ10_FULL_COEFFICIENTS,
        )
        predicted_mass_excess = mass_excess_mev_from_binding_energy(
            z=row.z,
            n=row.n,
            binding_energy_mev=predicted_binding,
        )
        comparisons.append(
            {
                "Z": row.z,
                "A": row.a,
                "reference_mass_excess_mev": row.mass_excess_mev,
                "published_variant_mass_excess_mev": round(predicted_mass_excess, 6),
                "abs_delta_mev": round(abs(predicted_mass_excess - row.mass_excess_mev), 6),
            }
        )
    max_delta = max((item["abs_delta_mev"] for item in comparisons), default=0.0)
    return {
        "comparison_count": len(comparisons),
        "max_abs_delta_mev": max_delta,
        "comparisons": tuple(comparisons),
        "verdict": "diagnostic_only_not_canonical_parity",
    }