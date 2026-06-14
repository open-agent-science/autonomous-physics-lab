#!/usr/bin/env python3
"""Report or validate the metadata-only source acquisition queue."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    """Create the acquisition queue CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    report = subparsers.add_parser(
        "report",
        help="Print a dry-run maintainer action report without fetching sources.",
    )
    report.add_argument("--queue", default="data/acquisition_queue.yaml")
    report.add_argument("--json", action="store_true", help="Print validated queue JSON.")

    validate = subparsers.add_parser("validate", help="Validate the queue and print errors.")
    validate.add_argument("--queue", default="data/acquisition_queue.yaml")

    return parser


def command_report(args: argparse.Namespace) -> int:
    """Print the metadata-only dry-run report."""
    from physics_lab.registry.acquisition_queue import (
        acquisition_queue_errors,
        load_acquisition_queue,
        render_acquisition_queue_report,
    )

    queue_path = Path(args.queue)
    payload = load_acquisition_queue(queue_path)
    errors = acquisition_queue_errors(payload)
    if errors:
        for error in errors:
            sys.stderr.write(f"ERROR: {error}\n")
        return 1
    if args.json:
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=False))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_acquisition_queue_report(payload, queue_path=queue_path))
    return 0


def command_validate(args: argparse.Namespace) -> int:
    """Validate the queue without printing a report."""
    from physics_lab.registry.acquisition_queue import (
        acquisition_queue_errors,
        load_acquisition_queue,
    )

    queue_path = Path(args.queue)
    payload = load_acquisition_queue(queue_path)
    errors = acquisition_queue_errors(payload)
    if errors:
        sys.stdout.write("Acquisition queue validation: FAIL\n")
        for error in errors:
            sys.stdout.write(f"- {error}\n")
        return 1
    sys.stdout.write("Acquisition queue validation: PASS\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the acquisition queue CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "report":
        return command_report(args)
    if args.command == "validate":
        return command_validate(args)
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
