"""Example configuration helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.validation import validate_document


TEXTBOOK_WIEN_FIXTURE_CONFIG_KIND = "textbook_wien_exact_reference_fixture"
QUANTUM_SIZE_EFFECTS_BASELINE_CONFIG_KIND = "quantum_size_effects_baseline"


def load_example_config(path: str | Path) -> dict[str, Any]:
    """Load and validate an example config."""
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in example config file: {path}")
    if _is_textbook_wien_fixture_config(data):
        # TASK-0537 allows an exact-reference fixture/config. The repository
        # also stores a copy under examples/ for discoverability, but it is not
        # a runnable benchmark config and must not point at unrelated results.
        return {
            "config_kind": TEXTBOOK_WIEN_FIXTURE_CONFIG_KIND,
            "task_id": "TASK-0537",
            "wien_fixture": data,
        }
    if _is_nuclear_prediction_variant_factory_config(data):
        from physics_lab.engines.nuclear_prediction_variants import generate_variant_slate

        repo_root = config_path.resolve().parents[1]
        generate_variant_slate(data, repo_root=repo_root, write_drafts=False)
        return {"config_kind": "nuclear_prediction_variant_factory", **data}
    if data.get("config_kind") == "nuclear_prediction_synthetic_reveal":
        from physics_lab.engines.nuclear_prediction_reveal import load_synthetic_reveal_config

        return load_synthetic_reveal_config(config_path)
    if data.get("config_kind") == QUANTUM_SIZE_EFFECTS_BASELINE_CONFIG_KIND:
        return _validate_quantum_size_effects_baseline_config(data, source=path)
    return validate_document(data, kind="example_config", source=path)


def _is_nuclear_prediction_variant_factory_config(data: dict[str, Any]) -> bool:
    return (
        "factory_id" in data
        and "baseline_model" in data
        and ("target_batches" in data or "target_batch_library" in data)
        and "variants" in data
    )


def _is_textbook_wien_fixture_config(data: dict[str, Any]) -> bool:
    return (
        data.get("id") == "textbook-wien-displacement-exact-reference"
        and data.get("campaign") == "textbook_formula_audit"
        and data.get("formula") == "wien_displacement_wavelength_domain"
    )


def _validate_quantum_size_effects_baseline_config(
    data: dict[str, Any],
    *,
    source: str | Path,
) -> dict[str, Any]:
    required = {
        "config_kind": str,
        "task_id": str,
        "campaign_profile_id": str,
        "dataset_path": str,
        "pre_reveal_path": str,
        "output_dir": str,
        "summary_path": str,
        "holdout_entry_id": str,
        "shuffle_seed": int,
        "required_holdout_improvement_ev": (int, float),
    }
    missing = sorted(set(required) - set(data))
    if missing:
        raise ValueError(f"Missing quantum baseline config fields in {source}: {missing}")

    unexpected = sorted(set(data) - set(required))
    if unexpected:
        raise ValueError(f"Unexpected quantum baseline config fields in {source}: {unexpected}")

    for field, expected_type in required.items():
        value = data[field]
        if not isinstance(value, expected_type) or isinstance(value, bool):
            raise ValueError(
                f"Invalid quantum baseline config field {field!r} in {source}: "
                f"expected {expected_type}, got {type(value).__name__}"
            )
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"Empty quantum baseline config field {field!r} in {source}")

    if data["config_kind"] != QUANTUM_SIZE_EFFECTS_BASELINE_CONFIG_KIND:
        raise ValueError(f"Unsupported quantum baseline config kind in {source}")
    if data["task_id"] != "TASK-0225":
        raise ValueError(f"Quantum baseline config must be bound to TASK-0225 in {source}")
    if data["shuffle_seed"] < 0:
        raise ValueError(f"shuffle_seed must be non-negative in {source}")
    if data["required_holdout_improvement_ev"] <= 0:
        raise ValueError(f"required_holdout_improvement_ev must be positive in {source}")
    return data
