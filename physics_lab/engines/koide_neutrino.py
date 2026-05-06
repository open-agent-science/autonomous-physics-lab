"""Neutrino Koide consistency test engine."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np


KOIDE_TARGET = 2.0 / 3.0


def koide_q(m1: float, m2: float, m3: float) -> float:
    """Compute the Koide quantity Q = (m1+m2+m3) / (sqrt(m1)+sqrt(m2)+sqrt(m3))^2."""
    if any(m < 0 for m in (m1, m2, m3)):
        raise ValueError("All masses must be non-negative.")
    denom = (math.sqrt(m1) + math.sqrt(m2) + math.sqrt(m3)) ** 2
    if denom == 0.0:
        raise ValueError("All masses are zero; Q is undefined.")
    return (m1 + m2 + m3) / denom


def nh_masses(m1: float, dm2_21: float, dm2_31: float) -> tuple[float, float, float]:
    """Return (m1, m2, m3) for normal hierarchy given the lightest mass m1."""
    m2 = math.sqrt(m1**2 + dm2_21)
    m3 = math.sqrt(m1**2 + dm2_31)
    return m1, m2, m3


def ih_masses(m3: float, dm2_21: float, dm2_32_abs: float) -> tuple[float, float, float]:
    """Return (m1, m2, m3) for inverted hierarchy given the lightest mass m3.

    IH convention: m3 < m1 < m2.
    Δm²₃₂ = m3² − m2² < 0  →  |Δm²₃₂| = m2² − m3² = Δm²₃₁ + Δm²₂₁.
    We use: m1² = m3² + |Δm²₃₂| − Δm²₂₁,  m2² = m3² + |Δm²₃₂|.
    """
    m2 = math.sqrt(m3**2 + dm2_32_abs)
    m1 = math.sqrt(m3**2 + dm2_32_abs - dm2_21)
    return m1, m2, m3


@dataclass
class HierarchyResult:
    hierarchy: str  # "NH" or "IH"
    lightest_mass_label: str  # "m1" or "m3"
    q_at_lightest_zero: float
    q_gap_to_target: float
    solution_exists: bool
    solution_lightest_mass_eV: float | None
    solution_masses_eV: tuple[float, float, float] | None
    solution_sum_eV: float | None
    planck_sum_bound_eV: float
    katrin_bound_eV: float
    planck_satisfied: bool | None
    katrin_satisfied: bool | None
    verdict: str
    q_profile: list[dict[str, float]]


def _scan_q_profile(
    hierarchy: str,
    dm2_21: float,
    dm2_31_or_32: float,
    n_points: int = 200,
) -> list[dict[str, float]]:
    """Return a Q vs m_lightest profile for plotting/reporting."""
    m_max = 0.5  # eV — well above any realistic bound
    m_values = np.linspace(0.0, m_max, n_points)
    profile = []
    for m_light in m_values:
        try:
            if hierarchy == "NH":
                m1, m2, m3 = nh_masses(float(m_light), dm2_21, dm2_31_or_32)
            else:
                m1, m2, m3 = ih_masses(float(m_light), dm2_21, dm2_31_or_32)
            q = koide_q(m1, m2, m3)
            profile.append({"m_lightest_eV": float(m_light), "Q": q, "sum_eV": m1 + m2 + m3})
        except (ValueError, ZeroDivisionError):
            continue
    return profile


def run_hierarchy_test(
    hierarchy: str,
    dm2_21: float,
    dm2_31_or_32: float,
    planck_sum_bound: float,
    katrin_bound: float,
    n_profile: int = 200,
) -> HierarchyResult:
    """Test whether Q = 2/3 is achievable for a given hierarchy.

    Returns a HierarchyResult with the full analysis.
    """
    if hierarchy == "NH":
        label = "m1"
        def m_fn(m: float) -> tuple[float, float, float]:
            return nh_masses(m, dm2_21, dm2_31_or_32)
    elif hierarchy == "IH":
        label = "m3"
        def m_fn(m: float) -> tuple[float, float, float]:
            return ih_masses(m, dm2_21, dm2_31_or_32)
    else:
        raise ValueError(f"Unknown hierarchy: {hierarchy!r}")

    # Q at lightest mass = 0 (the physical maximum)
    m1, m2, m3 = m_fn(0.0)
    q_at_zero = koide_q(m1, m2, m3)
    gap = KOIDE_TARGET - q_at_zero

    # Q is monotonically decreasing from q_at_zero toward 1/3.
    # If q_at_zero < 2/3, no solution exists.
    solution_exists = q_at_zero >= KOIDE_TARGET

    solution_lightest = None
    solution_masses = None
    solution_sum = None
    planck_ok = None
    katrin_ok = None

    if solution_exists:
        # Bisect to find the lightest mass where Q = 2/3.
        lo, hi = 0.0, 1.0
        for _ in range(80):
            mid = (lo + hi) / 2.0
            ms = m_fn(mid)
            if koide_q(*ms) > KOIDE_TARGET:
                lo = mid
            else:
                hi = mid
        solution_lightest = (lo + hi) / 2.0
        ms = m_fn(solution_lightest)
        solution_masses = ms
        solution_sum = sum(ms)
        planck_ok = solution_sum <= planck_sum_bound
        katrin_ok = all(m <= katrin_bound for m in ms)

    # Verdict
    if not solution_exists:
        verdict = "INCONSISTENT"
    elif solution_exists and planck_ok and katrin_ok:
        verdict = "CONSISTENT"
    elif solution_exists and (not planck_ok or not katrin_ok):
        verdict = "SOLUTION_EXCLUDED_BY_BOUNDS"
    else:
        verdict = "INCONCLUSIVE"

    profile = _scan_q_profile(hierarchy, dm2_21, dm2_31_or_32, n_points=n_profile)

    return HierarchyResult(
        hierarchy=hierarchy,
        lightest_mass_label=label,
        q_at_lightest_zero=q_at_zero,
        q_gap_to_target=gap,
        solution_exists=solution_exists,
        solution_lightest_mass_eV=solution_lightest,
        solution_masses_eV=solution_masses,
        solution_sum_eV=solution_sum,
        planck_sum_bound_eV=planck_sum_bound,
        katrin_bound_eV=katrin_bound,
        planck_satisfied=planck_ok,
        katrin_satisfied=katrin_ok,
        verdict=verdict,
        q_profile=profile,
    )


def uncertainty_propagation(
    hierarchy: str,
    dm2_21: float,
    dm2_21_unc: float,
    dm2_31_or_32: float,
    dm2_31_or_32_unc: float,
) -> dict[str, Any]:
    """Compute Q_max uncertainty at m_lightest = 0 by finite differences."""
    def q_max(d21: float, d31: float) -> float:
        if hierarchy == "NH":
            ms = nh_masses(0.0, d21, d31)
        else:
            ms = ih_masses(0.0, d21, d31)
        return koide_q(*ms)

    q_central = q_max(dm2_21, dm2_31_or_32)
    dq_d21 = (q_max(dm2_21 + dm2_21_unc, dm2_31_or_32) - q_max(dm2_21 - dm2_21_unc, dm2_31_or_32)) / (2 * dm2_21_unc)
    dq_d31 = (q_max(dm2_21, dm2_31_or_32 + dm2_31_or_32_unc) - q_max(dm2_21, dm2_31_or_32 - dm2_31_or_32_unc)) / (2 * dm2_31_or_32_unc)
    q_unc = math.sqrt((dq_d21 * dm2_21_unc)**2 + (dq_d31 * dm2_31_or_32_unc)**2)
    return {
        "q_max_central": q_central,
        "q_max_uncertainty_1sigma": q_unc,
        "gap_to_target": KOIDE_TARGET - q_central,
        "gap_in_sigma": (KOIDE_TARGET - q_central) / q_unc if q_unc > 0 else float("inf"),
    }
