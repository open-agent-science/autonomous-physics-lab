from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from physics_lab.registry.maintainer_review import (
    ReviewReport,
    branch_proposal_slug,
    branch_task_id,
    build_review_report,
    changed_task_proposal_files,
    line_is_rule_catalog_line,
    missing_pr_metadata_fields,
    overclaim_hits,
    parse_added_lines,
    render_review_report,
    run_task_validation,
    security_pattern_hits,
    sensitive_surface_hits,
)
from physics_lab.registry.review_checks import load_claim_status_from_ref
from physics_lab.registry.review_git import CommandResult


def test_branch_task_id_extracts_task_number() -> None:
    assert (
        branch_task_id("agent/roman/codex/task-0034-maintainer-review-agent")
        == "TASK-0034"
    )
    assert branch_task_id("main") is None


def test_branch_proposal_slug_extracts_task_proposal_slug() -> None:
    assert (
        branch_proposal_slug("agent/roman/codex/propose-task-koide-track")
        == "koide-track"
    )
    assert branch_proposal_slug("agent/roman/codex/task-0043-task-proposal-protocol") is None


def test_changed_task_proposal_files_filters_template_and_other_paths() -> None:
    changed_files = (
        "tasks/proposals/20260502-roman-koide-track.yaml",
        "tasks/proposals/TASK-PROPOSAL-TEMPLATE.yaml",
        "tasks/TASK-0043-add-task-proposal-protocol-and-id-allocation-rules.yaml",
    )

    assert changed_task_proposal_files(changed_files) == (
        "tasks/proposals/20260502-roman-koide-track.yaml",
    )


def test_missing_pr_metadata_fields_detects_blank_template_values() -> None:
    body = "\n".join(
        [
            "- Contributor ID: roman",
            "- GitHub username: ",
            "- Agent tool: codex",
            "- Task ID: TASK-0034",
            "- Branch: agent/roman/codex/task-0034-maintainer-review-agent",
            "- Human reviewer: ",
        ]
    )

    assert missing_pr_metadata_fields(body) == ("GitHub username", "Human reviewer")


def test_overclaim_and_security_hits_detect_obvious_risks() -> None:
    added_lines = (
        "We solved physics with a 100% correct model.",
        "value = eval(user_input)",
        "payload = pickle.loads(blob)",
    )

    assert "solved" in overclaim_hits(added_lines)
    assert "100% correct" in overclaim_hits(added_lines)
    pattern_hits = security_pattern_hits(added_lines)
    assert "Introduces eval(...)." in pattern_hits
    assert "Introduces pickle.loads(...)." in pattern_hits


def test_overclaim_hits_ignore_guardrail_language() -> None:
    added_lines = (
        "Do not say solved physics in result notes.",
        "Avoid claiming 100% correct models without proof.",
    )

    assert overclaim_hits(added_lines) == ()


def test_sensitive_surface_hits_flags_repository_safety_surfaces() -> None:
    changed_files = (
        "scripts/apl_review_pr.py",
        ".github/workflows/ci.yml",
        "docs/maintainer-review-agent.md",
    )

    hits = sensitive_surface_hits(changed_files)
    assert any("Repository scripts changed." in item for item in hits)
    assert any("CI workflow files changed." in item for item in hits)
    assert all("docs/maintainer-review-agent.md" not in item for item in hits)


def test_render_review_report_includes_security_section() -> None:
    report = ReviewReport(
        verdict="MERGE_OK",
        risk="medium",
        task_id="TASK-0034",
        branch="agent/roman/codex/task-0034-maintainer-review-agent",
        changed_files=("scripts/apl_review_pr.py",),
        validation="pass",
        security_risks=("Repository scripts changed. Path: scripts/apl_review_pr.py",),
        blockers=(),
        required_fixes=(),
        recommended_action="Merge after GitHub CI is green.",
    )

    rendered = render_review_report(report)

    assert "Security risks:" in rendered
    assert "Repository scripts changed." in rendered


def test_run_task_validation_skips_self_referential_review_command(tmp_path) -> None:
    payload = {
        "validation": {
            "commands": [
                "python3 scripts/apl_review_pr.py --branch agent/roman/codex/task-0034-maintainer-review-agent --task TASK-0034 || true",
                "python3 -c 'print(123)'",
            ]
        }
    }

    summary = run_task_validation(
        tmp_path,
        payload,
        enabled=True,
        skip_commands_containing=("scripts/apl_review_pr.py",),
    )

    assert summary.status == "pass"


def test_parse_added_lines_can_exclude_tests_or_limit_prefixes() -> None:
    diff_text = "\n".join(
        [
            "+++ b/tests/test_maintainer_review.py",
            "+We solved physics with a 100% correct model.",
            "+++ b/scripts/apl_review_pr.py",
            "+value = eval(user_input)",
        ]
    )

    assert parse_added_lines(diff_text, exclude_prefixes=("tests/",)) == (
        "value = eval(user_input)",
    )
    assert parse_added_lines(
        diff_text,
        include_prefixes=("scripts/",),
    ) == ("value = eval(user_input)",)


