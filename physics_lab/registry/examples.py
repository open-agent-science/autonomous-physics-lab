"""Example configuration helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.validation import validate_document


def load_example_config(path: str | Path) -> dict[str, Any]:
    """Load and validate an example config."""
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in example config file: {path}")
    if _is_nuclear_prediction_variant_factory_config(data):
        from physics_lab.engines.nuclear_prediction_variants import generate_variant_slate

        repo_root = config_path.resolve().parents[1]
        generate_variant_slate(data, repo_root=repo_root, write_drafts=False)
        return {"config_kind": "nuclear_prediction_variant_factory", **data}
    if data.get("config_kind") == "nuclear_prediction_synthetic_reveal":
        from physics_lab.engines.nuclear_prediction_reveal import load_synthetic_reveal_config

        return load_synthetic_reveal_config(config_path)
    return validate_document(data, kind="example_config", source=path)


def _is_nuclear_prediction_variant_factory_config(data: dict[str, Any]) -> bool:
    return (
        "factory_id" in data
        and "baseline_model" in data
        and ("target_batches" in data or "target_batch_library" in data)
        and "variants" in data
    )
