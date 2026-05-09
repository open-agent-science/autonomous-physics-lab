#!/usr/bin/env python3
"""Summarize an autonomous sandbox agent run into PR-ready maintainer context."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_helper():
    from physics_lab.registry.agent_run_pr import build_agent_run_pr_context

    return build_agent_run_pr_context


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("agent_run_path", help="Path to agent_runs/<id>/agent_run.yaml")
    parser.add_argument("--root", default=".", help="Repository root. Default: current directory.")
    parser.add_argument("--output-file", help="Optional Markdown file to write instead of stdout.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    build_agent_run_pr_context = _load_helper()
    context = build_agent_run_pr_context(args.agent_run_path, root=args.root)
    if args.output_file:
        Path(args.output_file).write_text(context, encoding="utf-8")
    else:
        sys.stdout.write(context)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
