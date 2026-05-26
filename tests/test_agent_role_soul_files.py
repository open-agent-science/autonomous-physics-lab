"""Tests for the TASK-0424 agent role soul files.

These tests verify:
- the canonical template exists;
- every agents/<role-id>.md role file conforms to the template
  (required frontmatter fields, allowed status values);
- referenced `required_reading` files exist in the repo;
- `can_invoke_other_roles` references point to existing role files;
- the agents/ README references every active role file.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = REPO_ROOT / "agents"
TEMPLATE_PATH = AGENTS_DIR / "AGENT-TEMPLATE.md"
README_PATH = AGENTS_DIR / "README.md"

REQUIRED_FRONTMATTER_FIELDS = (
    "role_id",
    "role_name",
    "short_description",
    "status",
    "activation_intent",
    "scope",
    "goals",
    "required_reading",
    "allowed_tools",
    "scripts_to_use",
    "can_invoke_other_roles",
    "restrictions",
    "operating_mode_summary",
)

FORBIDDEN_FRONTMATTER_FIELDS = (
    # Removed in the rev: roles are not "appointed" by a named individual,
    # and the soul file should not embed activation phrases as the
    # authoritative trigger (use activation_intent instead — match the
    # concept in any language).
    "appointed_by",
    "appointed_at",
    "activation_phrases",
)

ALLOWED_STATUS_VALUES = (
    "active",
    "planned",
    "deprecated",
    "legacy_test_fixture",
)

# Files in agents/ that are NOT role files and must be excluded from
# template-compliance checks.
NON_ROLE_FILES = (
    "AGENT-TEMPLATE.md",
    "README.md",
    "example-agent.yaml",  # legacy test fixture, see agents/README.md
)


def _read_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"{path.name} does not start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise AssertionError(f"{path.name} does not close the YAML frontmatter block")
    return yaml.safe_load(text[4:end])


def _role_files() -> list[Path]:
    return sorted(
        p
        for p in AGENTS_DIR.glob("*.md")
        if p.name not in NON_ROLE_FILES
    )


# ---------------------------------------------------------------------------
# Template + index existence
# ---------------------------------------------------------------------------


class TestAgentsDirectoryShape:
    def test_template_exists(self) -> None:
        assert TEMPLATE_PATH.exists(), TEMPLATE_PATH

    def test_readme_exists(self) -> None:
        assert README_PATH.exists(), README_PATH

    def test_at_least_six_active_role_files(self) -> None:
        # architect, review-agent, scientific-curator, researcher,
        # task-proposal-agent, microtask-agent.
        files = _role_files()
        assert len(files) >= 6, [f.name for f in files]

    def test_readme_links_each_role_file(self) -> None:
        readme = README_PATH.read_text(encoding="utf-8")
        for role_file in _role_files():
            assert role_file.name in readme, role_file.name


# ---------------------------------------------------------------------------
# Frontmatter conformance
# ---------------------------------------------------------------------------


class TestRoleFileConformance:
    @pytest.mark.parametrize("role_file", _role_files(), ids=lambda p: p.name)
    def test_required_frontmatter_fields_present(self, role_file: Path) -> None:
        front = _read_frontmatter(role_file)
        for field in REQUIRED_FRONTMATTER_FIELDS:
            assert field in front, f"{role_file.name}: missing field {field}"

    @pytest.mark.parametrize("role_file", _role_files(), ids=lambda p: p.name)
    def test_role_id_matches_filename(self, role_file: Path) -> None:
        front = _read_frontmatter(role_file)
        expected = role_file.stem
        assert front["role_id"] == expected, (
            f"{role_file.name}: role_id={front['role_id']} but filename stem={expected}"
        )

    @pytest.mark.parametrize("role_file", _role_files(), ids=lambda p: p.name)
    def test_status_in_allowed_values(self, role_file: Path) -> None:
        front = _read_frontmatter(role_file)
        assert front["status"] in ALLOWED_STATUS_VALUES, front["status"]

    @pytest.mark.parametrize("role_file", _role_files(), ids=lambda p: p.name)
    def test_activation_intent_is_non_empty_string(self, role_file: Path) -> None:
        front = _read_frontmatter(role_file)
        intent = front["activation_intent"]
        assert isinstance(intent, str)
        # Activation intent must be a real concept description, not a
        # trivial stub.
        assert len(intent.strip()) >= 40, (
            f"{role_file.name}: activation_intent is too short to be a real "
            f"concept description ({len(intent.strip())} chars)"
        )

    @pytest.mark.parametrize("role_file", _role_files(), ids=lambda p: p.name)
    def test_no_forbidden_frontmatter_fields(self, role_file: Path) -> None:
        front = _read_frontmatter(role_file)
        for field in FORBIDDEN_FRONTMATTER_FIELDS:
            assert field not in front, (
                f"{role_file.name}: forbidden frontmatter field {field} is present"
            )

    @pytest.mark.parametrize("role_file", _role_files(), ids=lambda p: p.name)
    def test_allowed_tools_does_not_embed_machine_paths(
        self, role_file: Path
    ) -> None:
        """Soul files must not embed absolute filesystem paths in
        allowed_tools; descriptions must be machine-agnostic."""
        front = _read_frontmatter(role_file)
        for entry in front["allowed_tools"]:
            text = str(entry)
            assert "/Users/" not in text, (
                f"{role_file.name}: allowed_tools entry embeds a /Users/ path: {entry}"
            )
            assert "/home/" not in text, (
                f"{role_file.name}: allowed_tools entry embeds a /home/ path: {entry}"
            )
            assert "C:\\" not in text, (
                f"{role_file.name}: allowed_tools entry embeds a Windows path: {entry}"
            )

    @pytest.mark.parametrize("role_file", _role_files(), ids=lambda p: p.name)
    def test_goals_split_into_long_term_and_optional_targets(
        self, role_file: Path
    ) -> None:
        """Goals must be a structured dict with a non-empty long_term list
        and an optional current_targets list. This separates durable
        concerns (rarely changed) from tunable numeric targets (can be
        adjusted as the project evolves)."""
        front = _read_frontmatter(role_file)
        goals = front["goals"]
        assert isinstance(goals, dict), (
            f"{role_file.name}: goals must be a dict with long_term/current_targets keys"
        )
        long_term = goals.get("long_term")
        assert isinstance(long_term, list) and len(long_term) >= 1, (
            f"{role_file.name}: goals.long_term must be a non-empty list"
        )
        if "current_targets" in goals:
            assert isinstance(goals["current_targets"], list), (
                f"{role_file.name}: goals.current_targets must be a list"
            )

    @pytest.mark.parametrize("role_file", _role_files(), ids=lambda p: p.name)
    def test_required_reading_files_exist(self, role_file: Path) -> None:
        front = _read_frontmatter(role_file)
        for entry in front["required_reading"]:
            # Skip dynamic placeholders (templated paths with <...>).
            if "<" in entry and ">" in entry:
                continue
            target = REPO_ROOT / entry
            assert target.exists(), (
                f"{role_file.name}: required_reading entry {entry} does not exist"
            )

    @pytest.mark.parametrize("role_file", _role_files(), ids=lambda p: p.name)
    def test_cross_role_invocation_targets_exist(self, role_file: Path) -> None:
        front = _read_frontmatter(role_file)
        for entry in front["can_invoke_other_roles"]:
            target_role_id = entry["role_id"]
            target_file = AGENTS_DIR / f"{target_role_id}.md"
            assert target_file.exists(), (
                f"{role_file.name}: can_invoke_other_roles points to "
                f"{target_role_id} but agents/{target_role_id}.md is missing"
            )


# ---------------------------------------------------------------------------
# Required active roles
# ---------------------------------------------------------------------------


class TestRequiredActiveRoles:
    """Roman asked for these four roles to exist explicitly in this PR."""

    @pytest.mark.parametrize(
        "role_id",
        [
            "architect",
            "review-agent",
            "scientific-curator",
            "researcher",
            "task-proposal-agent",
            "microtask-agent",
        ],
    )
    def test_role_file_present_and_active(self, role_id: str) -> None:
        path = AGENTS_DIR / f"{role_id}.md"
        assert path.exists(), path
        front = _read_frontmatter(path)
        assert front["status"] == "active", f"{role_id}: status={front['status']}"

    def test_architect_role_phase_documented(self) -> None:
        front = _read_frontmatter(AGENTS_DIR / "architect.md")
        # Architect role must explicitly carry a phase label so the
        # current operating mode is documented (Phase 1 = topic-driven
        # was promoted to Phase 2 = proactive on 2026-05-26).
        phase = front.get("phase", "")
        assert phase.startswith("Phase "), (
            f"architect.md: phase must start with 'Phase '; got {phase!r}"
        )

    def test_researcher_is_default_role(self) -> None:
        front = _read_frontmatter(AGENTS_DIR / "researcher.md")
        short = front["short_description"].lower()
        assert "default" in short, short


# ---------------------------------------------------------------------------
# AGENTS.md cross-reference
# ---------------------------------------------------------------------------


class TestAgentsMdCrossReference:
    def test_agents_md_references_soul_file_index(self) -> None:
        agents_md = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        assert "agents/README.md" in agents_md
