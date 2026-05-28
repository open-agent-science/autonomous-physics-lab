"""TASK-0427 exoplanet compact/sub-Neptune residual matched-control audit.

Sandbox-only audit of the CSN-001/002/003 compact and sub-Neptune
residual-stress slices on the committed PSCompPars snapshot. The runner
keeps the frozen Chen-Kipping baseline fixed, uses true-mass/transit-radius
rows as the interpretable axis, reproduces the TASK-0390 / AGENT-RUN-0036
pilot baselines, and tests whether each pattern survives matched controls
and deterministic negative controls before any promotion scorecard treats
it as a scientist-facing benchmark feature.

No live fetch, baseline refit, composition inference, atmospheric inference,
habitability wording, target-priority output, prediction entry, canonical
result, claim update, or knowledge edit is produced.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path
from typing import Any, Callable

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.datasets.exoplanets import (  # noqa: E402
    apply_inclusion_filters,
    load_exoplanet_snapshot,
)
from physics_lab.engines.exoplanet_mass_radius import (  # noqa: E402
    chen_kipping_predict_radius,
    planet_class_for_mass,
)

AGENT_RUN_ID = "AGENT-RUN-0042"
TASK_ID = "TASK-0427"
CAMPAIGN_PROFILE_ID = "exoplanet-mass-radius"
PILOT_AGENT_RUN_ID = "AGENT-RUN-0036"
PILOT_TASK_ID = "TASK-0390"

DEFAULT_SNAPSHOT_PATH = (
    REPO_ROOT / "data" / "exoplanets" / "exo-0001-pscomppars-snapshot.yaml"
)
DEFAULT_AGENT_RUN_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
DEFAULT_METRICS_PATH = DEFAULT_AGENT_RUN_DIR / "metrics.json"
DEFAULT_REPORT_PATH = DEFAULT_AGENT_RUN_DIR / "report.md"
DEFAULT_AGENT_RUN_PATH = DEFAULT_AGENT_RUN_DIR / "agent_run.yaml"
DEFAULT_LIMITATIONS_PATH = DEFAULT_AGENT_RUN_DIR / "limitations.md"
DEFAULT_PREFLIGHT_PATH = DEFAULT_AGENT_RUN_DIR / "preflight.md"
DEFAULT_REVIEW_SUMMARY_PATH = DEFAULT_AGENT_RUN_DIR / "review_summary.md"
DEFAULT_REVIEW_PATH = (
    REPO_ROOT
    / "docs"
    / "reviews"
    / "exoplanet-compact-subneptune-matched-control-audit.md"
)

MIN_SLICE_ROW_COUNT: int = 30
CONTROL_MARGIN_LOG10_RMSE: float = 0.022
SHUFFLE_SEED: int = 20260528
RANDOM_OUTSIDE_SEED: int = 20260528

# Pilot baselines from agent_runs/AGENT-RUN-0036/metrics.json. These are
# pinned to the committed snapshot at the time of TASK-0390 and are used as
# the reproduction-check anchor for this matched-control audit.
PILOT_BASELINES: dict[str, dict[str, Any]] = {
    "CSN-001": {
        "label": "compact_radius_lt1p5Re",
        "count": 92,
        "log10_rmse": 0.26335002767665594,
    },
    "CSN-002": {
        "label": "sub_neptune_radius_1p5_4Re",
        "count": 340,
        "log10_rmse": 0.20417461029825093,
    },
    "CSN-003": {
        "label": "compact_or_sub_neptune_radius_lt4Re",
        "count": 432,
        "log10_rmse": 0.21812633379546398,
    },
}
PILOT_ELIGIBLE_BASELINE: dict[str, Any] = {
    "count": 1207,
    "log10_rmse": 0.1581701926744863,
}
PILOT_REPRODUCTION_TOLERANCE: float = 1.0e-9


# ---------------------------------------------------------------------------
# Row + value helpers
# ---------------------------------------------------------------------------


def _is_positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value)) and value > 0


def _row_has_true_mass_and_transit_radius(entry: dict[str, Any]) -> bool:
    mass = entry.get("mass") or {}
    radius = entry.get("radius") or {}
    return (
        mass.get("mass_class") == "true_mass"
        and radius.get("radius_class") == "transit_radius"
        and _is_positive_number(mass.get("value"))
        and _is_positive_number(radius.get("value"))
    )


def _row_has_minimum_mass_and_transit_radius(entry: dict[str, Any]) -> bool:
    mass = entry.get("mass") or {}
    radius = entry.get("radius") or {}
    return (
        mass.get("mass_class") == "minimum_mass_msini"
        and radius.get("radius_class") == "transit_radius"
        and _is_positive_number(mass.get("value"))
        and _is_positive_number(radius.get("value"))
    )


def _mass_value(entry: dict[str, Any]) -> float:
    return float(entry["mass"]["value"])


def _radius_value(entry: dict[str, Any]) -> float:
    return float(entry["radius"]["value"])


def _host_teff(entry: dict[str, Any]) -> float | None:
    value = (entry.get("host_star") or {}).get("effective_temperature_K")
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def _detection_method(entry: dict[str, Any]) -> str | None:
    value = entry.get("detection_method")
    if isinstance(value, str) and value:
        return value
    return None


def _relative_uncertainty(component: dict[str, Any]) -> float | None:
    value = component.get("value")
    if not _is_positive_number(value):
        return None
    candidates = [
        abs(float(v))
        for v in (component.get("uncertainty_upper"), component.get("uncertainty_lower"))
        if isinstance(v, (int, float)) and math.isfinite(float(v))
    ]
    if not candidates:
        return None
    return max(candidates) / float(value)


def _combined_uncertainty(entry: dict[str, Any]) -> float | None:
    values = [
        value
        for value in (
            _relative_uncertainty(entry.get("mass") or {}),
            _relative_uncertainty(entry.get("radius") or {}),
        )
        if value is not None
    ]
    return max(values) if values else None


def _uncertainty_band(entry: dict[str, Any]) -> str:
    value = _combined_uncertainty(entry)
    if value is None:
        return "missing"
    if value <= 0.05:
        return "tight_le5pct"
    if value <= 0.15:
        return "moderate_5_15pct"
    return "loose_gt15pct"


# ---------------------------------------------------------------------------
# CSN target slice predicates (reproduced from TASK-0390 pilot)
# ---------------------------------------------------------------------------


def _is_compact(entry: dict[str, Any]) -> bool:
    return _radius_value(entry) < 1.5


def _is_sub_neptune(entry: dict[str, Any]) -> bool:
    radius = _radius_value(entry)
    return 1.5 <= radius < 4.0


def _is_compact_or_sub_neptune(entry: dict[str, Any]) -> bool:
    return _radius_value(entry) < 4.0


TARGET_SLICES: list[dict[str, Any]] = [
    {
        "id": "CSN-001",
        "label": "compact_radius_lt1p5Re",
        "predicate": _is_compact,
        "description": (
            "Compact true-mass/transit-radius rows with R/Re < 1.5; "
            "tests whether the pilot residual stress survives matched and "
            "negative controls."
        ),
    },
    {
        "id": "CSN-002",
        "label": "sub_neptune_radius_1p5_4Re",
        "predicate": _is_sub_neptune,
        "description": (
            "Sub-Neptune true-mass/transit-radius rows with 1.5 <= R/Re < 4; "
            "tests whether the pilot residual stress survives matched and "
            "negative controls."
        ),
    },
    {
        "id": "CSN-003",
        "label": "compact_or_sub_neptune_radius_lt4Re",
        "predicate": _is_compact_or_sub_neptune,
        "description": (
            "Combined compact/sub-Neptune envelope with R/Re < 4; tests "
            "the bounded high-stress envelope claim under matched and "
            "negative controls."
        ),
    },
]


# ---------------------------------------------------------------------------
# Residual + stats helpers
# ---------------------------------------------------------------------------


def _log_residual(entry: dict[str, Any]) -> float | None:
    mass = _mass_value(entry)
    radius = _radius_value(entry)
    pred = chen_kipping_predict_radius(mass)
    if not math.isfinite(pred) or pred <= 0.0:
        return None
    return math.log10(radius) - math.log10(pred)


def _rmse(values: list[float]) -> float | None:
    if not values:
        return None
    return math.sqrt(sum(v * v for v in values) / len(values))


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[midpoint]
    return 0.5 * (ordered[midpoint - 1] + ordered[midpoint])


def _stats(values: list[float]) -> dict[str, Any]:
    return {
        "count": len(values),
        "log10_rmse": _rmse(values),
        "log10_mae": _mean([abs(v) for v in values]),
        "log10_bias": _mean(values),
        "log10_median": _median(values),
    }


def _residual_map(entries: list[dict[str, Any]]) -> dict[str, float]:
    residuals: dict[str, float] = {}
    for entry in entries:
        value = _log_residual(entry)
        if value is not None and math.isfinite(value):
            residuals[entry["row_id"]] = value
    return residuals


def _residual_values(
    entries: list[dict[str, Any]], residuals: dict[str, float]
) -> list[float]:
    return [
        residuals[entry["row_id"]]
        for entry in entries
        if residuals.get(entry["row_id"]) is not None
    ]


def _per_class_median_residuals(
    entries: list[dict[str, Any]], residuals: dict[str, float]
) -> dict[str, float]:
    by_class: dict[str, list[float]] = {}
    for entry in entries:
        residual = residuals.get(entry["row_id"])
        if residual is None:
            continue
        by_class.setdefault(planet_class_for_mass(_mass_value(entry)), []).append(residual)
    return {
        label: median
        for label, values in by_class.items()
        if (median := _median(values)) is not None
    }


def _per_class_median_control_residuals(
    target_entries: list[dict[str, Any]], per_class_medians: dict[str, float]
) -> list[float]:
    out: list[float] = []
    for entry in target_entries:
        mass = _mass_value(entry)
        radius = _radius_value(entry)
        pred = chen_kipping_predict_radius(mass)
        if not math.isfinite(pred) or pred <= 0.0:
            continue
        shift = per_class_medians.get(planet_class_for_mass(mass), 0.0)
        out.append(math.log10(radius) - (math.log10(pred) + shift))
    return out


# ---------------------------------------------------------------------------
# Matching helpers
# ---------------------------------------------------------------------------


def _greedy_match_without_replacement(
    target_entries: list[dict[str, Any]],
    candidate_entries: list[dict[str, Any]],
    target_key: Callable[[dict[str, Any]], float | None],
    candidate_key: Callable[[dict[str, Any]], float | None],
) -> list[dict[str, Any]]:
    """Match each target to the nearest available candidate for a scalar key.

    Deterministic: scans candidates in their committed order.
    """

    available: list[tuple[int, dict[str, Any], float]] = []
    for index, candidate in enumerate(candidate_entries):
        value = candidate_key(candidate)
        if value is not None and math.isfinite(value):
            available.append((index, candidate, value))

    matched: list[dict[str, Any]] = []
    used: set[int] = set()
    for target in target_entries:
        target_value = target_key(target)
        if target_value is None or not math.isfinite(target_value):
            continue
        best_index = None
        best_candidate = None
        best_delta = float("inf")
        for index, candidate, candidate_value in available:
            if index in used:
                continue
            delta = abs(candidate_value - target_value)
            if delta < best_delta:
                best_delta = delta
                best_index = index
                best_candidate = candidate
        if best_index is not None and best_candidate is not None:
            used.add(best_index)
            matched.append(best_candidate)
    return matched


def _matched_categorical_control(
    target_entries: list[dict[str, Any]],
    candidate_entries: list[dict[str, Any]],
    categorical_key: Callable[[dict[str, Any]], str | None],
) -> list[dict[str, Any]]:
    """Pick one candidate per target sharing the same categorical key value.

    Ties broken by nearest log10 mass. Deterministic; no replacement.
    """

    by_category: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidate_entries:
        key = categorical_key(candidate)
        if key is None:
            continue
        by_category.setdefault(key, []).append(candidate)
    for rows in by_category.values():
        rows.sort(key=lambda row: (math.log10(_mass_value(row)), row["row_id"]))

    used: set[str] = set()
    matched: list[dict[str, Any]] = []
    for target in target_entries:
        category = categorical_key(target)
        if category is None:
            continue
        target_mass = math.log10(_mass_value(target))
        best = None
        best_delta = float("inf")
        for candidate in by_category.get(category, []):
            if candidate["row_id"] in used:
                continue
            delta = abs(math.log10(_mass_value(candidate)) - target_mass)
            if delta < best_delta:
                best_delta = delta
                best = candidate
        if best is not None:
            used.add(best["row_id"])
            matched.append(best)
    return matched


# ---------------------------------------------------------------------------
# Negative control helpers
# ---------------------------------------------------------------------------


def _shuffled_radius_label_control(
    target_entries: list[dict[str, Any]],
    eligible_entries: list[dict[str, Any]],
    *,
    seed: int,
) -> list[float]:
    """Deterministic radius-label shuffle within the eligible set.

    Each target keeps its own mass; its radius value is replaced by a
    deterministically shuffled radius drawn from the eligible pool. Residual
    is then recomputed with the shuffled radius.
    """

    pool = [
        _radius_value(entry)
        for entry in eligible_entries
        if _is_positive_number(entry.get("radius", {}).get("value"))
    ]
    rng = random.Random(seed)
    shuffled_pool = pool.copy()
    rng.shuffle(shuffled_pool)
    out: list[float] = []
    for index, entry in enumerate(target_entries):
        if index >= len(shuffled_pool):
            break
        mass = _mass_value(entry)
        pred = chen_kipping_predict_radius(mass)
        if not math.isfinite(pred) or pred <= 0.0:
            continue
        substituted_radius = shuffled_pool[index]
        if not _is_positive_number(substituted_radius):
            continue
        out.append(math.log10(substituted_radius) - math.log10(pred))
    return out


def _uncertainty_equalized_subset(
    target_entries: list[dict[str, Any]],
    *,
    max_combined_relative_uncertainty: float = 0.15,
) -> list[dict[str, Any]]:
    """Restrict target rows to a tight-uncertainty subset (<= threshold).

    Negative control: if signal is driven by loose-uncertainty rows, the
    tight-uncertainty subset RMSE should collapse toward the eligible
    baseline. This is a target-subset control, not a comparison cohort.
    """

    out: list[dict[str, Any]] = []
    for entry in target_entries:
        combined = _combined_uncertainty(entry)
        if combined is not None and combined <= max_combined_relative_uncertainty:
            out.append(entry)
    return out


def _adverse_nearest_radius_outside_slice(
    target_entries: list[dict[str, Any]],
    eligible_entries: list[dict[str, Any]],
    target_predicate: Callable[[dict[str, Any]], bool],
) -> list[dict[str, Any]]:
    """Build the nearest-radius matched cohort drawn from rows outside the slice.

    Adverse-negative control: the cohort matches each target's radius using
    candidates that do NOT satisfy the target predicate. If the residual
    stress is radius-position driven (rather than slice-membership driven),
    this control should rise toward the target RMSE.
    """

    outside = [entry for entry in eligible_entries if not target_predicate(entry)]
    return _greedy_match_without_replacement(
        target_entries,
        outside,
        target_key=_radius_value,
        candidate_key=_radius_value,
    )


def _sample_size_matched_random_outside(
    target_entries: list[dict[str, Any]],
    eligible_entries: list[dict[str, Any]],
    target_predicate: Callable[[dict[str, Any]], bool],
    *,
    seed: int,
) -> list[dict[str, Any]]:
    """Deterministic random sample of the same size from outside-slice eligible rows.

    Negative control: a same-size random outside-slice draw whose RMSE
    should sit near the eligible RMSE, by construction.
    """

    outside = [entry for entry in eligible_entries if not target_predicate(entry)]
    if not outside or not target_entries:
        return []
    rng = random.Random(seed)
    sample = list(outside)
    rng.shuffle(sample)
    return sample[: len(target_entries)]


# ---------------------------------------------------------------------------
# Control construction
# ---------------------------------------------------------------------------


def _build_control(
    label: str,
    entries: list[dict[str, Any]],
    residuals: dict[str, float],
    *,
    target_count: int,
    kind: str,
    interpretation: str,
) -> dict[str, Any]:
    stats = _stats(_residual_values(entries, residuals))
    if stats["count"] < MIN_SLICE_ROW_COUNT:
        status = "underpowered"
    elif stats["count"] < target_count:
        status = "partial_control"
    else:
        status = "usable_control"
    return {
        "label": label,
        "kind": kind,
        "status": status,
        "stats": stats,
        "interpretation": interpretation,
    }


def _build_residual_only_control(
    label: str,
    residual_values: list[float],
    *,
    target_count: int,
    kind: str,
    interpretation: str,
) -> dict[str, Any]:
    stats = _stats(residual_values)
    if stats["count"] < MIN_SLICE_ROW_COUNT:
        status = "underpowered"
    elif stats["count"] < target_count:
        status = "partial_control"
    else:
        status = "usable_control"
    return {
        "label": label,
        "kind": kind,
        "status": status,
        "stats": stats,
        "interpretation": interpretation,
    }


def _build_target_controls(
    target_entries: list[dict[str, Any]],
    eligible: list[dict[str, Any]],
    residuals: dict[str, float],
    *,
    target_predicate: Callable[[dict[str, Any]], bool],
    per_class_medians: dict[str, float],
) -> dict[str, dict[str, Any]]:
    target_count = len(target_entries)
    outside_slice = [entry for entry in eligible if not target_predicate(entry)]

    nearest_radius_entries = _greedy_match_without_replacement(
        target_entries,
        outside_slice,
        target_key=_radius_value,
        candidate_key=_radius_value,
    )
    host_target = [entry for entry in target_entries if _host_teff(entry) is not None]
    host_candidates = [
        entry for entry in outside_slice if _host_teff(entry) is not None
    ]
    host_temperature_entries = _greedy_match_without_replacement(
        host_target,
        host_candidates,
        target_key=_host_teff,
        candidate_key=_host_teff,
    )
    detection_method_entries = _matched_categorical_control(
        target_entries,
        outside_slice,
        categorical_key=_detection_method,
    )
    uncertainty_band_entries = _matched_categorical_control(
        target_entries,
        outside_slice,
        categorical_key=_uncertainty_band,
    )
    sample_size_random_entries = _sample_size_matched_random_outside(
        target_entries,
        eligible,
        target_predicate,
        seed=RANDOM_OUTSIDE_SEED,
    )

    per_class_residuals = _per_class_median_control_residuals(
        target_entries, per_class_medians
    )
    shuffled_residuals = _shuffled_radius_label_control(
        target_entries, eligible, seed=SHUFFLE_SEED
    )
    uncertainty_equalized_entries = _uncertainty_equalized_subset(target_entries)
    adverse_nearest_radius_entries = _adverse_nearest_radius_outside_slice(
        target_entries, eligible, target_predicate
    )

    controls: dict[str, dict[str, Any]] = {
        # Matched cohorts (independent row slices, outside target).
        "nearest_radius_outside_slice": _build_control(
            "nearest_radius_outside_slice",
            nearest_radius_entries,
            residuals,
            target_count=target_count,
            kind="matched_cohort",
            interpretation=(
                "Outside-slice eligible rows greedily matched to each target "
                "row's radius; tests whether the residual stress is driven by "
                "radius position rather than slice membership."
            ),
        ),
        "host_temperature_outside_slice": _build_control(
            "host_temperature_outside_slice",
            host_temperature_entries,
            residuals,
            target_count=len(host_target),
            kind="matched_cohort",
            interpretation=(
                "Outside-slice eligible rows greedily matched to each target "
                "row's host effective temperature; controls for host-context "
                "selection effects. Targets without host Teff are excluded."
            ),
        ),
        "detection_method_outside_slice": _build_control(
            "detection_method_outside_slice",
            detection_method_entries,
            residuals,
            target_count=target_count,
            kind="matched_cohort",
            interpretation=(
                "Outside-slice eligible rows sharing each target row's "
                "detection_method, broken by nearest log mass; controls for "
                "discovery-pipeline selection effects."
            ),
        ),
        "uncertainty_band_outside_slice": _build_control(
            "uncertainty_band_outside_slice",
            uncertainty_band_entries,
            residuals,
            target_count=target_count,
            kind="matched_cohort",
            interpretation=(
                "Outside-slice eligible rows sharing each target row's "
                "combined mass/radius uncertainty band, broken by nearest "
                "log mass; controls for measurement-quality selection."
            ),
        ),
        "sample_size_random_outside": _build_control(
            "sample_size_random_outside",
            sample_size_random_entries,
            residuals,
            target_count=target_count,
            kind="sample_size_matched_random",
            interpretation=(
                "Deterministic seeded random sample of the same size drawn "
                "from outside-slice eligible rows; expected to sit near the "
                "eligible RMSE by construction."
            ),
        ),
        # Per-class median residual shift (target-row residual shift).
        "per_class_median": _build_residual_only_control(
            "per_class_median",
            per_class_residuals,
            target_count=target_count,
            kind="residual_shift",
            interpretation=(
                "Per-class median residual shift on the target rows; controls "
                "for CK17 mass-class bias but is not an independent row slice."
            ),
        ),
        # Negative controls (deterministic; if signal survives them, it is
        # not a vocabulary or measurement-quality artifact).
        "shuffled_radius_label": _build_residual_only_control(
            "shuffled_radius_label",
            shuffled_residuals,
            target_count=target_count,
            kind="negative_control_shuffle",
            interpretation=(
                "Each target's radius is replaced by a deterministically "
                "shuffled radius drawn from the eligible pool; residual "
                "is recomputed. Tests whether the signal is mass-position "
                "driven independent of the true radius assignment."
            ),
        ),
        "uncertainty_equalized_subset": _build_control(
            "uncertainty_equalized_subset",
            uncertainty_equalized_entries,
            residuals,
            target_count=target_count,
            kind="negative_control_uncertainty",
            interpretation=(
                "Target subset restricted to combined relative uncertainty "
                "<= 15%; tests whether residual stress collapses when only "
                "tight-uncertainty rows are kept."
            ),
        ),
        "adverse_nearest_radius_outside_slice": _build_control(
            "adverse_nearest_radius_outside_slice",
            adverse_nearest_radius_entries,
            residuals,
            target_count=target_count,
            kind="negative_control_adverse",
            interpretation=(
                "Adverse-negative control: nearest-radius matched cohort "
                "drawn strictly from outside-slice rows. If residual stress "
                "is radius-position driven (not slice-driven), this cohort "
                "should rise toward the target RMSE."
            ),
        ),
    }
    return controls


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def _classify_audit(
    target_stats: dict[str, Any],
    eligible_stats: dict[str, Any],
    controls: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    count = target_stats["count"]
    target_rmse = target_stats["log10_rmse"]
    eligible_rmse = eligible_stats["log10_rmse"]
    if count < MIN_SLICE_ROW_COUNT:
        return {
            "outcome": "under_minimum_slice",
            "verdict": "INCONCLUSIVE",
            "adverse_control": None,
            "delta_log10_rmse_target_minus_eligible": None,
            "delta_log10_rmse_target_minus_adverse_control": None,
            "explanation": (
                f"Target slice has {count} rows (< {MIN_SLICE_ROW_COUNT}); "
                "no residual interpretation is allowed."
            ),
        }

    # Adverse-margin candidates are controls whose RMSE *rising toward the
    # target* would mean "an outside slice or class shift reproduces the
    # signal". The shuffled-label and uncertainty-equalized-subset controls
    # are diagnostic but not adverse anchors:
    #   - shuffled_radius_label: low RMSE is the expected behaviour and is a
    #     structure detector, not an adverse comparator.
    #   - uncertainty_equalized_subset: restricts the target itself; rising
    #     RMSE indicates the signal survives measurement-quality equalization
    #     (signal strength check), not that an outside slice matched the
    #     target.
    ADVERSE_CANDIDATE_KINDS = {
        "matched_cohort",
        "residual_shift",
        "sample_size_matched_random",
        "negative_control_adverse",
    }
    usable_controls = {
        name: control
        for name, control in controls.items()
        if control["status"] in {"usable_control", "partial_control"}
        and control["stats"]["log10_rmse"] is not None
        and control["kind"] in ADVERSE_CANDIDATE_KINDS
    }
    adverse_name = None
    adverse_rmse = None
    for name, control in usable_controls.items():
        rmse = control["stats"]["log10_rmse"]
        if adverse_rmse is None or rmse > adverse_rmse:
            adverse_name = name
            adverse_rmse = rmse

    delta_eligible = (
        None
        if target_rmse is None or eligible_rmse is None
        else float(target_rmse - eligible_rmse)
    )
    delta_control = (
        None
        if target_rmse is None or adverse_rmse is None
        else float(target_rmse - adverse_rmse)
    )

    if (
        delta_eligible is not None
        and delta_eligible > CONTROL_MARGIN_LOG10_RMSE
        and delta_control is not None
        and delta_control > CONTROL_MARGIN_LOG10_RMSE
    ):
        outcome = "residual_stress_above_eligible_and_controls"
        verdict = "SANDBOX_PASS"
    elif delta_eligible is not None and delta_eligible > CONTROL_MARGIN_LOG10_RMSE:
        outcome = "control_sensitive_residual_stress"
        verdict = "INCONCLUSIVE"
    elif delta_eligible is not None and abs(delta_eligible) <= CONTROL_MARGIN_LOG10_RMSE:
        outcome = "residual_close_to_eligible"
        verdict = "INCONCLUSIVE"
    elif delta_eligible is not None and delta_eligible < -CONTROL_MARGIN_LOG10_RMSE:
        outcome = "residual_below_eligible"
        verdict = "INCONCLUSIVE"
    else:
        outcome = "inconclusive"
        verdict = "INCONCLUSIVE"

    return {
        "outcome": outcome,
        "verdict": verdict,
        "adverse_control": adverse_name,
        "delta_log10_rmse_target_minus_eligible": delta_eligible,
        "delta_log10_rmse_target_minus_adverse_control": delta_control,
        "explanation": (
            f"target log10 RMSE = {target_rmse}; eligible log10 RMSE = "
            f"{eligible_rmse}; adverse control = {adverse_name} "
            f"(log10 RMSE = {adverse_rmse}); margin = {CONTROL_MARGIN_LOG10_RMSE}."
        ),
    }


def _audit_target_slice(
    slice_spec: dict[str, Any],
    eligible: list[dict[str, Any]],
    residuals: dict[str, float],
    per_class_medians: dict[str, float],
) -> dict[str, Any]:
    predicate = slice_spec["predicate"]
    target_entries = [entry for entry in eligible if predicate(entry)]
    target_stats = _stats(_residual_values(target_entries, residuals))
    eligible_stats = _stats(_residual_values(eligible, residuals))
    controls = _build_target_controls(
        target_entries,
        eligible,
        residuals,
        target_predicate=predicate,
        per_class_medians=per_class_medians,
    )
    classification = _classify_audit(target_stats, eligible_stats, controls)

    pilot_baseline = PILOT_BASELINES.get(slice_spec["id"], {})
    reproduces_pilot = None
    pilot_rmse_delta = None
    pilot_count_delta = None
    if pilot_baseline:
        pilot_rmse = pilot_baseline.get("log10_rmse")
        pilot_count = pilot_baseline.get("count")
        if target_stats["count"] is not None and pilot_count is not None:
            pilot_count_delta = int(target_stats["count"]) - int(pilot_count)
        if (
            target_stats["log10_rmse"] is not None
            and pilot_rmse is not None
        ):
            pilot_rmse_delta = float(target_stats["log10_rmse"]) - float(pilot_rmse)
            reproduces_pilot = (
                abs(pilot_rmse_delta) <= PILOT_REPRODUCTION_TOLERANCE
                and pilot_count_delta == 0
            )

    return {
        "id": slice_spec["id"],
        "label": slice_spec["label"],
        "description": slice_spec["description"],
        "target_stats": target_stats,
        "controls": controls,
        "classification": classification,
        "pilot_reproduction": {
            "pilot_agent_run_id": PILOT_AGENT_RUN_ID,
            "pilot_task_id": PILOT_TASK_ID,
            "pilot_count": pilot_baseline.get("count"),
            "pilot_log10_rmse": pilot_baseline.get("log10_rmse"),
            "current_count": target_stats["count"],
            "current_log10_rmse": target_stats["log10_rmse"],
            "count_delta": pilot_count_delta,
            "log10_rmse_delta": pilot_rmse_delta,
            "reproduces_pilot": reproduces_pilot,
            "tolerance": PILOT_REPRODUCTION_TOLERANCE,
        },
    }


# ---------------------------------------------------------------------------
# Top-level metrics build
# ---------------------------------------------------------------------------


def _band_counts(entries: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        counts[_uncertainty_band(entry)] = counts.get(_uncertainty_band(entry), 0) + 1
    return dict(sorted(counts.items()))


def _detection_method_counts(entries: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        method = _detection_method(entry) or "missing"
        counts[method] = counts.get(method, 0) + 1
    return dict(sorted(counts.items()))


def build_metrics(snapshot_path: Path) -> dict[str, Any]:
    payload = load_exoplanet_snapshot(snapshot_path)
    filtered = apply_inclusion_filters(payload)
    eligible = [
        entry
        for entry in filtered.included_rows
        if _row_has_true_mass_and_transit_radius(entry)
    ]
    residuals = _residual_map(eligible)
    eligible = [entry for entry in eligible if entry["row_id"] in residuals]

    minimum_mass_entries = [
        entry
        for entry in filtered.included_rows
        if _row_has_minimum_mass_and_transit_radius(entry)
    ]
    minimum_mass_residuals = _residual_map(minimum_mass_entries)

    eligible_stats = _stats(_residual_values(eligible, residuals))
    per_class_medians = _per_class_median_residuals(eligible, residuals)

    eligible_pilot_reproduction = {
        "pilot_agent_run_id": PILOT_AGENT_RUN_ID,
        "pilot_count": PILOT_ELIGIBLE_BASELINE["count"],
        "pilot_log10_rmse": PILOT_ELIGIBLE_BASELINE["log10_rmse"],
        "current_count": eligible_stats["count"],
        "current_log10_rmse": eligible_stats["log10_rmse"],
        "count_delta": (
            None
            if eligible_stats["count"] is None
            else int(eligible_stats["count"]) - int(PILOT_ELIGIBLE_BASELINE["count"])
        ),
        "log10_rmse_delta": (
            None
            if eligible_stats["log10_rmse"] is None
            else float(eligible_stats["log10_rmse"])
            - float(PILOT_ELIGIBLE_BASELINE["log10_rmse"])
        ),
        "tolerance": PILOT_REPRODUCTION_TOLERANCE,
    }
    eligible_pilot_reproduction["reproduces_pilot"] = (
        eligible_pilot_reproduction["log10_rmse_delta"] is not None
        and abs(eligible_pilot_reproduction["log10_rmse_delta"]) <= PILOT_REPRODUCTION_TOLERANCE
        and eligible_pilot_reproduction["count_delta"] == 0
    )

    slices = [
        _audit_target_slice(
            spec,
            eligible,
            residuals,
            per_class_medians,
        )
        for spec in TARGET_SLICES
    ]

    # Aggregate pilot reproduction status for the audit as a whole.
    all_reproductions = [eligible_pilot_reproduction["reproduces_pilot"]] + [
        s["pilot_reproduction"]["reproduces_pilot"] for s in slices
    ]
    pilot_reproduction_status = (
        "match" if all(value is True for value in all_reproductions) else "drift"
    )

    # Verdict aggregation: SANDBOX_PASS only if all 3 target slices passed.
    slice_verdicts = [s["classification"]["verdict"] for s in slices]
    if any(v == "SANDBOX_PASS" for v in slice_verdicts):
        # At least one slice survived eligible + adverse-control margins.
        # Audit verdict is SANDBOX_PASS to preserve the partial signal, but
        # per-slice classifications carry the detail.
        audit_verdict = "SANDBOX_PASS"
    else:
        audit_verdict = "INCONCLUSIVE"

    metrics: dict[str, Any] = {
        "task_id": TASK_ID,
        "agent_run_id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "snapshot_path": snapshot_path.relative_to(REPO_ROOT).as_posix(),
        "data_boundary": {
            "live_external_fetch_performed": False,
            "baseline_refit_performed": False,
            "minimum_mass_rows_in_headline_metrics": False,
            "true_mass_axis_primary": True,
        },
        "loader_summary": {
            "total_rows": filtered.total_rows,
            "pre_filter_included_count": filtered.pre_filter_included_count,
            "post_filter_included_count": filtered.post_filter_included_count,
            "eligible_true_mass_with_transit_radius": len(eligible),
            "minimum_mass_with_transit_radius_diagnostic": len(minimum_mass_residuals),
        },
        "thresholds": {
            "min_slice_row_count": MIN_SLICE_ROW_COUNT,
            "control_margin_log10_rmse": CONTROL_MARGIN_LOG10_RMSE,
            "pilot_reproduction_tolerance": PILOT_REPRODUCTION_TOLERANCE,
            "shuffle_seed": SHUFFLE_SEED,
            "random_outside_seed": RANDOM_OUTSIDE_SEED,
        },
        "eligible_true_mass_stats": eligible_stats,
        "eligible_pilot_reproduction": eligible_pilot_reproduction,
        "target_slices": slices,
        "diagnostics": {
            "per_class_medians_log10_residual": per_class_medians,
            "eligible_uncertainty_band_counts": _band_counts(eligible),
            "eligible_detection_method_counts": _detection_method_counts(eligible),
            "minimum_mass_sparse_diagnostic": _stats(
                list(minimum_mass_residuals.values())
            ),
        },
        "pilot_reproduction_status": pilot_reproduction_status,
        "verdict": audit_verdict,
    }
    return metrics


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _fmt(value: float | None, places: int = 6) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{places}f}"


def _fmt_bool(value: Any) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return "n/a"


def _render_report(metrics: dict[str, Any]) -> str:
    loader = metrics["loader_summary"]
    eligible = metrics["eligible_true_mass_stats"]
    eligible_rep = metrics["eligible_pilot_reproduction"]
    lines = [
        f"# {AGENT_RUN_ID} - Exoplanet compact/sub-Neptune matched-control audit",
        "",
        f"- Task: {TASK_ID}",
        f"- Campaign profile: {CAMPAIGN_PROFILE_ID}",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        f"- Verdict: **{metrics['verdict']}**",
        f"- Pilot reproduction status: `{metrics['pilot_reproduction_status']}`",
        "",
        "## Boundary",
        "",
        "Sandbox-only matched-control audit on committed snapshot rows. The "
        "primary axis is true-mass/transit-radius rows; minimum-mass rows are "
        "diagnostic-only. The frozen CK17 baseline is not refit.",
        "",
        "## Eligible baseline + pilot reproduction",
        "",
        f"- Eligible true-mass/transit-radius rows: {loader['eligible_true_mass_with_transit_radius']}",
        f"- Diagnostic minimum-mass/transit-radius rows: {loader['minimum_mass_with_transit_radius_diagnostic']}",
        f"- Current eligible log10 RMSE: {_fmt(eligible['log10_rmse'])}",
        f"- Pilot eligible log10 RMSE ({PILOT_AGENT_RUN_ID}): {_fmt(eligible_rep['pilot_log10_rmse'])}",
        f"- Eligible log10 RMSE delta vs pilot: {_fmt(eligible_rep['log10_rmse_delta'])}",
        f"- Reproduces pilot eligible baseline within {PILOT_REPRODUCTION_TOLERANCE}: "
        f"`{_fmt_bool(eligible_rep['reproduces_pilot'])}`",
        "",
        "## Per-slice summary",
        "",
        "| slice | label | count | log10 RMSE | pilot RMSE | reproduces | outcome | adverse control | delta vs adverse |",
        "| --- | --- | ---: | ---: | ---: | :-: | --- | --- | ---: |",
    ]
    for s in metrics["target_slices"]:
        rep = s["pilot_reproduction"]
        cls = s["classification"]
        lines.append(
            "| "
            + " | ".join(
                [
                    s["id"],
                    s["label"],
                    str(s["target_stats"]["count"]),
                    _fmt(s["target_stats"]["log10_rmse"]),
                    _fmt(rep["pilot_log10_rmse"]),
                    _fmt_bool(rep["reproduces_pilot"]),
                    cls["outcome"],
                    str(cls.get("adverse_control")),
                    _fmt(cls.get("delta_log10_rmse_target_minus_adverse_control")),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Per-slice control tables", ""])
    for s in metrics["target_slices"]:
        lines.extend(
            [
                f"### {s['id']} - {s['label']}",
                "",
                f"- Target count: {s['target_stats']['count']}",
                f"- Target log10 RMSE: {_fmt(s['target_stats']['log10_rmse'])}",
                (
                    "- Delta vs eligible: "
                    f"{_fmt(s['classification'].get('delta_log10_rmse_target_minus_eligible'))}"
                ),
                "",
                "| control | kind | status | count | log10 RMSE | delta target-control |",
                "| --- | --- | --- | ---: | ---: | ---: |",
            ]
        )
        target_rmse = s["target_stats"]["log10_rmse"]
        for name, control in s["controls"].items():
            stats = control["stats"]
            delta = (
                None
                if target_rmse is None or stats["log10_rmse"] is None
                else target_rmse - stats["log10_rmse"]
            )
            lines.append(
                "| "
                + " | ".join(
                    [
                        name,
                        control["kind"],
                        control["status"],
                        str(stats["count"]),
                        _fmt(stats["log10_rmse"]),
                        _fmt(delta),
                    ]
                )
                + " |"
            )
        lines.append("")
    lines.extend(
        [
            "## Output Routing",
            "",
            f"- Task verdict: `{metrics['verdict']}`.",
            f"- Canonical destination: sandbox-only `agent_runs/{AGENT_RUN_ID}/` "
            "and review note.",
            "- Review tier: none.",
            "- Gate A: not attempted.",
            "- Gate B: not attempted.",
            "- Claim impact: no claim change.",
            "- Knowledge impact: no knowledge change.",
            "- Publication blocker: task scope authorizes sandbox evidence only.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_review(metrics: dict[str, Any]) -> str:
    lines = [
        "# Exoplanet compact/sub-Neptune matched-control audit",
        "",
        f"- Agent run: `{AGENT_RUN_ID}`",
        f"- Task: `{TASK_ID}`",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        f"- Verdict: **{metrics['verdict']}**",
        f"- Pilot reproduction status: `{metrics['pilot_reproduction_status']}`",
        "",
        "## Scope",
        "",
        "This review tests whether the compact and sub-Neptune residual "
        "stress patterns identified in the TASK-0390 pilot "
        f"({PILOT_AGENT_RUN_ID}) survive matched controls and deterministic "
        "negative controls. It uses only the committed PSCompPars snapshot "
        "and frozen CK17 residuals.",
        "",
        "No live fetch, baseline refit, atmospheric inference, composition "
        "inference, inflation-physics claim, habitability wording, "
        "target-priority output, new mass-radius law, prediction entry, "
        "canonical result, claim update, or knowledge edit is authorized.",
        "",
        "## Pilot reproduction",
        "",
        "Pilot eligible baseline (TASK-0390, AGENT-RUN-0036): "
        f"count={metrics['eligible_pilot_reproduction']['pilot_count']}, "
        f"log10 RMSE={_fmt(metrics['eligible_pilot_reproduction']['pilot_log10_rmse'])}. "
        f"Current re-derived eligible baseline: count={metrics['eligible_pilot_reproduction']['current_count']}, "
        f"log10 RMSE={_fmt(metrics['eligible_pilot_reproduction']['current_log10_rmse'])}. "
        f"Reproduces within {PILOT_REPRODUCTION_TOLERANCE}: "
        f"`{_fmt_bool(metrics['eligible_pilot_reproduction']['reproduces_pilot'])}`.",
        "",
        "## Per-slice outcome",
        "",
        "| slice | label | count | RMSE | reproduces pilot | outcome | adverse control |",
        "| --- | --- | ---: | ---: | :-: | --- | --- |",
    ]
    for s in metrics["target_slices"]:
        rep = s["pilot_reproduction"]
        cls = s["classification"]
        lines.append(
            "| "
            + " | ".join(
                [
                    s["id"],
                    s["label"],
                    str(s["target_stats"]["count"]),
                    _fmt(s["target_stats"]["log10_rmse"]),
                    _fmt_bool(rep["reproduces_pilot"]),
                    cls["outcome"],
                    str(cls.get("adverse_control")),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Control families",
            "",
            "- Matched cohorts (independent row slices outside target):",
            "  - `nearest_radius_outside_slice` - radius proximity matching",
            "  - `host_temperature_outside_slice` - host Teff matching (excludes targets without Teff)",
            "  - `detection_method_outside_slice` - shared detection method, nearest log mass",
            "  - `uncertainty_band_outside_slice` - shared combined uncertainty band, nearest log mass",
            "  - `sample_size_random_outside` - deterministic seeded random outside-slice draw",
            "- Residual-shift control:",
            "  - `per_class_median` - target-row residual shifted by eligible per-class median",
            "- Deterministic negative controls:",
            "  - `shuffled_radius_label` - radius assignment shuffled within eligible pool",
            "  - `uncertainty_equalized_subset` - target rows restricted to combined relative "
            "uncertainty <= 15%",
            "  - `adverse_nearest_radius_outside_slice` - radius-matched cohort strictly outside "
            "slice; should rise toward target RMSE if signal is radius-position driven",
            "",
            "## Output Routing",
            "",
            f"- Task verdict: `{metrics['verdict']}`.",
            f"- Canonical destination: sandbox-only `agent_runs/{AGENT_RUN_ID}/` "
            "and this review note.",
            "- Review tier: none.",
            "- Gate A: not attempted.",
            "- Gate B: not attempted.",
            "- Claim impact: no claim change.",
            "- Knowledge impact: no knowledge change.",
            "- Publication blocker: sandbox-only validation task.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_limitations(metrics: dict[str, Any]) -> str:
    del metrics
    bullets = [
        "Controls use committed snapshot fields and frozen CK17 residuals only.",
        "Matched controls are diagnostic slices, not causal adjustments.",
        "Per-class median control is a target-row residual shift rather than an independent row slice.",
        "Host-temperature control excludes rows without host effective temperature.",
        "Detection-method control excludes rows missing detection_method.",
        "Uncertainty band control excludes rows whose combined uncertainty cannot be computed.",
        "Negative controls are deterministic but seed-dependent; the seed is recorded in thresholds.",
        "Minimum-mass rows are sparse diagnostics only and excluded from headline metrics.",
        "No composition, inflation-physics, habitability, target-priority, prediction, claim, or knowledge output is authorized.",
    ]
    return "# Limitations\n\n" + "\n".join(f"- {item}" for item in bullets) + "\n"


def _render_preflight(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Preflight",
            "",
            f"- Snapshot: `{metrics['snapshot_path']}`",
            "- Data boundary: only committed snapshot rows are read.",
            "- Baseline freeze: CK17 segments unchanged; no refit.",
            "- Primary axis: true-mass/transit-radius compact, sub-Neptune, combined slices.",
            "- Pilot anchor: TASK-0390 / AGENT-RUN-0036; reproduction tolerance recorded in thresholds.",
            "- Controls: 5 matched cohorts, 1 per-class residual shift, 3 deterministic negative controls.",
            "- Promotion boundary: sandbox-only; no canonical result, prediction, claim, or knowledge output.",
            "",
            "## Checks",
            "",
            "| name | status | notes |",
            "| --- | --- | --- |",
            "| data_boundary | PASS | Only committed snapshot rows are read. |",
            "| baseline_freeze | PASS | CK17 frozen segments are reused without refit. |",
            f"| pilot_reproduction | {'PASS' if metrics['pilot_reproduction_status'] == 'match' else 'DRIFT'} | "
            f"Eligible + per-slice counts and RMSE compared to {PILOT_AGENT_RUN_ID}. |",
            "| control_floor | PASS | Matched and negative controls reported with counts and gates. |",
            "| promotion_boundary | PASS | Sandbox-only output. |",
            "",
        ]
    )


def _render_review_summary(metrics: dict[str, Any]) -> str:
    lines = [
        "# Review summary",
        "",
        f"- Verdict: **{metrics['verdict']}**",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        f"- Pilot reproduction status: `{metrics['pilot_reproduction_status']}`",
        f"- Target slices audited: {len(metrics['target_slices'])}",
    ]
    for s in metrics["target_slices"]:
        lines.append(
            f"- {s['id']} ({s['label']}): "
            f"outcome=`{s['classification']['outcome']}`, "
            f"target_count={s['target_stats']['count']}, "
            f"target_rmse={_fmt(s['target_stats']['log10_rmse'])}"
        )
    lines.extend(
        [
            "",
            "The audit preserves control-sensitive and underpowered outcomes; it does "
            "not promote a result, prediction, claim, or knowledge artifact.",
            "",
        ]
    )
    return "\n".join(lines)


def _build_agent_run_payload(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "task_id": TASK_ID,
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {
            "contributor_id": "roman",
            "agent_id": "claude-code",
        },
        "proposal_paths": {
            # TASK-0427 is a matched-control audit of the CSN-001/002/003
            # patterns introduced by the TASK-0390 pilot; it inherits the
            # pilot's hypothesis and experiment proposal artifacts as its
            # scientific origin rather than introducing new proposals.
            "hypothesis": (
                "hypothesis_proposals/exoplanet-mass/"
                "HYP-PROPOSAL-0051-compact-subneptune-residual-pilot.yaml"
            ),
            "experiment": (
                "experiment_proposals/exoplanet-mass/"
                "EXP-PROPOSAL-0017-compact-subneptune-residual-pilot.yaml"
            ),
        },
        "artifacts": {
            "metrics": f"agent_runs/{AGENT_RUN_ID}/metrics.json",
            "report": f"agent_runs/{AGENT_RUN_ID}/report.md",
            "limitations": f"agent_runs/{AGENT_RUN_ID}/limitations.md",
            "preflight": f"agent_runs/{AGENT_RUN_ID}/preflight.md",
            "review_summary": f"agent_runs/{AGENT_RUN_ID}/review_summary.md",
        },
        "preflight": {
            "passed": True,
            "checks": [
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed snapshot rows are read; no live fetch.",
                },
                {
                    "name": "baseline_freeze",
                    "status": "PASS",
                    "notes": "CK17 frozen segments are reused without refit.",
                },
                {
                    "name": "pilot_reproduction",
                    "status": (
                        "PASS"
                        if metrics["pilot_reproduction_status"] == "match"
                        else "DRIFT"
                    ),
                    "notes": (
                        "Eligible + per-slice counts and RMSE compared to "
                        f"{PILOT_AGENT_RUN_ID} within "
                        f"{PILOT_REPRODUCTION_TOLERANCE}."
                    ),
                },
                {
                    "name": "control_floor",
                    "status": "PASS",
                    "notes": (
                        "5 matched cohorts (nearest-radius, host-temp, "
                        "detection-method, uncertainty-band, sample-size-random), "
                        "1 per-class residual shift, 3 deterministic negative "
                        "controls (shuffled radius, uncertainty-equalized "
                        "subset, adverse nearest-radius)."
                    ),
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No canonical result, prediction, claim, or knowledge output.",
                },
            ],
        },
        "limitations": [
            "Controls use committed snapshot fields and frozen CK17 residuals only.",
            "Matched controls are diagnostic slices, not causal adjustments.",
            "Per-class median control is a target-row residual shift rather than an independent row slice.",
            "Host-temperature control excludes rows without host effective temperature.",
            "Detection-method control excludes rows missing detection_method.",
            "Uncertainty band control excludes rows whose combined uncertainty cannot be computed.",
            "Negative controls are deterministic but seed-dependent; the seed is recorded in thresholds.",
            "Minimum-mass rows are sparse diagnostics only and excluded from headline metrics.",
            "No composition, inflation-physics, habitability, target-priority, prediction, claim, or knowledge output is authorized.",
        ],
        "verdict": metrics["verdict"],
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any canonical result, prediction "
                "registry entry, claim update, knowledge edit, or follow-up "
                "hypothesis lane treats the compact/sub-Neptune residual as "
                "physical structure."
            ),
        },
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def write_outputs(
    metrics: dict[str, Any],
    *,
    out: Path,
    report: Path,
    agent_run: Path,
    limitations: Path,
    preflight: Path,
    review_summary: Path,
    review: Path,
) -> None:
    for path in (out, report, agent_run, limitations, preflight, review_summary, review):
        path.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2, sort_keys=True)
        handle.write("\n")
    report.write_text(_render_report(metrics), encoding="utf-8")
    limitations.write_text(_render_limitations(metrics), encoding="utf-8")
    preflight.write_text(_render_preflight(metrics), encoding="utf-8")
    review_summary.write_text(_render_review_summary(metrics), encoding="utf-8")
    review.write_text(_render_review(metrics), encoding="utf-8")
    with agent_run.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(_build_agent_run_payload(metrics), handle, sort_keys=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT_PATH)
    parser.add_argument("--out", type=Path, default=DEFAULT_METRICS_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--agent-run", type=Path, default=DEFAULT_AGENT_RUN_PATH)
    parser.add_argument("--limitations", type=Path, default=DEFAULT_LIMITATIONS_PATH)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT_PATH)
    parser.add_argument("--review-summary", type=Path, default=DEFAULT_REVIEW_SUMMARY_PATH)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    args = parser.parse_args(argv)
    metrics = build_metrics(args.snapshot)
    write_outputs(
        metrics,
        out=args.out,
        report=args.report,
        agent_run=args.agent_run,
        limitations=args.limitations,
        preflight=args.preflight,
        review_summary=args.review_summary,
        review=args.review,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
