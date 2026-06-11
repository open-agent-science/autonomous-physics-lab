from __future__ import annotations

import json
from pathlib import Path
import sys
from unittest.mock import patch

from physics_lab.registry.maintainer_review import (
    ArtifactReviewSignal,
    CleanPrWorktree,
    ReviewReport,
    PullRequestMetadata,
    ValidationSummary,
    branch_microtask_id,
    branch_microtask_queue_id,
    branch_proposal_slug,
    branch_task_queue_slug,
    branch_task_id,
    build_review_report,
    classify_artifact_review_changes,
    changed_task_proposal_files,
    ci_aware_validation_command,
    coauthor_trailer_advisory_hits,
    line_is_rule_catalog_line,
    load_pr_metadata,
    missing_pr_metadata_fields,
    missing_pr_template_sections,
    decision_regression_advisory_hits,
    overclaim_advisory_hits,
    overclaim_hits,
    parse_added_lines,
    _portable_validation_command,
    output_routing_value,
    prepare_clean_pr_worktree,
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
from physics_lab.registry.review_policy import (
    agent_tool_metadata_mismatch,
    classify_review_protocol,
    validate_pr_title,
)
from physics_lab.registry.pr_finish_gate import (
    CheckState,
    CiGate,
    finish_pr,
    render_finish_gate_report,
)


def _full_pr_body(
    *,
    task_ref: str,
    branch: str,
    kind: str = "Canonical task PR",
    primary_reference: str | None = None,
) -> str:
    """Return a filled PR-template body for maintainer-review fixtures."""
    primary = primary_reference or f"- Task ID: `{task_ref}`"
    return "\n".join(
        [
            "## PR Kind",
            "",
            f"- [x] {kind}",
            "",
            "## Primary Reference",
            "",
            primary,
            "",
            "## Branch Name",
            "",
            f"- `{branch}`",
            "",
            "## PR Lifecycle",
            "",
            "- [x] Branch pushed",
            "- [x] Draft PR opened by agent or manual PR creation commands provided",
            "- [x] Post-PR review command run or manual review command provided if no PR number is available",
            "- [x] Marked ready for review after CI passes and review agent returns `MERGE_OK`, or manual ready command provided",
            "",
            "## Summary",
            "",
            "- Regression fixture body.",
            "",
            "## Changed Files",
            "",
            "- Fixture paths listed in test metadata.",
            "",
            "## Linked Repository Memory",
            "",
            "- Hypothesis:",
            "- Experiment:",
            f"- Task / Proposal / Queue: `{task_ref}`",
            "- Result:",
            "- Claim / Knowledge:",
            "",
            "## Validation Commands",
            "",
            "- [x] `python3 -m physics_lab.cli validate-repo .`",
            "",
            "## Scientific Claim Impact",
            "",
            "- None.",
            "",
            "## Result Artifact Impact",
            "",
            "- No canonical result artifacts changed.",
            "",
            "## Agent / Contributor Metadata",
            "",
            "- Contributor ID: roman",
            "- GitHub username: gladunrv",
            "- Agent tool: codex",
            "- Model/version if known: test",
            f"- Task ID / Proposal / Queue: `{task_ref}`",
            f"- Branch: `{branch}`",
            "- Human reviewer: roman",
            "",
            "## Maintainer Review Notes",
            "",
            "- Fixture review note.",
        ]
    )


def _write_review_task(
    root: Path,
    task_id: str,
    *,
    status: str = "REVIEW_READY",
    slug: str = "helper",
) -> None:
    tasks_dir = root / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    (tasks_dir / f"{task_id}-{slug}.yaml").write_text(
        "\n".join(
            [
                f"id: {task_id}",
                'title: "Maintainer review fixture"',
                "type: maintainer_workflow",
                f"status: {status}",
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
                f'  - "tasks/{task_id}-{slug}.yaml"',
                "validation:",
                "  commands:",
                '    - "python3 -m physics_lab.cli validate-repo ."',
                "can_be_done_by: [human]",
            ]
        )
        + "\n",
        encoding="utf-8",
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


def test_branch_task_queue_slug_extracts_task_queue_slug() -> None:
    assert (
        branch_task_queue_slug("agent/roman/codex/task-queue-coverage-audit")
        == "coverage-audit"
    )
    assert branch_task_queue_slug("agent/roman/codex/task-0043-task-proposal-protocol") is None


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


def test_review_protocol_classifies_supported_review_lanes() -> None:
    assert (
        classify_review_protocol(
            "agent/roman/codex/task-0137-maintainer-review-policy-layers"
        ).kind
        == "task"
    )
    assert (
        classify_review_protocol("agent/roman/codex/propose-task-review-policy").kind
        == "proposal"
    )
    assert (
        classify_review_protocol("agent/roman/codex/task-queue-coverage-audit").kind
        == "task_queue"
    )
    assert (
        classify_review_protocol("agent/roman/codex/closeout-merged-workflow-tasks").kind
        == "closeout"
    )
    microtask = classify_review_protocol(
        "agent/roman/codex/microtask-batch-dimensional-analysis-validator--challenge-entries",
        pr_title="microtask(dimensional-analysis-validator): add challenge entries",
    )
    assert microtask.kind == "microtask"
    assert microtask.microtask_queue_id == "dimensional-analysis-validator"
    assert microtask.title_microtask_queue_id == "dimensional-analysis-validator"


def test_review_protocol_uses_pr_title_for_closeout_and_microtask_lanes() -> None:
    closeout = classify_review_protocol(
        "agent/roman/codex/task-9999-admin",
        pr_title="TASK-CLOSEOUT: Mark confirmed merged tasks as done",
    )
    microtask = classify_review_protocol(
        "agent/roman/codex/task-9999-admin",
        pr_title="microtask(particle-mass-relations): add one audit note",
    )
    task_queue = classify_review_protocol(
        "agent/roman/codex/task-9999-admin",
        pr_title="TASK-QUEUE: Add coverage audit task",
    )

    assert closeout.kind == "closeout"
    assert microtask.kind == "microtask"
    assert microtask.title_microtask_queue_id == "particle-mass-relations"
    assert task_queue.kind == "task_queue"


def test_review_protocol_pr_title_policy_is_testable_without_github() -> None:
    assert validate_pr_title(
        review_kind="task",
        title="TASK-0137: Split maintainer review helper into clearer policy layers",
        resolved_task_id="TASK-0137",
    ).required_fixes == ()

    mismatch = validate_pr_title(
        review_kind="task",
        title="TASK-0138: Add replay hardening",
        resolved_task_id="TASK-0137",
    )
    assert mismatch.blockers == (
        "PR title task id TASK-0138 does not match TASK-0137.",
    )

    microtask = validate_pr_title(
        review_kind="microtask",
        title="TASK-0137: Wrong title lane",
        resolved_task_id="MICROTASK",
    )
    assert microtask.required_fixes == (
        "PR title does not follow microtask(<queue-id>): ... format.",
    )

    task_queue = validate_pr_title(
        review_kind="task_queue",
        title="TASK-QUEUE: Add coverage audit task",
        resolved_task_id="TASK-QUEUE",
    )
    assert task_queue.blockers == ()
    assert task_queue.required_fixes == ()


def test_pr_title_policy_flags_task_queue_and_closeout_lane_mismatches() -> None:
    task_queue = validate_pr_title(
        review_kind="task_queue",
        title="TASK-0241: Wrong title lane",
        resolved_task_id="TASK-QUEUE",
    )
    closeout = validate_pr_title(
        review_kind="closeout",
        title="TASK-0241: Wrong title lane",
        resolved_task_id="TASK-CLOSEOUT",
    )

    assert task_queue.required_fixes == (
        "PR title does not follow TASK-QUEUE: ... format.",
    )
    assert closeout.required_fixes == (
        "PR title does not follow TASK-CLOSEOUT: ... format.",
    )


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


def test_output_routing_value_extracts_review_fields() -> None:
    body = "\n".join(
        [
            "## Output Routing",
            "",
            "- Review tier: `AGENT_PUBLISHED`",
            "- Gate A status: pass",
            "- Gate B status: not_applicable",
        ]
    )

    assert output_routing_value(body, "Review tier") == "AGENT_PUBLISHED"
    assert output_routing_value(body, "Gate A status") == "pass"


def test_artifact_review_change_classification_uses_distinct_classes(tmp_path: Path) -> None:
    changed_files = (
        "results/EXP-9999/RUN-9999/result.yaml",
        "prediction_registry/test/PRED-9999.yaml",
        "claims/CLAIM-9999-test.md",
        "knowledge/KNOW-9999-test.yaml",
    )

    with (
        patch(
            "physics_lab.registry.maintainer_review.load_yaml_payload_from_ref",
            side_effect=[
                {"review_tier": "AGENT_PUBLISHED"},
                {"review_tier": "AGENT_VALIDATED"},
                {"review_tier": "MAINTAINER_REVIEWED"},
            ],
        ),
        patch(
            "physics_lab.registry.maintainer_review.load_claim_status_from_ref",
            side_effect=[None, "DRAFT"],
        ),
    ):
        signals = classify_artifact_review_changes(
            tmp_path,
            target_branch="agent/roman/codex/task-0410-review-helper-artifact-classes",
            base_ref="origin/main",
            changed_files=changed_files,
        )

    assert [signal.artifact_class for signal in signals] == [
        "result_publication",
        "prediction_publication",
        "draft_claim_authoring",
        "knowledge_phase1_maintainer_only",
    ]
    assert signals[0].review_tier == "AGENT_PUBLISHED"
    assert signals[1].review_tier == "AGENT_VALIDATED"


def test_build_review_report_requires_agent_published_output_routing(
    tmp_path: Path,
) -> None:
    _write_review_task(tmp_path, "TASK-0410")
    branch = "agent/roman/codex/task-0410-review-helper-artifact-classes"
    pr_metadata = PullRequestMetadata(
        number=410,
        title="TASK-0410: Teach review helper artifact classes",
        body=_full_pr_body(
            task_ref="TASK-0410",
            branch=branch,
            primary_reference="- Task ID: `TASK-0410`\n- Task File: `tasks/TASK-0410-helper.yaml`",
        ),
        branch=branch,
        base_branch="main",
        state="OPEN",
        merged=False,
        status_checks_passed=True,
        status_checks_pending=False,
        changed_files=("tasks/TASK-0410-helper.yaml",),
    )

    gate_report = type("GateReportFixture", (), {"ok": True, "issues": ()})()
    with (
        patch("physics_lab.registry.maintainer_review.current_branch", return_value=branch),
        patch("physics_lab.registry.maintainer_review.local_branch_exists", return_value=True),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch("physics_lab.registry.maintainer_review.changed_files_vs_main", return_value=("tasks/TASK-0410-helper.yaml",)),
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=pr_metadata),
        patch(
            "physics_lab.registry.maintainer_review.classify_artifact_review_changes",
            return_value=(
                ArtifactReviewSignal(
                    path="results/EXP-9999/RUN-9999/result.yaml",
                    artifact_class="result_publication",
                    review_tier="AGENT_PUBLISHED",
                ),
            ),
        ),
        patch("physics_lab.registry.maintainer_review.load_yaml_payload_from_ref", return_value={}),
        patch("physics_lab.registry.maintainer_review.check_payload", return_value=gate_report),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "present")),
        patch(
            "physics_lab.registry.maintainer_review.run_task_validation",
            return_value=ValidationSummary(status="pass", failed_commands=()),
        ),
    ):
        report = build_review_report(tmp_path, pull_request=410)

    assert report.verdict == "NEEDS_CHANGES"
    assert any("PR Output Routing must repeat that tier" in item for item in report.required_fixes)
    assert any("Gate A status" in item for item in report.required_fixes)
    assert any("Gate A checker passed" in item for item in report.advisory_warnings)


