"""Generate compact summaries for scientific microtask queues."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


SUMMARY_START = "<!-- BEGIN AUTO MICROTASK QUEUE SUMMARY -->"
SUMMARY_END = "<!-- END AUTO MICROTASK QUEUE SUMMARY -->"


@dataclass(frozen=True)
class MicrotaskQueueSummary:
    """Compact metadata for one microtask queue."""

    filename: str
    queue_id: str
    campaign: str
    campaign_status: str
    microtask_count: int
    available_count: int
    completed_count: int
    retired_count: int
    risk_levels: tuple[str, ...]
    guidance: str


@dataclass(frozen=True)
class MicrotaskAvailabilityItem:
    """Effective availability for one queue item after run-record checks."""

    filename: str
    queue_id: str
    microtask_id: str
    title: str
    type: str
    status: str
    queue_status: str
    repeatable: bool
    completed_runs: int
    active_runs: int
    risk_level: str


def load_microtask_queue_summaries(root: str | Path) -> tuple[MicrotaskQueueSummary, ...]:
    """Load compact metadata for all queue files under tasks/microtasks/."""
    root_path = Path(root)
    queue_root = root_path / "tasks" / "microtasks"
    completed_runs = _completed_microtask_ids_by_queue(root_path)
    summaries: list[MicrotaskQueueSummary] = []
    for path in sorted(queue_root.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle)
        if not isinstance(payload, dict):
            raise ValueError(f"{path} must contain a YAML mapping")

        microtasks = payload.get("microtasks", [])
        if not isinstance(microtasks, list):
            raise ValueError(f"{path} microtasks must be a list")

        guidance_items = payload.get("selection_guidance", [])
        if not isinstance(guidance_items, list):
            raise ValueError(f"{path} selection_guidance must be a list")

        statuses = [_microtask_status(item, completed_runs.get(str(payload.get("queue_id", path.stem)), set())) for item in microtasks]
        available_count = statuses.count("available")
        completed_count = statuses.count("completed")
        retired_count = statuses.count("retired")
        risk_levels = sorted(
            {
                str(item.get("risk_level", "unspecified"))
                for item, status in zip(microtasks, statuses)
                if isinstance(item, dict) and status == "available"
            }
        )
        summaries.append(
            MicrotaskQueueSummary(
                filename=path.name,
                queue_id=str(payload.get("queue_id", path.stem)),
                campaign=str(payload.get("campaign", "")),
                campaign_status=str(payload.get("campaign_status", "")),
                microtask_count=len(microtasks),
                available_count=available_count,
                completed_count=completed_count,
                retired_count=retired_count,
                risk_levels=tuple(risk_levels),
                guidance=str(guidance_items[0]) if guidance_items else "",
            )
        )
    return tuple(summaries)


def load_microtask_availability(
    root: str | Path,
    *,
    queue_id: str | None = None,
) -> tuple[MicrotaskAvailabilityItem, ...]:
    """Load effective microtask availability from queues plus run records."""
    root_path = Path(root)
    queue_root = root_path / "tasks" / "microtasks"
    run_counts = _microtask_run_status_counts_by_item(root_path)
    items: list[MicrotaskAvailabilityItem] = []
    for path in sorted(queue_root.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle)
        if not isinstance(payload, dict):
            raise ValueError(f"{path} must contain a YAML mapping")
        declared_queue_id = str(payload.get("queue_id", path.stem))
        if queue_id is not None and declared_queue_id != queue_id:
            continue
        microtasks = payload.get("microtasks", [])
        if not isinstance(microtasks, list):
            raise ValueError(f"{path} microtasks must be a list")
        for item in microtasks:
            if not isinstance(item, dict):
                continue
            microtask_id = str(item.get("id") or "").strip()
            if not microtask_id:
                continue
            counts = run_counts.get((declared_queue_id, microtask_id), {})
            repeatable = _is_repeatable_microtask(item)
            queue_status = str(item.get("status") or "available").strip().lower()
            completed_runs = counts.get("completed", 0)
            active_runs = counts.get("active", 0)
            status = _effective_microtask_status(
                queue_status=queue_status,
                repeatable=repeatable,
                completed_runs=completed_runs,
                active_runs=active_runs,
            )
            items.append(
                MicrotaskAvailabilityItem(
                    filename=path.name,
                    queue_id=declared_queue_id,
                    microtask_id=microtask_id,
                    title=str(item.get("title") or ""),
                    type=str(item.get("type") or ""),
                    status=status,
                    queue_status=queue_status,
                    repeatable=repeatable,
                    completed_runs=completed_runs,
                    active_runs=active_runs,
                    risk_level=str(item.get("risk_level") or "unspecified"),
                )
            )
    return tuple(items)


def render_microtask_queue_summary_table(summaries: tuple[MicrotaskQueueSummary, ...]) -> str:
    """Render queue summaries as a compact Markdown table."""
    lines = [
        "| Queue | Campaign | Campaign Status | Available | Completed | Retired | Risk Levels | Selection Guidance |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for summary in summaries:
        queue_link = f"[`{summary.queue_id}`]({summary.filename})"
        lines.append(
            "| "
            f"{queue_link} | "
            f"{_escape_table_cell(summary.campaign)} | "
            f"`{summary.campaign_status}` | "
            f"{summary.available_count} / {summary.microtask_count} | "
            f"{summary.completed_count} | "
            f"{summary.retired_count} | "
            f"{_format_values(summary.risk_levels)} | "
            f"{_escape_table_cell(summary.guidance)} |"
        )
    return "\n".join(lines)


def refresh_microtask_queue_summary(readme_path: str | Path, root: str | Path) -> str:
    """Refresh the generated queue summary section in tasks/microtasks/README.md."""
    path = Path(readme_path)
    text = path.read_text(encoding="utf-8")
    summaries = load_microtask_queue_summaries(root)
    table = render_microtask_queue_summary_table(summaries)
    section = f"{SUMMARY_START}\n\n{table}\n\n{SUMMARY_END}"

    if SUMMARY_START not in text or SUMMARY_END not in text:
        raise ValueError(f"{path} is missing generated summary markers")
    before, rest = text.split(SUMMARY_START, 1)
    _old, after = rest.split(SUMMARY_END, 1)
    updated = before + section + after
    path.write_text(updated, encoding="utf-8")
    return updated


def _format_values(values: tuple[str, ...]) -> str:
    if not values:
        return "`unspecified`"
    return ", ".join(f"`{_escape_table_cell(value)}`" for value in values)


def _escape_table_cell(value: str) -> str:
    return value.replace("|", "\\|")


def _completed_microtask_ids_by_queue(root: Path) -> dict[str, set[str]]:
    runs_root = root / "microtask_runs"
    completed: dict[str, set[str]] = {}
    if not runs_root.exists():
        return completed
    for path in sorted(runs_root.glob("*/*.yaml")):
        if path.name == "MICROTASK-RUN-TEMPLATE.yaml":
            continue
        with path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle)
        if not isinstance(payload, dict):
            continue
        if str(payload.get("status") or "").strip() != "COMPLETED":
            continue
        queue_id = str(payload.get("queue_id") or "").strip()
        microtask_id = str(payload.get("microtask_id") or "").strip()
        if queue_id and microtask_id:
            completed.setdefault(queue_id, set()).add(microtask_id)
    return completed


def _microtask_run_status_counts_by_item(root: Path) -> dict[tuple[str, str], dict[str, int]]:
    runs_root = root / "microtask_runs"
    counts: dict[tuple[str, str], dict[str, int]] = {}
    if not runs_root.exists():
        return counts
    active_statuses = {"CLAIMED", "IN_PROGRESS", "PR_OPEN", "REVIEW_READY"}
    for path in sorted(runs_root.glob("*/*.yaml")):
        if path.name == "MICROTASK-RUN-TEMPLATE.yaml":
            continue
        with path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle)
        if not isinstance(payload, dict):
            continue
        queue_id = str(payload.get("queue_id") or "").strip()
        microtask_id = str(payload.get("microtask_id") or "").strip()
        status = str(payload.get("status") or "").strip()
        if not queue_id or not microtask_id:
            continue
        key = (queue_id, microtask_id)
        bucket = counts.setdefault(key, {"active": 0, "completed": 0})
        if status in active_statuses:
            bucket["active"] += 1
        elif status == "COMPLETED":
            bucket["completed"] += 1
    return counts


def _is_repeatable_microtask(item: dict[str, object]) -> bool:
    if bool(item.get("repeatable")):
        return True
    item_type = str(item.get("type") or "").strip()
    return item_type.startswith("repeatable-")


def _effective_microtask_status(
    *,
    queue_status: str,
    repeatable: bool,
    completed_runs: int,
    active_runs: int,
) -> str:
    if queue_status == "retired":
        return "retired"
    if active_runs:
        return "claimed"
    if queue_status == "completed":
        return "completed"
    if completed_runs and not repeatable:
        return "completed"
    return "available"


def _microtask_status(item: object, completed_run_ids: set[str]) -> str:
    if not isinstance(item, dict):
        return "retired"
    microtask_id = str(item.get("id") or "").strip()
    if microtask_id in completed_run_ids and not _is_repeatable_microtask(item):
        return "completed"
    status = str(item.get("status") or "available").strip().lower()
    if status in {"completed", "retired"}:
        return status
    return "available"
