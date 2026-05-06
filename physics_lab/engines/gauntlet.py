"""Deterministic candidate generator for the pendulum hypothesis gauntlet."""

from __future__ import annotations

import itertools
from typing import Sequence

import numpy as np

from physics_lab.engines.formula_discovery import CandidateModel
from physics_lab.engines.scoring import ModelScore


# Ten basis atoms ordered for deterministic enumeration.
ATOM_NAMES: list[str] = ["t2", "t4", "t6", "t8", "x1", "x2", "x3", "x4", "l1", "l2"]

ATOM_DISPLAY: dict[str, str] = {
    "t2": "theta^2",
    "t4": "theta^4",
    "t6": "theta^6",
    "t8": "theta^8",
    "x1": "x",
    "x2": "x^2",
    "x3": "x^3",
    "x4": "x^4",
    "l1": "x*log(1/(1-x))",
    "l2": "x^2*log(1/(1-x))",
}

ATOM_FAMILIES: dict[str, str] = {
    "t2": "theta_poly",
    "t4": "theta_poly",
    "t6": "theta_poly",
    "t8": "theta_poly",
    "x1": "x_poly",
    "x2": "x_poly",
    "x3": "x_poly",
    "x4": "x_poly",
    "l1": "log_enhanced",
    "l2": "log_enhanced",
}


def _x(theta: np.ndarray) -> np.ndarray:
    return np.sin(theta / 2.0) ** 2


def _l1(theta: np.ndarray) -> np.ndarray:
    x = _x(theta)
    return x * np.log(1.0 / np.clip(1.0 - x, 1.0e-12, None))


def _l2(theta: np.ndarray) -> np.ndarray:
    x = _x(theta)
    return x**2 * np.log(1.0 / np.clip(1.0 - x, 1.0e-12, None))


_ATOM_FEATURES: dict[str, object] = {
    "t2": lambda theta: theta**2,
    "t4": lambda theta: theta**4,
    "t6": lambda theta: theta**6,
    "t8": lambda theta: theta**8,
    "x1": _x,
    "x2": lambda theta: _x(theta) ** 2,
    "x3": lambda theta: _x(theta) ** 3,
    "x4": lambda theta: _x(theta) ** 4,
    "l1": _l1,
    "l2": _l2,
}


def _build_candidate(atoms: Sequence[str]) -> CandidateModel:
    atom_tuple = tuple(atoms)
    model_id = "model_" + "_".join(atom_tuple)
    coefficient_names = tuple(chr(ord("a") + i) for i in range(len(atom_tuple)))
    formula_parts = [
        f"{coef}*{ATOM_DISPLAY[atom]}"
        for coef, atom in zip(coefficient_names, atom_tuple)
    ]
    formula = "1 + " + " + ".join(formula_parts)

    def feature_builder(theta: np.ndarray, _atoms: tuple[str, ...] = atom_tuple) -> np.ndarray:
        columns = [_ATOM_FEATURES[a](theta) for a in _atoms]  # type: ignore[operator]
        return np.column_stack(columns).astype(float)

    return CandidateModel(
        model_id=model_id,
        formula=formula,
        coefficient_names=coefficient_names,
        feature_builder=feature_builder,
    )


def build_gauntlet_candidates() -> tuple[list[tuple[str, ...]], list[CandidateModel]]:
    """Return (atom_groups, models) for exactly 100 deterministic candidates.

    Candidates are organised in three tiers:
    - Tier 1 (size-1): 10 single-atom models
    - Tier 2 (size-2): 45 two-atom combinations — all C(10,2)
    - Tier 3 (size-3): 45 three-atom combinations — first C(10,3)[:45]

    Total: 100 candidates. The ordering is fixed and reproducible.
    """
    size1: list[tuple[str, ...]] = [(a,) for a in ATOM_NAMES]
    size2: list[tuple[str, ...]] = list(itertools.combinations(ATOM_NAMES, 2))
    size3: list[tuple[str, ...]] = list(itertools.combinations(ATOM_NAMES, 3))[:45]
    groups = size1 + size2 + size3
    assert len(groups) == 100, f"Expected 100 candidates, got {len(groups)}"
    models = [_build_candidate(atoms) for atoms in groups]
    return groups, models


def build_constrained_candidate() -> tuple[tuple[str, ...], CandidateModel]:
    """Return a physics-constrained candidate with c = 1/pi fixed.

    Formula: 1 + a*theta^2 + b*x^4 + (1/pi)*x*log(1/(1-x))
    The log coefficient is fixed to the theoretically correct asymptotic value
    derived from K(k^2) ~ ln(4/sqrt(1-k^2)) as k -> 1.
    Free parameters a, b are fitted by least squares.
    """
    import math

    fixed_c = 1.0 / math.pi
    atoms = ("t2", "x4")

    def feature_builder(theta: np.ndarray) -> np.ndarray:
        x = _x(theta)
        return np.column_stack([theta**2, x**4]).astype(float)

    def fixed_offset_fn(theta: np.ndarray) -> np.ndarray:
        return fixed_c * _l1(theta)

    model = CandidateModel(
        model_id="model_phys_constrained_l1",
        formula=f"1 + a*theta^2 + b*x^4 + (1/pi)*x*log(1/(1-x)) [c={fixed_c:.6f} fixed]",
        coefficient_names=("a", "b"),
        feature_builder=feature_builder,
        fixed_offset_fn=fixed_offset_fn,
    )
    return atoms, model


def classify_failure_mode(score: ModelScore) -> str:
    """Classify the primary failure mode for a gauntlet candidate.

    Based on test-set error only. The test range covers larger amplitudes than
    the train range, so train-test ratio is always high; that is expected physics
    behaviour, not statistical overfitting.
    """
    test_mean = score.test_metrics.mean_relative_error
    test_max = score.test_metrics.max_relative_error

    if test_mean > 0.05:
        return "high_error"
    if test_max > 0.0 and test_mean > 0.0 and test_max / test_mean >= 10.0:
        return "max_error_dominated"
    if test_mean > 0.005:
        return "moderate_error"
    return "none"


def atom_family(atoms: Sequence[str]) -> str:
    """Classify a candidate's feature family based on which atom groups are present."""
    atom_set = set(atoms)
    theta_atoms = {"t2", "t4", "t6", "t8"}
    x_atoms = {"x1", "x2", "x3", "x4"}
    log_atoms = {"l1", "l2"}

    has_theta = bool(atom_set & theta_atoms)
    has_x = bool(atom_set & x_atoms)
    has_log = bool(atom_set & log_atoms)

    if has_log and has_theta:
        return "mixed"
    if has_log:
        return "log_enhanced"
    if has_theta and has_x:
        return "cross_domain"
    if has_theta:
        return "theta_poly"
    return "x_poly"
