"""Helpers for scaffolding and preflighting canonical task PRs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from physics_lab.registry.review_policy import (
    BRANCH_PATTERN,
    PR_TITLE_PATTERN,
    branch_task_id,
    missing_pr_metadata_fields,
    missing_pr_template_sections,
)
from physics_lab.registry.task_closeout import find_task_file


PLACEHOLDER_MARKERS = (
    "TASK-XXXX",
    "tasks/TASK-XXXX-short-slug.yaml",
    "agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug>",
    "<short title>",
)


@dataclass(frozen=True)
class TaskPrPreflightReport:
    """Result of checking a canonical task PR branch/title/body triple."""

    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def task_branch(contributor_id: str, agent_id: str, task_id: str, short_slug: str) -> str:
    """Build a canonical task branch name."""
    task_number = task_id.removeprefix("TASK-")
    return f"agent/{contributor_id}/{agent_id}/task-{task_number}-{short_slug}"


def task_title(task_id: str, short_description: str) -> str:
    """Build the canonical task PR title."""
    return f"{task_id}: {short_description}"


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
    model_version: str | None = None,
    root: Path = Path("."),
) -> str:
    """Render a repository-native canonical task PR body."""
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
            "- [x] Branch pushed",
            "- [x] Draft PR opened by agent or explicit blocker recorded",
            "- [x] Post-PR review command run or blocked by missing PR number",
            "- [ ] Marked ready for review after CI passes and review agent returns `MERGE_OK`, or explicit blocker recorded",
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

    if "./scripts/apl_review_bundle.sh" not in body_text and "apl_review_bundle.sh" not in body_text:
        warnings.append("PR body does not mention the generated review bundle.")
    if "python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings" not in body_text:
        warnings.append("PR body does not mention strict repository validation.")

    return TaskPrPreflightReport(errors=tuple(errors), warnings=tuple(warnings))
