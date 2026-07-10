from __future__ import annotations

import pytest

from physics_lab.registry.yaml_io import SAFE_LOADER_NAME, load_yaml_mapping, safe_load_yaml


def test_safe_load_yaml_uses_safe_loader_family() -> None:
    assert SAFE_LOADER_NAME in {"CSafeLoader", "SafeLoader"}
    assert safe_load_yaml("alpha: 1\n") == {"alpha": 1}


def test_load_yaml_mapping_requires_mapping(tmp_path) -> None:
    path = tmp_path / "payload.yaml"
    path.write_text("- not\n- a\n- mapping\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Expected mapping in test payload"):
        load_yaml_mapping(path, expected="test payload")
