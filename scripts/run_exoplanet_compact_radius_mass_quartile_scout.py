"""TASK-0480 exoplanet compact-radius mass-quartile scout.

Sandbox-only diagnostic that asks one narrow question about the strongest
current exoplanet benchmark survivor: is the compact-radius residual stress
(slice CSN-001, R/Re < 1.5, the only matched-control survivor in
AGENT-RUN-0042 / TASK-0427) concentrated in a *mass subrange*, or is it
spread across the slice?

To avoid post-hoc bin gerrymandering, the partition *rules* are predeclared
in ``PARTITION_SPECS`` before any residual metric is computed. The bin edges
themselves are derived deterministically from the mass-sorted compact slice:

- primary partition ``mass_quartile``: 4 equal-count contiguous bins by
  ascending true mass (Q1..Q4);
- fallback partition ``mass_half``: 2 equal-count contiguous bins by
  ascending true mass (H1, H2).

The compact slice has ~92 eligible rows on the committed snapshot, so the
quartile bins (~23 rows each) fall below the 30-row interpretation floor
inherited from the matched-control audit. The quartile resolution is
therefore expected to be underpowered; the coarser mass-half partition is
reported as a supporting diagnostic only. The headline verdict is driven by
the predeclared primary (quartile) partition.

Each interpreted bin is compared against:

- a per-class median residual-shift control (controls for CK17 mass-class
  bias on the bin's own rows);
- matched outside-compact cohorts (nearest radius and nearest log mass drawn
  strictly from eligible rows with R/Re >= 1.5);
- a deterministic seeded same-size random draw from outside-compact rows.

No live fetch, baseline refit, composition / habitability / target-priority
/ atmospheric inference, new mass-radius law, prediction entry, canonical
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

AGENT_RUN_ID = "AGENT-RUN-0049"
TASK_ID = "TASK-0480"
CAMPAIGN_PROFILE_ID = "exoplanet-mass-radius"

# Source slice anchor. CSN-001 is the compact-radius matched-control survivor
# from TASK-0427 / AGENT-RUN-0042 (which in turn reproduces the TASK-0390 /
# AGENT-RUN-0036 pilot). The scout reproduces this compact-slice baseline as a
# data-path sanity check before partitioning it by mass.
SOURCE_SLICE_ID = "CSN-001"
SOURCE_AGENT_RUN_ID = "AGENT-RUN-0042"
SOURCE_TASK_ID = "TASK-0427"
COMPACT_SLICE_BASELINE: dict[str, Any] = {
    "count": 92,
    "log10_rmse": 0.26335002767665594,
}
ELIGIBLE_BASELINE: dict[str, Any] = {
    "count": 1207,
    "log10_rmse": 0.15817019267448623,
}
REPRODUCTION_TOLERANCE: float = 1.0e-9

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
    REPO_ROOT / "docs" / "reviews" / "exoplanet-compact-radius-mass-quartile-scout.md"
)

# Interpretation floor: a bin with fewer rows is reported but not interpreted.
# Mirrors the matched-control audit (TASK-0427) so the scout uses the same
# row-count discipline.
MIN_BIN_ROW_COUNT: int = 30
CONTROL_MARGIN_LOG10_RMSE: float = 0.022
RANDOM_OUTSIDE_SEED: int = 20260530


# ---------------------------------------------------------------------------
# Predeclared partition rules (declared before any metric is computed).
# ---------------------------------------------------------------------------

PARTITION_SPECS: list[dict[str, Any]] = [
    {
        "id": "mass_quartile",
        "role": "primary",
        "n_bins": 4,
        "bin_prefix": "Q",
        "description": (
            "Predeclared primary partition: 4 equal-count contiguous bins of "
            "the compact slice ordered by ascending true mass. Headline scout "
            "question (mass-subrange localization) is decided on this partition."
        ),
    },
    {
        "id": "mass_half",
        "role": "fallback_diagnostic",
        "n_bins": 2,
        "bin_prefix": "H",
        "description": (
            "Predeclared coarse fallback partition: 2 equal-count contiguous "
            "bins by ascending true mass. Reported as a supporting diagnostic "
            "when the quartile resolution is underpowered; does not drive the "
            "headline verdict."
        ),
    },
]


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


def _mass_value(entry: dict[str, Any]) -> float:
    return float(entry["mass"]["value"])


def _radius_value(entry: dict[str, Any]) -> float:
    return float(entry["radius"]["value"])


def _is_compact(entry: dict[str, Any]) -> bool:
    """Compact-radius slice predicate (R/Re < 1.5), matching CSN-001."""

    return _radius_value(entry) < 1.5


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
        by_class.setdefault(planet_class_for_mass(_mass_value(entry)), []).append(
            residual
        )
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
# Matching helpers (deterministic, no replacement)
# ---------------------------------------------------------------------------


def _greedy_match_without_replacement(
    target_entries: list[dict[str, Any]],
    candidate_entries: list[dict[str, Any]],
    target_key: Callable[[dict[str, Any]], float | None],
    candidate_key: Callable[[dict[str, Any]], float | None],
) -> list[dict[str, Any]]:
    """Match each target to the nearest available candidate for a scalar key."""

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


def _sample_size_matched_random_outside(
    target_entries: list[dict[str, Any]],
    outside_entries: list[dict[str, Any]],
    *,
    seed: int,
) -> list[dict[str, Any]]:
    """Deterministic same-size random draw from the outside-compact pool."""

    if not outside_entries or not target_entries:
        return []
    rng = random.Random(seed)
    sample = list(outside_entries)
    rng.shuffle(sample)
    return sample[: len(target_entries)]


def _log_mass(entry: dict[str, Any]) -> float:
    return math.log10(_mass_value(entry))


# ---------------------------------------------------------------------------
# Predeclared partitioning
# ---------------------------------------------------------------------------


def _contiguous_equal_count_bins(
    sorted_entries: list[dict[str, Any]], n_bins: int
) -> list[list[dict[str, Any]]]:
    """Split mass-sorted rows into ``n_bins`` contiguous equal-count chunks.

    Deterministic: chunk boundaries use integer index arithmetic, so the
    split does not depend on tie-breaking at a quantile value.
    """

    total = len(sorted_entries)
    bins: list[list[dict[str, Any]]] = []
    for k in range(n_bins):
        start = k * total // n_bins
        end = (k + 1) * total // n_bins
        bins.append(sorted_entries[start:end])
    return bins


def _bin_mass_edges(entries: list[dict[str, Any]]) -> dict[str, float | None]:
    masses = [_mass_value(entry) for entry in entries]
    if not masses:
        return {"mass_min_mearth": None, "mass_max_mearth": None}
    return {"mass_min_mearth": min(masses), "mass_max_mearth": max(masses)}


# ---------------------------------------------------------------------------
# Control construction
# ---------------------------------------------------------------------------


def _build_entry_control(
    label: str,
    entries: list[dict[str, Any]],
    residuals: dict[str, float],
    *,
    target_count: int,
    kind: str,
    interpretation: str,
) -> dict[str, Any]:
    stats = _stats(_residual_values(entries, residuals))
    return {
        "label": label,
        "kind": kind,
        "status": _control_status(stats["count"], target_count),
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
    return {
        "label": label,
        "kind": kind,
        "status": _control_status(stats["count"], target_count),
        "stats": stats,
        "interpretation": interpretation,
    }


def _control_status(count: int, target_count: int) -> str:
    if count < MIN_BIN_ROW_COUNT:
        return "underpowered"
    if count < target_count:
        return "partial_control"
    return "usable_control"


def _build_bin_controls(
    bin_entries: list[dict[str, Any]],
    outside_compact: list[dict[str, Any]],
    residuals: dict[str, float],
    per_class_medians: dict[str, float],
) -> dict[str, dict[str, Any]]:
    target_count = len(bin_entries)

    nearest_radius_entries = _greedy_match_without_replacement(
        bin_entries,
        outside_compact,
        target_key=_radius_value,
        candidate_key=_radius_value,
    )
    nearest_mass_entries = _greedy_match_without_replacement(
        bin_entries,
        outside_compact,
        target_key=_log_mass,
        candidate_key=_log_mass,
    )
    sample_size_random_entries = _sample_size_matched_random_outside(
        bin_entries, outside_compact, seed=RANDOM_OUTSIDE_SEED
    )
    per_class_residuals = _per_class_median_control_residuals(
        bin_entries, per_class_medians
    )

    return {
        "per_class_median": _build_residual_only_control(
            "per_class_median",
            per_class_residuals,
            target_count=target_count,
            kind="residual_shift",
            interpretation=(
                "Per-class median residual shift on the bin's own rows; "
                "controls for CK17 mass-class bias but is not an independent "
                "row slice."
            ),
        ),
        "nearest_radius_outside_compact": _build_entry_control(
            "nearest_radius_outside_compact",
            nearest_radius_entries,
            residuals,
            target_count=target_count,
            kind="matched_cohort",
            interpretation=(
                "Eligible rows with R/Re >= 1.5 greedily matched to each bin "
                "row's radius; tests whether the residual stress is driven by "
                "radius position rather than compact-slice membership."
            ),
        ),
        "nearest_mass_outside_compact": _build_entry_control(
            "nearest_mass_outside_compact",
            nearest_mass_entries,
            residuals,
            target_count=target_count,
            kind="matched_cohort",
            interpretation=(
                "Eligible rows with R/Re >= 1.5 greedily matched to each bin "
                "row's log mass; if the bin's residual stress is mass-position "
                "driven, this cohort should rise toward the bin RMSE."
            ),
        ),
        "sample_size_random_outside_compact": _build_entry_control(
            "sample_size_random_outside_compact",
            sample_size_random_entries,
            residuals,
            target_count=target_count,
            kind="sample_size_matched_random",
            interpretation=(
                "Deterministic seeded same-size random draw from eligible rows "
                "with R/Re >= 1.5; expected to sit near the eligible RMSE by "
                "construction."
            ),
        ),
    }


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

ADVERSE_CANDIDATE_KINDS = {
    "matched_cohort",
    "residual_shift",
    "sample_size_matched_random",
}


def _classify_bin(
    bin_stats: dict[str, Any],
    eligible_stats: dict[str, Any],
    controls: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    count = bin_stats["count"]
    bin_rmse = bin_stats["log10_rmse"]
    eligible_rmse = eligible_stats["log10_rmse"]

    if count < MIN_BIN_ROW_COUNT:
        return {
            "interpretable": False,
            "outcome": "under_minimum_bin",
            "verdict": "INCONCLUSIVE",
            "adverse_control": None,
            "delta_log10_rmse_bin_minus_eligible": (
                None
                if bin_rmse is None or eligible_rmse is None
                else float(bin_rmse - eligible_rmse)
            ),
            "delta_log10_rmse_bin_minus_adverse_control": None,
            "explanation": (
                f"Bin has {count} rows (< {MIN_BIN_ROW_COUNT}); no residual "
                "interpretation is allowed at this resolution."
            ),
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
        if bin_rmse is None or eligible_rmse is None
        else float(bin_rmse - eligible_rmse)
    )
    delta_control = (
        None
        if bin_rmse is None or adverse_rmse is None
        else float(bin_rmse - adverse_rmse)
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
        "interpretable": True,
        "outcome": outcome,
        "verdict": verdict,
        "adverse_control": adverse_name,
        "delta_log10_rmse_bin_minus_eligible": delta_eligible,
        "delta_log10_rmse_bin_minus_adverse_control": delta_control,
        "explanation": (
            f"bin log10 RMSE = {bin_rmse}; eligible log10 RMSE = {eligible_rmse}; "
            f"adverse control = {adverse_name} (log10 RMSE = {adverse_rmse}); "
            f"margin = {CONTROL_MARGIN_LOG10_RMSE}."
        ),
    }


# ---------------------------------------------------------------------------
# Partition audit
# ---------------------------------------------------------------------------


def _audit_partition(
    spec: dict[str, Any],
    compact_sorted: list[dict[str, Any]],
    outside_compact: list[dict[str, Any]],
    residuals: dict[str, float],
    eligible_stats: dict[str, Any],
    compact_stats: dict[str, Any],
    per_class_medians: dict[str, float],
) -> dict[str, Any]:
    n_bins = spec["n_bins"]
    bins = _contiguous_equal_count_bins(compact_sorted, n_bins)
    compact_rmse = compact_stats["log10_rmse"]

    bin_payloads: list[dict[str, Any]] = []
    for index, bin_entries in enumerate(bins, start=1):
        bin_id = f"{spec['bin_prefix']}{index}"
        bin_stats = _stats(_residual_values(bin_entries, residuals))
        controls = _build_bin_controls(
            bin_entries, outside_compact, residuals, per_class_medians
        )
        classification = _classify_bin(bin_stats, eligible_stats, controls)
        delta_compact = (
            None
            if bin_stats["log10_rmse"] is None or compact_rmse is None
            else float(bin_stats["log10_rmse"] - compact_rmse)
        )
        bin_payloads.append(
            {
                "bin_id": bin_id,
                "mass_edges": _bin_mass_edges(bin_entries),
                "uncertainty_band_counts": _band_counts(bin_entries),
                "bin_stats": bin_stats,
                "delta_log10_rmse_bin_minus_compact_slice": delta_compact,
                "controls": controls,
                "classification": classification,
            }
        )

    interpretable = [b for b in bin_payloads if b["classification"]["interpretable"]]
    survivors = [
        b
        for b in interpretable
        if b["classification"]["verdict"] == "SANDBOX_PASS"
    ]
    if not interpretable:
        partition_outcome = "underpowered_no_interpretable_bin"
    elif survivors:
        partition_outcome = "localized_residual_stress_in_subrange"
    else:
        partition_outcome = "no_localized_subrange_above_controls"

    return {
        "id": spec["id"],
        "role": spec["role"],
        "n_bins": n_bins,
        "description": spec["description"],
        "bins": bin_payloads,
        "interpretable_bin_count": len(interpretable),
        "survivor_bin_ids": [b["bin_id"] for b in survivors],
        "partition_outcome": partition_outcome,
    }


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


def _band_counts(entries: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        band = _uncertainty_band(entry)
        counts[band] = counts.get(band, 0) + 1
    return dict(sorted(counts.items()))


def _reproduction_block(
    label: str, baseline: dict[str, Any], stats: dict[str, Any]
) -> dict[str, Any]:
    count_delta = (
        None
        if stats["count"] is None
        else int(stats["count"]) - int(baseline["count"])
    )
    rmse_delta = (
        None
        if stats["log10_rmse"] is None
        else float(stats["log10_rmse"]) - float(baseline["log10_rmse"])
    )
    reproduces = (
        rmse_delta is not None
        and abs(rmse_delta) <= REPRODUCTION_TOLERANCE
        and count_delta == 0
    )
    return {
        "anchor": label,
        "anchor_count": baseline["count"],
        "anchor_log10_rmse": baseline["log10_rmse"],
        "current_count": stats["count"],
        "current_log10_rmse": stats["log10_rmse"],
        "count_delta": count_delta,
        "log10_rmse_delta": rmse_delta,
        "reproduces_anchor": reproduces,
        "tolerance": REPRODUCTION_TOLERANCE,
    }


# ---------------------------------------------------------------------------
# Top-level metrics build
# ---------------------------------------------------------------------------


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

    eligible_stats = _stats(_residual_values(eligible, residuals))
    per_class_medians = _per_class_median_residuals(eligible, residuals)

    compact = [entry for entry in eligible if _is_compact(entry)]
    outside_compact = [entry for entry in eligible if not _is_compact(entry)]
    compact_stats = _stats(_residual_values(compact, residuals))

    # Deterministic mass ordering for the predeclared contiguous partitions.
    compact_sorted = sorted(compact, key=lambda entry: (_log_mass(entry), entry["row_id"]))

    eligible_reproduction = _reproduction_block(
        "eligible_true_mass", ELIGIBLE_BASELINE, eligible_stats
    )
    compact_reproduction = _reproduction_block(
        f"{SOURCE_SLICE_ID}_compact_slice", COMPACT_SLICE_BASELINE, compact_stats
    )

    partitions = [
        _audit_partition(
            spec,
            compact_sorted,
            outside_compact,
            residuals,
            eligible_stats,
            compact_stats,
            per_class_medians,
        )
        for spec in PARTITION_SPECS
    ]

    primary = next(p for p in partitions if p["role"] == "primary")

    # The headline verdict is driven by the predeclared primary (quartile)
    # partition only. Underpowered quartiles -> INCONCLUSIVE regardless of the
    # coarser fallback diagnostic.
    if primary["interpretable_bin_count"] == 0:
        scout_outcome = "compact_slice_underpowered_for_mass_quartile_localization"
        verdict = "INCONCLUSIVE"
    elif primary["survivor_bin_ids"]:
        scout_outcome = "compact_residual_stress_localized_to_mass_subrange"
        verdict = "SANDBOX_PASS"
    else:
        scout_outcome = "compact_residual_stress_not_localized_to_mass_subrange"
        verdict = "INCONCLUSIVE"

    reproduction_status = (
        "match"
        if eligible_reproduction["reproduces_anchor"]
        and compact_reproduction["reproduces_anchor"]
        else "drift"
    )

    return {
        "task_id": TASK_ID,
        "agent_run_id": AGENT_RUN_ID,
        "campaign_profile_id": CAMPAIGN_PROFILE_ID,
        "snapshot_path": snapshot_path.relative_to(REPO_ROOT).as_posix(),
        "source_slice": {
            "id": SOURCE_SLICE_ID,
            "source_agent_run_id": SOURCE_AGENT_RUN_ID,
            "source_task_id": SOURCE_TASK_ID,
            "definition": "compact true-mass/transit-radius rows with R/Re < 1.5",
        },
        "data_boundary": {
            "live_external_fetch_performed": False,
            "baseline_refit_performed": False,
            "true_mass_axis_primary": True,
            "minimum_mass_rows_in_headline_metrics": False,
            "bins_predeclared_before_metrics": True,
        },
        "loader_summary": {
            "total_rows": filtered.total_rows,
            "pre_filter_included_count": filtered.pre_filter_included_count,
            "post_filter_included_count": filtered.post_filter_included_count,
            "eligible_true_mass_with_transit_radius": len(eligible),
            "compact_slice_count": len(compact),
            "outside_compact_count": len(outside_compact),
        },
        "thresholds": {
            "min_bin_row_count": MIN_BIN_ROW_COUNT,
            "control_margin_log10_rmse": CONTROL_MARGIN_LOG10_RMSE,
            "reproduction_tolerance": REPRODUCTION_TOLERANCE,
            "random_outside_seed": RANDOM_OUTSIDE_SEED,
            "compact_radius_threshold_rearth": 1.5,
        },
        "eligible_true_mass_stats": eligible_stats,
        "compact_slice_stats": compact_stats,
        "eligible_reproduction": eligible_reproduction,
        "compact_slice_reproduction": compact_reproduction,
        "partitions": partitions,
        "diagnostics": {
            "per_class_medians_log10_residual": per_class_medians,
            "compact_uncertainty_band_counts": _band_counts(compact),
        },
        "reproduction_status": reproduction_status,
        "scout_outcome": scout_outcome,
        "verdict": verdict,
    }


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


def _render_partition_section(partition: dict[str, Any]) -> list[str]:
    lines = [
        f"### Partition `{partition['id']}` ({partition['role']}, "
        f"{partition['n_bins']} bins)",
        "",
        partition["description"],
        "",
        f"- Partition outcome: `{partition['partition_outcome']}`",
        f"- Interpretable bins (>= {MIN_BIN_ROW_COUNT} rows): "
        f"{partition['interpretable_bin_count']} / {partition['n_bins']}",
        f"- Survivor bins: "
        f"{partition['survivor_bin_ids'] if partition['survivor_bin_ids'] else 'none'}",
        "",
        "| bin | mass min (Me) | mass max (Me) | count | log10 RMSE | "
        "delta vs eligible | delta vs compact | interpretable | outcome | adverse control |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | :-: | --- | --- |",
    ]
    for b in partition["bins"]:
        cls = b["classification"]
        edges = b["mass_edges"]
        lines.append(
            "| "
            + " | ".join(
                [
                    b["bin_id"],
                    _fmt(edges["mass_min_mearth"], 4),
                    _fmt(edges["mass_max_mearth"], 4),
                    str(b["bin_stats"]["count"]),
                    _fmt(b["bin_stats"]["log10_rmse"]),
                    _fmt(cls.get("delta_log10_rmse_bin_minus_eligible")),
                    _fmt(b.get("delta_log10_rmse_bin_minus_compact_slice")),
                    _fmt_bool(cls["interpretable"]),
                    cls["outcome"],
                    str(cls.get("adverse_control")),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _render_report(metrics: dict[str, Any]) -> str:
    loader = metrics["loader_summary"]
    eligible = metrics["eligible_true_mass_stats"]
    compact = metrics["compact_slice_stats"]
    elig_rep = metrics["eligible_reproduction"]
    comp_rep = metrics["compact_slice_reproduction"]
    lines = [
        f"# {AGENT_RUN_ID} - Exoplanet compact-radius mass-quartile scout",
        "",
        f"- Task: {TASK_ID}",
        f"- Campaign profile: {CAMPAIGN_PROFILE_ID}",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        f"- Source slice: `{metrics['source_slice']['id']}` "
        f"({metrics['source_slice']['source_agent_run_id']})",
        f"- Verdict: **{metrics['verdict']}**",
        f"- Scout outcome: `{metrics['scout_outcome']}`",
        f"- Reproduction status: `{metrics['reproduction_status']}`",
        "",
        "## Boundary",
        "",
        "Sandbox-only scout on committed snapshot rows. The primary axis is "
        "true-mass/transit-radius rows. The frozen CK17 baseline is not refit. "
        "Mass-quartile and mass-half partitions are predeclared before metrics; "
        "bin edges are derived deterministically from the mass-sorted compact "
        "slice.",
        "",
        "## Baseline reproduction",
        "",
        f"- Eligible true-mass/transit-radius rows: "
        f"{loader['eligible_true_mass_with_transit_radius']}",
        f"- Eligible log10 RMSE: {_fmt(eligible['log10_rmse'])} "
        f"(anchor {_fmt(elig_rep['anchor_log10_rmse'])}, "
        f"reproduces: `{_fmt_bool(elig_rep['reproduces_anchor'])}`)",
        f"- Compact slice (R/Re < 1.5) rows: {loader['compact_slice_count']}",
        f"- Compact slice log10 RMSE: {_fmt(compact['log10_rmse'])} "
        f"(anchor {_fmt(comp_rep['anchor_log10_rmse'])}, "
        f"reproduces: `{_fmt_bool(comp_rep['reproduces_anchor'])}`)",
        f"- Outside-compact eligible rows (control pool): "
        f"{loader['outside_compact_count']}",
        "",
        "## Partition results",
        "",
    ]
    for partition in metrics["partitions"]:
        lines.extend(_render_partition_section(partition))

    lines.extend(
        [
            "## Interpretation",
            "",
            f"The compact slice has {loader['compact_slice_count']} eligible rows. "
            f"At quartile resolution each bin holds roughly "
            f"{loader['compact_slice_count'] // 4} rows, below the "
            f"{MIN_BIN_ROW_COUNT}-row interpretation floor; the quartile "
            "partition is therefore reported but not interpreted. The coarser "
            "mass-half partition is a supporting diagnostic only and does not "
            "drive the verdict.",
            "",
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


def _render_interpretation_lines(metrics: dict[str, Any]) -> list[str]:
    """Build a bounded, data-driven interpretation for the review note."""

    compact_count = metrics["loader_summary"]["compact_slice_count"]
    quartile = next(
        (p for p in metrics["partitions"] if p["id"] == "mass_quartile"), None
    )
    half = next((p for p in metrics["partitions"] if p["id"] == "mass_half"), None)

    lines = [
        "## Interpretation",
        "",
        f"The compact slice holds {compact_count} eligible rows. At quartile "
        f"resolution each bin holds roughly {compact_count // 4} rows, below the "
        f"{MIN_BIN_ROW_COUNT}-row interpretation floor, so the predeclared "
        "primary partition is underpowered and the headline verdict is "
        "`INCONCLUSIVE`: the scout cannot localize the compact-radius residual "
        "stress to a mass *quartile* at the current data coverage.",
    ]

    if half is not None and half["survivor_bin_ids"]:
        survivor_ids = set(half["survivor_bin_ids"])
        survivors = [b for b in half["bins"] if b["bin_id"] in survivor_ids]
        edges = [
            f"{b['bin_id']} ({_fmt(b['mass_edges']['mass_min_mearth'], 2)}-"
            f"{_fmt(b['mass_edges']['mass_max_mearth'], 2)} Me, "
            f"log10 RMSE {_fmt(b['bin_stats']['log10_rmse'])})"
            for b in survivors
        ]
        lines.extend(
            [
                "",
                "As a coarse supporting diagnostic only (not a verdict driver), "
                "the mass-half partition shows the residual stress carried by the "
                f"upper-mass half: {', '.join(edges)} survives the per-class "
                "median and outside-compact matched controls, while the "
                "lower-mass half sits at or below the eligible baseline. This is a "
                "directional hint that the compact-slice stress concentrates "
                "toward higher mass, but it is not established: it rests on a "
                "two-bin split and the quartile resolution that would test it is "
                "underpowered.",
            ]
        )
    elif quartile is not None:
        lines.extend(
            [
                "",
                "No mass subrange survives the controls at any interpretable "
                "resolution; the compact-radius residual stress is not localized "
                "to a mass subrange in this scout.",
            ]
        )

    lines.extend(
        [
            "",
            "Recommended (not authorized by this run): a data-coverage expansion "
            "that lifts the compact slice above ~120 eligible rows would make a "
            "predeclared mass-quartile audit interpretable; until then, only a "
            "predeclared mass-half audit can be powered, and any such follow-up "
            "must keep the upper-mass concentration framed as a benchmark "
            "diagnostic rather than a planet-physics conclusion.",
            "",
        ]
    )
    return lines


def _render_review(metrics: dict[str, Any]) -> str:
    lines = [
        "# Exoplanet compact-radius mass-quartile scout",
        "",
        f"- Agent run: `{AGENT_RUN_ID}`",
        f"- Task: `{TASK_ID}`",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        f"- Source slice: `{metrics['source_slice']['id']}` "
        f"(`{metrics['source_slice']['source_agent_run_id']}` / "
        f"`{metrics['source_slice']['source_task_id']}`)",
        f"- Verdict: **{metrics['verdict']}**",
        f"- Scout outcome: `{metrics['scout_outcome']}`",
        f"- Reproduction status: `{metrics['reproduction_status']}`",
        "",
        "## Scope",
        "",
        "This scout tests whether the compact-radius residual stress "
        "(`CSN-001`, R/Re < 1.5; the only matched-control survivor of the "
        "TASK-0427 audit) is concentrated in a mass subrange. It uses only the "
        "committed PSCompPars snapshot and frozen CK17 residuals. Mass-quartile "
        "(primary) and mass-half (fallback diagnostic) partitions are "
        "predeclared before any metric is computed.",
        "",
        "No live fetch, baseline refit, composition inference, atmospheric "
        "inference, habitability wording, target-priority output, new "
        "mass-radius law, prediction entry, canonical result, claim update, or "
        "knowledge edit is authorized.",
        "",
        "## Result summary",
        "",
        f"- Compact slice rows: {metrics['loader_summary']['compact_slice_count']} "
        f"(reproduces `CSN-001` anchor: "
        f"`{_fmt_bool(metrics['compact_slice_reproduction']['reproduces_anchor'])}`).",
        f"- Compact slice log10 RMSE: "
        f"{_fmt(metrics['compact_slice_stats']['log10_rmse'])}; eligible log10 "
        f"RMSE: {_fmt(metrics['eligible_true_mass_stats']['log10_rmse'])}.",
        "",
        "| partition | role | bins | interpretable | survivors | outcome |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for p in metrics["partitions"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    p["id"],
                    p["role"],
                    str(p["n_bins"]),
                    str(p["interpretable_bin_count"]),
                    str(p["survivor_bin_ids"]) if p["survivor_bin_ids"] else "none",
                    p["partition_outcome"],
                ]
            )
            + " |"
        )
    lines.append("")
    lines.extend(_render_interpretation_lines(metrics))
    lines.extend(
        [
            "## Controls per interpreted bin",
            "",
            "- `per_class_median` - per-class CK17 median residual shift on the "
            "bin's own rows (controls for mass-class bias).",
            "- `nearest_radius_outside_compact` - radius-matched cohort drawn "
            "from eligible rows with R/Re >= 1.5.",
            "- `nearest_mass_outside_compact` - log-mass-matched cohort drawn "
            "from eligible rows with R/Re >= 1.5; the key control for a "
            "mass-subrange interpretation.",
            "- `sample_size_random_outside_compact` - deterministic seeded "
            "same-size random outside-compact draw.",
            "",
            "## Limitations",
            "",
            "- The compact slice is small; quartile bins fall below the 30-row "
            "interpretation floor, so the primary partition is underpowered.",
            "- The mass-half partition is a coarse fallback diagnostic only and "
            "does not establish a localized subrange.",
            "- Controls are diagnostic slices, not causal adjustments.",
            "- Bin edges are equal-count contiguous chunks of the mass-sorted "
            "compact slice; they are deterministic but not fixed physical "
            "mass boundaries.",
            "- No composition, inflation-physics, habitability, target-priority, "
            "prediction, claim, or knowledge output is authorized.",
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
        "Compact slice is small; quartile bins fall below the 30-row floor.",
        "Mass-half partition is a coarse fallback diagnostic, not a localized subrange.",
        "Controls use committed snapshot fields and frozen CK17 residuals only.",
        "Matched controls are diagnostic slices, not causal adjustments.",
        "Per-class median control is a residual shift on the bin's own rows, not an independent slice.",
        "Bin edges are equal-count contiguous chunks of mass-sorted rows, not fixed physical boundaries.",
        "Random outside-compact control is deterministic but seed-dependent; the seed is recorded in thresholds.",
        "Minimum-mass rows are excluded; only true-mass/transit-radius rows are used.",
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
            "- Partition predeclaration: quartile (primary) and half (fallback) "
            "rules declared before metrics.",
            f"- Source-slice anchor: {SOURCE_SLICE_ID} from {SOURCE_AGENT_RUN_ID}; "
            "reproduction tolerance recorded in thresholds.",
            "- Controls: per-class residual shift, nearest-radius and "
            "nearest-mass outside-compact cohorts, seeded random outside-compact.",
            "- Promotion boundary: sandbox-only; no canonical result, prediction, "
            "claim, or knowledge output.",
            "",
            "## Checks",
            "",
            "| name | status | notes |",
            "| --- | --- | --- |",
            "| data_boundary | PASS | Only committed snapshot rows are read. |",
            "| baseline_freeze | PASS | CK17 frozen segments are reused without refit. |",
            "| bins_predeclared | PASS | Partition rules declared before metrics. |",
            f"| compact_slice_reproduction | "
            f"{'PASS' if metrics['compact_slice_reproduction']['reproduces_anchor'] else 'DRIFT'} | "
            f"Compact-slice count and RMSE compared to {SOURCE_SLICE_ID} anchor. |",
            "| promotion_boundary | PASS | Sandbox-only output. |",
            "",
        ]
    )


def _render_review_summary(metrics: dict[str, Any]) -> str:
    lines = [
        "# Review summary",
        "",
        f"- Verdict: **{metrics['verdict']}**",
        f"- Scout outcome: `{metrics['scout_outcome']}`",
        f"- Snapshot: `{metrics['snapshot_path']}`",
        f"- Reproduction status: `{metrics['reproduction_status']}`",
        f"- Compact slice rows: {metrics['loader_summary']['compact_slice_count']}",
    ]
    for p in metrics["partitions"]:
        lines.append(
            f"- partition `{p['id']}` ({p['role']}): "
            f"outcome=`{p['partition_outcome']}`, "
            f"interpretable_bins={p['interpretable_bin_count']}/{p['n_bins']}"
        )
    lines.extend(
        [
            "",
            "The scout preserves the underpowered / control-sensitive outcome; it "
            "does not promote a result, prediction, claim, or knowledge artifact.",
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
            # TASK-0480 is a deeper compact-slice scout within the same
            # hypothesis lane as the TASK-0390 pilot / TASK-0427 audit, so it
            # inherits those proposal artifacts as its scientific origin.
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
                    "name": "bins_predeclared",
                    "status": "PASS",
                    "notes": (
                        "Quartile (primary) and half (fallback) partition rules "
                        "are declared before any residual metric is computed."
                    ),
                },
                {
                    "name": "compact_slice_reproduction",
                    "status": (
                        "PASS"
                        if metrics["compact_slice_reproduction"]["reproduces_anchor"]
                        else "DRIFT"
                    ),
                    "notes": (
                        "Compact-slice count and RMSE compared to "
                        f"{SOURCE_SLICE_ID} anchor within {REPRODUCTION_TOLERANCE}."
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
            "Compact slice is small; quartile bins fall below the 30-row floor.",
            "Mass-half partition is a coarse fallback diagnostic, not a localized subrange.",
            "Controls use committed snapshot fields and frozen CK17 residuals only.",
            "Matched controls are diagnostic slices, not causal adjustments.",
            "Per-class median control is a residual shift on the bin's own rows.",
            "Bin edges are equal-count contiguous chunks of mass-sorted rows.",
            "Random outside-compact control is deterministic but seed-dependent.",
            "Minimum-mass rows are excluded; only true-mass/transit-radius rows are used.",
            "No composition, inflation-physics, habitability, target-priority, prediction, claim, or knowledge output is authorized.",
        ],
        "verdict": metrics["verdict"],
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any canonical result, prediction "
                "registry entry, claim update, knowledge edit, or follow-up "
                "lane treats the compact-radius residual as physical structure "
                "or as localized to a mass subrange."
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
    parser.add_argument(
        "--review-summary", type=Path, default=DEFAULT_REVIEW_SUMMARY_PATH
    )
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
