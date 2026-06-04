"""Enforce id-only task references in prose (TASK-0577).

Reference tasks by id (TASK-XXXX), not by file path, so references never break
when a task is archived. See docs/task-reference-convention.md.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TASK_PATH_RE = re.compile(r"tasks/TASK-\d{4}-[a-z0-9-]+\.(?:yaml|md)")
ALLOWED_FILES = {
    "docs/task-archive-migration-plan.md",
    "docs/task-reference-convention.md",
}
ALLOWED_PREFIXES = ("docs/task-views/",)


def _scanned_files() -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "*.md", "tasks/proposals/*.yaml"],
        capture_output=True, text=True, check=True,
    )
    files = []
    for rel in out.stdout.splitlines():
        if rel in ALLOWED_FILES or any(rel.startswith(p) for p in ALLOWED_PREFIXES):
            continue
        files.append(rel)
    return files


def test_no_task_path_references_in_prose():
    offenders: list[str] = []
    for rel in _scanned_files():
        text = (REPO / rel).read_text(encoding="utf-8")
        for match in TASK_PATH_RE.findall(text):
            offenders.append(f"{rel}: {match}")
    assert not offenders, (
        "Reference tasks by id (TASK-XXXX), not by file path "
        "(see docs/task-reference-convention.md). Offenders:\n"
        + "\n".join(offenders)
    )
