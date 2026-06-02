"""Atomic-clock residual source loaders.

This module supports two disjoint loaders:

* ``load_atomic_clock_synthetic_dataset`` validates synthetic dry-run fixtures
  (``row_class: synthetic_dry_run``) that use a ``source_metadata`` block.
* ``load_atomic_clock_direct_dataset`` validates committed real
  ``row_class: direct_measurement`` rows (e.g. the Beloy 2021 / BACON seed)
  that use a ``source`` block.

The two loaders are intentionally kept apart so that synthetic test rows and
real measurement rows cannot be silently mixed, and so that the ``source`` vs
``source_metadata`` naming difference is reconciled explicitly rather than by
accepting arbitrary keys. Neither loader fits drifts, computes residuals,
derives constants constraints, writes prediction or result artifacts, or
promotes claims; they only validate and surface committed rows.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ALLOWED_SYNTHETIC_ROW_CLASSES = {"synthetic_dry_run"}
REQUIRED_ROW_KEYS = {
    "row_id",
    "row_class",
    "observable_id",
    "clock_system",
    "reference_system",
    "observable",
    "uncertainty",
    "source_metadata",
    "classification",
    "holdout",
    "limitations",
}


@dataclass(frozen=True)
class AtomicClockSyntheticRow:
    """Validated synthetic atomic-clock row for schema dry runs."""

    row_id: str
    row_class: str
    observable_id: str
    value_kind: str
    units: str
    split: str
    synthetic: bool
    derived_constraint: bool
    covariance_group: str | None


@dataclass(frozen=True)
class AtomicClockSyntheticDataset:
    """Validated synthetic-only atomic-clock fixture."""

    dataset_id: str
    task_id: str
    rows: tuple[AtomicClockSyntheticRow, ...]
    row_class_counts: dict[str, int]
    value_kind_counts: dict[str, int]


def _require_mapping(value: Any, *, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def _require_string(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _validate_synthetic_row(row: dict[str, Any], *, dataset_id: str) -> AtomicClockSyntheticRow:
    missing = sorted(REQUIRED_ROW_KEYS - set(row))
    if missing:
        raise ValueError(f"{dataset_id} row missing required keys: {missing}")

    row_id = _require_string(row["row_id"], label="row_id")
    row_class = _require_string(row["row_class"], label=f"{row_id}.row_class")
    if row_class not in ALLOWED_SYNTHETIC_ROW_CLASSES:
        raise ValueError(f"{row_id} row_class must be synthetic_dry_run")

    classification = _require_mapping(row["classification"], label=f"{row_id}.classification")
    if classification.get("synthetic") is not True:
        raise ValueError(f"{row_id} must be explicitly marked synthetic")
    if classification.get("direct_measurement") is True:
        raise ValueError(f"{row_id} synthetic rows must not be direct measurements")
    if classification.get("review_summary") is True:
        raise ValueError(f"{row_id} synthetic rows must not be review summaries")

    observable = _require_mapping(row["observable"], label=f"{row_id}.observable")
    value_kind = _require_string(observable.get("value_kind"), label=f"{row_id}.observable.value_kind")
    units = _require_string(observable.get("units"), label=f"{row_id}.observable.units")
    if observable.get("value") is None:
        raise ValueError(f"{row_id} synthetic dry-run row needs a fabricated test value")

    source = _require_mapping(row["source_metadata"], label=f"{row_id}.source_metadata")
    if source.get("source_class") != "synthetic_rows":
        raise ValueError(f"{row_id} source_class must be synthetic_rows")

    uncertainty = _require_mapping(row["uncertainty"], label=f"{row_id}.uncertainty")
    if "total" not in uncertainty:
        raise ValueError(f"{row_id} uncertainty.total is required, even when fabricated")

    holdout = _require_mapping(row["holdout"], label=f"{row_id}.holdout")
    split = _require_string(holdout.get("split"), label=f"{row_id}.holdout.split")
    if split != "synthetic_only":
        raise ValueError(f"{row_id} holdout.split must be synthetic_only")

    limitations = row["limitations"]
    if not isinstance(limitations, list) or not limitations:
        raise ValueError(f"{row_id} must preserve limitations")

    derived = bool(classification.get("derived_constraint"))
    if derived and "derived_constraint" not in row:
        raise ValueError(f"{row_id} derived synthetic rows need derived_constraint metadata")

    return AtomicClockSyntheticRow(
        row_id=row_id,
        row_class=row_class,
        observable_id=_require_string(row["observable_id"], label=f"{row_id}.observable_id"),
        value_kind=value_kind,
        units=units,
        split=split,
        synthetic=True,
        derived_constraint=derived,
        covariance_group=uncertainty.get("covariance_group"),
    )


def _counts(values: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items()))


def load_atomic_clock_synthetic_dataset(path: str | Path) -> AtomicClockSyntheticDataset:
    """Load and validate a synthetic-only atomic-clock dry-run fixture."""
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    data = _require_mapping(payload, label="dataset")
    dataset_id = _require_string(data.get("dataset_id"), label="dataset_id")
    if data.get("task_id") != "TASK-0328":
        raise ValueError(f"{dataset_id} must be tied to TASK-0328")
    if data.get("synthetic") is not True:
        raise ValueError(f"{dataset_id} must be explicitly synthetic")
    if data.get("benchmark_allowed") is not False:
        raise ValueError(f"{dataset_id} must not allow benchmarks")
    if data.get("claim_promotion_allowed") is not False:
        raise ValueError(f"{dataset_id} must not allow claim promotion")

    raw_rows = data.get("rows")
    if not isinstance(raw_rows, list) or not raw_rows:
        raise ValueError(f"{dataset_id} must contain synthetic rows")
    rows = tuple(
        _validate_synthetic_row(_require_mapping(row, label=f"{dataset_id}.row"), dataset_id=dataset_id)
        for row in raw_rows
    )
    row_ids = [row.row_id for row in rows]
    if len(set(row_ids)) != len(row_ids):
        raise ValueError(f"{dataset_id} row_id values must be unique")

    return AtomicClockSyntheticDataset(
        dataset_id=dataset_id,
        task_id=str(data["task_id"]),
        rows=rows,
        row_class_counts=_counts([row.row_class for row in rows]),
        value_kind_counts=_counts([row.value_kind for row in rows]),
    )


# ---------------------------------------------------------------------------
# Real direct-measurement loader (TASK-0453)
# ---------------------------------------------------------------------------

# The direct loader handles committed, source-reviewed real rows. It does NOT
# accept derived constraints, review summaries, or synthetic rows: those need
# their own explicit ingestion paths and must not be silently mixed with direct
# measurements.
ALLOWED_DIRECT_ROW_CLASSES = {"direct_measurement"}

REQUIRED_DIRECT_ROW_KEYS = {
    "row_id",
    "row_class",
    "observable_id",
    "clock_system",
    "reference_system",
    "observable",
    "uncertainty",
    "source",
    "classification",
    "holdout",
    "limitations",
}

# Uncertainty fields every direct row must carry so downstream benchmarks never
# silently inherit an undocumented uncertainty basis.
REQUIRED_DIRECT_UNCERTAINTY_KEYS = {
    "total",
    "confidence_level_label",
    "bound_style",
    "covariance_reference",
}


@dataclass(frozen=True)
class AtomicClockDirectRow:
    """Validated real direct-measurement atomic-clock row."""

    row_id: str
    row_class: str
    observable_id: str
    value_kind: str
    units: str
    value: float
    total_uncertainty: float
    confidence_level_label: str
    bound_style: str
    covariance_reference: str
    covariance_group: str | None
    split: str


@dataclass(frozen=True)
class AtomicClockDirectDataset:
    """Validated real direct-measurement atomic-clock dataset."""

    dataset_id: str
    schema_version: str
    campaign_profile_id: str
    rows: tuple[AtomicClockDirectRow, ...]
    row_class_counts: dict[str, int]
    value_kind_counts: dict[str, int]
    covariance_groups: tuple[str, ...]


def _require_number(value: Any, *, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a real number")
    return float(value)


def _validate_direct_classification(row_id: str, row: dict[str, Any]) -> None:
    classification = _require_mapping(row["classification"], label=f"{row_id}.classification")
    if classification.get("direct_measurement") is not True:
        raise ValueError(f"{row_id} classification.direct_measurement must be true")
    if classification.get("derived_constraint") is not False:
        raise ValueError(f"{row_id} direct rows must set classification.derived_constraint false")
    if classification.get("review_summary") is not False:
        raise ValueError(f"{row_id} direct rows must set classification.review_summary false")
    if classification.get("synthetic") is not False:
        raise ValueError(f"{row_id} direct rows must set classification.synthetic false")


def _validate_direct_source(row_id: str, row: dict[str, Any]) -> None:
    # Reconcile the source vs source_metadata naming drift explicitly: real
    # direct rows must use `source`; the synthetic `source_metadata` block is a
    # different contract and must not appear on a direct row.
    if "source_metadata" in row:
        raise ValueError(
            f"{row_id} direct rows must use the `source` block, not the synthetic "
            "`source_metadata` block"
        )
    source = _require_mapping(row["source"], label=f"{row_id}.source")
    _require_string(source.get("citation"), label=f"{row_id}.source.citation")
    has_checksum = isinstance(source.get("checksum_sha256"), str) and bool(source.get("checksum_sha256"))
    has_archive = isinstance(source.get("archive_url"), str) and bool(source.get("archive_url"))
    if not (has_checksum or has_archive):
        raise ValueError(
            f"{row_id} source must provide a checksum_sha256 or an archive_url locator"
        )


def _validate_direct_uncertainty(row_id: str, row: dict[str, Any]) -> tuple[float, str, str, str, str | None]:
    uncertainty = _require_mapping(row["uncertainty"], label=f"{row_id}.uncertainty")
    missing = sorted(REQUIRED_DIRECT_UNCERTAINTY_KEYS - set(uncertainty))
    if missing:
        raise ValueError(f"{row_id} uncertainty missing required keys: {missing}")
    total = _require_number(uncertainty["total"], label=f"{row_id}.uncertainty.total")
    if total <= 0:
        raise ValueError(f"{row_id} uncertainty.total must be positive")
    confidence_level_label = _require_string(
        uncertainty["confidence_level_label"], label=f"{row_id}.uncertainty.confidence_level_label"
    )
    bound_style = _require_string(uncertainty["bound_style"], label=f"{row_id}.uncertainty.bound_style")
    covariance_reference = _require_string(
        uncertainty["covariance_reference"], label=f"{row_id}.uncertainty.covariance_reference"
    )
    covariance_group = uncertainty.get("covariance_group")
    if covariance_group is not None and not isinstance(covariance_group, str):
        raise ValueError(f"{row_id} uncertainty.covariance_group must be a string when present")
    return total, confidence_level_label, bound_style, covariance_reference, covariance_group


def _validate_direct_row(row: dict[str, Any], *, dataset_id: str) -> AtomicClockDirectRow:
    missing = sorted(REQUIRED_DIRECT_ROW_KEYS - set(row))
    if missing:
        raise ValueError(f"{dataset_id} direct row missing required keys: {missing}")

    row_id = _require_string(row["row_id"], label="row_id")
    row_class = _require_string(row["row_class"], label=f"{row_id}.row_class")
    if row_class not in ALLOWED_DIRECT_ROW_CLASSES:
        raise ValueError(
            f"{row_id} row_class must be direct_measurement for the direct loader; "
            f"got {row_class!r}"
        )

    _validate_direct_classification(row_id, row)
    _validate_direct_source(row_id, row)
    total, confidence_level_label, bound_style, covariance_reference, covariance_group = (
        _validate_direct_uncertainty(row_id, row)
    )

    observable = _require_mapping(row["observable"], label=f"{row_id}.observable")
    value_kind = _require_string(observable.get("value_kind"), label=f"{row_id}.observable.value_kind")
    units = _require_string(observable.get("units"), label=f"{row_id}.observable.units")
    if observable.get("value") is None:
        raise ValueError(f"{row_id} direct measurement row needs a value")
    value = _require_number(observable["value"], label=f"{row_id}.observable.value")

    holdout = _require_mapping(row["holdout"], label=f"{row_id}.holdout")
    split = _require_string(holdout.get("split"), label=f"{row_id}.holdout.split")

    limitations = row["limitations"]
    if not isinstance(limitations, list) or not limitations:
        raise ValueError(f"{row_id} must preserve limitations")

    return AtomicClockDirectRow(
        row_id=row_id,
        row_class=row_class,
        observable_id=_require_string(row["observable_id"], label=f"{row_id}.observable_id"),
        value_kind=value_kind,
        units=units,
        value=value,
        total_uncertainty=total,
        confidence_level_label=confidence_level_label,
        bound_style=bound_style,
        covariance_reference=covariance_reference,
        covariance_group=covariance_group,
        split=split,
    )


def load_atomic_clock_direct_dataset(path: str | Path) -> AtomicClockDirectDataset:
    """Load and validate a committed real direct-measurement atomic-clock dataset.

    This is a validation/loader contract only. It deliberately enforces the
    dataset's sandbox boundary (no benchmarks, no claim promotion) and never
    fits drifts, computes residuals, or derives constants constraints.
    """
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    data = _require_mapping(payload, label="dataset")
    dataset_id = _require_string(data.get("dataset_id"), label="dataset_id")
    schema_version = _require_string(data.get("schema_version"), label=f"{dataset_id}.schema_version")
    campaign_profile_id = _require_string(
        data.get("campaign_profile_id"), label=f"{dataset_id}.campaign_profile_id"
    )

    scope = _require_mapping(data.get("scope"), label=f"{dataset_id}.scope")
    if scope.get("sandbox_only") is not True:
        raise ValueError(f"{dataset_id} must declare scope.sandbox_only true")
    if scope.get("benchmark_allowed") is not False:
        raise ValueError(f"{dataset_id} must declare scope.benchmark_allowed false")
    if scope.get("claim_promotion_allowed") is not False:
        raise ValueError(f"{dataset_id} must declare scope.claim_promotion_allowed false")

    raw_rows = data.get("rows")
    if not isinstance(raw_rows, list) or not raw_rows:
        raise ValueError(f"{dataset_id} must contain direct rows")
    rows = tuple(
        _validate_direct_row(_require_mapping(row, label=f"{dataset_id}.row"), dataset_id=dataset_id)
        for row in raw_rows
    )
    row_ids = [row.row_id for row in rows]
    if len(set(row_ids)) != len(row_ids):
        raise ValueError(f"{dataset_id} row_id values must be unique")

    covariance_groups = tuple(
        sorted({row.covariance_group for row in rows if row.covariance_group is not None})
    )

    return AtomicClockDirectDataset(
        dataset_id=dataset_id,
        schema_version=schema_version,
        campaign_profile_id=campaign_profile_id,
        rows=rows,
        row_class_counts=_counts([row.row_class for row in rows]),
        value_kind_counts=_counts([row.value_kind for row in rows]),
        covariance_groups=covariance_groups,
    )
