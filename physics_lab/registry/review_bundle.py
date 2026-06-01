"""Portable PR review-bundle generation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re

from physics_lab.registry.pr_capability import find_git_path
from physics_lab.registry.review_git import run_command


def _git(root: Path, *args: str) -> str:
    git_path = find_git_path()
    if git_path is None:
        raise FileNotFoundError("Git executable was not found on PATH or in common install paths.")
    result = run_command([git_path, *args], cwd=root, timeout=120)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.rstrip()


def _safe_branch(branch: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", branch).strip("-") or "detached"


def generate_review_bundle(root: Path, *, base: str = "main") -> Path:
    """Write a Markdown review bundle and return its repository-relative path."""
    root = root.resolve()
    branch = _git(root, "branch", "--show-current").strip()
    if not branch:
        raise RuntimeError("Cannot generate a review bundle from detached HEAD.")

    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    output_dir = root / "_snapshots"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"review_{_safe_branch(branch)}_{timestamp}.md"

    status = _git(root, "status", "--short")
    commits = _git(root, "log", "--oneline", f"{base}..HEAD")
    changed_files = _git(root, "diff", "--name-only", f"{base}...HEAD")
    diff_stat = _git(root, "diff", "--stat", f"{base}...HEAD")
    full_diff = _git(root, "diff", f"{base}...HEAD")

    content = "\n".join(
        [
            "# PR Review Bundle",
            "",
            f"- branch: `{branch}`",
            f"- base: `{base}`",
            f"- generated_at_utc: {now.strftime('%Y-%m-%dT%H:%M:%SZ')}",
            "",
            "## Git status",
            "```",
            status,
            "```",
            "",
            f"## Commits vs {base}",
            "```",
            commits,
            "```",
            "",
            f"## Changed files vs {base}",
            "```",
            changed_files,
            "```",
            "",
            f"## Diff stat vs {base}",
            "```",
            diff_stat,
            "```",
            "",
            f"## Full diff vs {base}",
            "```diff",
            full_diff,
            "```",
            "",
        ]
    )
    output.write_text(content, encoding="utf-8")
    return output.relative_to(root)
