"""Particle-mass relation falsifier helpers."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np


KOIDE_TARGET = 2.0 / 3.0
Q_RANGE_MIN = 1.0 / 3.0
Q_RANGE_MAX = 1.0


@dataclass(frozen=True)
class ParticleMassInput:
    """One particle mass input normalized to MeV."""

    particle: str
    symbol: str
    family: str
    mass_mev: float
    uncertainty_mev: float
    mass_type: str
    scheme: str | None
    scale: str | None
    source: str


@dataclass(frozen=True)
class ComplexityPenalty:
    """Reviewable complexity penalty ledger for one relation family."""

    parameter_count: float
    arbitrary_constants: float
    tuned_exponents: float
    structural_flexibility: float
    cross_family_mixing: float
    post_hoc_prediction: float
    total: float
    severity: str
    disqualifying_flags: tuple[str, ...]


@dataclass(frozen=True)
class RandomBaseline:
    """Deterministic log-uniform random triplet baseline summary."""

    seed: int
    sample_count: int
    mass_min_mev: float
    mass_max_mev: float
    mean_q: float
    std_q: float
    best_gap_to_target: float
    fraction_within_observed_gap: float
    observed_gap_percentile: float


@dataclass(frozen=True)
class FamilyEvaluation:
    """Evaluation of one guardrail-compliant particle family triplet."""

    family_id: str
    label: str
    particles: tuple[ParticleMassInput, ParticleMassInput, ParticleMassInput]
    q_value: float
    q_uncertainty: float
    target: float
    absolute_gap: float
    relative_gap: float
    gap_sigma: float | None
    within_uncertainty: bool
    analytic_range_fraction: float
    random_baseline: RandomBaseline
    verdict: str
    limitation: str


def koide_q(masses_mev: tuple[float, float, float] | list[float]) -> float:
    """Compute the standard real Koide Q value for three positive masses."""
    if len(masses_mev) != 3:
        raise ValueError("Koide Q requires exactly three masses.")
    if any(mass <= 0.0 for mass in masses_mev):
        raise ValueError("Koide Q requires positive masses.")
    numerator = sum(masses_mev)
    denominator = sum(math.sqrt(mass) for mass in masses_mev) ** 2
    return numerator / denominator


def koide_q_uncertainty(
    masses_mev: tuple[float, float, float],
    uncertainties_mev: tuple[float, float, float],
) -> float:
    """Propagate independent 1-sigma mass uncertainty into standard Koide Q."""
    sqrt_sum = sum(math.sqrt(mass) for mass in masses_mev)
    mass_sum = sum(masses_mev)
    variance = 0.0
    for mass, uncertainty in zip(masses_mev, uncertainties_mev):
        if uncertainty <= 0.0:
            continue
        derivative = (1.0 / (sqrt_sum**2)) - (mass_sum / (sqrt_sum**3 * math.sqrt(mass)))
        variance += (derivative * uncertainty) ** 2
    return math.sqrt(variance)


def analytic_q_range_fraction(gap: float) -> float:
    """Fraction of the analytic Q range within a +/- gap window around 2/3."""
    width = Q_RANGE_MAX - Q_RANGE_MIN
    return min(1.0, max(0.0, 2.0 * gap / width))


def standard_koide_complexity_penalty() -> ComplexityPenalty:
    """Return the fixed low-complexity ledger for the standard Koide relation."""
    total = 1.0
    return ComplexityPenalty(
        parameter_count=0.0,
        arbitrary_constants=0.0,
        tuned_exponents=0.0,
        structural_flexibility=total,
        cross_family_mixing=0.0,
        post_hoc_prediction=0.0,
        total=total,
        severity="low",
        disqualifying_flags=(),
    )


def random_log_uniform_baseline(
    *,
    mass_min_mev: float,
    mass_max_mev: float,
    observed_gap: float,
    seed: int,
    sample_count: int,
) -> RandomBaseline:
    """Sample random SM-scale triplets and compare their Q gaps to an observed gap."""
    if mass_min_mev <= 0.0 or mass_max_mev <= mass_min_mev:
        raise ValueError("Random baseline requires 0 < mass_min_mev < mass_max_mev.")
    if sample_count <= 0:
        raise ValueError("Random baseline requires a positive sample_count.")

    rng = np.random.default_rng(seed)
    log_min = math.log(mass_min_mev)
    log_max = math.log(mass_max_mev)
    samples = np.exp(rng.uniform(log_min, log_max, size=(sample_count, 3)))
    roots = np.sqrt(samples)
    q_values = np.sum(samples, axis=1) / np.square(np.sum(roots, axis=1))
    gaps = np.abs(q_values - KOIDE_TARGET)
    fraction_within = float(np.mean(gaps <= observed_gap))
    percentile = float(np.mean(gaps <= observed_gap) * 100.0)
    return RandomBaseline(
        seed=seed,
        sample_count=sample_count,
        mass_min_mev=mass_min_mev,
        mass_max_mev=mass_max_mev,
        mean_q=float(np.mean(q_values)),
        std_q=float(np.std(q_values)),
        best_gap_to_target=float(np.min(gaps)),
        fraction_within_observed_gap=fraction_within,
        observed_gap_percentile=percentile,
    )


def evaluate_family(
    *,
    family_id: str,
    label: str,
    particles: tuple[ParticleMassInput, ParticleMassInput, ParticleMassInput],
    mass_min_mev: float,
    mass_max_mev: float,
    baseline_seed: int,
    baseline_sample_count: int,
    limitation: str,
) -> FamilyEvaluation:
    """Evaluate the standard Koide relation for one family triplet."""
    masses = tuple(particle.mass_mev for particle in particles)
    uncertainties = tuple(particle.uncertainty_mev for particle in particles)
    q_value = koide_q(masses)
    q_uncertainty = koide_q_uncertainty(masses, uncertainties)
    absolute_gap = abs(q_value - KOIDE_TARGET)
    relative_gap = absolute_gap / KOIDE_TARGET
    gap_sigma = absolute_gap / q_uncertainty if q_uncertainty > 0.0 else None
    within_uncertainty = absolute_gap <= q_uncertainty if q_uncertainty > 0.0 else False
    if within_uncertainty:
        verdict = "VALID"
    elif q_uncertainty > 0.0:
        verdict = "INVALID"
    else:
        verdict = "INCONCLUSIVE"
    baseline = random_log_uniform_baseline(
        mass_min_mev=mass_min_mev,
        mass_max_mev=mass_max_mev,
        observed_gap=absolute_gap,
        seed=baseline_seed,
        sample_count=baseline_sample_count,
    )
    return FamilyEvaluation(
        family_id=family_id,
        label=label,
        particles=particles,
        q_value=q_value,
        q_uncertainty=q_uncertainty,
        target=KOIDE_TARGET,
        absolute_gap=absolute_gap,
        relative_gap=relative_gap,
        gap_sigma=gap_sigma,
        within_uncertainty=within_uncertainty,
        analytic_range_fraction=analytic_q_range_fraction(absolute_gap),
        random_baseline=baseline,
        verdict=verdict,
        limitation=limitation,
    )


def particle_input_from_mapping(entry: dict[str, Any]) -> ParticleMassInput:
    """Normalize a YAML particle entry into a typed mass input."""
    uncertainty = entry.get("uncertainty", {})
    if "value" in uncertainty:
        uncertainty_mev = float(uncertainty["value"])
    else:
        uncertainty_mev = max(
            float(uncertainty.get("plus", 0.0)),
            float(uncertainty.get("minus", 0.0)),
        )
    source = entry.get("source", {})
    return ParticleMassInput(
        particle=str(entry["particle"]),
        symbol=str(entry["symbol"]),
        family=str(entry["family"]),
        mass_mev=float(entry["mass_value_mev"]),
        uncertainty_mev=uncertainty_mev,
        mass_type=str(entry["mass_type"]),
        scheme=None if entry.get("scheme") is None else str(entry.get("scheme")),
        scale=None if entry.get("scale") is None else str(entry.get("scale")),
        source=str(source.get("citation", source.get("authority", "unknown"))),
    )

