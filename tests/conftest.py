"""Pytest session guardrails shared by the full test suite."""

from __future__ import annotations

import pytest

from physics_lab._runtime import enforce as _enforce_python_runtime


def pytest_sessionstart(session: pytest.Session) -> None:
    """Fail fast when pytest is launched with an unsupported interpreter."""
    try:
        _enforce_python_runtime()
    except RuntimeError as exc:
        pytest.exit(str(exc), returncode=2)
