"""Lightweight documentation link integrity checks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


DOCS_LINK_SURFACES = (
    "docs/campaigns",
    "docs/results",
    "docs/status.md",
    "docs/mission-control.md",
)
MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel"}


@dataclass(frozen=True)
class DocsLinkIssue:
    """Broken repository-local Markdown link."""

    source_path: str
    target: str
    message: str


def docs_link_source_paths(root: str | Path) -> tuple[Path, ...]:
    """Return campaign/result documentation files covered by the narrow check."""
    root_path = Path(root)
    paths: list[Path] = []
    for surface in DOCS_LINK_SURFACES:
        candidate = root_path / surface
        if candidate.is_file() and candidate.suffix == ".md":
            paths.append(candidate)
        elif candidate.is_dir():
            paths.extend(sorted(candidate.rglob("*.md")))
    return tuple(dict.fromkeys(paths))


def find_docs_link_issues(root: str | Path) -> tuple[DocsLinkIssue, ...]:
    """Find broken repository-local links in campaign and result documentation."""
    root_path = Path(root).resolve()
    issues: list[DocsLinkIssue] = []
    for path in docs_link_source_paths(root_path):
        text = path.read_text(encoding="utf-8")
        for target in _iter_markdown_targets(text):
            if not _is_repository_local_target(target):
                continue
            if _target_exists(path, target):
                continue
            issues.append(
                DocsLinkIssue(
                    source_path=path.resolve().relative_to(root_path).as_posix(),
                    target=target,
                    message=f"Broken repository-local Markdown link: {target}",
                )
            )
    return tuple(issues)


def _iter_markdown_targets(text: str) -> tuple[str, ...]:
    targets: list[str] = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        targets.extend(match.group(1) for match in MARKDOWN_LINK_PATTERN.finditer(line))
    return tuple(targets)


def _is_repository_local_target(target: str) -> bool:
    parsed = urlsplit(target)
    if parsed.scheme in EXTERNAL_SCHEMES:
        return False
    if parsed.scheme or parsed.netloc:
        return False
    if target.startswith("#"):
        return False
    return bool(parsed.path)


def _target_exists(source_path: Path, target: str) -> bool:
    parsed = urlsplit(target)
    decoded_path = unquote(parsed.path)
    resolved_target = (source_path.parent / decoded_path).resolve()
    return resolved_target.exists()
