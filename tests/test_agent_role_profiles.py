"""Tests for the TASK-0424 agent role profiles.

Role profiles are pure YAML under agents/<role-id>.yaml and validated
against physics_lab/schemas/agent.schema.json.

These tests verify:
- the canonical template and schema exist;
- every agents/<role-id>.yaml conforms to the schema;
- role_id matches the filename;
- referenced required_reading files exist;
- can_invoke_other_roles targets exist as siblings;
- allowed_tools entries do not embed absolute machine paths;
- the agents/ README links every active role file;
- AGENTS.md references the role-profile index;
- the six expected active roles are present.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = REPO_ROOT / "agents"
TEMPLATE_PATH = AGENTS_DIR / "AGENT-TEMPLATE.yaml"
README_PATH = AGENTS_DIR / "README.md"
SCHEMA_PATH = REPO_ROOT / "physics_lab" / "schemas" / "agent.schema.json"

# Files in agents/ that are NOT role files and must be excluded from
# conformance checks.
NON_ROLE_FILES = (
    "AGENT-TEMPLATE.yaml",
    "README.md",
)


def _role_files() -> list[Path]:
    return sorted(
        p
        for p in AGENTS_DIR.glob("*.yaml")
        if p.name not in NON_ROLE_FILES
    )


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Template + schema + index existence
# ---------------------------------------------------------------------------


class TestAgentsDirectoryShape:
    def test_template_exists(self) -> None:
        assert TEMPLATE_PATH.exists(), TEMPLATE_PATH

    def test_schema_exists(self) -> None:
        assert SCHEMA_PATH.exists(), SCHEMA_PATH

    def test_schema_parses_as_json(self) -> None:
        schema = _load_schema()
        assert schema.get("title") == "AgentRole"

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

    def test_no_legacy_markdown_role_files(self) -> None:
        """Pure YAML migration: no .md role files except the README."""
        md_files = sorted(AGENTS_DIR.glob("*.md"))
        names = [p.name for p in md_files]
        assert names == ["README.md"], (
            f"agents/ contains unexpected .md files: {names}. "
            f"Role files must be pure YAML (agents/<role-id>.yaml)."
        )


# ---------------------------------------------------------------------------
# Per-role schema conformance
# ---------------------------------------------------------------------------


class TestRoleFileConformance:
    @pytest.mark.parametrize("role_file", _role_files(), ids=lambda p: p.name)
    def test_validates_against_schema(self, role_file: Path) -> None:
        schema = _load_schema()
        payload = _load_yaml(role_file)
        jsonschema.validate(instance=payload, schema=schema)

    @pytest.mark.parametrize("role_file", _role_files(), ids=lambda p: p.name)
    def test_role_id_matches_filename(self, role_file: Path) -> None:
        payload = _load_yaml(role_file)
        expected = role_file.stem
        assert payload["role_id"] == expected, (
            f"{role_file.name}: role_id={payload['role_id']!r} but filename stem={expected!r}"
        )

    @pytest.mark.parametrize("role_file", _role_files(), ids=lambda p: p.name)
    def test_required_reading_files_exist(self, role_file: Path) -> None:
        payload = _load_yaml(role_file)
        for entry in payload["required_reading"]:
            assert "<" not in entry and ">" not in entry, (
                f"{role_file.name}: required_reading entry contains a "
                f"templated placeholder, which is forbidden: {entry!r}"
            )
            target = REPO_ROOT / entry
            assert target.exists(), (
                f"{role_file.name}: required_reading entry {entry!r} does not exist"
            )

    @pytest.mark.parametrize("role_file", _role_files(), ids=lambda p: p.name)
    def test_can_invoke_other_roles_targets_exist(self, role_file: Path) -> None:
        payload = _load_yaml(role_file)
        for entry in payload["can_invoke_other_roles"]:
            target_role_id = entry["role_id"]
            target_file = AGENTS_DIR / f"{target_role_id}.yaml"
            assert target_file.exists(), (
                f"{role_file.name}: can_invoke_other_roles points to "
                f"{target_role_id!r} but agents/{target_role_id}.yaml is missing"
            )

    @pytest.mark.parametrize("role_file", _role_files(), ids=lambda p: p.name)
    def test_allowed_tools_does_not_embed_machine_paths(
        self, role_file: Path
    ) -> None:
        """Role profiles must not embed absolute filesystem paths in
        allowed_tools; descriptions must be machine-agnostic."""
        payload = _load_yaml(role_file)
        for entry in payload["allowed_tools"]:
            text = str(entry)
            assert "/Users/" not in text, (
                f"{role_file.name}: allowed_tools entry embeds a /Users/ path: {entry!r}"
            )
            assert "/home/" not in text, (
                f"{role_file.name}: allowed_tools entry embeds a /home/ path: {entry!r}"
            )
            assert "C:\\" not in text, (
                f"{role_file.name}: allowed_tools entry embeds a Windows path: {entry!r}"
            )

    @pytest.mark.parametrize("role_file", _role_files(), ids=lambda p: p.name)
    def test_scripts_to_use_files_exist(self, role_file: Path) -> None:
        payload = _load_yaml(role_file)
        for entry in payload["scripts_to_use"]:
            target = REPO_ROOT / entry
            assert target.exists(), (
                f"{role_file.name}: scripts_to_use entry {entry!r} does not exist"
            )


# ---------------------------------------------------------------------------
# Required active roles
# ---------------------------------------------------------------------------


class TestRequiredActiveRoles:
    """The six roles roman asked to be present and active."""

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
        path = AGENTS_DIR / f"{role_id}.yaml"
        assert path.exists(), path
        payload = _load_yaml(path)
        assert payload["status"] == "active", f"{role_id}: status={payload['status']}"

    def test_architect_role_phase_documented(self) -> None:
        payload = _load_yaml(AGENTS_DIR / "architect.yaml")
        phase = payload.get("phase", "")
        assert phase.startswith("Phase "), (
            f"architect.yaml: phase must start with 'Phase '; got {phase!r}"
        )

    def test_researcher_is_default_role(self) -> None:
        payload = _load_yaml(AGENTS_DIR / "researcher.yaml")
        short = payload["short_description"].lower()
        assert "default" in short, short


# ---------------------------------------------------------------------------
# AGENTS.md cross-reference
# ---------------------------------------------------------------------------


class TestAgentsMdCrossReference:
    def test_agents_md_references_role_profile_index(self) -> None:
        agents_md = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        assert "agents/README.md" in agents_md


# ---------------------------------------------------------------------------
# docs/agent-catalog.md cross-reference (TASK-0426)
# ---------------------------------------------------------------------------


class TestAgentCatalogLinksEveryActiveRoleProfile:
    """Every agents/<role>.yaml with status: active must be linked from
    docs/agent-catalog.md so a reader of the catalog can find the
    compact role profile alongside the long-form narrative description.
    """

    def _catalog_text(self) -> str:
        return (REPO_ROOT / "docs" / "agent-catalog.md").read_text(
            encoding="utf-8"
        )

    @pytest.mark.parametrize("role_file", _role_files(), ids=lambda p: p.name)
    def test_active_role_profile_is_linked_from_catalog(
        self, role_file: Path
    ) -> None:
        payload = _load_yaml(role_file)
        if payload.get("status") != "active":
            pytest.skip(f"{role_file.name} is not status: active")
        catalog = self._catalog_text()
        # The catalog must link to the role profile via its repo-relative
        # path so a reader navigating from the catalog reaches the YAML
        # in one click.
        link_token = f"agents/{role_file.name}"
        assert link_token in catalog, (
            f"docs/agent-catalog.md is missing a link to {link_token!r}. "
            f"Add a 'Role profile:' line under the matching agent path "
            f"entry per TASK-0426."
        )

    def test_catalog_introduces_role_profiles_section(self) -> None:
        catalog = self._catalog_text()
        # The catalog must explain agents/ as the role-profile directory
        # so a reader understands what the per-entry links mean.
        assert "Role Profiles Under `agents/`" in catalog, (
            "docs/agent-catalog.md is missing the 'Role Profiles Under "
            "`agents/`' section introduced by TASK-0426."
        )

    def test_catalog_has_architect_entry(self) -> None:
        catalog = self._catalog_text()
        # Architect role had no catalog entry before TASK-0426; the entry
        # must be present in the Repository-Architecture-Facing section.
        assert "### 9. Architect" in catalog, (
            "docs/agent-catalog.md is missing the '### 9. Architect' "
            "entry added by TASK-0426."
        )
        assert "Repository-Architecture-Facing" in catalog, (
            "docs/agent-catalog.md is missing the "
            "'Repository-Architecture-Facing Agent Paths' subsection "
            "added by TASK-0426."
        )
