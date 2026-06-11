"""Helpers for maintainer closeout sweep automation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from physics_lab.registry.maintainer_review import (
    PullRequestMetadata,
    branch_task_id,
    build_closeout_report,
    load_pr_metadata,
)
from physics_lab.registry.pr_capability import find_gh_path
from physics_lab.registry.review_git import current_branch, git_status_clean, run_command
from physics_lab.registry.tasks import load_task


MERGE_SUBJECT_PATTERN = re.compile(r"^Merge pull request #(?P<number>[0-9]+)\s+from\s+.+$")
SQUASH_MERGE_SUBJECT_PATTERN = re.compile(
    r"^(?P<title>(?P<task_id>TASK-[0-9]{4}):\s+.+)\s+\(#(?P<number>[0-9]+)\)$"
)
CONVENTIONAL_TASK_SUBJECT_PATTERN = re.compile(
    r"^[a-z]+(?:\((?P<task_id>TASK-[0-9]{4})\))!?:\s+.+$",
    re.IGNORECASE,
)
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
    branch: str = ""
    base_branch: str = "main"
    status_checks_passed: bool | None = None
    status_checks_pending: bool = False
    changed_files: tuple[str, ...] = ()


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


@dataclass(frozen=True)
class CloseoutSweepApplyReport:
    """Files changed by an applied closeout sweep."""

    applied: tuple[CloseoutSweepCandidate, ...]
    changed_files: tuple[Path, ...]


def closeout_pr_binding_blockers(root: Path, *, task_id: str, pull_request: int) -> tuple[str, ...]:
    """Verify that GitHub PR metadata still binds the PR to the expected task id."""
    pr_metadata = load_pr_metadata(root, pull_request)
    return closeout_pr_metadata_binding_blockers(task_id=task_id, pr_metadata=pr_metadata)


def closeout_pr_metadata_binding_blockers(
    *,
    task_id: str,
    pr_metadata: PullRequestMetadata | None,
) -> tuple[str, ...]:
    """Verify that already-loaded GitHub PR metadata binds to the expected task id."""
    if pr_metadata is None:
        return ()

    title_match = PR_TITLE_TASK_PATTERN.match(pr_metadata.title.strip())
    title_task_id = title_match.group("task_id") if title_match is not None else None
    branch_task = branch_task_id(pr_metadata.branch.strip())

    if title_task_id == task_id or branch_task == task_id:
        return ()

    detail_parts: list[str] = []
    if title_task_id is not None:
        detail_parts.append(f"title task id is {title_task_id}")
    if branch_task is not None:
        detail_parts.append(f"branch task id is {branch_task}")
    if not detail_parts:
        detail_parts.append("neither PR title nor head branch resolves to a canonical task id")

    return (
        "Merged PR metadata does not match canonical task id: "
        + ", ".join(detail_parts)
        + ".",
    )


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


def _task_file_by_id(root: Path, task_id: str) -> Path | None:
    """Return the canonical task file for ``task_id`` when present."""
    for path in sorted((root / "tasks").glob(f"{task_id}-*.yaml")):
        if path.name == "TASK-TEMPLATE.yaml":
            continue
        payload = load_task(path)
        if str(payload["id"]) == task_id:
            return path
    return None


def load_merged_task_pull_requests(
    root: Path,
    *,
    limit: int = 200,
) -> dict[str, MergedTaskPullRequest]:
    """Load merged PR metadata keyed by TASK-XXXX.

    Local merge history is the first source because it is deterministic and
    works offline after the maintainer has pulled `main`. A GitHub CLI fallback
    covers the common closeout case where PRs were merged remotely but the local
    first-parent history has not yet been refreshed.
    """
    remote_url = _origin_remote_web_url(root)
    by_task = _load_merged_task_pull_requests_from_git(
        root,
        limit=limit,
        remote_url=remote_url,
    )
    gh_prs = _load_merged_task_pull_requests_from_gh(
        root,
        limit=limit,
        remote_url=remote_url,
    )
    for task_id, candidate in gh_prs.items():
        previous = by_task.get(task_id)
        if previous is None or candidate.merged_at > previous.merged_at:
            by_task[task_id] = candidate
    for task_id, candidate in tuple(by_task.items()):
        if candidate.number > 0:
            continue
        resolved = _load_merged_task_pull_request_from_gh_search(
            root,
            task_id=task_id,
            remote_url=remote_url,
        )
        if resolved is not None:
            by_task[task_id] = resolved
        else:
            del by_task[task_id]
    return by_task


def merged_task_pr_metadata(pr: MergedTaskPullRequest) -> PullRequestMetadata:
    """Convert merged-PR summary data into closeout report metadata."""
    return PullRequestMetadata(
        number=pr.number,
        title=pr.title,
        body="",
        branch=pr.branch,
        base_branch=pr.base_branch,
        state="MERGED",
        merged=True,
        status_checks_passed=pr.status_checks_passed,
        status_checks_pending=pr.status_checks_pending,
        changed_files=pr.changed_files,
    )


def apply_closeout_sweep_report(
    root: Path,
    report: CloseoutSweepReport,
) -> CloseoutSweepApplyReport:
    """Apply all ready closeout candidates from a sweep report.

    This is intentionally narrow: the sweep report has already verified merged
    PR binding, accepted outputs, and CI via ``build_closeout_report``. The
    batch applier only updates task status lines from ``REVIEW_READY`` to
    ``DONE`` so a multi-task sweep does not fail after the first task dirties
    the worktree.
    """
    if report.branch != "main":
        raise ValueError("Closeout sweep apply must run on main.")
    if not git_status_clean(root):
        raise ValueError("Closeout sweep apply requires a clean git status.")

    applied: list[CloseoutSweepCandidate] = []
    changed_files: list[Path] = []
    for candidate in report.ready:
        task_file = _task_file_by_id(root, candidate.task_id)
        if task_file is None:
            raise ValueError(f"Task file not found for {candidate.task_id}.")
        text = task_file.read_text(encoding="utf-8")
        needle = "status: REVIEW_READY"
        if needle not in text:
            raise ValueError(f"{candidate.task_id} is not REVIEW_READY.")
        task_file.write_text(text.replace(needle, "status: DONE", 1), encoding="utf-8")
        applied.append(candidate)
        changed_files.append(task_file)
    return CloseoutSweepApplyReport(
        applied=tuple(applied),
        changed_files=tuple(changed_files),
    )


PROTECTED_ARTIFACT_PREFIXES: tuple[str, ...] = (
    "claims/",
    "results/",
    "prediction_registry/",
    "experiments/",
    "knowledge/",
)


def task_closeout_policy(task_payload: dict) -> str:
    """Return a task's closeout policy: 'review' (opt-out) or 'auto' (default)."""
    return "review" if task_payload.get("closeout") == "review" else "auto"


