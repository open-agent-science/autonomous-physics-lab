"""Tests for accepted-output parsing in review_checks (TASK-0466, F4)."""

from __future__ import annotations

from physics_lab.registry.review_checks import normalize_output_path, output_paths


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