def test_agent_tool_metadata_mismatch_detects_claude_branch_with_codex_body() -> None:
    body = "\n".join(
        [
            "- Contributor ID: roman",
            "- GitHub username: gladunrv",
            "- Agent tool: Codex",
            "- Task ID / Proposal / Queue: TASK-CLOSEOUT",
            "- Branch: agent/roman/claude/closeout-merged-task-batch",
            "- Human reviewer: roman",
        ]
    )

    mismatch = agent_tool_metadata_mismatch(
        "agent/roman/claude/closeout-merged-task-batch",
        body,
    )

    assert mismatch is not None
    assert "expected `Claude Code`" in mismatch


def test_coauthor_trailer_is_advisory_only() -> None:
    hits = coauthor_trailer_advisory_hits(
        (
            "Co-authored-by: Claude <noreply@example.com>",
            "Regular line.",
        )
    )

    assert hits == (
        "Co-authored-by trailer detected; keep AI attribution in PR metadata "
        "and omit the trailer from the final squash merge body.",
    )


def test_build_review_report_keeps_coauthor_trailer_noise_advisory(
    tmp_path: Path,
) -> None:
    task_id = "TASK-0719"
    branch = "agent/roman/codex/task-0719-coauthor-trailer-advisory"
    changed = (f"tasks/{task_id}-coauthor-trailer-advisory.yaml",)
    _write_review_task(tmp_path, task_id, slug="coauthor-trailer-advisory")
    body = (
        _full_pr_body(task_ref=task_id, branch=branch)
        + "\n\nCo-authored-by: Claude <noreply@example.com>\n"
    )
    pr_metadata = PullRequestMetadata(
        number=719,
        title=f"{task_id}: Treat co-author trailer noise as advisory",
        body=body,
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
        patch("physics_lab.registry.maintainer_review.run_git_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "present")),
        patch(
            "physics_lab.registry.maintainer_review.run_task_validation",
            return_value=ValidationSummary(status="pass", failed_commands=()),
        ),
    ):
        report = build_review_report(tmp_path, pull_request=719)

    assert report.verdict == "MERGE_OK"
    assert report.blockers == ()
    assert report.required_fixes == ()
    assert any("Co-authored-by trailer detected" in item for item in report.advisory_warnings)


def test_missing_pr_template_sections_detects_short_pr_body() -> None:
    body = "\n".join(
        [
            "## Summary",
            "",
            "- Short body that bypasses the repository template.",
            "",
            "## Validation",
            "",
            "- python3 -m pytest",
        ]
    )

    assert missing_pr_template_sections(body) == (
        "PR Kind",
        "Primary Reference",
        "Branch Name",
        "PR Lifecycle",
        "Changed Files",
        "Linked Repository Memory",
        "Validation Commands",
        "Scientific Claim Impact",
        "Result Artifact Impact",
        "Agent / Contributor Metadata",
        "Maintainer Review Notes",
    )


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


def test_overclaim_hits_block_positive_claims_with_later_limitations() -> None:
    added_lines = (
        "The benchmark solved the anomaly without fitting.",
    )

    assert overclaim_hits(added_lines) == ("solved",)
    assert overclaim_advisory_hits(added_lines) == ()


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


def test_decision_regression_hits_flag_static_agent_state_layers() -> None:
    added_lines = (
        "Add campaigns/task-index.yaml as a generated static index for agents.",
        "Create a second source of truth for task routing.",
    )

    hits = decision_regression_advisory_hits(added_lines)

    assert any("campaign task-index" in item for item in hits)
    assert any("source-of-truth" in item for item in hits)


def test_decision_regression_hits_ignore_guardrail_context() -> None:
    added_lines = (
        "Do not add campaigns/task-index.yaml as a generated static index for agents.",
        "The postmortem says a second source of truth is redundant.",
    )

    assert decision_regression_advisory_hits(added_lines) == ()


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


def test_render_review_report_includes_advisory_quality_score() -> None:
    report = ReviewReport(
        verdict="MERGE_OK",
        risk="medium",
        task_id="TASK-0429",
        branch="agent/roman/codex/task-0429-review-agent-quality-score",
        changed_files=("physics_lab/registry/maintainer_review.py",),
        validation="pass",
        security_risks=("Repository scripts changed. Path: physics_lab/registry/maintainer_review.py",),
        blockers=(),
        required_fixes=(),
        recommended_action="Merge after GitHub CI is green.",
    )

    rendered = render_review_report(report)

    assert "Quality: 8/10" in rendered
    assert "Quality notes:" in rendered
    assert "- medium-risk change surface" in rendered
    assert "- security-sensitive paths need maintainer attention" in rendered


def test_run_task_validation_skips_self_referential_review_command(tmp_path) -> None:
    payload = {
        "validation": {
                "commands": [
                    "python3 scripts/apl_review_pr.py --branch agent/roman/codex/task-0034-maintainer-review-agent --task TASK-0034 || true",
                    f'"{sys.executable}" -c "print(123)"',
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


def test_run_task_validation_uses_active_python_for_python3_commands(tmp_path) -> None:
    payload = {
        "validation": {
            "commands": [
                "python3 -c \"print(456)\"",
            ]
        }
    }

    summary = run_task_validation(tmp_path, payload, enabled=True)

    assert summary.status == "pass"


def test_portable_validation_command_uses_active_python_for_python_launcher() -> None:
    assert _portable_validation_command("python -c \"print(456)\"").startswith(
        f'"{sys.executable}" '
    )


def test_ci_aware_validation_keeps_local_full_repo_pytest_slice() -> None:
    assert ci_aware_validation_command("python3 -m ruff check .") is None
    assert ci_aware_validation_command("python -m ruff check .") is None
    assert ci_aware_validation_command("python3 -m physics_lab.cli validate-repo .") is None
    assert ci_aware_validation_command("python -m physics_lab.cli validate-repo .") is None
    assert (
        ci_aware_validation_command(
            "python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings"
        )
        is None
    )
    assert (
        ci_aware_validation_command("python3 -m pytest")
        == "python3 -m pytest -m full_repo"
    )
    assert ci_aware_validation_command("python -m pytest") == "python -m pytest -m full_repo"
    assert (
        ci_aware_validation_command(
            "python3 -m pytest --basetemp=.pytest-basetemp-0619 tests/test_maintainer_review.py -q"
        )
        == "python3 -m pytest --basetemp=.pytest-basetemp-0619 tests/test_maintainer_review.py -q"
    )
    assert (
        ci_aware_validation_command(
            "python3 scripts/run_nuclear_local_curvature_lane.py --help"
        )
        == "python3 scripts/run_nuclear_local_curvature_lane.py --help"
    )


def test_run_task_validation_ci_aware_skips_ci_duplicates_but_runs_remainder(
    tmp_path,
) -> None:
    payload = {
        "validation": {
            "commands": [
                "python3 -m ruff check .",
                "python3 -m pytest",
                "python3 scripts/example_task_check.py",
                "python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings",
            ]
        }
    }
    seen_commands: list[str] = []

    def fake_run_command(command: str, **kwargs: object) -> CommandResult:
        del kwargs
        seen_commands.append(command)
        return CommandResult(returncode=0, stdout="", stderr="")

    with patch("physics_lab.registry.maintainer_review.run_command", fake_run_command):
        summary = run_task_validation(tmp_path, payload, enabled=True, ci_aware=True)

    assert summary.status == "pass"
    assert len(seen_commands) == 2
    assert any("-m full_repo" in command for command in seen_commands)
    assert any("scripts/example_task_check.py" in command for command in seen_commands)
    assert summary.skipped_commands == (
        "python3 -m ruff check .",
        "python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings",
    )


def test_portable_validation_command_uses_git_bash_for_repo_shell_script() -> None:
    with patch(
        "physics_lab.registry.maintainer_review._git_bash_path",
        return_value="C:/Program Files/Git/bin/bash.exe",
    ):
        command = _portable_validation_command("./scripts/apl_snapshot.sh")

    assert command == (
        '"C:/Program Files/Git/bin/bash.exe" -lc "./scripts/apl_snapshot.sh"'
    )


def test_portable_validation_command_leaves_complex_shell_commands_unchanged() -> None:
    command = _portable_validation_command("./scripts/apl_snapshot.sh --flag")

    assert command == "./scripts/apl_snapshot.sh --flag"


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


def test_prepare_clean_pr_worktree_fetches_remote_head(tmp_path: Path) -> None:
    branch = "agent/roman/codex/task-0094-fix-helper-stale-diff"
    metadata = PullRequestMetadata(
        number=104,
        title="TASK-0094: Track maintainer review helper stale diff false positives",
        body="",
        branch=branch,
        base_branch="main",
        state="OPEN",
        merged=False,
        status_checks_passed=True,
        status_checks_pending=False,
        changed_files=("tasks/TASK-0094-helper.yaml",),
        head_sha="1234567890abcdef",
    )
    commands: list[list[str]] = []

    def fake_run_git_command(
        args: list[str],
        *,
        cwd: Path,
        extra_safe_directories: tuple[Path, ...] = (),
        timeout: int = 60,
    ) -> CommandResult:
        del cwd, extra_safe_directories, timeout
        commands.append(args)
        return _EMPTY_DIFF

    with (
        patch(
            "physics_lab.registry.maintainer_review.run_git_command",
            side_effect=fake_run_git_command,
        ),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
    ):
        prepared = prepare_clean_pr_worktree(tmp_path, metadata)

    assert prepared.ready
    assert prepared.root == tmp_path / ".worktrees" / "_reviews" / "pr-104-1234567890ab"
    assert prepared.review_ref == "HEAD"
    assert commands[0] == [
        "fetch",
        "--no-tags",
        "origin",
        f"refs/heads/{branch}:refs/remotes/origin/{branch}",
    ]
    assert commands[1] == [
        "worktree",
        "add",
        "--detach",
        str(prepared.root),
        "1234567890abcdef",
    ]


def test_build_review_report_pr_uses_clean_remote_worktree_from_dirty_caller(
    tmp_path: Path,
) -> None:
    caller_root = tmp_path / "caller"
    clean_root = tmp_path / "clean-pr"
    caller_root.mkdir()
    clean_root.mkdir()
    _write_review_task(clean_root, "TASK-0094")
    branch = "agent/roman/codex/task-0094-fix-helper-stale-diff"
    pr_metadata = PullRequestMetadata(
        number=104,
        title="TASK-0094: Track maintainer review helper stale diff false positives",
        body=_full_pr_body(
            task_ref="TASK-0094",
            branch=branch,
            primary_reference="- Task ID: `TASK-0094`\n- Task File: `tasks/TASK-0094-helper.yaml`",
        ),
        branch=branch,
        base_branch="main",
        state="OPEN",
        merged=False,
        status_checks_passed=True,
        status_checks_pending=False,
        changed_files=("tasks/TASK-0094-helper.yaml",),
        head_sha="1234567890abcdef",
    )
    changed = ("tasks/TASK-0094-helper.yaml",)

    def fake_changed_files(root: Path, ref: str, **_: object) -> tuple[str, ...]:
        assert root == clean_root
        assert ref == "HEAD"
        return changed

    def fake_git_status_clean(root: Path, **_: object) -> bool:
        if root == caller_root:
            return False
        assert root == clean_root
        return True

    with (
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=pr_metadata),
        patch(
            "physics_lab.registry.maintainer_review.prepare_clean_pr_worktree",
            return_value=CleanPrWorktree(
                root=clean_root,
                review_ref="HEAD",
                ready=True,
                message="Reviewing from clean fixture worktree.",
            ),
        ),
        patch("physics_lab.registry.maintainer_review.current_branch", return_value=""),
        patch(
            "physics_lab.registry.maintainer_review.local_branch_exists",
            side_effect=AssertionError("clean PR worktree must not require a local branch"),
        ),
        patch("physics_lab.registry.maintainer_review.changed_files_vs_main", side_effect=fake_changed_files),
        patch("physics_lab.registry.maintainer_review.git_status_clean", side_effect=fake_git_status_clean),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "missing")),
        patch(
            "physics_lab.registry.maintainer_review.run_task_validation",
            return_value=ValidationSummary(status="pass", failed_commands=()),
        ) as validation_mock,
    ):
        report = build_review_report(caller_root, pull_request=104)

    assert report.verdict == "MERGE_OK"
    assert report.branch == branch
    assert validation_mock.call_args.args[0] == clean_root
    assert validation_mock.call_args.kwargs["enabled"] is True
    assert any("clean fixture worktree" in item for item in report.advisory_warnings)
    assert any("Review bundle generation was skipped" in item for item in report.advisory_warnings)


def test_build_review_report_pr_metadata_failure_has_fallback_diagnostic(
    tmp_path: Path,
) -> None:
    with (
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=None),
        patch(
            "physics_lab.registry.maintainer_review.current_branch",
            side_effect=AssertionError("metadata failure must not inspect current checkout"),
        ),
        patch(
            "physics_lab.registry.maintainer_review.changed_files_vs_main",
            side_effect=AssertionError("metadata failure must not diff current checkout"),
        ),
    ):
        report = build_review_report(tmp_path, pull_request=104)

    assert report.verdict == "BLOCKED"
    assert report.branch == "PR-104-UNRESOLVED"
    assert report.changed_files == ()
    assert any("intentionally did not review the current checkout" in item for item in report.blockers)
    assert any("Fallback commands" in item for item in report.blockers)


