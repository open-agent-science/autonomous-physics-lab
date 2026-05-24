"""TASK-0361 exoplanet mass-radius baseline benchmark engine.

This module implements the first benchmark surface for the Exoplanet
Mass-Radius campaign as a deterministic, snapshot-only computation. It
exposes a frozen Chen-Kipping-style piecewise-power-law baseline (no new
free parameters fit to the snapshot) and a simple per-class median null
baseline so any candidate improvement has a non-trivial floor.

The module does not fetch live data, does not promote claims, does not
register prediction-registry entries, does not produce habitability /
biosignature / target-prioritization output, and does not fit any new
free parameters on the snapshot. All baseline coefficients are pinned to
published Chen-Kipping 2017 values.

Reference
---------

Chen, J. & Kipping, D. M. (2017), "Probabilistic Forecasting of the
Masses and Radii of Other Worlds", ApJ 834, 17.
DOI: 10.3847/1538-4357/834/1/17.

The piecewise power-law segmentation and slopes used here are the
published median-relation values; per-class prefactors are derived from
the continuity condition at each changepoint anchored at the canonical
Terran segment (R = 1.008 * (M / M_earth) ** 0.279).
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable


# Unit conversions used throughout the module. M_earth and M_jup are the
# IAU 2015 nominal values; Jovian → Earth and Solar → Earth ratios are
# the published CK17 transitions converted to Earth-mass units.
EARTH_MASS_TO_JUP_MASS: float = 1.0 / 317.828
JUP_MASS_TO_EARTH_MASS: float = 317.828
SOLAR_MASS_TO_EARTH_MASS: float = 332946.0


# ---------------------------------------------------------------------------
# Chen-Kipping piecewise power-law baseline (frozen parameters)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ChenKippingSegment:
    """One segment of the Chen-Kipping piecewise mass-radius relation."""

    name: str
    mass_lower_mearth: float
    mass_upper_mearth: float
    slope_log_r_per_log_m: float
    prefactor_r_earth_per_mass_unit_pow_slope: float
    anchor_mass_mearth: float


def _build_chen_kipping_segments() -> tuple[ChenKippingSegment, ...]:
    """Build the four frozen Chen-Kipping segments.

    Terran segment uses the canonical CK17 prefactor 1.008 in
    Earth-radii at one Earth-mass. Subsequent segments inherit
    continuity at each changepoint.
    """

    terran_prefactor = 1.008
    terran_slope = 0.279
    neptunian_slope = 0.589
    jovian_slope = -0.044
    stellar_slope = 0.881

    m_terran_upper = 2.04  # Earth masses
    m_neptunian_upper = 0.414 * JUP_MASS_TO_EARTH_MASS  # ≈ 131.58 Earth masses
    m_jovian_upper = 0.0800 * SOLAR_MASS_TO_EARTH_MASS  # ≈ 26635.68 Earth masses
    m_stellar_upper = float("inf")

    # Continuity: each segment's prefactor is set so that the prediction
    # equals the previous segment's prediction at the lower changepoint.
    radius_at_terran_upper = terran_prefactor * (m_terran_upper ** terran_slope)
    neptunian_prefactor = radius_at_terran_upper / (m_terran_upper ** neptunian_slope)

    radius_at_neptunian_upper = neptunian_prefactor * (
        m_neptunian_upper ** neptunian_slope
    )
    jovian_prefactor = radius_at_neptunian_upper / (
        m_neptunian_upper ** jovian_slope
    )

    radius_at_jovian_upper = jovian_prefactor * (m_jovian_upper ** jovian_slope)
    stellar_prefactor = radius_at_jovian_upper / (m_jovian_upper ** stellar_slope)

    return (
        ChenKippingSegment(
            name="terran",
            mass_lower_mearth=0.0,
            mass_upper_mearth=m_terran_upper,
            slope_log_r_per_log_m=terran_slope,
            prefactor_r_earth_per_mass_unit_pow_slope=terran_prefactor,
            anchor_mass_mearth=1.0,
        ),
        ChenKippingSegment(
            name="neptunian",
            mass_lower_mearth=m_terran_upper,
            mass_upper_mearth=m_neptunian_upper,
            slope_log_r_per_log_m=neptunian_slope,
            prefactor_r_earth_per_mass_unit_pow_slope=neptunian_prefactor,
            anchor_mass_mearth=m_terran_upper,
        ),
        ChenKippingSegment(
            name="jovian",
            mass_lower_mearth=m_neptunian_upper,
            mass_upper_mearth=m_jovian_upper,
            slope_log_r_per_log_m=jovian_slope,
            prefactor_r_earth_per_mass_unit_pow_slope=jovian_prefactor,
            anchor_mass_mearth=m_neptunian_upper,
        ),
        ChenKippingSegment(
            name="stellar",
            mass_lower_mearth=m_jovian_upper,
            mass_upper_mearth=m_stellar_upper,
            slope_log_r_per_log_m=stellar_slope,
            prefactor_r_earth_per_mass_unit_pow_slope=stellar_prefactor,
            anchor_mass_mearth=m_jovian_upper,
        ),
    )


CHEN_KIPPING_SEGMENTS: tuple[ChenKippingSegment, ...] = _build_chen_kipping_segments()


def chen_kipping_segment_for_mass(mass_mearth: float) -> ChenKippingSegment:
    """Return the CK17 segment containing the given Earth-mass value."""

    if mass_mearth <= 0.0 or not math.isfinite(mass_mearth):
        return CHEN_KIPPING_SEGMENTS[0]
    for segment in CHEN_KIPPING_SEGMENTS:
        if mass_mearth <= segment.mass_upper_mearth:
            return segment
    return CHEN_KIPPING_SEGMENTS[-1]


def chen_kipping_predict_radius(mass_mearth: float) -> float:
    """Return the CK17 predicted radius (Earth radii) for the given mass."""

    if mass_mearth is None or mass_mearth <= 0.0 or not math.isfinite(mass_mearth):
        return float("nan")
    segment = chen_kipping_segment_for_mass(mass_mearth)
    return float(
        segment.prefactor_r_earth_per_mass_unit_pow_slope
        * (mass_mearth ** segment.slope_log_r_per_log_m)
    )


def planet_class_for_mass(mass_mearth: float) -> str:
    """Return a coarse planet-class label keyed on CK17 segments."""

    return chen_kipping_segment_for_mass(mass_mearth).name


# ---------------------------------------------------------------------------
# Null baselines
# ---------------------------------------------------------------------------


def per_class_median_log_radius(
    pairs: Iterable[tuple[float, float]]
) -> dict[str, float]:
    """Return per-class median log10(R/R_earth) over the given (M, R) pairs.

    Pairs are (mass_mearth, radius_rearth) of rows that contribute to the
    null baseline's training fold. The returned mapping is keyed on the
    same CK17 planet-class names returned by :func:`planet_class_for_mass`.
    """

    by_class: dict[str, list[float]] = {}
    for mass, radius in pairs:
        if mass is None or radius is None:
            continue
        if mass <= 0.0 or radius <= 0.0:
            continue
        if not (math.isfinite(mass) and math.isfinite(radius)):
            continue
        label = planet_class_for_mass(float(mass))
        by_class.setdefault(label, []).append(math.log10(float(radius)))
    medians: dict[str, float] = {}
    for label, values in by_class.items():
        values_sorted = sorted(values)
        mid = len(values_sorted) // 2
        if len(values_sorted) % 2 == 1:
            medians[label] = values_sorted[mid]
        else:
            medians[label] = 0.5 * (values_sorted[mid - 1] + values_sorted[mid])
    return medians


def null_baseline_predict_radius(
    mass_mearth: float, *, per_class_medians: dict[str, float]
) -> float:
    """Return per-class median radius prediction for the given mass."""

    if mass_mearth is None or mass_mearth <= 0.0 or not math.isfinite(mass_mearth):
        return float("nan")
    label = planet_class_for_mass(float(mass_mearth))
    log_radius = per_class_medians.get(label)
    if log_radius is None:
        # Fall back to the dataset-wide median when the class is unseen
        # in the training fold (e.g. extreme stellar masses with no
        # observed radius). The fallback is documented; the absence is
        # also recorded explicitly in the run metrics.
        return float("nan")
    return float(10.0 ** log_radius)


# ---------------------------------------------------------------------------
# Row eligibility for the true-mass residual axis
# ---------------------------------------------------------------------------


def _row_has_true_mass_and_transit_radius(entry: dict[str, Any]) -> bool:
    """Return True when an entry is admissible to the true-mass axis."""

    mass = entry.get("mass") or {}
    radius = entry.get("radius") or {}
    return (
        mass.get("mass_class") == "true_mass"
        and radius.get("radius_class") == "transit_radius"
        and isinstance(mass.get("value"), (int, float))
        and isinstance(radius.get("value"), (int, float))
        and float(mass.get("value")) > 0.0
        and float(radius.get("value")) > 0.0
    )


def _row_has_minimum_mass_and_transit_radius(entry: dict[str, Any]) -> bool:
    """Return True when an entry is admissible to the minimum-mass axis."""

    mass = entry.get("mass") or {}
    radius = entry.get("radius") or {}
    return (
        mass.get("mass_class") == "minimum_mass_msini"
        and radius.get("radius_class") == "transit_radius"
        and isinstance(mass.get("value"), (int, float))
        and isinstance(radius.get("value"), (int, float))
        and float(mass.get("value")) > 0.0
        and float(radius.get("value")) > 0.0
    )


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ResidualSummary:
    """Summary statistics for a set of log-space residuals."""

    count: int
    log10_mae: float | None
    log10_rmse: float | None
    log10_bias: float | None
    median_log10_residual: float | None
    interval_68_coverage: float | None
    interval_95_coverage: float | None
    fraction_within_factor_2: float | None


def _safe_mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _safe_median(values: list[float]) -> float | None:
    if not values:
        return None
    sorted_values = sorted(values)
    mid = len(sorted_values) // 2
    if len(sorted_values) % 2 == 1:
        return sorted_values[mid]
    return 0.5 * (sorted_values[mid - 1] + sorted_values[mid])


def _absolute_mean(values: list[float]) -> float | None:
    return sum(abs(value) for value in values) / len(values) if values else None


def _root_mean_square(values: list[float]) -> float | None:
    if not values:
        return None
    return math.sqrt(sum(value * value for value in values) / len(values))


def summarize_log_residuals(
    residuals: list[float],
    *,
    interval_68_threshold: float = 0.176,
    interval_95_threshold: float = 0.301,
) -> ResidualSummary:
    """Summarise log10-space residuals.

    The interval thresholds are the log10 widths corresponding to a
    factor-1.5 and factor-2 ratio (log10(1.5) ≈ 0.176, log10(2.0) ≈ 0.301)
    so the campaign can report calibration-flavoured coverage without
    requiring uncertainty estimates from the baseline itself.
    """

    if not residuals:
        return ResidualSummary(
            count=0,
            log10_mae=None,
            log10_rmse=None,
            log10_bias=None,
            median_log10_residual=None,
            interval_68_coverage=None,
            interval_95_coverage=None,
            fraction_within_factor_2=None,
        )
    abs_residuals = [abs(value) for value in residuals]
    inside_68 = sum(1 for value in abs_residuals if value <= interval_68_threshold)
    inside_95 = sum(1 for value in abs_residuals if value <= interval_95_threshold)
    within_factor_2 = sum(1 for value in abs_residuals if value <= 0.301)
    return ResidualSummary(
        count=len(residuals),
        log10_mae=_absolute_mean(residuals),
        log10_rmse=_root_mean_square(residuals),
        log10_bias=_safe_mean(residuals),
        median_log10_residual=_safe_median(residuals),
        interval_68_coverage=inside_68 / len(residuals),
        interval_95_coverage=inside_95 / len(residuals),
        fraction_within_factor_2=within_factor_2 / len(residuals),
    )


# ---------------------------------------------------------------------------
# Benchmark execution
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BenchmarkRow:
    """One eligible row contributing to the benchmark residual axis."""

    row_id: str
    planet_name: str
    detection_method: str
    mass_mearth: float
    radius_rearth: float
    mass_class: str
    radius_class: str
    planet_class: str
    chen_kipping_radius_rearth: float
    null_baseline_radius_rearth: float
    chen_kipping_log_residual: float
    null_baseline_log_residual: float | None


@dataclass(frozen=True)
class BenchmarkResult:
    """Outcome of running both baselines on a single residual axis."""

    axis_name: str
    eligible_row_count: int
    rows: list[BenchmarkRow]
    overall_chen_kipping: ResidualSummary
    overall_null: ResidualSummary
    per_class_chen_kipping: dict[str, ResidualSummary]
    per_class_null: dict[str, ResidualSummary]
    per_detection_method_chen_kipping: dict[str, ResidualSummary]
    per_detection_method_null: dict[str, ResidualSummary]


def _build_rows_for_axis(
    entries: list[dict[str, Any]],
    *,
    eligibility: callable,
    per_class_medians: dict[str, float],
) -> list[BenchmarkRow]:
    rows: list[BenchmarkRow] = []
    for entry in entries:
        if not eligibility(entry):
            continue
        mass = float(entry["mass"]["value"])
        radius = float(entry["radius"]["value"])
        if mass <= 0.0 or radius <= 0.0:
            continue
        ck_radius = chen_kipping_predict_radius(mass)
        null_radius = null_baseline_predict_radius(
            mass, per_class_medians=per_class_medians
        )
        ck_log_residual = math.log10(radius) - math.log10(ck_radius)
        null_log_residual = (
            math.log10(radius) - math.log10(null_radius)
            if null_radius == null_radius  # NaN check
            else None
        )
        if not math.isfinite(ck_log_residual):
            continue
        rows.append(
            BenchmarkRow(
                row_id=str(entry["row_id"]),
                planet_name=str(entry["planet_name"]),
                detection_method=str(entry["detection_method"]),
                mass_mearth=mass,
                radius_rearth=radius,
                mass_class=str(entry["mass"]["mass_class"]),
                radius_class=str(entry["radius"]["radius_class"]),
                planet_class=planet_class_for_mass(mass),
                chen_kipping_radius_rearth=ck_radius,
                null_baseline_radius_rearth=null_radius,
                chen_kipping_log_residual=ck_log_residual,
                null_baseline_log_residual=null_log_residual,
            )
        )
    return rows


def _summarize_by_label(
    rows: list[BenchmarkRow],
    label_fn: callable,
    *,
    use_chen_kipping: bool,
) -> dict[str, ResidualSummary]:
    buckets: dict[str, list[float]] = {}
    for row in rows:
        if use_chen_kipping:
            residual = row.chen_kipping_log_residual
        else:
            residual = row.null_baseline_log_residual
        if residual is None or not math.isfinite(residual):
            continue
        buckets.setdefault(label_fn(row), []).append(residual)
    return {
        label: summarize_log_residuals(values)
        for label, values in sorted(buckets.items())
    }


def run_benchmark_for_axis(
    entries: list[dict[str, Any]],
    *,
    axis_name: str,
    eligibility: callable,
) -> BenchmarkResult:
    """Run both baselines on the rows that satisfy the eligibility predicate."""

    eligible_entries = [entry for entry in entries if eligibility(entry)]
    pairs = [
        (float(entry["mass"]["value"]), float(entry["radius"]["value"]))
        for entry in eligible_entries
    ]
    per_class_medians = per_class_median_log_radius(pairs)
    rows = _build_rows_for_axis(
        entries, eligibility=eligibility, per_class_medians=per_class_medians
    )
    overall_ck = summarize_log_residuals(
        [row.chen_kipping_log_residual for row in rows]
    )
    overall_null = summarize_log_residuals(
        [
            row.null_baseline_log_residual
            for row in rows
            if row.null_baseline_log_residual is not None
        ]
    )
    return BenchmarkResult(
        axis_name=axis_name,
        eligible_row_count=len(rows),
        rows=rows,
        overall_chen_kipping=overall_ck,
        overall_null=overall_null,
        per_class_chen_kipping=_summarize_by_label(
            rows, lambda r: r.planet_class, use_chen_kipping=True
        ),
        per_class_null=_summarize_by_label(
            rows, lambda r: r.planet_class, use_chen_kipping=False
        ),
        per_detection_method_chen_kipping=_summarize_by_label(
            rows, lambda r: r.detection_method, use_chen_kipping=True
        ),
        per_detection_method_null=_summarize_by_label(
            rows, lambda r: r.detection_method, use_chen_kipping=False
        ),
    )


def run_benchmark(entries: list[dict[str, Any]]) -> dict[str, BenchmarkResult]:
    """Run both baselines on every eligible residual axis."""

    return {
        "true_mass_with_transit_radius": run_benchmark_for_axis(
            entries,
            axis_name="true_mass_with_transit_radius",
            eligibility=_row_has_true_mass_and_transit_radius,
        ),
        "minimum_mass_with_transit_radius": run_benchmark_for_axis(
            entries,
            axis_name="minimum_mass_with_transit_radius",
            eligibility=_row_has_minimum_mass_and_transit_radius,
        ),
    }


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------


def residual_summary_to_dict(summary: ResidualSummary) -> dict[str, Any]:
    """Return a JSON-serialisable form of a residual summary."""

    return {
        "count": summary.count,
        "log10_mae": summary.log10_mae,
        "log10_rmse": summary.log10_rmse,
        "log10_bias": summary.log10_bias,
        "median_log10_residual": summary.median_log10_residual,
        "interval_68_coverage": summary.interval_68_coverage,
        "interval_95_coverage": summary.interval_95_coverage,
        "fraction_within_factor_2": summary.fraction_within_factor_2,
    }


def benchmark_result_to_dict(result: BenchmarkResult) -> dict[str, Any]:
    """Return a JSON-serialisable form of a benchmark result."""

    return {
        "axis_name": result.axis_name,
        "eligible_row_count": result.eligible_row_count,
        "overall_chen_kipping": residual_summary_to_dict(result.overall_chen_kipping),
        "overall_null": residual_summary_to_dict(result.overall_null),
        "per_class_chen_kipping": {
            label: residual_summary_to_dict(summary)
            for label, summary in result.per_class_chen_kipping.items()
        },
        "per_class_null": {
            label: residual_summary_to_dict(summary)
            for label, summary in result.per_class_null.items()
        },
        "per_detection_method_chen_kipping": {
            label: residual_summary_to_dict(summary)
            for label, summary in result.per_detection_method_chen_kipping.items()
        },
        "per_detection_method_null": {
            label: residual_summary_to_dict(summary)
            for label, summary in result.per_detection_method_null.items()
        },
    }


def chen_kipping_baseline_metadata() -> dict[str, Any]:
    """Return the frozen Chen-Kipping baseline metadata for the manifest."""

    return {
        "name": "Chen-Kipping 2017 piecewise median power-law (frozen)",
        "reference": (
            "Chen, J. & Kipping, D. M. (2017), ApJ 834, 17, "
            "DOI 10.3847/1538-4357/834/1/17"
        ),
        "no_new_parameters_fit": True,
        "segments": [
            {
                "name": segment.name,
                "mass_lower_mearth": segment.mass_lower_mearth,
                "mass_upper_mearth": (
                    None
                    if math.isinf(segment.mass_upper_mearth)
                    else segment.mass_upper_mearth
                ),
                "slope_log_r_per_log_m": segment.slope_log_r_per_log_m,
                "prefactor_r_earth_per_mass_unit_pow_slope": (
                    segment.prefactor_r_earth_per_mass_unit_pow_slope
                ),
                "anchor_mass_mearth": segment.anchor_mass_mearth,
            }
            for segment in CHEN_KIPPING_SEGMENTS
        ],
    }


def planet_class_distribution(rows: list[BenchmarkRow]) -> dict[str, int]:
    """Return a count of rows per planet class for the failure-map summary."""

    counter = Counter(row.planet_class for row in rows)
    return dict(sorted(counter.items()))
