"""Deterministic FIRAS Wien-peak consistency metric (Textbook Formula Audit).

This engine performs ONE bounded, deterministic spectral-domain consistency
check: it compares the wavelength-domain peak of the pinned COBE/FIRAS absolute
monopole spectrum against the frozen textbook Wien-displacement reference
``lambda_peak = b / T`` at a separately pinned reference temperature.

It does NOT fit a blackbody spectrum, does NOT re-pin or re-fetch the source,
does NOT choose a temperature, and introduces NO fitted free parameters. The
local parabolic-vertex refinement is a fixed, deterministic interpolation of the
already-located raw-bin peak (a sampling-resolution diagnostic), not a model fit.

The central physics point is the wavelength-vs-frequency DOMAIN CONVERSION: the
FIRAS product is tabulated on a native wavenumber/frequency axis (``B_nu`` vs
``cm^-1``), so the Jacobian ``B_lambda = B_nu * nu^2 / c`` must be applied before
locating a wavelength-domain peak. A bare axis relabel (no Jacobian) is a
predeclared negative control that must produce the wrong peak.

Verdict vocabulary is fixed by the TASK-0793 / TASK-0815 contract:
``CONSISTENT_IN_SCOPE``, ``DOMAIN_CONVERSION_MISMATCH``,
``INCONCLUSIVE_PRODUCT_SEMANTICS``, ``INCONCLUSIVE_SAMPLING_RESOLUTION``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


# Frozen physical constants (no fitting; SI internally).
SPEED_OF_LIGHT_M_S = 299_792_458.0  # exact, SI definition
WIEN_WAVELENGTH_DISPLACEMENT_M_K = 0.002897771955  # CODATA 2022, NIST (m*K)

# Pinned reference temperature from the TASK-0815 domain contract
# (Fixsen 2009, ApJ 707, 916; literature-combined value). Provenance only,
# NOT a fitted parameter chosen from the FIRAS rows.
REFERENCE_TEMPERATURE_K = 2.72548
REFERENCE_TEMPERATURE_SIGMA_K = 0.00057
REFERENCE_TEMPERATURE_CITATION = "Fixsen 2009, ApJ 707, 916"

# Predeclared decision tolerances (fixed BEFORE running; not tuned to output).
# The raw-bin peak is limited by the ~0.45 cm^-1 FIRAS bin spacing, so the
# raw-bin gate is loose and the interpolation gate is tight.
RAW_BIN_RELATIVE_TOLERANCE = 0.02
INTERPOLATED_RELATIVE_TOLERANCE = 0.005
# A no-Jacobian relabel or wrong temperature must miss by clearly more than this.
CONTROL_MIN_RELATIVE_MISS = 0.05

ADMISSIBLE_VERDICTS = (
    "CONSISTENT_IN_SCOPE",
    "DOMAIN_CONVERSION_MISMATCH",
    "INCONCLUSIVE_PRODUCT_SEMANTICS",
    "INCONCLUSIVE_SAMPLING_RESOLUTION",
)


@dataclass(frozen=True)
class SpectralPoint:
    """One FIRAS row mapped onto SI spectral quantities (read-only)."""

    row_id: str
    wavenumber_cm_inverse: float
    wavenumber_m_inverse: float
    frequency_hz: float
    wavelength_m: float
    b_nu_mjy_sr: float
    b_lambda_arbitrary: float


def reference_wavelength_peak_m(
    temperature_k: float = REFERENCE_TEMPERATURE_K,
    constant_m_k: float = WIEN_WAVELENGTH_DISPLACEMENT_M_K,
) -> float:
    """Return the textbook wavelength-domain Wien peak ``b / T`` in metres."""
    if temperature_k <= 0:
        raise ValueError("temperature_k must be positive Kelvin")
    return constant_m_k / temperature_k


def load_firas_rows(path: str | Path) -> dict[str, Any]:
    """Load the pinned FIRAS monopole rows YAML (read-only)."""
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict) or "rows" not in data:
        raise ValueError("FIRAS rows file must be a mapping containing 'rows'")
    return data


def _is_absolute_product(dataset: dict[str, Any]) -> bool:
    """Gate 1: confirm the committed product is an absolute monopole spectrum.

    Fails (returns ``False``) only if the rows are tagged as residual-only or
    model-normalized rather than absolute spectral radiance.
    """
    rows = dataset["rows"]
    if not rows:
        return False
    semantics = dataset.get("column_semantics", {})
    intensity_doc = str(semantics.get("monopole_intensity_mjy_sr", "")).lower()
    if "residual" in intensity_doc and "absolute" not in intensity_doc:
        return False
    return all(
        str(row.get("monopole_intensity_class", "")) == "source_derived_absolute"
        for row in rows
    )


def build_spectral_points(dataset: dict[str, Any]) -> list[SpectralPoint]:
    """Map FIRAS rows to SI spectral quantities with the declared Jacobian.

    Native axis is wavenumber in ``cm^-1``. Conversions::

        k[m^-1] = k[cm^-1] * 100
        nu      = c * k[m^-1]
        lambda  = 1 / k[m^-1]
        B_lambda = B_nu * nu^2 / c   (proportional; arbitrary units)

    ``B_lambda`` is reported in arbitrary units because only its argmax (the
    peak location) is used; the MJy/sr -> SI ordinate scale cancels under argmax.
    """
    points: list[SpectralPoint] = []
    for row in dataset["rows"]:
        k_cm = float(row["spectral_axis_cm_inverse"])
        k_m = k_cm * 100.0
        nu = SPEED_OF_LIGHT_M_S * k_m
        wavelength = 1.0 / k_m
        b_nu = float(row["monopole_intensity_mjy_sr"])
        b_lambda = b_nu * nu * nu / SPEED_OF_LIGHT_M_S
        points.append(
            SpectralPoint(
                row_id=str(row["row_id"]),
                wavenumber_cm_inverse=k_cm,
                wavenumber_m_inverse=k_m,
                frequency_hz=nu,
                wavelength_m=wavelength,
                b_nu_mjy_sr=b_nu,
                b_lambda_arbitrary=b_lambda,
            )
        )
    return points


def _parabolic_vertex(
    x0: float, x1: float, x2: float, y0: float, y1: float, y2: float
) -> float:
    """Return the x-location of the vertex of the parabola through 3 points."""
    denom = (x0 - x1) * (x0 - x2) * (x1 - x2)
    if denom == 0:
        return x1
    coeff_a = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / denom
    coeff_b = (
        x2 * x2 * (y0 - y1) + x1 * x1 * (y2 - y0) + x0 * x0 * (y1 - y2)
    ) / denom
    if coeff_a == 0:
        return x1
    return -coeff_b / (2.0 * coeff_a)


@dataclass(frozen=True)
class WienFirasPeakMetric:
    """Deterministic Wien-peak consistency metric and control outcomes."""

    verdict: str
    reference_temperature_k: float
    reference_wavelength_peak_m: float
    reference_wavenumber_cm_inverse: float
    wavelength_domain_peak_raw_bin_m: float
    wavelength_domain_peak_raw_bin_wavenumber_cm_inverse: float
    wavelength_domain_peak_interpolated_m: float
    raw_bin_relative_difference: float
    interpolated_relative_difference: float
    frequency_domain_peak_wavenumber_cm_inverse: float
    frequency_domain_peak_frequency_hz: float
    no_jacobian_relabel_wavelength_m: float
    no_jacobian_relabel_relative_difference: float
    wrong_temperature_k: float
    wrong_temperature_relative_difference: float
    bin_spacing_below_cm_inverse: float
    bin_spacing_above_cm_inverse: float
    controls: dict[str, bool]


def evaluate_wien_firas_peak(
    dataset: dict[str, Any],
    *,
    reference_temperature_k: float = REFERENCE_TEMPERATURE_K,
    constant_m_k: float = WIEN_WAVELENGTH_DISPLACEMENT_M_K,
) -> WienFirasPeakMetric:
    """Compute the deterministic Wien-peak consistency metric and controls."""
    points = build_spectral_points(dataset)
    if len(points) < 3:
        raise ValueError("need at least three spectral points to locate a peak")

    lambda_ref = reference_wavelength_peak_m(reference_temperature_k, constant_m_k)

    # --- Control: absolute-vs-residual product gate (gate 1). ---
    absolute_product_ok = _is_absolute_product(dataset)

    # --- Frequency-domain control peak: argmax of native B_nu. ---
    freq_peak = max(points, key=lambda p: p.b_nu_mjy_sr)

    # --- Primary metric: wavelength-domain peak after the Jacobian. ---
    by_wavelength = sorted(points, key=lambda p: p.wavelength_m)
    lambdas = [p.wavelength_m for p in by_wavelength]
    b_lambdas = [p.b_lambda_arbitrary for p in by_wavelength]
    imax = max(range(len(b_lambdas)), key=lambda i: b_lambdas[i])
    raw_bin_peak = by_wavelength[imax]

    # Parabolic refinement (fixed deterministic interpolation, not a fit).
    if 0 < imax < len(lambdas) - 1:
        interp_peak_m = _parabolic_vertex(
            lambdas[imax - 1], lambdas[imax], lambdas[imax + 1],
            b_lambdas[imax - 1], b_lambdas[imax], b_lambdas[imax + 1],
        )
    else:
        interp_peak_m = raw_bin_peak.wavelength_m

    raw_bin_rel = abs(raw_bin_peak.wavelength_m - lambda_ref) / lambda_ref
    interp_rel = abs(interp_peak_m - lambda_ref) / lambda_ref

    # Bin spacing around the wavelength peak (sampling-resolution diagnostic),
    # measured on the native wavenumber axis where FIRAS is uniformly sampled.
    by_wavenumber = sorted(points, key=lambda p: p.wavenumber_cm_inverse)
    k_values = [p.wavenumber_cm_inverse for p in by_wavenumber]
    k_index = k_values.index(raw_bin_peak.wavenumber_cm_inverse)
    spacing_below = (
        k_values[k_index] - k_values[k_index - 1] if k_index > 0 else float("nan")
    )
    spacing_above = (
        k_values[k_index + 1] - k_values[k_index]
        if k_index < len(k_values) - 1
        else float("nan")
    )

    # --- Control: no-Jacobian relabel. Interpret the B_nu argmax directly as a
    # wavelength peak (i.e. relabel the axis without the Jacobian). ---
    relabel_wavelength_m = freq_peak.wavelength_m
    relabel_rel = abs(relabel_wavelength_m - lambda_ref) / lambda_ref

    # --- Control: wrong temperature. Offset T by +10% deterministically. ---
    wrong_temperature_k = reference_temperature_k * 1.10
    lambda_ref_wrong = reference_wavelength_peak_m(wrong_temperature_k, constant_m_k)
    wrong_temperature_rel = (
        abs(raw_bin_peak.wavelength_m - lambda_ref_wrong) / lambda_ref_wrong
    )

    controls = {
        "absolute_product_gate": absolute_product_ok,
        "no_jacobian_relabel_rejected": relabel_rel >= CONTROL_MIN_RELATIVE_MISS,
        "frequency_domain_peak_distinct": (
            abs(
                freq_peak.wavenumber_cm_inverse
                - raw_bin_peak.wavenumber_cm_inverse
            )
            > max(spacing_below, spacing_above)
        ),
        "wrong_temperature_rejected": (
            wrong_temperature_rel >= CONTROL_MIN_RELATIVE_MISS
        ),
    }

    verdict = _decide_verdict(
        absolute_product_ok=absolute_product_ok,
        controls=controls,
        raw_bin_rel=raw_bin_rel,
        interp_rel=interp_rel,
    )

    return WienFirasPeakMetric(
        verdict=verdict,
        reference_temperature_k=reference_temperature_k,
        reference_wavelength_peak_m=lambda_ref,
        reference_wavenumber_cm_inverse=1.0 / lambda_ref / 100.0,
        wavelength_domain_peak_raw_bin_m=raw_bin_peak.wavelength_m,
        wavelength_domain_peak_raw_bin_wavenumber_cm_inverse=(
            raw_bin_peak.wavenumber_cm_inverse
        ),
        wavelength_domain_peak_interpolated_m=interp_peak_m,
        raw_bin_relative_difference=raw_bin_rel,
        interpolated_relative_difference=interp_rel,
        frequency_domain_peak_wavenumber_cm_inverse=freq_peak.wavenumber_cm_inverse,
        frequency_domain_peak_frequency_hz=freq_peak.frequency_hz,
        no_jacobian_relabel_wavelength_m=relabel_wavelength_m,
        no_jacobian_relabel_relative_difference=relabel_rel,
        wrong_temperature_k=wrong_temperature_k,
        wrong_temperature_relative_difference=wrong_temperature_rel,
        bin_spacing_below_cm_inverse=spacing_below,
        bin_spacing_above_cm_inverse=spacing_above,
        controls=controls,
    )


def _decide_verdict(
    *,
    absolute_product_ok: bool,
    controls: dict[str, bool],
    raw_bin_rel: float,
    interp_rel: float,
) -> str:
    """Map metric + control outcomes to exactly one admissible verdict."""
    if not absolute_product_ok:
        return "INCONCLUSIVE_PRODUCT_SEMANTICS"
    # If the declared domain-conversion controls do not behave (the Jacobian /
    # frequency-domain separation collapses or the wrong-T control passes),
    # the conversion is mishandled or the spectrum is non-blackbody.
    conversion_controls_ok = (
        controls["no_jacobian_relabel_rejected"]
        and controls["frequency_domain_peak_distinct"]
        and controls["wrong_temperature_rejected"]
    )
    if not conversion_controls_ok:
        return "DOMAIN_CONVERSION_MISMATCH"
    # Primary consistency decision: prefer the interpolation gate; fall back to
    # the loose raw-bin gate. If neither passes, the sampling resolution is the
    # limiting factor rather than a domain mismatch.
    if interp_rel <= INTERPOLATED_RELATIVE_TOLERANCE:
        return "CONSISTENT_IN_SCOPE"
    if raw_bin_rel <= RAW_BIN_RELATIVE_TOLERANCE:
        return "CONSISTENT_IN_SCOPE"
    return "INCONCLUSIVE_SAMPLING_RESOLUTION"


__all__ = [
    "ADMISSIBLE_VERDICTS",
    "INTERPOLATED_RELATIVE_TOLERANCE",
    "RAW_BIN_RELATIVE_TOLERANCE",
    "REFERENCE_TEMPERATURE_CITATION",
    "REFERENCE_TEMPERATURE_K",
    "REFERENCE_TEMPERATURE_SIGMA_K",
    "SPEED_OF_LIGHT_M_S",
    "WIEN_WAVELENGTH_DISPLACEMENT_M_K",
    "SpectralPoint",
    "WienFirasPeakMetric",
    "build_spectral_points",
    "evaluate_wien_firas_peak",
    "load_firas_rows",
    "reference_wavelength_peak_m",
]
