#!/usr/bin/env python3
"""Fast cross-platform inner-loop validation for agents and maintainers."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    printable = " ".join(command)
    print(f"$ {printable}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main(argv: list[str]) -> int:
    run([sys.executable, "-m", "ruff", "check", "."])
    run([sys.executable, "-m", "pytest", "-m", "not full_repo", *argv])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
