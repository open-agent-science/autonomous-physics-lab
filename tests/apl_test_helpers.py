"""Shared, byte-identical test helpers extracted by TASK-0951.

Only helpers whose copies were AST-identical across test files live here;
file-local variants (different tolerances, bespoke factories) intentionally
stay in their test files. Keep additions to this module strictly generic.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


def _assert_nested_close(actual, expected, *, abs_tol: float = 1.0e-12) -> None:
    if isinstance(expected, dict):
        assert isinstance(actual, dict)
        assert set(actual) == set(expected)
        for key in expected:
            _assert_nested_close(actual[key], expected[key], abs_tol=abs_tol)
        return
    if isinstance(expected, list):
        assert isinstance(actual, list)
        assert len(actual) == len(expected)
        for actual_item, expected_item in zip(actual, expected):
            _assert_nested_close(actual_item, expected_item, abs_tol=abs_tol)
        return
    if isinstance(expected, float):
        assert actual == pytest.approx(expected, abs=abs_tol, rel=0.0)
        return
    assert actual == expected


def _stats_from_rmse(count: int, rmse: float | None) -> dict:
    return {
        "count": count,
        "log10_rmse": rmse,
        "log10_mae": None if rmse is None else rmse * 0.8,
        "log10_bias": 0.0,
        "log10_median": 0.0,
    }


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        payload = yaml.safe_load(fh)
    assert isinstance(payload, dict)
    return payload