def task_unblocks_others(root: Path, task_id: str) -> bool:
    """Return True if any BLOCKED task references ``task_id``.

    Conservative over-approximation: closing a task that another BLOCKED task
    names may require a manual dependent-unblock decision, so such tasks are not
    auto-closed.
    """
    tasks_dir = root / "tasks"
    if not tasks_dir.is_dir():
        return False
    for path in sorted(tasks_dir.glob("TASK-*.yaml")):
        text = path.read_text(encoding="utf-8")
        status_match = re.search(r"^status:\s*(\S+)", text, re.MULTILINE)
        if status_match is None or status_match.group(1) != "BLOCKED":
            continue
        own_id_match = re.search(r"^id:\s*(\S+)", text, re.MULTILINE)
        if own_id_match is not None and own_id_match.group(1) == task_id:
            continue
        if task_id in text:
            return True
    return False


def auto_closeout_blockers(
    task_payload: dict,
    *,
    pr_changed_files: tuple[str, ...],
    unblocks_others: bool,
) -> tuple[str, ...]:
    """Return reasons a task is NOT safe for automatic closeout (empty = auto-safe)."""
    reasons: list[str] = []
    if task_closeout_policy(task_payload) == "review":
        reasons.append("Task opts out of auto-closeout via `closeout: review`.")
    protected = sorted(
        path
        for path in pr_changed_files
        if any(path.startswith(prefix) for prefix in PROTECTED_ARTIFACT_PREFIXES)
    )
    if protected:
        reasons.append(
            "Merged PR touched protected scientific artifact(s): " + ", ".join(protected) + "."
        )
    if unblocks_others:
        reasons.append(
            "Task is referenced by a BLOCKED task; closing it may need a manual unblock decision."
        )
    return tuple(reasons)


