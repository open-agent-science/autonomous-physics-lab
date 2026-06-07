from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _load_conftest_module():
    path = Path(__file__).resolve().parent / "conftest.py"
    spec = importlib.util.spec_from_file_location("apl_tests_conftest", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pytest_sessionstart_fails_fast_on_unsupported_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_conftest_module()

    def unsupported_runtime() -> None:
        raise RuntimeError("unsupported runtime sentinel")

    monkeypatch.setattr(module, "_enforce_python_runtime", unsupported_runtime)

    with pytest.raises(pytest.exit.Exception) as exc_info:
        module.pytest_sessionstart(object())

    assert "unsupported runtime sentinel" in str(exc_info.value)
