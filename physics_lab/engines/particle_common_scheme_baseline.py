"""Deterministic common-scheme hierarchy baseline for pinned quark Yukawas."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any

import yaml


EXPECTED_PARAMETERS = {"y_u", "y_d", "y_s", "y_c", "y_b", "y_t"}
METRIC_ID = "geometric_midpoint_log10_residual_dex"


def _load_mapping(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a mapping in {path}")
    return payload


def sha256_file(path: Path) -> str:
    """Return a lowercase SHA-256 digest for one file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_contract(config_path: str | Path, *, root: str | Path) -> tuple[dict[str, Any], dict[str, Any], Path]:
    """Load and verify the frozen metric fixture and source artifact."""
    root_path = Path(root).resolve()
    config = _load_mapping(Path(config_path).resolve())
    source_spec = config["source"]
    source_path = root_path / str(source_spec["path"])
    actual_hash = sha256_file(source_path)
    if actual_hash != str(source_spec["sha256"]):
        raise ValueError(
            f"Source checksum mismatch: expected {source_spec['sha256']}, got {actual_hash}"
        )
    source = _load_mapping(source_path)
    if source.get("dataset_id") != source_spec.get("dataset_id"):
        raise ValueError("Source dataset_id does not match the frozen fixture")

    required_surface = source_spec["required_surface"]
    surface = source.get("surface", {})
    for key, expected in required_surface.items():
        if surface.get(key) != expected:
            raise ValueError(
                f"Source surface mismatch for {key}: expected {expected!r}, got {surface.get(key)!r}"
            )

    contract = config["metric_contract"]
    if contract.get("frozen_before_scoring") is not True:
        raise ValueError("Metric contract must be frozen before scoring")
    if contract.get("procedural_not_blind") is not True:
        raise ValueError("Metric contract must disclose that predeclaration is procedural")
    if contract.get("metric_id") != METRIC_ID:
        raise ValueError(f"Unsupported metric_id: {contract.get('metric_id')}")
    if contract.get("success_threshold") is not None:
        raise ValueError("This diagnostic must not define a post-hoc quality threshold")
    return config, source, source_path


def compute_metrics(config: dict[str, Any], source: dict[str, Any], *, source_sha256: str) -> dict[str, Any]:
    """Compute the predeclared zero-parameter log-spacing diagnostic."""
    entries = source.get("entries", [])
    values = {str(row["parameter"]): float(row["central_value"]) for row in entries}
    if set(values) != EXPECTED_PARAMETERS:
        raise ValueError(
            f"Expected exactly {sorted(EXPECTED_PARAMETERS)}, got {sorted(values)}"
        )
    if any(value <= 0.0 or not math.isfinite(value) for value in values.values()):
        raise ValueError("All Yukawa values must be finite and positive")

    sector_rows: list[dict[str, Any]] = []
    residuals: list[float] = []
    for sector in config["sectors"]:
        ordered = list(sector["ordered_parameters"])
        if len(ordered) != 3 or len(set(ordered)) != 3:
            raise ValueError(f"Sector {sector['id']} must contain three distinct parameters")
        light, middle, heavy = (values[name] for name in ordered)
        if not light < middle < heavy:
            raise ValueError(f"Sector {sector['id']} is not strictly ordered by value")
        predicted_middle = math.sqrt(light * heavy)
        signed_residual = math.log10(middle / predicted_middle)
        residuals.append(signed_residual)
        sector_rows.append(
            {
                "sector_id": str(sector["id"]),
                "ordered_parameters": ordered,
                "light_yukawa": light,
                "observed_middle_yukawa": middle,
                "heavy_yukawa": heavy,
                "predicted_middle_yukawa": predicted_middle,
                "signed_residual_dex": signed_residual,
                "absolute_residual_dex": abs(signed_residual),
                "multiplicative_deviation_factor": 10.0 ** abs(signed_residual),
            }
        )

    count = len(residuals)
    mean_abs = sum(abs(value) for value in residuals) / count
    rmse = math.sqrt(sum(value * value for value in residuals) / count)
    return {
        "benchmark_id": str(config["benchmark_id"]),
        "task_id": str(config["task_id"]),
        "agent_run_id": str(config["agent_run_id"]),
        "campaign_profile_id": str(config["campaign_profile_id"]),
        "generated_at_utc": str(config["generated_at_utc"]),
        "source": {
            "path": str(config["source"]["path"]),
            "sha256": source_sha256,
            "dataset_id": str(source["dataset_id"]),
            "representation": str(source["surface"]["representation"]),
            "renormalization_scheme": str(source["surface"]["renormalization_scheme"]),
            "renormalization_scale": str(source["surface"]["renormalization_scale"]),
            "units": str(source["surface"]["units"]),
            "entry_count": len(entries),
        },
        "metric_contract": config["metric_contract"],
        "sectors": sector_rows,
        "aggregate": {
            "sector_count": count,
            "mean_signed_residual_dex": sum(residuals) / count,
            "mean_absolute_residual_dex": mean_abs,
            "root_mean_square_residual_dex": rmse,
            "maximum_absolute_residual_dex": max(abs(value) for value in residuals),
        },
        "verdict": "INCONCLUSIVE",
        "routing": {
            "sandbox_only": True,
            "canonical_result_created": False,
            "claim_or_knowledge_changed": False,
            "reason": "No predeclared quality threshold and only two descriptive sectors.",
        },
    }


def run_from_config(config_path: str | Path, *, root: str | Path) -> dict[str, Any]:
    """Load verified committed inputs and compute the benchmark payload."""
    config, source, source_path = load_contract(config_path, root=root)
    return compute_metrics(config, source, source_sha256=sha256_file(source_path))


__all__ = ["METRIC_ID", "compute_metrics", "load_contract", "run_from_config", "sha256_file"]