def test_build_review_report_allows_explicit_local_pr_ref_review(
    tmp_path: Path,
) -> None:
    _write_review_task(tmp_path, "TASK-0104")
    task_path = "tasks/TASK-0104-helper.yaml"
    clean_root = tmp_path / ".worktrees" / "_reviews" / "origin-pr-104-abc123"
    clean_root.mkdir(parents=True)
    _write_review_task(clean_root, "TASK-0104")

    def fake_changed_files(root: Path, ref: str, **_: object) -> tuple[str, ...]:
        assert root == clean_root
        assert ref == "HEAD"
        return (task_path,)

    with (
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=None),
        patch("physics_lab.registry.maintainer_review.current_branch", return_value="main"),
        patch(
            "physics_lab.registry.maintainer_review.prepare_clean_local_ref_worktree",
            return_value=CleanPrWorktree(
                root=clean_root,
                review_ref="HEAD",
                ready=True,
                message="Reviewing local PR ref from clean fixture worktree.",
            ),
        ) as worktree_mock,
        patch(
            "physics_lab.registry.maintainer_review.local_branch_exists",
            side_effect=AssertionError("local PR refs must not require local canonical branches"),
        ),
        patch("physics_lab.registry.maintainer_review.changed_files_vs_main", side_effect=fake_changed_files),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "missing")),
        patch(
            "physics_lab.registry.maintainer_review.run_task_validation",
            return_value=ValidationSummary(status="pass", failed_commands=()),
        ),
    ):
        report = build_review_report(
            tmp_path,
            branch="origin/pr-104",
            task_id="TASK-0104",
            validation_mode="strict",
        )

    assert report.verdict == "MERGE_OK"
    assert report.branch == "origin/pr-104"
    assert report.changed_files == (task_path,)
    worktree_mock.assert_called_once_with(tmp_path, "origin/pr-104")
    assert any("fetched local PR ref" in item for item in report.advisory_warnings)


