"""Deterministic Special Relativity light-clock consistency checks."""

from __future__ import annotations

import math
from typing import Any

ENGINE_VERSION = "1.0.0"
SPEED_OF_LIGHT_M_S = 299_792_458.0
VALID_BETAS = (0.0, 0.1, 0.5, 0.9, 0.99)
INVALID_BETAS = (1.0, 1.01)
LC_001_002_REL_TOL = 1.0e-9
LC_003_REL_TOL = 1.0e-12
LC_004_ABS_TOL = 1.0e-9


def lorentz_factor(beta: float) -> float:
    """Return gamma for a physical, non-negative subluminal beta."""
    if beta < 0.0 or beta >= 1.0:
        raise ValueError("beta must satisfy 0 <= beta < 1")
    return 1.0 / math.sqrt(1.0 - beta * beta)


def _relative_error(observed: float, expected: float) -> float:
    if expected == 0.0:
        return abs(observed - expected)
    return abs(observed - expected) / abs(expected)


def _numeric_check(
    check_id: str,
    observed: float,
    expected: float,
    tolerance: float,
    *,
    mode: str = "relative",
) -> dict[str, Any]:
    error = (
        _relative_error(observed, expected)
        if mode == "relative"
        else abs(observed - expected)
    )
    return {
        "id": check_id,
        "status": "PASS" if error <= tolerance else "FAIL",
        "observed": observed,
        "expected": expected,
        "error": error,
        "tolerance": tolerance,
        "tolerance_mode": mode,
    }


def evaluate_light_clock(
    beta: float,
    *,
    mirror_separation_m: float = 1.0,
    speed_of_light_m_s: float = SPEED_OF_LIGHT_M_S,
    candidate: str = "lorentz",
) -> dict[str, Any]:
    """Evaluate LC-001, LC-002, LC-003, and LC-005 for one beta."""
    if mirror_separation_m <= 0.0:
        raise ValueError("mirror_separation_m must be positive")
    if speed_of_light_m_s <= 0.0:
        raise ValueError("speed_of_light_m_s must be positive")
    if beta < 0.0 or beta >= 1.0:
        return {
            "beta": beta,
            "candidate": candidate,
            "verdict": "UNDEFINED",
            "reason": "Light-clock benchmark requires 0 <= v/c < 1.",
            "checks": [],
        }

    gamma = lorentz_factor(beta)
    velocity_m_s = beta * speed_of_light_m_s
    rest_period_s = 2.0 * mirror_separation_m / speed_of_light_m_s
    if candidate == "lorentz":
        moving_period_s = rest_period_s * gamma
    elif candidate == "newtonian":
        moving_period_s = rest_period_s
    else:
        raise ValueError(f"Unknown light-clock candidate: {candidate}")

    diagonal_path_m = 2.0 * math.sqrt(
        mirror_separation_m**2 + (velocity_m_s * moving_period_s / 2.0) ** 2
    )
    observed_light_speed_m_s = diagonal_path_m / moving_period_s
    period_ratio = moving_period_s / rest_period_s
    path_ratio = diagonal_path_m / (2.0 * mirror_separation_m)

    checks = [
        _numeric_check(
            "LC-001", period_ratio, gamma, LC_001_002_REL_TOL
        ),
        _numeric_check("LC-002", path_ratio, gamma, LC_001_002_REL_TOL),
        _numeric_check(
            "LC-003",
            observed_light_speed_m_s,
            speed_of_light_m_s,
            LC_003_REL_TOL,
        ),
        {
            "id": "LC-005",
            "status": "PASS" if moving_period_s >= rest_period_s else "FAIL",
            "observed": moving_period_s >= rest_period_s,
            "expected": True,
        },
    ]
    verdict = "CONSISTENT" if all(c["status"] == "PASS" for c in checks) else "INCONSISTENT"
    return {
        "beta": beta,
        "candidate": candidate,
        "gamma": gamma,
        "rest_period_s": rest_period_s,
        "moving_period_s": moving_period_s,
        "diagonal_path_m": diagonal_path_m,
        "observed_light_speed_m_s": observed_light_speed_m_s,
        "checks": checks,
        "verdict": verdict,
    }


def run_light_clock_benchmark() -> dict[str, Any]:
    """Run the frozen beta sweep and the declared Newtonian control."""
    valid_cases = [evaluate_light_clock(beta) for beta in VALID_BETAS]
    undefined_cases = [evaluate_light_clock(beta) for beta in INVALID_BETAS]
    newtonian_control = evaluate_light_clock(0.5, candidate="newtonian")
    low_velocity_check = _numeric_check(
        "LC-004", lorentz_factor(0.0), 1.0, LC_004_ABS_TOL, mode="absolute"
    )

    numeric_checks = [
        check
        for case in valid_cases
        for check in case["checks"]
        if "error" in check
    ]
    check_max_errors = {
        check_id: max(
            check["error"] for check in numeric_checks if check["id"] == check_id
        )
        for check_id in ("LC-001", "LC-002", "LC-003")
    }
    wrong_lc001 = next(
        check for check in newtonian_control["checks"] if check["id"] == "LC-001"
    )
    all_pass = (
        all(case["verdict"] == "CONSISTENT" for case in valid_cases)
        and all(case["verdict"] == "UNDEFINED" for case in undefined_cases)
        and low_velocity_check["status"] == "PASS"
        and newtonian_control["verdict"] == "INCONSISTENT"
        and wrong_lc001["status"] == "FAIL"
    )

    return {
        "engine_version": ENGINE_VERSION,
        "scenario": "TE-001-light-clock",
        "assumptions": [
            "Inertial transverse light clock in flat spacetime.",
            "Mirror separation is the proper transverse length and remains fixed.",
            "Light propagates at the exact configured speed c in inertial frames.",
            "Acceleration, gravity, diffraction, and finite mirror effects are excluded.",
        ],
        "reference_equations": {
            "rest_period": "T_rest = 2 L / c",
            "lorentz_factor": "gamma = 1 / sqrt(1 - beta^2)",
            "moving_period": "T_moving = gamma T_rest",
            "diagonal_path": "d/2 = sqrt(L^2 + (v T_moving / 2)^2)",
        },
        "tolerances": {
            "LC-001_relative": LC_001_002_REL_TOL,
            "LC-002_relative": LC_001_002_REL_TOL,
            "LC-003_relative": LC_003_REL_TOL,
            "LC-004_absolute": LC_004_ABS_TOL,
        },
        "valid_beta_sweep": valid_cases,
        "undefined_beta_cases": undefined_cases,
        "low_velocity_check": low_velocity_check,
        "wrong_candidate_control": newtonian_control,
        "summary": {
            "valid_case_count": len(valid_cases),
            "consistent_case_count": sum(
                case["verdict"] == "CONSISTENT" for case in valid_cases
            ),
            "undefined_case_count": sum(
                case["verdict"] == "UNDEFINED" for case in undefined_cases
            ),
            "check_max_errors": check_max_errors,
            "newtonian_lc001_status": wrong_lc001["status"],
        },
        "verdict": "CONSISTENT" if all_pass else "INCONSISTENT",
        "limitations": [
            "This validates APL's implementation of the named SR thought experiment, not SR empirically.",
            "Only TE-001 and the declared beta sweep are in scope.",
            "General Relativity, acceleration, longitudinal clocks, and other thought experiments are excluded.",
            "No claim, knowledge, or discovery promotion is authorized.",
        ],
    }
