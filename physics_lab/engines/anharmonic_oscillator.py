"""Deterministic anharmonic-oscillator period helpers."""

from __future__ import annotations

from dataclasses import dataclass

import math

import numpy as np
from scipy.integrate import quad


@dataclass(frozen=True)
class AnharmonicOscillatorParameters:
    """Physical parameters for the quartic anharmonic oscillator."""

    mass: float
    stiffness: float
    quartic_coefficient: float

    def validate(self) -> None:
        if self.mass <= 0.0:
            raise ValueError("mass must be positive")
        if self.stiffness <= 0.0:
            raise ValueError("stiffness must be positive")
        if self.quartic_coefficient < 0.0:
            raise ValueError("quartic_coefficient must be non-negative")

    @property
    def harmonic_period(self) -> float:
        return float(2.0 * math.pi * math.sqrt(self.mass / self.stiffness))


@dataclass(frozen=True)
class AnharmonicSample:
    """One amplitude-dependent period sample for the benchmark."""

    amplitude: float
    quartic_coefficient: float
    anharmonicity_ratio: float
    reference_period: float


def anharmonicity_ratio(parameters: AnharmonicOscillatorParameters, amplitude: float) -> float:
    """Return the dimensionless perturbative control parameter lambda*A^2/k."""
    parameters.validate()
    if amplitude <= 0.0:
        raise ValueError("amplitude must be positive")
    return float(parameters.quartic_coefficient * amplitude * amplitude / parameters.stiffness)


def reference_period(parameters: AnharmonicOscillatorParameters, amplitude: float) -> float:
    """Return the reference period from the conservative energy integral.

    For V(x) = 1/2 k x^2 + lambda x^4 and turning point amplitude A, the
    quarter-period integral becomes numerically stable under x = A sin(theta):

        T = 4 * sqrt(m/2) * integral_0^(pi/2)
                dtheta / sqrt(0.5*k + lambda*A^2*(1 + sin(theta)^2))
    """
    parameters.validate()
    if amplitude <= 0.0:
        raise ValueError("amplitude must be positive")

    def _integrand(theta: float) -> float:
        denom = 0.5 * parameters.stiffness + parameters.quartic_coefficient * amplitude * amplitude * (
            1.0 + math.sin(theta) ** 2
        )
        return 1.0 / math.sqrt(denom)

    integral, _ = quad(_integrand, 0.0, math.pi / 2.0, epsabs=1.0e-12, epsrel=1.0e-12, limit=400)
    return float(4.0 * math.sqrt(parameters.mass / 2.0) * integral)


def perturbative_period(parameters: AnharmonicOscillatorParameters, amplitude: float) -> float:
    """Return the leading-order perturbative period approximation.

    For the equation of motion m*x'' + k*x + 4*lambda*x^3 = 0, the leading
    Duffing frequency shift is Omega ~= Omega0 * (1 + 3/2 * epsilon), where
    epsilon = lambda*A^2/k. Inverting to first order gives
    T ~= T0 * (1 - 3/2 * epsilon).
    """
    epsilon = anharmonicity_ratio(parameters, amplitude)
    return float(parameters.harmonic_period * (1.0 - 1.5 * epsilon))


def harmonic_period_prediction(parameters: AnharmonicOscillatorParameters, amplitude: float) -> float:
    """Return the purely harmonic baseline."""
    _ = amplitude
    parameters.validate()
    return parameters.harmonic_period


def generate_reference_samples(
    *,
    mass: float,
    stiffness: float,
    amplitudes: np.ndarray,
    quartic_coefficients: np.ndarray,
) -> list[AnharmonicSample]:
    """Generate a deterministic sample grid for the benchmark."""
    amplitudes = np.asarray(amplitudes, dtype=float)
    quartic_coefficients = np.asarray(quartic_coefficients, dtype=float)
    if amplitudes.ndim != 1 or quartic_coefficients.ndim != 1:
        raise ValueError("amplitudes and quartic_coefficients must be 1D arrays")

    samples: list[AnharmonicSample] = []
    for quartic_coefficient in quartic_coefficients:
        params = AnharmonicOscillatorParameters(
            mass=mass,
            stiffness=stiffness,
            quartic_coefficient=float(quartic_coefficient),
        )
        params.validate()
        for amplitude in amplitudes:
            amplitude_value = float(amplitude)
            ratio = anharmonicity_ratio(params, amplitude_value)
            samples.append(
                AnharmonicSample(
                    amplitude=amplitude_value,
                    quartic_coefficient=float(quartic_coefficient),
                    anharmonicity_ratio=ratio,
                    reference_period=reference_period(params, amplitude_value),
                )
            )
    samples.sort(key=lambda sample: (sample.anharmonicity_ratio, sample.quartic_coefficient, sample.amplitude))
    return samples


def fit_empirical_quadratic_ratio(samples: list[AnharmonicSample], *, mass: float, stiffness: float) -> dict[str, float]:
    """Fit T/T0 = 1 + a*epsilon + b*epsilon^2 on a training slice."""
    if not samples:
        raise ValueError("at least one sample is required to fit the empirical quadratic ratio")
    baseline_period = float(2.0 * math.pi * math.sqrt(mass / stiffness))
    x = np.asarray([sample.anharmonicity_ratio for sample in samples], dtype=float)
    y = np.asarray([(sample.reference_period / baseline_period) - 1.0 for sample in samples], dtype=float)
    design = np.column_stack([x, x**2])
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
    return {"a": float(coefficients[0]), "b": float(coefficients[1])}


def empirical_quadratic_period(
    parameters: AnharmonicOscillatorParameters,
    amplitude: float,
    coefficients: dict[str, float],
) -> float:
    """Evaluate the fitted quadratic ratio model."""
    epsilon = anharmonicity_ratio(parameters, amplitude)
    a = float(coefficients.get("a", 0.0))
    b = float(coefficients.get("b", 0.0))
    return float(parameters.harmonic_period * (1.0 + a * epsilon + b * epsilon * epsilon))
