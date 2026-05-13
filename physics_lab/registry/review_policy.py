"""Protocol parsing and policy helpers for maintainer review."""

from __future__ import annotations

from dataclasses import dataclass
import re


BRANCH_PATTERN = re.compile(
    r"^agent/(?P<contributor>[a-z0-9-]+)/(?P<agent>[a-z0-9-]+)/"
    r"task-(?P<number>[0-9]{4})-(?P<slug>[a-z0-9-]+)$"
)
PROPOSAL_BRANCH_PATTERN = re.compile(
    r"^agent/(?P<contributor>[a-z0-9-]+)/(?P<agent>[a-z0-9-]+)/"
    r"propose-task-(?P<slug>[a-z0-9-]+)$"
)
CLOSEOUT_BRANCH_PATTERN = re.compile(
    r"^agent/(?P<contributor>[a-z0-9-]+)/(?P<agent>[a-z0-9-]+)/"
    r"closeout-(?P<slug>[a-z0-9-]+)$"
)
TASK_QUEUE_BRANCH_PATTERN = re.compile(
    r"^agent/(?P<contributor>[a-z0-9-]+)/(?P<agent>[a-z0-9-]+)/"
    r"task-queue-(?P<slug>[a-z0-9-]+)$"
)
MICROTASK_BRANCH_PATTERN = re.compile(
    r"^agent/(?P<contributor>[a-z0-9-]+)/(?P<agent>[a-z0-9-]+)/"
    r"microtask-(?P<microtask_id>[A-Z0-9]{3,8}-[0-9]{3})-(?P<slug>[a-z0-9-]+)$"
)
MICROTASK_BATCH_BRANCH_PATTERN = re.compile(
    r"^agent/(?P<contributor>[a-z0-9-]+)/(?P<agent>[a-z0-9-]+)/"
    r"microtask-batch-(?P<queue_id>[a-z0-9-]+)--(?P<slug>[a-z0-9-]+)$"
)
PR_TITLE_PATTERN = re.compile(r"^(?P<task_id>TASK-[0-9]{4}): .+")
PROPOSAL_PR_TITLE_PATTERN = re.compile(r"^TASK-PROPOSAL: .+")
CLOSEOUT_PR_TITLE_PATTERN = re.compile(r"^TASK-CLOSEOUT: .+")
TASK_QUEUE_PR_TITLE_PATTERN = re.compile(r"^TASK-QUEUE: .+")
MICROTASK_PR_TITLE_PATTERN = re.compile(r"^microtask\((?P<queue_id>[a-z0-9-]+)\): .+")
PR_METADATA_FIELDS = (
    "Contributor ID",
    "GitHub username",
    "Agent tool",
    "Task ID",
    "Branch",
    "Human reviewer",
)
PR_METADATA_FIELD_ALIASES = {
    "Task ID": ("Task ID", "Task ID / Proposal / Queue"),
}


@dataclass(frozen=True)
class ReviewProtocol:
    """Parsed branch and PR-title protocol state for a review run."""

    kind: str
    branch_task_id: str | None
    proposal_slug: str | None
    task_queue_slug: str | None
    microtask_id: str | None
    microtask_queue_id: str | None
    title_microtask_queue_id: str | None

    @property
    def is_supported(self) -> bool:
        return self.kind != "unknown"


@dataclass(frozen=True)
class PolicyMessages:
    """Blockers and required fixes emitted by an isolated policy rule."""

    blockers: tuple[str, ...] = ()
    required_fixes: tuple[str, ...] = ()


def branch_task_id(branch: str) -> str | None:
    """Extract TASK-XXXX from a canonical branch name."""
    match = BRANCH_PATTERN.match(branch)
    if match is None:
        return None
    return f"TASK-{match.group('number')}"


def branch_proposal_slug(branch: str) -> str | None:
    """Extract the task-proposal slug from a proposal branch."""
    match = PROPOSAL_BRANCH_PATTERN.match(branch)
    if match is None:
        return None
    return str(match.group("slug"))


def branch_task_queue_slug(branch: str) -> str | None:
    """Extract the task-queue slug from a task-queue branch."""
    match = TASK_QUEUE_BRANCH_PATTERN.match(branch)
    if match is None:
        return None
    return str(match.group("slug"))


def branch_microtask_id(branch: str) -> str | None:
    """Extract the microtask id from a canonical microtask branch name."""
    match = MICROTASK_BRANCH_PATTERN.match(branch)
    if match is None:
        return None
    return str(match.group("microtask_id"))


