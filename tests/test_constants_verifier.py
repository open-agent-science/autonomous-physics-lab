"""Tests for ``physics_lab.engines.constants_verifier``."""

from __future__ import annotations

from physics_lab.engines.constants_verifier import fine_structure_constant


def test_fine_structure_constant_within_tolerance() -> None:
    computed, reference, rel_err = fine_structure_constant()
    assert rel_err < 1e-9
    assert abs(computed - reference) < 1e-12 * abs(reference)


def test_fine_structure_constant_returns_finite_values() -> None:
    computed, reference, rel_err = fine_structure_constant()
    assert computed > 0
    assert reference > 0
    assert rel_err >= 0
