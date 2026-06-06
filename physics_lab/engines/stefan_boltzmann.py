"""Deterministic Stefan-Boltzmann exact-reference fixture checks.

This module verifies APL's software gates against synthetic SI rows. It does
not ingest empirical emitters or assess the physical law outside the declared
exact-reference fixture.
"""

from __future__ import annotations

import math
from typing import Any

from physics_lab.engines.dimensions import validate_item


STEFAN_BOLTZMANN_CONSTANT_W_M2_K4 = 5.670374419e-8


def sphere_area_m2(radius_m: float) -> float:
    """Return the surface area of a sphere with a positive SI radius."""

    if radius_m <= 0.0:
        raise ValueError("radius_m must be positive")
    return 4.0 * math.pi * radius_m**2


def radiated_power_w(
    area_m2: float,
    temperature_k: float,
    *,
    sigma_w_m2_k4: float = STEFAN_BOLTZMANN_CONSTANT_W_M2_K4,
    temperature_exponent: float = 4.0,
) -> float:
    """Return ``sigma * area * temperature**exponent`` in SI units."""

    if area_m2 <= 0.0:
        raise ValueError("area_m2 must be positive")
    if temperature_k <= 0.0:
        raise ValueError("temperature_k must be positive")
    if sigma_w_m2_k4 <= 0.0:
        raise ValueError("sigma_w_m2_k4 must be positive")
    return sigma_w_m2_k4 * area_m2 * temperature_k**temperature_exponent


def spherical_luminosity_w(radius_m: float, temperature_k: float) -> float:
    """Return the frozen-baseline luminosity for a synthetic sphere."""

    return radiated_power_w(sphere_area_m2(radius_m), temperature_k)


