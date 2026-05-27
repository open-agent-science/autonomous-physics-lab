"""Generated task navigation views derived from canonical task YAML files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from physics_lab.registry.tasks import load_task


ACTIVE_VIEW_STATUSES = ("READY", "IN_PROGRESS", "REVIEW_READY")
WATCHLIST_STATUSES = ("PROPOSED", "SUPERSEDED", "REJECTED")

RELEASE_MARKERS = (
    "release",
    "launch",
    "public",
    "replication",
    "signoff",
    "readiness",
    "external reviewer",
)
RESEARCH_MARKERS = (
    "scientific",
    "science",
    "research",
    "physics",
    "benchmark",
    "campaign",
    "autonomous",
    "hypothesis",
    "experiment",
    "result",
    "dataset",
    "prediction",
    "nuclear",
    "quantum",
    "holdout",
    "validator",
    "numerical",
)
SUPPORT_MARKERS = (
    "documentation",
    "workflow",
    "maintainer",
    "contributor",
    "repository",
    "review_quality",
    "test_quality",
    "test_infrastructure",
    "coverage",
    "review_git",
    "code_quality",
    "maintainer_review",
)

TASK_VIEW_PATHS = {
    "research": "docs/task-views/research.md",
    "support": "docs/task-views/support.md",
    "release": "docs/task-views/release.md",
    "watchlist": "docs/task-views/watchlist.md",
    "blocked": "docs/task-views/blocked.md",
}


@dataclass(frozen=True)
class TaskViewEntry:
    """Expanded task metadata for generated navigation views."""

    task_id: str
    title: str
    type: str
    status: str
    priority: str
    difficulty: str
    related_domain: str
    planning_context: str
    lane: str

    @property
    def task_number(self) -> int:
        return int(self.task_id.removeprefix("TASK-"))


def load_task_view_entries(root: Path) -> tuple[TaskViewEntry, ...]:
    """Load canonical task files as view-ready entries."""
    entries: list[TaskViewEntry] = []
    for path in sorted((root / "tasks").glob("TASK-[0-9][0-9][0-9][0-9]-*.yaml")):
        payload = load_task(path)
        status = str(payload["status"])
        input_payload = payload.get("input", {})
        if not isinstance(input_payload, dict):
            input_payload = {}
        related_domain = str(input_payload.get("related_domain") or "").strip()
        planning_context = str(input_payload.get("planning_context") or "").strip()
        entries.append(
            TaskViewEntry(
                task_id=str(payload["id"]),
                title=str(payload["title"]),
                type=str(payload["type"]),
                status=status,
                priority=str(payload["priority"]),
                difficulty=str(payload["difficulty"]),
                related_domain=related_domain,
                planning_context=planning_context,
                lane=_classify_lane(payload),
            )
        )
    return tuple(entries)


def render_task_views(root: Path) -> dict[str, str]:
    """Render all generated task views from canonical task files."""
    entries = load_task_view_entries(root)
    return {
        "research": _render_lane_view(
            title="Research Tasks",
            description=(
                "Generated research-first navigation for executor agents and maintainers. "
                "Canonical storage remains `tasks/TASK-*.yaml`; this view hides DONE history "
                "so current science work is easier to scan."
            ),
            entries=tuple(entry for entry in entries if entry.lane == "research"),
        ),
        "support": _render_lane_view(
            title="Support Tasks",
            description=(
                "Generated support-lane view for docs, workflow, coverage, repository, and "
                "contributor-experience work that should not displace research mode by default."
            ),
            entries=tuple(entry for entry in entries if entry.lane == "support"),
        ),
        "release": _render_lane_view(
            title="Release Tasks",
            description=(
                "Generated release/readiness view for public wording, replication, signoff, and "
                "launch-gate work that needs a maintainer-facing checklist."
            ),
            entries=tuple(entry for entry in entries if entry.lane == "release"),
        ),
        "watchlist": _render_watchlist_view(entries),
        "blocked": _render_blocked_view(entries),
    }


def sync_task_views(root: Path) -> tuple[Path, ...]:
    """Write generated task-view documents under docs/task-views/."""
    rendered = render_task_views(root)
    written_paths: list[Path] = []
    for lane, relpath in TASK_VIEW_PATHS.items():
        path = root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered[lane], encoding="utf-8")
        written_paths.append(path)
    return tuple(written_paths)


def _classify_lane(payload: dict[str, object]) -> str:
    status = str(payload.get("status", ""))
    if status == "BLOCKED":
        return "blocked"
    if status in WATCHLIST_STATUSES:
        return "watchlist"

    input_payload = payload.get("input", {})
    if not isinstance(input_payload, dict):
        input_payload = {}
    identity_parts = [
        str(payload.get("title", "")),
        str(payload.get("type", "")),
        str(input_payload.get("related_domain", "")),
    ]
    haystack = " ".join(identity_parts).lower()

    if any(marker in haystack for marker in RELEASE_MARKERS):
        return "release"
    if any(marker in haystack for marker in SUPPORT_MARKERS):
        return "support"
    if any(marker in haystack for marker in RESEARCH_MARKERS):
        return "research"
    return "support"


def _render_lane_view(*, title: str, description: str, entries: tuple[TaskViewEntry, ...]) -> str:
    lines = [
        f"# {title}",
        "",
        "> This file is generated from canonical `tasks/TASK-*.yaml` files.",
        f"> {description}",
        "> Refresh with `python3 -m physics_lab.cli sync-active-board .`.",
        "",
    ]
    for status in ACTIVE_VIEW_STATUSES:
        lines.append(f"## {status}")
        lines.append("")
        status_entries = _entries_for_status(entries, status)
        if status_entries:
            lines.extend(_render_entry(entry) for entry in status_entries)
        else:
            lines.append("None.")
        lines.append("")
    return "\n".join(lines)


def _render_watchlist_view(entries: tuple[TaskViewEntry, ...]) -> str:
    lines = [
        "# Task Watchlist",
        "",
        "> This file is generated from canonical `tasks/TASK-*.yaml` files.",
        "> Use it for proposals, superseded work, rejected ideas, and deferred directions that should not be picked as executor work.",
        "> Refresh with `python3 -m physics_lab.cli sync-active-board .`.",
        "",
    ]
    watchlist_entries = tuple(entry for entry in entries if entry.lane == "watchlist")
    for status in WATCHLIST_STATUSES:
        lines.append(f"## {status}")
        lines.append("")
        status_entries = _entries_for_status(watchlist_entries, status)
        if status_entries:
            lines.extend(_render_entry(entry) for entry in status_entries)
        else:
            lines.append("None.")
        lines.append("")
    return "\n".join(lines)


def _render_blocked_view(entries: tuple[TaskViewEntry, ...]) -> str:
    lines = [
        "# Blocked Tasks",
        "",
        "> This file is generated from canonical `tasks/TASK-*.yaml` files.",
        "> Use it to see what is blocked without scanning the full DONE history in `tasks/ACTIVE.md`.",
        "> Refresh with `python3 -m physics_lab.cli sync-active-board .`.",
        "",
    ]
    blocked_entries = tuple(entry for entry in entries if entry.lane == "blocked")
    grouped = {
        "release": tuple(entry for entry in blocked_entries if _fallback_lane(entry) == "release"),
        "research": tuple(entry for entry in blocked_entries if _fallback_lane(entry) == "research"),
        "support": tuple(entry for entry in blocked_entries if _fallback_lane(entry) == "support"),
    }
    for lane, header in (
        ("release", "Release Blockers"),
        ("research", "Research Blockers"),
        ("support", "Support Blockers"),
    ):
        lines.append(f"## {header}")
        lines.append("")
        lane_entries = _sorted_entries(grouped[lane])
        if lane_entries:
            lines.extend(_render_entry(entry) for entry in lane_entries)
        else:
            lines.append("None.")
        lines.append("")
    return "\n".join(lines)


def _fallback_lane(entry: TaskViewEntry) -> str:
    haystack = " ".join(
        [entry.title, entry.type, entry.related_domain, entry.planning_context]
    ).lower()
    if any(marker in haystack for marker in RELEASE_MARKERS):
        return "release"
    if any(marker in haystack for marker in SUPPORT_MARKERS):
        return "support"
    if any(marker in haystack for marker in RESEARCH_MARKERS):
        return "research"
    return "support"


def _entries_for_status(
    entries: tuple[TaskViewEntry, ...],
    status: str,
) -> tuple[TaskViewEntry, ...]:
    return tuple(entry for entry in _sorted_entries(entries) if entry.status == status)


def _sorted_entries(entries: tuple[TaskViewEntry, ...]) -> tuple[TaskViewEntry, ...]:
    return tuple(
        sorted(
            entries,
            key=lambda entry: (entry.task_number, entry.title.lower()),
        )
    )


def _render_entry(entry: TaskViewEntry) -> str:
    details = [f"`{entry.type}`", f"priority `{entry.priority}`", f"difficulty `{entry.difficulty}`"]
    if entry.related_domain:
        details.append(f"domain `{entry.related_domain}`")
    return f"- `{entry.task_id}` - {entry.title} ({', '.join(details)})"
