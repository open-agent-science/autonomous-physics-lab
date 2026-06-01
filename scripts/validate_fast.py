#!/usr/bin/env python3
"""Fast cross-platform inner-loop validation for agents and maintainers."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path
import uuid


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    printable = " ".join(command)
    print(f"$ {printable}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def adaptive_pytest_args(argv: list[str]) -> list[str]:
    """Add a short unique Windows basetemp unless the caller chose one."""
    if platform.system() != "Windows" or any(arg.startswith("--basetemp") for arg in argv):
        return argv
    root = Path(os.environ.get("APL_PYTEST_BASETEMP_ROOT", "C:/tmp"))
    root.mkdir(parents=True, exist_ok=True)
    return [f"--basetemp={root / f'apl-pytest-{uuid.uuid4().hex[:12]}'}", *argv]


def pytest_commands(pytest_args: list[str]) -> list[list[str]]:
    """Build the platform-specific fast pytest layers."""
    command = [
        sys.executable,
        "-m",
        "pytest",
        "--durations=10",
    ]
    if platform.system() != "Windows":
        return [[*command, "-m", "not full_repo", *pytest_args]]
    return [
        [*command, "-m", "not full_repo and not resource_sensitive", *pytest_args],
        [
            *command,
            "-n0",
            "-m",
            "resource_sensitive and not full_repo",
            *pytest_args,
        ],
    ]


def main(argv: list[str]) -> int:
    pytest_args = adaptive_pytest_args(argv)
    run([sys.executable, "-m", "ruff", "check", "."])
    run(
        [
            sys.executable,
            "-m",
            "physics_lab.cli",
            "validate-repo",
            ".",
            "--strict",
            "--fail-on-warnings",
        ]
    )
    for command in pytest_commands(pytest_args):
        run(command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