def load_pr_changed_files(
    root: Path, pull_request: int, *, gh_path: str | None = None
) -> tuple[str, ...]:
    """Return the file paths changed by a PR via gh; empty tuple if unavailable."""
    resolved_gh_path = gh_path or find_gh_path()
    if resolved_gh_path is None:
        return ()
    result = run_command(
        [
            resolved_gh_path,
            "pr",
            "view",
            str(pull_request),
            "--json",
            "files",
            "--jq",
            ".files[].path",
        ],
        cwd=root,
        timeout=60,
    )
    if result.returncode != 0:
        return ()
    return tuple(line.strip() for line in result.stdout.splitlines() if line.strip())


def auto_safe_closeout_candidates(
    root: Path,
    report: CloseoutSweepReport,
    *,
    pr_changed_files_by_number: dict[int, tuple[str, ...]] | None = None,
) -> tuple[tuple[CloseoutSweepCandidate, tuple[str, ...]], ...]:
    """Pair each ready candidate with its auto-closeout blockers (empty = auto-safe)."""
    files_by_number = pr_changed_files_by_number or {}
    classified: list[tuple[CloseoutSweepCandidate, tuple[str, ...]]] = []
    for candidate in report.ready:
        task_file = _task_file_by_id(root, candidate.task_id)
        payload = load_task(task_file) if task_file is not None else {}
        pr_files = files_by_number.get(candidate.pull_request or -1)
        if pr_files is None and candidate.pull_request is not None:
            pr_files = load_pr_changed_files(root, candidate.pull_request)
        blockers = auto_closeout_blockers(
            payload,
            pr_changed_files=pr_files or (),
            unblocks_others=task_unblocks_others(root, candidate.task_id),
        )
        classified.append((candidate, blockers))
    return tuple(classified)


def apply_auto_safe_closeouts(
    root: Path,
    report: CloseoutSweepReport,
    *,
    pr_changed_files_by_number: dict[int, tuple[str, ...]] | None = None,
) -> CloseoutSweepApplyReport:
    """Flip only auto-safe ready candidates from REVIEW_READY to DONE."""
    if not git_status_clean(root):
        raise ValueError("Auto-safe closeout apply requires a clean git status.")
    classified = auto_safe_closeout_candidates(
        root, report, pr_changed_files_by_number=pr_changed_files_by_number
    )
    applied: list[CloseoutSweepCandidate] = []
    changed_files: list[Path] = []
    for candidate, blockers in classified:
        if blockers:
            continue
        task_file = _task_file_by_id(root, candidate.task_id)
        if task_file is None:
            continue
        text = task_file.read_text(encoding="utf-8")
        needle = "status: REVIEW_READY"
        if needle not in text:
            continue
        task_file.write_text(text.replace(needle, "status: DONE", 1), encoding="utf-8")
        applied.append(candidate)
        changed_files.append(task_file)
    return CloseoutSweepApplyReport(applied=tuple(applied), changed_files=tuple(changed_files))


def classify_full_repo_signal(
    conclusion: str | None,
    created_at: str | None,
    *,
    now: datetime | None = None,
    max_age_hours: float = 48.0,
) -> str:
    """Classify the latest completed full_repo signal: ok | red | stale | unknown."""
    if conclusion is None or not str(conclusion).strip():
        return "unknown"
    if str(conclusion).strip().lower() != "success":
        return "red"
    if created_at is None or not str(created_at).strip():
        return "unknown"
    try:
        created = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
    except ValueError:
        return "unknown"
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    current = now or datetime.now(timezone.utc)
    age_hours = (current - created).total_seconds() / 3600.0
    if age_hours > max_age_hours:
        return "stale"
    return "ok"