def test_load_pr_metadata_falls_back_to_pr_list_when_view_fails(tmp_path: Path) -> None:
    payload = json.dumps(
        [
            {
                "number": 104,
                "title": "TASK-0104: Fixture",
                "headRefName": "agent/roman/codex/task-0104-fixture",
                "headRefOid": "abc123",
                "baseRefName": "main",
                "state": "MERGED",
                "mergedAt": "2026-06-07T00:00:00Z",
                "statusCheckRollup": [
                    {"conclusion": "SUCCESS", "status": "COMPLETED"},
                ],
            }
        ]
    )

    def fake_run_command(command, *, cwd, shell=False, timeout=60):  # noqa: ARG001
        if command[1:3] == ["pr", "view"]:
            return CommandResult(returncode=1, stdout="", stderr="network")
        if command[1:3] == ["pr", "list"]:
            return CommandResult(returncode=0, stdout=payload, stderr="")
        return CommandResult(returncode=1, stdout="", stderr="unexpected")

    with (
        patch("physics_lab.registry.maintainer_review.find_gh_path", return_value="/custom/gh"),
        patch("physics_lab.registry.maintainer_review.run_command", side_effect=fake_run_command),
    ):
        metadata = load_pr_metadata(tmp_path, 104)

    assert metadata is not None
    assert metadata.number == 104
    assert metadata.merged is True
    assert metadata.status_checks_passed is True


def test_build_review_report_multi_proposal_pr_is_not_blocked(tmp_path: Path) -> None:
    """A PR with multiple proposal files must run proposal-level validation."""
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

    validation_payloads: list[dict[str, object]] = []

    def fake_validation(
        _root: Path,
        payload: dict[str, object],
        *,
        enabled: bool,
        **_kwargs: object,
    ) -> ValidationSummary:
        validation_payloads.append(payload)
        assert enabled
        commands = tuple(payload.get("validation", {}).get("commands", ()))  # type: ignore[union-attr]
        assert "python3 -m physics_lab.cli validate-repo ." in commands
        assert (
            "python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings"
            in commands
        )
        return ValidationSummary(status="pass", failed_commands=())

    with (
        patch("physics_lab.registry.maintainer_review.current_branch", return_value=branch),
        patch("physics_lab.registry.maintainer_review.local_branch_exists", return_value=True),
        patch("physics_lab.registry.maintainer_review.changed_files_vs_main", return_value=changed),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "present")),
        patch("physics_lab.registry.maintainer_review.run_task_validation", side_effect=fake_validation),
    ):
        report = build_review_report(tmp_path, branch=branch)

    assert validation_payloads
    assert report.verdict == "MERGE_OK"
    assert not any("multiple" in b.lower() and "proposal" in b.lower() for b in report.blockers), (
        f"Unexpected multi-proposal blocker: {report.blockers}"
    )
    assert "Validation commands were not executed during this review run." not in report.required_fixes


