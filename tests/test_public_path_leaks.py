from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_checker():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "check_public_path_leaks.py"
    spec = importlib.util.spec_from_file_location("check_public_path_leaks", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.find_public_path_leaks


find_public_path_leaks = _load_checker()


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
