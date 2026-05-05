"""Tests for ``physics_lab.engines.approximation_probes``."""

from __future__ import annotations

import math

import pytest

from physics_lab.engines.approximation_probes import (
    small_angle_pendulum_breakdown,
)


def test_small_angle_pendulum_breakdown_one_percent() -> None:
    rad, deg, threshold = small_angle_pendulum_breakdown(0.01)
    # Textbook small-angle approximation breaks at ~23 degrees for 1% error.
    assert 0.39 < rad < 0.41
    assert 22.0 < deg < 24.0
    assert threshold == 0.01


def test_small_angle_pendulum_breakdown_tighter_threshold_gives_smaller_angle() -> None:
    rad_1pct, _, _ = small_angle_pendulum_breakdown(0.01)
    rad_01pct, _, _ = small_angle_pendulum_breakdown(0.001)
    assert rad_01pct < rad_1pct


def test_small_angle_pendulum_breakdown_rejects_nonpositive_threshold() -> None:
    with pytest.raises(ValueError):
        small_angle_pendulum_breakdown(0.0)
    with pytest.raises(ValueError):
        small_angle_pendulum_breakdown(-0.01)


def test_small_angle_pendulum_breakdown_units_consistent() -> None:
    rad, deg, _ = small_angle_pendulum_breakdown(0.01)
    assert math.isclose(math.degrees(rad), deg, rel_tol=1e-9)