def branch_microtask_queue_id(branch: str) -> str | None:
    """Extract the queue id from a canonical batch microtask branch name."""
    match = MICROTASK_BATCH_BRANCH_PATTERN.match(branch)
    if match is None:
        return None
    return str(match.group("queue_id"))


def microtask_queue_id_from_title(title: str) -> str | None:
    """Extract the microtask queue id from a microtask PR title."""
    match = MICROTASK_PR_TITLE_PATTERN.match(title)
    if match is None:
        return None
    return str(match.group("queue_id"))


def classify_review_protocol(branch: str, *, pr_title: str | None = None) -> ReviewProtocol:
    """Classify a review target as task, proposal, closeout, microtask, or unknown."""
    proposal_slug = branch_proposal_slug(branch)
    task_queue_slug = branch_task_queue_slug(branch)
    branch_microtask = branch_microtask_id(branch)
    branch_microtask_queue = branch_microtask_queue_id(branch)
    title_microtask_queue = microtask_queue_id_from_title(pr_title or "")
    title_is_closeout = (
        pr_title is not None and CLOSEOUT_PR_TITLE_PATTERN.match(pr_title) is not None
    )
    title_is_task_queue = (
        pr_title is not None and TASK_QUEUE_PR_TITLE_PATTERN.match(pr_title) is not None
    )

    if proposal_slug is not None:
        kind = "proposal"
    elif CLOSEOUT_BRANCH_PATTERN.match(branch) is not None or title_is_closeout:
        kind = "closeout"
    elif task_queue_slug is not None or title_is_task_queue:
        kind = "task_queue"
    elif (
        branch_microtask is not None
        or branch_microtask_queue is not None
        or title_microtask_queue is not None
    ):
        kind = "microtask"
    elif BRANCH_PATTERN.match(branch) is not None:
        kind = "task"
    else:
        kind = "unknown"

    return ReviewProtocol(
        kind=kind,
        branch_task_id=branch_task_id(branch),
        proposal_slug=proposal_slug,
        task_queue_slug=task_queue_slug,
        microtask_id=branch_microtask,
        microtask_queue_id=branch_microtask_queue,
        title_microtask_queue_id=title_microtask_queue,
    )


def missing_pr_metadata_fields(body: str) -> tuple[str, ...]:
    """Return required PR metadata fields that are still blank."""
    missing: list[str] = []
    lines = body.splitlines()
    for field in PR_METADATA_FIELDS:
        field_names = PR_METADATA_FIELD_ALIASES.get(field, (field,))
        matching_line = None
        for field_name in field_names:
            prefix = f"- {field_name}:"
            matching_line = next((line for line in lines if line.startswith(prefix)), None)
            if matching_line is not None:
                break
        if matching_line is None:
            missing.append(field)
            continue
        value = matching_line.split(":", 1)[1].strip()
        if value == "":
            missing.append(field)
    return tuple(missing)


def validate_pr_title(
    *,
    review_kind: str,
    title: str,
    resolved_task_id: str,
) -> PolicyMessages:
    """Validate PR title format for the classified review lane."""
    if review_kind == "proposal":
        if PROPOSAL_PR_TITLE_PATTERN.match(title) is None:
            return PolicyMessages(
                required_fixes=("PR title does not follow TASK-PROPOSAL: ... format.",)
            )
        return PolicyMessages()
    if review_kind == "closeout":
        if CLOSEOUT_PR_TITLE_PATTERN.match(title) is None:
            return PolicyMessages(
                required_fixes=("PR title does not follow TASK-CLOSEOUT: ... format.",)
            )
        return PolicyMessages()
    if review_kind == "task_queue":
        if TASK_QUEUE_PR_TITLE_PATTERN.match(title) is None:
            return PolicyMessages(
                required_fixes=("PR title does not follow TASK-QUEUE: ... format.",)
            )
        return PolicyMessages()
    if review_kind == "microtask":
        if MICROTASK_PR_TITLE_PATTERN.match(title) is None:
            return PolicyMessages(
                required_fixes=("PR title does not follow microtask(<queue-id>): ... format.",)
            )
        return PolicyMessages()

    title_match = PR_TITLE_PATTERN.match(title)
    if title_match is None:
        return PolicyMessages(
            required_fixes=("PR title does not follow TASK-XXXX: ... format.",)
        )
    title_task_id = title_match.group("task_id")
    if title_task_id != resolved_task_id:
        return PolicyMessages(
            blockers=(
                f"PR title task id {title_task_id} does not match {resolved_task_id}.",
            )
        )
    return PolicyMessages()
