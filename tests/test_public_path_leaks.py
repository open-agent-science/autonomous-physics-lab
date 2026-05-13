from __future__ import annotations

from pathlib import Path

from scripts.check_public_path_leaks import find_public_path_leaks


def test_public_path_leak_checker_reports_local_paths(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "example.md").write_text(
        "See /Users/example/project/file.md for local scratch notes.\n",
        encoding="utf-8",
    )

    leaks = find_public_path_leaks(tmp_path, ("docs",))

    assert len(leaks) == 1
    assert leaks[0].path == Path("docs/example.md")
    assert leaks[0].label == "macOS user home path"


def test_public_path_leak_checker_allows_generic_release_command(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "release-checklist.md").write_text(
        "Run `python3 scripts/check_public_path_leaks.py` before release.\n",
        encoding="utf-8",
    )

    assert find_public_path_leaks(tmp_path, ("docs",)) == []
