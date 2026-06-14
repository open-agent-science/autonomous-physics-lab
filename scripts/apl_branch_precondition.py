#!/usr/bin/env python3
"""Branch + working-tree precondition check for APL agent sessions.

Agents should run this script before any ``git add`` / ``git commit`` /
``git push`` to catch two common failure modes early:

1. **Wrong branch.** A parallel session may have switched HEAD without
   the agent noticing (see the TASK-0227 / TASK-0251 incident). The
   check exits non-zero when HEAD does not match the expected branch.

2. **Surprise working-tree changes.** Modified or untracked files that
   the agent did not produce are usually the symptom of cross-session
   contamination. The check filters known harness state via
   ``HARNESS_IGNORE_PATHS`` and an optional ``--allow-untracked`` glob
   list, then exits non-zero when anything else is dirty.

Usage:

    python3 scripts/apl_branch_precondition.py \\
        --expected-branch agent/gladunrv/claude/task-0263-foo \\
        --allow-untracked "docs/notes/draft-*.md"

Exit codes:

    0 — all checks pass
    1 — branch mismatch or unexpected working-tree changes
    2 — invalid arguments

The script is opt-in and additive. It does not modify the working tree.
"""

from __future__ import annotations

import argparse
import fnmatch
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.review_git import (  # noqa: E402
    HARNESS_IGNORE_PATHS,
    current_branch,
    run_command,
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="APL agent branch + working-tree precondition check.",
    )
    parser.add_argument(
        "--expected-branch",
        required=True,
        help="The branch the agent expects to be on (e.g. agent/<id>/<agent>/task-XXXX-slug).",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root (default: current directory).",
    )
    parser.add_argument(
        "--allow-untracked",
        action="append",
        default=[],
        metavar="PATTERN",
        help=(
            "Glob pattern (fnmatch-style) for additional untracked paths the agent "
            "expects to see. Can be passed multiple times."
        ),
    )
    parser.add_argument(
        "--allow-modified",
        action="append",
        default=[],
        metavar="PATTERN",
        help=(
            "Glob pattern (fnmatch-style) for additional modified paths the agent "
            "expects. Can be passed multiple times."
        ),
    )
    parser.add_argument(
        "--check-upstream",
        action="store_true",
        help=(
            "Also verify the current branch's upstream tracks its own remote "
            "branch (not origin/main or a missing upstream) for task-lifecycle "
            "branches, and print a safe explicit push command when it does not."
        ),
    )
    parser.add_argument(
        "--remote",
        default="origin",
        help="Remote name used for the safe push command (default: origin).",
    )
    return parser.parse_args(argv)


# Task-lifecycle branch kinds whose upstream should be their own remote branch,
# never a shared branch such as origin/main.
TASK_BRANCH_KINDS = ("task", "proposal", "queue", "closeout", "microtask")


def classify_branch_kind(branch: str) -> str | None:
    """Classify a branch as a task-lifecycle kind, or ``None`` for others.

    Canonical agent branches look like
    ``agent/<contributor>/<agent>/<kind-segment>``. The kind is read from the
    fourth path segment so the upstream check only flags lifecycle branches that
    are expected to publish to their own upstream (and not, for example, ``main``).
    """
    parts = branch.split("/")
    if len(parts) < 4 or parts[0] != "agent":
        return None
    segment = parts[3]
    # Order matters: ``task-queue-`` is checked before the generic ``task-``.
    if segment.startswith("task-queue-"):
        return "queue"
    if segment.startswith("propose-task-"):
        return "proposal"
    if segment.startswith("closeout-"):
        return "closeout"
    if segment.startswith("microtask-"):
        return "microtask"
    if segment.startswith("task-"):
        return "task"
    return None


