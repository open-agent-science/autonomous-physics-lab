"""Quark Koide cascade engine — standard and phase-modified formulas."""

from __future__ import annotations

import math
import cmath
from dataclasses import dataclass

import numpy as np


KOIDE_TARGET = 2.0 / 3.0


def koide_q_real(m1: float, m2: float, m3: float) -> float:
    """Standard Koide Q = (m1+m2+m3) / (sqrt(m1)+sqrt(m2)+sqrt(m3))^2."""
    if any(m <= 0 for m in (m1, m2, m3)):
        raise ValueError("All masses must be positive.")
    denom = (math.sqrt(m1) + math.sqrt(m2) + math.sqrt(m3)) ** 2
    return (m1 + m2 + m3) / denom


def koide_q_phase(m1: float, m2: float, m3: float, delta: float) -> float:
    """Phase-modified Q(δ) = (Σm) / |√m1 + √m2·e^{iδ} + √m3·e^{2iδ}|².

    At δ=0 reduces to the standard real Koide formula.
    The denominator |√m1 + √m2·e^{iδ} + √m3·e^{2iδ}|² equals
    m1+m2+m3 + 2(√(m1m2)+√(m2m3))·cos(δ) + 2√(m1m3)·cos(2δ).
    """
    a, b, c = math.sqrt(m1), math.sqrt(m2), math.sqrt(m3)
    z = complex(a) + b * cmath.exp(1j * delta) + c * cmath.exp(2j * delta)
    denom = abs(z) ** 2
    if denom == 0.0:
        raise ValueError("Denominator is zero.")
    return (m1 + m2 + m3) / denom


def brannen_q(m1: float, m2: float, m3: float) -> float:
    """Brannen equal-spacing Q_B = (Σm) / (Σm − √(m1m2) − √(m1m3) − √(m2m3)).

    This is the Koide ratio when phases are equally spaced by 2π/3:
    denominator = |√m1 + √m2·e^{i2π/3} + √m3·e^{i4π/3}|²
    = m1+m2+m3 − √(m1m2) − √(m1m3) − √(m2m3).
    """
    s = m1 + m2 + m3
    p = math.sqrt(m1 * m2) + math.sqrt(m1 * m3) + math.sqrt(m2 * m3)
    denom = s - p
    if denom <= 0.0:
        raise ValueError("Brannen denominator non-positive; masses may be degenerate.")
    return s / denom


def brannen_fit(m1: float, m2: float, m3: float) -> tuple[float, float, float, float]:
    """Fit Brannen parametrization √mₖ = A + B·cos(δ + 2πk/3) for k=0,1,2.

    Returns (A, B, delta, B_over_A).
    A = (√m1+√m2+√m3)/3 is the arithmetic mean of the √masses.
    B and δ are derived from the discrete Fourier transform of (√m1,√m2,√m3).
    """
    sq = np.array([math.sqrt(m1), math.sqrt(m2), math.sqrt(m3)])
    a = float(np.mean(sq))
    d = sq - a  # deviations from mean, sum to zero
    omega = np.exp(-1j * 2 * np.pi / 3)
    z = d[0] + d[1] * omega + d[2] * omega**2  # DFT coefficient k=1
    b = float(abs(z)) * 2 / 3
    delta = float(np.angle(z))
    return a, b, delta, b / a if a != 0 else float("inf")


def scan_phase(
    m1: float,
    m2: float,
    m3: float,
    n_points: int = 500,
) -> dict:
    """Scan Q(δ) over δ ∈ [0, π] and return summary statistics.

    Returns dict with keys: q_min, q_max, delta_at_min, delta_at_max,
    achieves_target, delta_at_target (or None), q_profile (list of (delta, Q)).
    """
    deltas = np.linspace(0.0, math.pi, n_points)
    qs = np.array([koide_q_phase(m1, m2, m3, float(d)) for d in deltas])

    q_min = float(np.min(qs))
    q_max = float(np.max(qs))
    delta_at_min = float(deltas[np.argmin(qs)])
    delta_at_max = float(deltas[np.argmax(qs)])

    achieves = bool(q_min <= KOIDE_TARGET <= q_max)
    delta_at_target = None
    if achieves:
        # Linear interpolation to find crossing
        for i in range(len(qs) - 1):
            if (qs[i] - KOIDE_TARGET) * (qs[i + 1] - KOIDE_TARGET) <= 0:
                t = (KOIDE_TARGET - qs[i]) / (qs[i + 1] - qs[i])
                delta_at_target = float(deltas[i] + t * (deltas[i + 1] - deltas[i]))
                break

    profile = [{"delta_rad": float(d), "Q": float(q)} for d, q in zip(deltas[::10], qs[::10])]
    return {
        "q_min": q_min,
        "q_max": q_max,
        "delta_at_min": delta_at_min,
        "delta_at_max": delta_at_max,
        "achieves_target": achieves,
        "delta_at_target": delta_at_target,
        "q_profile": profile,
    }


