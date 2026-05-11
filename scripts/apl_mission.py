#!/usr/bin/env python3
"""Show the research-first APL mission menu for humans and coding agents."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.mission_control import (  # noqa: E402
    SUPPORTED_MODES,
    load_current_missions,
    mission_json,
    render_agent_prompt,
    render_human_mission,
)


def build_parser() -> argparse.ArgumentParser:
    """Create the mission-control argument parser."""
    parser = argparse.ArgumentParser(
        description="Print the Agent First mission menu for Autonomous Physics Lab."
    )
    parser.add_argument(
        "--mode",
        choices=SUPPORTED_MODES,
        help="Mission mode. Defaults to the research-first mode from missions/current.yaml.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a compact machine-readable mission recommendation.",
    )
    parser.add_argument(
        "--agent-prompt",
        action="store_true",
        help="Emit a copy-paste prompt for Codex, Claude Code, or another coding agent.",
    )
    parser.add_argument(
        "--root",
        default=str(REPO_ROOT),
        help="Repository root. Defaults to the checkout containing this script.",
    )
    return parser


def main() -> int:
    """Run the mission-control entrypoint."""
    args = build_parser().parse_args()
    root = Path(args.root).resolve()
    payload = load_current_missions(root)
    if args.agent_prompt:
        print(render_agent_prompt(payload, root=root))
    elif args.json:
        print(mission_json(payload, args.mode, root=root))
    else:
        print(render_human_mission(payload, args.mode, root=root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
