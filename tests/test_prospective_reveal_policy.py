"""Regression tests for the shared prospective-reveal source-admissibility policy (TASK-1036)."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY = REPO_ROOT / "docs" / "prospective-reveal-source-admissibility.md"

REQUIRED_INVARIANTS = (
    "official metadata surfaces",
    "search-result snippets are\n  forbidden",
    "BLOCKED_NO_PEEK_AUDIT",
    "source_discovery_mode: official_metadata_only",
    "search_result_snippets_allowed: false",
    "target_matching_requires_manifest_approval: true",
    "value_access_requires_reveal_task: true",
    "no_peek_context_status: contaminated",
    "prospective_reveal_eligibility: false",
    "maintainer-reviewed",
)

BACKLINKED_DOCS = (
    "docs/nuclear-prediction-reveal-protocol.md",
    "docs/nuclear-reveal-source-readiness-checklist.md",
    "docs/reviews/frb-reveal-source-admissibility-contract.md",
)


def test_shared_policy_exists_with_invariants():
    text = POLICY.read_text(encoding="utf-8")
    for invariant in REQUIRED_INVARIANTS:
        assert invariant in text, f"policy missing invariant: {invariant!r}"


def test_domain_protocols_reference_shared_policy():
    for rel in BACKLINKED_DOCS:
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert "prospective-reveal-source-admissibility.md" in text, rel


def test_task_template_carries_reveal_scout_fields():
    text = (REPO_ROOT / "tasks" / "TASK-TEMPLATE.yaml").read_text(encoding="utf-8")
    for field in (
        "source_discovery_mode: official_metadata_only",
        "search_result_snippets_allowed: false",
        "no_peek_context_status: clean",
    ):
        assert field in text, f"template missing reveal-scout field: {field}"
