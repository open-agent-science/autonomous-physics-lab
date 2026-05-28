#!/usr/bin/env python3
"""Build a maintainer-facing Scientific Campaign Director brief."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.campaign_curator import (  # noqa: E402
    SUPPORTED_CAMPAIGN_CURATOR_MODES,
    SUPPORTED_CAMPAIGN_CURATOR_OUTPUTS,
    build_campaign_brief,
    campaign_brief_json,
    render_campaign_brief,
    render_campaign_role_instructions,
)


def build_parser() -> argparse.ArgumentParser:
    """Create the Campaign Curator parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Print an advisory campaign-level brief for a maintainer-run "
            "Scientific Campaign Director agent. Scientific Campaign Curator "
            "and campaign-curator remain accepted aliases."
        )
    )
    parser.add_argument(
        "--campaign",
        help="Campaign id. Defaults to the top-ranked campaign in missions/current.yaml.",
    )
    parser.add_argument(
        "--mode",
        choices=SUPPORTED_CAMPAIGN_CURATOR_MODES,
        default="cycle-review",
        help="Curator mode. Defaults to cycle-review.",
    )
    parser.add_argument(
        "--role",
        choices=("director", "curator"),
        default="director",
        help=(
            "Role framing for the brief. `director` is the current stronger "
            "campaign-direction role; `curator` is the backward-compatible alias."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Backward-compatible alias for --output json.",
    )
    parser.add_argument(
        "--agent-prompt",
        action="store_true",
        help="Backward-compatible alias for --output agent.",
    )
    parser.add_argument(
        "--output",
        choices=SUPPORTED_CAMPAIGN_CURATOR_OUTPUTS,
        default="brief",
        help=(
            "Output format. `brief` is human-readable, `json` is machine-readable, "
            "and `agent` prints role activation instructions."
        ),
    )
    parser.add_argument(
        "--root",
        default=str(REPO_ROOT),
        help="Repository root. Defaults to the checkout containing this script.",
    )
    return parser


def main() -> int:
    """Run the Campaign Curator entrypoint."""
    args = build_parser().parse_args()
    root = Path(args.root).resolve()
    brief = build_campaign_brief(
        root,
        campaign_id=args.campaign,
        mode=args.mode,
        role=args.role,
    )
    output = args.output
    if args.agent_prompt:
        output = "agent"
    elif args.json:
        output = "json"

    if output == "agent":
        print(render_campaign_role_instructions(brief))
    elif output == "json":
        print(campaign_brief_json(brief))
    else:
        print(render_campaign_brief(brief))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
