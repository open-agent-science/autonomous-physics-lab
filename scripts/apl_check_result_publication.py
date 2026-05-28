#!/usr/bin/env python3
"""Check AGENT_PUBLISHED RESULT/PRED artifacts against Gate A."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.result_publication_gate import check_artifact  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate agent-published RESULT/PRED artifacts against Gate A."
    )
    parser.add_argument("artifacts", nargs="+", help="YAML artifact paths to check.")
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root used for protected-artifact checks.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output.")
    args = parser.parse_args(argv)

    reports = [check_artifact(Path(path), root=args.root) for path in args.artifacts]
    if args.json:
        print(
            json.dumps(
                [
                    {
                        "artifact_path": report.artifact_path,
                        "artifact_kind": report.artifact_kind,
                        "review_tier": report.review_tier,
                        "ok": report.ok,
                        "issues": [
                            {
                                "code": issue.code,
                                "severity": issue.severity,
                                "message": issue.message,
                            }
                            for issue in report.issues
                        ],
                    }
                    for report in reports
                ],
                indent=2,
                sort_keys=True,
            )
        )
    else:
        for report in reports:
            status = "PASS" if report.ok else "FAIL"
            print(f"{status} {report.artifact_path} ({report.artifact_kind})")
            for issue in report.issues:
                print(f"- {issue.severity.upper()} {issue.code}: {issue.message}")

    return 0 if all(report.ok for report in reports) else 1


if __name__ == "__main__":
    sys.exit(main())
