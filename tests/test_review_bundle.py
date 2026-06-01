from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from physics_lab.registry.maintainer_review import ensure_review_bundle
from physics_lab.registry.review_bundle import generate_review_bundle


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def _init_repo(root: Path) -> None:
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.name", "APL Test")
    _git(root, "config", "user.email", "apl-test@example.test")
    (root / "README.md").write_text("base\n", encoding="utf-8")
    _git(root, "add", "README.md")
    _git(root, "commit", "-m", "chore: init")
    _git(root, "switch", "-c", "agent/roman/codex/task-0520-review-bundle")
    (root / "README.md").write_text("base\nchange\n", encoding="utf-8")
    _git(root, "add", "README.md")
    _git(root, "commit", "-m", "docs(task-0520): change readme")


def test_generate_review_bundle_writes_expected_sections(tmp_path: Path) -> None:
    _init_repo(tmp_path)

    output = generate_review_bundle(tmp_path)
    text = (tmp_path / output).read_text(encoding="utf-8")

    assert output.parent == Path("_snapshots")
    assert "- branch: `agent/roman/codex/task-0520-review-bundle`" in text
    assert "- base: `main`" in text
    assert "## Git status" in text
    assert "## Commits vs main" in text
    assert "docs(task-0520): change readme" in text
    assert "## Changed files vs main" in text
    assert "README.md" in text
    assert "## Full diff vs main" in text


def test_review_bundle_cli_runs_from_repo_root(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    repo_root = Path(__file__).resolve().parents[1]

    result = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "apl_review_bundle.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (result.stdout, result.stderr)
    assert "Review bundle written to:" in result.stdout


def test_ensure_review_bundle_uses_portable_python_entrypoint(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "apl_review_bundle.py").write_text(
        (repo_root / "scripts" / "apl_review_bundle.py").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    bundle, status = ensure_review_bundle(
        tmp_path,
        "agent/roman/codex/task-0520-review-bundle",
        can_generate=True,
    )

    assert status == "generated"
    assert bundle is not None
    assert bundle.exists()
