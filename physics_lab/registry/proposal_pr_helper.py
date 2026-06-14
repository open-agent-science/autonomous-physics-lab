"""Helpers for scaffolding and preflighting task-proposal PRs.

Task proposals previously had no helper (unlike canonical tasks, microtasks,
closeouts, and agent runs), so authors hand-built the branch, title, filename,
and YAML by hand and only discovered format or schema mistakes after pushing.
This module mirrors ``task_pr_helper`` for the proposal lane: it scaffolds a
schema-valid proposal YAML and runs a lightweight preflight (branch, title,
filename, and schema) that does not require the full pytest suite. See
TASK-0467.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import yaml

from physics_lab.registry.review_policy import (
    PROPOSAL_BRANCH_PATTERN,
    PROPOSAL_PR_TITLE_PATTERN,
    branch_proposal_slug,
    normalize_contributor_id,
)
from physics_lab.registry.task_proposals import load_task_proposal


PROPOSAL_DIR = "tasks/proposals"
PROPOSAL_FILENAME_PATTERN = re.compile(
    r"^(?P<date>[0-9]{8})-(?P<rest>[a-z0-9-]+)\.yaml$"
)
LEGACY_PROPOSAL_FILENAME_PATTERN = re.compile(
    r"^(?P<date>[0-9]{8})-(?P<contributor>[a-z0-9]+)-(?P<slug>[a-z0-9-]+)\.yaml$"
)


@dataclass(frozen=True)
class ProposalPrPreflightReport:
    """Result of checking a task-proposal branch/title/file triple."""

    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def proposal_branch(contributor_id: str, agent_id: str, slug: str) -> str:
    """Build the canonical proposal branch name."""
    contributor_id = normalize_contributor_id(contributor_id)
    return f"agent/{contributor_id}/{agent_id}/propose-task-{slug}"


def proposal_title(short_title: str) -> str:
    """Build the canonical proposal PR title."""
    return f"TASK-PROPOSAL: {short_title}"


def proposal_id_value(date_str: str, contributor_id: str, slug: str) -> str:
    """Build the canonical proposal id (and filename stem)."""
    contributor_id = normalize_contributor_id(contributor_id)
    return f"{date_str}-{contributor_id}-{slug}"


def proposal_filename(date_str: str, contributor_id: str, slug: str) -> str:
    """Build the canonical proposal filename."""
    return f"{proposal_id_value(date_str, contributor_id, slug)}.yaml"


def proposal_yaml(
    *,
    date_str: str,
    contributor_id: str,
    agent_id: str,
    slug: str,
    title: str,
    proposal_type: str,
    summary: str,
    rationale: str,
    related_domain: str,
    planning_context: str,
    priority: str = "medium",
    input_mode: str = "planning_only",
    related_objects: tuple[str, ...] = (),
    strategy_alignment: tuple[str, ...] = (),
    requirements: tuple[str, ...] = (),
    accepted_outputs: tuple[str, ...] = (),
) -> str:
    """Render a schema-valid task-proposal YAML document.

    The ``planning_context`` field (a frequent omission that fails the input
    ``oneOf`` schema) is always included.
    """
    contributor_id = normalize_contributor_id(contributor_id)
    document = {
        "proposal_id": proposal_id_value(date_str, contributor_id, slug),
        "title": title,
        "status": "PROPOSED",
        "type": proposal_type,
        "priority": priority,
        "proposed_by": {
            "contributor_id": contributor_id,
            "agent_id": agent_id,
        },
        "strategy_alignment": list(strategy_alignment)
        or ["Describe how this proposal advances a campaign or removes a blocker."],
        "summary": summary,
        "rationale": rationale or summary,
        "input": {
            "mode": input_mode,
            "related_domain": related_domain,
            "related_objects": list(related_objects),
            "planning_context": planning_context,
        },
        "requirements": list(requirements)
        or ["Keep the proposal atomic", "Do not promote claims automatically"],
        "accepted_outputs": list(accepted_outputs)
        or ["canonical task spec", "docs update"],
        "promotion": {
            "canonical_task_id": None,
            "decision": "pending",
            "notes": "Awaiting maintainer acceptance and canonical task id.",
        },
    }
    return yaml.safe_dump(document, sort_keys=False, allow_unicode=True, width=88)


def _proposal_filename_parts(
    name: str,
    *,
    branch_slug: str | None,
) -> tuple[str, str, str] | None:
    """Parse proposal filenames, using the branch slug to disambiguate dashes.

    Proposal filenames are ``YYYYMMDD-<contributor-id>-<slug>.yaml``. Once
    contributor ids may contain dashes, the branch slug is the canonical way to
    determine where the contributor id ends and the slug begins.
    """
    match = PROPOSAL_FILENAME_PATTERN.match(name)
    if match is None:
        return None
    date_str = match.group("date")
    rest = match.group("rest")
    if branch_slug:
        suffix = f"-{branch_slug}"
        if not rest.endswith(suffix):
            return None
        contributor = rest[: -len(suffix)]
        if not contributor:
            return None
        return date_str, contributor, branch_slug

    legacy_match = LEGACY_PROPOSAL_FILENAME_PATTERN.match(name)
    if legacy_match is None:
        return None
    return (
        legacy_match.group("date"),
        legacy_match.group("contributor"),
        legacy_match.group("slug"),
    )


def preflight_proposal_pr(
    root: Path,
    *,
    branch: str,
    title: str,
    proposal_path: str,
) -> ProposalPrPreflightReport:
    """Check a proposal branch/title/file before opening a PR.

    This is the lighter proposal validation path: it checks the branch, title,
    and filename formats and validates the proposal against the task_proposal
    schema. It does not run the full test suite.
    """
    errors: list[str] = []
    warnings: list[str] = []

    branch_match = PROPOSAL_BRANCH_PATTERN.match(branch)
    if branch_match is None:
        errors.append(
            f"Branch {branch!r} does not match the proposal branch format "
            "agent/<contributor-id>/<agent-id>/propose-task-<short-slug>."
        )

    if PROPOSAL_PR_TITLE_PATTERN.match(title) is None:
        errors.append(
            f"Title {title!r} does not match the proposal PR title format "
            "'TASK-PROPOSAL: <short title>'."
        )

    rel_path = proposal_path.replace("\\", "/")
    name = Path(rel_path).name
    if not rel_path.startswith(f"{PROPOSAL_DIR}/"):
        errors.append(f"Proposal file {rel_path!r} must live under {PROPOSAL_DIR}/.")
    # Branch slug and filename slug should agree, so the PR is easy to trace.
    branch_slug = branch_proposal_slug(branch)
    filename_parts = _proposal_filename_parts(name, branch_slug=branch_slug)
    if filename_parts is None and branch_slug is not None:
        legacy_match = LEGACY_PROPOSAL_FILENAME_PATTERN.match(name)
        if legacy_match is not None:
            filename_parts = (
                legacy_match.group("date"),
                legacy_match.group("contributor"),
                legacy_match.group("slug"),
            )
    if filename_parts is None:
        errors.append(
            f"Proposal filename {name!r} does not match the format "
            "YYYYMMDD-<contributor-id>-<short-slug>.yaml."
        )
    elif branch_slug is not None and filename_parts[2] != branch_slug:
        warnings.append(
            f"Branch slug {branch_slug!r} does not match proposal filename slug "
            f"{filename_parts[2]!r}."
        )

    absolute_path = (root / rel_path).resolve()
    if not absolute_path.exists():
        errors.append(f"Proposal file {rel_path!r} does not exist.")
    else:
        try:
            load_task_proposal(absolute_path)
        except (ValueError, yaml.YAMLError) as exc:
            errors.append(str(exc))

    return ProposalPrPreflightReport(errors=tuple(errors), warnings=tuple(warnings))
