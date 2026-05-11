from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from physics_lab.registry.maintainer_review import (
    ReviewReport,
    PullRequestMetadata,
    ValidationSummary,
    branch_microtask_id,
    branch_microtask_queue_id,
    branch_proposal_slug,
    branch_task_id,
    build_review_report,
    changed_task_proposal_files,
    line_is_rule_catalog_line,
    missing_pr_metadata_fields,
    overclaim_advisory_hits,
    overclaim_hits,
    parse_added_lines,
    render_review_report,
    run_task_validation,
    security_pattern_hits,
    sensitive_surface_hits,
)
from physics_lab.registry.review_checks import (
    load_claim_status_from_ref,
    unexpected_protected_changes,
)
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


def test_branch_microtask_id_extracts_microtask_id() -> None:
    assert (
        branch_microtask_id("agent/roman/codex/microtask-PMR-001-audit-electron-mass")
        == "PMR-001"
    )
    assert branch_microtask_id("agent/roman/codex/microtask-pmr-batch-1") is None


def test_branch_microtask_queue_id_extracts_queue_id_from_batch_branch() -> None:
    assert (
        branch_microtask_queue_id(
            "agent/roman/codex/microtask-batch-dimensional-analysis-validator--challenge-batch-02"
        )
        == "dimensional-analysis-validator"
    )
    assert branch_microtask_queue_id(
        "agent/roman/codex/microtask-PMR-001-audit-electron-mass"
    ) is None


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


def test_missing_pr_metadata_fields_accepts_task_id_alias() -> None:
    body = "\n".join(
        [
            "- Contributor ID: roman",
            "- GitHub username: gladunrv",
            "- Agent tool: codex",
            "- Task ID / Proposal / Queue: microtask(dimensional-analysis-validator)",
            "- Branch: agent/roman/codex/microtask-batch-dimensional-analysis-validator--challenge-entries",
            "- Human reviewer: roman",
        ]
    )

    assert missing_pr_metadata_fields(body) == ()


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


def test_overclaim_hits_treat_wrapped_guardrail_language_as_advisory() -> None:
    added_lines = (
        "Do not promote claims, rewrite canonical results, or use",
        "discovery/proved/solved wording.",
    )

    assert overclaim_hits(added_lines) == ()
    assert "proved" in overclaim_advisory_hits(added_lines)
    assert "solved" in overclaim_advisory_hits(added_lines)


def test_overclaim_hits_still_block_positive_claims() -> None:
    added_lines = (
        "The benchmark proved the model and solved the anomaly.",
    )

    assert "proved" in overclaim_hits(added_lines)
    assert "solved" in overclaim_hits(added_lines)


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
    assert "Advisory warnings:" in rendered


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


def test_build_review_report_closeout_batch_pr_is_merge_ok(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "ACTIVE.md").write_text("# active board\n", encoding="utf-8")
    (tmp_path / "docs").mkdir(parents=True)
    (tmp_path / "docs" / "multi-agent-dry-run.md").write_text("# dry run\n", encoding="utf-8")

    for task_id, slug in (("TASK-0027", "units"), ("TASK-0062", "roadmap")):
        (tasks_dir / f"{task_id}-{slug}.yaml").write_text(
            "\n".join(
                [
                    f"id: {task_id}",
                    'title: "Test closeout task"',
                    "type: documentation",
                    "status: DONE",
                    "difficulty: low",
                    "priority: medium",
                    "strategy_alignment:",
                    '  - "Closeout regression fixture"',
                    "input:",
                    "  mode: workflow",
                    '  related_domain: "testing"',
                    "  related_objects: []",
                    '  planning_context: "Closeout review fixture"',
                    "requirements:",
                    '  - "Keep task status at DONE in closeout branch"',
                    "accepted_outputs:",
                    '  - "updated task status"',
                    "validation:",
                    "  commands:",
                    '    - "python3 -m physics_lab.cli validate-repo ."',
                    "can_be_done_by: [human]",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    branch = "agent/roman/codex/closeout-confirmed-merged-tasks"
    changed = (
        "docs/multi-agent-dry-run.md",
        "tasks/ACTIVE.md",
        "tasks/TASK-0027-units.yaml",
        "tasks/TASK-0062-roadmap.yaml",
    )
    pr_metadata = PullRequestMetadata(
        number=67,
        title="TASK-CLOSEOUT: Mark confirmed merged tasks as done",
        body="closeout batch",
        branch=branch,
        base_branch="main",
        state="OPEN",
        merged=False,
        status_checks_passed=True,
        status_checks_pending=False,
        changed_files=changed,
    )

    with (
        patch("physics_lab.registry.maintainer_review.current_branch", return_value=branch),
        patch("physics_lab.registry.maintainer_review.local_branch_exists", return_value=True),
        patch("physics_lab.registry.maintainer_review.changed_files_vs_main", return_value=changed),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=pr_metadata),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "present")),
        patch(
            "physics_lab.registry.maintainer_review.run_task_validation",
            return_value=ValidationSummary(status="pass", failed_commands=()),
        ),
    ):
        report = build_review_report(tmp_path, pull_request=67)

    assert report.task_id == "TASK-CLOSEOUT"
    assert report.verdict == "MERGE_OK"
    assert report.blockers == ()


def test_build_review_report_closeout_batch_pr_can_pass_from_non_branch_checkout(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "ACTIVE.md").write_text("# active board\n", encoding="utf-8")

    for task_id, slug in (("TASK-0027", "units"), ("TASK-0062", "roadmap")):
        (tasks_dir / f"{task_id}-{slug}.yaml").write_text(
            "\n".join(
                [
                    f"id: {task_id}",
                    'title: "Test closeout task"',
                    "type: documentation",
                    "status: DONE",
                    "difficulty: low",
                    "priority: medium",
                    "strategy_alignment:",
                    '  - "Closeout regression fixture"',
                    "input:",
                    '  mode: workflow',
                    '  related_domain: "testing"',
                    "  related_objects: []",
                    '  planning_context: "Closeout review fixture"',
                    "requirements:",
                    '  - "Keep task status at DONE in closeout branch"',
                    "accepted_outputs:",
                    '  - "updated task status"',
                    "validation:",
                    "  commands:",
                    '    - "python3 -m physics_lab.cli validate-repo ."',
                    "can_be_done_by: [human]",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    branch = "agent/roman/codex/closeout-confirmed-merged-tasks"
    changed = (
        "tasks/ACTIVE.md",
        "tasks/TASK-0027-units.yaml",
        "tasks/TASK-0062-roadmap.yaml",
    )
    pr_metadata = PullRequestMetadata(
        number=67,
        title="TASK-CLOSEOUT: Mark confirmed merged tasks as done",
        body="closeout batch",
        branch=branch,
        base_branch="main",
        state="OPEN",
        merged=False,
        status_checks_passed=True,
        status_checks_pending=False,
        changed_files=changed,
    )

    with (
        patch("physics_lab.registry.maintainer_review.current_branch", return_value="main"),
        patch("physics_lab.registry.maintainer_review.local_branch_exists", return_value=True),
        patch("physics_lab.registry.maintainer_review.changed_files_vs_main", return_value=changed),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=pr_metadata),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "missing")),
    ):
        report = build_review_report(tmp_path, pull_request=67)

    assert report.task_id == "TASK-CLOSEOUT"
    assert report.verdict == "MERGE_OK"
    assert not any("Switch to the PR branch" in item for item in report.required_fixes)


def test_build_review_report_closeout_batch_pr_does_not_require_active_board_sync(
    tmp_path: Path,
) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)

    for task_id, slug in (("TASK-0027", "units"), ("TASK-0062", "roadmap")):
        (tasks_dir / f"{task_id}-{slug}.yaml").write_text(
            "\n".join(
                [
                    f"id: {task_id}",
                    'title: "Test closeout task"',
                    "type: documentation",
                    "status: DONE",
                    "difficulty: low",
                    "priority: medium",
                    "strategy_alignment:",
                    '  - "Closeout regression fixture"',
                    "input:",
                    '  mode: workflow',
                    '  related_domain: "testing"',
                    "  related_objects: []",
                    '  planning_context: "Closeout review fixture"',
                    "requirements:",
                    '  - "Keep task status at DONE in closeout branch"',
                    "accepted_outputs:",
                    '  - "updated task status"',
                    "validation:",
                    "  commands:",
                    '    - "python3 -m physics_lab.cli validate-repo ."',
                    "can_be_done_by: [human]",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    branch = "agent/roman/codex/closeout-confirmed-merged-tasks"
    changed = (
        "tasks/TASK-0027-units.yaml",
        "tasks/TASK-0062-roadmap.yaml",
    )
    pr_metadata = PullRequestMetadata(
        number=67,
        title="TASK-CLOSEOUT: Mark confirmed merged tasks as done",
        body="closeout batch",
        branch=branch,
        base_branch="main",
        state="OPEN",
        merged=False,
        status_checks_passed=True,
        status_checks_pending=False,
        changed_files=changed,
    )

    with (
        patch("physics_lab.registry.maintainer_review.current_branch", return_value=branch),
        patch("physics_lab.registry.maintainer_review.local_branch_exists", return_value=True),
        patch("physics_lab.registry.maintainer_review.changed_files_vs_main", return_value=changed),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=pr_metadata),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "present")),
        patch(
            "physics_lab.registry.maintainer_review.run_task_validation",
            return_value=ValidationSummary(status="pass", failed_commands=()),
        ),
    ):
        report = build_review_report(tmp_path, pull_request=67)

    assert report.task_id == "TASK-CLOSEOUT"
    assert report.verdict == "MERGE_OK"
    assert not any("ACTIVE.md" in item for item in report.required_fixes)


def test_build_review_report_prefers_origin_main_as_diff_base_for_prs(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "TASK-0094-helper.yaml").write_text(
        "\n".join(
            [
                "id: TASK-0094",
                'title: "Helper bug task"',
                "type: maintainer_workflow",
                "status: REVIEW_READY",
                "difficulty: medium",
                "priority: high",
                "strategy_alignment:",
                '  - "Test fixture"',
                "input:",
                '  mode: workflow',
                '  related_domain: "maintainer_review"',
                "  related_objects: []",
                '  planning_context: "Fixture"',
                "requirements:",
                '  - "Keep review helper deterministic"',
                "accepted_outputs:",
                '  - "tasks/TASK-0094-helper.yaml"',
                "validation:",
                "  commands:",
                '    - "python3 -m physics_lab.cli validate-repo ."',
                "can_be_done_by: [human]",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    pr_metadata = PullRequestMetadata(
        number=103,
        title="TASK-0094: Track maintainer review helper stale diff false positives",
        body="\n".join(
            [
                "- Contributor ID: roman",
                "- GitHub username: gladunrv",
                "- Agent tool: codex",
                "- Task ID: TASK-0094",
                "- Branch: agent/roman/codex/task-0094-fix-helper-stale-diff",
                "- Human reviewer: roman",
            ]
        ),
        branch="agent/roman/codex/task-0094-fix-helper-stale-diff",
        base_branch="main",
        state="OPEN",
        merged=False,
        status_checks_passed=True,
        status_checks_pending=False,
        changed_files=("tasks/TASK-0094-helper.yaml",),
    )
    changed = ("tasks/TASK-0094-helper.yaml",)

    with (
        patch(
            "physics_lab.registry.maintainer_review.current_branch",
            return_value="agent/roman/codex/task-0094-fix-helper-stale-diff",
        ),
        patch("physics_lab.registry.maintainer_review.local_branch_exists", return_value=True),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch("physics_lab.registry.maintainer_review.branch_exists", side_effect=lambda _root, ref: ref == "origin/main"),
        patch("physics_lab.registry.maintainer_review.changed_files_vs_main", return_value=changed) as changed_mock,
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=pr_metadata),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "present")),
        patch(
            "physics_lab.registry.maintainer_review.run_task_validation",
            return_value=ValidationSummary(status="pass", failed_commands=()),
        ),
    ):
        report = build_review_report(tmp_path, pull_request=103)

    assert report.verdict == "MERGE_OK"
    assert changed_mock.call_args.kwargs["base_ref"] == "origin/main"


def test_build_review_report_accepts_canonical_microtask_pr(tmp_path: Path) -> None:
    microtasks_dir = tmp_path / "tasks" / "microtasks"
    microtasks_dir.mkdir(parents=True)
    (microtasks_dir / "particle-mass-relations.yaml").write_text(
        "\n".join(
            [
                "queue_id: particle-mass-relations",
                "campaign: particle-mass-relations",
                "campaign_status: active_with_narrow_results",
                "selection_guidance:",
                '  - "Prefer falsification-first notes."',
                "microtasks:",
                '  - id: PMR-001',
                '    campaign: particle-mass-relations',
                '    title: "Audit one mass entry"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    pr_metadata = PullRequestMetadata(
        number=129,
        title="microtask(particle-mass-relations): add one Koide methodology note",
        body="\n".join(
            [
                "- Contributor ID: roman",
                "- GitHub username: gladunrv",
                "- Agent tool: codex",
                "- Task ID: microtask(PMR-001)",
                "- Branch: agent/roman/codex/microtask-PMR-001-koide-methodology-note",
                "- Human reviewer: roman",
            ]
        ),
        branch="agent/roman/codex/microtask-PMR-001-koide-methodology-note",
        base_branch="main",
        state="OPEN",
        merged=False,
        status_checks_passed=True,
        status_checks_pending=False,
        changed_files=("docs/notes/pmr-001-audit-note.md",),
    )
    changed = ("docs/notes/pmr-001-audit-note.md",)

    with (
        patch(
            "physics_lab.registry.maintainer_review.current_branch",
            return_value="agent/roman/codex/microtask-PMR-001-koide-methodology-note",
        ),
        patch("physics_lab.registry.maintainer_review.local_branch_exists", return_value=True),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch("physics_lab.registry.maintainer_review.changed_files_vs_main", return_value=changed),
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=pr_metadata),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "present")),
        patch(
            "physics_lab.registry.maintainer_review.run_task_validation",
            return_value=ValidationSummary(status="pass", failed_commands=()),
        ),
    ):
        report = build_review_report(tmp_path, pull_request=129)

    assert report.verdict == "MERGE_OK"
    assert report.task_id == "MICROTASK(particle-mass-relations)"
    assert not any("task file" in item.lower() for item in report.blockers)


def test_build_review_report_accepts_canonical_microtask_batch_pr(tmp_path: Path) -> None:
    microtasks_dir = tmp_path / "tasks" / "microtasks"
    microtasks_dir.mkdir(parents=True)
    (microtasks_dir / "dimensional-analysis-validator.yaml").write_text(
        "\n".join(
            [
                "queue_id: dimensional-analysis-validator",
                "campaign: dimensional-analysis-validator",
                "campaign_status: active_with_narrow_results",
                "selection_guidance:",
                '  - "Prefer narrow challenge-set additions."',
                "microtasks:",
                '  - id: DAV-003',
                '    campaign: dimensional-analysis-validator',
                '    title: "Add one SUSPICIOUS challenge item"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    changed = (
        "docs/notes/dimensional-analysis-microtask-batch-02.md",
        "knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml",
    )

    pr_metadata = PullRequestMetadata(
        number=148,
        title="microtask(dimensional-analysis-validator): add DAV-003 DAV-004 DAV-008 challenge entries",
        body="\n".join(
            [
                "- Contributor ID: roman",
                "- GitHub username: gladunrv",
                "- Agent tool: codex",
                "- Task ID: microtask(dimensional-analysis-validator)",
                "- Branch: agent/roman/codex/microtask-batch-dimensional-analysis-validator--challenge-entries",
                "- Human reviewer: roman",
            ]
        ),
        branch="agent/roman/codex/microtask-batch-dimensional-analysis-validator--challenge-entries",
        base_branch="main",
        state="OPEN",
        merged=False,
        status_checks_passed=True,
        status_checks_pending=False,
        changed_files=changed,
    )

    with (
        patch(
            "physics_lab.registry.maintainer_review.current_branch",
                return_value="agent/roman/codex/microtask-batch-dimensional-analysis-validator--challenge-entries",
        ),
        patch("physics_lab.registry.maintainer_review.local_branch_exists", return_value=True),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch("physics_lab.registry.maintainer_review.changed_files_vs_main", return_value=changed),
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=pr_metadata),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "present")),
        patch(
            "physics_lab.registry.maintainer_review.run_task_validation",
            return_value=ValidationSummary(status="pass", failed_commands=()),
        ),
    ):
        report = build_review_report(tmp_path, pull_request=148)

    assert report.verdict == "MERGE_OK"
    assert report.task_id == "MICROTASK(dimensional-analysis-validator)"