def test_build_review_report_allows_explicit_proposal_triage_supersede(
    tmp_path: Path,
) -> None:
    clean_root = tmp_path / "clean-pr"
    proposal_path = "tasks/proposals/20260531-roman-old-coordination.yaml"
    (clean_root / "tasks" / "proposals").mkdir(parents=True)
    (clean_root / proposal_path).write_text(
        _PROPOSAL_YAML.format(proposal_id="20260531-roman-old-coordination").replace(
            "status: PROPOSED",
            "status: SUPERSEDED",
        ).replace(
            "decision: pending",
            "decision: superseded",
        ),
        encoding="utf-8",
    )
    branch = "agent/roman/codex/propose-task-supersede-old-coordination"
    pr_metadata = PullRequestMetadata(
        number=1032,
        title="TASK-PROPOSAL: Supersede stale task coordination proposal",
        body=_full_pr_body(
            task_ref="TASK-PROPOSAL",
            branch=branch,
            kind="Task proposal PR",
            primary_reference=(
                "- Task ID: `TASK-PROPOSAL`\n"
                "- Proposal File: `tasks/proposals/20260531-roman-old-coordination.yaml`\n"
                "- Proposal superseded during proposal triage."
            ),
        ),
        branch=branch,
        base_branch="main",
        state="OPEN",
        merged=False,
        status_checks_passed=True,
        status_checks_pending=False,
        changed_files=(proposal_path,),
        head_sha="abc123456789",
    )

    with (
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=pr_metadata),
        patch(
            "physics_lab.registry.maintainer_review.prepare_clean_pr_worktree",
            return_value=CleanPrWorktree(
                root=clean_root,
                review_ref="HEAD",
                ready=True,
                message="Reviewing from clean fixture worktree.",
            ),
        ),
        patch("physics_lab.registry.maintainer_review.current_branch", return_value=""),
        patch("physics_lab.registry.maintainer_review.changed_files_vs_main", return_value=(proposal_path,)),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "present")),
        patch(
            "physics_lab.registry.maintainer_review.run_task_validation",
            return_value=ValidationSummary(status="pass", failed_commands=()),
        ),
    ):
        report = build_review_report(tmp_path, pull_request=1032)

    assert report.verdict == "MERGE_OK"
    assert not any("status is SUPERSEDED" in item for item in report.required_fixes)


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
        body=_full_pr_body(
            task_ref="TASK-CLOSEOUT",
            branch=branch,
            kind="Task closeout PR",
            primary_reference="- Closed Task Files: `tasks/TASK-0027-units.yaml`, `tasks/TASK-0062-roadmap.yaml`",
        ),
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


