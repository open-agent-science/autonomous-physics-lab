#!/usr/bin/env python3
"""Run Gate B independent replay validation for an AGENT_PUBLISHED RESULT."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.agent_replay_validation import (  # noqa: E402
    ReplayReport,
    ReplayIdentity,
    validate_agent_published_result,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an AGENT_PUBLISHED RESULT with Gate B independent replay."
    )
    parser.add_argument("result", help="Path to a canonical RESULT result.yaml.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument(
        "--output-dir",
        help="Replay output directory. If omitted, a temporary directory is used.",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=1.0e-9,
        help="Absolute tolerance for numeric metric comparisons.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output.")
    parser.add_argument(
        "--expect-status",
        choices=("PASS", "BLOCKED", "CONTESTED_RESULT"),
        help=(
            "Return success only when the replay report has this status. "
            "Without this option, only PASS is successful."
        ),
    )
    parser.add_argument(
        "--validator-contributor-id",
        required=True,
        help="Contributor ID of the validating agent/human.",
    )
    parser.add_argument(
        "--validator-github-username",
        required=True,
        help="GitHub username of the validating agent/human.",
    )
    parser.add_argument(
        "--validator-agent-tool",
        required=True,
        help="Agent tool performing replay, e.g. Codex or Claude Code.",
    )
    parser.add_argument(
        "--validator-model",
        required=True,
        help="Model/version performing replay, e.g. GPT-5 Codex.",
    )
    args = parser.parse_args(argv)

    report = validate_agent_published_result(
        args.result,
        root=args.root,
        output_dir=args.output_dir,
        tolerance=args.tolerance,
        replayed_by=ReplayIdentity(
            contributor_id=args.validator_contributor_id,
            github_username=args.validator_github_username,
            agent_tool=args.validator_agent_tool,
            model_version=args.validator_model,
        ),
    )

    if args.json:
        print(json.dumps(_report_to_dict(report), indent=2, sort_keys=True))
    else:
        _print_human_report(report)

    return _exit_code_for_report(report, expected_status=args.expect_status)


def _exit_code_for_report(report: ReplayReport, *, expected_status: str | None) -> int:
    if expected_status is not None:
        return 0 if report.status == expected_status else 1
    return 0 if report.ok else 1


def _report_to_dict(report: ReplayReport) -> dict:
    return {
        "result_path": report.result_path,
        "replay_output_dir": report.replay_output_dir,
        "status": report.status,
        "ok": report.ok,
        "issues": [
            {"code": issue.code, "severity": issue.severity, "message": issue.message}
            for issue in report.issues
        ],
        "metric_deltas": [
            {
                "path": delta.path,
                "expected": delta.expected,
                "observed": delta.observed,
                "abs_delta": delta.abs_delta,
                "tolerance": delta.tolerance,
                "ok": delta.ok,
            }
            for delta in report.metric_deltas
        ],
        "validation_record": report.validation_record,
        "contested_report": report.contested_report,
    }


def _print_human_report(report: ReplayReport) -> None:
    print(f"Gate B {report.status}: {report.result_path}")
    if report.replay_output_dir:
        print(f"Replay output: {report.replay_output_dir}")
    for issue in report.issues:
        print(f"- {issue.severity.upper()} {issue.code}: {issue.message}")
    if report.validation_record is not None:
        print("")
        print("Validation record draft:")
        print(yaml.safe_dump(report.validation_record, sort_keys=False).strip())
    if report.contested_report is not None:
        print("")
        print(report.contested_report)


if __name__ == "__main__":
    sys.exit(main())