def test_changed_task_proposal_files_returns_multiple_files() -> None:
    changed_files = (
        "tasks/proposals/20260503-roman-glossary.yaml",
        "tasks/proposals/20260503-roman-conftest.yaml",
        "tasks/proposals/20260503-roman-diagram.yaml",
        "tasks/proposals/TASK-PROPOSAL-TEMPLATE.yaml",
        "tasks/ACTIVE.md",
    )

    result = changed_task_proposal_files(changed_files)
    assert result == (
        "tasks/proposals/20260503-roman-glossary.yaml",
        "tasks/proposals/20260503-roman-conftest.yaml",
        "tasks/proposals/20260503-roman-diagram.yaml",
    )


def test_rule_catalog_lines_are_not_treated_as_live_risk() -> None:
    assert line_is_rule_catalog_line('    "solved",')
    assert line_is_rule_catalog_line(
        '    (re.compile(r"\\beval\\s*\\("), "Introduces eval(...)."),'
    )


_PROPOSAL_YAML = """\
proposal_id: {proposal_id}
title: "Test proposal"
status: PROPOSED
type: documentation
priority: medium
proposed_by:
  contributor_id: roman
  agent_id: claude
strategy_alignment:
  - verification-first
summary: "Test proposal for e2e test."
rationale: "Ensures multi-proposal PRs are reviewed correctly."
input:
  mode: planning_only
  related_domain: "testing"
  related_objects: []
  planning_context: "e2e test fixture"
requirements:
  - "Keep the proposal atomic"
  - "Do not promote claims automatically"
accepted_outputs:
  - "canonical task spec"
  - "docs update"
validation:
  commands:
    - "./scripts/validate_quick.sh"
    - "python3 -m physics_lab.cli validate-repo ."
    - "python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings"
promotion:
  canonical_task_id: null
  decision: pending
  notes: "pending maintainer review"
"""

_EMPTY_DIFF = CommandResult(returncode=0, stdout="", stderr="")


def test_build_review_report_multi_proposal_pr_is_not_blocked(tmp_path: Path) -> None:
    """A PR with multiple tasks/proposals/*.yaml files must not produce a BLOCKED verdict."""
    proposals_dir = tmp_path / "tasks" / "proposals"
    proposals_dir.mkdir(parents=True)
    proposal_slugs = ("alpha", "beta", "gamma")
    proposal_paths = []
    for slug in proposal_slugs:
        path = proposals_dir / f"20260503-roman-{slug}.yaml"
        path.write_text(_PROPOSAL_YAML.format(proposal_id=f"20260503-roman-{slug}"), encoding="utf-8")
        proposal_paths.append(f"tasks/proposals/20260503-roman-{slug}.yaml")

    branch = "agent/roman/claude/propose-task-multi-test"
    changed = tuple(proposal_paths) + ("docs/notes/some-planning-note.md",)

    with (
        patch("physics_lab.registry.maintainer_review.current_branch", return_value="main"),
        patch("physics_lab.registry.maintainer_review.local_branch_exists", return_value=True),
        patch("physics_lab.registry.maintainer_review.changed_files_vs_main", return_value=changed),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "present")),
    ):
        report = build_review_report(tmp_path, branch=branch)

    assert report.verdict != "BLOCKED", f"Expected non-BLOCKED verdict, got blockers: {report.blockers}"
    assert not any("multiple" in b.lower() and "proposal" in b.lower() for b in report.blockers), (
        f"Unexpected multi-proposal blocker: {report.blockers}"
    )


def test_load_claim_status_from_ref_handles_git_worktree_layout(tmp_path: Path) -> None:
    """The helper must work when .git is a file, as in git worktrees."""
    (tmp_path / ".git").write_text("gitdir: /tmp/fake-worktree-gitdir\n", encoding="utf-8")
    claim_markdown = "\n".join(
        [
            "---",
            "id: CLAIM-0001",
            "title: Test claim",
            "domain: testing",
            "status: DRAFT",
            "hypothesis_id: HYP-0001",
            "evidence:",
            "  experiments:",
            "    - EXP-0001",
            "  results:",
            "    - RESULT-0001",
            "scope: Temporary review helper regression fixture.",
            "---",
            "",
            "# Claim body",
            "",
            "Worktree-safe temp file handling should preserve claim parsing.",
        ]
    )

    with (
        patch("physics_lab.registry.review_checks.path_exists_in_ref", return_value=True),
        patch(
            "physics_lab.registry.review_checks.run_command",
            return_value=CommandResult(returncode=0, stdout=claim_markdown, stderr=""),
        ),
    ):
        assert (
            load_claim_status_from_ref(tmp_path, "main", "claims/CLAIM-TEST.md") == "DRAFT"
        )