def upstream_preflight(
    *, branch: str, upstream: str | None, remote: str = "origin"
) -> dict[str, object]:
    """Evaluate whether ``branch`` tracks its own remote branch.

    Pure decision logic (no git calls) so it is fully unit-testable. Returns a
    mapping with ``status``, ``ok``, ``branch_kind``, ``message``, and a
    ``safe_command`` (an explicit ``git push <remote> HEAD:<branch>``) when the
    upstream is wrong or missing.
    """
    if not branch:
        return {
            "status": "detached_head",
            "ok": True,
            "branch_kind": None,
            "message": "Detached HEAD; no branch upstream to check.",
            "safe_command": None,
        }
    kind = classify_branch_kind(branch)
    if kind is None:
        return {
            "status": "not_a_task_branch",
            "ok": True,
            "branch_kind": None,
            "message": (
                f"Branch {branch!r} is not a task-lifecycle branch; "
                "upstream tracking not checked."
            ),
            "safe_command": None,
        }
    expected = f"{remote}/{branch}"
    safe_command = f"git push {remote} HEAD:{branch}"
    if not upstream:
        return {
            "status": "missing_upstream",
            "ok": False,
            "branch_kind": kind,
            "message": (
                f"Branch {branch!r} has no upstream. Publish it to its own remote "
                "branch rather than relying on a default."
            ),
            "safe_command": safe_command,
        }
    if upstream != expected:
        return {
            "status": "upstream_mismatch",
            "ok": False,
            "branch_kind": kind,
            "message": (
                f"Branch {branch!r} tracks {upstream!r}, not {expected!r}. "
                "Pushing now could target the wrong upstream."
            ),
            "safe_command": safe_command,
        }
    return {
        "status": "ok",
        "ok": True,
        "branch_kind": kind,
        "message": f"Branch {branch!r} correctly tracks {expected!r}.",
        "safe_command": None,
    }


def _resolve_upstream(root: Path) -> str | None:
    """Return the current branch's upstream ref (e.g. ``origin/...``) or ``None``."""
    result = run_command(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
        cwd=root,
    )
    if result.returncode != 0:
        return None
    upstream = result.stdout.strip()
    return upstream or None


def _filter_paths(paths: tuple[str, ...], patterns: list[str]) -> tuple[str, ...]:
    """Drop paths matching any of the fnmatch-style patterns."""
    if not patterns:
        return paths
    return tuple(
        path
        for path in paths
        if not any(fnmatch.fnmatch(path, pattern) for pattern in patterns)
    )


def _working_tree_entries(root: Path) -> tuple[tuple[str, str], ...]:
    """Return ``(status, path)`` entries from ``git status --short``."""
    result = run_command(["git", "status", "--short"], cwd=root)
    entries: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        entry = line[3:] if len(line) > 3 else line
        if " -> " in entry and any(code in status for code in ("R", "C")):
            entry = entry.split(" -> ", 1)[1]
        path = entry.strip()
        if any(fnmatch.fnmatch(path, pattern) for pattern in HARNESS_IGNORE_PATHS):
            continue
        entries.append((status, path))
    return tuple(entries)


def run(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    actual_branch = current_branch(root)
    failures: list[str] = []

    if actual_branch != args.expected_branch:
        failures.append(
            f"Branch mismatch: expected {args.expected_branch!r}, on {actual_branch!r}."
        )

    dirty_entries = _working_tree_entries(root)
    untracked_paths = tuple(
        path for status, path in dirty_entries if status == "??"
    )
    modified_paths = tuple(
        path for status, path in dirty_entries if status != "??"
    )
    surprise_paths = _filter_paths(
        untracked_paths, list(args.allow_untracked)
    ) + _filter_paths(modified_paths, list(args.allow_modified))
    if surprise_paths:
        joined = ", ".join(surprise_paths)
        failures.append(
            f"Working tree has unexpected changes: {joined}. "
            "Stash, commit, or pass --allow-untracked / --allow-modified for each expected path."
        )

    if getattr(args, "check_upstream", False):
        remote = getattr(args, "remote", "origin")
        verdict = upstream_preflight(
            branch=actual_branch, upstream=_resolve_upstream(root), remote=remote
        )
        if not verdict["ok"]:
            failures.append(str(verdict["message"]))
            if verdict["safe_command"]:
                failures.append(f"Safe publish command: {verdict['safe_command']}")

    if failures:
        print("Branch precondition FAILED:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"Branch precondition OK: on {actual_branch}, no surprise files.")
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parse_args(argv)
    except SystemExit as exc:
        # argparse exits with code 2 on parse errors; preserve that.
        return int(exc.code) if exc.code is not None else 2
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
