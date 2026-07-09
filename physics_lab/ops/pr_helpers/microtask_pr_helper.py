"""Helpers for scaffolding and preflighting microtask PRs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from physics_lab.registry.maintainer_review import (
    MICROTASK_BATCH_BRANCH_PATTERN,
    MICROTASK_BRANCH_PATTERN,
    MICROTASK_PR_TITLE_PATTERN,
    branch_microtask_queue_id,
    latest_review_bundle,
    review_bundle_branch,
)
from physics_lab.registry.review_policy import normalize_contributor_id


PLACEHOLDER_MARKERS = (
    "TASK-XXXX",
    "tasks/TASK-XXXX-short-slug.yaml",
    "agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug>",
)


@dataclass(frozen=True)
class MicrotaskPreflightReport:
    """Result of checking a microtask PR branch/title/body triple."""

    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def microtask_branch(
    contributor_id: str,
    agent_id: str,
    short_slug: str,
    *,
    queue_id: str | None = None,
    microtask_id: str | None = None,
) -> str:
    """Build a canonical microtask branch name."""
    if (queue_id is None) == (microtask_id is None):
        raise ValueError("Provide exactly one of queue_id or microtask_id.")
    contributor_id = normalize_contributor_id(contributor_id)
    if microtask_id is not None:
        return (
            f"agent/{contributor_id}/{agent_id}/"
            f"microtask-{microtask_id}-{short_slug}"
        )
    return (
        f"agent/{contributor_id}/{agent_id}/"
        f"microtask-batch-{queue_id}--{short_slug}"
    )


def microtask_title(queue_id: str, short_description: str) -> str:
    """Build the canonical microtask PR title."""
    return f"microtask({queue_id}): {short_description}"


def microtask_pr_body(
    *,
    queue_id: str,
    branch: str,
    title: str,
    microtask_ids: tuple[str, ...],
) -> str:
    """Render a repository-native microtask PR body."""
    ids_rendered = ", ".join(microtask_ids) if microtask_ids else "narrow same-queue batch"
    return "\n".join(
        [
            "## PR Kind",
            "",
            "- [ ] Canonical task PR",
            "- [ ] Task proposal PR",
            "- [x] Microtask PR",
            "- [ ] Task closeout PR",
            "",
            "## Primary Reference",
            "",
            "Microtask PR:",
            "",
            f"- Queue ID: `{queue_id}`",
            f"- Queue File: `tasks/microtasks/{queue_id}.yaml`",
            f"- Microtask IDs: `{ids_rendered}`",
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
            "Describe the change in narrow, verification-first terms.",
            "",
            "## Changed Files",
            "",
            "- ",
            "",
            "## Linked Repository Memory",
            "",
            "- Hypothesis:",
            "- Experiment:",
            f"- Task / Proposal / Queue: `microtask({queue_id})`",
            "- Result:",
            "- Claim / Knowledge:",
            "",
            "## Validation Commands",
            "",
            "- [ ] `./scripts/validate_quick.sh`",
            "- [ ] `python3 -m physics_lab.cli validate-repo .`",
            "- [ ] `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings`",
            "- [ ] `./scripts/apl_review_bundle.sh`",
            "",
            "Note: agents do not commit regenerated `docs/task-views/*.md`",
            "from microtask PRs; the `Sync Active Board` post-merge GitHub",
            "Action handles regeneration on `main`.",
            "",
            "## Scientific Claim Impact",
            "",
            "- None beyond the narrow microtask scope.",
            "",
            "## Result Artifact Impact",
            "",
            "- [ ] I used `--output-dir` for routine validation runs, or no workflow runs were needed.",
            "- [ ] I intentionally left committed `results/` artifacts untouched.",
            "- [ ] No canonical result artifacts changed in this PR.",
            "",
            "## Agent / Contributor Metadata",
            "",
            "- Contributor ID:",
            "- GitHub username:",
            "- Agent tool:",
            "- Model/version if known:",
            f"- Task ID / Proposal / Queue: `microtask({queue_id})`",
            f"- Branch: `{branch}`",
            "- Human reviewer:",
            "",
            "## Maintainer Review Notes",
            "",
            f"- Target microtask ids: `{ids_rendered}`.",
            "- Keep limitations explicit and do not promote claims from this PR.",
            "",
        ]
    )


def _placeholder_hits(body_text: str) -> tuple[str, ...]:
    return tuple(marker for marker in PLACEHOLDER_MARKERS if marker in body_text)


def preflight_microtask_pr(
    root: Path,
    *,
    branch: str,
    title: str,
    body_text: str,
) -> MicrotaskPreflightReport:
    """Check whether a microtask PR shape looks repository-ready."""
    errors: list[str] = []
    warnings: list[str] = []

    single_match = MICROTASK_BRANCH_PATTERN.match(branch)
    batch_match = MICROTASK_BATCH_BRANCH_PATTERN.match(branch)
    title_match = MICROTASK_PR_TITLE_PATTERN.match(title)

    if single_match is None and batch_match is None:
        errors.append(
            "Branch must follow agent/<contributor-id>/<agent-id>/microtask-<microtask-id>-<short-slug> "
            "or agent/<contributor-id>/<agent-id>/microtask-batch-<queue-id>--<short-slug>."
        )

    if title_match is None:
        errors.append("PR title must follow microtask(<queue-id>): <short description>.")
        queue_id = None
    else:
        queue_id = title_match.group("queue_id")

    if queue_id is not None and batch_match is not None:
        branch_queue = branch_microtask_queue_id(branch)
        if branch_queue != queue_id:
            errors.append(
                f"Batch branch queue id {branch_queue} does not match PR title queue id {queue_id}."
            )

    placeholders = _placeholder_hits(body_text)
    if placeholders:
        errors.append(
            "PR body still contains placeholder text: " + ", ".join(placeholders) + "."
        )

    if "./scripts/apl_review_bundle.sh" not in body_text and "apl_review_bundle.sh" not in body_text:
        warnings.append("PR body does not remind the contributor to run ./scripts/apl_review_bundle.sh.")

    bundle = latest_review_bundle(root, branch)
    if bundle is None or review_bundle_branch(bundle) != branch:
        warnings.append(
            "No valid review bundle found for this branch yet. Run ./scripts/apl_review_bundle.sh before requesting maintainer review."
        )

    return MicrotaskPreflightReport(errors=tuple(errors), warnings=tuple(warnings))
