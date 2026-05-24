"""Synthetic dry-run helpers for future nuclear prediction reveal workflows."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from math import sqrt
from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.nuclear_mass_predictions import load_nuclear_mass_prediction


ELIGIBLE_STATUS = "ELIGIBLE_SYNTHETIC"
TARGET_NOT_REVEALED = "TARGET_NOT_REVEALED"
NON_MEASURED_VALUE_ONLY = "NON_MEASURED_VALUE_ONLY"
SOURCE_PREDATES_REGISTRATION = "SOURCE_PREDATES_REGISTRATION"
UNIT_SEMANTICS_AMBIGUOUS = "UNIT_SEMANTICS_AMBIGUOUS"
NO_PEEK_AUDIT_FAILED = "NO_PEEK_AUDIT_FAILED"


def run_synthetic_reveal_dry_run(root: Path, config_path: Path) -> dict[str, Any]:
    """Run a synthetic reveal dry-run without mutating frozen registry entries."""
    root = root.resolve()
    config_path = config_path if config_path.is_absolute() else root / config_path
    config = load_synthetic_reveal_config(config_path)
    source = config["synthetic_source"]
    prediction_ids = tuple(str(item) for item in config["registry_snapshot"]["prediction_ids"])
    entries = [_load_registry_entry(root, prediction_id) for prediction_id in prediction_ids]
    source_rows = _source_rows_by_nuclide(source)

    comparison_rows: list[dict[str, Any]] = []
    for entry in entries:
        for target in entry["target_set"]["target_nuclides"]:
            row = _comparison_row(entry, target, source_rows.get(str(target["nuclide_id"])), source)
            comparison_rows.append(row)

    status_counts = Counter(str(row["eligibility_status"]) for row in comparison_rows)
    eligible_rows = [row for row in comparison_rows if row["eligible_for_synthetic_scoring"]]
    return {
        "task_id": "TASK-0273",
        "mode": "synthetic_reveal_dry_run",
        "config_path": str(config_path.relative_to(root)),
        "source": {
            "source_id": source["source_id"],
            "source_kind": source["source_kind"],
            "synthetic_source": True,
            "real_measurement_source": False,
            "source_label": source["source_label"],
            "source_available_utc": source["source_available_utc"],
        },
        "registry_snapshot": {
            "prediction_ids": list(prediction_ids),
            "entry_count": len(entries),
            "target_row_count": len(comparison_rows),
            "registry_files": [
                f"prediction_registry/nuclear_masses/{prediction_id}.yaml"
                for prediction_id in prediction_ids
            ],
        },
        "comparison_rows": comparison_rows,
        "coverage": {
            "target_rows": len(comparison_rows),
            "eligible_rows": len(eligible_rows),
            "unrevealed_rows": status_counts[TARGET_NOT_REVEALED],
            "ineligible_rows": len(comparison_rows) - len(eligible_rows) - status_counts[TARGET_NOT_REVEALED],
            "eligibility_status_counts": dict(sorted(status_counts.items())),
            "partial_reveal_fraction": _safe_fraction(len(eligible_rows), len(comparison_rows)),
        },
        "metrics": _synthetic_metrics(eligible_rows),
        "verdict": "INCONCLUSIVE_SYNTHETIC_DRY_RUN",
        "limitations": [
            "Synthetic dry-run only; rows are fake toy values, not measured nuclear data.",
            "No live external source is fetched or compared.",
            "Frozen prediction registry entries are read-only inputs.",
            "Metrics exercise plumbing only and must not be interpreted scientifically.",
        ],
    }


def load_synthetic_reveal_config(path: Path) -> dict[str, Any]:
    """Load a reveal dry-run fixture and enforce synthetic-source labeling."""
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in synthetic reveal config: {path}")
    if data.get("config_kind") != "nuclear_prediction_synthetic_reveal":
        raise ValueError("Synthetic reveal config must set config_kind.")
    source = data.get("synthetic_source")
    if not isinstance(source, dict):
        raise ValueError("Synthetic reveal config must include synthetic_source.")
    _require_synthetic_source(source)
    snapshot = data.get("registry_snapshot")
    if not isinstance(snapshot, dict) or not snapshot.get("prediction_ids"):
        raise ValueError("Synthetic reveal config must include registry_snapshot.prediction_ids.")
    return data


def _require_synthetic_source(source: dict[str, Any]) -> None:
    if source.get("synthetic_source") is not True:
        raise ValueError("Reveal dry-run source must set synthetic_source: true.")
    if source.get("real_measurement_source") is not False:
        raise ValueError("Reveal dry-run source must set real_measurement_source: false.")
    if source.get("source_kind") != "synthetic_toy_measurement":
        raise ValueError("Reveal dry-run source_kind must be synthetic_toy_measurement.")
    if not source.get("fake_source_warning"):
        raise ValueError("Reveal dry-run source must include a fake_source_warning.")
    rows = source.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Reveal dry-run source must include synthetic rows.")


def _load_registry_entry(root: Path, prediction_id: str) -> dict[str, Any]:
    path = root / "prediction_registry" / "nuclear_masses" / f"{prediction_id}.yaml"
    return load_nuclear_mass_prediction(path)


def _source_rows_by_nuclide(source: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for row in source["rows"]:
        if not isinstance(row, dict):
            raise ValueError("Synthetic source rows must be mappings.")
        nuclide_id = str(row.get("nuclide_id", ""))
        if not nuclide_id:
            raise ValueError("Synthetic source rows must include nuclide_id.")
        rows[nuclide_id] = row
    return rows


def _comparison_row(
    entry: dict[str, Any],
    target: dict[str, Any],
    source_row: dict[str, Any] | None,
    source: dict[str, Any],
) -> dict[str, Any]:
    base = {
        "prediction_id": entry["prediction_id"],
        "nuclide_id": target["nuclide_id"],
        "Z": target["Z"],
        "N": target["N"],
        "A": target["A"],
        "predicted_value_mev": target["predicted_value_mev"],
        "synthetic_value_mev": None,
        "signed_error_mev": None,
        "absolute_error_mev": None,
        "eligible_for_synthetic_scoring": False,
    }
    if source_row is None:
        return {
            **base,
            "eligibility_status": TARGET_NOT_REVEALED,
            "exclusion_reason": TARGET_NOT_REVEALED,
        }

    status = _eligibility_status(entry, target, source_row, source)
    synthetic_value = float(source_row["synthetic_value_mev"])
    signed_error = float(target["predicted_value_mev"]) - synthetic_value
    eligible = status == ELIGIBLE_STATUS
    return {
        **base,
        "synthetic_value_mev": synthetic_value,
        "signed_error_mev": signed_error if eligible else None,
        "absolute_error_mev": abs(signed_error) if eligible else None,
        "eligible_for_synthetic_scoring": eligible,
        "eligibility_status": status,
        "exclusion_reason": None if eligible else status,
    }


def _eligibility_status(
    entry: dict[str, Any],
    target: dict[str, Any],
    source_row: dict[str, Any],
    source: dict[str, Any],
) -> str:
    row_available = str(source_row.get("source_available_utc") or source["source_available_utc"])
    if _parse_utc(row_available) <= _parse_utc(str(entry["registered_at_utc"])):
        return SOURCE_PREDATES_REGISTRATION
    if source_row.get("value_semantics") != "measured_synthetic":
        return NON_MEASURED_VALUE_ONLY
    if source_row.get("unit") != "MeV" or source_row.get("quantity") != entry["target_set"]["quantity"]:
        return UNIT_SEMANTICS_AMBIGUOUS
    if source_row.get("no_peek_audit_passed") is False:
        return NO_PEEK_AUDIT_FAILED
    if str(source_row["nuclide_id"]) != str(target["nuclide_id"]):
        return TARGET_NOT_REVEALED
    return ELIGIBLE_STATUS


def _parse_utc(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _synthetic_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "eligible_count": 0,
            "mae_mev": None,
            "rmse_mev": None,
            "mean_signed_error_mev": None,
        }
    signed_errors = [float(row["signed_error_mev"]) for row in rows]
    absolute_errors = [abs(error) for error in signed_errors]
    return {
        "eligible_count": len(rows),
        "mae_mev": sum(absolute_errors) / len(absolute_errors),
        "rmse_mev": sqrt(sum(error * error for error in signed_errors) / len(signed_errors)),
        "mean_signed_error_mev": sum(signed_errors) / len(signed_errors),
    }


def _safe_fraction(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator
