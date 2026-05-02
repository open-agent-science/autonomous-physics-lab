from __future__ import annotations

from physics_lab.registry.maintainer_review import (
    ReviewReport,
    branch_proposal_slug,
    branch_task_id,
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


def test_rule_catalog_lines_are_not_treated_as_live_risk() -> None:
    assert line_is_rule_catalog_line('    "solved",')
    assert line_is_rule_catalog_line(
        '    (re.compile(r"\\beval\\s*\\("), "Introduces eval(...)."),'
    )
