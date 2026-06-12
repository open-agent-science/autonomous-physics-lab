"""Deterministic helpers for maintainer PR review and task closeout."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path
import re
import sys
from typing import Any
import yaml

from physics_lab.registry.review_git import (
    CommandResult,  # noqa: F401 — re-exported for backwards compatibility
    run_command,
    run_git_command,
    branch_exists,
    current_branch,
    git_status_clean,
    local_branch_exists,
    changed_files_vs_main,
    parse_added_lines,  # noqa: F401 — re-exported; tests import from here
)
from physics_lab.registry.review_worktree_gc import (
    DEFAULT_GC_AGE_HOURS,
    gc_review_worktrees,
    teardown_own_worktree,
)
from physics_lab.registry.repo_python import resolve_validation_python
from physics_lab.registry.generated_state import sync_generated_task_state
from physics_lab.registry.pr_capability import find_gh_path
from physics_lab.registry.task_discovery import find_task_files
from physics_lab.registry.review_checks import (
    line_is_rule_catalog_line,  # noqa: F401 — re-exported
    load_claim_status_from_ref,  # noqa: F401 — re-exported; tests import from here
    overclaim_advisory_hits,
    overclaim_hits,
    security_pattern_hits,
    sensitive_surface_hits,
    cross_platform_advisory_hits,
    cross_platform_surface_hits,
    coauthor_trailer_advisory_hits,
    decision_regression_advisory_hits,
    follow_up_task_advisory_hits,
    missing_expected_outputs,
    unexpected_protected_changes,
    claim_status_promotions,
)
from physics_lab.registry.result_publication_gate import check_payload
from physics_lab.registry.review_policy import (
    BRANCH_PATTERN,  # noqa: F401 — re-exported for backwards compatibility
    CLOSEOUT_BRANCH_PATTERN,  # noqa: F401 — re-exported for backwards compatibility
    CLOSEOUT_PR_TITLE_PATTERN,  # noqa: F401 — re-exported for backwards compatibility
    MICROTASK_BATCH_BRANCH_PATTERN,  # noqa: F401 — re-exported for backwards compatibility
    MICROTASK_BRANCH_PATTERN,  # noqa: F401 — re-exported for backwards compatibility
    MICROTASK_PR_TITLE_PATTERN,  # noqa: F401 — re-exported for backwards compatibility
    PROPOSAL_BRANCH_PATTERN,  # noqa: F401 — re-exported for backwards compatibility
    PROPOSAL_PR_TITLE_PATTERN,  # noqa: F401 — re-exported for backwards compatibility
    PR_TITLE_PATTERN,  # noqa: F401 — re-exported for backwards compatibility
    TASK_QUEUE_BRANCH_PATTERN,  # noqa: F401 — re-exported for backwards compatibility
    TASK_QUEUE_PR_TITLE_PATTERN,  # noqa: F401 — re-exported for backwards compatibility
    branch_microtask_id,  # noqa: F401 — re-exported; tests import from here
    branch_microtask_queue_id,  # noqa: F401 — re-exported; tests import from here
    branch_proposal_slug,  # noqa: F401 — re-exported; tests import from here
    branch_task_queue_slug,  # noqa: F401 — re-exported; tests import from here
    branch_task_id,  # noqa: F401 — re-exported; tests import from here
    agent_tool_metadata_mismatch,
    classify_review_protocol,
    missing_pr_metadata_fields,  # noqa: F401 — re-exported; tests import from here
    missing_pr_template_sections,  # noqa: F401 — re-exported; tests import from here
    validate_pr_title,
)
from physics_lab.registry.task_proposals import load_task_proposal
from physics_lab.registry.tasks import load_task
from physics_lab.registry.task_closeout import (
    PUBLIC_STATE_CLOSEOUT_DOCS,
    render_public_state_doc_checklist,
)
from physics_lab.registry.task_unblock import safe_unblock_candidates


REVIEW_BUNDLE_BRANCH_PATTERN = re.compile(r"^- branch: `(?P<branch>.+)`$")
RUN_ENTRY_PATTERN = re.compile(r"^## Run #(?P<number>[0-9]+)$")
LOCAL_PR_REF_PATTERN = re.compile(r"^(?:refs/remotes/)?origin/pr-[0-9]+$")
DRY_RUN_KEYWORDS = ("dry run", "contributor", "pilot")
PROPOSAL_TRIAGE_BODY_MARKERS = (
    "proposal triage",
    "proposal-pool triage",
    "proposal superseded",
    "proposal rejected",
    "proposal cleanup",
    "stale proposal",
)
CLOSEOUT_VALIDATION_COMMANDS = (
    "python3 -m pytest",
    "python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings",
)
MICROTASK_VALIDATION_COMMANDS = (
    "python3 -m physics_lab.cli validate-repo .",
    "python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings",
)
TASK_QUEUE_VALIDATION_COMMANDS = (
    "python3 -m physics_lab.cli validate-repo .",
    "python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings",
)
TASK_PROPOSAL_VALIDATION_COMMANDS = (
    "python3 -m physics_lab.cli validate-repo .",
    "python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings",
)
TASK_QUEUE_ALLOWED_STATUSES = frozenset({"PROPOSED", "READY", "BLOCKED"})
TASK_QUEUE_FORBIDDEN_PREFIXES = (
    "agent_runs/",
    "claims/",
    "experiments/",
    "experiment_proposals/",
    "hypotheses/",
    "hypothesis_proposals/",
    "knowledge/",
    "results/",
)
AGENT_PUBLICATION_TIERS = frozenset({"AGENT_PUBLISHED", "AGENT_VALIDATED"})
CONTEXT_BUNDLE_SOURCE_FILES = frozenset(
    {
        "AGENTS.md",
        "CLAUDE.md",
        "docs/strategy.md",
        "docs/current-missions.md",
        "missions/current.yaml",
        "docs/mission-control.md",
        "docs/agent-task-protocol.md",
        "docs/agent-scientific-work-mode.md",
        "docs/contributing-workflow.md",
        "docs/maintainer-review-agent.md",
        "docs/scientific-micro-task-protocol.md",
        "scripts/generate_context_bundle.py",
    }
)
PUBLIC_STATE_DOCS = PUBLIC_STATE_CLOSEOUT_DOCS
PUBLIC_STATE_DOC_TRIGGER_PREFIXES = (
    "experiments/",
    "results/",
    "claims/",
    "knowledge/",
    "campaign_profiles/",
    "agent_runs/",
    "hypothesis_proposals/",
    "experiment_proposals/",
    "data/nuclear_masses/",
)
PUBLIC_STATE_DOC_TRIGGER_FILES = frozenset(
    {
        "docs/strategy.md",
        "docs/current-missions.md",
        "missions/current.yaml",
        "docs/next-steps.md",
        "docs/roadmap.md",
        "docs/public-release-gates.md",
    }
)
PUBLIC_STATE_TASK_MARKERS = (
    "agent-run",
    "autonomous",
    "benchmark",
    "campaign",
    "completed experiment",
    "experiment",
    "flagship",
    "holdout",
    "mission",
    "nuclear",
    "public-facing",
    "release",
    "result",
    "scientific",
    "status",
)


@dataclass(frozen=True)
class PullRequestMetadata:
    """Best-effort metadata loaded from GitHub CLI."""

    number: int
    title: str
    body: str
    branch: str
    base_branch: str
    state: str
    merged: bool
    status_checks_passed: bool | None
    status_checks_pending: bool
    changed_files: tuple[str, ...]
    head_sha: str = ""


@dataclass(frozen=True)
class CleanPrWorktree:
    """Prepared clean worktree for reviewing a remote PR head."""

    root: Path
    review_ref: str
    ready: bool
    message: str
    fallback_commands: tuple[str, ...] = ()


@dataclass(frozen=True)
class ValidationSummary:
    """Result of running task validation commands."""

    status: str
    failed_commands: tuple[str, ...]
    executed_commands: tuple[str, ...] = ()
    skipped_commands: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReviewReport:
    """Rendered maintainer review decision."""

    verdict: str
    risk: str
    task_id: str
    branch: str
    changed_files: tuple[str, ...]
    validation: str
    security_risks: tuple[str, ...]
    blockers: tuple[str, ...]
    required_fixes: tuple[str, ...]
    recommended_action: str
    advisory_warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class ArtifactReviewSignal:
    """Classification for scientific-memory artifacts changed by a PR."""

    path: str
    artifact_class: str
    review_tier: str | None = None
    before_status: str | None = None
    after_status: str | None = None


@dataclass(frozen=True)
class CloseoutReport:
    """Rendered maintainer closeout decision."""

    outcome: str
    task_id: str
    pull_request: int
    branch: str
    task_status: str
    merged: str
    accepted_outputs: str
    ci_status: str
    blockers: tuple[str, ...]
    required_actions: tuple[str, ...]
    suggested_actions: tuple[str, ...]
    applied_changes: tuple[str, ...]


def resolve_task_file(root: Path, task_id: str) -> Path:
    """Resolve a task id to its unique task file."""
    matches = find_task_files(root, task_id)
    if not matches:
        raise FileNotFoundError(f"No task file found for {task_id}")
    if len(matches) > 1:
        rendered = ", ".join(path.name for path in matches)
        raise ValueError(f"Multiple task files found for {task_id}: {rendered}")
    return matches[0]


def resolve_microtask_queue_file(root: Path, queue_id: str) -> Path:
    """Resolve a microtask queue id to a queue file under tasks/microtasks."""
    path = root / "tasks" / "microtasks" / f"{queue_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"No microtask queue file found for queue id {queue_id}."
        )
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping in microtask queue file: {path}")
    actual_queue_id = str(payload.get("queue_id") or "").strip()
    if actual_queue_id != queue_id:
        raise ValueError(
            f"Microtask queue file {path.name} declares queue_id={actual_queue_id!r}, "
            f"expected {queue_id!r}."
        )
    return path


def changed_task_proposal_files(changed_files: tuple[str, ...]) -> tuple[str, ...]:
    """Return changed task proposal files excluding the template."""
    return tuple(
        path
        for path in changed_files
        if path.startswith("tasks/proposals/")
        and path.endswith(".yaml")
        and Path(path).name != "TASK-PROPOSAL-TEMPLATE.yaml"
    )


def body_requests_proposal_triage(body: str | None) -> bool:
    """Return whether the PR body explicitly frames proposal status cleanup."""
    normalized = (body or "").lower()
    return any(marker in normalized for marker in PROPOSAL_TRIAGE_BODY_MARKERS)


def latest_review_bundle(root: Path, branch: str) -> Path | None:
    """Return the latest review bundle for a branch if present."""
    safe_branch = branch.replace("/", "-")
    bundles = sorted((root / "_snapshots").glob(f"review_{safe_branch}_*.md"))
    if not bundles:
        return None
    return bundles[-1]


def ensure_review_bundle(root: Path, branch: str, *, can_generate: bool) -> tuple[Path | None, str]:
    """Return a valid review bundle path or a status string."""
    bundle = latest_review_bundle(root, branch)
    if bundle is not None:
        if review_bundle_branch(bundle) == branch:
            return bundle, "present"
        return bundle, "invalid"
    if not can_generate:
        return None, "missing"
    script = Path(__file__).resolve().parents[2] / "scripts" / "apl_review_bundle.py"
    if not script.exists():
        script = root / "scripts" / "apl_review_bundle.py"
    result = run_command(
        [sys.executable, str(script), "--root", str(root)],
        cwd=root,
        timeout=120,
    )
    if result.returncode != 0:
        return None, "missing"
    bundle = latest_review_bundle(root, branch)
    if bundle is None:
        return None, "missing"
    if review_bundle_branch(bundle) != branch:
        return bundle, "invalid"
    return bundle, "generated"


def review_bundle_branch(path: Path) -> str | None:
    """Read the branch metadata from a review bundle."""
    for line in path.read_text(encoding="utf-8").splitlines():
        match = REVIEW_BUNDLE_BRANCH_PATTERN.match(line.strip())
        if match is not None:
            return match.group("branch")
    return None


def _portable_validation_command(
    command_text: str, *, python_executable: str | None = None
) -> str:
    """Run validation through local portable executables where needed.

    ``python_executable`` is the interpreter used for ``python3``/``python``
    validation commands; it defaults to ``sys.executable``. Callers with a
    repository root pass the resolved repo-venv interpreter so validation does not
    run on an unsupported launcher (see TASK-0725).
    """
    interpreter = python_executable or sys.executable
    for launcher in ("python3 ", "python "):
        if command_text.startswith(launcher):
            return f'"{interpreter}" {command_text.removeprefix(launcher)}'
    if _looks_like_repo_shell_script(command_text):
        bash = _git_bash_path()
        if bash is not None:
            return f'"{bash}" -lc "{command_text}"'
        return f"bash {command_text}"
    return command_text


def _looks_like_repo_shell_script(command_text: str) -> bool:
    parts = command_text.strip().split()
    if len(parts) != 1:
        return False
    command = parts[0]
    return command.startswith("./") and command.endswith(".sh")


def _git_bash_path() -> str | None:
    candidates = (
        Path("C:/Program Files/Git/bin/bash.exe"),
        Path("C:/Program Files/Git/usr/bin/bash.exe"),
    )
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def ci_aware_validation_command(command_text: str) -> str | None:
    """Return the local validation command still needed after green PR CI.

    PR CI already runs ruff, fast pytest, and repository validation. The
    maintainer review helper should not duplicate those checks when GitHub has
    already reported them green, but it should still run the local-only
    full-repo pytest slice for task files that request a bare pytest run.
    """
    normalized = " ".join(command_text.strip().split())
    python_launcher = ""
    python_args = normalized
    for launcher in ("python3 ", "python "):
        if normalized.startswith(launcher):
            python_launcher = launcher.strip()
            python_args = normalized.removeprefix(launcher)
            break
    if python_args == "-m ruff check .":
        return None
    if python_args.startswith("-m physics_lab.cli validate-repo ."):
        return None
    if python_args == "-m pytest":
        return f"{python_launcher or 'python3'} -m pytest -m full_repo"
    if python_args.startswith("-m pytest --basetemp="):
        if len(python_args.split()) > 3:
            return command_text
        target = f"{python_launcher or 'python3'} -m pytest"
        return command_text.replace(target, f"{target} -m full_repo", 1)
    if python_args.startswith("-m pytest -m 'not full_repo'"):
        return None
    if python_args.startswith('-m pytest -m "not full_repo"'):
        return None
    return command_text


def run_task_validation(
    root: Path,
    task_payload: dict[str, Any],
    *,
    enabled: bool,
    skip_commands_containing: tuple[str, ...] = (),
    ci_aware: bool = False,
) -> ValidationSummary:
    """Run validation commands from the task file when feasible."""
    if not enabled:
        return ValidationSummary(status="not_run", failed_commands=())
    failed_commands: list[str] = []
    executed_commands: list[str] = []
    skipped_commands: list[str] = []
    # Prefer the repository venv interpreter so validation never runs on an
    # unsupported launcher (e.g. a bare system python 3.9) — see TASK-0725.
    validation_python = resolve_validation_python(root)
    for command in task_payload.get("validation", {}).get("commands", []):
        command_text = str(command)
        if any(token in command_text for token in skip_commands_containing):
            skipped_commands.append(command_text)
            continue
        local_command = ci_aware_validation_command(command_text) if ci_aware else command_text
        if local_command is None:
            skipped_commands.append(command_text)
            continue
        executed_commands.append(local_command)
        result = run_command(
            _portable_validation_command(local_command, python_executable=validation_python),
            cwd=root,
            shell=True,
            # The full local pytest fallback (used when GitHub checks are not yet
            # green and ci-aware cannot reuse them) runs close to 300s, so a 300s
            # timeout crashed the review tool. Give the fallback ample headroom;
            # ci-aware mode still skips this re-run when checks are already green.
            # See TASK-0466, F3.
            timeout=900,
        )
        if result.returncode != 0:
            failed_commands.append(command_text)
    if failed_commands:
        return ValidationSummary(
            status="fail",
            failed_commands=tuple(failed_commands),
            executed_commands=tuple(executed_commands),
            skipped_commands=tuple(skipped_commands),
        )
    return ValidationSummary(
        status="pass",
        failed_commands=(),
        executed_commands=tuple(executed_commands),
        skipped_commands=tuple(skipped_commands),
    )


def load_pr_metadata(root: Path, number: int) -> PullRequestMetadata | None:
    """Load PR metadata through the GitHub CLI when available."""
    gh_path = find_gh_path()
    if gh_path is None:
        return None
    result = run_command(
        [
            gh_path,
            "pr",
            "view",
            str(number),
            "--json",
            "number,title,body,headRefName,headRefOid,baseRefName,state,mergedAt,statusCheckRollup,files",
        ],
        cwd=root,
        timeout=30,
    )
    if result.returncode != 0:
        return _load_pr_metadata_from_list(root, number, gh_path=gh_path)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return _load_pr_metadata_from_list(root, number, gh_path=gh_path)
    return _pull_request_metadata_from_payload(payload)


def _load_pr_metadata_from_list(
    root: Path,
    number: int,
    *,
    gh_path: str | None = None,
) -> PullRequestMetadata | None:
    """Fallback PR metadata path for flaky direct gh pr view calls."""
    resolved_gh_path = gh_path or find_gh_path()
    if resolved_gh_path is None:
        return None
    result = run_command(
        [
            resolved_gh_path,
            "pr",
            "list",
            "--state",
            "all",
            "--limit",
            "200",
            "--json",
            "number,title,headRefName,headRefOid,baseRefName,state,mergedAt,statusCheckRollup",
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
    for row in rows:
        if isinstance(row, dict) and int(row.get("number") or -1) == number:
            return _pull_request_metadata_from_payload(row)
    return None


def _pull_request_metadata_from_payload(payload: dict[str, Any]) -> PullRequestMetadata:
    """Normalize a GitHub CLI PR payload into internal metadata."""
    changed_files = tuple(
        str(item.get("path") or "").strip()
        for item in (payload.get("files") or [])
        if str(item.get("path") or "").strip()
    )
    status_checks = payload.get("statusCheckRollup") or []
    has_failure = False
    has_pending = False
    has_success = False
    for item in status_checks:
        conclusion = str(item.get("conclusion") or "").upper()
        state = str(item.get("state") or "").upper()
        if conclusion in {"FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED"}:
            has_failure = True
        elif conclusion == "SUCCESS":
            has_success = True
        elif state and state not in {"COMPLETED", "SUCCESS"}:
            has_pending = True
    status_passed: bool | None
    if has_failure:
        status_passed = False
    elif has_success and not has_pending:
        status_passed = True
    else:
        status_passed = None
    return PullRequestMetadata(
        number=int(payload["number"]),
        title=str(payload.get("title") or ""),
        body=str(payload.get("body") or ""),
        branch=str(payload.get("headRefName") or ""),
        base_branch=str(payload.get("baseRefName") or "main"),
        state=str(payload.get("state") or ""),
        merged=bool(payload.get("mergedAt")),
        status_checks_passed=status_passed,
        status_checks_pending=has_pending,
        changed_files=changed_files,
        head_sha=str(payload.get("headRefOid") or ""),
    )


def _clean_pr_worktree_path(root: Path, metadata: PullRequestMetadata) -> Path:
    """Return the deterministic local path for a generated PR review worktree."""
    suffix = metadata.head_sha[:12] if metadata.head_sha else "unknown"
    return root / ".worktrees" / "_reviews" / f"pr-{metadata.number}-{suffix}"


def _clean_local_ref_worktree_path(root: Path, ref: str, head_sha: str) -> Path:
    """Return the deterministic path for a generated local-ref review worktree."""
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", ref).strip("-") or "local-pr-ref"
    suffix = head_sha[:12] if head_sha else "unknown"
    return root / ".worktrees" / "_reviews" / f"{normalized}-{suffix}"


def prepare_clean_local_ref_worktree(root: Path, ref: str) -> CleanPrWorktree:
    """Check out an already-fetched PR ref in a clean disposable worktree."""
    fallback_commands = (
        "git fetch origin pull/<number>/head:refs/remotes/origin/pr-<number>",
        f"git worktree add --detach <review-worktree> {ref}",
        f"python3 scripts/apl_review_pr.py --branch {ref} --task <TASK-XXXX>",
    )
    rev_parse = run_git_command(["rev-parse", "--verify", ref], cwd=root, timeout=30)
    if rev_parse.returncode != 0:
        detail = (rev_parse.stderr or rev_parse.stdout).strip()
        return CleanPrWorktree(
            root=root,
            review_ref=ref,
            ready=False,
            message="Could not resolve local PR ref" + (f": {detail}" if detail else "."),
            fallback_commands=fallback_commands,
        )
    head_sha = rev_parse.stdout.strip().splitlines()[0].strip()
    worktree = _clean_local_ref_worktree_path(root, ref, head_sha)
    if worktree.exists():
        remove = run_git_command(
            ["worktree", "remove", "--force", str(worktree)],
            cwd=root,
            extra_safe_directories=(worktree,),
            timeout=120,
        )
        if remove.returncode != 0:
            detail = (remove.stderr or remove.stdout).strip()
            return CleanPrWorktree(
                root=root,
                review_ref=ref,
                ready=False,
                message="Could not replace existing local PR-ref review worktree"
                + (f": {detail}" if detail else "."),
                fallback_commands=fallback_commands,
            )
    worktree.parent.mkdir(parents=True, exist_ok=True)
    add = run_git_command(
        ["worktree", "add", "--detach", str(worktree), head_sha],
        cwd=root,
        extra_safe_directories=(worktree,),
        timeout=120,
    )
    if add.returncode != 0:
        detail = (add.stderr or add.stdout).strip()
        return CleanPrWorktree(
            root=root,
            review_ref=ref,
            ready=False,
            message="Could not create local PR-ref review worktree"
            + (f": {detail}" if detail else "."),
            fallback_commands=fallback_commands,
        )
    if not git_status_clean(worktree, ignore_paths=()):
        return CleanPrWorktree(
            root=worktree,
            review_ref="HEAD",
            ready=False,
            message="Prepared local PR-ref review worktree is not clean.",
            fallback_commands=fallback_commands,
        )
    return CleanPrWorktree(
        root=worktree,
        review_ref="HEAD",
        ready=True,
        message=f"Reviewing {ref} from clean local PR-ref worktree at {worktree}.",
        fallback_commands=fallback_commands,
    )


def prepare_clean_pr_worktree(root: Path, metadata: PullRequestMetadata) -> CleanPrWorktree:
    """Fetch a PR head and check it out in a clean disposable worktree."""
    fallback_commands = (
        f"git fetch origin refs/heads/{metadata.branch}:refs/remotes/origin/{metadata.branch}",
        f"git worktree add --detach {_clean_pr_worktree_path(root, metadata)} {metadata.head_sha or '<head-sha>'}",
        f"python3 scripts/apl_review_pr.py --pr {metadata.number}",
    )
    if not metadata.branch:
        return CleanPrWorktree(
            root=root,
            review_ref="HEAD",
            ready=False,
            message="PR metadata did not include headRefName.",
            fallback_commands=fallback_commands,
        )
    if not metadata.head_sha:
        return CleanPrWorktree(
            root=root,
            review_ref="HEAD",
            ready=False,
            message="PR metadata did not include headRefOid.",
            fallback_commands=fallback_commands,
        )
    fetch = run_git_command(
        [
            "fetch",
            "--no-tags",
            "origin",
            f"refs/heads/{metadata.branch}:refs/remotes/origin/{metadata.branch}",
        ],
        cwd=root,
        timeout=120,
    )
    if fetch.returncode != 0:
        detail = (fetch.stderr or fetch.stdout).strip()
        return CleanPrWorktree(
            root=root,
            review_ref="HEAD",
            ready=False,
            message="Could not fetch PR head from origin" + (f": {detail}" if detail else "."),
            fallback_commands=fallback_commands,
        )

    worktree = _clean_pr_worktree_path(root, metadata)
    if worktree.exists():
        remove = run_git_command(
            ["worktree", "remove", "--force", str(worktree)],
            cwd=root,
            extra_safe_directories=(worktree,),
            timeout=120,
        )
        if remove.returncode != 0:
            detail = (remove.stderr or remove.stdout).strip()
            return CleanPrWorktree(
                root=root,
                review_ref="HEAD",
                ready=False,
                message="Could not replace existing PR review worktree"
                + (f": {detail}" if detail else "."),
                fallback_commands=fallback_commands,
            )
    worktree.parent.mkdir(parents=True, exist_ok=True)
    add = run_git_command(
        ["worktree", "add", "--detach", str(worktree), metadata.head_sha],
        cwd=root,
        extra_safe_directories=(worktree,),
        timeout=120,
    )
    if add.returncode != 0:
        detail = (add.stderr or add.stdout).strip()
        return CleanPrWorktree(
            root=root,
            review_ref="HEAD",
            ready=False,
            message="Could not create clean PR review worktree"
            + (f": {detail}" if detail else "."),
            fallback_commands=fallback_commands,
        )
    if not git_status_clean(worktree, ignore_paths=()):
        return CleanPrWorktree(
            root=worktree,
            review_ref="HEAD",
            ready=False,
            message="Prepared PR review worktree is not clean.",
            fallback_commands=fallback_commands,
        )
    return CleanPrWorktree(
        root=worktree,
        review_ref="HEAD",
        ready=True,
        message=f"Reviewing PR #{metadata.number} from clean remote worktree at {worktree}.",
        fallback_commands=fallback_commands,
    )


def context_bundle_followups(
    changed_files: tuple[str, ...],
    *,
    sync_board: bool = False,
) -> tuple[str, ...]:
    """Return reminders when merged work touched CONTEXT.md source surfaces."""
    del sync_board  # tasks/ACTIVE.md was retired; the board is no longer a bundle source.
    touched = {path for path in changed_files if path in CONTEXT_BUNDLE_SOURCE_FILES}
    if not touched:
        return ()
    rendered = ", ".join(sorted(touched))
    return (
        "Regenerate CONTEXT.md after this merge batch because context bundle "
        f"sources changed: {rendered}. Run python3 scripts/generate_context_bundle.py "
        "after merge on main; task PR branches need not commit regenerated CONTEXT.md.",
    )


def public_state_doc_followups(
    changed_files: tuple[str, ...],
    task_payload: dict[str, Any],
) -> tuple[str, ...]:
    """Return closeout reminders for docs/status and Mission Control drift."""
    if not _public_state_docs_need_review(changed_files, task_payload):
        return ()

    changed = set(changed_files)
    missing_reviews = tuple(path for path in PUBLIC_STATE_DOCS if path not in changed)
    return render_public_state_doc_checklist(missing_reviews)


def _public_state_docs_need_review(
    changed_files: tuple[str, ...],
    task_payload: dict[str, Any],
) -> bool:
    if any(path.startswith(PUBLIC_STATE_DOC_TRIGGER_PREFIXES) for path in changed_files):
        return True
    if any(path in PUBLIC_STATE_DOC_TRIGGER_FILES for path in changed_files):
        return True

    parts: list[str] = [
        str(task_payload.get("id", "")),
        str(task_payload.get("title", "")),
        str(task_payload.get("type", "")),
    ]
    task_input = task_payload.get("input", {})
    if isinstance(task_input, dict):
        parts.append(str(task_input.get("related_domain", "")))
        parts.append(str(task_input.get("planning_context", "")))
        related_objects = task_input.get("related_objects", [])
        if isinstance(related_objects, list):
            parts.extend(str(item) for item in related_objects)
    for key in ("strategy_alignment", "requirements", "accepted_outputs"):
        items = task_payload.get(key, [])
        if isinstance(items, list):
            parts.extend(str(item) for item in items)

    haystack = " ".join(parts).lower()
    return any(marker in haystack for marker in PUBLIC_STATE_TASK_MARKERS)


def load_yaml_payload_from_ref(root: Path, ref: str, repo_path: str) -> dict[str, Any] | None:
    """Load a YAML mapping from a git ref, or from the worktree for the current branch."""
    result = run_git_command(["show", f"{ref}:{repo_path}"], cwd=root, timeout=30)
    text: str | None = result.stdout if result.returncode == 0 else None
    if text is None and ref == current_branch(root):
        path = root / repo_path
        if path.exists():
            text = path.read_text(encoding="utf-8")
    if text is None:
        return None
    payload = yaml.safe_load(text)
    return payload if isinstance(payload, dict) else None


def output_routing_value(body: str, field: str) -> str | None:
    """Return a value from the PR Output Routing section."""
    prefix = f"- {field}:"
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith(prefix):
            continue
        value = stripped.split(":", 1)[1].strip()
        return value.strip("`").strip() or None
    return None


def classify_artifact_review_changes(
    root: Path,
    *,
    target_branch: str,
    base_ref: str,
    changed_files: tuple[str, ...],
) -> tuple[ArtifactReviewSignal, ...]:
    """Classify changed scientific-memory artifacts for maintainer review."""
    signals: list[ArtifactReviewSignal] = []
    for path in changed_files:
        if path.startswith("results/") and path.endswith("/result.yaml"):
            payload = load_yaml_payload_from_ref(root, target_branch, path)
            review_tier = payload.get("review_tier") if isinstance(payload, dict) else None
            signals.append(
                ArtifactReviewSignal(
                    path=path,
                    artifact_class="result_publication",
                    review_tier=str(review_tier) if review_tier else None,
                )
            )
            continue
        if (
            path.startswith("prediction_registry/")
            and path.endswith(".yaml")
            and Path(path).name.startswith("PRED-")
        ):
            payload = load_yaml_payload_from_ref(root, target_branch, path)
            review_tier = payload.get("review_tier") if isinstance(payload, dict) else None
            signals.append(
                ArtifactReviewSignal(
                    path=path,
                    artifact_class="prediction_publication",
                    review_tier=str(review_tier) if review_tier else None,
                )
            )
            continue
        if path.startswith("claims/") and path.endswith(".md"):
            before = load_claim_status_from_ref(root, base_ref, path)
            after = load_claim_status_from_ref(root, target_branch, path)
            if before is None and after == "DRAFT":
                artifact_class = "draft_claim_authoring"
            elif before != after:
                artifact_class = "claim_status_transition"
            else:
                artifact_class = "claim_text_update"
            signals.append(
                ArtifactReviewSignal(
                    path=path,
                    artifact_class=artifact_class,
                    before_status=before,
                    after_status=after,
                )
            )
            continue
        if (
            path.startswith("knowledge/")
            and path.endswith((".md", ".yaml", ".yml"))
            and Path(path).name.startswith("KNOW-")
        ):
            payload = load_yaml_payload_from_ref(root, target_branch, path)
            review_tier = payload.get("review_tier") if isinstance(payload, dict) else None
            signals.append(
                ArtifactReviewSignal(
                    path=path,
                    artifact_class="knowledge_phase1_maintainer_only",
                    review_tier=str(review_tier) if review_tier else None,
                )
            )
    return tuple(signals)


def render_artifact_review_signal(signal: ArtifactReviewSignal) -> str:
    """Render a compact artifact-class signal for review output."""
    details: list[str] = [signal.path, signal.artifact_class]
    if signal.review_tier:
        details.append(f"review_tier={signal.review_tier}")
    if signal.before_status != signal.after_status:
        details.append(f"status={signal.before_status or 'new'}->{signal.after_status or 'missing'}")
    return " ".join(details)


def _explicit_output_routing(value: str | None) -> bool:
    if value is None:
        return False
    normalized = value.strip().strip("`").lower()
    return normalized not in {"", "none", "n/a", "not_applicable", "not applicable"}


def _agent_tier_pr_body_issues(
    signal: ArtifactReviewSignal,
    body: str,
) -> tuple[str, ...]:
    required: list[str] = []
    review_tier_value = output_routing_value(body, "Review tier")
    if signal.review_tier not in (review_tier_value or ""):
        required.append(
            f"{signal.path} sets review_tier {signal.review_tier}; PR Output Routing must repeat that tier explicitly."
        )
    gate_field = "Gate A status" if signal.review_tier == "AGENT_PUBLISHED" else "Gate B status"
    if not _explicit_output_routing(output_routing_value(body, gate_field)):
        required.append(
            f"{signal.path} sets {signal.review_tier}; PR Output Routing must include an explicit {gate_field}."
        )
    return tuple(required)


def diff_base_ref(root: Path, pr_metadata: PullRequestMetadata | None) -> str:
    """Return the best available diff base ref for PR review."""
    base_branch = pr_metadata.base_branch if pr_metadata is not None else "main"
    remote_base = f"origin/{base_branch}"
    if branch_exists(root, remote_base):
        return remote_base
    return base_branch


def build_review_report(
    root: Path,
    *,
    pull_request: int | None = None,
    branch: str | None = None,
    task_id: str | None = None,
    validation_mode: str = "strict",
) -> ReviewReport:
    """Build a maintainer review verdict, self-cleaning any review worktree.

    Thin wrapper around :func:`_compose_review_report` that adds the two
    review-worktree lifecycle guards from TASK-0724:

    - **Backstop janitor (Layer 2):** before reviewing, reclaim *abandoned*
      detached review worktrees older than the TTL so crashed earlier runs
      self-heal. Best-effort; never blocks the review.
    - **Self-cleanup (Layer 1):** in a ``finally``, tear down only the worktree
      this run created, on every exit path (success or exception). Removal is
      branch-safety checked, so a parallel agent's active worktree is never
      touched.
    """
    repo_root = root
    try:
        gc_review_worktrees(repo_root, older_than_hours=DEFAULT_GC_AGE_HOURS)
    except Exception:
        # Cleanup must never break a review run; the GC is a backstop, not a gate.
        pass
    created_worktrees: list[Path] = []
    try:
        return _compose_review_report(
            root,
            pull_request=pull_request,
            branch=branch,
            task_id=task_id,
            validation_mode=validation_mode,
            worktree_sink=created_worktrees,
        )
    finally:
        for worktree_path in created_worktrees:
            try:
                teardown_own_worktree(repo_root, worktree_path)
            except Exception:
                pass


def _compose_review_report(
    root: Path,
    *,
    pull_request: int | None = None,
    branch: str | None = None,
    task_id: str | None = None,
    validation_mode: str = "strict",
    worktree_sink: list[Path] | None = None,
) -> ReviewReport:
    """Build a maintainer review verdict for the current or provided branch."""
    if validation_mode not in {"strict", "ci-aware"}:
        raise ValueError(f"Unsupported validation mode: {validation_mode}")
    pr_metadata = load_pr_metadata(root, pull_request) if pull_request is not None else None
    if pull_request is not None and pr_metadata is None and branch is None:
        return ReviewReport(
            verdict="BLOCKED",
            risk="high",
            task_id=task_id or "TASK-UNKNOWN",
            branch=f"PR-{pull_request}-UNRESOLVED",
            changed_files=(),
            validation="not_run",
            security_risks=(),
            blockers=(
                "Could not load PR metadata via gh CLI, so the helper cannot "
                "prove which PR head to review. It intentionally did not review "
                "the current checkout. Fallback commands: "
                f"gh pr view {pull_request} --json headRefName,headRefOid,baseRefName ; "
                f"git fetch origin pull/{pull_request}/head:refs/remotes/origin/pr-{pull_request} ; "
                f"python3 scripts/apl_review_pr.py --branch origin/pr-{pull_request} --task <TASK-XXXX>.",
            ),
            required_fixes=(),
            recommended_action="Do not merge. Re-run review against a verified PR head ref.",
            advisory_warnings=(),
        )
    clean_pr_worktree: CleanPrWorktree | None = None
    current = current_branch(root)
    needs_clean_pr_worktree = (
        pull_request is not None
        and branch is None
        and pr_metadata is not None
        and bool(pr_metadata.head_sha)
        and (current != pr_metadata.branch or not git_status_clean(root))
    )
    if needs_clean_pr_worktree:
        clean_pr_worktree = prepare_clean_pr_worktree(root, pr_metadata)
        if clean_pr_worktree.ready:
            root = clean_pr_worktree.root
            branch = pr_metadata.branch
            current = current_branch(root)
    requested_local_pr_ref_review = bool(
        branch is not None
        and LOCAL_PR_REF_PATTERN.match(branch) is not None
        and task_id is not None
    )
    if (
        clean_pr_worktree is None
        and requested_local_pr_ref_review
        and (current != branch or not git_status_clean(root))
    ):
        clean_pr_worktree = prepare_clean_local_ref_worktree(root, branch)
        if clean_pr_worktree.ready:
            root = clean_pr_worktree.root
            current = current_branch(root)
    if (
        worktree_sink is not None
        and clean_pr_worktree is not None
        and clean_pr_worktree.ready
    ):
        # Hand the disposable worktree this run created to the caller's finally
        # so it is torn down on every exit path (Layer 1 self-cleanup).
        worktree_sink.append(clean_pr_worktree.root)
    target_branch = branch or (pr_metadata.branch if pr_metadata is not None else current)
    review_ref = clean_pr_worktree.review_ref if clean_pr_worktree and clean_pr_worktree.ready else target_branch
    base_ref = diff_base_ref(root, pr_metadata)
    local_pr_ref_review = requested_local_pr_ref_review
    blockers: list[str] = []
    required_fixes: list[str] = []
    security_risks: list[str] = []
    advisory_warnings: list[str] = []
    reviewing_clean_pr_worktree = bool(clean_pr_worktree and clean_pr_worktree.ready)
    review_worktree_is_current = reviewing_clean_pr_worktree or target_branch == current

    if pull_request is not None and pr_metadata is None:
        blockers.append(
            "Could not load PR metadata via gh CLI, so the helper could not "
            "prepare a clean remote PR review worktree. Fallback commands: "
            f"gh pr view {pull_request} --json headRefName,headRefOid,baseRefName ; "
            f"git fetch origin pull/{pull_request}/head:refs/remotes/origin/pr-{pull_request} ; "
            f"python3 scripts/apl_review_pr.py --branch <local-pr-branch>."
        )
    if clean_pr_worktree is not None:
        if clean_pr_worktree.ready:
            advisory_warnings.append(clean_pr_worktree.message)
        else:
            blockers.append(
                "Could not prepare clean remote PR review worktree: "
                + clean_pr_worktree.message
                + " Fallback commands: "
                + " ; ".join(clean_pr_worktree.fallback_commands)
                + "."
            )

    if target_branch == "main":
        blockers.append("Branch is main. PR review must target a task branch, not main.")

    protocol = classify_review_protocol(
        target_branch,
        pr_title=pr_metadata.title if pr_metadata is not None else None,
    )
    is_proposal_review = protocol.kind == "proposal"
    is_closeout_review = protocol.kind == "closeout"
    is_task_queue_review = protocol.kind == "task_queue"
    is_microtask_review = protocol.kind == "microtask"
    if local_pr_ref_review:
        advisory_warnings.append(
            "Review target is a fetched local PR ref, not the contributor's "
            "canonical branch name. This is allowed only because an explicit "
            "task id was supplied; prefer --pr <number> when GitHub metadata is available."
        )
    if not protocol.is_supported and not local_pr_ref_review:
        blockers.append(
            "Branch does not follow a canonical task, task-proposal, task-queue, closeout, or microtask branch format."
        )
    elif (
        not local_pr_ref_review
        and not reviewing_clean_pr_worktree
        and not local_branch_exists(root, target_branch)
    ):
        blockers.append(
            f"Local branch {target_branch} is not available. Checkout the PR branch locally first."
        )
    changed_files = changed_files_vs_main(root, review_ref, base_ref=base_ref)
    if not changed_files:
        blockers.append("Diff vs main is empty. There is no reviewable task change.")

    artifact_signals = classify_artifact_review_changes(
        root,
        target_branch=review_ref,
        base_ref=base_ref,
        changed_files=changed_files,
    )
    if artifact_signals:
        advisory_warnings.append(
            "Artifact review classes: "
            + "; ".join(render_artifact_review_signal(signal) for signal in artifact_signals)
            + "."
        )

    branch_task = protocol.branch_task_id
    branch_microtask = protocol.microtask_id
    branch_microtask_queue = protocol.microtask_queue_id
    task_payload: dict[str, Any] | None = None
    validation_payload: dict[str, Any] = {}
    if is_proposal_review:
        resolved_task_id = "TASK-PROPOSAL"
        proposal_triage_review = body_requests_proposal_triage(
            pr_metadata.body if pr_metadata is not None else None
        )
        proposal_files = changed_task_proposal_files(changed_files)
        if len(proposal_files) == 0:
            blockers.append("Task proposal review requires at least one changed tasks/proposals/*.yaml file.")
        elif len(proposal_files) == 1:
            proposal_path = root / proposal_files[0]
            task_payload = load_task_proposal(proposal_path)
            proposal_status = str(task_payload["status"])
            if proposal_status != "PROPOSED" and not (
                proposal_triage_review and proposal_status in {"REJECTED", "SUPERSEDED"}
            ):
                required_fixes.append(
                    f"Task proposal status is {proposal_status}. Keep it PROPOSED while requesting "
                    "acceptance, or use an explicit proposal-triage PR body when closing a stale "
                    "proposal as REJECTED or SUPERSEDED."
                )
        else:
            # Multiple proposals in one PR is allowed — validate each one individually.
            for pf in proposal_files:
                payload = load_task_proposal(root / pf)
                proposal_status = str(payload["status"])
                if proposal_status != "PROPOSED" and not (
                    proposal_triage_review and proposal_status in {"REJECTED", "SUPERSEDED"}
                ):
                    required_fixes.append(
                        f"Proposal {pf} status is {proposal_status}. Keep it PROPOSED while requesting "
                        "acceptance, or use an explicit proposal-triage PR body when closing a stale "
                        "proposal as REJECTED or SUPERSEDED."
                    )
        if proposal_files:
            validation_payload = {
                "validation": {"commands": list(TASK_PROPOSAL_VALIDATION_COMMANDS)}
            }
        canonical_task_files = tuple(
            path
            for path in changed_files
            if path.startswith("tasks/TASK-") and path.endswith(".yaml")
        )
        if canonical_task_files:
            blockers.append(
                "Task proposal PR must not create or edit canonical task files: "
                + ", ".join(canonical_task_files)
                + "."
            )
        task_view_changes = tuple(
            path for path in changed_files if path.startswith("docs/task-views/")
        )
        if task_view_changes:
            required_fixes.append(
                "Task proposal PR should not update generated task views before maintainer acceptance."
            )
    elif is_closeout_review:
        resolved_task_id = "TASK-CLOSEOUT"
        closeout_task_files = tuple(
            path
            for path in changed_files
            if path.startswith("tasks/TASK-") and path.endswith(".yaml")
        )
        if not closeout_task_files:
            blockers.append("Closeout PR requires at least one changed canonical task file.")
        elif review_worktree_is_current:
            for task_path in closeout_task_files:
                payload = load_task(root / task_path)
                if str(payload["status"]) in {"DONE", "READY", "REJECTED", "SUPERSEDED"}:
                    continue
                required_fixes.append(
                    f"Closeout PR should mark {task_path} as DONE, READY, REJECTED, or SUPERSEDED."
                )
        validation_payload = {
            "validation": {
                "commands": list(CLOSEOUT_VALIDATION_COMMANDS),
            }
        }
    elif is_task_queue_review:
        resolved_task_id = "TASK-QUEUE"
        if protocol.task_queue_slug is None:
            required_fixes.append(
                "TASK-QUEUE PR branch should follow agent/<contributor-id>/<agent-id>/task-queue-<short-slug>."
            )
        queue_task_files = tuple(
            path
            for path in changed_files
            if path.startswith("tasks/TASK-") and path.endswith(".yaml")
        )
        if not queue_task_files:
            blockers.append("TASK-QUEUE PR requires at least one changed canonical task file.")
        for task_path in queue_task_files:
            try:
                payload = load_task(root / task_path)
            except (FileNotFoundError, ValueError) as exc:
                blockers.append(str(exc))
                continue
            status = str(payload["status"])
            if status not in TASK_QUEUE_ALLOWED_STATUSES:
                required_fixes.append(
                    f"TASK-QUEUE PR should leave {task_path} in PROPOSED, READY, or BLOCKED; found {status}."
                )
        generated_navigation_changes = tuple(
            path
            for path in changed_files
            if path.startswith("docs/task-views/")
        )
        if generated_navigation_changes:
            advisory_warnings.append(
                "TASK-QUEUE PR includes generated task navigation; this is allowed, "
                "but the post-merge Sync Active Board action normally regenerates "
                "docs/task-views/*.md on main."
            )
        forbidden_paths = tuple(
            path
            for path in changed_files
            if path.startswith(TASK_QUEUE_FORBIDDEN_PREFIXES)
        )
        if forbidden_paths:
            blockers.append(
                "TASK-QUEUE PR must not change canonical scientific artifacts: "
                + ", ".join(forbidden_paths)
                + "."
            )
        validation_payload = {
            "validation": {
                "commands": list(TASK_QUEUE_VALIDATION_COMMANDS),
            }
        }
    elif is_microtask_review:
        queue_id = protocol.title_microtask_queue_id
        resolved_task_id = (
            f"MICROTASK({queue_id})" if queue_id is not None else "MICROTASK"
        )
        if queue_id is None:
            required_fixes.append(
                "Microtask PR title must follow microtask(<queue-id>): ... format."
            )
        else:
            try:
                resolve_microtask_queue_file(root, queue_id)
            except (FileNotFoundError, ValueError) as exc:
                blockers.append(str(exc))
        if branch_microtask is None and branch_microtask_queue is None:
            required_fixes.append(
                "Microtask PR branch should follow agent/<contributor-id>/<agent-id>/microtask-<microtask-id>-<short-slug> or agent/<contributor-id>/<agent-id>/microtask-batch-<queue-id>--<short-slug>."
            )
        if (
            queue_id is not None
            and branch_microtask_queue is not None
            and branch_microtask_queue != queue_id
        ):
            blockers.append(
                f"Microtask batch branch queue id {branch_microtask_queue} does not match PR title queue id {queue_id}."
            )
        validation_payload = {
            "validation": {
                "commands": list(MICROTASK_VALIDATION_COMMANDS),
            }
        }
    else:
        resolved_task_id = task_id or branch_task
        if resolved_task_id is None:
            blockers.append("Task id could not be inferred from the branch and was not provided.")
            resolved_task_id = "TASK-UNKNOWN"
        elif branch_task is not None and task_id is not None and branch_task != task_id:
            blockers.append(
                f"Explicit task id {task_id} does not match branch task id {branch_task}."
            )

    looks_like_task_queue_pr = False
    if (
        not is_proposal_review
        and not is_closeout_review
        and not is_task_queue_review
        and not is_microtask_review
        and resolved_task_id != "TASK-UNKNOWN"
    ):
        queue_like_task_files = tuple(
            path
            for path in changed_files
            if path.startswith("tasks/TASK-") and path.endswith(".yaml")
        )
        queue_like_non_task_files = tuple(
            path
            for path in changed_files
            if path not in queue_like_task_files
            and not path.startswith("docs/task-views/")
            and path != "tasks/ACTIVE.md"
        )
        queue_like_statuses: list[str] = []
        if queue_like_task_files and not queue_like_non_task_files:
            for task_path in queue_like_task_files:
                try:
                    payload = load_task(root / task_path)
                except (FileNotFoundError, ValueError):
                    queue_like_statuses = []
                    break
                queue_like_statuses.append(str(payload["status"]))
            looks_like_task_queue_pr = bool(queue_like_statuses) and all(
                status in TASK_QUEUE_ALLOWED_STATUSES
                for status in queue_like_statuses
            )
        if looks_like_task_queue_pr:
            required_fixes.append(
                "This PR only adds or updates future task files in "
                "PROPOSED, READY, or BLOCKED. Use TASK-QUEUE title, "
                "agent/<contributor-id>/<agent-id>/task-queue-<short-slug> "
                "branch naming, and TASK-QUEUE metadata instead of marking "
                "queued future tasks REVIEW_READY."
            )
            task_file = None
        else:
            try:
                task_file = resolve_task_file(root, resolved_task_id)
                task_payload = load_task(task_file)
            except (FileNotFoundError, ValueError) as exc:
                blockers.append(str(exc))
                task_file = None
        if (
            not looks_like_task_queue_pr
            and task_payload is not None
            and str(task_payload["status"]) != "REVIEW_READY"
        ):
            required_fixes.append(
                f"Task status is {task_payload['status']}. Set it to REVIEW_READY before merge."
            )
    else:
        task_file = None

    closeout_ci_pass = bool(
        is_closeout_review and pr_metadata is not None and pr_metadata.status_checks_passed is True
    )

    if review_worktree_is_current and not git_status_clean(root):
        required_fixes.append("Git status is not clean on the review branch.")
    elif not review_worktree_is_current and not closeout_ci_pass:
        required_fixes.append(
            "Switch to the PR branch locally to verify clean git status and run validations."
        )

    if pr_metadata is not None:
        title_policy = validate_pr_title(
            review_kind=protocol.kind,
            title=pr_metadata.title,
            resolved_task_id=resolved_task_id,
        )
        blockers.extend(title_policy.blockers)
        required_fixes.extend(title_policy.required_fixes)
        if pr_metadata.branch and pr_metadata.branch != target_branch:
            blockers.append(
                f"PR branch {pr_metadata.branch} does not match reviewed branch {target_branch}."
            )
        missing_sections = missing_pr_template_sections(pr_metadata.body)
        if missing_sections:
            required_fixes.append(
                "PR body is missing required repository-template sections: "
                + ", ".join(missing_sections)
                + ". Use .github/pull_request_template.md or a filled --body-file before requesting review."
            )
        missing_fields = missing_pr_metadata_fields(pr_metadata.body)
        if missing_fields:
            required_fixes.append(
                "PR metadata is incomplete: " + ", ".join(missing_fields) + "."
            )
        agent_tool_mismatch = agent_tool_metadata_mismatch(target_branch, pr_metadata.body)
        if agent_tool_mismatch is not None:
            required_fixes.append(agent_tool_mismatch)
        for signal in artifact_signals:
            if signal.review_tier in AGENT_PUBLICATION_TIERS:
                required_fixes.extend(
                    _agent_tier_pr_body_issues(signal, pr_metadata.body)
                )
        if pr_metadata.status_checks_passed is False:
            blockers.append("GitHub status checks are failing.")
        elif pr_metadata.status_checks_pending:
            required_fixes.append("GitHub status checks are still pending.")
    elif pull_request is None:
        advisory_warnings.append(
            "Branch-only review cannot validate the GitHub PR body/template. "
            "After opening the PR, run python3 scripts/apl_review_pr.py --pr <number> before merge."
        )

    if task_payload is not None and not is_closeout_review:
        missing_outputs = missing_expected_outputs(
            root,
            review_ref,
            task_payload,
            changed_files,
        )
        if missing_outputs:
            required_fixes.append(
                "Accepted outputs appear to be missing: " + ", ".join(missing_outputs) + "."
            )
        unexpected_paths = unexpected_protected_changes(changed_files, task_payload)
        if unexpected_paths:
            blockers.append(
                "Unexpected protected artifact changes: "
                + ", ".join(unexpected_paths)
                + "."
            )
        promotions = claim_status_promotions(root, review_ref, changed_files)
        if promotions:
            blockers.append("Claim status promotion detected: " + ", ".join(promotions) + ".")

    for signal in artifact_signals:
        if signal.artifact_class == "knowledge_phase1_maintainer_only":
            blockers.append(
                f"KNOW-* changes are maintainer-only in Phase 1: {signal.path}."
            )
        if signal.artifact_class == "claim_status_transition":
            advisory_warnings.append(
                f"Claim status transition detected for {signal.path}; Phase 1 transitions require maintainer judgment."
            )
        if signal.review_tier == "AGENT_PUBLISHED":
            payload = load_yaml_payload_from_ref(root, review_ref, signal.path)
            if payload is None:
                blockers.append(f"Could not load {signal.path} for Gate A classification.")
                continue
            gate_report = check_payload(payload, artifact_path=signal.path, root=root)
            if gate_report.ok:
                advisory_warnings.append(f"Gate A checker passed for {signal.path}.")
            else:
                blockers.append(
                    f"Gate A checker failed for {signal.path}: "
                    + ", ".join(issue.code for issue in gate_report.issues)
                    + "."
                )
        elif signal.review_tier == "AGENT_VALIDATED":
            advisory_warnings.append(
                f"{signal.path} is AGENT_VALIDATED; Gate B replay helper is not yet wired, so inspect replay metadata manually."
            )

    overclaim_lines = tuple(
        parse_added_lines(
            run_git_command(
                ["diff", "--unified=0", f"{base_ref}...{review_ref}"],
                cwd=root,
                timeout=120,
            ).stdout,
            exclude_prefixes=("tests/",),
        )
    )
    if review_worktree_is_current and not git_status_clean(root):
        overclaim_lines = overclaim_lines + parse_added_lines(
            run_git_command(["diff", "--unified=0"], cwd=root, timeout=120).stdout,
            exclude_prefixes=("tests/",),
        )
    overclaims = overclaim_hits(overclaim_lines)
    if overclaims:
        blockers.append("Overclaim language detected: " + ", ".join(overclaims) + ".")
    overclaim_advisories = overclaim_advisory_hits(overclaim_lines)
    if overclaim_advisories:
        advisory_warnings.append(
            "Overclaim terms appear only in guardrail or policy context: "
            + ", ".join(overclaim_advisories)
            + "."
        )
    decision_regressions = decision_regression_advisory_hits(overclaim_lines)
    if decision_regressions:
        confirmation_markers = (
            "maintainer confirmation: architecture tradeoff accepted",
            "maintainer confirmation: decision-regression accepted",
            "architecture regression accepted",
        )
        confirmation_text = (pr_metadata.body if pr_metadata is not None else "").lower()
        message = (
            "Potential architecture decision regression: "
            + " ".join(decision_regressions)
            + " If intentional, add explicit maintainer confirmation before merge."
        )
        if any(marker in confirmation_text for marker in confirmation_markers):
            advisory_warnings.append(message)
        else:
            required_fixes.append(message)
    follow_up_task_advisories = follow_up_task_advisory_hits(
        overclaim_lines,
        changed_files,
        pr_title=pr_metadata.title if pr_metadata is not None else "",
        pr_body=pr_metadata.body if pr_metadata is not None else "",
    )
    advisory_warnings.extend(follow_up_task_advisories)
    security_lines = tuple(
        parse_added_lines(
            run_git_command(
                ["diff", "--unified=0", f"{base_ref}...{review_ref}"],
                cwd=root,
                timeout=120,
            ).stdout,
            include_prefixes=("physics_lab/", "scripts/", ".github/workflows/"),
        )
    )
    if review_worktree_is_current and not git_status_clean(root):
        security_lines = security_lines + parse_added_lines(
            run_git_command(["diff", "--unified=0"], cwd=root, timeout=120).stdout,
            include_prefixes=("physics_lab/", "scripts/", ".github/workflows/"),
        )
    dangerous_patterns = security_pattern_hits(security_lines)
    if dangerous_patterns:
        security_risks.extend(dangerous_patterns)
        blockers.append(
            "Dangerous code patterns detected: " + ", ".join(dangerous_patterns) + "."
        )
    security_risks.extend(sensitive_surface_hits(changed_files))

    cross_platform_advisories = cross_platform_advisory_hits(security_lines)
    if cross_platform_advisories:
        advisory_warnings.append(
            "Cross-platform portability review (advisory): "
            + " ".join(cross_platform_advisories)
        )
    advisory_warnings.extend(cross_platform_surface_hits(changed_files))
    pr_body_lines = tuple(pr_metadata.body.splitlines()) if pr_metadata is not None else ()
    coauthor_advisories = coauthor_trailer_advisory_hits(overclaim_lines + pr_body_lines)
    advisory_warnings.extend(coauthor_advisories)

    bundle_path, bundle_status = ensure_review_bundle(
        root,
        target_branch,
        can_generate=target_branch == current and target_branch != "main",
    )
    if bundle_status == "missing" and reviewing_clean_pr_worktree:
        advisory_warnings.append(
            "Review bundle generation was skipped for clean remote PR worktree review."
        )
    elif bundle_status == "missing" and not closeout_ci_pass:
        required_fixes.append("Review bundle is missing and could not be generated.")
    elif bundle_status == "invalid":
        blockers.append(
            "Review bundle exists but was generated from the wrong branch, not the PR branch."
        )

    validation = run_task_validation(
        root,
        validation_payload or task_payload or {},
        enabled=bool(validation_payload or task_payload)
        and review_worktree_is_current
        and git_status_clean(root),
        skip_commands_containing=("scripts/apl_review_pr.py",),
        ci_aware=bool(
            validation_mode == "ci-aware"
            and pr_metadata is not None
            and pr_metadata.status_checks_passed is True
        ),
    )
    if validation_mode == "ci-aware" and validation.skipped_commands:
        executed = ", ".join(validation.executed_commands) or "no local-only commands"
        advisory_warnings.append(
            "CI-aware validation reused already-green GitHub checks for duplicated "
            "commands and ran local remainder: "
            + executed
            + "."
        )
    if validation.status == "fail":
        blockers.append(
            "Validation commands failed: " + ", ".join(validation.failed_commands) + "."
        )
    elif validation.status == "not_run" and not closeout_ci_pass:
        required_fixes.append("Validation commands were not executed during this review run.")

    if blockers:
        verdict = "BLOCKED"
        risk = "high"
        recommended_action = "Do not merge. Return the blockers to the developer."
    elif required_fixes:
        verdict = "NEEDS_CHANGES"
        risk = "medium"
        recommended_action = "Request changes and re-run the maintainer review."
    elif security_risks:
        verdict = "MERGE_OK"
        risk = "medium"
        recommended_action = (
            "Merge after GitHub CI is green and the maintainer accepts the listed "
            "security-sensitive changes."
        )
    else:
        verdict = "MERGE_OK"
        risk = "low"
        recommended_action = "Merge after GitHub CI is green."

    if bundle_path is not None and bundle_status == "generated":
        required_fixes = [
            item for item in required_fixes if item != "Review bundle is missing and could not be generated."
        ]

    return ReviewReport(
        verdict=verdict,
        risk=risk,
        task_id=resolved_task_id,
        branch=target_branch,
        changed_files=changed_files,
        validation=validation.status,
        security_risks=tuple(dict.fromkeys(security_risks)),
        blockers=tuple(blockers),
        required_fixes=tuple(required_fixes),
        recommended_action=recommended_action,
        advisory_warnings=tuple(advisory_warnings),
    )


def render_review_report(report: ReviewReport) -> str:
    """Render a stable PR review report."""
    quality_score, quality_notes = review_quality_score(report)
    lines = [
        f"Verdict: {report.verdict}",
        f"Quality: {quality_score}/10",
        f"Risk: {report.risk}",
        f"Task: {report.task_id}",
        f"Branch: {report.branch}",
        "Changed files:",
    ]
    if report.changed_files:
        lines.extend(f"- {path}" for path in report.changed_files)
    else:
        lines.append("- none")
    lines.append(f"Validation: {report.validation}")
    lines.append("Security risks:")
    if report.security_risks:
        lines.extend(f"- {item}" for item in report.security_risks)
    else:
        lines.append("- none")
    lines.append("Advisory warnings:")
    if report.advisory_warnings:
        lines.extend(f"- {item}" for item in report.advisory_warnings)
    else:
        lines.append("- none")
    lines.append("Blockers:")
    if report.blockers:
        lines.extend(f"- {item}" for item in report.blockers)
    else:
        lines.append("- none")
    lines.append("Required fixes:")
    if report.required_fixes:
        lines.extend(f"- {item}" for item in report.required_fixes)
    else:
        lines.append("- none")
    lines.append("Quality notes:")
    if quality_notes:
        lines.extend(f"- {item}" for item in quality_notes)
    else:
        lines.append("- clean low-risk review surface")
    lines.append("Recommended action:")
    lines.append(f"- {report.recommended_action}")
    return "\n".join(lines)


def review_quality_score(report: ReviewReport) -> tuple[int, tuple[str, ...]]:
    """Return an advisory human triage score for a review report.

    The score is deliberately not part of verdict calculation. It only makes
    review output easier to compare across many open PRs.
    """
    score = 10
    notes: list[str] = []

    if report.blockers:
        score -= 4
        notes.append("blockers remain")
    if report.required_fixes:
        score -= 2
        notes.append("required fixes remain")
    if report.risk == "high":
        score -= 2
        notes.append("high-risk change surface")
    elif report.risk == "medium":
        score -= 1
        notes.append("medium-risk change surface")
    if report.security_risks:
        score -= 1
        notes.append("security-sensitive paths need maintainer attention")
    if report.advisory_warnings:
        score -= 1
        notes.append("advisory warnings need context check")

    if report.verdict != "MERGE_OK" and "verdict is not MERGE_OK" not in notes:
        score -= 1
        notes.append("verdict is not MERGE_OK")

    bounded_score = max(1, min(10, score))
    return bounded_score, tuple(dict.fromkeys(notes))


def update_task_status(task_file: Path, new_status: str) -> None:
    """Set the status field in a task YAML file."""
    text = task_file.read_text(encoding="utf-8")
    updated_text, count = re.subn(
        r"^status:\s+.+$",
        f"status: {new_status}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError(f"Could not update status in {task_file}")
    task_file.write_text(updated_text, encoding="utf-8")


def update_active_board_for_done(root: Path, task_id: str, task_title: str) -> None:
    """Refresh generated task navigation (docs/task-views/*.md) after DONE."""
    del task_id, task_title
    sync_generated_task_state(root)


def should_append_dry_run_entry(task_payload: dict[str, Any]) -> bool:
    """Return whether a merged task should be recorded in multi-agent dry run notes."""
    related_objects = [str(item).lower() for item in task_payload.get("input", {}).get("related_objects", [])]
    planning_context = str(task_payload.get("input", {}).get("planning_context", "")).lower()
    task_type = str(task_payload.get("type", "")).lower()
    if any("multi-agent-dry-run" in item or "task-0012" in item for item in related_objects):
        return True
    if any(keyword in planning_context for keyword in DRY_RUN_KEYWORDS):
        return True
    return task_type in {"contributor_pilot", "agent_workflow"}


def append_dry_run_entry(root: Path, task_id: str, pull_request: int) -> bool:
    """Append a minimal dry-run closeout entry if the task is not already recorded."""
    doc_path = root / "docs" / "multi-agent-dry-run.md"
    text = doc_path.read_text(encoding="utf-8")
    if task_id in text:
        return False
    run_numbers = [int(match.group("number")) for match in RUN_ENTRY_PATTERN.finditer(text)]
    next_run = max(run_numbers, default=0) + 1
    entry = "\n".join(
        [
            "",
            f"## Run #{next_run}",
            "",
            f"- Date: `{date.today().isoformat()}`",
            f"- Task: `{task_id}`",
            f"- Pull request: `#{pull_request}`",
            "- Scope: maintainer closeout entry for a merged contributor or workflow task",
            "",
            "### Outcome",
            "",
            "- the merged PR was reviewed and closed out on `main`;",
            "- the task moved from `REVIEW_READY` to `DONE`.",
            "",
            "### Limitations",
            "",
            "- this note is a short maintainer closeout summary only;",
            "- detailed review discussion remains in the PR thread.",
            "",
        ]
    )
    doc_path.write_text(text.rstrip() + "\n" + entry, encoding="utf-8")
    return True


def build_closeout_report(
    root: Path,
    *,
    task_id: str,
    pull_request: int,
    apply: bool,
    sync_board: bool = False,
    pr_metadata: PullRequestMetadata | None = None,
) -> CloseoutReport:
    """Build and optionally apply a maintainer closeout decision on main."""
    blockers: list[str] = []
    required_actions: list[str] = []
    suggested_actions: list[str] = []
    applied_changes: list[str] = []
    branch = current_branch(root)

    if branch != "main":
        blockers.append("Current branch is not main. Closeout must run on main after merge.")
    if not git_status_clean(root):
        blockers.append("Git status is not clean before closeout.")

    pr_metadata = pr_metadata or load_pr_metadata(root, pull_request)
    merged = "unknown"
    ci_status = "unknown"
    changed_files: tuple[str, ...] = ()
    if pr_metadata is None:
        required_actions.append("Could not verify PR metadata via gh CLI.")
    else:
        changed_files = pr_metadata.changed_files
        merged = "yes" if pr_metadata.merged else "no"
        if pr_metadata.status_checks_passed is True:
            ci_status = "pass"
        elif pr_metadata.status_checks_passed is False:
            ci_status = "fail"
            blockers.append("GitHub status checks for the PR are failing.")
        elif pr_metadata.status_checks_pending:
            ci_status = "pending"
            required_actions.append("GitHub status checks are still pending.")
        if not pr_metadata.merged:
            blockers.append("PR is not merged.")

    suggested_actions.extend(
        context_bundle_followups(
            changed_files,
            sync_board=bool(apply and sync_board),
        )
    )

    task_file = resolve_task_file(root, task_id)
    task_payload = load_task(task_file)
    suggested_actions.extend(public_state_doc_followups(changed_files, task_payload))
    task_status = str(task_payload["status"])
    if task_status != "REVIEW_READY":
        blockers.append(f"Task status is {task_status}, not REVIEW_READY.")

    missing_outputs = missing_expected_outputs(
        root,
        "HEAD",
        task_payload,
        changed_files=(),
    )
    if missing_outputs:
        blockers.append(
            "Accepted outputs are missing in main: " + ", ".join(missing_outputs) + "."
        )
        accepted_outputs_status = "fail"
    else:
        accepted_outputs_status = "pass"

    if blockers:
        outcome = "BLOCKED"
    elif required_actions and not apply:
        outcome = "NEEDS_ATTENTION"
    elif required_actions and apply:
        outcome = "BLOCKED"
        blockers.extend(required_actions)
        required_actions = []
    elif apply:
        outcome = "APPLIED"
    else:
        outcome = "READY_TO_APPLY"

    unblock_candidates = safe_unblock_candidates(root)
    safe_unblocks = tuple(item for item in unblock_candidates if item.safe_to_unblock)
    pending_unblocks = tuple(item for item in unblock_candidates if not item.safe_to_unblock)
    if not apply:
        for item in safe_unblocks:
            suggested_actions.append(
                f"Safe unblock candidate: {item.task_id} can move from BLOCKED to READY; "
                f"all explicit dependencies are DONE ({', '.join(item.dependencies)})."
            )
        for item in pending_unblocks:
            suggested_actions.append(f"Blocked unblock candidate: {item.task_id} — {item.reason}")

    if apply and outcome == "APPLIED":
        update_task_status(task_file, "DONE")
        applied_changes.append(f"Updated {task_file.as_posix()} status to DONE.")
        for item in safe_unblock_candidates(root):
            if not item.safe_to_unblock:
                suggested_actions.append(f"Blocked unblock candidate: {item.task_id} — {item.reason}")
                continue
            update_task_status(item.task_file, "READY")
            applied_changes.append(
                f"Safely unblocked {item.task_file.as_posix()} from BLOCKED to READY "
                f"after explicit dependencies were DONE ({', '.join(item.dependencies)})."
            )
        if sync_board:
            update_active_board_for_done(root, task_id, str(task_payload["title"]))
            applied_changes.append(
                "Synchronized generated task navigation: docs/task-views/*.md."
            )
        else:
            applied_changes.append(
                "Deferred generated task navigation sync; the Sync Active Board "
                "GitHub Action regenerates docs/task-views/*.md on main after the "
                "closeout merges. Run python3 -m physics_lab.cli sync-active-board . "
                "by hand only for explicit audits or when the action is temporarily "
                "disabled."
            )
        if should_append_dry_run_entry(task_payload):
            if append_dry_run_entry(root, task_id, pull_request):
                applied_changes.append("Appended a closeout note to docs/multi-agent-dry-run.md.")
        suggested_actions.append(
            "Closeout publish reminder: do not leave applied closeout changes "
            "only in the local worktree. Review git status/diff, run the required "
            "validation/context refresh, then prepare a closeout commit and PR "
            "or ask the maintainer to do so. Do not push or merge unless the "
            "maintainer explicitly authorizes it."
        )

    return CloseoutReport(
        outcome=outcome,
        task_id=task_id,
        pull_request=pull_request,
        branch=branch,
        task_status=task_status,
        merged=merged,
        accepted_outputs=accepted_outputs_status,
        ci_status=ci_status,
        blockers=tuple(blockers),
        required_actions=tuple(required_actions),
        suggested_actions=tuple(suggested_actions),
        applied_changes=tuple(applied_changes),
    )


def render_closeout_report(report: CloseoutReport) -> str:
    """Render a stable closeout report."""
    lines = [
        f"Closeout: {report.outcome}",
        f"Task: {report.task_id}",
        f"PR: #{report.pull_request}",
        f"Branch: {report.branch}",
        f"Task status: {report.task_status}",
        f"PR merged: {report.merged}",
        f"Accepted outputs in main: {report.accepted_outputs}",
        f"CI: {report.ci_status}",
        "Blockers:",
    ]
    if report.blockers:
        lines.extend(f"- {item}" for item in report.blockers)
    else:
        lines.append("- none")
    lines.append("Required actions:")
    if report.required_actions:
        lines.extend(f"- {item}" for item in report.required_actions)
    else:
        lines.append("- none")
    lines.append("Suggested follow-ups:")
    if report.suggested_actions:
        lines.extend(f"- {item}" for item in report.suggested_actions)
    else:
        lines.append("- none")
    lines.append("Applied changes:")
    if report.applied_changes:
        lines.extend(f"- {item}" for item in report.applied_changes)
    else:
        lines.append("- none")
    return "\n".join(lines)
