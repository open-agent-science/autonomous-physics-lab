from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_fast.py"
SPEC = importlib.util.spec_from_file_location("validate_fast", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_validate_fast_runs_cheap_gates_before_parallel_pytest(monkeypatch) -> None:
    commands: list[list[str]] = []
    monkeypatch.setattr(MODULE, "run", commands.append)
    monkeypatch.setattr(MODULE.platform, "system", lambda: "Linux")

    assert MODULE.main(["--basetemp=C:/tmp/apl-pytest-test", "tests/test_example.py"]) == 0

    assert commands == [
        [sys.executable, "-m", "ruff", "check", "."],
        [
            sys.executable,
            "-m",
            "physics_lab.cli",
            "validate-repo",
            ".",
            "--strict",
            "--fail-on-warnings",
        ],
        [
            sys.executable,
            "-m",
            "pytest",
            "--durations=10",
            "-m",
            "not full_repo",
            "--basetemp=C:/tmp/apl-pytest-test",
            "tests/test_example.py",
        ],
    ]


def test_adaptive_pytest_args_adds_short_unique_windows_basetemp(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(MODULE.platform, "system", lambda: "Windows")
    monkeypatch.setenv("APL_PYTEST_BASETEMP_ROOT", str(tmp_path))
    monkeypatch.setattr(MODULE.uuid, "uuid4", lambda: type("UUID", (), {"hex": "abcd1234efgh"})())

    args = MODULE.adaptive_pytest_args(["tests/test_example.py"])

    assert args[0].startswith("--basetemp=")
    assert Path(args[0].split("=", 1)[1]) == tmp_path / "apl-pytest-abcd1234efgh"
    assert args[1:] == ["tests/test_example.py"]


def test_adaptive_pytest_args_falls_back_to_workspace_basetemp(
    monkeypatch,
) -> None:
    monkeypatch.setattr(MODULE.platform, "system", lambda: "Windows")
    monkeypatch.delenv("APL_PYTEST_BASETEMP_ROOT", raising=False)
    monkeypatch.setattr(MODULE.uuid, "uuid4", lambda: type("UUID", (), {"hex": "abcd1234efgh"})())

    attempted: list[Path] = []

    def fake_ensure_directory(path: Path) -> None:
        attempted.append(path)
        if path == Path("C:/tmp"):
            raise PermissionError("blocked test temp root")

    monkeypatch.setattr(MODULE, "_ensure_directory", fake_ensure_directory)

    args = MODULE.adaptive_pytest_args(["tests/test_example.py"])

    assert attempted == [Path("C:/tmp"), MODULE.ROOT / ".pytest-basetemp"]
    assert Path(args[0].split("=", 1)[1]) == (
        MODULE.ROOT / ".pytest-basetemp" / "session-abcd1234efgh"
    )
    assert args[1:] == ["tests/test_example.py"]


def test_windows_fast_lane_isolates_resource_sensitive_group(monkeypatch) -> None:
    monkeypatch.setattr(MODULE.platform, "system", lambda: "Windows")

    commands = MODULE.pytest_commands(["--basetemp=C:/tmp/apl-pytest-test"])

    assert commands == [
        [
            sys.executable,
            "-m",
            "pytest",
            "--durations=10",
            "-m",
            "not full_repo and not resource_sensitive",
            "--basetemp=C:/tmp/apl-pytest-test",
        ],
        [
            sys.executable,
            "-m",
            "pytest",
            "--durations=10",
            "-n0",
            "-m",
            "resource_sensitive and not full_repo",
            "--basetemp=C:/tmp/apl-pytest-test",
        ],
    ]
