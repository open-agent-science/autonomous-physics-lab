"""Exoplanet mass-radius dataset loader.

Implements the dry-run loader contract from TASK-0354 against the
schema locked by TASK-0337 and the ingestion plan locked by TASK-0345.
The loader applies the inclusion/exclusion filters that the Exoplanet
Mass-Radius baseline protocol (TASK-0346) assumes are already enforced
before any baseline is scored.

What this module does
=====================

- read a normalized exoplanet snapshot YAML;
- enforce loader-level invariants beyond the JSON Schema (known
  mass_class / radius_class buckets, duplicate planet-name detection,
  synthetic-fixture safety);
- apply the inclusion/exclusion filter chain in the order documented
  in `docs/reviews/exoplanet-pscomppars-snapshot-ingestion-plan.md`;
- apply the recommended quality-filter thresholds
  (`sigma_M/M <= 0.30`, `sigma_R/R <= 0.15`); thresholds are overridable
  per call but both pre-filter and post-filter row counts are always
  reported;
- return row-count summaries, per-class counts, and an
  exclusion-reason histogram suitable for review notes and PR bodies.

What this module does NOT do
============================

- it does not fetch live NASA Exoplanet Archive data;
- it does not compute baseline residuals, calibration metrics, or
  failure maps (those are owned by TASK-0346 and a future baseline
  implementation task);
- it does not promote claims, register prediction-registry entries, or
  produce habitability / biosignature / planet-prioritization output;
- it does not silently rewrite mass_class, radius_class, or
  inclusion_status fields; unknown values raise loader-level errors
  rather than being mapped to a default bucket.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


# ---------------------------------------------------------------------------
# Canonical class buckets (mirror the schema enums).
# ---------------------------------------------------------------------------

KNOWN_ROW_CLASSES: frozenset[str] = frozenset(
    {
        "direct_mass_radius_measurement",
        "transit_radius_with_rv_minimum_mass",
        "transit_radius_only",
        "rv_minimum_mass_only",
        "microlensing_or_astrometry_mass",
        "model_inferred",
        "synthetic_dry_run",
    }
)

KNOWN_MASS_CLASSES: frozenset[str] = frozenset(
    {
        "true_mass",
        "minimum_mass_msini",
        "transit_timing_dynamical_mass",
        "microlensing_mass",
        "astrometric_mass",
        "model_inferred",
        "not_measured",
    }
)

KNOWN_RADIUS_CLASSES: frozenset[str] = frozenset(
    {
        "transit_radius",
        "direct_imaging_radius",
        "model_inferred",
        "not_measured",
    }
)


# ---------------------------------------------------------------------------
# Exclusion reason codes the loader emits.
# ---------------------------------------------------------------------------

REASON_INCLUDED: str = "included"
REASON_PRE_SNAPSHOT_EXCLUDED: str = "pre_snapshot_excluded"
REASON_DUPLICATE_PLANET_NAME: str = "duplicate_planet_name_in_snapshot"
REASON_UNKNOWN_MASS_CLASS: str = "unknown_mass_class"
REASON_UNKNOWN_RADIUS_CLASS: str = "unknown_radius_class"
REASON_UNKNOWN_ROW_CLASS: str = "unknown_row_class"
REASON_MASS_INFERRED_FROM_MR_RELATION: str = (
    "mass_inferred_from_mass_radius_relationship"
)
REASON_RADIUS_INFERRED_FROM_NON_TRANSIT: str = (
    "radius_inferred_from_non_transit_method"
)
REASON_MASS_RELATIVE_UNCERTAINTY_ABOVE_THRESHOLD: str = (
    "mass_relative_uncertainty_above_threshold"
)
REASON_RADIUS_RELATIVE_UNCERTAINTY_ABOVE_THRESHOLD: str = (
    "radius_relative_uncertainty_above_threshold"
)
REASON_MASS_VALUE_NULL_FOR_TRUE_MASS_AXIS: str = (
    "mass_value_null_for_true_mass_axis"
)
REASON_RADIUS_VALUE_NULL_FOR_TRUE_MASS_AXIS: str = (
    "radius_value_null_for_true_mass_axis"
)


# ---------------------------------------------------------------------------
# Default quality-filter thresholds.
# ---------------------------------------------------------------------------

DEFAULT_MASS_SIGMA_THRESHOLD: float = 0.30
DEFAULT_RADIUS_SIGMA_THRESHOLD: float = 0.15


# ---------------------------------------------------------------------------
# Normalized snapshot checksum.
# ---------------------------------------------------------------------------


def normalized_snapshot_checksum(snapshot: dict[str, Any]) -> str:
    """Return the stable SHA-256 for a normalized snapshot payload.

    The embedded checksum field is normalized to ``None`` before a sorted,
    compact JSON encoding is hashed. This avoids a self-referential file hash
    while making row-level or metadata drift visible across YAML serializers.
    """

    canonical_snapshot = copy.deepcopy(snapshot)
    provenance = canonical_snapshot.get("snapshot_provenance")
    if not isinstance(provenance, dict):
        raise ValueError("snapshot_provenance must be a mapping")
    provenance["normalized_checksum_sha256"] = None
    encoded = json.dumps(
        canonical_snapshot,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


# ---------------------------------------------------------------------------
# Result dataclasses.
# ---------------------------------------------------------------------------


@dataclass
class FilteredSnapshot:
    """Outcome of applying the loader's filter chain to a snapshot.

    Designed to be cheap to JSON-serialize via :func:`summarize` so the
    same object can be used in tests, review notes, and PR bodies.
    """

    dataset_id: str
    snapshot_kind: str
    source_family_id: str
    retrieval_date_utc: str
    total_rows: int
    included_rows: list[dict[str, Any]]
    excluded_rows: list[dict[str, Any]]
    exclusion_reason_counts: dict[str, int]
    row_class_counts: dict[str, int]
    mass_class_counts: dict[str, int]
    radius_class_counts: dict[str, int]
    detection_method_counts: dict[str, int]
    pre_filter_included_count: int
    post_filter_included_count: int
    mass_sigma_threshold: float
    radius_sigma_threshold: float


# ---------------------------------------------------------------------------
# Public API.
# ---------------------------------------------------------------------------


def load_exoplanet_snapshot(path: Path) -> dict[str, Any]:
    """Load a normalized exoplanet snapshot YAML and run loader invariants.

    Performs structural checks that the JSON Schema does not enforce:

    - top-level payload must be a mapping;
    - `entries` must be present and non-empty;
    - synthetic-dry-run snapshots must carry a `fake_source_warning`
      string;
    - `snapshot_provenance.live_external_fetch_allowed` must be `False`
      for any committed-shape snapshot (non-synthetic).

    The function does not run the JSON Schema validator itself; the
    repository's own schema-validation harness owns that step. The
    intent here is to catch the small set of invariants that a careless
    fixture could violate without the schema noticing.
    """

    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        payload = yaml.load(fh, Loader=YAML_LOADER)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping at top of {path}")
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"Snapshot {path} must include a non-empty entries list")

    provenance = payload.get("snapshot_provenance", {})
    if not isinstance(provenance, dict):
        raise ValueError(f"Snapshot {path} snapshot_provenance must be a mapping")

    snapshot_kind = provenance.get("snapshot_kind")
    if snapshot_kind == "synthetic_dry_run":
        if not isinstance(payload.get("fake_source_warning"), str) or not payload[
            "fake_source_warning"
        ].strip():
            raise ValueError(
                f"Snapshot {path} is synthetic_dry_run but is missing a "
                "non-empty fake_source_warning"
            )
    else:
        if provenance.get("live_external_fetch_allowed") is True:
            raise ValueError(
                f"Snapshot {path} sets live_external_fetch_allowed: true on a "
                "non-synthetic snapshot; this is forbidden"
            )

    expected_checksum = provenance.get("normalized_checksum_sha256")
    if expected_checksum is not None:
        actual_checksum = normalized_snapshot_checksum(payload)
        if expected_checksum != actual_checksum:
            raise ValueError(
                f"Snapshot {path} normalized_checksum_sha256 does not match "
                f"canonical payload checksum: expected {expected_checksum}, "
                f"computed {actual_checksum}"
            )

    return payload


def apply_inclusion_filters(
    snapshot: dict[str, Any],
    *,
    mass_sigma_threshold: float = DEFAULT_MASS_SIGMA_THRESHOLD,
    radius_sigma_threshold: float = DEFAULT_RADIUS_SIGMA_THRESHOLD,
) -> FilteredSnapshot:
    """Apply the TASK-0345 / TASK-0346 inclusion/exclusion filter chain.

    Filter order (each step is preserved in the exclusion-reason
    histogram; no row is silently dropped):

    1. Reject unknown `row_class`, `mass_class`, or `radius_class` values
       (loader-level invariant).
    2. Reject duplicate `planet_name` within the same snapshot.
    3. Respect `inclusion_status == "excluded"` set at snapshot time
       (preserves snapshot-level filter decisions such as
       solution_type != "Published Confirmed").
    4. Exclude `mass_class == "model_inferred"` rows from the true-mass
       residual axis (circular-validation guard).
    5. Exclude `radius_class == "model_inferred"` rows from the
       transit-radius axis (non-transit-derived radius).
    6. Apply mass relative-uncertainty filter
       (`sigma_M / M > mass_sigma_threshold`).
    7. Apply radius relative-uncertainty filter
       (`sigma_R / R > radius_sigma_threshold`).

    Steps 1-5 produce the *pre-filter* included set. Steps 6-7 produce
    the *post-filter* included set. Both counts are reported so the
    pre/post comparison is itself a diagnostic.

    Returns a :class:`FilteredSnapshot` instance.
    """

    entries: list[dict[str, Any]] = snapshot["entries"]
    provenance: dict[str, Any] = snapshot.get("snapshot_provenance", {})

    pre_filter_included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    reasons: Counter[str] = Counter()

    row_class_counts: Counter[str] = Counter()
    mass_class_counts: Counter[str] = Counter()
    radius_class_counts: Counter[str] = Counter()
    detection_method_counts: Counter[str] = Counter()

    seen_planet_names: dict[str, str] = {}

    for entry in entries:
        row_class = entry["row_class"]
        row_class_counts[row_class] += 1
        mass_class = entry["mass"]["mass_class"]
        mass_class_counts[mass_class] += 1
        radius_class = entry["radius"]["radius_class"]
        radius_class_counts[radius_class] += 1
        detection_method = entry["detection_method"]
        detection_method_counts[detection_method] += 1

        # Step 1: loader-level invariants.
        if row_class not in KNOWN_ROW_CLASSES:
            excluded.append(entry)
            reasons[REASON_UNKNOWN_ROW_CLASS] += 1
            continue
        if mass_class not in KNOWN_MASS_CLASSES:
            excluded.append(entry)
            reasons[REASON_UNKNOWN_MASS_CLASS] += 1
            continue
        if radius_class not in KNOWN_RADIUS_CLASSES:
            excluded.append(entry)
            reasons[REASON_UNKNOWN_RADIUS_CLASS] += 1
            continue

        # Step 2: duplicate-name guard.
        planet_name = entry["planet_name"]
        if planet_name in seen_planet_names:
            excluded.append(entry)
            reasons[REASON_DUPLICATE_PLANET_NAME] += 1
            continue
        seen_planet_names[planet_name] = entry["row_id"]

        # Step 3: snapshot-time exclusion is final; preserve its reason.
        if entry.get("inclusion_status") == "excluded":
            excluded.append(entry)
            reason_code = entry.get("inclusion_reason") or REASON_PRE_SNAPSHOT_EXCLUDED
            reasons[reason_code] += 1
            continue

        # Step 4: mass-class gate for the true-mass axis.
        if mass_class == "model_inferred":
            excluded.append(entry)
            reasons[REASON_MASS_INFERRED_FROM_MR_RELATION] += 1
            continue

        # Step 5: radius-class gate for the transit-radius axis.
        if radius_class == "model_inferred":
            excluded.append(entry)
            reasons[REASON_RADIUS_INFERRED_FROM_NON_TRANSIT] += 1
            continue

        pre_filter_included.append(entry)

    # Steps 6-7: quality filters.
    post_filter_included: list[dict[str, Any]] = []
    for entry in pre_filter_included:
        if _exceeds_mass_uncertainty(entry, mass_sigma_threshold):
            excluded.append(entry)
            reasons[REASON_MASS_RELATIVE_UNCERTAINTY_ABOVE_THRESHOLD] += 1
            continue
        if _exceeds_radius_uncertainty(entry, radius_sigma_threshold):
            excluded.append(entry)
            reasons[REASON_RADIUS_RELATIVE_UNCERTAINTY_ABOVE_THRESHOLD] += 1
            continue
        post_filter_included.append(entry)

    return FilteredSnapshot(
        dataset_id=snapshot["dataset_id"],
        snapshot_kind=str(provenance.get("snapshot_kind", "unknown")),
        source_family_id=str(provenance.get("source_family_id", "unknown")),
        retrieval_date_utc=str(provenance.get("retrieval_date_utc", "unknown")),
        total_rows=len(entries),
        included_rows=post_filter_included,
        excluded_rows=excluded,
        exclusion_reason_counts=dict(reasons),
        row_class_counts=dict(row_class_counts),
        mass_class_counts=dict(mass_class_counts),
        radius_class_counts=dict(radius_class_counts),
        detection_method_counts=dict(detection_method_counts),
        pre_filter_included_count=len(pre_filter_included),
        post_filter_included_count=len(post_filter_included),
        mass_sigma_threshold=mass_sigma_threshold,
        radius_sigma_threshold=radius_sigma_threshold,
    )


def summarize(filtered: FilteredSnapshot) -> dict[str, Any]:
    """Return a JSON-serializable summary of a :class:`FilteredSnapshot`."""

    return {
        "dataset_id": filtered.dataset_id,
        "snapshot_kind": filtered.snapshot_kind,
        "source_family_id": filtered.source_family_id,
        "retrieval_date_utc": filtered.retrieval_date_utc,
        "total_rows": filtered.total_rows,
        "pre_filter_included_count": filtered.pre_filter_included_count,
        "post_filter_included_count": filtered.post_filter_included_count,
        "thresholds": {
            "mass_sigma_threshold": filtered.mass_sigma_threshold,
            "radius_sigma_threshold": filtered.radius_sigma_threshold,
        },
        "exclusion_reason_counts": dict(
            sorted(filtered.exclusion_reason_counts.items())
        ),
        "row_class_counts": dict(sorted(filtered.row_class_counts.items())),
        "mass_class_counts": dict(sorted(filtered.mass_class_counts.items())),
        "radius_class_counts": dict(sorted(filtered.radius_class_counts.items())),
        "detection_method_counts": dict(
            sorted(filtered.detection_method_counts.items())
        ),
    }


def load_and_filter(
    path: Path,
    *,
    mass_sigma_threshold: float = DEFAULT_MASS_SIGMA_THRESHOLD,
    radius_sigma_threshold: float = DEFAULT_RADIUS_SIGMA_THRESHOLD,
) -> FilteredSnapshot:
    """Convenience: load a snapshot YAML and apply the filter chain."""

    snapshot = load_exoplanet_snapshot(path)
    return apply_inclusion_filters(
        snapshot,
        mass_sigma_threshold=mass_sigma_threshold,
        radius_sigma_threshold=radius_sigma_threshold,
    )


# ---------------------------------------------------------------------------
# Internal helpers.
# ---------------------------------------------------------------------------


def _exceeds_mass_uncertainty(entry: dict[str, Any], threshold: float) -> bool:
    mass = entry["mass"]
    value = mass.get("value")
    if value is None or value == 0:
        return False
    upper = mass.get("uncertainty_upper")
    lower = mass.get("uncertainty_lower")
    sigma = max(
        abs(float(upper)) if upper is not None else 0.0,
        abs(float(lower)) if lower is not None else 0.0,
    )
    if sigma == 0.0:
        return False
    return sigma / abs(float(value)) > threshold


def _exceeds_radius_uncertainty(entry: dict[str, Any], threshold: float) -> bool:
    radius = entry["radius"]
    value = radius.get("value")
    if value is None or value == 0:
        return False
    upper = radius.get("uncertainty_upper")
    lower = radius.get("uncertainty_lower")
    sigma = max(
        abs(float(upper)) if upper is not None else 0.0,
        abs(float(lower)) if lower is not None else 0.0,
    )
    if sigma == 0.0:
        return False
    return sigma / abs(float(value)) > threshold
