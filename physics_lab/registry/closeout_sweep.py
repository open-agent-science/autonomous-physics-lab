"""Helpers for maintainer closeout sweep automation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from physics_lab.registry.maintainer_review import build_closeout_report
from physics_lab.registry.review_git import current_branch, run_command
from physics_lab.registry.tasks import load_task


MERGE_SUBJECT_PATTERN = re.compile(r"^Merge pull request #(?P<number>[0-9]+)\s+from\s+.+$")
PR_TITLE_TASK_PATTERN = re.compile(r"^(?P<task_id>TASK-[0-9]{4}):\s+.+$")
CANONICAL_TASK_ID_PATTERN = re.compile(r"^TASK-[0-9]{4}$")


@dataclass(frozen=True)
class MergedTaskPullRequest:
    """Merged pull request mapped to a canonical task id."""

    task_id: str
    number: int
    title: str
    merged_at: str
    url: str


@dataclass(frozen=True)
class CloseoutSweepCandidate:
    """One task checked during a closeout sweep."""

    task_id: str
    task_title: str
    pull_request: int | None
    pr_title: str | None
    pr_url: str | None
    outcome: str
    blockers: tuple[str, ...]
    required_actions: tuple[str, ...]
    recommended_apply_command: str | None


@dataclass(frozen=True)
class CloseoutSweepReport:
    """Rendered result for a closeout sweep run."""

    branch: str
    ready: tuple[CloseoutSweepCandidate, ...]
    blocked: tuple[CloseoutSweepCandidate, ...]
    skipped: tuple[CloseoutSweepCandidate, ...]


def list_review_ready_tasks(root: Path) -> tuple[tuple[str, str], ...]:
    """Return canonical tasks that are still REVIEW_READY."""
    items: list[tuple[str, str]] = []
    for path in sorted((root / "tasks").glob("TASK-*.yaml")):
        if path.name == "TASK-TEMPLATE.yaml":
            continue
        payload = load_task(path)
        task_id = str(payload["id"])
        if CANONICAL_TASK_ID_PATTERN.match(task_id) is None:
            continue
        if str(payload["status"]) == "REVIEW_READY":
            items.append((task_id, str(payload["title"])))
    return tuple(items)


def load_merged_task_pull_requests(
    root: Path,
    *,
    limit: int = 200,
) -> dict[str, MergedTaskPullRequest]:
    """Load merged PR metadata keyed by TASK-XXXX from local git history."""
    remote_url = _origin_remote_web_url(root)
    result = run_command(
        [
            "git",
            "log",
            "--first-parent",
            "--merges",
            f"--max-count={limit}",
            "--format=%cI%x1f%s%x1f%b%x1e",
        ],
        cwd=root,
        timeout=60,
    )
    if result.returncode != 0:
        return {}

    by_task: dict[str, MergedTaskPullRequest] = {}
    for raw_record in result.stdout.split("\x1e"):
        record = raw_record.strip()
        if not record:
            continue
        merged_at, subject, body = (record.split("\x1f", 2) + ["", "", ""])[:3]
        merge_match = MERGE_SUBJECT_PATTERN.match(subject.strip())
        if merge_match is None:
            continue
        pr_number = int(merge_match.group("number"))
        title = next(
            (
                line.strip()
                for line in body.splitlines()
                if PR_TITLE_TASK_PATTERN.match(line.strip()) is not None
            ),
            "",
        )
        title_match = PR_TITLE_TASK_PATTERN.match(title)
        if title_match is None:
            continue
        task_id = title_match.group("task_id")
        candidate = MergedTaskPullRequest(
            task_id=task_id,
            number=pr_number,
            title=title,
            merged_at=merged_at.strip(),
            url=(f"{remote_url}/pull/{pr_number}" if remote_url else ""),
        )
        previous = by_task.get(task_id)
        if previous is None or candidate.merged_at > previous.merged_at:
            by_task[task_id] = candidate
    return by_task


def _origin_remote_web_url(root: Path) -> str | None:
    """Return the GitHub web URL for origin when it can be derived locally."""
    result = run_command(["git", "remote", "get-url", "origin"], cwd=root, timeout=30)
    if result.returncode != 0:
        return None
    remote = result.stdout.strip()
    if remote.startswith("git@github.com:"):
        slug = remote.removeprefix("git@github.com:").removesuffix(".git")
        return f"https://github.com/{slug}"
    if remote.startswith("https://github.com/"):
        return remote.removesuffix(".git")
    return None


def build_closeout_sweep_report(
    root: Path,
    *,
    merged_limit: int = 200,
) -> CloseoutSweepReport:
    """Build a sweep report for merged tasks that may need closeout."""
    merged_prs = load_merged_task_pull_requests(root, limit=merged_limit)
    ready: list[CloseoutSweepCandidate] = []
    blocked: list[CloseoutSweepCandidate] = []
    skipped: list[CloseoutSweepCandidate] = []

    for task_id, task_title in list_review_ready_tasks(root):
        pr = merged_prs.get(task_id)
        if pr is None:
            skipped.append(
                CloseoutSweepCandidate(
                    task_id=task_id,
                    task_title=task_title,
                    pull_request=None,
                    pr_title=None,
                    pr_url=None,
                    outcome="NO_MERGED_PR",
                    blockers=(),
                    required_actions=("No merged canonical task PR was found for this task.",),
                    recommended_apply_command=None,
                )
            )
            continue

        closeout = build_closeout_report(
            root,
            task_id=task_id,
            pull_request=pr.number,
            apply=False,
        )
        candidate = CloseoutSweepCandidate(
            task_id=task_id,
            task_title=task_title,
            pull_request=pr.number,
            pr_title=pr.title,
            pr_url=pr.url,
            outcome=closeout.outcome,
            blockers=closeout.blockers,
            required_actions=closeout.required_actions,
            recommended_apply_command=(
                f"python3 scripts/apl_closeout_task.py --task {task_id} --pr {pr.number} --apply"
                if closeout.outcome == "READY_TO_APPLY"
                else None
            ),
        )
        if closeout.outcome == "READY_TO_APPLY":
            ready.append(candidate)
        else:
            blocked.append(candidate)

    return CloseoutSweepReport(
        branch=current_branch(root),
        ready=tuple(ready),
        blocked=tuple(blocked),
        skipped=tuple(skipped),
    )


def render_closeout_sweep_report(report: CloseoutSweepReport) -> str:
    """Render a stable text report for closeout sweep runs."""
    lines = [
        f"Closeout sweep branch: {report.branch}",
        f"Ready candidates: {len(report.ready)}",
        f"Blocked candidates: {len(report.blocked)}",
        f"Skipped candidates: {len(report.skipped)}",
        "",
        "Ready closeout candidates:",
    ]
    if report.ready:
        for item in report.ready:
            lines.append(f"- {item.task_id} — {item.task_title}")
            lines.append(f"  PR: #{item.pull_request} {item.pr_title}")
            if item.pr_url:
                lines.append(f"  URL: {item.pr_url}")
            lines.append(f"  Apply: {item.recommended_apply_command}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Blocked closeout candidates:")
    if report.blocked:
        for item in report.blocked:
            lines.extend(
                [
                    f"- {item.task_id} — {item.task_title}",
                    f"  PR: #{item.pull_request} {item.pr_title}",
                    f"  Outcome: {item.outcome}",
                ]
            )
            for blocker in item.blockers:
                lines.append(f"  Blocker: {blocker}")
            for action in item.required_actions:
                lines.append(f"  Action: {action}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Skipped REVIEW_READY tasks:")
    if report.skipped:
        for item in report.skipped:
            lines.extend(
                [
                    f"- {item.task_id} — {item.task_title}",
                    f"  Reason: {item.required_actions[0]}",
                ]
            )
    else:
        lines.append("- none")

    return "\n".join(lines)
