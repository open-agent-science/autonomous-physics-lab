"""Deterministic verification of derived physical constants.

Each function in this module reproduces one published physical constant
from a small set of base constants taken from ``scipy.constants`` (which
shadows CODATA values). Functions return a tuple of
``(computed_value, reference_value, relative_error)``.

Usage example:

    from physics_lab.engines.constants_verifier import fine_structure_constant
    computed, reference, rel_err = fine_structure_constant()

No external API calls are made at runtime. All input values are pulled
from ``scipy.constants`` which is bundled with SciPy and pinned via the
project's dependency requirements.
"""

from __future__ import annotations

from math import pi

from scipy import constants


def _relative_error(computed: float, reference: float) -> float:
    """Return ``|computed - reference| / |reference|``."""
    return abs(computed - reference) / abs(reference)


def fine_structure_constant() -> tuple[float, float, float]:
    """Verify alpha = e^2 / (4*pi*epsilon_0*hbar*c).

    Returns
    -------
    (computed, reference, relative_error)
    """
    computed = constants.e**2 / (
        4 * pi * constants.epsilon_0 * constants.hbar * constants.c
    )
    reference = constants.alpha
    return computed, reference, _relative_error(computed, reference)
