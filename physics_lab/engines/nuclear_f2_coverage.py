"""NMD-0003 F2 coverage-gate helper (TASK-0539).

This module computes the residual-free F2 finer-taxonomy bin populations frozen
by TASK-0478 (``docs/reviews/nuclear-f2-finer-taxonomy-preflight.md``) and checks
them against the TASK-0478 reopen coverage gate. It is a *pre-score* coverage
check: it never fits a candidate, computes candidate metrics, scores F2, or
touches any residual, baseline error, source-status, or target label.

Every bin label is a deterministic function of ``Z``, ``N``, ``A``, parity,
magic-distance, and asymmetry only, as required by the no-leakage contract
(``F2-REQ-LABEL-FROM-Z-N-ONLY``).
"""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Any, Iterable

from physics_lab.engines.nuclear_masses import NuclearMassEntry, load_nuclear_mass_dataset

# Published magic-number list for the F2 promotion path (no-leakage contract and
# TASK-0478 preflight). Note this includes 184 and therefore differs from the
# five-coefficient baseline MAGIC_NUMBERS used elsewhere.
F2_MAGIC_NUMBERS: tuple[int, ...] = (2, 8, 20, 28, 50, 82, 126, 184)

# Frozen TASK-0478 thresholds. These are pre-score declarations and must not be
# re-tuned after inspecting residuals or scores.
MAGIC_DISTANCE_THRESHOLD = 1
NEUTRON_RICH_ASYMMETRY_EDGE = 0.18
LIGHT_A_CUT = 50

# Ordered finer taxonomy; first matching bin wins.
F2_TAXONOMY: tuple[str, ...] = (
    "doubly_magic_near",
    "magic_z_near",
    "magic_n_near",
    "mid_shell_neutron_rich",
    "mid_shell_balanced",
    "light_a_lt_50",
)

# The three near-magic bins are the split of the single coarse near-magic family
# that swallowed TASK-0449; the multi-cell floor requires scored bins outside it.
NEAR_MAGIC_FAMILY: frozenset[str] = frozenset(
    {"doubly_magic_near", "magic_z_near", "magic_n_near"}
)

# Frozen TASK-0478 coverage floors.
PER_CELL_FLOOR = 5
MULTI_CELL_FLOOR = 3
OUTSIDE_NEAR_MAGIC_FLOOR = 2
TOTAL_SCORED_FLOOR = 30


def f2_magic_distance(value: int) -> int:
    """Minimum absolute distance from ``value`` to any published F2 magic number."""
    return min(abs(value - magic) for magic in F2_MAGIC_NUMBERS)


def assign_f2_bin(z: int, n: int, a: int) -> str:
    """Return the frozen residual-free F2 finer-taxonomy bin for ``(Z, N, A)``.

    Depends only on ``Z``, ``N``, ``A`` and the published magic-number list. It
    reads no residual, baseline error, residual quantile, source-status flag, or
    any error-derived quantity (``F2-REQ-LABEL-FROM-Z-N-ONLY``).
    """
    if z < 0 or n < 0 or a <= 0:
        raise ValueError(f"invalid nuclide coordinates: Z={z}, N={n}, A={a}")
    d_z = f2_magic_distance(z)
    d_n = f2_magic_distance(n)
    eta = (n - z) / a
    if d_z <= MAGIC_DISTANCE_THRESHOLD and d_n <= MAGIC_DISTANCE_THRESHOLD:
        return "doubly_magic_near"
    if d_z <= MAGIC_DISTANCE_THRESHOLD and d_n > MAGIC_DISTANCE_THRESHOLD:
        return "magic_z_near"
    if d_n <= MAGIC_DISTANCE_THRESHOLD and d_z > MAGIC_DISTANCE_THRESHOLD:
        return "magic_n_near"
    if eta >= NEUTRON_RICH_ASYMMETRY_EDGE:
        return "mid_shell_neutron_rich"
    if eta < NEUTRON_RICH_ASYMMETRY_EDGE and a >= LIGHT_A_CUT:
        return "mid_shell_balanced"
    if a < LIGHT_A_CUT:
        return "light_a_lt_50"
    # The ordered rules above are exhaustive over non-negative integers, but keep
    # an explicit guard so any future edit that breaks exhaustiveness is caught.
    raise ValueError(f"no F2 bin matched nuclide Z={z}, N={n}, A={a}")


