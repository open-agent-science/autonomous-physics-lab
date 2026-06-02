"""GitHub task-claim issue closeout helpers.

Task-claim issues are coordination markers, not canonical task state. This
module keeps their closeout mechanical and conservative: only DONE tasks are
safe to auto-close; REVIEW_READY tasks are reported so task closeout can happen
first.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import subprocess
from typing import Any

import yaml


TASK_ID_PATTERN = re.compile(r"\bTASK-[0-9]{4}\b")
BRANCH_PATTERN = re.compile(r"(?im)^Branch:\s*(?P<branch>\S+)\s*$")


@dataclass(frozen=True)
class TaskClaimIssue:
    """One open GitHub issue that looks like a task claim."""

    number: int
    title: str
    url: str
    task_id: str | None
    branch: str | None
    labels: tuple[str, ...]
    state: str
    reason: str


@dataclass(frozen=True)
class TaskClaimIssueReport:
    """Closeout report for task-claim issue hygiene."""

    closeable: tuple[TaskClaimIssue, ...]
    needs_task_closeout: tuple[TaskClaimIssue, ...]
    ignored: tuple[TaskClaimIssue, ...]


def extract_task_id(*values: str) -> str | None:
    """Return the first TASK-XXXX id found in the given text values."""
    for value in values:
        match = TASK_ID_PATTERN.search(value or "")
        if match is not None:
            return match.group(0)
    return None


def extract_branch(body: str) -> str | None:
    """Extract the task branch recorded in a task-claim issue body."""
    match = BRANCH_PATTERN.search(body or "")
    return match.group("branch") if match is not None else None


def is_task_claim_like(issue: dict[str, Any]) -> bool:
    """Return whether an issue is a task-claim coordination marker."""
    labels = {
        str(label.get("name", ""))
        for label in issue.get("labels", []) or []
        if isinstance(label, dict)
    }
    title = str(issue.get("title", ""))
    body = str(issue.get("body", ""))
    if "task-claim" in labels:
        return True
    lowered_title = title.lower()
    if lowered_title.startswith("task claim:") and extract_task_id(title, body) is not None:
        return True
    if re.match(r"^TASK-[0-9]{4}\s+claim:", title) is not None:
        return True
    return "claim channel:" in body.lower() and extract_task_id(title, body) is not None


def load_task_status(root: Path, task_id: str) -> str | None:
    """Load the canonical task status for a task id."""
    matches = sorted((root / "tasks").glob(f"{task_id}-*.yaml"))
    if not matches:
        return None
    payload = yaml.safe_load(matches[0].read_text(encoding="utf-8")) or {}
    return str(payload.get("status", "")) or None


def classify_task_claim_issues(root: Path, issues: list[dict[str, Any]]) -> TaskClaimIssueReport:
    """Classify open task-claim-like issues from canonical task YAML state."""
    closeable: list[TaskClaimIssue] = []
    needs_task_closeout: list[TaskClaimIssue] = []
    ignored: list[TaskClaimIssue] = []

    for issue in issues:
        labels = tuple(
            sorted(
                str(label.get("name", ""))
                for label in issue.get("labels", []) or []
                if isinstance(label, dict)
            )
        )
        title = str(issue.get("title", ""))
        body = str(issue.get("body", ""))
        task_id = extract_task_id(title, body)
        branch = extract_branch(body)
        number = int(issue.get("number", 0))
        url = str(issue.get("url", ""))

        if not is_task_claim_like(issue) or task_id is None:
            ignored.append(
                TaskClaimIssue(
                    number=number,
                    title=title,
                    url=url,
                    task_id=task_id,
                    branch=branch,
                    labels=labels,
                    state="ignored",
                    reason="not a task-claim-like issue",
                )
            )
            continue

        task_status = load_task_status(root, task_id)
        if task_status == "DONE":
            closeable.append(
                TaskClaimIssue(
                    number=number,
                    title=title,
                    url=url,
                    task_id=task_id,
                    branch=branch,
                    labels=labels,
                    state="closeable",
                    reason="canonical task is DONE",
                )
            )
        elif task_status == "REVIEW_READY":
            needs_task_closeout.append(
                TaskClaimIssue(
                    number=number,
                    title=title,
                    url=url,
                    task_id=task_id,
                    branch=branch,
                    labels=labels,
                    state="needs_task_closeout",
                    reason="canonical task is REVIEW_READY; close the task before closing the claim",
                )
            )
        else:
            ignored.append(
                TaskClaimIssue(
                    number=number,
                    title=title,
                    url=url,
                    task_id=task_id,
                    branch=branch,
                    labels=labels,
                    state="ignored",
                    reason=f"canonical task status is {task_status or 'missing'}",
                )
            )

    return TaskClaimIssueReport(
        closeable=tuple(closeable),
        needs_task_closeout=tuple(needs_task_closeout),
        ignored=tuple(ignored),
    )


def load_open_github_issues(*, repo: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    """Load open GitHub issues through gh CLI."""
    command = [
        "gh",
        "issue",
        "list",
        "--state",
        "open",
        "--limit",
        str(limit),
        "--json",
        "number,title,labels,body,url",
    ]
    if repo:
        command.extend(["--repo", repo])
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    payload = json.loads(completed.stdout or "[]")
    return payload if isinstance(payload, list) else []


def close_task_claim_issue(number: int, *, repo: str | None = None) -> None:
    """Close one stale task-claim issue through gh CLI."""
    comment = (
        "Closing stale task-claim issue: the canonical task is already DONE. "
        "Future closeout sweeps should close task-claim issues alongside task YAML closeout."
    )
    command = ["gh", "issue", "close", str(number), "--comment", comment]
    if repo:
        command.extend(["--repo", repo])
    subprocess.run(command, check=True)


def render_task_claim_issue_report(report: TaskClaimIssueReport) -> str:
    """Render a stable human-readable task-claim issue report."""
    lines = [
        f"Closeable task-claim issues: {len(report.closeable)}",
        f"Need task closeout first: {len(report.needs_task_closeout)}",
        f"Ignored open issues: {len(report.ignored)}",
        "",
        "Closeable:",
    ]
    if report.closeable:
        for issue in report.closeable:
            lines.append(f"- #{issue.number} {issue.task_id}: {issue.title}")
            lines.append(f"  Reason: {issue.reason}")
            if issue.url:
                lines.append(f"  URL: {issue.url}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Need task closeout first:")
    if report.needs_task_closeout:
        for issue in report.needs_task_closeout:
            lines.append(f"- #{issue.number} {issue.task_id}: {issue.title}")
            lines.append(f"  Reason: {issue.reason}")
            if issue.branch:
                lines.append(f"  Branch: {issue.branch}")
    else:
        lines.append("- none")
    return "\n".join(lines)
