"""Helpers for scaffolding and preflighting closeout PRs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from physics_lab.registry.maintainer_review import (
    CLOSEOUT_BRANCH_PATTERN,
    CLOSEOUT_PR_TITLE_PATTERN,
    missing_pr_metadata_fields,
    missing_pr_template_sections,
)
from physics_lab.registry.review_policy import (
    agent_tool_metadata_mismatch,
    contributor_metadata_mismatch,
    normalize_contributor_id,
)
from physics_lab.registry.task_closeout import find_task_file


PLACEHOLDER_MARKERS = (
    "TASK-XXXX",
    "agent/<contributor-id>/<agent-id>/closeout-<short-slug>",
)


@dataclass(frozen=True)
class CloseoutPreflightReport:
    """Result of checking a closeout PR branch/title/body triple."""

    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def closeout_branch(contributor_id: str, agent_id: str, short_slug: str) -> str:
    """Build a canonical closeout branch name."""
    contributor_id = normalize_contributor_id(contributor_id)
    return f"agent/{contributor_id}/{agent_id}/closeout-{short_slug}"


def closeout_title(short_description: str) -> str:
    """Build the canonical closeout PR title."""
    return f"TASK-CLOSEOUT: {short_description}"


def _render_checkbox(is_checked: bool) -> str:
    return "[x]" if is_checked else "[ ]"


def closeout_pr_body(
    *,
    task_ids: tuple[str, ...],
    branch: str,
    title: str,
    contributor_id: str,
    github_username: str,
    agent_tool: str,
    human_reviewer: str,
    changed_files: tuple[str, ...] = (),
    proposal_drift: bool = False,
    proposal_paths: tuple[str, ...] = (),
    include_task_views: bool = False,
    include_context: bool = False,
    model_version: str | None = None,
    root: Path = Path("."),
) -> str:
    """Render a repository-native closeout PR body."""
    contributor_id = normalize_contributor_id(contributor_id)
    if proposal_drift and not proposal_paths:
        raise ValueError("Proposal-drift closeout requires at least one --proposal-path value.")
    if not proposal_drift and not task_ids:
        raise ValueError("At least one --closed-task TASK-XXXX value is required.")
    if any(task_id == "TASK-CLOSEOUT" for task_id in task_ids):
        raise ValueError(
            "TASK-CLOSEOUT is the closeout PR marker, not a task file. "
            "Pass real closed task ids with --closed-task TASK-XXXX."
        )
    task_files = tuple(find_task_file(root, task_id).as_posix() for task_id in task_ids)
    changed = list(proposal_paths if proposal_drift else task_files)
    if include_task_views:
        changed.append("docs/task-views/")
    if include_context:
        changed.append("CONTEXT.md")
    changed.extend(item for item in changed_files if item not in changed)

    closed_task_files = ", ".join(f"`{item}`" for item in task_files)
    proposal_closeout_files = ", ".join(f"`{item}`" for item in proposal_paths)
    changed_lines = [f"- `{item}`" for item in changed] or ["- "]
    task_refs = ", ".join(f"`{task_id}`" for task_id in task_ids) or "`TASK-CLOSEOUT`"
    model_value = f"`{model_version}`" if model_version else ""
    primary_reference = (
        [f"- Proposal Drift Closeout Files: {proposal_closeout_files}"]
        if proposal_drift
        else [f"- Closed Task Files: {closed_task_files}"]
    )
    summary = (
        "Mechanically reconcile proposal-pool drift for proposals whose canonical tasks are already DONE."
        if proposal_drift
        else "Close out already-merged task work, synchronize generated task state, and keep the repository handoff accurate."
    )
    validation_lines = (
        [
            "- [x] `python3 scripts/apl_proposal_triage.py`",
            "- [x] `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings`",
        ]
        if proposal_drift
        else [
            f"- {_render_checkbox(include_task_views)} `python3 -m physics_lab.cli sync-active-board .` (normally not needed; the `Sync Active Board` post-merge GitHub Action regenerates `docs/task-views/*.md` on `main` after the closeout merges)",
            f"- {_render_checkbox(include_context)} `python3 scripts/generate_context_bundle.py`",
            "- [x] `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings`",
        ]
    )
    maintainer_notes = (
        [
            "- Use this closeout PR only for mechanical proposal-pool reconciliation after canonical task delivery.",
            "- Do not use this lane to accept new proposal ideas or make science-scope decisions.",
        ]
        if proposal_drift
        else [
            f"- Closed tasks in this PR: {task_refs}.",
            "- Use this closeout PR only for task-status updates and generated navigation/context sync.",
        ]
    )

    return "\n".join(
        [
            "## PR Kind",
            "",
            "- [ ] Canonical task PR",
            "- [ ] Task proposal PR",
            "- [ ] Microtask PR",
            "- [x] Task closeout PR",
            "",
            "## Primary Reference",
            "",
            "Task closeout PR:",
            "",
            "- Task ID: `TASK-CLOSEOUT`",
            *primary_reference,
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
            "- [x] Branch pushed",
            "- [x] Draft PR opened by agent or manual PR creation commands provided",
            "- [ ] Post-PR review command run or manual review command provided if no PR number is available",
            "- [ ] Marked ready for review after CI passes and review agent returns `MERGE_OK`, or manual ready command provided",
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
            f"- Task / Proposal / Queue: {task_refs}",
            "- Result:",
            "- Claim / Knowledge:",
            "",
            "## Validation Commands",
            "",
            *validation_lines,
            "",
            "## Scientific Claim Impact",
            "",
            "- None. This PR is closeout bookkeeping only.",
            "",
            "## Result Artifact Impact",
            "",
            "- [x] I used `--output-dir` for routine validation runs, or no workflow runs were needed.",
            "- [x] I intentionally updated committed `results/` artifacts, or I left them untouched.",
            "- [x] If canonical artifacts changed, the change is scientifically meaningful and explained in this PR.",
            "",
            "## Agent / Contributor Metadata",
            "",
            f"- Contributor ID: `{contributor_id}`",
            f"- GitHub username: `{github_username}`",
            f"- Agent tool: `{agent_tool}`",
            f"- Model/version if known: {model_value}",
            "- Task ID / Proposal / Queue: `TASK-CLOSEOUT`",
            f"- Branch: `{branch}`",
            f"- Human reviewer: `{human_reviewer}`",
            "",
            "## Maintainer Review Notes",
            "",
            *maintainer_notes,
            "",
        ]
    )


def _placeholder_hits(body_text: str) -> tuple[str, ...]:
    return tuple(marker for marker in PLACEHOLDER_MARKERS if marker in body_text)


def preflight_closeout_pr(
    root: Path,
    *,
    branch: str,
    title: str,
    body_text: str,
) -> CloseoutPreflightReport:
    """Check whether a closeout PR shape looks repository-ready."""
    errors: list[str] = []
    warnings: list[str] = []

    if CLOSEOUT_BRANCH_PATTERN.match(branch) is None:
        errors.append(
            "Branch must follow agent/<contributor-id>/<agent-id>/closeout-<short-slug>."
        )

    if CLOSEOUT_PR_TITLE_PATTERN.match(title) is None:
        errors.append("PR title must follow TASK-CLOSEOUT: <short title>.")

    missing_sections = missing_pr_template_sections(body_text)
    if missing_sections:
        rendered_sections = ", ".join(missing_sections)
        errors.append(
            "PR body is missing required template sections: "
            + rendered_sections
            + ". Use .github/pull_request_template.md or a filled --body-file before requesting review."
        )

    missing_fields = missing_pr_metadata_fields(body_text)
    if missing_fields:
        rendered_fields = ", ".join(missing_fields)
        errors.append(
            "PR body is missing required metadata fields or values: "
            + rendered_fields
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

    if "Closed Task Files:" not in body_text and "Proposal Drift Closeout Files:" not in body_text:
        warnings.append(
            "PR body does not list Closed Task Files or Proposal Drift Closeout Files under Primary Reference."
        )
    if "python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings" not in body_text:
        warnings.append("PR body does not mention strict repository validation.")

    return CloseoutPreflightReport(errors=tuple(errors), warnings=tuple(warnings))