def test_build_review_report_requires_agent_tool_to_match_branch_agent(
    tmp_path: Path,
) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "ACTIVE.md").write_text("# active board\n", encoding="utf-8")
    (tasks_dir / "TASK-0027-units.yaml").write_text(
        "\n".join(
            [
                "id: TASK-0027",
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

    branch = "agent/roman/claude/closeout-confirmed-merged-tasks"
    changed = ("tasks/TASK-0027-units.yaml",)
    pr_metadata = PullRequestMetadata(
        number=67,
        title="TASK-CLOSEOUT: Mark confirmed merged tasks as done",
        body=_full_pr_body(
            task_ref="TASK-CLOSEOUT",
            branch=branch,
            kind="Task closeout PR",
            primary_reference="- Closed Task Files: `tasks/TASK-0027-units.yaml`",
        ),
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

    assert report.verdict == "NEEDS_CHANGES"
    assert any("expected `Claude Code`" in item for item in report.required_fixes)


def test_build_review_report_closeout_pr_may_unblock_dependent_task(
    tmp_path: Path,
) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "ACTIVE.md").write_text("# active board\n", encoding="utf-8")

    (tasks_dir / "TASK-0027-units.yaml").write_text(
        "\n".join(
            [
                "id: TASK-0027",
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
    (tasks_dir / "TASK-0204-adversarial-review.yaml").write_text(
        "\n".join(
            [
                "id: TASK-0204",
                'title: "Unblocked dependent task"',
                "type: scientific_audit",
                "status: READY",
                "difficulty: medium",
                "priority: high",
                "strategy_alignment:",
                '  - "Closeout may unblock dependent review work"',
                "input:",
                "  mode: workflow",
                '  related_domain: "testing"',
                "  related_objects: []",
                '  planning_context: "Unblock fixture"',
                "requirements:",
                '  - "Review after closeout"',
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
    (tasks_dir / "TASK-0099-stale.yaml").write_text(
        "\n".join(
            [
                "id: TASK-0099",
                'title: "Stale task"',
                "type: documentation",
                "status: REJECTED",
                "difficulty: low",
                "priority: medium",
                "strategy_alignment:",
                '  - "Close stale task when maintainer approves cleanup"',
                "input:",
                "  mode: workflow",
                '  related_domain: "testing"',
                "  related_objects: []",
                '  planning_context: "Stale closeout fixture"',
                "requirements:",
                '  - "No longer relevant"',
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
        "tasks/TASK-0099-stale.yaml",
        "tasks/TASK-0027-units.yaml",
        "tasks/TASK-0204-adversarial-review.yaml",
    )
    pr_metadata = PullRequestMetadata(
        number=67,
        title="TASK-CLOSEOUT: Mark confirmed merged tasks done and unblock TASK-0204",
        body=_full_pr_body(
            task_ref="TASK-CLOSEOUT",
            branch=branch,
            kind="Task closeout PR",
            primary_reference=(
                "- Closed Task Files: `tasks/TASK-0027-units.yaml`\n"
                "- Unblocked Task Files: `tasks/TASK-0204-adversarial-review.yaml`"
                "\n- Stale Task Files: `tasks/TASK-0099-stale.yaml`"
            ),
        ),
        branch=branch,
        base_branch="main",
        state="OPEN",
        merged=False,
        status_checks_passed=True,
        status_checks_pending=False,
        changed_files=changed,
    )

    def fake_run_command(command: list[str] | str, **_: object) -> CommandResult:
        if (
            isinstance(command, list)
            and len(command) >= 3
            and command[:2] == ["git", "show"]
            and "TASK-0204-adversarial-review.yaml" in command[2]
        ):
            return CommandResult(
                returncode=0,
                stdout="\n".join(
                    [
                        "id: TASK-0204",
                        'title: "Unblocked dependent task"',
                        "type: scientific_audit",
                        "status: BLOCKED",
                    ]
                ),
                stderr="",
            )
        return _EMPTY_DIFF

    with (
        patch("physics_lab.registry.maintainer_review.current_branch", return_value=branch),
        patch("physics_lab.registry.maintainer_review.local_branch_exists", return_value=True),
        patch("physics_lab.registry.maintainer_review.changed_files_vs_main", return_value=changed),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=pr_metadata),
        patch("physics_lab.registry.maintainer_review.run_command", side_effect=fake_run_command),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "present")),
        patch(
            "physics_lab.registry.maintainer_review.run_task_validation",
            return_value=ValidationSummary(status="pass", failed_commands=()),
        ),
    ):
        report = build_review_report(tmp_path, pull_request=67)

    assert report.task_id == "TASK-CLOSEOUT"
    assert report.verdict == "MERGE_OK"
    assert report.required_fixes == ()


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
        body=_full_pr_body(
            task_ref="TASK-CLOSEOUT",
            branch=branch,
            kind="Task closeout PR",
            primary_reference="- Closed Task Files: `tasks/TASK-0027-units.yaml`, `tasks/TASK-0062-roadmap.yaml`",
        ),
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


def test_build_review_report_closeout_short_body_needs_changes_even_with_green_ci(
    tmp_path: Path,
) -> None:
    _write_review_task(tmp_path, "TASK-0027", status="DONE", slug="units")
    tasks_dir = tmp_path / "tasks"
    (tasks_dir / "ACTIVE.md").write_text("# active board\n", encoding="utf-8")
    branch = "agent/roman/codex/closeout-confirmed-merged-tasks"
    changed = ("tasks/ACTIVE.md", "tasks/TASK-0027-units.yaml")
    pr_metadata = PullRequestMetadata(
        number=68,
        title="TASK-CLOSEOUT: Mark confirmed merged tasks as done",
        body="## Summary\n\nShort closeout body.\n",
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
        report = build_review_report(tmp_path, pull_request=68)

    assert report.verdict == "NEEDS_CHANGES"
    assert any("repository-template sections" in item for item in report.required_fixes)


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
        body=_full_pr_body(
            task_ref="TASK-CLOSEOUT",
            branch=branch,
            kind="Task closeout PR",
            primary_reference="- Closed Task Files: `tasks/TASK-0027-units.yaml`, `tasks/TASK-0062-roadmap.yaml`",
        ),
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


def test_build_review_report_accepts_task_queue_pr_with_ready_future_task(
    tmp_path: Path,
) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "ACTIVE.md").write_text("# active board\n", encoding="utf-8")
    (tasks_dir / "TASK-0999-future-coverage-audit.yaml").write_text(
        "\n".join(
            [
                "id: TASK-0999",
                'title: "Future coverage audit"',
                "type: test_infrastructure",
                "status: READY",
                "difficulty: medium",
                "priority: medium",
                "strategy_alignment:",
                '  - "Task queue regression fixture"',
                "input:",
                "  mode: workflow",
                '  related_domain: "testing"',
                "  related_objects: []",
                '  planning_context: "Future task fixture"',
                "requirements:",
                '  - "Keep future task READY in task-queue PR"',
                "accepted_outputs:",
                '  - "future implementation"',
                "validation:",
                "  commands:",
                '    - "python3 -m physics_lab.cli validate-repo ."',
                "can_be_done_by: [human]",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    branch = "agent/roman/codex/task-queue-coverage-audit"
    changed = (
        "docs/agent-task-protocol.md",
        "docs/task-views/research.md",
        "docs/task-views/support.md",
        "docs/task-views/release.md",
        "docs/task-views/watchlist.md",
        "docs/task-views/blocked.md",
        "tasks/ACTIVE.md",
        "tasks/TASK-0999-future-coverage-audit.yaml",
    )
    pr_metadata = PullRequestMetadata(
        number=172,
        title="TASK-QUEUE: Add coverage audit task",
        body=_full_pr_body(
            task_ref="TASK-QUEUE",
            branch=branch,
            kind="Canonical task PR",
            primary_reference="- Task ID: `TASK-QUEUE`",
        ),
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
        report = build_review_report(tmp_path, pull_request=172)

    assert report.task_id == "TASK-QUEUE"
    assert report.verdict == "MERGE_OK"
    assert report.blockers == ()
    assert not any("REVIEW_READY" in item for item in report.required_fixes)
    assert not any("Accepted outputs" in item for item in report.required_fixes)
    assert any(
        "TASK-QUEUE PR includes generated task navigation" in item
        for item in report.advisory_warnings
    )


def test_build_review_report_accepts_task_queue_pr_without_generated_navigation(
    tmp_path: Path,
) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "ACTIVE.md").write_text("# active board\n", encoding="utf-8")
    (tasks_dir / "TASK-0999-future-coverage-audit.yaml").write_text(
        "\n".join(
            [
                "id: TASK-0999",
                'title: "Future coverage audit"',
                "type: test_infrastructure",
                "status: READY",
                "difficulty: medium",
                "priority: medium",
                "strategy_alignment:",
                '  - "Task queue regression fixture"',
                "input:",
                "  mode: workflow",
                '  related_domain: "testing"',
                "  related_objects: []",
                '  planning_context: "Future task fixture"',
                "requirements:",
                '  - "Keep future task READY in task-queue PR"',
                "accepted_outputs:",
                '  - "future implementation"',
                "validation:",
                "  commands:",
                '    - "python3 -m physics_lab.cli validate-repo ."',
                "can_be_done_by: [human]",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    branch = "agent/roman/codex/task-queue-coverage-audit"
    changed = ("tasks/TASK-0999-future-coverage-audit.yaml",)
    pr_metadata = PullRequestMetadata(
        number=175,
        title="TASK-QUEUE: Add coverage audit task",
        body=_full_pr_body(
            task_ref="TASK-QUEUE",
            branch=branch,
            kind="Canonical task PR",
            primary_reference="- Task ID: `TASK-QUEUE`",
        ),
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
        report = build_review_report(tmp_path, pull_request=175)

    assert report.task_id == "TASK-QUEUE"
    assert report.verdict == "MERGE_OK"
    assert report.blockers == ()
    assert not any("sync tasks/ACTIVE.md" in item for item in report.required_fixes)
    assert not any("sync docs/task-views" in item for item in report.required_fixes)
    assert not any(
        "generated task navigation" in item for item in report.advisory_warnings
    )


def test_build_review_report_blocks_task_queue_pr_that_changes_results(
    tmp_path: Path,
) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "ACTIVE.md").write_text("# active board\n", encoding="utf-8")
    (tasks_dir / "TASK-0999-future-coverage-audit.yaml").write_text(
        "\n".join(
            [
                "id: TASK-0999",
                'title: "Future coverage audit"',
                "type: test_infrastructure",
                "status: READY",
                "difficulty: medium",
                "priority: medium",
                "strategy_alignment:",
                '  - "Task queue regression fixture"',
                "input:",
                "  mode: workflow",
                '  related_domain: "testing"',
                "  related_objects: []",
                '  planning_context: "Future task fixture"',
                "requirements:",
                '  - "Keep future task READY in task-queue PR"',
                "accepted_outputs:",
                '  - "future implementation"',
                "validation:",
                "  commands:",
                '    - "python3 -m physics_lab.cli validate-repo ."',
                "can_be_done_by: [human]",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    branch = "agent/roman/codex/task-queue-coverage-audit"
    changed = (
        "tasks/ACTIVE.md",
        "tasks/TASK-0999-future-coverage-audit.yaml",
        "results/EXP-0001/RUN-0001/result.yaml",
    )
    pr_metadata = PullRequestMetadata(
        number=173,
        title="TASK-QUEUE: Add coverage audit task",
        body="\n".join(
            [
                "- Contributor ID: roman",
                "- GitHub username: gladunrv",
                "- Agent tool: codex",
                "- Task ID: TASK-QUEUE",
                "- Branch: agent/roman/codex/task-queue-coverage-audit",
                "- Human reviewer: roman",
            ]
        ),
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
        report = build_review_report(tmp_path, pull_request=173)

    assert report.verdict == "BLOCKED"
    assert any(
        "TASK-QUEUE PR must not change canonical scientific artifacts" in item
        for item in report.blockers
    )


def test_build_review_report_task_queue_wrong_title_needs_changes(
    tmp_path: Path,
) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "ACTIVE.md").write_text("# active board\n", encoding="utf-8")
    _write_review_task(tmp_path, "TASK-0999", status="READY", slug="future-coverage-audit")
    branch = "agent/roman/codex/task-queue-coverage-audit"
    changed = (
        "tasks/ACTIVE.md",
        "tasks/TASK-0999-future-coverage-audit.yaml",
    )
    pr_metadata = PullRequestMetadata(
        number=174,
        title="TASK-0999: Add coverage audit task",
        body=_full_pr_body(
            task_ref="TASK-QUEUE",
            branch=branch,
            kind="Canonical task PR",
            primary_reference="- Task ID: `TASK-QUEUE`",
        ),
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
        report = build_review_report(tmp_path, pull_request=174)

    assert report.verdict == "NEEDS_CHANGES"
    assert any("TASK-QUEUE" in item for item in report.required_fixes)
    assert report.blockers == ()


def test_build_review_report_redirects_queue_shaped_canonical_pr(
    tmp_path: Path,
) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True)
    _write_review_task(tmp_path, "TASK-0999", status="READY", slug="future-coverage-audit")
    branch = "agent/roman/codex/task-0999-coverage-audit"
    changed = ("tasks/TASK-0999-future-coverage-audit.yaml",)
    pr_metadata = PullRequestMetadata(
        number=176,
        title="TASK-0999: Add coverage audit task",
        body=_full_pr_body(
            task_ref="TASK-0999",
            branch=branch,
            kind="Canonical task PR",
            primary_reference="- Task ID: `TASK-0999`",
        ),
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
        report = build_review_report(tmp_path, pull_request=176)

    assert report.verdict == "NEEDS_CHANGES"
    assert any("TASK-QUEUE" in item for item in report.required_fixes)
    assert not any("Set it to REVIEW_READY" in item for item in report.required_fixes)
    assert report.blockers == ()


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
        body=_full_pr_body(
            task_ref="TASK-0094",
            branch="agent/roman/codex/task-0094-fix-helper-stale-diff",
            primary_reference="- Task ID: `TASK-0094`\n- Task File: `tasks/TASK-0094-helper.yaml`",
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


def test_build_review_report_requires_repository_pr_template_sections(tmp_path: Path) -> None:
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
    branch = "agent/roman/codex/task-0094-fix-helper-stale-diff"
    pr_metadata = PullRequestMetadata(
        number=104,
        title="TASK-0094: Track maintainer review helper stale diff false positives",
        body="## Summary\n\n- Short body.\n\n## Validation\n\n- pytest",
        branch=branch,
        base_branch="main",
        state="OPEN",
        merged=False,
        status_checks_passed=True,
        status_checks_pending=False,
        changed_files=("tasks/TASK-0094-helper.yaml",),
    )

    with (
        patch("physics_lab.registry.maintainer_review.current_branch", return_value=branch),
        patch("physics_lab.registry.maintainer_review.local_branch_exists", return_value=True),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch("physics_lab.registry.maintainer_review.changed_files_vs_main", return_value=("tasks/TASK-0094-helper.yaml",)),
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=pr_metadata),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "present")),
        patch(
            "physics_lab.registry.maintainer_review.run_task_validation",
            return_value=ValidationSummary(status="pass", failed_commands=()),
        ),
    ):
        report = build_review_report(tmp_path, pull_request=104)

    assert report.verdict == "NEEDS_CHANGES"
    assert any("PR body is missing required repository-template sections" in item for item in report.required_fixes)


def test_build_review_report_blocks_explicit_task_id_branch_mismatch(tmp_path: Path) -> None:
    _write_review_task(tmp_path, "TASK-0095")
    branch = "agent/roman/codex/task-0094-fix-helper-stale-diff"
    pr_metadata = PullRequestMetadata(
        number=105,
        title="TASK-0095: Track maintainer review helper stale diff false positives",
        body=_full_pr_body(
            task_ref="TASK-0095",
            branch=branch,
            primary_reference="- Task ID: `TASK-0095`\n- Task File: `tasks/TASK-0095-helper.yaml`",
        ),
        branch=branch,
        base_branch="main",
        state="OPEN",
        merged=False,
        status_checks_passed=True,
        status_checks_pending=False,
        changed_files=("tasks/TASK-0095-helper.yaml",),
    )

    with (
        patch("physics_lab.registry.maintainer_review.current_branch", return_value=branch),
        patch("physics_lab.registry.maintainer_review.local_branch_exists", return_value=True),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch("physics_lab.registry.maintainer_review.changed_files_vs_main", return_value=("tasks/TASK-0095-helper.yaml",)),
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=pr_metadata),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "present")),
        patch(
            "physics_lab.registry.maintainer_review.run_task_validation",
            return_value=ValidationSummary(status="pass", failed_commands=()),
        ),
    ):
        report = build_review_report(tmp_path, pull_request=105, task_id="TASK-0095")

    assert report.verdict == "BLOCKED"
    assert any("does not match branch task id" in item for item in report.blockers)


def test_build_review_report_branch_only_keeps_missing_pr_body_advisory(
    tmp_path: Path,
) -> None:
    _write_review_task(tmp_path, "TASK-0094")
    branch = "agent/roman/codex/task-0094-fix-helper-stale-diff"

    with (
        patch("physics_lab.registry.maintainer_review.current_branch", return_value=branch),
        patch("physics_lab.registry.maintainer_review.local_branch_exists", return_value=True),
        patch("physics_lab.registry.maintainer_review.git_status_clean", return_value=True),
        patch("physics_lab.registry.maintainer_review.changed_files_vs_main", return_value=("tasks/TASK-0094-helper.yaml",)),
        patch("physics_lab.registry.maintainer_review.load_pr_metadata", return_value=None),
        patch("physics_lab.registry.maintainer_review.run_command", return_value=_EMPTY_DIFF),
        patch(
            "physics_lab.registry.maintainer_review.prepare_clean_pr_worktree",
            side_effect=AssertionError("branch-only review should stay local"),
        ),
        patch("physics_lab.registry.maintainer_review.ensure_review_bundle", return_value=(None, "present")),
        patch(
            "physics_lab.registry.maintainer_review.run_task_validation",
            return_value=ValidationSummary(status="pass", failed_commands=()),
        ),
    ):
        report = build_review_report(tmp_path, branch=branch)

    assert report.verdict == "MERGE_OK"
    assert report.risk == "low"
    assert report.required_fixes == ()
    assert any("Branch-only review cannot validate" in item for item in report.advisory_warnings)


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
        body=_full_pr_body(
            task_ref="microtask(PMR-001)",
            branch="agent/roman/codex/microtask-PMR-001-koide-methodology-note",
            kind="Microtask PR",
            primary_reference="- Queue ID: `particle-mass-relations`\n- Queue File: `tasks/microtasks/particle-mass-relations.yaml`\n- Microtask IDs: `PMR-001`",
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
        body=_full_pr_body(
            task_ref="microtask(dimensional-analysis-validator)",
            branch="agent/roman/codex/microtask-batch-dimensional-analysis-validator--challenge-entries",
            kind="Microtask PR",
            primary_reference="- Queue ID: `dimensional-analysis-validator`\n- Queue File: `tasks/microtasks/dimensional-analysis-validator.yaml`\n- Microtask IDs: `DAV-003, DAV-004, DAV-008`",
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


def test_finish_gate_marks_ready_after_merge_ok_and_green_ci(tmp_path: Path) -> None:
    ci_gate = CiGate(
        status="pass",
        checks=(CheckState(name="Python fast tests", bucket="pass", state="SUCCESS", link=""),),
        failures=(),
        pending=(),
    )

    with (
        patch(
            "physics_lab.registry.pr_finish_gate.run_review_gate",
            return_value=CommandResult(returncode=0, stdout="Verdict: MERGE_OK\n", stderr=""),
        ),
        patch("physics_lab.registry.pr_finish_gate.load_ci_gate", return_value=ci_gate),
        patch(
            "physics_lab.registry.pr_finish_gate.mark_ready",
            return_value=CommandResult(returncode=0, stdout="ready\n", stderr=""),
        ) as ready,
    ):
        report = finish_pr(tmp_path, 101)

    assert report.ok
    assert report.status == "ready_marked"
    assert report.review_verdict == "MERGE_OK"
    assert report.ci_status == "pass"
    ready.assert_called_once()


def test_finish_gate_blocks_ready_transition_when_ci_fails(tmp_path: Path) -> None:
    failing_check = CheckState(
        name="Python fast tests",
        bucket="fail",
        state="FAILURE",
        link="https://github.com/open-agent-science/autonomous-physics-lab/actions/runs/123/job/456",
    )
    ci_gate = CiGate(
        status="fail",
        checks=(failing_check,),
        failures=(failing_check,),
        pending=(),
    )

    with (
        patch(
            "physics_lab.registry.pr_finish_gate.run_review_gate",
            return_value=CommandResult(returncode=0, stdout="Verdict: MERGE_OK\n", stderr=""),
        ),
        patch("physics_lab.registry.pr_finish_gate.load_ci_gate", return_value=ci_gate),
        patch("physics_lab.registry.pr_finish_gate.mark_ready") as ready,
    ):
        report = finish_pr(tmp_path, 102)

    rendered = render_finish_gate_report(report, pr_number=102)
    assert not report.ok
    assert report.status == "blocked"
    assert report.ready_transition == "not_attempted"
    assert report.next_safe_command == "gh run view 123 --log-failed"
    assert "Python fast tests" in rendered
    assert "https://github.com/open-agent-science/autonomous-physics-lab/actions/runs/123/job/456" in rendered
    ready.assert_not_called()


def test_finish_gate_leaves_draft_when_review_blocks(tmp_path: Path) -> None:
    with (
        patch(
            "physics_lab.registry.pr_finish_gate.run_review_gate",
            return_value=CommandResult(returncode=0, stdout="Verdict: BLOCKED\n", stderr=""),
        ),
        patch("physics_lab.registry.pr_finish_gate.load_ci_gate") as ci_gate,
        patch("physics_lab.registry.pr_finish_gate.mark_ready") as ready,
    ):
        report = finish_pr(tmp_path, 103)

    assert not report.ok
    assert report.review_verdict == "BLOCKED"
    assert report.ci_status == "not_checked"
    assert report.next_safe_command == "python3 scripts/apl_review_pr.py --pr 103"
    ci_gate.assert_not_called()
    ready.assert_not_called()


def _init_review_gc_repo(tmp_path: Path) -> Path:
    """Create a minimal real git repo for review-worktree self-cleanup tests."""
    import shutil
    import subprocess

    if shutil.which("git") is None:  # pragma: no cover - environment guard
        import pytest

        pytest.skip("git is required for review-worktree self-cleanup tests")

    def _git(*args: str) -> None:
        subprocess.run(
            ["git", *args], cwd=repo, check=True, capture_output=True, text=True
        )

    repo = tmp_path / "repo"
    repo.mkdir()
    _git("init", "-b", "main")
    _git("config", "user.email", "test@example.com")
    _git("config", "user.name", "Test Runner")
    (repo / ".gitignore").write_text(".worktrees/\n", encoding="utf-8")
    _git("add", ".gitignore")
    _git("commit", "-m", "init")
    return repo


def _add_detached_review_worktree(repo: Path, name: str) -> Path:
    import subprocess

    from physics_lab.registry.review_worktree_gc import review_worktrees_root

    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()
    path = review_worktrees_root(repo) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(path), head],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return path


def test_build_review_report_tears_down_own_review_worktree(tmp_path: Path) -> None:
    repo = _init_review_gc_repo(tmp_path)
    created = _add_detached_review_worktree(repo, "pr-42-self00000000")
    assert created.exists()

    dummy = ReviewReport(
        verdict="MERGE_OK",
        risk="low",
        task_id="TASK-0001",
        branch="main",
        changed_files=(),
        validation="pass",
        security_risks=(),
        blockers=(),
        required_fixes=(),
        recommended_action="Merge.",
    )

    def fake_compose(root, *, worktree_sink=None, **kwargs):  # noqa: ANN001, ANN003
        # Simulate a review run that created a clean PR worktree.
        if worktree_sink is not None:
            worktree_sink.append(created)
        return dummy

    with patch(
        "physics_lab.registry.maintainer_review._compose_review_report",
        side_effect=fake_compose,
    ):
        report = build_review_report(repo, branch="main", task_id="TASK-0001")

    assert report.verdict == "MERGE_OK"
    # Layer 1: the worktree this run created must be gone afterward.
    assert not created.exists()


def test_build_review_report_self_cleanup_runs_even_on_exception(tmp_path: Path) -> None:
    repo = _init_review_gc_repo(tmp_path)
    created = _add_detached_review_worktree(repo, "pr-43-boom00000000")

    def boom(root, *, worktree_sink=None, **kwargs):  # noqa: ANN001, ANN003
        if worktree_sink is not None:
            worktree_sink.append(created)
        raise RuntimeError("review blew up mid-run")

    with patch(
        "physics_lab.registry.maintainer_review._compose_review_report",
        side_effect=boom,
    ):
        try:
            build_review_report(repo, branch="main", task_id="TASK-0001")
        except RuntimeError:
            pass

    # finally must still tear the worktree down on the exception path.
    assert not created.exists()


def test_build_review_report_startup_janitor_reclaims_old_worktree(tmp_path: Path) -> None:
    import os
    import time

    repo = _init_review_gc_repo(tmp_path)
    stale = _add_detached_review_worktree(repo, "pr-44-stale0000000")
    old = time.time() - 100 * 3600.0
    os.utime(stale, (old, old))

    dummy = ReviewReport(
        verdict="MERGE_OK",
        risk="low",
        task_id="TASK-0001",
        branch="main",
        changed_files=(),
        validation="pass",
        security_risks=(),
        blockers=(),
        required_fixes=(),
        recommended_action="Merge.",
    )

    with patch(
        "physics_lab.registry.maintainer_review._compose_review_report",
        return_value=dummy,
    ):
        build_review_report(repo, branch="main", task_id="TASK-0001")

    # Layer 2: the abandoned >48h detached review worktree is reclaimed.
    assert not stale.exists()
