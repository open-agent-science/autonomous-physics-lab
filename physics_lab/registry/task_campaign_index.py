"""Task-to-campaign lane index (TASK-0460/TASK-0509).

Maps active canonical tasks to campaign lanes using existing task metadata
(`related_domain`, related objects, accepted outputs) and the campaign ids from
`campaign_profiles/_catalog.yaml`, so agents and the Scientific Campaign
Director can see which READY task belongs to which lane and whether it is safe
for parallel work without reading every task file.

Design boundaries:
- descriptive only: it never changes task status, never promotes claims, and
  never edits campaign metadata;
- it reuses existing task metadata and campaign ids instead of inventing new
  per-task campaign fields;
- it is rendered on demand instead of committed as a constantly changing
  generated board file;
- tasks with no confident campaign signal are flagged ``UNMAPPED`` for curator
  review rather than guessed into a lane.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.campaigns import campaign_catalog_path

ACTIVE_STATUSES = ("READY", "IN_PROGRESS", "REVIEW_READY", "BLOCKED")

SUPPORT_LANE = "support"
UNMAPPED_LANE = "UNMAPPED"

# related_domain / type values that are cross-campaign support or workflow lanes,
# not science campaigns. Tasks in these lanes are coordination/infra work.
SUPPORT_DOMAINS = frozenset(
    {
        "agent_capacity",
        "maintainer_review",
        "result_promotion",
        "campaign_portfolio",
        "repository_workflow",
        "repository_coordination",
        "multi_agent_coordination",
        "snapshot_tooling",
        "cross_campaign_research_factory",
    }
)
SUPPORT_TYPES = frozenset(
    {
        "maintainer_workflow",
        "workflow_protocol",
        "repository_maintenance",
    }
)

# Non-doc write surfaces that mean a task mutates shared canonical state and is
# therefore not automatically safe for blind parallel work.
SHARED_MUTABLE_SURFACES = (
    "results/",
    "claims/",
    "knowledge/",
    "prediction_registry/",
    "hypotheses/",
    "experiments/",
    "campaign_profiles/_catalog.yaml",
    "missions/current.yaml",
)


@dataclass(frozen=True)
class TaskLaneEntry:
    """One active task mapped to a campaign or support lane."""

    task_id: str
    title: str
    status: str
    lane: str
    mapping_basis: str
    artifact_surface: tuple[str, ...]
    parallel_safe: bool

    @property
    def ambiguous(self) -> bool:
        return self.lane == UNMAPPED_LANE


def load_campaign_ids(root: Path) -> tuple[str, ...]:
    """Return campaign ids declared in the generated campaign portfolio index."""
    catalog_path = campaign_catalog_path(root)
    if not catalog_path.exists():
        return ()
    payload = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
    return tuple(str(c["id"]) for c in payload.get("campaigns", []) if "id" in c)


def _normalize_domain(domain: str) -> str:
    return domain.strip().lower().replace("_", "-")


def _campaign_slug_from_path(text: str, campaign_ids: tuple[str, ...]) -> str | None:
    """Return a campaign id referenced by a docs/campaigns path or id substring."""
    lowered = text.lower()
    for campaign_id in campaign_ids:
        if f"docs/campaigns/{campaign_id}" in lowered or f"/{campaign_id}." in lowered:
            return campaign_id
    return None


def map_lane(
    payload: dict[str, Any], campaign_ids: tuple[str, ...]
) -> tuple[str, str]:
    """Map a task payload to ``(lane, mapping_basis)``.

    Resolution order: exact ``related_domain`` match to a campaign id, then the
    special cross-campaign factory support domain, then a ``docs/campaigns/<id>``
    reference in related objects / accepted outputs, then other known support
    domains/types, otherwise ``UNMAPPED`` for curator review. The factory
    special-case prevents a cross-campaign protocol task from being misclassified
    just because it mentions a campaign profile as an example or first adopter.
    """
    task_input = payload.get("input") or {}
    domain = str(task_input.get("related_domain") or "")
    if domain:
        normalized = _normalize_domain(domain)
        if normalized in campaign_ids:
            return normalized, f"related_domain={domain}"

    if domain == "cross_campaign_research_factory":
        return SUPPORT_LANE, f"support domain={domain}"

    references: list[str] = []
    references.extend(str(item) for item in task_input.get("related_objects", []) or [])
    references.extend(str(item) for item in payload.get("accepted_outputs", []) or [])
    for reference in references:
        matched = _campaign_slug_from_path(reference, campaign_ids)
        if matched is not None:
            return matched, f"campaign reference: {reference}"

    if domain in SUPPORT_DOMAINS or str(payload.get("type") or "") in SUPPORT_TYPES:
        basis = f"support domain={domain}" if domain else f"support type={payload.get('type')}"
        return SUPPORT_LANE, basis

    return UNMAPPED_LANE, "no confident campaign signal"


def artifact_surface(payload: dict[str, Any]) -> tuple[str, ...]:
    """Return the likely top-level write surfaces from accepted outputs."""
    surfaces: list[str] = []
    for raw in payload.get("accepted_outputs", []) or []:
        token = str(raw).strip().strip("`")
        # keep only entries that look like a path token, not prose
        candidate = token.split()[0] if token else ""
        if "/" not in candidate:
            continue
        top = candidate.split("/", 1)[0] + "/"
        surfaces.append(top)
    return tuple(sorted(dict.fromkeys(surfaces)))


def is_parallel_safe(surfaces: tuple[str, ...]) -> bool:
    """A task is parallel-safe when it does not write a shared mutable surface."""
    for surface in surfaces:
        for shared in SHARED_MUTABLE_SURFACES:
            if surface == shared or shared.startswith(surface):
                return False
    return True


def _iter_active_tasks(root: Path) -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[int, str, dict[str, Any]]] = []
    for path in sorted((root / "tasks").glob("TASK-[0-9][0-9][0-9][0-9]-*.yaml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if str(payload.get("status")) not in ACTIVE_STATUSES:
            continue
        task_id = str(payload.get("id", path.stem))
        try:
            number = int(task_id.removeprefix("TASK-"))
        except ValueError:
            number = -1
        rows.append((number, task_id, payload))
    rows.sort(key=lambda r: r[0])
    return [(task_id, payload) for _number, task_id, payload in rows]


def build_index(root: Path) -> dict[str, Any]:
    """Build the task-to-campaign lane index as a serializable dict."""
    campaign_ids = load_campaign_ids(root)
    entries: list[TaskLaneEntry] = []
    for task_id, payload in _iter_active_tasks(root):
        lane, basis = map_lane(payload, campaign_ids)
        surfaces = artifact_surface(payload)
        entries.append(
            TaskLaneEntry(
                task_id=task_id,
                title=str(payload.get("title", "")),
                status=str(payload.get("status", "")),
                lane=lane,
                mapping_basis=basis,
                artifact_surface=surfaces,
                parallel_safe=is_parallel_safe(surfaces),
            )
        )

    lanes: dict[str, list[str]] = {}
    for entry in entries:
        lanes.setdefault(entry.lane, []).append(entry.task_id)

    # Concrete accepted-output path collisions across active tasks (real conflict).
    path_conflicts = _output_path_conflicts(root)

    return {
        "generated_by": "scripts/apl_task_campaign_index.py",
        "purpose": (
            "Task-to-campaign lane index for parallel research lanes (TASK-0460). "
            "Generated on demand from canonical task YAML; not a committed source of truth."
        ),
        "active_statuses": list(ACTIVE_STATUSES),
        "campaign_ids": list(campaign_ids),
        "summary": {
            "active_tasks": len(entries),
            "lanes": len(lanes),
            "unmapped": sum(1 for e in entries if e.ambiguous),
            "needs_curator_review": [e.task_id for e in entries if e.ambiguous],
        },
        "lanes": {lane: sorted(ids) for lane, ids in sorted(lanes.items())},
        "tasks": [
            {
                "task_id": e.task_id,
                "title": e.title,
                "status": e.status,
                "lane": e.lane,
                "mapping_basis": e.mapping_basis,
                "artifact_surface": list(e.artifact_surface),
                "parallel_safe": e.parallel_safe,
            }
            for e in entries
        ],
        "path_conflicts": path_conflicts,
    }


def _output_path_conflicts(root: Path) -> list[dict[str, Any]]:
    """Return concrete accepted-output paths claimed by more than one active task."""
    owners: dict[str, list[str]] = {}
    for task_id, payload in _iter_active_tasks(root):
        for raw in payload.get("accepted_outputs", []) or []:
            token = str(raw).strip().strip("`")
            candidate = token.split()[0] if token else ""
            if (
                "/" not in candidate
                or candidate.endswith("/")
                or _is_placeholder_output_path(candidate)
            ):
                continue
            owners.setdefault(candidate, []).append(task_id)
    return [
        {"path": path, "tasks": sorted(set(tasks))}
        for path, tasks in sorted(owners.items())
        if len(set(tasks)) > 1
    ]


def _is_placeholder_output_path(path: str) -> bool:
    """Return True for template paths that should not count as real collisions."""
    return "XXXX" in path or "<" in path or ">" in path


def render_yaml(index: dict[str, Any]) -> str:
    """Render the index as an on-demand YAML document."""
    header = (
        "# Generated on demand by scripts/apl_task_campaign_index.py.\n"
        "# Do not commit this output as a canonical board; tasks/TASK-*.yaml is the source of truth.\n"
    )
    body = yaml.safe_dump(index, sort_keys=False, allow_unicode=True, width=100)
    return header + body


def render_markdown(index: dict[str, Any]) -> str:
    """Render the index as a compact Markdown table for humans."""
    lines = [
        "# Task-to-Campaign Lane Index",
        "",
        "Generated by `scripts/apl_task_campaign_index.py` (TASK-0460). "
        "Query on demand; do not commit the output as a generated board.",
        "",
        f"- active tasks: {index['summary']['active_tasks']}",
        f"- lanes: {index['summary']['lanes']}",
        f"- needs curator review (UNMAPPED): "
        f"{', '.join(index['summary']['needs_curator_review']) or 'none'}",
        "",
        "| Task | Status | Lane | Parallel-safe | Artifact surface | Mapping basis |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for task in index["tasks"]:
        surface = ", ".join(task["artifact_surface"]) or "—"
        lines.append(
            f"| {task['task_id']} | {task['status']} | {task['lane']} | "
            f"{'yes' if task['parallel_safe'] else 'no'} | {surface} | "
            f"{task['mapping_basis']} |"
        )
    if index["path_conflicts"]:
        lines.extend(["", "## Accepted-output path conflicts", ""])
        for conflict in index["path_conflicts"]:
            lines.append(f"- `{conflict['path']}` claimed by {', '.join(conflict['tasks'])}")
    return "\n".join(lines) + "\n"
