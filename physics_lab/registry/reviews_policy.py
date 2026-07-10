"""Helpers for the docs/reviews shard-forward policy."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import subprocess


REVIEWS_ROOT = PurePosixPath("docs/reviews")
LEGACY_ROOT_GROUP = "legacy-root"
README_NAME = "README.md"


@dataclass(frozen=True)
class ReviewInventoryEntry:
    """One file in docs/reviews grouped for read-only navigation."""

    path: str
    group: str


@dataclass(frozen=True)
class ReviewInventory:
    """Recursive docs/reviews inventory."""

    entries: tuple[ReviewInventoryEntry, ...]

    @property
    def total_files(self) -> int:
        return len(self.entries)

    @property
    def counts_by_group(self) -> dict[str, int]:
        return dict(Counter(entry.group for entry in self.entries))


def is_root_review_file(path: str) -> bool:
    """Return true for flat-root docs/reviews files governed by the cutover."""

    parts = PurePosixPath(path).parts
    return len(parts) == 3 and parts[:2] == REVIEWS_ROOT.parts and parts[2] != README_NAME


def root_review_additions_from_name_status(lines: list[str]) -> tuple[str, ...]:
    """Return newly added/renamed flat-root review files from git name-status lines."""

    violations: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split("\t")
        status = parts[0]
        if status == "A" and len(parts) >= 2:
            candidate = parts[1]
        elif (status.startswith("R") or status.startswith("C")) and len(parts) >= 3:
            candidate = parts[2]
        else:
            continue
        if is_root_review_file(candidate):
            violations.append(candidate)
    return tuple(sorted(violations))


def git_name_status(root: str | Path, base: str, head: str) -> list[str]:
    """Return git name-status diff lines for base..head."""

    result = subprocess.run(
        ["git", "diff", "--name-status", "--diff-filter=ACR", base, head],
        cwd=Path(root),
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()


def new_root_review_files(root: str | Path, base: str, head: str) -> tuple[str, ...]:
    """Return root-level docs/reviews files newly added in a git diff."""

    return root_review_additions_from_name_status(git_name_status(root, base, head))


def review_group_for_path(path: Path) -> str:
    """Return the inventory group for a docs/reviews-relative file path."""

    relative = PurePosixPath(path.as_posix())
    if len(relative.parts) <= 1:
        return LEGACY_ROOT_GROUP
    return relative.parts[0]


def build_reviews_inventory(root: str | Path) -> ReviewInventory:
    """Build a recursive inventory of committed review-memory files."""

    root_path = Path(root)
    reviews_path = root_path / "docs" / "reviews"
    entries: list[ReviewInventoryEntry] = []
    if not reviews_path.exists():
        return ReviewInventory(entries=())
    for path in sorted(candidate for candidate in reviews_path.rglob("*") if candidate.is_file()):
        relative_to_reviews = path.relative_to(reviews_path)
        if relative_to_reviews.as_posix() == README_NAME:
            continue
        entries.append(
            ReviewInventoryEntry(
                path=path.relative_to(root_path).as_posix(),
                group=review_group_for_path(relative_to_reviews),
            )
        )
    return ReviewInventory(entries=tuple(entries))


def render_reviews_inventory(inventory: ReviewInventory) -> str:
    """Render a compact human-readable inventory."""

    lines = [
        "docs/reviews inventory",
        f"total files: {inventory.total_files}",
        "",
        "groups:",
    ]
    for group, count in sorted(inventory.counts_by_group.items()):
        lines.append(f"- {group}: {count}")
    return "\n".join(lines) + "\n"
