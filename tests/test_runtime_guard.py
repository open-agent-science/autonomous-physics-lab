from __future__ import annotations

import pytest

from physics_lab._runtime import (
    MINIMUM_PYTHON,
    MINIMUM_PYTHON_DISPLAY,
    enforce,
    is_supported,
    unsupported_message,
)


def test_minimum_matches_requires_python() -> None:
    assert MINIMUM_PYTHON == (3, 11)
    assert MINIMUM_PYTHON_DISPLAY == "3.11"


def test_is_supported_boundaries() -> None:
    assert is_supported((3, 11, 0)) is True
    assert is_supported((3, 12, 5)) is True
    assert is_supported((4, 0, 0)) is True
    assert is_supported((3, 10, 9)) is False
    assert is_supported((3, 9, 6)) is False


def test_enforce_raises_actionable_message_on_old_python() -> None:
    with pytest.raises(RuntimeError) as exc_info:
        enforce((3, 9, 6))
    message = str(exc_info.value)
    assert "Python 3.11+" in message
    assert ".venv" in message
    assert "3.9.6" in message


def test_enforce_is_noop_on_supported_python() -> None:
    # Must not raise.
    enforce((3, 11, 0))
    enforce((3, 12, 0))
    enforce((4, 0, 0))


def test_unsupported_message_is_cross_platform() -> None:
    message = unsupported_message((3, 10, 0))
    assert 'pip install -e ".[dev]"' in message
    # Mentions both activation styles so Windows and Unix users are covered.
    assert "macOS/Linux" in message
    assert "Windows" in message