def test_build_review_report_blocks_microtask_batch_when_branch_queue_mismatches_title(
    tmp_path: Path,
) -> None:
    microtasks_dir = tmp_path / "tasks" / "microtasks"
    microtasks_dir.mkdir(parents=True)
    (microtasks_dir / "dimensional-analysis-validator.yaml").write_text(
        "queue_id: dimensional-analysis-validator\nmicrotasks: []\n",
        encoding="utf-8",
    )

    pr_metadata = PullRequestMetadata(
        number=149,
        title="microtask(dimensional-analysis-validator): add batch note",
        body="\n".join(
            [
                "- Contributor ID: roman",
                "- GitHub username: gladunrv",
                "- Agent tool: codex",
                "- Task ID: microtask(dimensional-analysis-validator)",
                "- Branch: agent/roman/codex/microtask-batch-particle-mass-relations--challenge-entries",
                "- Human reviewer: roman",
            ]
        ),
        branch="agent/roman/codex/microtask-batch-particle-mass-relations--challenge-entries",
        base_branch="main",
        state="OPEN",
        merged=False,
        status_checks_passed=True,
        status_checks_pending=False,
        changed_files=("docs/notes/test.md",),
    )

    with (
        patch(
            "physics_lab.registry.maintainer_review.current_branch",
                return_value="agent/roman/codex/microtask-batch-particle-mass-relations--challenge-entries",
        ),
        patch("physics_lab.registry.maintainer_review.local_branch_exists", return_value=True),
        patch(
            "physics_lab.registry.maintainer_review.changed_files_vs_main",
            return_value=("docs/notes/test.md",),
        ),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=pr_metadata),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "present")),
        patch(
            "physics_lab.registry.maintainer_review.run_task_validation",
            return_value=ValidationSummary(status="pass", failed_commands=()),
        ),
    ):
        report = build_review_report(tmp_path, pull_request=149)

    assert report.verdict == "BLOCKED"
    assert any("does not match PR title queue id" in item for item in report.blockers)


def test_unexpected_protected_changes_allows_task_authorized_result_artifacts() -> None:
    task_payload = {
        "accepted_outputs": (
            "particle-mass relation falsifier workflow",
            "reproducible benchmark result artifacts",
        ),
        "requirements": (),
        "input": {"related_objects": ()},
    }

    changed_files = (
        "results/EXP-0009/RUN-0001/result.yaml",
        "results/EXP-0009/RUN-0001/report.md",
    )

    assert unexpected_protected_changes(changed_files, task_payload) == ()


def test_unexpected_protected_changes_still_blocks_unauthorized_result_artifacts() -> None:
    task_payload = {
        "accepted_outputs": ("docs update",),
        "requirements": (),
        "input": {"related_objects": ()},
    }

    changed_files = ("results/EXP-9999/RUN-0001/result.yaml",)

    assert unexpected_protected_changes(changed_files, task_payload) == changed_files


def test_build_review_report_blocks_microtask_pr_when_queue_file_missing(tmp_path: Path) -> None:
    pr_metadata = PullRequestMetadata(
        number=130,
        title="microtask(unknown-queue): add one note",
        body="\n".join(
            [
                "- Contributor ID: roman",
                "- GitHub username: gladunrv",
                "- Agent tool: codex",
                "- Task ID: microtask(ABC-001)",
                "- Branch: agent/roman/codex/microtask-ABC-001-test-note",
                "- Human reviewer: roman",
            ]
        ),
        branch="agent/roman/codex/microtask-ABC-001-test-note",
        base_branch="main",
        state="OPEN",
        merged=False,
        status_checks_passed=True,
        status_checks_pending=False,
        changed_files=("docs/notes/test.md",),
    )

    with (
        patch(
            "physics_lab.registry.maintainer_review.current_branch",
            return_value="agent/roman/codex/microtask-ABC-001-test-note",
        ),
        patch("physics_lab.registry.maintainer_review.local_branch_exists", return_value=True),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch(
            "physics_lab.registry.maintainer_review.changed_files_vs_main",
            return_value=("docs/notes/test.md",),
        ),
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=pr_metadata),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "present")),
        patch(
            "physics_lab.registry.maintainer_review.run_task_validation",
            return_value=ValidationSummary(status="pass", failed_commands=()),
        ),
    ):
        report = build_review_report(tmp_path, pull_request=130)

    assert report.verdict == "BLOCKED"
    assert any("No microtask queue file found" in item for item in report.blockers)
