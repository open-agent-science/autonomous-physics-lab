"""Helpers for source-of-truth-driven repository snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

import yaml

from physics_lab.registry.active_board import STATUS_SECTION_ORDER, load_board_entries
from physics_lab.registry.experiments import load_experiment
from physics_lab.registry.results import load_result


@dataclass(frozen=True)
class SnapshotContext:
    """Canonical git context for a repository snapshot run."""

    invocation_root: Path
    canonical_root: Path
    repo_name: str
    current_branch: str
    head_commit: str
    default_base_ref: str


@dataclass(frozen=True)
class ResultSnapshot:
    """Compact summary of one canonical result artifact."""

    result_id: str
    experiment_id: str
    run_id: str
    task_id: str
    best_verdict: str
    generated_at: str
    path: str
    title: str


@dataclass(frozen=True)
class AgentRunSnapshot:
    """Compact summary of one agent-run evidence artifact."""

    run_id: str
    campaign_id: str
    task_id: str
    status: str
    verdict: str
    sandbox_only: str
    next_step: str
    path: str


def build_snapshot_context(root: Path) -> SnapshotContext:
    """Return canonical repository identity for snapshot output."""
    invocation_root = root.resolve()
    common_dir_raw = _run_git(invocation_root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    common_dir = Path(common_dir_raw).resolve() if common_dir_raw else None
    if common_dir is not None and common_dir.name == ".git":
        canonical_root = common_dir.parent
    else:
        canonical_root_raw = _run_git(invocation_root, "rev-parse", "--show-toplevel")
        canonical_root = Path(canonical_root_raw).resolve() if canonical_root_raw else invocation_root
    current_branch = _run_git(invocation_root, "branch", "--show-current") or "detached"
    head_commit = _run_git(invocation_root, "rev-parse", "--short=12", "HEAD") or "unknown"

    default_base_ref = "origin/main"
    if not _git_ref_exists(invocation_root, default_base_ref):
        current_ref = current_branch if current_branch != "detached" else "HEAD"
        default_base_ref = current_ref

    return SnapshotContext(
        invocation_root=invocation_root,
        canonical_root=canonical_root,
        repo_name=canonical_root.name,
        current_branch=current_branch,
        head_commit=head_commit,
        default_base_ref=default_base_ref,
    )


def render_authority_notes(root: Path) -> str:
    """Return markdown notes describing snapshot authority layers."""
    context = build_snapshot_context(root)
    lines = [
        "### Snapshot Authority",
        "",
        f"- canonical_repo_name: `{context.repo_name}`",
        f"- canonical_repo_root: `{context.canonical_root}`",
        f"- invocation_path: `{context.invocation_root}`",
        f"- current_branch: `{context.current_branch}`",
        f"- head_commit: `{context.head_commit}`",
        f"- default_base_ref: `{context.default_base_ref}`",
        "",
        "Authoritative current-state sections below are generated from canonical",
        "`tasks/TASK-*.yaml`, `experiments/*.yaml`, and `results/*/*/result.yaml`",
        "artifacts. Maintainer-facing docs such as `docs/status.md` and",
        "`docs/next-steps.md` remain useful context, but they are secondary and",
        "may lag behind the structured repository state.",
        "",
        "Large tree, task, result, and knowledge dumps remain included later as",
        "archive context for deep audits.",
    ]
    return "\n".join(lines)


def render_current_state_summary(root: Path, *, recent_done_limit: int = 5, recent_result_limit: int = 5) -> str:
    """Render a markdown summary of current structured repository state."""
    entries = load_board_entries(root.resolve())
    experiments = _load_experiment_rows(root)
    results = _load_recent_results(root, limit=recent_result_limit)

    lines = [
        "### Current Task State",
        "",
    ]
    for status, _header in STATUS_SECTION_ORDER:
        section_entries = [entry for entry in entries if entry.status == status]
        lines.append(f"- {status}: {len(section_entries)}")

    ready_entries = [entry for entry in entries if entry.status == "READY"]
    review_ready_entries = [entry for entry in entries if entry.status == "REVIEW_READY"]
    blocked_entries = [entry for entry in entries if entry.status == "BLOCKED"]
    done_entries = [entry for entry in entries if entry.status == "DONE"]

    lines.extend(_render_entry_list("READY now", ready_entries, limit=6))
    lines.extend(_render_entry_list("REVIEW_READY now", review_ready_entries, limit=6))
    lines.extend(_render_entry_list("BLOCKED now", blocked_entries, limit=6))
    lines.extend(_render_entry_list("Recently DONE", done_entries, limit=recent_done_limit, merged=True))

    lines.extend(
        [
            "",
            "### Current Experiment State",
            "",
        ]
    )
    experiment_status_counts: dict[str, int] = {}
    for experiment in experiments:
        experiment_status_counts[experiment["status"]] = experiment_status_counts.get(experiment["status"], 0) + 1
    for status in sorted(experiment_status_counts):
        lines.append(f"- {status}: {experiment_status_counts[status]}")
    lines.extend(_render_experiment_list(experiments))

    lines.extend(
        [
            "",
            "### Recent Result Surface",
            "",
        ]
    )
    if results:
        for result in results:
            lines.append(
                f"- `{result.result_id}` / `{result.experiment_id}` / `{result.run_id}` "
                f"({result.best_verdict}) [{result.task_id}] - {result.path}"
            )
            lines.append(f"  {result.title} | generated_at `{result.generated_at}`")
    else:
        lines.append("- none")
    return "\n".join(lines)


def render_strategic_context_map(root: Path, *, recent_agent_run_limit: int = 8, blocked_limit: int = 10) -> str:
    """Render the project-stage map needed by strategy and curator agents."""
    root = root.resolve()
    entries = load_board_entries(root)
    mission_payload = _load_yaml(root / "missions" / "current.yaml")
    missions = _mission_rows(mission_payload)
    agent_runs = _load_recent_agent_runs(root, limit=recent_agent_run_limit)
    result_tiers = _result_review_tier_counts(root)
    prediction_count = len(
        [
            path
            for path in (root / "prediction_registry").glob("*/*.yaml")
            if path.name.startswith("PRED-") and "TEMPLATE" not in path.name
        ]
    )

    lines = [
        "### Strategic Snapshot Front Page",
        "",
        "_Generated from structured repository files; use later archive sections for deep audit context._",
    ]

    lines.extend(_render_repository_state_signals(entries, missions, agent_runs, result_tiers, prediction_count))
    lines.extend(_render_campaign_at_a_glance(missions))
    lines.extend(_render_recent_scientific_learnings(missions, agent_runs))
    lines.extend(_render_recommended_parallel_allocation(missions))
    lines.extend(_render_context_file_map(root))
    lines.extend(_render_campaign_rows(missions))
    lines.extend(_render_task_queue_snapshot(entries))
    lines.extend(_render_agent_run_rows(agent_runs))
    lines.extend(_render_scientific_memory_snapshot(result_tiers, prediction_count))
    lines.extend(_render_blocked_work_snapshot(root, entries, limit=blocked_limit))
    return "\n".join(lines)


def _render_entry_list(title: str, entries: list, *, limit: int, merged: bool = False) -> list[str]:
    lines = ["", f"### {title}", ""]
    if not entries:
        lines.append("- none")
        return lines

    sorted_entries = sorted(entries, key=lambda entry: entry.task_number, reverse=merged)
    for entry in sorted_entries[:limit]:
        if merged:
            lines.append(f"- `{entry.task_id}` - {entry.title}")
        else:
            lines.append(
                f"- `{entry.task_id}` - {entry.title} "
                f"(`{entry.type}`, priority `{entry.priority}`, difficulty `{entry.difficulty}`)"
            )
    return lines


def _render_context_file_map(root: Path) -> list[str]:
    file_map = [
        ("README.md", "public landing page and shortest project pitch"),
        ("AGENTS.md", "agent rules, project guardrails, and mandatory workflow expectations"),
        ("CONTEXT.md", "downloadable single-file context bundle for fresh agents"),
        ("docs/status.md", "human-facing current project status and public-alpha posture"),
        ("docs/current-missions.md", "campaign overview for maintainers and contributors"),
        ("missions/current.yaml", "machine-readable mission priority, campaign recommendations, and guardrails"),
        ("docs/strategy.md", "strategic compass and long-term positioning"),
        ("docs/open-agent-network.md", "public collaboration model for many agents working on shared campaigns"),
        ("docs/agent-operating-model.md", "shared execution model for agent-first research and support work"),
        ("docs/result-promotion-protocol.md", "routing rules for sandbox, RESULT, PRED, CLAIM, and knowledge outputs"),
        ("docs/scientific-memory-review-tiers.md", "meaning of AGENT_PUBLISHED, AGENT_VALIDATED, and maintainer-reviewed tiers"),
        ("docs/result-artifacts-index.md", "index of canonical result artifacts and their review posture"),
        ("docs/negative-results-registry.md", "preserved falsifications, failures, and do-not-repeat evidence"),
        ("docs/fresh-data-readiness-matrix.md", "cross-campaign readiness view for fresh-data source surfaces"),
        ("docs/fresh-data-intake-protocol.md", "source-artifact intake workflow for new scientific data surfaces"),
        ("docs/agent-task-protocol.md", "canonical branch, PR, validation, and task execution flow"),
        ("docs/maintainer-review-agent.md", "review-agent protocol for PR review and merge readiness"),
        ("docs/review-checklists/task-closeout-checklist.md", "post-merge closeout and safe unblock checklist"),
        ("agents/README.md", "agent role profile index for review, closeout, curator, and executor modes"),
        ("docs/task-views/research.md", "generated lightweight research task queue"),
        ("docs/task-views/support.md", "generated infrastructure/support task queue"),
        ("docs/task-views/blocked.md", "generated blocked-task view for unblock/supersede sweeps"),
        ("campaign_profiles/", "campaign metadata used by curator and mission tooling"),
        ("docs/campaigns/", "campaign narrative docs and source-surface explanations"),
        ("agent_runs/", "sandbox/evidence run outputs from autonomous agents"),
        ("docs/reviews/", "review-agent, scientific review, and decision artifacts"),
        ("results/", "canonical reproducible RESULT artifacts"),
        ("prediction_registry/", "frozen prediction entries and reveal-readiness state"),
        ("tasks/TASK-*.yaml", "canonical task contracts and lifecycle states"),
    ]
    lines = ["", "#### Critical Files And Directories", ""]
    for path, description in file_map:
        exists = (root / path).exists() if not path.endswith("*.yaml") else bool((root / "tasks").glob("TASK-*.yaml"))
        status = "present" if exists else "missing"
        lines.append(f"- `{path}` ({status}) — {description}.")
    return lines


def _render_repository_state_signals(
    entries: tuple,
    missions: list[dict],
    agent_runs: list[AgentRunSnapshot],
    result_tiers: dict[str, int],
    prediction_count: int,
) -> list[str]:
    status_counts: dict[str, int] = {}
    for entry in entries:
        status_counts[entry.status] = status_counts.get(entry.status, 0) + 1
    tier_text = ", ".join(f"{tier} {count}" for tier, count in sorted(result_tiers.items())) or "none"
    task_text = ", ".join(
        f"{status} {status_counts.get(status, 0)}"
        for status in ("READY", "REVIEW_READY", "BLOCKED", "DONE")
    )
    return [
        "",
        "#### Repository State Signals",
        "",
        f"- Campaign rows in `missions/current.yaml`: {len(missions)}.",
        f"- Task status counts: {task_text}.",
        f"- Recent agent-run artifacts included here: {len(agent_runs)}.",
        f"- Canonical RESULT review tiers: {tier_text}.",
        f"- Frozen prediction entries: {prediction_count}.",
    ]


def _render_campaign_at_a_glance(missions: list[dict]) -> list[str]:
    lines = [
        "",
        "#### Campaigns At A Glance",
        "",
        "| Campaign | Status | Can agents run now? | Best next action | Blocker | Risk |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    if not missions:
        lines.append("| none | unknown | unknown | see `missions/current.yaml` | unknown | unknown |")
        return lines
    for mission in missions[:8]:
        lines.append(
            "| "
            f"{_table_cell(str(mission.get('title', mission.get('id', 'unknown'))))} | "
            f"{_table_cell(str(mission.get('status', 'unknown')))} | "
            f"{_table_cell(_can_agents_run_now(mission))} | "
            f"{_table_cell(_one_line(str(mission.get('recommendation', '')), limit=120))} | "
            f"{_table_cell(_mission_blocker(mission))} | "
            f"{_table_cell(str(mission.get('risk', mission.get('scientific_value', 'unknown'))))} |"
        )
    return lines


def _render_recent_scientific_learnings(
    missions: list[dict],
    agent_runs: list[AgentRunSnapshot],
) -> list[str]:
    lines = [
        "",
        "#### Recent Scientific Learnings",
        "",
    ]
    for mission in missions[:6]:
        why_now = mission.get("why_now") or []
        if why_now:
            title = mission.get("title", mission.get("id", "unknown"))
            lines.append(f"- {title}: {_one_line(str(why_now[-1]))}")
    if agent_runs:
        verdict_counts: dict[str, int] = {}
        for run in agent_runs:
            verdict_counts[run.verdict] = verdict_counts.get(run.verdict, 0) + 1
        counts = ", ".join(f"{verdict} {count}" for verdict, count in sorted(verdict_counts.items()))
        lines.append(f"- Recent agent-run verdict mix: {counts}.")
    if len(lines) == 3:
        lines.append("- No recent campaign learnings were found in `missions/current.yaml` or `agent_runs/`.")
    return lines


def _render_recommended_parallel_allocation(missions: list[dict]) -> list[str]:
    active_missions = [mission for mission in missions if _can_agents_run_now(mission) != "no"]
    lines = [
        "",
        "#### Recommended Parallel Allocation",
        "",
    ]
    for index, mission in enumerate(active_missions[:4], start=1):
        title = str(mission.get("title", mission.get("id", "unknown")))
        run_state = _can_agents_run_now(mission)
        recommendation = _one_line(str(mission.get("recommendation", "")), limit=150)
        lines.append(f"- Agent {index}: {title} (`{run_state}`) — {recommendation}")
    lines.append("- One additional agent, when available: review/curator/closeout pass over recent evidence and blockers.")
    lines.append("- Support/release/docs agents should run only when they unblock science or public-readiness work.")
    return lines


def _can_agents_run_now(mission: dict) -> str:
    status = str(mission.get("status", "")).lower()
    if "blocked" in status:
        return "no"
    if any(marker in status for marker in ("source", "readiness", "planned", "prepare")):
        return "limited"
    return "yes"


def _mission_blocker(mission: dict) -> str:
    actions = mission.get("actions") or []
    for action in actions:
        if not isinstance(action, dict):
            continue
        gated_by = action.get("gated_by") or []
        if gated_by:
            return _one_line("gated by: " + ", ".join(str(item) for item in gated_by[:3]), limit=120)
        expected_outputs = action.get("expected_outputs") or []
        for output in expected_outputs:
            text = str(output)
            if any(marker in text.lower() for marker in ("blocked", "until")):
                return _one_line(text, limit=120)
    forbidden = mission.get("forbidden") or []
    if forbidden:
        return _one_line("guardrail: " + str(forbidden[0]), limit=120)
    return "none"


def _table_cell(value: str) -> str:
    return value.replace("|", "/")


def _render_campaign_rows(missions: list[dict]) -> list[str]:
    lines = ["", "#### Campaign Motion", ""]
    if not missions:
        lines.append("- No campaigns found in `missions/current.yaml`.")
        return lines
    for mission in missions:
        action_counts = _mission_action_counts(mission)
        recommendation = _one_line(mission.get("recommendation", ""))
        status = mission.get("status", "unknown")
        title = mission.get("title", mission.get("id", "unknown"))
        rank = mission.get("rank", "?")
        lines.append(f"- `rank {rank}` `{mission.get('id', 'unknown')}` — {title} (`{status}`).")
        if recommendation:
            lines.append(f"  Recommendation: {recommendation}")
        if action_counts:
            counts = ", ".join(f"{key} {value}" for key, value in sorted(action_counts.items()))
            lines.append(f"  Action state: {counts}.")
        why_now = mission.get("why_now") or []
        if why_now:
            lines.append(f"  Latest useful context: {_one_line(str(why_now[-1]))}")
    return lines


def _render_task_queue_snapshot(entries: tuple) -> list[str]:
    ready_entries = [entry for entry in entries if entry.status == "READY"]
    review_ready_entries = [entry for entry in entries if entry.status == "REVIEW_READY"]
    lines = ["", "#### Current Work Queue", ""]
    lines.append(f"- READY tasks: {len(ready_entries)}.")
    lines.append(f"- REVIEW_READY tasks: {len(review_ready_entries)}.")
    if ready_entries:
        lines.append("- Highest-signal READY candidates:")
        for entry in sorted(ready_entries, key=_task_sort_key)[:8]:
            lines.append(
                f"  - `{entry.task_id}` — {entry.title} "
                f"(`{entry.type}`, priority `{entry.priority}`, difficulty `{entry.difficulty}`)."
            )
    else:
        lines.append("- No READY tasks are currently available.")
    return lines


def _render_agent_run_rows(agent_runs: list[AgentRunSnapshot]) -> list[str]:
    lines = ["", "#### Recent Agent Evidence", ""]
    if not agent_runs:
        lines.append("- No `agent_runs/AGENT-RUN-*` artifacts found.")
        return lines
    for run in agent_runs:
        lines.append(
            f"- `{run.run_id}` / `{run.campaign_id}` / `{run.task_id}` — "
            f"status `{run.status}`, verdict `{run.verdict}`, sandbox_only `{run.sandbox_only}`."
        )
        if run.next_step:
            lines.append(f"  Next step: {_one_line(run.next_step)}")
        lines.append(f"  Artifact: `{run.path}`.")
    return lines


def _render_scientific_memory_snapshot(result_tiers: dict[str, int], prediction_count: int) -> list[str]:
    lines = ["", "#### Scientific Memory Conveyor", ""]
    if result_tiers:
        tier_text = ", ".join(f"{tier} {count}" for tier, count in sorted(result_tiers.items()))
        lines.append(f"- Canonical RESULT review tiers: {tier_text}.")
    else:
        lines.append("- Canonical RESULT review tiers: none found.")
    lines.append(f"- Frozen prediction entries: {prediction_count}.")
    lines.append("- Use `docs/result-promotion-protocol.md` before routing any new scientific output.")
    lines.append("- Use `docs/scientific-memory-review-tiers.md` to distinguish evidence from endorsed interpretation.")
    return lines


def _render_blocked_work_snapshot(root: Path, entries: tuple, *, limit: int) -> list[str]:
    blocked_entries = [entry for entry in entries if entry.status == "BLOCKED"]
    lines = ["", "#### Blocked Work To Re-check", ""]
    if not blocked_entries:
        lines.append("- No BLOCKED tasks found.")
        return lines
    for entry in sorted(blocked_entries, key=_task_sort_key)[:limit]:
        payload = _load_task_payload(root, entry.task_id)
        blocker = _extract_blocker_note(payload)
        lines.append(f"- `{entry.task_id}` — {entry.title}.")
        if blocker:
            lines.append(f"  Blocker/context: {_one_line(blocker)}")
    if len(blocked_entries) > limit:
        lines.append(f"- ... plus {len(blocked_entries) - limit} more BLOCKED tasks in `docs/task-views/blocked.md`.")
    return lines


def _mission_rows(payload: dict) -> list[dict]:
    rows = payload.get("missions", []) if isinstance(payload, dict) else []
    if not isinstance(rows, list):
        return []
    return sorted(
        [row for row in rows if isinstance(row, dict)],
        key=lambda row: int(row.get("rank", 999)),
    )


def _mission_action_counts(mission: dict) -> dict[str, int]:
    counts: dict[str, int] = {}
    actions = mission.get("actions") or []
    if not isinstance(actions, list):
        return counts
    for action in actions:
        if not isinstance(action, dict):
            continue
        status = str(action.get("status", "open"))
        counts[status] = counts.get(status, 0) + 1
    return counts


def _task_sort_key(entry) -> tuple[int, int, int]:
    priority_rank = {"high": 0, "medium": 1, "low": 2}.get(entry.priority, 9)
    difficulty_rank = {"low": 0, "medium": 1, "high": 2}.get(entry.difficulty, 9)
    return (priority_rank, difficulty_rank, entry.task_number)


def _load_recent_agent_runs(root: Path, *, limit: int) -> list[AgentRunSnapshot]:
    rows: list[AgentRunSnapshot] = []
    for path in sorted((root / "agent_runs").glob("AGENT-RUN-*/agent_run.yaml")):
        payload = _load_yaml(path)
        promotion_boundary = payload.get("promotion_boundary") or {}
        rows.append(
            AgentRunSnapshot(
                run_id=str(payload.get("id", path.parent.name)),
                campaign_id=str(payload.get("campaign_profile_id", "unknown")),
                task_id=str(payload.get("task_id", "unknown")),
                status=str(payload.get("status", "unknown")),
                verdict=str(payload.get("verdict", "unknown")),
                sandbox_only=str(payload.get("sandbox_only", "unknown")),
                next_step=str(promotion_boundary.get("required_next_step", "")),
                path=path.relative_to(root).as_posix(),
            )
        )
    rows.sort(key=lambda row: _numeric_suffix(row.run_id), reverse=True)
    return rows[:limit]


def _result_review_tier_counts(root: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in sorted((root / "results").glob("*/*/result.yaml")):
        payload = _load_yaml(path)
        tier = str(payload.get("review_tier", "LEGACY_UNTIERED"))
        counts[tier] = counts.get(tier, 0) + 1
    return counts


def _load_task_payload(root: Path, task_id: str) -> dict:
    matches = sorted((root / "tasks").glob(f"{task_id}-*.yaml"))
    if not matches:
        return {}
    return _load_yaml(matches[0])


def _extract_blocker_note(payload: dict) -> str:
    if not payload:
        return ""
    input_payload = payload.get("input") or {}
    candidates: list[str] = []
    for key in ("blocker", "blocked_reason", "planning_context"):
        value = payload.get(key) or input_payload.get(key)
        if value:
            candidates.append(str(value))
    requirements = payload.get("requirements") or []
    for requirement in requirements:
        text = str(requirement)
        lowered = text.lower()
        if any(marker in lowered for marker in ("blocked", "blocker", "until", "external", "source", "reveal")):
            candidates.append(text)
    return candidates[0] if candidates else ""


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def _one_line(value: str, *, limit: int = 220) -> str:
    text = " ".join(str(value).split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def _numeric_suffix(value: str) -> int:
    digits = "".join(char for char in value if char.isdigit())
    return int(digits) if digits else -1


def _render_experiment_list(experiments: list[dict[str, str]]) -> list[str]:
    lines = ["", "### Canonical Experiments", ""]
    if not experiments:
        lines.append("- none")
        return lines

    for experiment in experiments:
        lines.append(
            f"- `{experiment['id']}` - {experiment['title']} "
            f"(`{experiment['status']}`, domain `{experiment['domain']}`)"
        )
    return lines


def _load_experiment_rows(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted((root / "experiments").glob("EXP-*.yaml")):
        payload = load_experiment(path)
        rows.append(
            {
                "id": str(payload["id"]),
                "title": str(payload["title"]),
                "status": str(payload["status"]),
                "domain": str(payload["domain"]),
            }
        )
    return rows


def _load_recent_results(root: Path, *, limit: int) -> list[ResultSnapshot]:
    rows: list[ResultSnapshot] = []
    for path in sorted((root / "results").glob("*/*/result.yaml")):
        payload = load_result(path)
        rows.append(
            ResultSnapshot(
                result_id=str(payload["result_id"]),
                experiment_id=str(payload["experiment_id"]),
                run_id=str(payload["run_id"]),
                task_id=str(payload.get("task_id", "unknown")),
                best_verdict=str(payload["best_verdict"]),
                generated_at=str(payload.get("generated_at", "")),
                path=path.relative_to(root).as_posix(),
                title=str(payload["title"]),
            )
        )
    rows.sort(key=lambda row: (row.generated_at, row.path), reverse=True)
    return rows[:limit]


def _run_git(root: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return completed.stdout.strip()


def _git_ref_exists(root: Path, ref: str) -> bool:
    try:
        subprocess.run(
            ["git", "rev-parse", "--verify", ref],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return False
    return True
