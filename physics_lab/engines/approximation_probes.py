"""Deterministic probes that quantify where physics approximations break down.

Each function in this module compares a well-known approximation with an
exact (or higher-order) reference and returns the parameter value at which
the relative error first exceeds a stated threshold.

Usage example:

    from physics_lab.engines.approximation_probes import (
        small_angle_pendulum_breakdown,
    )
    breakdown_rad, breakdown_deg, threshold = small_angle_pendulum_breakdown()

No external API calls are made at runtime. All numerical inputs come from
``math`` / ``scipy.special`` which are bundled with the project.
"""

from __future__ import annotations

import math

from scipy.optimize import brentq
from scipy.special import ellipk


def small_angle_pendulum_breakdown(
    threshold: float = 0.01,
) -> tuple[float, float, float]:
    """Find amplitude where small-angle pendulum approximation fails.

    The exact period of a simple pendulum at amplitude ``theta_0`` is
    ``T(theta_0) = (4 / omega_0) * K(sin(theta_0 / 2))`` where ``K`` is the
    complete elliptic integral of the first kind and
    ``omega_0 = sqrt(g / L)``. The small-angle approximation gives
    ``T_approx = 2 * pi / omega_0`` (period independent of amplitude).

    The relative error is ``T(theta_0) / T_approx - 1 =
    (2 / pi) * K(sin(theta_0 / 2)) - 1``. This function returns the
    amplitude where this relative error first exceeds ``threshold``.

    Parameters
    ----------
    threshold:
        Maximum allowed relative period error (default 0.01 = 1%).

    Returns
    -------
    (breakdown_radians, breakdown_degrees, threshold_used)
    """
    if threshold <= 0:
        raise ValueError("threshold must be positive")

    def relative_error_minus_threshold(theta: float) -> float:
        k_squared = math.sin(theta / 2.0) ** 2
        return (2.0 / math.pi) * ellipk(k_squared) - 1.0 - threshold

    # err(0) = -threshold (negative); err(pi - eps) is large positive.
    breakdown_theta = brentq(
        relative_error_minus_threshold,
        1e-6,
        math.pi - 1e-3,
        xtol=1e-10,
    )
    return breakdown_theta, math.degrees(breakdown_theta), threshold
