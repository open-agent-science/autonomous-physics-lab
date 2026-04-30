"""Deterministic damped oscillator helpers for the next benchmark."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class DampedOscillatorParameters:
    """Physical parameters for the damped harmonic oscillator."""

    mass: float
    damping: float
    stiffness: float
    x0: float
    v0: float

    @property
    def natural_frequency(self) -> float:
        return float(np.sqrt(self.stiffness / self.mass))

    @property
    def damping_ratio(self) -> float:
        return float(self.damping / (2.0 * np.sqrt(self.mass * self.stiffness)))

    @property
    def alpha(self) -> float:
        return float(self.damping / (2.0 * self.mass))


@dataclass(frozen=True)
class DampedOscillatorDataset:
    """Reference data for damped oscillator verification experiments."""

    time_seconds: np.ndarray
    displacement: np.ndarray
    velocity: np.ndarray
    energy: np.ndarray
    regime: str


def classify_damping_regime(parameters: DampedOscillatorParameters) -> str:
    """Return the canonical damping regime label."""
    ratio = parameters.damping_ratio
    if np.isclose(ratio, 1.0, atol=1.0e-9):
        return "critical"
    if ratio < 1.0:
        return "underdamped"
    return "overdamped"


def exact_damped_oscillator_solution(
    time_seconds: np.ndarray,
    parameters: DampedOscillatorParameters,
) -> tuple[np.ndarray, np.ndarray]:
    """Return displacement and velocity for the exact damped oscillator."""
    t = np.asarray(time_seconds, dtype=float)
    regime = classify_damping_regime(parameters)
    alpha = parameters.alpha
    x0 = parameters.x0
    v0 = parameters.v0

    if regime == "underdamped":
        omega_d = float(np.sqrt(parameters.natural_frequency**2 - alpha**2))
        c1 = x0
        c2 = (v0 + alpha * x0) / omega_d
        exp_term = np.exp(-alpha * t)
        cos_term = np.cos(omega_d * t)
        sin_term = np.sin(omega_d * t)
        displacement = exp_term * (c1 * cos_term + c2 * sin_term)
        velocity = exp_term * (
            -alpha * (c1 * cos_term + c2 * sin_term)
            + (-c1 * omega_d * sin_term + c2 * omega_d * cos_term)
        )
        return displacement, velocity

    if regime == "critical":
        c1 = x0
        c2 = v0 + alpha * x0
        exp_term = np.exp(-alpha * t)
        displacement = exp_term * (c1 + c2 * t)
        velocity = exp_term * (c2 - alpha * (c1 + c2 * t))
        return displacement, velocity

    radical = float(np.sqrt(alpha**2 - parameters.natural_frequency**2))
    r1 = -alpha + radical
    r2 = -alpha - radical
    c1 = (v0 - r2 * x0) / (r1 - r2)
    c2 = x0 - c1
    exp_r1 = np.exp(r1 * t)
    exp_r2 = np.exp(r2 * t)
    displacement = c1 * exp_r1 + c2 * exp_r2
    velocity = c1 * r1 * exp_r1 + c2 * r2 * exp_r2
    return displacement, velocity


def generate_damped_oscillator_dataset(
    time_start: float,
    time_end: float,
    sample_count: int,
    parameters: DampedOscillatorParameters,
) -> DampedOscillatorDataset:
    """Generate an exact damped-oscillator dataset across a time interval."""
    if sample_count < 3:
        raise ValueError("sample_count must be at least 3")
    if time_start < 0.0:
        raise ValueError("time_start must be non-negative")
    if time_end <= time_start:
        raise ValueError("time_end must be greater than time_start")
    if parameters.mass <= 0.0:
        raise ValueError("mass must be positive")
    if parameters.stiffness <= 0.0:
        raise ValueError("stiffness must be positive")
    if parameters.damping < 0.0:
        raise ValueError("damping must be non-negative")

    time_seconds = np.linspace(time_start, time_end, sample_count)
    displacement, velocity = exact_damped_oscillator_solution(time_seconds, parameters)
    energy = 0.5 * parameters.mass * velocity**2 + 0.5 * parameters.stiffness * displacement**2
    return DampedOscillatorDataset(
        time_seconds=time_seconds,
        displacement=displacement,
        velocity=velocity,
        energy=energy,
        regime=classify_damping_regime(parameters),
    )