def generate_exact_reference_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate deterministic synthetic sphere rows from a fixture config."""

    constant = float(config["constant"]["value_w_m2_k4"])
    radii_m = [float(value) for value in config["grid"]["radii_m"]]
    temperatures_k = [float(value) for value in config["grid"]["temperatures_K"]]
    rows: list[dict[str, Any]] = []
    for radius_index, radius_m in enumerate(radii_m):
        for temperature_index, temperature_k in enumerate(temperatures_k):
            area_m2 = sphere_area_m2(radius_m)
            rows.append(
                {
                    "row_id": f"SB-SYN-R{radius_index + 1:02d}-T{temperature_index + 1:02d}",
                    "route": "synthetic_blackbody",
                    "split": (
                        "holdout"
                        if (radius_index + temperature_index) % 2
                        else "reference"
                    ),
                    "radius_m": radius_m,
                    "area_m2": area_m2,
                    "temperature_K": temperature_k,
                    "luminosity_expected_W": radiated_power_w(
                        area_m2,
                        temperature_k,
                        sigma_w_m2_k4=constant,
                    ),
                    "luminosity_provenance_class": "exact_fixture",
                }
            )
    return rows


def _relative_error(actual: float, expected: float) -> float:
    return abs(actual - expected) / abs(expected)


def _max_relative_error(actual: list[float], expected: list[float]) -> float:
    return max(
        (_relative_error(actual_value, expected_value) for actual_value, expected_value in zip(actual, expected)),
        default=0.0,
    )


def _dimensional_gate() -> dict[str, Any]:
    result = validate_item(
        {
            "id": "SB-DIM-001",
            "formula": "P = sigma * A * T**4",
            "variables": {
                "P": "W",
                "sigma": "kg s^-3 K^-4",
                "A": "m^2",
                "T": "K",
            },
            "expected_verdict": "VALID",
        }
    )
    return {
        "status": "PASS" if result.computed_verdict == "VALID" else "FAIL",
        "computed_verdict": result.computed_verdict,
        "detail": result.detail,
    }


def _promotion_boundary(config: dict[str, Any]) -> dict[str, Any]:
    """Echo the fixture's declared promotion boundary.

    The boundary is read from the fixture manifest so a maintainer-reviewed
    route change (for example, sandbox-only -> scoped software-result packaging
    for a canonical experiment/hypothesis identity) flows through the runner and
    its report. ``empirical_audit_performed`` is always ``False`` because this
    engine never ingests empirical emitter rows.
    """

    declared = config.get("promotion_boundary")
    declared = declared if isinstance(declared, dict) else {}
    return {
        "sandbox_only": bool(declared.get("sandbox_only", True)),
        "writes_canonical_result": bool(declared.get("writes_canonical_result", False)),
        "claim_promotion_allowed": bool(declared.get("claim_promotion_allowed", False)),
        "empirical_audit_performed": False,
    }


def audit_exact_reference_fixture(config: dict[str, Any]) -> dict[str, Any]:
    """Run software-only gates against a deterministic synthetic fixture."""

    rows = generate_exact_reference_rows(config)
    tolerance = float(config["tolerances"]["relative_error"])
    wrong_exponent = float(config["negative_controls"]["wrong_temperature_exponent"])
    wrong_area_multiplier = float(
        config["negative_controls"]["wrong_spherical_area_multiplier"]
    )

    expected = [float(row["luminosity_expected_W"]) for row in rows]
    baseline = [
        spherical_luminosity_w(float(row["radius_m"]), float(row["temperature_K"]))
        for row in rows
    ]
    wrong_exponent_values = [
        radiated_power_w(
            float(row["area_m2"]),
            float(row["temperature_K"]),
            temperature_exponent=wrong_exponent,
        )
        for row in rows
    ]
    wrong_area_values = [
        radiated_power_w(
            wrong_area_multiplier * math.pi * float(row["radius_m"]) ** 2,
            float(row["temperature_K"]),
        )
        for row in rows
    ]

    radii = sorted({float(row["radius_m"]) for row in rows})
    temperatures = sorted({float(row["temperature_K"]) for row in rows})
    temperature_ratios = [
        spherical_luminosity_w(radius_m, temperatures[-1])
        / spherical_luminosity_w(radius_m, temperatures[0])
        for radius_m in radii
    ]
    expected_temperature_ratio = (temperatures[-1] / temperatures[0]) ** 4
    radius_ratios = [
        spherical_luminosity_w(radii[-1], temperature_k)
        / spherical_luminosity_w(radii[0], temperature_k)
        for temperature_k in temperatures
    ]
    expected_radius_ratio = (radii[-1] / radii[0]) ** 2
    temperature_scaling_error = max(
        (_relative_error(value, expected_temperature_ratio) for value in temperature_ratios),
        default=0.0,
    )
    radius_scaling_error = max(
        (_relative_error(value, expected_radius_ratio) for value in radius_ratios),
        default=0.0,
    )
    monotonic_temperature = all(
        spherical_luminosity_w(radius_m, low) < spherical_luminosity_w(radius_m, high)
        for radius_m in radii
        for low, high in zip(temperatures, temperatures[1:])
    )
    monotonic_radius = all(
        spherical_luminosity_w(low, temperature_k) < spherical_luminosity_w(high, temperature_k)
        for temperature_k in temperatures
        for low, high in zip(radii, radii[1:])
    )

    exact_reference_error = _max_relative_error(baseline, expected)
    wrong_exponent_error = _max_relative_error(wrong_exponent_values, expected)
    wrong_area_error = _max_relative_error(wrong_area_values, expected)
    gates = {
        "dimensional_consistency": _dimensional_gate(),
        "constant_convention": {
            "status": (
                "PASS"
                if float(config["constant"]["value_w_m2_k4"])
                == STEFAN_BOLTZMANN_CONSTANT_W_M2_K4
                else "FAIL"
            ),
            "expected_value_w_m2_k4": STEFAN_BOLTZMANN_CONSTANT_W_M2_K4,
        },
        "exact_reference": {
            "status": "PASS" if exact_reference_error <= tolerance else "FAIL",
            "max_relative_error": exact_reference_error,
        },
        "temperature_t4_scaling": {
            "status": "PASS" if temperature_scaling_error <= tolerance else "FAIL",
            "max_relative_error": temperature_scaling_error,
        },
        "radius_r2_area_scaling": {
            "status": "PASS" if radius_scaling_error <= tolerance else "FAIL",
            "max_relative_error": radius_scaling_error,
        },
        "monotonicity": {
            "status": "PASS" if monotonic_temperature and monotonic_radius else "FAIL",
            "temperature_increases_power": monotonic_temperature,
            "radius_increases_power": monotonic_radius,
        },
        "wrong_temperature_exponent_control": {
            "status": "PASS" if wrong_exponent_error > tolerance else "FAIL",
            "control_rejected": wrong_exponent_error > tolerance,
            "max_relative_error": wrong_exponent_error,
        },
        "wrong_area_control": {
            "status": "PASS" if wrong_area_error > tolerance else "FAIL",
            "control_rejected": wrong_area_error > tolerance,
            "max_relative_error": wrong_area_error,
        },
    }
    all_pass = all(gate["status"] == "PASS" for gate in gates.values())
    return {
        "task_id": str(config["task_id"]),
        "fixture_id": str(config["fixture_id"]),
        "verdict": "VALID_IN_RANGE" if all_pass else "INCONCLUSIVE",
        "scope": {
            "route": "synthetic_blackbody_exact_reference",
            "software_fixture_only": True,
            "radius_range_m": [radii[0], radii[-1]],
            "temperature_range_K": [temperatures[0], temperatures[-1]],
            "row_count": len(rows),
            "reference_row_count": sum(row["split"] == "reference" for row in rows),
            "holdout_row_count": sum(row["split"] == "holdout" for row in rows),
        },
        "constant": {
            "value_w_m2_k4": STEFAN_BOLTZMANN_CONSTANT_W_M2_K4,
            "source_convention": str(config["constant"]["source_convention"]),
        },
        "gates": gates,
        "rows": rows,
        "promotion_boundary": _promotion_boundary(config),
        "limitations": [
            "Synthetic exact-reference fixture only; no empirical emitter rows were ingested.",
            "Passing gates verifies software behavior and the frozen SI convention only.",
            "No universal Stefan-Boltzmann-law validation or falsification is authorized.",
        ],
    }