def f2_bin_assignments(entries: Iterable[NuclearMassEntry]) -> "OrderedDict[str, list[str]]":
    """Group nuclide ids into F2 bins, preserving the declared taxonomy order."""
    grouped: OrderedDict[str, list[str]] = OrderedDict((bin_id, []) for bin_id in F2_TAXONOMY)
    for entry in entries:
        bin_id = assign_f2_bin(entry.Z, entry.N, entry.A)
        grouped[bin_id].append(entry.nuclide_id)
    for bin_id in grouped:
        grouped[bin_id].sort()
    return grouped


def evaluate_f2_coverage_gate(entries: Iterable[NuclearMassEntry]) -> dict[str, Any]:
    """Evaluate the TASK-0478 F2 reopen coverage gate on a training slice."""
    assignments = f2_bin_assignments(entries)
    populations = {bin_id: len(ids) for bin_id, ids in assignments.items()}

    bins: "OrderedDict[str, dict[str, Any]]" = OrderedDict()
    scored_bins: list[str] = []
    scored_outside_near_magic: list[str] = []
    total_scored_rows = 0
    for bin_id in F2_TAXONOMY:
        count = populations[bin_id]
        clears = count >= PER_CELL_FLOOR
        in_near_magic = bin_id in NEAR_MAGIC_FAMILY
        if clears:
            scored_bins.append(bin_id)
            total_scored_rows += count
            if not in_near_magic:
                scored_outside_near_magic.append(bin_id)
        bins[bin_id] = {
            "count": count,
            "clears_per_cell_floor": clears,
            "near_magic_family": in_near_magic,
            "role": "scored" if clears else "context_only",
        }

    multi_cell_ok = len(scored_bins) >= MULTI_CELL_FLOOR
    outside_ok = len(scored_outside_near_magic) >= OUTSIDE_NEAR_MAGIC_FLOOR
    total_ok = total_scored_rows >= TOTAL_SCORED_FLOOR
    gate_clears = multi_cell_ok and outside_ok and total_ok

    return {
        "row_count": sum(populations.values()),
        "bins": bins,
        "scored_bins": scored_bins,
        "scored_bins_outside_near_magic": scored_outside_near_magic,
        "total_scored_rows": total_scored_rows,
        "floors": {
            "per_cell_floor": PER_CELL_FLOOR,
            "multi_cell_floor": MULTI_CELL_FLOOR,
            "outside_near_magic_floor": OUTSIDE_NEAR_MAGIC_FLOOR,
            "total_scored_floor": TOTAL_SCORED_FLOOR,
        },
        "gate_criteria": {
            "multi_cell_floor_met": multi_cell_ok,
            "outside_near_magic_floor_met": outside_ok,
            "total_scored_floor_met": total_ok,
        },
        "gate_clears": gate_clears,
    }


def taxonomy_declaration() -> dict[str, Any]:
    """Return the frozen taxonomy and threshold declaration for manifests/reviews."""
    return {
        "magic_numbers": list(F2_MAGIC_NUMBERS),
        "magic_distance_threshold": MAGIC_DISTANCE_THRESHOLD,
        "neutron_rich_asymmetry_edge": NEUTRON_RICH_ASYMMETRY_EDGE,
        "light_a_cut": LIGHT_A_CUT,
        "bin_order": list(F2_TAXONOMY),
        "near_magic_family": sorted(NEAR_MAGIC_FAMILY),
        "rules": {
            "doubly_magic_near": "dZ <= 1 AND dN <= 1",
            "magic_z_near": "dZ <= 1 AND dN > 1",
            "magic_n_near": "dN <= 1 AND dZ > 1",
            "mid_shell_neutron_rich": "not near-magic AND eta >= 0.18",
            "mid_shell_balanced": "not near-magic AND eta < 0.18 AND A >= 50",
            "light_a_lt_50": "not near-magic AND eta < 0.18 AND A < 50",
        },
        "label_inputs": "Z, N, A, and published magic numbers only; no residual or source-status input",
    }


def evaluate_f2_coverage_for_dataset(dataset_path: str | Path) -> dict[str, Any]:
    """Load a committed nuclear-mass dataset and evaluate the F2 coverage gate."""
    dataset = load_nuclear_mass_dataset(dataset_path)
    entries = sorted(
        dataset.entries, key=lambda entry: (entry.A, entry.Z, entry.N, entry.nuclide_id)
    )
    gate = evaluate_f2_coverage_gate(entries)
    assignments = f2_bin_assignments(entries)
    return {
        "dataset_id": dataset.dataset_id,
        "dataset_path": str(dataset_path),
        "taxonomy": taxonomy_declaration(),
        "gate": gate,
        "bin_assignments": dict(assignments),
    }