def full_repo_signal_status(
    root: Path,
    *,
    gh_path: str | None = None,
    now: datetime | None = None,
    max_age_hours: float = 48.0,
) -> str:
    """Return the latest main full_repo signal (ok|red|stale|unknown) via gh.

    Reads the most recent completed CI run on ``main`` (the main matrix runs
    full_repo on every push to main). Any gh failure yields ``unknown`` so the
    caller falls back to report-only.
    """
    resolved_gh_path = gh_path or find_gh_path()
    if resolved_gh_path is None:
        return "unknown"
    result = run_command(
        [
            resolved_gh_path,
            "run",
            "list",
            "--workflow",
            "ci.yml",
            "--branch",
            "main",
            "--event",
            "push",
            "--status",
            "completed",
            "--limit",
            "1",
            "--json",
            "conclusion,createdAt",
        ],
        cwd=root,
        timeout=60,
    )
    if result.returncode != 0:
        return "unknown"
    try:
        rows = json.loads(result.stdout)
    except json.JSONDecodeError:
        return "unknown"
    if not isinstance(rows, list) or not rows:
        return "unknown"
    latest = rows[0]
    return classify_full_repo_signal(
        latest.get("conclusion"),
        latest.get("createdAt"),
        now=now,
        max_age_hours=max_age_hours,
    )


