"""Frozen Joback normal-boiling-point (Tb) estimator and fidelity fixture.

This module is the *frozen candidate* for the bounded ThermoML Tb transfer audit
(TASK-0841). It implements the Joback & Reid (1987) group-contribution estimator
for the normal boiling point:

    Tb = base + sum_i n_i * dTb_i   (Kelvin)

and nothing else. It does **not** fit anything, ingest any ThermoML row, compute
any benchmark/transfer metric, or assess the physical accuracy of Joback's
method. Its job is to (a) compute a structure-only Tb from a frozen group count
and (b) pass an implementation-fidelity gate against published predicted Tb
values *before* any benchmark is allowed to read transfer error. An off-by-one
group assignment must not be allowed to masquerade as a "method failure"; the
fixture below is the gate that catches exactly that.

Scope and exclusions:

- Tb ONLY. Tc is intentionally not implemented here: Joback's Tc estimator is a
  function of Tb (``Tc = Tb * [0.584 + 0.965*sum(dTc) - sum(dTc)**2]**-1``), so
  auditing Tc with an experimental Tb substituted is an information-leakage path.
  See ``docs/reviews/thermoml-joback-source-readiness-scout.md`` (TASK-0833).
- The estimator consumes an explicit, frozen group-count mapping. It does not
  parse SMILES; deterministic structure -> group decomposition is a separate
  curation tool whose output the fixture spot-checks (the canonical decomposition
  for each fixture compound is frozen in ``JOBACK_FIDELITY_FIXTURE`` below,
  reproduced from the TASK-0833 scout note).

Two intercept conventions appear in the wild and are both pinned here so the
fixture compares each compound against *its own source's intercept* rather than
manufacturing a false 100% mismatch across a flat ~0.08 K offset:

- ``JOBACK_BASE_JR1987 = 198.2`` -- canonical Joback & Reid (1987); used by
  Wikipedia and the ``thermo`` library (acetone CC(=O)C -> 322.11 K).
- ``JOBACK_BASE_MOLECULARKNOWLEDGE = 198.12`` -- the intercept the
  molecularknowledge.com worked table is internally consistent with.

Any future *scoring* run must pin a single intercept (recommend 198.2, the
canonical Joback & Reid value); the dual-intercept handling here is a fidelity
artifact-control, not a scoring convention.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

# --- Frozen intercepts ------------------------------------------------------

JOBACK_BASE_JR1987 = 198.2
"""Canonical Joback & Reid (1987) Tb intercept (K). Recommended for scoring."""

JOBACK_BASE_MOLECULARKNOWLEDGE = 198.12
"""Intercept the molecularknowledge.com worked Tb table is consistent with (K)."""

# Fidelity-match tolerance (K). Matches the TASK-0833 scout convention.
FIDELITY_TOLERANCE_K = 0.05


# --- Frozen Joback & Reid (1987) Tb group-contribution table ----------------
#
# Group key -> dTb,i contribution in Kelvin, from the canonical Joback & Reid
# (1987) 41-group table as tabulated on the Wikipedia "Joback method" page and
# cross-checked against the ``thermo`` library (TASK-0833). Ring vs non-ring
# variants are distinct keys, exactly as Joback defines them. This table is the
# frozen group set; it is organics-only and does not cover organometallics,
# boron/silicon/phosphorus-centred groups, charged centres, or isotopic labels.

JOBACK_TB_GROUPS: dict[str, float] = {
    # --- non-ring carbon ---
    "-CH3": 23.58,
    "-CH2-": 22.88,
    ">CH-": 21.74,
    ">C<": 18.25,
    "=CH2": 18.18,
    "=CH-": 24.96,
    "=C<": 24.14,
    "=C=": 26.15,
    "#CH": 9.20,
    "#C-": 27.38,
    # --- ring carbon ---
    "ring -CH2-": 27.15,
    "ring >CH-": 21.78,
    "ring >C<": 21.32,
    "ring =CH-": 26.73,
    "ring =C<": 31.01,
    # --- halogens ---
    "-F": -0.03,
    "-Cl": 38.13,
    "-Br": 66.86,
    "-I": 93.84,
    # --- oxygen ---
    "-OH (alcohol)": 92.88,
    "-OH (phenol)": 76.34,
    "-O- (non-ring)": 22.42,
    "ring -O-": 31.22,
    ">C=O (non-ring)": 76.75,
    "ring >C=O": 94.97,
    "O=CH- (aldehyde)": 72.24,
    "-COOH (acid)": 169.09,
    "-COO- (ester)": 81.10,
    "=O (other than above)": -10.50,
    # --- nitrogen ---
    "-NH2": 73.23,
    ">NH (non-ring)": 50.17,
    "ring >NH": 52.82,
    ">N- (non-ring)": 11.74,
    "-N= (non-ring)": 74.60,
    "ring -N=": 57.55,
    "=NH": 83.08,
    "-CN": 125.66,
    "-NO2": 152.54,
    # --- sulfur ---
    "-SH": 63.56,
    "-S- (non-ring)": 68.78,
    "ring -S-": 52.10,
}
"""Frozen Joback & Reid (1987) Tb group-contribution table (K), organics-only."""


class GroupCoverageError(ValueError):
    """Raised when a requested group is outside the frozen Joback Tb table.

    An out-of-coverage group means the molecule is out of Joback coverage and
    must be *excluded* from the audit, never force-fit. This mirrors the frozen
    group-assignment rule (every heavy atom covered by exactly one tabulated
    group, else out-of-coverage).
    """


def joback_tb(
    group_counts: Mapping[str, int],
    *,
    base: float = JOBACK_BASE_JR1987,
    table: Mapping[str, float] = JOBACK_TB_GROUPS,
) -> float:
    """Return the Joback Tb estimate (K) for a frozen group-count mapping.

    ``Tb = base + sum_i n_i * dTb_i``. ``base`` defaults to the canonical Joback
    & Reid (1987) intercept (198.2 K). A group key absent from ``table`` raises
    :class:`GroupCoverageError` (out-of-coverage; exclude, do not force-fit).
    """

    if not group_counts:
        raise ValueError("group_counts must be a non-empty mapping")
    total = float(base)
    for group, count in group_counts.items():
        if count <= 0:
            raise ValueError(f"group count must be positive: {group}={count}")
        if group not in table:
            raise GroupCoverageError(
                f"group {group!r} is outside the frozen Joback Tb table "
                f"(molecule is out-of-coverage; exclude it)"
            )
        total += int(count) * float(table[group])
    return total


def joback_group_sum(
    group_counts: Mapping[str, int],
    *,
    table: Mapping[str, float] = JOBACK_TB_GROUPS,
) -> float:
    """Return ``sum_i n_i * dTb_i`` (K) without the intercept."""

    return joback_tb(group_counts, base=0.0, table=table) - 0.0


@dataclass(frozen=True)
class FidelityCompound:
    """A frozen Joback Tb fidelity reference compound (predicted-value match)."""

    name: str
    smiles: str
    group_counts: Mapping[str, int]
    base: float
    published_tb_k: float
    secondary_functions: tuple[str, ...] = field(default_factory=tuple)

    def computed_tb_k(self) -> float:
        return joback_tb(self.group_counts, base=self.base)

    def abs_error_k(self) -> float:
        return abs(self.computed_tb_k() - self.published_tb_k)

    def matches(self, tolerance_k: float = FIDELITY_TOLERANCE_K) -> bool:
        return self.abs_error_k() <= tolerance_k


# --- Frozen 25-compound Joback Tb fidelity fixture --------------------------
#
# Reproduced verbatim (group decompositions, intercept per source, published
# predicted Tb) from the TASK-0833 scout note fixture table, which compared
# computed vs published *predicted* Tb and reported 0 mismatches / 25. The
# audit target is "did our implementation reproduce the published method", which
# is why the comparison is against published *predicted* Tb (not experimental
# Tb) and why each compound uses its own source's intercept. Two construction
# traps the scout caught are retained as worked regression evidence: the
# 198.2/198.12 intercept variant, and the ethyl-thioacetate decomposition (a
# missing -CH2- once manufactured a ~23 K outlier; corrected grouping matches).

JOBACK_FIDELITY_FIXTURE: tuple[FidelityCompound, ...] = (
    FidelityCompound(
        "Acetone", "CC(C)=O",
        {"-CH3": 2, ">C=O (non-ring)": 1},
        JOBACK_BASE_JR1987, 322.11,
    ),
    FidelityCompound(
        "Benzene", "c1ccccc1",
        {"ring =CH-": 6},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 358.50,
    ),
    FidelityCompound(
        "Toluene", "Cc1ccccc1",
        {"-CH3": 1, "ring =C<": 1, "ring =CH-": 5},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 386.36,
    ),
    FidelityCompound(
        "o-Xylene", "Cc1ccccc1C",
        {"-CH3": 2, "ring =C<": 2, "ring =CH-": 4},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 414.22,
    ),
    FidelityCompound(
        "Styrene", "C=Cc1ccccc1",
        {"=CH2": 1, "=CH-": 1, "ring =C<": 1, "ring =CH-": 5},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 405.92,
    ),
    FidelityCompound(
        "Isopropylbenzene", "CC(C)c1ccccc1",
        {"-CH3": 2, ">CH-": 1, "ring =C<": 1, "ring =CH-": 5},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 431.68,
    ),
    FidelityCompound(
        "Bromobenzene", "Brc1ccccc1",
        {"-Br": 1, "ring =C<": 1, "ring =CH-": 5},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 429.64,
    ),
    FidelityCompound(
        "1,2-Dichlorobenzene", "Clc1ccccc1Cl",
        {"-Cl": 2, "ring =C<": 2, "ring =CH-": 4},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 443.32,
    ),
    FidelityCompound(
        "2-Butyne", "CC#CC",
        {"-CH3": 2, "#C-": 2},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 300.04,
    ),
    FidelityCompound(
        "1-Octanol", "CCCCCCCCO",
        {"-CH3": 1, "-CH2-": 7, "-OH (alcohol)": 1},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 474.74,
    ),
    FidelityCompound(
        "Ethyl acetate", "CCOC(C)=O",
        {"-CH3": 2, "-CH2-": 1, "-COO- (ester)": 1},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 349.26,
    ),
    FidelityCompound(
        "Tetrahydrofuran", "C1CCOC1",
        {"ring -CH2-": 4, "ring -O-": 1},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 337.94,
    ),
    FidelityCompound(
        "Cyclohexanone", "O=C1CCCCC1",
        {"ring -CH2-": 5, "ring >C=O": 1},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 428.84,
    ),
    FidelityCompound(
        "Cyclohexanol", "OC1CCCCC1",
        {"ring -CH2-": 5, "ring >CH-": 1, "-OH (alcohol)": 1},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 448.53,
    ),
    FidelityCompound(
        "Ethanethiol", "CCS",
        {"-CH3": 1, "-CH2-": 1, "-SH": 1},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 308.14,
    ),
    FidelityCompound(
        "Tetrahydrothiophene", "C1CCSC1",
        {"ring -CH2-": 4, "ring -S-": 1},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 358.82,
    ),
    FidelityCompound(
        "Acrylonitrile", "C=CC#N",
        {"=CH2": 1, "=CH-": 1, "-CN": 1},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 366.92,
    ),
    FidelityCompound(
        "Benzaldehyde", "O=Cc1ccccc1",
        {"O=CH- (aldehyde)": 1, "ring =C<": 1, "ring =CH-": 5},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 435.02,
    ),
    FidelityCompound(
        "n-Heptanoic acid", "CCCCCCC(O)=O",
        {"-CH3": 1, "-CH2-": 5, "-COOH (acid)": 1},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 505.19,
    ),
    FidelityCompound(
        "n-Decanoic acid", "CCCCCCCCCC(O)=O",
        {"-CH3": 1, "-CH2-": 8, "-COOH (acid)": 1},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 573.83,
    ),
    FidelityCompound(
        "(+/-)-1-Phenylethanol", "CC(O)c1ccccc1",
        {"-CH3": 1, ">CH-": 1, "-OH (alcohol)": 1, "ring =C<": 1, "ring =CH-": 5},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 500.98,
        secondary_functions=("aromatic",),
    ),
    FidelityCompound(
        "Methyl salicylate", "COC(=O)c1ccccc1O",
        {
            "-CH3": 1,
            "-COO- (ester)": 1,
            "-OH (phenol)": 1,
            "ring =C<": 2,
            "ring =CH-": 4,
        },
        JOBACK_BASE_MOLECULARKNOWLEDGE, 548.08,
        secondary_functions=("phenol", "aromatic"),
    ),
    FidelityCompound(
        "Succinic acid", "OC(=O)CCC(O)=O",
        {"-CH2-": 2, "-COOH (acid)": 2},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 582.06,
    ),
    FidelityCompound(
        "gamma-Butyrolactone", "O=C1CCCO1",
        {"ring -CH2-": 3, "ring -O-": 1, "ring >C=O": 1},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 405.76,
    ),
    FidelityCompound(
        "Ethyl thioacetate", "CCSC(C)=O",
        {"-CH3": 2, "-CH2-": 1, ">C=O (non-ring)": 1, "-S- (non-ring)": 1},
        JOBACK_BASE_MOLECULARKNOWLEDGE, 413.69,
    ),
)
"""Frozen 25-compound Joback Tb fidelity fixture (TASK-0833 scout; 0 mismatches)."""


@dataclass(frozen=True)
class FidelityRow:
    """Per-compound fidelity result row."""

    name: str
    smiles: str
    group_sum_k: float
    base: float
    computed_tb_k: float
    published_tb_k: float
    abs_error_k: float
    match: bool


@dataclass(frozen=True)
class FidelityReport:
    """Aggregate fidelity-gate outcome for the frozen fixture."""

    tolerance_k: float
    compound_count: int
    mismatch_count: int
    max_abs_error_k: float
    rows: tuple[FidelityRow, ...]

    @property
    def passed(self) -> bool:
        return self.mismatch_count == 0


def evaluate_fidelity_fixture(
    fixture: tuple[FidelityCompound, ...] = JOBACK_FIDELITY_FIXTURE,
    *,
    tolerance_k: float = FIDELITY_TOLERANCE_K,
) -> FidelityReport:
    """Evaluate the frozen fidelity fixture and return the aggregate report.

    Each compound is recomputed from its frozen group decomposition and intercept
    and compared against its published predicted Tb. The gate passes only with
    zero mismatches; ``TASK-0841`` stops at ``IMPLEMENTATION_INCONCLUSIVE`` if any
    compound mismatches.
    """

    rows: list[FidelityRow] = []
    mismatches = 0
    max_err = 0.0
    for compound in fixture:
        computed = compound.computed_tb_k()
        err = compound.abs_error_k()
        match = err <= tolerance_k
        if not match:
            mismatches += 1
        max_err = max(max_err, err)
        rows.append(
            FidelityRow(
                name=compound.name,
                smiles=compound.smiles,
                group_sum_k=round(joback_group_sum(compound.group_counts), 2),
                base=compound.base,
                computed_tb_k=round(computed, 2),
                published_tb_k=compound.published_tb_k,
                abs_error_k=round(err, 4),
                match=match,
            )
        )
    return FidelityReport(
        tolerance_k=tolerance_k,
        compound_count=len(fixture),
        mismatch_count=mismatches,
        max_abs_error_k=round(max_err, 4),
        rows=tuple(rows),
    )
