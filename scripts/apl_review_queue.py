#!/usr/bin/env python3
"""Snapshot the open PR review queue without foreground-watching CI."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import subprocess
import sys
from typing import Any


PASS_CONCLUSIONS = frozenset({"SUCCESS", "SKIPPED", "NEUTRAL"})
FAIL_CONCLUSIONS = frozenset({"FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED"})
PENDING_STATUSES = frozenset({"QUEUED", "IN_PROGRESS", "PENDING", "WAITING", "REQUESTED"})
MERGE_OK_DECISIONS = frozenset({"APPROVED"})
DEPENDABOT_MARKERS = ("dependabot", "chore(deps):")
DECISION_ORDER = {
    "MERGE_NOW": 0,
    "READY_AFTER_UPDATE": 1,
    "NEEDS_REVIEW": 2,
    "RISKY_DEPENDABOT": 3,
    "WAIT_CI": 4,
    "DRAFT": 5,
}


@dataclass(frozen=True)
class CheckSummary:
    """Collapsed check-rollup state for one pull request."""

    status: str
    pending: tuple[str, ...] = ()
    failing: tuple[str, ...] = ()


@dataclass(frozen=True)
class QueueEntry:
    """Maintainer-facing queue decision for one pull request."""

    number: int
    title: str
    decision: str
    reason: str
    action: str
    merge_state: str
    check_status: str
    url: str


def _check_name(row: dict[str, Any]) -> str:
    return str(row.get("name") or row.get("context") or "<unnamed check>")


def _latest_check_rows(status_check_rollup: list[object]) -> tuple[dict[str, Any], ...]:
    """Return the newest row per check name from a possibly stale GH rollup."""

    # Keep this as a bounded snapshot operation. During merge waves GitHub may
    # leave cancelled rows from superseded runs in statusCheckRollup; streaming
    # `gh pr checks --watch` per PR burns maintainer time/API budget and can
    # hide other merge-ready PRs behind one slow queue run.
    latest: dict[str, tuple[tuple[str, int], dict[str, Any]]] = {}
    for index, row in enumerate(status_check_rollup):
        if not isinstance(row, dict):
            continue
        name = _check_name(row)
        timestamp = str(row.get("startedAt") or row.get("completedAt") or "")
        sort_key = (timestamp, index)
        previous = latest.get(name)
        if previous is None or sort_key > previous[0]:
            latest[name] = (sort_key, row)
    return tuple(item[1] for item in latest.values())


def summarize_checks(status_check_rollup: object) -> CheckSummary:
    """Return pass/fail/pending/unknown for a GitHub statusCheckRollup value."""

    if not isinstance(status_check_rollup, list) or not status_check_rollup:
        return CheckSummary(status="unknown")

    pending: list[str] = []
    failing: list[str] = []
    saw_completed = False
    saw_unknown = False
    for row in _latest_check_rows(status_check_rollup):
        if not isinstance(row, dict):
            saw_unknown = True
            continue
        name = _check_name(row)
        status = str(row.get("status") or row.get("state") or "").upper()
        conclusion = str(row.get("conclusion") or "").upper()
        bucket = str(row.get("bucket") or "").lower()
        if status in PENDING_STATUSES or bucket == "pending":
            pending.append(name)
            continue
        if conclusion in FAIL_CONCLUSIONS or bucket in {"fail", "cancel"}:
            failing.append(name)
            continue
        if status == "COMPLETED" and conclusion in PASS_CONCLUSIONS:
            saw_completed = True
            continue
        if bucket in {"pass", "skipping"}:
            saw_completed = True
            continue
        saw_unknown = True

    if failing:
        return CheckSummary(status="fail", failing=tuple(failing))
    if pending:
        return CheckSummary(status="pending", pending=tuple(pending))
    if saw_unknown:
        return CheckSummary(status="unknown")
    if saw_completed:
        return CheckSummary(status="pass")
    return CheckSummary(status="unknown")


def _author_login(pr: dict[str, Any]) -> str:
    author = pr.get("author")
    if isinstance(author, dict):
        return str(author.get("login") or "").lower()
    return ""


def is_dependabot_pr(pr: dict[str, Any]) -> bool:
    """Return whether a PR should get dependency-maintenance scrutiny first."""

    title = str(pr.get("title") or "").lower()
    author = _author_login(pr)
    return any(marker in title or marker in author for marker in DEPENDABOT_MARKERS)


def classify_pr(pr: dict[str, Any], *, merge_ok_prs: set[int] | None = None) -> QueueEntry:
    """Classify one open PR into a next-action bucket."""

    merge_ok_prs = merge_ok_prs or set()
    number = int(pr.get("number") or 0)
    title = str(pr.get("title") or "")
    merge_state = str(pr.get("mergeStateStatus") or "UNKNOWN")
    check_summary = summarize_checks(pr.get("statusCheckRollup"))
    url = str(pr.get("url") or "")
    review_decision = str(pr.get("reviewDecision") or "").upper()
    has_review_ok = number in merge_ok_prs or review_decision in MERGE_OK_DECISIONS

    if bool(pr.get("isDraft")):
        return QueueEntry(
            number=number,
            title=title,
            decision="DRAFT",
            reason="draft PR",
            action="leave parked until author or maintainer marks ready",
            merge_state=merge_state,
            check_status=check_summary.status,
            url=url,
        )
    if is_dependabot_pr(pr):
        return QueueEntry(
            number=number,
            title=title,
            decision="RISKY_DEPENDABOT",
            reason="dependency or Actions bump needs supply-chain review before queue merge",
            action="review changelog, pinning, and compatibility before merge",
            merge_state=merge_state,
            check_status=check_summary.status,
            url=url,
        )
    if check_summary.status == "pending":
        pending = ", ".join(check_summary.pending) or "required checks"
        # Architecture decision: pending CI parks the PR. A review sweep should
        # advance other green PRs instead of foreground-watching one run; a
        # deliberately selected PR can still be watched manually outside this
        # queue snapshot.
        return QueueEntry(
            number=number,
            title=title,
            decision="WAIT_CI",
            reason=f"pending checks: {pending}",
            action="park this PR; do not foreground-watch unless maintainer explicitly chooses it",
            merge_state=merge_state,
            check_status=check_summary.status,
            url=url,
        )
    if check_summary.status == "fail":
        failing = ", ".join(check_summary.failing) or "required checks"
        return QueueEntry(
            number=number,
            title=title,
            decision="NEEDS_REVIEW",
            reason=f"failing checks: {failing}",
            action="inspect failing check logs and request or apply a fix",
            merge_state=merge_state,
            check_status=check_summary.status,
            url=url,
        )
    if check_summary.status != "pass":
        return QueueEntry(
            number=number,
            title=title,
            decision="NEEDS_REVIEW",
            reason="unknown or empty check rollup",
            action="refresh GitHub checks or inspect PR metadata before merge",
            merge_state=merge_state,
            check_status=check_summary.status,
            url=url,
        )
    if not has_review_ok:
        return QueueEntry(
            number=number,
            title=title,
            decision="NEEDS_REVIEW",
            reason="green CI but no recorded review-agent MERGE_OK or GitHub approval",
            action="run apl_review_pr.py, then rerun this snapshot with --merge-ok-pr",
            merge_state=merge_state,
            check_status=check_summary.status,
            url=url,
        )
    if merge_state == "CLEAN":
        return QueueEntry(
            number=number,
            title=title,
            decision="MERGE_NOW",
            reason="green checks, clean merge state, and review recorded",
            action="maintainer skim, then merge",
            merge_state=merge_state,
            check_status=check_summary.status,
            url=url,
        )
    if merge_state == "BEHIND":
        return QueueEntry(
            number=number,
            title=title,
            decision="READY_AFTER_UPDATE",
            reason="green checks and review recorded, but branch is behind main",
            action="update branch with main, rerun narrow validation/review if needed",
            merge_state=merge_state,
            check_status=check_summary.status,
            url=url,
        )
    return QueueEntry(
        number=number,
        title=title,
        decision="NEEDS_REVIEW",
        reason=f"merge state is {merge_state}",
        action="inspect merge state before merge",
        merge_state=merge_state,
        check_status=check_summary.status,
        url=url,
    )


def classify_queue(
    prs: list[dict[str, Any]], *, merge_ok_prs: set[int] | None = None
) -> list[QueueEntry]:
    """Classify and sort open PRs by maintainer queue priority."""

    entries = [classify_pr(pr, merge_ok_prs=merge_ok_prs) for pr in prs]
    return sorted(
        entries,
        key=lambda entry: (DECISION_ORDER.get(entry.decision, 99), entry.number),
    )


def render_markdown(entries: list[QueueEntry]) -> str:
    """Render queue entries as a compact maintainer table."""

    lines = [
        "# APL Review Queue Snapshot",
        "",
        "| PR | Decision | Merge | Checks | Reason | Next action |",
        "|---:|---|---|---|---|---|",
    ]
    for entry in entries:
        title = entry.title.replace("|", "\\|")
        reason = entry.reason.replace("|", "\\|")
        action = entry.action.replace("|", "\\|")
        pr = f"[#{entry.number}]({entry.url})" if entry.url else f"#{entry.number}"
        lines.append(
            f"| {pr} | `{entry.decision}` | `{entry.merge_state}` | "
            f"`{entry.check_status}` | {reason} | {action}: {title} |"
        )
    if not entries:
        lines.append("| - | `EMPTY` | - | - | No open PRs returned. | - |")
    return "\n".join(lines)


def _load_prs_from_gh(limit: int) -> list[dict[str, Any]]:
    # Ask GitHub for one compact rollup, then classify locally. Avoid per-PR
    # follow-up calls here; those caused rate-limit and token churn during
    # maintainer review sessions.
    command = [
        "gh",
        "pr",
        "list",
        "--state",
        "open",
        "--limit",
        str(limit),
        "--json",
        "number,title,isDraft,mergeStateStatus,reviewDecision,statusCheckRollup,updatedAt,url,author",
    ]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write((result.stderr or result.stdout).strip() + "\n")
        raise SystemExit(result.returncode)
    payload = json.loads(result.stdout)
    if not isinstance(payload, list):
        raise SystemExit("gh pr list returned a non-list payload.")
    return payload


def _load_prs_from_file(path: str) -> list[dict[str, Any]]:
    payload = json.loads(open(path, encoding="utf-8").read())
    if not isinstance(payload, list):
        raise SystemExit("Expected a list of PR payloads.")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=30, help="Open PR limit for gh.")
    parser.add_argument(
        "--input-json",
        help="Read a saved gh pr list JSON payload instead of calling gh.",
    )
    parser.add_argument(
        "--merge-ok-pr",
        type=int,
        action="append",
        default=[],
        help="PR number that already has maintainer-review-agent MERGE_OK.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output.")
    args = parser.parse_args(argv)

    prs = _load_prs_from_file(args.input_json) if args.input_json else _load_prs_from_gh(args.limit)
    entries = classify_queue(prs, merge_ok_prs=set(args.merge_ok_pr))
    if args.json:
        print(json.dumps([entry.__dict__ for entry in entries], indent=2, sort_keys=True))
    else:
        print(render_markdown(entries))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