def _load_merged_task_pull_requests_from_git(
    root: Path,
    *,
    limit: int,
    remote_url: str | None,
) -> dict[str, MergedTaskPullRequest]:
    """Load merged PR metadata keyed by TASK-XXXX from local git history."""
    result = run_command(
        [
            "git",
            "log",
            "--first-parent",
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
        squash_match = SQUASH_MERGE_SUBJECT_PATTERN.match(subject.strip())
        if squash_match is not None:
            pr_number = int(squash_match.group("number"))
            task_id = squash_match.group("task_id")
            candidate = MergedTaskPullRequest(
                task_id=task_id,
                number=pr_number,
                title=squash_match.group("title"),
                merged_at=merged_at.strip(),
                url=(f"{remote_url}/pull/{pr_number}" if remote_url else ""),
            )
            previous = by_task.get(task_id)
            if previous is None or candidate.merged_at > previous.merged_at:
                by_task[task_id] = candidate
            continue
        conventional_match = CONVENTIONAL_TASK_SUBJECT_PATTERN.match(subject.strip())
        if conventional_match is not None:
            task_id = conventional_match.group("task_id").upper()
            candidate = MergedTaskPullRequest(
                task_id=task_id,
                number=0,
                title=f"{task_id}: merged via conventional squash commit",
                merged_at=merged_at.strip(),
                url="",
            )
            previous = by_task.get(task_id)
            if previous is None or candidate.merged_at > previous.merged_at:
                by_task[task_id] = candidate
            continue
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


def _load_merged_task_pull_request_from_gh_search(
    root: Path,
    *,
    task_id: str,
    remote_url: str | None,
) -> MergedTaskPullRequest | None:
    """Resolve a conventional squash commit's PR number via exact task search."""
    gh_path = find_gh_path()
    if gh_path is None:
        return None
    result = run_command(
        [
            gh_path,
            "pr",
            "list",
            "--state",
            "merged",
            "--search",
            task_id,
            "--limit",
            "20",
            "--json",
            "number,title,mergedAt,headRefName,baseRefName,statusCheckRollup",
        ],
        cwd=root,
        timeout=60,
    )
    if result.returncode != 0:
        return None
    try:
        rows = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(rows, list):
        return None

    best: MergedTaskPullRequest | None = None
    for row in rows:
        if not isinstance(row, dict):
            continue
        title = str(row.get("title") or "").strip()
        title_match = PR_TITLE_TASK_PATTERN.match(title)
        if title_match is None or title_match.group("task_id") != task_id:
            continue
        try:
            pr_number = int(row["number"])
        except (KeyError, TypeError, ValueError):
            continue
        status_checks_passed, status_checks_pending = _status_checks_from_rollup(
            row.get("statusCheckRollup")
        )
        candidate = MergedTaskPullRequest(
            task_id=task_id,
            number=pr_number,
            title=title,
            merged_at=str(row.get("mergedAt") or "").strip(),
            url=(f"{remote_url}/pull/{pr_number}" if remote_url else ""),
            branch=str(row.get("headRefName") or "").strip(),
            base_branch=str(row.get("baseRefName") or "main").strip() or "main",
            status_checks_passed=status_checks_passed,
            status_checks_pending=status_checks_pending,
        )
        if best is None or candidate.merged_at > best.merged_at:
            best = candidate
    return best


def _status_checks_from_rollup(status_checks: object) -> tuple[bool | None, bool]:
    """Return (passed, pending) from GitHub statusCheckRollup-like payloads."""
    if not isinstance(status_checks, list):
        return None, False
    has_failure = False
    has_pending = False
    has_success = False
    for item in status_checks:
        if not isinstance(item, dict):
            continue
        conclusion = str(item.get("conclusion") or "").upper()
        status = str(item.get("status") or item.get("state") or "").upper()
        if conclusion in {"FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED"}:
            has_failure = True
        elif conclusion == "SUCCESS":
            has_success = True
        elif status and status not in {"COMPLETED", "SUCCESS"}:
            has_pending = True
    if has_failure:
        return False, has_pending
    if has_success and not has_pending:
        return True, False
    return None, has_pending


def _load_merged_task_pull_requests_from_gh(
    root: Path,
    *,
    limit: int,
    remote_url: str | None,
) -> dict[str, MergedTaskPullRequest]:
    """Load merged task PR metadata from GitHub CLI when it is available."""
    gh_path = find_gh_path()
    if gh_path is None:
        return {}
    result = run_command(
        [
            gh_path,
            "pr",
            "list",
            "--state",
            "merged",
            "--limit",
            str(limit),
            "--json",
            "number,title,mergedAt,headRefName,baseRefName,statusCheckRollup",
        ],
        cwd=root,
        timeout=60,
    )
    if result.returncode != 0:
        return {}

    try:
        rows = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}
    if not isinstance(rows, list):
        return {}

    by_task: dict[str, MergedTaskPullRequest] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        title = str(row.get("title") or "").strip()
        title_match = PR_TITLE_TASK_PATTERN.match(title)
        if title_match is None:
            continue
        try:
            pr_number = int(row["number"])
        except (KeyError, TypeError, ValueError):
            continue
        task_id = title_match.group("task_id")
        status_checks_passed, status_checks_pending = _status_checks_from_rollup(
            row.get("statusCheckRollup")
        )
        candidate = MergedTaskPullRequest(
            task_id=task_id,
            number=pr_number,
            title=title,
            merged_at=str(row.get("mergedAt") or "").strip(),
            url=(f"{remote_url}/pull/{pr_number}" if remote_url else ""),
            branch=str(row.get("headRefName") or "").strip(),
            base_branch=str(row.get("baseRefName") or "main").strip() or "main",
            status_checks_passed=status_checks_passed,
            status_checks_pending=status_checks_pending,
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

        pr_metadata = load_pr_metadata(root, pr.number) or merged_task_pr_metadata(pr)
        closeout = build_closeout_report(
            root,
            task_id=task_id,
            pull_request=pr.number,
            apply=False,
            pr_metadata=pr_metadata,
        )
        binding_blockers = closeout_pr_metadata_binding_blockers(
            task_id=task_id,
            pr_metadata=pr_metadata,
        )
        blockers = closeout.blockers + binding_blockers
        outcome = closeout.outcome if not binding_blockers else "BLOCKED"
        candidate = CloseoutSweepCandidate(
            task_id=task_id,
            task_title=task_title,
            pull_request=pr.number,
            pr_title=pr.title,
            pr_url=pr.url,
            outcome=outcome,
            blockers=blockers,
            required_actions=closeout.required_actions,
            recommended_apply_command=(
                f"python3 scripts/apl_closeout_task.py --task {task_id} --pr {pr.number} --apply"
                if outcome == "READY_TO_APPLY"
                else None
            ),
        )
        if outcome == "READY_TO_APPLY":
            ready.append(candidate)
        else:
            blocked.append(candidate)

    return CloseoutSweepReport(
        branch=current_branch(root),
        ready=tuple(ready),
        blocked=tuple(blocked),
        skipped=tuple(skipped),
    )


def render_closeout_sweep_apply_report(report: CloseoutSweepApplyReport) -> str:
    """Render applied closeout sweep changes."""
    lines = [f"Applied closeout candidates: {len(report.applied)}"]
    if not report.applied:
        lines.append("- none")
        return "\n".join(lines)
    for candidate, path in zip(report.applied, report.changed_files, strict=True):
        lines.append(f"- {candidate.task_id} -> DONE ({path.as_posix()})")
    return "\n".join(lines)


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
