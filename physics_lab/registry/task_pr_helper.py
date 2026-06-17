"""Helpers for scaffolding and preflighting canonical task PRs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import unicodedata

from physics_lab.registry.review_policy import (
    BRANCH_PATTERN,
    PR_TITLE_PATTERN,
    agent_tool_metadata_mismatch,
    branch_task_id,
    contributor_metadata_mismatch,
    missing_pr_metadata_fields,
    missing_pr_template_sections,
    normalize_pr_body,
    normalize_contributor_id,
)
from physics_lab.registry.review_git import (
    branch_exists,
    changed_files_vs_main,
    current_branch,
    run_git_command,
)
from physics_lab.registry.task_closeout import find_task_file
from physics_lab.registry.tasks import load_task


DEFAULT_PREPARE_CURRENT_REMOTE_BASES = ("origin/main", "upstream/main")
DEFAULT_PREPARE_CURRENT_LOCAL_BASE = "main"
PLACEHOLDER_MARKERS = (
    "TASK-XXXX",
    "tasks/TASK-XXXX-short-slug.yaml",
    "agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug>",
    "<short title>",
)
STRICT_VALIDATE_REPO_PATTERN = re.compile(
    r'(?:^|[\s`])(?:"[^"]*[\\/]python(?:3)?(?:\.exe)?"|'
    r"(?:\S*[\\/])?(?:python3?|py)(?:\.exe)?)"
    r"\s+-m\s+physics_lab\.cli\s+validate-repo\s+\."
    r"\s+--strict\s+--fail-on-warnings(?:$|[\s`)])",
    re.IGNORECASE,
)
TASK_COMMIT_SUBJECT_PATTERN = re.compile(
    r"^(feat|fix|refactor|docs|test|chore)\(task-(?P<number>[0-9]{4})\): .+"
)


@dataclass(frozen=True)
class TaskPrPreflightReport:
    """Result of checking a canonical task PR branch/title/body triple."""

    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class PreparedTaskPr:
    """Generated PR shape for the current branch."""

    task_id: str
    task_file: Path
    expected_branch: str
    current_branch: str
    title: str
    base_ref: str
    body: str
    changed_files: tuple[str, ...]
    validation_commands: tuple[str, ...]
    preflight: TaskPrPreflightReport


def task_branch(contributor_id: str, agent_id: str, task_id: str, short_slug: str) -> str:
    """Build a canonical task branch name."""
    contributor_id = normalize_contributor_id(contributor_id)
    task_number = task_id.removeprefix("TASK-")
    return f"agent/{contributor_id}/{agent_id}/task-{task_number}-{short_slug}"


def task_title(task_id: str, short_description: str) -> str:
    """Build the canonical task PR title."""
    return f"{task_id}: {short_description}"


def task_slug_from_title(title: str, *, fallback: str, max_length: int = 64) -> str:
    """Build a portable ASCII branch slug from a task title."""
    normalized = unicodedata.normalize("NFKD", title)
    ascii_title = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")
    if not slug:
        slug = fallback.lower()
    if len(slug) <= max_length:
        return slug
    trimmed = slug[:max_length].rstrip("-")
    return trimmed or fallback.lower()


def task_payload(root: Path, task_id: str) -> tuple[Path, dict]:
    """Load a task and return its path plus validated payload."""
    task_file = find_task_file(root, task_id)
    return task_file, load_task(task_file)


def task_validation_commands_from_payload(payload: dict) -> tuple[str, ...]:
    """Return task-declared validation commands, preserving order."""
    validation = payload.get("validation", {})
    if not isinstance(validation, dict):
        return ()
    commands = validation.get("commands", ())
    if not isinstance(commands, list):
        return ()
    return tuple(str(command) for command in commands if str(command).strip())


def commit_subjects_vs_base(root: Path, branch: str, *, base_ref: str = "main") -> tuple[str, ...]:
    """Return commit subjects on ``branch`` that are not in ``base_ref``."""
    result = run_git_command(["log", "--format=%s", f"{base_ref}..{branch}"], cwd=root)
    if result.returncode != 0:
        return ()
    return tuple(line.strip() for line in result.stdout.splitlines() if line.strip())


def commit_subject_errors_for_task(task_id: str, subjects: tuple[str, ...]) -> tuple[str, ...]:
    """Return commit subject format errors for a canonical task PR."""
    expected_number = task_id.removeprefix("TASK-").lower()
    expected_format = f"<type>(task-{expected_number}): <short summary>"
    errors: list[str] = []
    for subject in subjects:
        match = TASK_COMMIT_SUBJECT_PATTERN.match(subject)
        if match is None or match.group("number") != expected_number:
            errors.append(
                f"Commit subject {subject!r} does not follow {expected_format!r} "
                f"for {task_id}."
            )
    return tuple(errors)


def default_prepare_current_base(root: Path) -> str:
    """Return the safest default base ref for prepare-current helper diffs."""
    for ref in DEFAULT_PREPARE_CURRENT_REMOTE_BASES:
        if branch_exists(root, ref):
            return ref
    return DEFAULT_PREPARE_CURRENT_LOCAL_BASE


def prepare_current_task_pr(
    root: Path,
    *,
    task_id: str,
    contributor_id: str,
    github_username: str,
    agent_id: str,
    human_reviewer: str,
    summary: str,
    slug: str | None = None,
    description: str | None = None,
    changed_files: tuple[str, ...] = (),
    validation_commands: tuple[str, ...] = (),
    scientific_claim_impact: str = "No claim promotion.",
    result_artifact_impact: str = "No committed result artifacts changed.",
    task_verdict: str = "not_applicable",
    canonical_destination: str = "none",
    review_tier: str = "none",
    gate_a_status: str = "not_applicable",
    gate_b_status: str = "not_applicable",
    claim_impact: str = "No claim promotion.",
    knowledge_impact: str = "No knowledge promotion.",
    limitations_blockers: str = "None for this PR shape.",
    model_version: str | None = None,
    base_ref: str | None = None,
    agent_tool: str | None = None,
    local_artifact_paths: tuple[str, ...] = (),
) -> PreparedTaskPr:
    """Generate and preflight a full task PR body for the current branch.

    This helper intentionally uses the *current* branch in the generated body.
    If the agent is on a non-canonical branch, preflight fails before the PR is
    opened instead of hiding the mistake behind a generated expected branch.
    """
    from physics_lab.registry.review_policy import infer_agent_tool

    task_file, payload = task_payload(root, task_id)
    task_description = description or str(payload.get("title", task_id)).strip()
    task_slug = slug or task_slug_from_title(task_description, fallback=task_id.lower())
    expected_branch = task_branch(contributor_id, agent_id, task_id, task_slug)
    branch = current_branch(root)
    title = task_title(task_id, task_description)
    resolved_base_ref = base_ref or default_prepare_current_base(root)
    ignored_local_artifacts = {
        Path(item).as_posix().lstrip("./") for item in local_artifact_paths
    }
    auto_changed_files = tuple(
        path
        for path in changed_files_vs_main(root, branch, base_ref=resolved_base_ref)
        if path.lstrip("./") not in ignored_local_artifacts
    )
    merged_changed_files = tuple(dict.fromkeys((*auto_changed_files, *changed_files)))
    task_commands = task_validation_commands_from_payload(payload)
    merged_validation_commands = tuple(dict.fromkeys((*task_commands, *validation_commands)))
    body = task_pr_body(
        task_id=task_id,
        branch=branch,
        title=title,
        contributor_id=contributor_id,
        github_username=github_username,
        agent_tool=agent_tool or infer_agent_tool(agent_id),
        human_reviewer=human_reviewer,
        summary=summary,
        changed_files=merged_changed_files,
        validation_commands=merged_validation_commands,
        scientific_claim_impact=scientific_claim_impact,
        result_artifact_impact=result_artifact_impact,
        task_verdict=task_verdict,
        canonical_destination=canonical_destination,
        review_tier=review_tier,
        gate_a_status=gate_a_status,
        gate_b_status=gate_b_status,
        claim_impact=claim_impact,
        knowledge_impact=knowledge_impact,
        limitations_blockers=limitations_blockers,
        branch_pushed=False,
        draft_pr_opened=False,
        post_pr_review_run=False,
        ready_for_review=False,
        model_version=model_version,
        root=root,
    )
    report = preflight_task_pr(root, branch=branch, title=title, body_text=body)
    errors = list(report.errors)
    warnings = list(report.warnings)
    errors.extend(
        commit_subject_errors_for_task(
            task_id,
            commit_subjects_vs_base(root, branch, base_ref=resolved_base_ref),
        )
    )
    if branch != expected_branch:
        warnings.append(
            "Current branch differs from the generated suggested branch for this task: "
            f"current `{branch}`, expected `{expected_branch}`."
        )
    report = TaskPrPreflightReport(errors=tuple(errors), warnings=tuple(warnings))
    return PreparedTaskPr(
        task_id=task_id,
        task_file=task_file,
        expected_branch=expected_branch,
        current_branch=branch,
        title=title,
        base_ref=resolved_base_ref,
        body=body,
        changed_files=merged_changed_files,
        validation_commands=merged_validation_commands,
        preflight=report,
    )


def _render_checkbox(is_checked: bool) -> str:
    return "[x]" if is_checked else "[ ]"


def task_pr_body(
    *,
    task_id: str,
    branch: str,
    title: str,
    contributor_id: str,
    github_username: str,
    agent_tool: str,
    human_reviewer: str,
    summary: str,
    changed_files: tuple[str, ...],
    validation_commands: tuple[str, ...],
    scientific_claim_impact: str,
    result_artifact_impact: str,
    task_verdict: str = "not_applicable",
    canonical_destination: str = "none",
    review_tier: str = "none",
    gate_a_status: str = "not_applicable",
    gate_b_status: str = "not_applicable",
    claim_impact: str = "No claim promotion.",
    knowledge_impact: str = "No knowledge promotion.",
    limitations_blockers: str = "None for this PR shape.",
    branch_pushed: bool = False,
    draft_pr_opened: bool = False,
    post_pr_review_run: bool = False,
    ready_for_review: bool = False,
    model_version: str | None = None,
    root: Path = Path("."),
) -> str:
    """Render a repository-native canonical task PR body."""
    contributor_id = normalize_contributor_id(contributor_id)
    task_file = find_task_file(root, task_id).as_posix()
    changed = tuple(dict.fromkeys((task_file, *changed_files)))
    changed_lines = [f"- `{item}`" for item in changed] or ["- "]
    validation_lines = [
        f"- {_render_checkbox(True)} `{command}`"
        for command in validation_commands
    ] or ["- "]
    model_value = f"`{model_version}`" if model_version else ""

    return "\n".join(
        [
            "## PR Kind",
            "",
            "- [x] Canonical task PR",
            "- [ ] Task proposal PR",
            "- [ ] Microtask PR",
            "- [ ] Task closeout PR",
            "",
            "## Primary Reference",
            "",
            "Canonical task PR:",
            "",
            f"- Task ID: `{task_id}`",
            f"- Task File: `{task_file}`",
            "",
            "## Branch Name",
            "",
            f"- `{branch}`",
            "",
            "## PR Title",
            "",
            f"- `{title}`",
            "",
            "## PR Lifecycle",
            "",
            f"- {_render_checkbox(branch_pushed)} Branch pushed",
            f"- {_render_checkbox(draft_pr_opened)} Draft PR opened by agent or manual PR creation commands provided",
            f"- {_render_checkbox(post_pr_review_run)} Post-PR review command run or manual review command provided if no PR number is available",
            f"- {_render_checkbox(ready_for_review)} Marked ready for review after CI passes and review agent returns `MERGE_OK`, or manual ready command provided",
            "",
            "## Summary",
            "",
            summary,
            "",
            "## Changed Files",
            "",
            *changed_lines,
            "",
            "## Linked Repository Memory",
            "",
            "- Hypothesis:",
            "- Experiment:",
            f"- Task / Proposal / Queue: `{task_id}`",
            "- Result:",
            "- Claim / Knowledge:",
            "",
            "## Validation Commands",
            "",
            *validation_lines,
            "",
            "## Scientific Claim Impact",
            "",
            f"- {scientific_claim_impact}",
            "",
            "## Result Artifact Impact",
            "",
            f"- {result_artifact_impact}",
            "",
            "## Output Routing",
            "",
            f"- Task verdict: `{task_verdict}`",
            f"- Canonical destination: `{canonical_destination}`",
            f"- Review tier: `{review_tier}`",
            f"- Gate A status: `{gate_a_status}`",
            f"- Gate B status: `{gate_b_status}`",
            f"- Claim impact: {claim_impact}",
            f"- Knowledge impact: {knowledge_impact}",
            f"- Limitations / blockers: {limitations_blockers}",
            "",
            "If this PR contains `AGENT_PUBLISHED` or `AGENT_VALIDATED` artifacts, "
            "keep the qualifier explicit and document Gate A/Gate B status.",
            "",
            "## Agent / Contributor Metadata",
            "",
            f"- Contributor ID: `{contributor_id}`",
            f"- GitHub username: `{github_username}`",
            f"- Agent tool: `{agent_tool}`",
            f"- Model/version if known: {model_value}",
            f"- Task ID / Proposal / Queue: `{task_id}`",
            f"- Branch: `{branch}`",
            f"- Human reviewer: `{human_reviewer}`",
            "",
            "## Maintainer Review Notes",
            "",
            "- Review the validation commands and generated review bundle before merge.",
            "- Keep any task status transition at REVIEW_READY until maintainer closeout.",
            "",
        ]
    )


def _placeholder_hits(body_text: str) -> tuple[str, ...]:
    return tuple(marker for marker in PLACEHOLDER_MARKERS if marker in body_text)


def preflight_task_pr(
    root: Path,
    *,
    branch: str,
    title: str,
    body_text: str,
) -> TaskPrPreflightReport:
    """Check whether a canonical task PR shape looks repository-ready."""
    body_text = normalize_pr_body(body_text)
    errors: list[str] = []
    warnings: list[str] = []

    branch_match = BRANCH_PATTERN.match(branch)
    title_match = PR_TITLE_PATTERN.match(title)

    if branch_match is None:
        errors.append(
            "Branch must follow agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug>."
        )
    if title_match is None:
        errors.append("PR title must follow TASK-XXXX: <short title>.")

    branch_id = branch_task_id(branch)
    title_id = title_match.group("task_id") if title_match is not None else None
    if branch_id is not None and title_id is not None and branch_id != title_id:
        errors.append(f"Branch task id {branch_id} does not match PR title task id {title_id}.")

    missing_sections = missing_pr_template_sections(body_text)
    if missing_sections:
        errors.append(
            "PR body is missing required template sections: "
            + ", ".join(missing_sections)
            + ". Use .github/pull_request_template.md or a filled helper-generated body file."
        )

    missing_fields = missing_pr_metadata_fields(body_text)
    if missing_fields:
        errors.append(
            "PR body is missing required metadata fields or values: "
            + ", ".join(missing_fields)
            + "."
        )

    agent_tool_mismatch = agent_tool_metadata_mismatch(branch, body_text)
    if agent_tool_mismatch is not None:
        errors.append(agent_tool_mismatch)

    contributor_mismatch = contributor_metadata_mismatch(branch, body_text)
    if contributor_mismatch is not None:
        errors.append(contributor_mismatch)

    placeholders = _placeholder_hits(body_text)
    if placeholders:
        errors.append(
            "PR body still contains placeholder text: " + ", ".join(placeholders) + "."
        )

    if title_id is not None:
        try:
            find_task_file(root, title_id)
        except (FileNotFoundError, ValueError) as exc:
            errors.append(str(exc))

    # The review bundle is optional, not a mandatory PR step (see TASK-0466, F5),
    # so its absence is no longer flagged. scripts/apl_review_bundle.sh remains
    # available for maintainers who want a full diff snapshot.
    if STRICT_VALIDATE_REPO_PATTERN.search(body_text) is None:
        warnings.append("PR body does not mention strict repository validation.")

    return TaskPrPreflightReport(errors=tuple(errors), warnings=tuple(warnings))
