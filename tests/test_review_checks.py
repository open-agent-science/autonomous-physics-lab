"""Tests for accepted-output parsing in review_checks (TASK-0466, F4)."""

from __future__ import annotations

from physics_lab.registry.review_checks import (
    cross_platform_advisory_hits,
    cross_platform_surface_hits,
    follow_up_task_advisory_hits,
    normalize_output_path,
    novelty_classification,
    output_paths,
)


def test_novelty_classification_extracts_declared_class() -> None:
    body = "## Novelty Classification\n\nNovelty Classification: calibration_known_physics\n"
    assert novelty_classification(body) == "calibration_known_physics"


def test_novelty_classification_accepts_inline_and_backticked() -> None:
    assert (
        novelty_classification("novelty classification = `frontier_novel`")
        == "frontier_novel"
    )
    assert novelty_classification("Novelty Classification: reusable_dataset") == "reusable_dataset"


def test_novelty_classification_returns_none_when_absent_or_unknown() -> None:
    assert novelty_classification("no declaration here") is None
    assert novelty_classification("") is None
    assert novelty_classification(None) is None
    assert novelty_classification("Novelty Classification: not_a_real_class") is None


def test_novelty_classification_rejects_template_choice_list() -> None:
    backticked_choice_list = (
        "- Novelty Classification: `frontier_novel` / `reusable_dataset` / "
        "`valuable_negative` / `calibration_known_physics` / `n/a`"
    )
    angle_bracket_choice_list = (
        "- Novelty Classification: <frontier_novel | reusable_dataset | "
        "valuable_negative | calibration_known_physics | n/a>"
    )
    assert novelty_classification(backticked_choice_list) is None
    assert novelty_classification(angle_bracket_choice_list) is None


def test_normalize_output_path_returns_bare_path() -> None:
    assert normalize_output_path("docs/foo.md") == "docs/foo.md"


def test_normalize_output_path_strips_backticks() -> None:
    assert normalize_output_path("`docs/foo.md`") == "docs/foo.md"


def test_normalize_output_path_handles_updated_prefix() -> None:
    assert normalize_output_path("updated docs/foo.md") == "docs/foo.md"


def test_normalize_output_path_skips_optional_entry_ending_in_extension() -> None:
    # Regression: a multi-word "optional ..." entry that ends in .md previously
    # returned the whole noisy string and was then flagged as a missing output.
    assert normalize_output_path("optional update to docs/scientific-campaign-curator.md") is None


def test_normalize_output_path_skips_optional_prefixed_entry() -> None:
    assert normalize_output_path("optional docs/reviews/foo-blocker.md if not admissible") is None


def test_normalize_output_path_skips_conditional_only_if_entry() -> None:
    assert (
        normalize_output_path(
            "docs/notes/candidate-list.md only if the plan changes the ordering"
        )
        is None
    )


def test_normalize_output_path_skips_non_path_text() -> None:
    assert normalize_output_path("no audit RESULT, PRED, CLAIM, KNOW, or metric artifact") is None


def test_normalize_output_path_skips_multi_word_descriptive_entry() -> None:
    # Multi-word descriptive entries are not a single required path token.
    assert normalize_output_path("docs/foo.md (new planning artifact)") is None


def test_output_paths_collects_only_required_paths() -> None:
    payload = {
        "accepted_outputs": [
            "docs/required-one.md",
            "physics_lab/engines/loader.py",
            "optional update to docs/optional-one.md",
            "no result artifact",
        ]
    }
    assert output_paths(payload) == (
        "docs/required-one.md",
        "physics_lab/engines/loader.py",
    )


# --- Cross-platform advisory checks (TASK-0503) ---


def test_cross_platform_flags_hardcoded_tmp() -> None:
    hits = cross_platform_advisory_hits(('    path = "/tmp/scratch.json"',))
    assert len(hits) == 1
    assert "tempfile" in hits[0]


def test_cross_platform_flags_hardcoded_python3_executable() -> None:
    hits = cross_platform_advisory_hits(("    run([\"python3\", \"-m\", \"ruff\"])",))
    assert any("sys.executable" in hit for hit in hits)


def test_cross_platform_flags_direct_shell_script_invocation() -> None:
    hits = cross_platform_advisory_hits(('    run(["./scripts/apl_review_bundle.sh"])',))
    assert any("cross-platform (Python) entrypoint" in hit for hit in hits)


def test_cross_platform_flags_home_env_read() -> None:
    hits = cross_platform_advisory_hits(('    home = os.getenv("HOME")',))
    assert any("Path.home()" in hit for hit in hits)


def test_cross_platform_ignores_clean_portable_code() -> None:
    clean = (
        "    home = Path.home()",
        "    tmp = tempfile.gettempdir()",
        "    run([sys.executable, \"-m\", \"pytest\"])",
    )
    assert cross_platform_advisory_hits(clean) == ()


def test_cross_platform_skips_rule_catalog_lines() -> None:
    # A diff that only adds rule-catalog lines (this module's own patterns)
    # must not flag itself.
    catalog = ('        re.compile(r"""[\'"]/tmp/"""),',)
    assert cross_platform_advisory_hits(catalog) == ()


def test_cross_platform_surface_flags_changed_shell_scripts() -> None:
    hits = cross_platform_surface_hits(
        ("scripts/validate_quick.sh", "docs/foo.md", "scripts/apl_setup_worktree.sh")
    )
    assert len(hits) == 2
    assert all(".sh" in hit for hit in hits)


def test_cross_platform_surface_ignores_non_shell_files() -> None:
    assert cross_platform_surface_hits(("docs/foo.md", "physics_lab/cli.py")) == ()


# --- Follow-up task advisory checks (TASK-0534) ---


def test_follow_up_task_advisory_flags_informal_pr_body_mention() -> None:
    hits = follow_up_task_advisory_hits(
        (),
        ("docs/reviews/foo.md", "tasks/TASK-0123-foo.yaml"),
        pr_body="A minimal schema follow-up task is proposed for this blocker.",
    )
    assert len(hits) == 1
    assert "TASK-QUEUE" in hits[0]


def test_follow_up_task_advisory_flags_added_review_note_mention() -> None:
    hits = follow_up_task_advisory_hits(
        ("A separate task should add the validated row role enum.",),
        ("docs/reviews/foo.md", "tasks/TASK-0123-foo.yaml"),
    )
    assert len(hits) == 1


def test_follow_up_task_advisory_ignores_task_queue_pr() -> None:
    hits = follow_up_task_advisory_hits(
        ("A follow-up task is created in this queue.",),
        ("tasks/TASK-0124-follow-up.yaml",),
        pr_title="TASK-QUEUE: Add follow-up work",
    )
    assert hits == ()


def test_follow_up_task_advisory_ignores_formal_proposal_file() -> None:
    hits = follow_up_task_advisory_hits(
        ("A follow-up task is proposed.",),
        ("tasks/proposals/20260602-roman-follow-up.yaml",),
    )
    assert hits == ()
