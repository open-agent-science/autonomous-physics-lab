#!/usr/bin/env python3
"""Advisory mission-drift checker (TASK-0497).

Reports when missions/current.yaml routes agents into work canonical state no
longer supports: recommended actions pointing at DONE/BLOCKED/REJECTED/
SUPERSEDED/PROPOSED tasks, references to missing tasks, and mission campaign
recommendations that conflict with campaign_profiles/_catalog.yaml.

Advisory by default (exit 0). Pass --strict to exit non-zero when drift is
found. It never rewrites missions/current.yaml. It complements the existing
mission_freshness checks that run under validate-repo --strict.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when drift (not just advisory transient notices) is found.",
    )
    return parser


def main() -> int:
    from physics_lab.registry.mission_drift import check_mission_drift

    args = build_parser().parse_args()
    report = check_mission_drift(args.root)
    drift = report.drift_items()

    if args.json:
        payload = {
            "drift_count": len(drift),
            "items": [
                {
                    "kind": item.kind,
                    "owner": item.owner,
                    "detail": item.detail,
                    "advisory_only": item.advisory_only,
                }
                for item in report.items
            ],
        }
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        return 1 if (args.strict and drift) else 0

    sys.stdout.write("Mission drift check\n")
    if not report.items:
        sys.stdout.write("- no mission drift detected.\n")
        return 0
    if drift:
        sys.stdout.write(f"Drift ({len(drift)}):\n")
        for item in drift:
            sys.stdout.write(f"- [{item.kind}] {item.owner}: {item.detail}\n")
    advisory = [item for item in report.items if item.advisory_only]
    if advisory:
        sys.stdout.write(f"Advisory ({len(advisory)}) — transient, no action needed:\n")
        for item in advisory:
            sys.stdout.write(f"- [{item.kind}] {item.owner}: {item.detail}\n")
    return 1 if (args.strict and drift) else 0


if __name__ == "__main__":
    raise SystemExit(main())
