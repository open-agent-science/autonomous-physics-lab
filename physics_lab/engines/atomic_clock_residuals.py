"""Atomic-clock residual source loaders.

The module keeps synthetic dry-run validation separate from committed real
direct-row validation. Loading direct rows is a schema/readiness check only; it
does not authorize benchmarks, drift fits, constants constraints, predictions,
results, or claims.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ALLOWED_SYNTHETIC_ROW_CLASSES = {"synthetic_dry_run"}
ALLOWED_DIRECT_ROW_CLASSES = {"direct_measurement"}
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
REQUIRED_DIRECT_UNCERTAINTY_KEYS = {
    "total",
    "confidence_level_label",
    "bound_style",
    "covariance_reference",
}
REQUIRED_DIRECT_SOURCE_KEYS = {
    "citation",
    "retrieval_date",
    "checksum_sha256",
    "checksum_scope",
    "license_note",
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


@dataclass(frozen=True)
class AtomicClockSyntheticCrossSourceDataset:
    """Validated fabricated cross-source benchmark dry-run fixture."""

    dataset_id: str
    task_id: str
    rows: tuple[AtomicClockSyntheticRow, ...]
    row_roles: dict[str, str]
    covariance_states: dict[str, str]
    row_class_counts: dict[str, int]
    value_kind_counts: dict[str, int]


@dataclass(frozen=True)
class AtomicClockDirectRow:
    """Validated committed direct atomic-clock measurement row."""

    row_id: str
    row_class: str
    observable_id: str
    value_kind: str
    units: str
    split: str
    total_uncertainty: float
    confidence_level_label: str
    bound_style: str
    covariance_reference: str
    covariance_group: str | None


@dataclass(frozen=True)
class AtomicClockDirectDataset:
    """Validated committed direct atomic-clock row dataset."""

    dataset_id: str
    task_id: str
    rows: tuple[AtomicClockDirectRow, ...]
    row_class_counts: dict[str, int]
    value_kind_counts: dict[str, int]
    covariance_group_counts: dict[str, int]


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


def _require_number(value: Any, *, label: str) -> float:
    if not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric")
    return float(value)


def _validate_direct_row(row: dict[str, Any], *, dataset_id: str) -> AtomicClockDirectRow:
    if "source_metadata" in row:
        raise ValueError(f"{dataset_id} direct rows must use source, not source_metadata")
    missing = sorted(REQUIRED_DIRECT_ROW_KEYS - set(row))
    if missing:
        raise ValueError(f"{dataset_id} direct row missing required keys: {missing}")

    row_id = _require_string(row["row_id"], label="row_id")
    row_class = _require_string(row["row_class"], label=f"{row_id}.row_class")
    if row_class not in ALLOWED_DIRECT_ROW_CLASSES:
        raise ValueError(f"{row_id} row_class must be direct_measurement")

    classification = _require_mapping(row["classification"], label=f"{row_id}.classification")
    if classification.get("direct_measurement") is not True:
        raise ValueError(f"{row_id} must be explicitly marked direct_measurement")
    for flag in ("derived_constraint", "review_summary", "synthetic"):
        if classification.get(flag) is not False:
            raise ValueError(f"{row_id} direct rows must set classification.{flag} false")

    for group_name in ("clock_system", "reference_system"):
        group = _require_mapping(row[group_name], label=f"{row_id}.{group_name}")
        _require_string(group.get("clock_id"), label=f"{row_id}.{group_name}.clock_id")
        _require_string(group.get("species"), label=f"{row_id}.{group_name}.species")
        _require_string(group.get("transition_label"), label=f"{row_id}.{group_name}.transition_label")

    observable = _require_mapping(row["observable"], label=f"{row_id}.observable")
    value_kind = _require_string(observable.get("value_kind"), label=f"{row_id}.observable.value_kind")
    if value_kind != "frequency_ratio":
        raise ValueError(f"{row_id} direct rows must use observable.value_kind frequency_ratio")
    units = _require_string(observable.get("units"), label=f"{row_id}.observable.units")
    if observable.get("value") is None:
        raise ValueError(f"{row_id} direct row needs a committed measurement value")
    _require_string(observable.get("epoch_start"), label=f"{row_id}.observable.epoch_start")
    _require_string(observable.get("epoch_end"), label=f"{row_id}.observable.epoch_end")

    uncertainty = _require_mapping(row["uncertainty"], label=f"{row_id}.uncertainty")
    missing_uncertainty = sorted(REQUIRED_DIRECT_UNCERTAINTY_KEYS - set(uncertainty))
    if missing_uncertainty:
        raise ValueError(f"{row_id} uncertainty missing required keys: {missing_uncertainty}")
    total_uncertainty = _require_number(uncertainty.get("total"), label=f"{row_id}.uncertainty.total")
    if total_uncertainty <= 0:
        raise ValueError(f"{row_id} uncertainty.total must be positive")
    confidence_level_label = _require_string(
        uncertainty.get("confidence_level_label"),
        label=f"{row_id}.uncertainty.confidence_level_label",
    )
    bound_style = _require_string(uncertainty.get("bound_style"), label=f"{row_id}.uncertainty.bound_style")
    covariance_reference = _require_string(
        uncertainty.get("covariance_reference"),
        label=f"{row_id}.uncertainty.covariance_reference",
    )

    source = _require_mapping(row["source"], label=f"{row_id}.source")
    missing_source = sorted(REQUIRED_DIRECT_SOURCE_KEYS - set(source))
    if missing_source:
        raise ValueError(f"{row_id} source missing required keys: {missing_source}")
    _require_string(source.get("citation"), label=f"{row_id}.source.citation")
    if not source.get("doi") and not source.get("archive_url"):
        raise ValueError(f"{row_id} source needs doi or archive_url")

    holdout = _require_mapping(row["holdout"], label=f"{row_id}.holdout")
    split = _require_string(holdout.get("split"), label=f"{row_id}.holdout.split")
    limitations = row["limitations"]
    if not isinstance(limitations, list) or not limitations:
        raise ValueError(f"{row_id} must preserve limitations")

    covariance_group = uncertainty.get("covariance_group")
    if covariance_group is not None:
        covariance_group = _require_string(covariance_group, label=f"{row_id}.uncertainty.covariance_group")

    return AtomicClockDirectRow(
        row_id=row_id,
        row_class=row_class,
        observable_id=_require_string(row["observable_id"], label=f"{row_id}.observable_id"),
        value_kind=value_kind,
        units=units,
        split=split,
        total_uncertainty=total_uncertainty,
        confidence_level_label=confidence_level_label,
        bound_style=bound_style,
        covariance_reference=covariance_reference,
        covariance_group=covariance_group,
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


def load_atomic_clock_synthetic_cross_source_dataset(path: str | Path) -> AtomicClockSyntheticCrossSourceDataset:
    """Load a fabricated cross-source atomic-clock benchmark dry-run fixture."""
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    data = _require_mapping(payload, label="dataset")
    dataset_id = _require_string(data.get("dataset_id"), label="dataset_id")
    if data.get("task_id") != "TASK-0488":
        raise ValueError(f"{dataset_id} must be tied to TASK-0488")
    if data.get("synthetic") is not True:
        raise ValueError(f"{dataset_id} must be explicitly synthetic")
    if data.get("contains_real_clock_values") is not False:
        raise ValueError(f"{dataset_id} must declare contains_real_clock_values false")
    if data.get("benchmark_allowed") is not False:
        raise ValueError(f"{dataset_id} must not allow real benchmarks")
    if data.get("claim_promotion_allowed") is not False:
        raise ValueError(f"{dataset_id} must not allow claim promotion")

    dry_run = _require_mapping(data.get("cross_source_dry_run"), label=f"{dataset_id}.cross_source_dry_run")
    if dry_run.get("real_benchmark_unblocked") is not False:
        raise ValueError(f"{dataset_id} must not unblock real benchmark work")
    row_roles = _require_mapping(dry_run.get("row_roles"), label=f"{dataset_id}.cross_source_dry_run.row_roles")
    covariance_states = _require_mapping(
        dry_run.get("covariance_states"),
        label=f"{dataset_id}.cross_source_dry_run.covariance_states",
    )

    raw_rows = data.get("rows")
    if not isinstance(raw_rows, list) or len(raw_rows) < 2:
        raise ValueError(f"{dataset_id} must contain at least two synthetic rows")
    rows = tuple(
        _validate_synthetic_row(_require_mapping(row, label=f"{dataset_id}.row"), dataset_id=dataset_id)
        for row in raw_rows
    )
    row_ids = [row.row_id for row in rows]
    if len(set(row_ids)) != len(row_ids):
        raise ValueError(f"{dataset_id} row_id values must be unique")

    missing_roles = sorted(set(row_ids) - set(row_roles))
    if missing_roles:
        raise ValueError(f"{dataset_id} row_roles missing rows: {missing_roles}")
    for row_id, role in row_roles.items():
        _require_string(str(row_id), label=f"{dataset_id}.row_roles.key")
        role_value = _require_string(role, label=f"{dataset_id}.row_roles.{row_id}")
        if "real" in role_value.lower() or "beloy" in role_value.lower() or "nemitz" in role_value.lower():
            raise ValueError(f"{dataset_id} row roles must stay synthetic and not name real sources")

    for key, state in covariance_states.items():
        _require_string(str(key), label=f"{dataset_id}.covariance_states.key")
        state_value = _require_string(state, label=f"{dataset_id}.covariance_states.{key}")
        if not state_value.startswith("COV_SYNTHETIC_"):
            raise ValueError(f"{dataset_id} covariance states must use COV_SYNTHETIC_* labels")

    frequency_ratio_rows = [row for row in rows if row.value_kind == "frequency_ratio"]
    if len(frequency_ratio_rows) < 2:
        raise ValueError(f"{dataset_id} needs at least two synthetic frequency_ratio rows")

    return AtomicClockSyntheticCrossSourceDataset(
        dataset_id=dataset_id,
        task_id=str(data["task_id"]),
        rows=rows,
        row_roles={str(k): str(v) for k, v in row_roles.items()},
        covariance_states={str(k): str(v) for k, v in covariance_states.items()},
        row_class_counts=_counts([row.row_class for row in rows]),
        value_kind_counts=_counts([row.value_kind for row in rows]),
    )


def load_atomic_clock_direct_dataset(path: str | Path) -> AtomicClockDirectDataset:
    """Load and validate committed real direct atomic-clock measurement rows."""
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    data = _require_mapping(payload, label="dataset")
    dataset_id = _require_string(data.get("dataset_id"), label="dataset_id")
    task_id = _require_string(data.get("task_id"), label=f"{dataset_id}.task_id")

    scope = _require_mapping(data.get("scope"), label=f"{dataset_id}.scope")
    if scope.get("synthetic") is True:
        raise ValueError(f"{dataset_id} direct dataset must not be synthetic")
    for forbidden_flag in (
        "benchmark_allowed",
        "drift_fitting_allowed",
        "derived_constants_constraint_allowed",
        "claim_promotion_allowed",
        "prediction_registry_allowed",
    ):
        if scope.get(forbidden_flag) is not False:
            raise ValueError(f"{dataset_id} scope.{forbidden_flag} must be false for loader validation")

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

    covariance_groups = [row.covariance_group or "none" for row in rows]
    return AtomicClockDirectDataset(
        dataset_id=dataset_id,
        task_id=task_id,
        rows=rows,
        row_class_counts=_counts([row.row_class for row in rows]),
        value_kind_counts=_counts([row.value_kind for row in rows]),
        covariance_group_counts=_counts(covariance_groups),
    )
