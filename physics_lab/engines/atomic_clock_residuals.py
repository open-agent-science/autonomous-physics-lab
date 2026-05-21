"""Atomic-clock residual source loaders.

The current module intentionally supports only synthetic dry-run fixtures.
Real atomic-clock rows remain blocked behind source-manifest review.
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
