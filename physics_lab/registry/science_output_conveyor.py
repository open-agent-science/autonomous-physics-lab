"""Advisory science-output conveyor health report helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.active_board import TaskBoardEntry, load_board_entries
from physics_lab.registry.mission_control import ready_science_pool_health
from physics_lab.registry.results import load_result
from physics_lab.registry.tasks import load_task


RESULT_CANDIDATE_VERDICTS = {
    "VALID",
    "VALID_IN_RANGE",
    "PARTIALLY_VALID",
    "INCONCLUSIVE",
}
SANDBOX_CANDIDATE_VERDICTS = {
    "SANDBOX_PASS",
    "PARTIALLY_VALID",
    "REVIEW_NEEDED",
}
BLOCKER_TERMS = (
    "BLOCKED",
    "blocker",
    "Stop condition",
    "stop condition",
    "PARTIALLY_CLEARED",
    "INCONCLUSIVE_SOURCE_REVIEW",
    "negative result",
)
DECISION_TERMS = (
    "## Decision",
    "## Verdict",
    "Curator Verdict",
    "Queue Decision",
    "Accepted",
    "Rejected",
)
@dataclass(frozen=True)
class ConveyorTaskSummary:
    """Compact task status item."""

    task_id: str
    title: str
    status: str
    type: str
    priority: str
    difficulty: str
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConveyorResultArtifact:
    """Compact canonical result artifact item."""

    result_id: str
    task_id: str
    experiment_id: str
    title: str
    verdict: str
    verification_passed: bool
    generated_at: str
    path: str


@dataclass(frozen=True)
class ConveyorAgentRun:
    """Compact sandbox run item."""

    run_id: str
    task_id: str
    campaign_id: str
    verdict: str
    path: str


@dataclass(frozen=True)
class ConveyorReviewItem:
    """Compact review-note item."""

    path: str
    title: str
    matched_terms: tuple[str, ...]


@dataclass(frozen=True)
class ScienceOutputConveyorReport:
    """Serializable maintainer health report."""

    advisory_only: bool
    task_queue_needed: bool
    recent_task_transitions: tuple[ConveyorTaskSummary, ...]
    ready_science_task_count: int
    ready_science_surfaces: tuple[str, ...]
    blocked_lane_reasons: tuple[ConveyorTaskSummary, ...]
    new_result_artifacts: tuple[ConveyorResultArtifact, ...]
    sandbox_result_candidates: tuple[ConveyorAgentRun, ...]
    blocker_reviews: tuple[ConveyorReviewItem, ...]
    campaign_decisions: tuple[ConveyorReviewItem, ...]
    result_candidates: tuple[str, ...]
    overclaim_risk: tuple[str, ...]
    guardrails: tuple[str, ...]
    source_paths: tuple[str, ...]

    def to_json_data(self) -> dict[str, Any]:
        """Return a JSON-safe representation."""
        return asdict(self)


def build_science_output_conveyor_report(
    root: str | Path,
    *,
    recent_limit: int = 8,
) -> ScienceOutputConveyorReport:
    """Build an advisory science-output conveyor report.

    The report is read-only: it does not create tasks, promote claims, merge PRs,
    or rewrite generated task navigation.
    """
    root_path = Path(root).resolve()
    board_entries = load_board_entries(root_path)
    ready_health = ready_science_pool_health(root_path)
    result_artifacts = _recent_results(root_path, limit=recent_limit)
    sandbox_candidates = _sandbox_result_candidates(root_path, limit=recent_limit)
    blocker_reviews = _review_items(root_path, BLOCKER_TERMS, limit=recent_limit)
    campaign_decisions = _review_items(root_path, DECISION_TERMS, limit=recent_limit)

    return ScienceOutputConveyorReport(
        advisory_only=True,
        task_queue_needed=ready_health.task_queue_needed,
        recent_task_transitions=_recent_task_transitions(board_entries, limit=recent_limit),
        ready_science_task_count=ready_health.ready_science_count,
        ready_science_surfaces=ready_health.active_surfaces,
        blocked_lane_reasons=_blocked_lane_reasons(root_path, board_entries, limit=recent_limit),
        new_result_artifacts=result_artifacts,
        sandbox_result_candidates=sandbox_candidates,
        blocker_reviews=blocker_reviews,
        campaign_decisions=campaign_decisions,
        result_candidates=_result_candidate_refs(result_artifacts, sandbox_candidates),
        overclaim_risk=_overclaim_risk(result_artifacts, sandbox_candidates, board_entries),
        guardrails=(
            "Advisory report only; do not create tasks, merge PRs, or promote claims from this output.",
            "Treat sandbox agent runs as review candidates, not canonical results.",
            "Keep blocked source, covariance, uncertainty, and row-class gates explicit.",
            "Use task_queue_needed as a maintainer warning, not a CI failure.",
        ),
        source_paths=(
            "tasks/TASK-*.yaml",
            "results/*/*/result.yaml",
            "agent_runs/AGENT-RUN-*/agent_run.yaml",
            "docs/reviews/*.md",
            "docs/task-queue-health-policy.md",
        ),
    )


def science_output_conveyor_json(report: ScienceOutputConveyorReport) -> str:
    """Render report JSON for automation."""
    return json.dumps(report.to_json_data(), indent=2, sort_keys=False)


def render_science_output_conveyor_markdown(report: ScienceOutputConveyorReport) -> str:
    """Render a maintainer-readable Markdown report."""
    lines = [
        "# Science-Output Conveyor Health Report",
        "",
        f"- Advisory only: `{str(report.advisory_only).lower()}`",
        f"- Task queue needed: `{str(report.task_queue_needed).lower()}`",
        f"- READY science tasks: `{report.ready_science_task_count}`",
        f"- READY science surfaces: {', '.join(report.ready_science_surfaces) or 'none'}",
        "",
        "## Recent Task Transitions",
        *_render_tasks(report.recent_task_transitions),
        "",
        "## New Result Artifacts",
        *_render_results(report.new_result_artifacts),
        "",
        "## Sandbox Result Candidates",
        *_render_agent_runs(report.sandbox_result_candidates),
        "",
        "## Blocker Reviews",
        *_render_reviews(report.blocker_reviews),
        "",
        "## Campaign Decisions",
        *_render_reviews(report.campaign_decisions),
        "",
        "## BLOCKED Lane Reasons",
        *_render_tasks(report.blocked_lane_reasons),
        "",
        "## Possible Result Candidates",
        *_render_plain(report.result_candidates),
        "",
        "## Overclaim Risk",
        *_render_plain(report.overclaim_risk),
        "",
        "## Guardrails",
        *_render_plain(report.guardrails),
        "",
        "## Source Paths",
        *_render_code_plain(report.source_paths),
    ]
    return "\n".join(lines)


def _task_number(entry: TaskBoardEntry) -> int:
    return int(entry.task_id.removeprefix("TASK-"))


def _recent_task_transitions(
    board_entries: tuple[TaskBoardEntry, ...],
    *,
    limit: int,
) -> tuple[ConveyorTaskSummary, ...]:
    selected = [
        entry
        for entry in board_entries
        if entry.status in {"DONE", "REVIEW_READY", "IN_PROGRESS"}
    ]
    selected.sort(key=_task_number, reverse=True)
    return tuple(_task_summary(entry) for entry in selected[:limit])


def _task_summary(
    entry: TaskBoardEntry,
    *,
    notes: tuple[str, ...] = (),
) -> ConveyorTaskSummary:
    return ConveyorTaskSummary(
        task_id=entry.task_id,
        title=entry.title,
        status=entry.status,
        type=entry.type,
        priority=entry.priority,
        difficulty=entry.difficulty,
        notes=notes,
    )


def _blocked_lane_reasons(
    root: Path,
    board_entries: tuple[TaskBoardEntry, ...],
    *,
    limit: int,
) -> tuple[ConveyorTaskSummary, ...]:
    blocked = [entry for entry in board_entries if entry.status == "BLOCKED"]
    def rank(entry: TaskBoardEntry) -> tuple[int, int]:
        priority_rank = {"high": 0, "medium": 1, "low": 2}.get(entry.priority, 9)
        return (priority_rank, -_task_number(entry))

    blocked.sort(key=rank)
    summaries: list[ConveyorTaskSummary] = []
    for entry in blocked[:limit]:
        notes: tuple[str, ...] = ()
        path = next((root / "tasks").glob(f"{entry.task_id}-*.yaml"), None)
        if path is not None:
            payload = load_task(path)
            notes = _blocked_reason_notes(payload)
        summaries.append(_task_summary(entry, notes=notes))
    return tuple(summaries)


def _blocked_reason_notes(payload: dict[str, Any]) -> tuple[str, ...]:
    """Extract concise blocker notes from common task YAML fields."""
    notes: list[str] = []
    for field in ("blocked_on", "blocked_by", "blockers", "blocking_tasks", "depends_on"):
        value = payload.get(field)
        if value:
            notes.append(f"{field}: {_compact_yaml_value(value)}")

    planning_context = payload.get("input", {}).get("planning_context", "")
    if isinstance(planning_context, str):
        notes.extend(_blocker_snippets(planning_context))

    for field in ("requirements", "accepted_outputs"):
        for item in payload.get(field, []):
            if isinstance(item, str):
                notes.extend(_blocker_snippets(item))

    deduped: list[str] = []
    for note in notes:
        normalized = " ".join(note.split())
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return tuple(deduped[:3]) or ("No explicit blocker reason found in task YAML.",)


def _compact_yaml_value(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if isinstance(value, dict):
        return ", ".join(f"{key}={val}" for key, val in value.items())
    return str(value)


def _blocker_snippets(text: str) -> tuple[str, ...]:
    snippets: list[str] = []
    for raw_sentence in text.replace("\n", " ").split("."):
        sentence = " ".join(raw_sentence.split())
        lowered = sentence.lower()
        if "blocked" in lowered or "blocker" in lowered or "until" in lowered:
            snippets.append(sentence[:220])
    return tuple(snippets[:2])


def _recent_results(root: Path, *, limit: int) -> tuple[ConveyorResultArtifact, ...]:
    items: list[ConveyorResultArtifact] = []
    for path in sorted((root / "results").glob("EXP-*/RUN-*/result.yaml")):
        payload = load_result(path)
        verification = payload.get("verification", {})
        verification_passed = (
            isinstance(verification, dict) and verification.get("passed") is True
        )
        items.append(
            ConveyorResultArtifact(
                result_id=str(payload["result_id"]),
                task_id=str(payload["task_id"]),
                experiment_id=str(payload["experiment_id"]),
                title=str(payload["title"]),
                verdict=str(payload["best_verdict"]),
                verification_passed=verification_passed,
                generated_at=str(payload["generated_at"]),
                path=_repo_path(root, path),
            )
        )
    items.sort(key=lambda item: (item.generated_at, item.result_id), reverse=True)
    return tuple(items[:limit])


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def _sandbox_result_candidates(root: Path, *, limit: int) -> tuple[ConveyorAgentRun, ...]:
    items: list[ConveyorAgentRun] = []
    for path in sorted((root / "agent_runs").glob("AGENT-RUN-*/agent_run.yaml")):
        payload = _load_yaml(path)
        verdict = str(payload.get("verdict", ""))
        if verdict not in SANDBOX_CANDIDATE_VERDICTS:
            continue
        boundary = payload.get("promotion_boundary", {})
        if isinstance(boundary, dict) and boundary.get("claim_promotion_allowed") is True:
            continue
        items.append(
            ConveyorAgentRun(
                run_id=str(payload.get("id", path.parent.name)),
                task_id=str(payload.get("task_id", "")),
                campaign_id=str(payload.get("campaign_profile_id", "")),
                verdict=verdict,
                path=_repo_path(root, path),
            )
        )
    items.sort(key=lambda item: _run_number(item.run_id), reverse=True)
    return tuple(items[:limit])


def _run_number(run_id: str) -> int:
    try:
        return int(run_id.removeprefix("AGENT-RUN-"))
    except ValueError:
        return -1


def _review_items(
    root: Path,
    terms: tuple[str, ...],
    *,
    limit: int,
) -> tuple[ConveyorReviewItem, ...]:
    items: list[ConveyorReviewItem] = []
    for path in sorted((root / "docs" / "reviews").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        matches = tuple(term for term in terms if term in text)
        if not matches:
            continue
        title = _markdown_title(text, fallback=path.stem)
        items.append(
            ConveyorReviewItem(
                path=_repo_path(root, path),
                title=title,
                matched_terms=matches,
            )
        )
    items.sort(key=lambda item: item.path, reverse=True)
    return tuple(items[:limit])


def _markdown_title(text: str, *, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return fallback


def _result_candidate_refs(
    result_artifacts: tuple[ConveyorResultArtifact, ...],
    sandbox_candidates: tuple[ConveyorAgentRun, ...],
) -> tuple[str, ...]:
    refs: list[str] = []
    for item in result_artifacts:
        if item.verdict in RESULT_CANDIDATE_VERDICTS and item.verification_passed:
            refs.append(
                f"{item.result_id} / {item.task_id}: {item.title} ({item.verdict})"
            )
    for item in sandbox_candidates:
        refs.append(
            f"{item.run_id} / {item.task_id}: sandbox {item.campaign_id} ({item.verdict})"
        )
    return tuple(refs[:10]) or ("No result candidates detected in the configured window.",)


def _overclaim_risk(
    result_artifacts: tuple[ConveyorResultArtifact, ...],
    sandbox_candidates: tuple[ConveyorAgentRun, ...],
    board_entries: tuple[TaskBoardEntry, ...],
) -> tuple[str, ...]:
    notes = [
        "Claim promotion remains blocked unless a separate maintainer review explicitly allows it.",
    ]
    if sandbox_candidates:
        notes.append(
            f"{len(sandbox_candidates)} sandbox candidate(s) need review before any public wording."
        )
    inconclusive_results = [
        item for item in result_artifacts if item.verdict == "INCONCLUSIVE"
    ]
    if inconclusive_results:
        notes.append(
            f"{len(inconclusive_results)} recent canonical result(s) are INCONCLUSIVE and should stay conservative."
        )
    high_priority_blocked = [
        entry
        for entry in board_entries
        if entry.status == "BLOCKED" and entry.priority == "high"
    ]
    if high_priority_blocked:
        notes.append(
            f"{len(high_priority_blocked)} high-priority BLOCKED task(s) still gate campaign maturity."
        )
    return tuple(notes)


def _repo_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _render_tasks(items: tuple[ConveyorTaskSummary, ...]) -> list[str]:
    if not items:
        return ["- None."]
    return [_render_task(item) for item in items]


def _render_task(item: ConveyorTaskSummary) -> str:
    line = (
        f"- `{item.task_id}` - {item.title} "
        f"({item.status}, {item.type}, {item.priority}/{item.difficulty})"
    )
    if item.notes:
        line += f"; notes: {' | '.join(item.notes)}"
    return line


def _render_results(items: tuple[ConveyorResultArtifact, ...]) -> list[str]:
    if not items:
        return ["- None."]
    return [
        f"- `{item.result_id}` / `{item.task_id}` - {item.title} "
        f"({item.verdict}, verification_passed={str(item.verification_passed).lower()}) "
        f"at `{item.path}`"
        for item in items
    ]


def _render_agent_runs(items: tuple[ConveyorAgentRun, ...]) -> list[str]:
    if not items:
        return ["- None."]
    return [
        f"- `{item.run_id}` / `{item.task_id}` - {item.campaign_id} "
        f"({item.verdict}) at `{item.path}`"
        for item in items
    ]


def _render_reviews(items: tuple[ConveyorReviewItem, ...]) -> list[str]:
    if not items:
        return ["- None."]
    return [
        f"- `{item.path}` - {item.title} "
        f"(matched: {', '.join(item.matched_terms)})"
        for item in items
    ]


def _render_plain(items: tuple[str, ...]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- None."]


def _render_code_plain(items: tuple[str, ...]) -> list[str]:
    return [f"- `{item}`" for item in items] if items else ["- None."]
