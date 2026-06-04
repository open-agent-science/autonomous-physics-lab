#!/usr/bin/env python3
"""Resolve a canonical task id to its file path (active or archived).

Makes finding a past task one command, regardless of whether it sits flat under
``tasks/`` or in a future ``tasks/archive/<bucket>/`` directory.

Examples::

    python3 scripts/apl_task_path.py TASK-0559
    python3 scripts/apl_task_path.py 559            # bare number is accepted
    python3 scripts/apl_task_path.py --list         # all canonical task ids -> path
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from physics_lab.registry.task_discovery import (  # noqa: E402
    find_task_file,
    iter_canonical_task_files,
    task_id_from_path,
)


def _normalize(task_id: str) -> str:
    text = task_id.strip()
    if text.upper().startswith("TASK-"):
        return text.upper()
    return f"TASK-{int(text):04d}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id", nargs="?", help="canonical id, e.g. TASK-0559 (or bare 559)")
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    parser.add_argument("--list", action="store_true", help="list all canonical task ids and paths")
    args = parser.parse_args(argv)

    root = Path(args.root)

    if args.list:
        for path in iter_canonical_task_files(root):
            print(f"{task_id_from_path(path)}\t{path.relative_to(root)}")
        return 0

    if not args.task_id:
        parser.error("task_id is required unless --list is given")

    try:
        task_id = _normalize(args.task_id)
    except ValueError:
        print(f"invalid task id: {args.task_id!r}", file=sys.stderr)
        return 2

    path = find_task_file(root, task_id)
    if path is None:
        print(f"{task_id}: not found", file=sys.stderr)
        return 1
    print(path.relative_to(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
