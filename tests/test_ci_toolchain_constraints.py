"""Regression checks for deterministic CI-critical development tools."""

from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_merge_group_ruff_version_is_exactly_pinned() -> None:
    """Fresh merge-group installs must not silently change the lint baseline."""
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dev_requirements = metadata["project"]["optional-dependencies"]["dev"]
    ruff_requirements = [
        requirement
        for requirement in dev_requirements
        if requirement.partition("==")[0].partition(">=")[0] == "ruff"
    ]

    assert ruff_requirements == ["ruff==0.15.22"]
