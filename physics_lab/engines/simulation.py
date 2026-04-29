"""Deterministic simulators for physics benchmark workflows."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import ellipk


@dataclass(frozen=True)
class PendulumDataset:
    """Reference data for pendulum period ratio experiments."""

    theta: np.ndarray
    period_ratio: np.ndarray


def exact_pendulum_period_ratio(theta_radians: np.ndarray) -> np.ndarray:
    """Return the exact pendulum period ratio T/T0 for amplitudes in radians."""
    theta = np.asarray(theta_radians, dtype=float)
    k_squared = np.sin(theta / 2.0) ** 2
    return (2.0 / np.pi) * ellipk(k_squared)


def generate_pendulum_dataset(
    amplitude_start: float,
    amplitude_end: float,
    sample_count: int,
) -> PendulumDataset:
    """Generate exact pendulum period ratio data across an amplitude range."""
    if sample_count < 3:
        raise ValueError("sample_count must be at least 3")
    if amplitude_start <= 0.0:
        raise ValueError("amplitude_start must be positive")
    if amplitude_end <= amplitude_start:
        raise ValueError("amplitude_end must be greater than amplitude_start")

    theta = np.linspace(amplitude_start, amplitude_end, sample_count)
    period_ratio = exact_pendulum_period_ratio(theta)
    return PendulumDataset(theta=theta, period_ratio=period_ratio)
