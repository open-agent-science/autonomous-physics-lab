#!/usr/bin/env python3
"""Check public-facing repository files for maintainer-local path leaks."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


PUBLIC_SCAN_PATHS = (
    "README.md",
    "AGENTS.md",
    "CODEX_TASK.md",
    "docs",
    "claims",
    "knowledge",
    "results",
)


@dataclass(frozen=True)
class PathLeak:
    path: Path
    line_number: int
    label: str
    line: str


def _local_path_patterns() -> tuple[tuple[str, re.Pattern[str]], ...]:
    """Build patterns without embedding maintainer-specific absolute paths in docs."""
    users_root = "/" + "Users"
    private_tmp = "/" + "private" + "/" + "tmp"
    var_folders = "/" + "var" + "/" + "folders"
    return (
        ("macOS user home path", re.compile(re.escape(users_root) + r"/[^\s)>\"']+")),
        ("private temporary path", re.compile(re.escape(private_tmp))),
        ("macOS var folders path", re.compile(re.escape(var_folders))),
        ("machine-local host label", re.compile(r"\bMacBook\b")),
        ("encoded local workspace path", re.compile(r"Autonomous%20Physics%20Lab")),
    )


def _iter_files(root: Path, scan_paths: Sequence[str]) -> Iterable[Path]:
    for raw_path in scan_paths:
        path = root / raw_path
        if not path.exists():
            continue
        if path.is_file():
            yield path
            continue
        for child in sorted(path.rglob("*")):
            if child.is_file():
                yield child


def find_public_path_leaks(
    root: Path,
    scan_paths: Sequence[str] = PUBLIC_SCAN_PATHS,
) -> list[PathLeak]:
    leaks: list[PathLeak] = []
    patterns = _local_path_patterns()
    for path in _iter_files(root, scan_paths):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            for label, pattern in patterns:
                if pattern.search(line):
                    leaks.append(
                        PathLeak(
                            path=path.relative_to(root),
                            line_number=line_number,
                            label=label,
                            line=line.strip(),
                        )
                    )
    return leaks


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check public-facing files for maintainer-local path leaks."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root to scan. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--path",
        action="append",
        dest="paths",
        help="Path to scan. May be passed multiple times. Defaults to public-facing paths.",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    leaks = find_public_path_leaks(root, tuple(args.paths or PUBLIC_SCAN_PATHS))
    if not leaks:
        print("No public path leaks found.")
        return 0

    for leak in leaks:
        print(f"{leak.path}:{leak.line_number}: {leak.label}: {leak.line}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
