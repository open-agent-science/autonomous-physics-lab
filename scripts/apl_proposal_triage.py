#!/usr/bin/env python3
"""Triage the task-proposal pool: effective state, drift, routing, duplicates.

This is the Stage 0/1 tool of the proposal-pool processing architecture
(docs/proposal-pool-triage.md). It is advisory: it reports what each proposal's
effective state is, where declared status drifts from it, which role should act,
and which proposals look like possible duplicates. It never edits a proposal or
sets REJECTED/SUPERSEDED on its own.
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
        "--role",
        choices=["scientific-director", "architect", "review-agent"],
        help="Only show proposals routed to this role.",
    )
    return parser


def _state_dict(state) -> dict:
    return {
        "path": state.path,
        "proposal_id": state.proposal_id,
        "title": state.title,
        "declared_status": state.declared_status,
        "effective_state": state.effective_state,
        "linked_task_id": state.linked_task_id,
        "linked_task_status": state.linked_task_status,
        "is_science": state.is_science,
        "routing_target": state.routing_target,
        "drift": list(state.drift),
    }


def _print_human(report, role_filter: str | None) -> None:
    counts = report.counts()
    sys.stdout.write("Proposal pool triage\n")
    sys.stdout.write(
        f"- total: {len(report.states)} | "
        + " | ".join(f"{key}: {value}" for key, value in sorted(counts.items()))
        + "\n"
    )
    sys.stdout.write(
        f"- suggested routing: scientific-director {len(report.routed_to('scientific-director'))}, "
        f"architect {len(report.routed_to('architect'))}, "
        f"review-agent {len(report.routed_to('review-agent'))}, "
        f"unrouted {len(report.routed_to('unrouted'))}\n"
    )
    sys.stdout.write(
        "- routing is a suggestion: every role may read all pending proposals "
        "and self-select; unrouted ones especially need an agent to judge fit.\n\n"
    )

    drifting = report.drifting()
    if drifting and not role_filter:
        sys.stdout.write(f"Status drift ({len(drifting)}) -> review-agent / maintainer closeout:\n")
        for state in drifting:
            sys.stdout.write(f"- {state.path}\n")
            for reason in state.drift:
                sys.stdout.write(f"    drift: {reason}\n")
        sys.stdout.write("\n")

    closeouts = report.suggested_closeouts()
    if closeouts and not role_filter:
        sys.stdout.write(f"Suggested closeouts ({len(closeouts)}) — canonical task is DONE:\n")
        for state in closeouts:
            sys.stdout.write(
                f"- {state.path}: set status ACCEPTED "
                f"(delivered via {state.linked_task_id})\n"
            )
        sys.stdout.write("\n")

    if not role_filter or role_filter == "scientific-director":
        director = report.routed_to("scientific-director")
        if director:
            sys.stdout.write(f"Pending -> Scientific Campaign Director ({len(director)}):\n")
            for state in director:
                sys.stdout.write(f"- {state.path}: {state.title}\n")
            sys.stdout.write("\n")

    if not role_filter or role_filter == "architect":
        architect = report.routed_to("architect")
        if architect:
            sys.stdout.write(f"Pending -> Architect ({len(architect)}):\n")
            for state in architect:
                sys.stdout.write(f"- {state.path}: {state.title}\n")
            sys.stdout.write("\n")

    if not role_filter:
        unrouted = report.routed_to("unrouted")
        if unrouted:
            sys.stdout.write(
                f"Pending -> unrouted ({len(unrouted)}) — any role may claim if in scope:\n"
            )
            for state in unrouted:
                sys.stdout.write(f"- {state.path}: {state.title}\n")
            sys.stdout.write("\n")

    if report.duplicates and not role_filter:
        sys.stdout.write(
            f"Possible duplicates ({len(report.duplicates)}) — low-confidence advisory only; "
            "an agent decides, never the script:\n"
        )
        for candidate in report.duplicates:
            sys.stdout.write(
                f"- {candidate.left} <> {candidate.right} "
                f"(shared: {', '.join(candidate.shared)})\n"
            )
        sys.stdout.write("\n")


def main() -> int:
    from physics_lab.registry.proposal_triage import triage_pool

    args = build_parser().parse_args()
    report = triage_pool(args.root)

    if args.json:
        states = report.routed_to(args.role) if args.role else report.states
        payload = {
            "counts": report.counts(),
            "routing": {
                "scientific-director": len(report.routed_to("scientific-director")),
                "architect": len(report.routed_to("architect")),
                "review-agent": len(report.routed_to("review-agent")),
                "unrouted": len(report.routed_to("unrouted")),
            },
            "proposals": [_state_dict(state) for state in states],
            "duplicates": [
                {"left": d.left, "right": d.right, "shared": list(d.shared)}
                for d in report.duplicates
            ],
            "suggested_closeouts": [state.path for state in report.suggested_closeouts()],
        }
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        return 0

    _print_human(report, args.role)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
