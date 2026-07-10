"""Fast safe YAML loading helpers for registry artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, TextIO

import yaml

try:
    _SafeLoader = yaml.CSafeLoader
except AttributeError:  # pragma: no cover - depends on PyYAML build
    _SafeLoader = yaml.SafeLoader

SAFE_LOADER_NAME = _SafeLoader.__name__


def safe_load_yaml(stream: str | TextIO) -> Any:
    """Load YAML using LibYAML's safe loader when available."""
    loader = _SafeLoader(stream)
    try:
        return loader.get_single_data()
    finally:
        loader.dispose()


def load_yaml(path: str | Path) -> Any:
    """Load a YAML file with the repository's safe loader."""
    with Path(path).open("r", encoding="utf-8") as handle:
        return safe_load_yaml(handle)


def load_yaml_mapping(path: str | Path, *, expected: str) -> dict[str, Any]:
    """Load a YAML file and require a mapping payload."""
    data = load_yaml(path)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {expected}: {path}")
    return data
