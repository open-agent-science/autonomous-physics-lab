#!/usr/bin/env python3
"""Advisory lane-collision preflight for parallel APL agent work.

The helper is local-only: it reads canonical task YAML through the existing
task-campaign index and inspects local git branches/worktrees. By default it
prints warnings and exits 0. Pass ``--strict`` to turn warnings into a failing
precondition.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.review_git import current_branch, run_command  # noqa: E402
from physics_lab.registry.task_campaign_index import build_index  # noqa: E402

TASK_ID_PATTERN = re.compile(r"TASK-(?P<number>[0-9]{4})", re.IGNORECASE)
TASK_BRANCH_PATTERN = re.compile(r"(?:^|/)task-(?P<number>[0-9]{4})(?:-|$)")
GENERATED_FILE_PREFIXES = ("docs/task-views/", "CONTEXT.md")


@dataclass(frozen=True)
class LaneFinding:
    """One advisory or strict finding from the lane preflight."""

    severity: str
    message: str


@dataclass(frozen=True)
class LocalOwner:
    """Local branch/worktree that appears to own a task."""

    kind: str
    name: str
    task_id: str | None


def infer_task_id(value: str) -> str | None:
    """Infer ``TASK-XXXX`` from a task id, branch name, or free text."""
    task_match = TASK_ID_PATTERN.search(value)
    if task_match is not None:
        return f"TASK-{task_match.group('number')}"
    branch_match = TASK_BRANCH_PATTERN.search(value)
    if branch_match is not None:
        return f"TASK-{branch_match.group('number')}"
    return None


def task_by_id(index: dict[str, object], task_id: str) -> dict[str, object] | None:
    """Return the indexed task row for ``task_id``."""
    for task in index.get("tasks", []):
        if isinstance(task, dict) and task.get("task_id") == task_id:
            return task
    return None


def _surface_overlap(a: dict[str, object], b: dict[str, object]) -> tuple[str, ...]:
    left = set(str(item) for item in a.get("artifact_surface", []) or [])
    right = set(str(item) for item in b.get("artifact_surface", []) or [])
    return tuple(sorted(left & right))


def analyze_lane(
    *,
    index: dict[str, object],
    task_id: str,
    local_owners: tuple[LocalOwner, ...] = (),
    current_owner_name: str = "",
) -> tuple[LaneFinding, ...]:
    """Return advisory findings for the selected task."""
    task = task_by_id(index, task_id)
    if task is None:
        return (LaneFinding("error", f"{task_id} is not present in the active task index."),)

    findings: list[LaneFinding] = []
    task_status = str(task.get("status", ""))
    lane = str(task.get("lane", ""))
    surfaces = tuple(str(item) for item in task.get("artifact_surface", []) or [])

    if task_status == "BLOCKED":
        findings.append(LaneFinding("warning", f"{task_id} is BLOCKED; do not start it without maintainer direction."))

    for owner in local_owners:
        if owner.task_id == task_id and owner.name != current_owner_name:
            findings.append(
                LaneFinding(
                    "warning",
                    f"Local {owner.kind} {owner.name!r} also appears to own {task_id}.",
                )
            )

    for other in index.get("tasks", []):
        if not isinstance(other, dict) or other.get("task_id") == task_id:
            continue
        other_status = str(other.get("status", ""))
        if str(other.get("lane", "")) != lane:
            continue
        if other_status == "BLOCKED":
            findings.append(
                LaneFinding(
                    "warning",
                    f"Lane {lane!r} has blocked task {other.get('task_id')}; check whether it blocks this work.",
                )
            )
        overlap = _surface_overlap(task, other)
        if overlap:
            findings.append(
                LaneFinding(
                    "warning",
                    f"{task_id} shares lane {lane!r} and artifact surface {', '.join(overlap)} with {other.get('task_id')} ({other_status}).",
                )
            )

    for conflict in index.get("path_conflicts", []):
        if not isinstance(conflict, dict):
            continue
        tasks = set(str(item) for item in conflict.get("tasks", []) or [])
        path = str(conflict.get("path", ""))
        if task_id in tasks:
            findings.append(
                LaneFinding(
                    "warning",
                    f"Accepted-output path {path!r} is also claimed by {', '.join(sorted(tasks - {task_id}))}.",
                )
            )

    if any(str(surface).startswith(prefix) for surface in surfaces for prefix in GENERATED_FILE_PREFIXES):
        findings.append(
            LaneFinding(
                "warning",
                f"{task_id} appears to touch generated navigation; do not commit generated task views from a task PR.",
            )
        )

    if not findings:
        findings.append(LaneFinding("ok", f"No likely lane collision found for {task_id}."))
    return tuple(findings)


def local_branch_owners(root: Path) -> tuple[LocalOwner, ...]:
    """Return local branches with task ids inferred from their names."""
    result = run_command(
        ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"],
        cwd=root,
    )
    if result.returncode != 0:
        return ()
    owners = []
    for line in result.stdout.splitlines():
        name = line.strip()
        task_id = infer_task_id(name)
        if task_id:
            owners.append(LocalOwner("branch", name, task_id))
    return tuple(owners)


def local_worktree_owners(root: Path) -> tuple[LocalOwner, ...]:
    """Return local worktree branches with task ids inferred from branch names."""
    result = run_command(["git", "worktree", "list", "--porcelain"], cwd=root)
    if result.returncode != 0:
        return ()
    owners = []
    for line in result.stdout.splitlines():
        if not line.startswith("branch "):
            continue
        ref = line.removeprefix("branch ").strip()
        name = ref.removeprefix("refs/heads/")
        task_id = infer_task_id(name)
        if task_id:
            owners.append(LocalOwner("worktree", name, task_id))
    return tuple(owners)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--task", help="Canonical task id, for example TASK-0461.")
    target.add_argument("--branch", help="Branch name to infer the task id from.")
    parser.add_argument("--root", default=".", help="Repository root (default: current directory).")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on warnings.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    target = args.task or args.branch or ""
    task_id = infer_task_id(target)
    if task_id is None:
        print(f"Could not infer task id from {target!r}.", file=sys.stderr)
        return 2

    current = current_branch(root)
    owners = tuple(dict.fromkeys((*local_branch_owners(root), *local_worktree_owners(root))))
    index = build_index(root)
    task = task_by_id(index, task_id)
    if task is None:
        print(f"Lane precondition FAILED: {task_id} not found in active task index.", file=sys.stderr)
        return 1

    print(f"Lane precondition for {task_id}")
    print(f"- branch: {current}")
    print(f"- lane: {task.get('lane')}")
    print(f"- status: {task.get('status')}")
    print(f"- artifact surface: {', '.join(task.get('artifact_surface', []) or []) or 'none'}")
    print(f"- mapping basis: {task.get('mapping_basis')}")

    findings = analyze_lane(
        index=index,
        task_id=task_id,
        local_owners=owners,
        current_owner_name=current,
    )
    warnings = [finding for finding in findings if finding.severity != "ok"]
    for finding in findings:
        print(f"- {finding.severity.upper()}: {finding.message}")

    if warnings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
