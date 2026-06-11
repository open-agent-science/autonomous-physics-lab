"""Generate a single-file context bundle for Autonomous Physics Lab.

Usage
-----
    python3 scripts/generate_context_bundle.py            # writes CONTEXT.md
    python3 scripts/generate_context_bundle.py --full     # includes extended docs
    python3 scripts/generate_context_bundle.py --out FILE # custom output path
    python3 scripts/generate_context_bundle.py --stdout   # print to stdout

The bundle is intended for use with chat-based LLMs or as a quick orientation
file for agents. It contains the core instructions, strategy, and current task
board in one place. Extended docs (--full) add contributing workflow, review
agent protocol, and micro-task protocol.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CORE_FILES: list[tuple[str, str]] = [
    ("Agent & Contributor Rules", "AGENTS.md"),
    ("Claude Code Entry Point", "CLAUDE.md"),
    ("Project Strategy", "docs/strategy.md"),
    ("Current Missions", "docs/current-missions.md"),
    ("Machine-Readable Missions", "missions/current.yaml"),
    ("Mission Control (Current Phase)", "docs/mission-control.md"),
    ("Agent Task Protocol", "docs/agent-task-protocol.md"),
    ("Agent Scientific Work Mode", "docs/agent-scientific-work-mode.md"),
]

EXTENDED_FILES: list[tuple[str, str]] = [
    ("Contributing Workflow", "docs/contributing-workflow.md"),
    ("Maintainer Review Agent", "docs/maintainer-review-agent.md"),
    ("Scientific Micro-Task Protocol", "docs/scientific-micro-task-protocol.md"),
]

SEPARATOR = "\n\n" + "─" * 72 + "\n\n"
GENERATED_LINE_RE = re.compile(r"^Generated: .+$", re.MULTILINE)
NORMALIZED_GENERATED_LINE = "Generated: <timestamp>"


def _section(title: str, rel_path: str, content: str) -> str:
    return (
        f"# {title}\n"
        f"<!-- source: {rel_path} -->\n\n"
        f"{content.strip()}\n"
    )


def build_bundle(*, full: bool = False) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    files = CORE_FILES + (EXTENDED_FILES if full else [])

    header = (
        "# Autonomous Physics Lab — Context Bundle\n\n"
        f"Generated: {now}\n"
        f"Mode: {'full' if full else 'core'}\n"
        f"Repo: open-agent-science/autonomous-physics-lab\n\n"
        "This file bundles the core project instructions, strategy, and current\n"
        "task board into one document for use with chat-based LLMs or as a\n"
        "quick agent orientation file.\n\n"
        "For the live repository see: https://github.com/open-agent-science/autonomous-physics-lab\n"
    )

    sections: list[str] = [header]
    missing: list[str] = []

    for title, rel_path in files:
        full_path = REPO_ROOT / rel_path
        if not full_path.exists():
            missing.append(rel_path)
            continue
        content = full_path.read_text(encoding="utf-8")
        sections.append(_section(title, rel_path, content))

    bundle = SEPARATOR.join(sections)

    if missing:
        bundle += (
            SEPARATOR
            + "# Missing Files\n\n"
            + "\n".join(f"- {p}" for p in missing)
            + "\n"
        )

    return bundle


def normalize_generated_timestamp(bundle: str) -> str:
    """Normalize the volatile generated timestamp line for idempotence checks."""
    return GENERATED_LINE_RE.sub(NORMALIZED_GENERATED_LINE, bundle, count=1)


def differs_only_by_generated_timestamp(existing: str, candidate: str) -> bool:
    """Return true when two bundles differ only in their Generated timestamp."""
    if existing == candidate:
        return False
    return normalize_generated_timestamp(existing) == normalize_generated_timestamp(candidate)


def write_bundle_if_changed(out_path: Path, bundle: str) -> bool:
    """Write a bundle unless it would only refresh the timestamp line.

    Review and snapshot workflows often regenerate CONTEXT.md after merges. A
    timestamp-only rewrite creates a false dirty worktree, so preserve the
    existing file whenever the generated content is otherwise identical.
    """
    if out_path.exists():
        existing = out_path.read_text(encoding="utf-8")
        if existing == bundle or differs_only_by_generated_timestamp(existing, bundle):
            return False
    out_path.write_text(bundle, encoding="utf-8")
    return True


def bundle_is_current(*, full: bool = False, out_path: Path | None = None) -> bool:
    """Return whether the on-disk bundle matches a fresh generation."""
    target = out_path or (REPO_ROOT / "CONTEXT.md")
    candidate = build_bundle(full=full)
    if not target.exists():
        return False
    existing = target.read_text(encoding="utf-8")
    return existing == candidate or differs_only_by_generated_timestamp(existing, candidate)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 when the output file is missing or stale relative to sources.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Include extended docs (contributing, review agent, micro-task protocol).",
    )
    parser.add_argument(
        "--out",
        default="CONTEXT.md",
        help="Output file path relative to repo root (default: CONTEXT.md).",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print bundle to stdout instead of writing a file.",
    )
    args = parser.parse_args()

    out_path = REPO_ROOT / args.out

    if args.check:
        if not bundle_is_current(full=args.full, out_path=out_path):
            rel = out_path.relative_to(REPO_ROOT)
            print(
                f"Stale or missing context bundle: {rel}. "
                "Run python3 scripts/generate_context_bundle.py to refresh.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        rel = out_path.relative_to(REPO_ROOT)
        print(f"Context bundle is current: {rel}")
        return

    bundle = build_bundle(full=args.full)

    if args.stdout:
        sys.stdout.write(bundle)
        return

    changed = write_bundle_if_changed(out_path, bundle)
    lines = bundle.count("\n")
    size_kb = len(bundle.encode()) / 1024
    action = "Written" if changed else "Unchanged"
    print(f"{action}: {out_path.relative_to(REPO_ROOT)}  ({lines} lines, {size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
