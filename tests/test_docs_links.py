from __future__ import annotations

import textwrap
from pathlib import Path

from physics_lab.registry.docs_links import find_docs_link_issues
from physics_lab.registry.repository import validate_repository


def test_docs_link_checker_accepts_existing_campaign_and_result_links(tmp_path: Path) -> None:
    campaign = tmp_path / "docs" / "campaigns" / "example.md"
    result = tmp_path / "docs" / "results" / "summary.md"
    campaign.parent.mkdir(parents=True)
    result.parent.mkdir(parents=True)
    campaign.write_text("[result](../results/summary.md)\n", encoding="utf-8")
    result.write_text("[campaign](../campaigns/example.md)\n", encoding="utf-8")

    assert find_docs_link_issues(tmp_path) == ()


def test_docs_link_checker_reports_broken_repository_local_link(tmp_path: Path) -> None:
    campaign = tmp_path / "docs" / "campaigns" / "example.md"
    campaign.parent.mkdir(parents=True)
    campaign.write_text("[missing](../results/missing.md)\n", encoding="utf-8")

    issues = find_docs_link_issues(tmp_path)

    assert len(issues) == 1
    assert issues[0].source_path == "docs/campaigns/example.md"
    assert issues[0].target == "../results/missing.md"


def test_docs_link_checker_ignores_external_links_anchors_and_code_blocks(tmp_path: Path) -> None:
    page = tmp_path / "docs" / "mission-control.md"
    page.parent.mkdir(parents=True)
    page.write_text(
        textwrap.dedent(
            """\
            [external](https://example.com/missing.md)
            [anchor](#local-section)

            ```md
            [not checked](./missing.md)
            ```
            """
        ),
        encoding="utf-8",
    )

    assert find_docs_link_issues(tmp_path) == ()


def test_strict_validate_repository_reports_docs_link_issues(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("README\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("license\n", encoding="utf-8")
    page = tmp_path / "docs" / "results" / "summary.md"
    page.parent.mkdir(parents=True)
    page.write_text("[missing](./missing.md)\n", encoding="utf-8")

    summary = validate_repository(tmp_path, strict=True)

    assert any(issue.code == "broken_docs_link" for issue in summary.issues)