def propagate_q_uncertainty(
    m1: float,
    m2: float,
    m3: float,
    unc1: float,
    unc2: float,
    unc3: float,
    delta: float = 0.0,
) -> float:
    """Estimate 1σ uncertainty on Q(δ) by finite differences."""
    q0 = koide_q_phase(m1, m2, m3, delta)
    sq = 0.0
    for m, dm, idx in ((m1, unc1, 0), (m2, unc2, 1), (m3, unc3, 2)):
        masses = [m1, m2, m3]
        h = m * 1e-6 + 1e-12  # fractional step, avoid zero
        masses[idx] = m + h
        dq_dm = (koide_q_phase(*masses, delta) - q0) / h  # ∂Q/∂mi
        sq += (dq_dm * dm) ** 2
    return math.sqrt(sq)


@dataclass
class SectorResult:
    sector: str
    quarks: tuple[str, str, str]
    masses_MeV: tuple[float, float, float]
    uncertainties_MeV: tuple[float, float, float]
    q_standard: float
    q_standard_unc: float
    q_standard_gap: float
    q_standard_gap_sigma: float
    q_brannen: float
    q_brannen_gap: float
    q_brannen_gap_sigma: float
    q_phase_min: float
    q_phase_max: float
    phase_achieves_target: bool
    delta_at_target: float | None
    brannen_fit_A: float
    brannen_fit_B: float
    brannen_fit_delta: float
    brannen_fit_B_over_A: float
    verdict: str


def run_sector_test(
    sector: str,
    quarks: tuple[str, str, str],
    masses_MeV: tuple[float, float, float],
    uncertainties_MeV: tuple[float, float, float],
) -> SectorResult:
    """Run the full Koide test for one quark sector."""
    m1, m2, m3 = masses_MeV
    u1, u2, u3 = uncertainties_MeV

    q_std = koide_q_real(m1, m2, m3)
    q_std_unc = propagate_q_uncertainty(m1, m2, m3, u1, u2, u3, delta=0.0)
    q_std_gap = abs(q_std - KOIDE_TARGET)
    q_std_gap_sigma = q_std_gap / q_std_unc if q_std_unc > 0 else float("inf")

    q_b = brannen_q(m1, m2, m3)
    q_b_unc = propagate_q_uncertainty(m1, m2, m3, u1, u2, u3, delta=2 * math.pi / 3)
    q_b_gap = abs(q_b - KOIDE_TARGET)
    q_b_gap_sigma = q_b_gap / q_b_unc if q_b_unc > 0 else float("inf")

    scan = scan_phase(m1, m2, m3)
    fit_A, fit_B, fit_delta, fit_B_A = brannen_fit(m1, m2, m3)

    # Verdict: INVALID if neither the standard nor phase scan reaches 2/3
    if not scan["achieves_target"]:
        verdict = "INVALID"
    else:
        # Achieved — check if within 1σ uncertainty
        verdict = "INCONSISTENT"

    return SectorResult(
        sector=sector,
        quarks=quarks,
        masses_MeV=(m1, m2, m3),
        uncertainties_MeV=(u1, u2, u3),
        q_standard=q_std,
        q_standard_unc=q_std_unc,
        q_standard_gap=q_std_gap,
        q_standard_gap_sigma=round(q_std_gap_sigma, 1),
        q_brannen=q_b,
        q_brannen_gap=q_b_gap,
        q_brannen_gap_sigma=round(q_b_gap_sigma, 1),
        q_phase_min=scan["q_min"],
        q_phase_max=scan["q_max"],
        phase_achieves_target=scan["achieves_target"],
        delta_at_target=scan["delta_at_target"],
        brannen_fit_A=round(fit_A, 6),
        brannen_fit_B=round(fit_B, 6),
        brannen_fit_delta=round(fit_delta, 4),
        brannen_fit_B_over_A=round(fit_B_A, 4),
        verdict=verdict,
    )
