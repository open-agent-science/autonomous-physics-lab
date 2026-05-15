"""Mission-first onboarding helpers for agents and contributors."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import random
from typing import Any, Optional

import yaml

from physics_lab.registry.active_board import TaskBoardEntry, load_board_entries


SUPPORTED_MODES = ("research", "audit", "support", "maintainer")
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
DIFFICULTY_RANK = {"low": 0, "medium": 1, "high": 2}
DIFFICULTY_TIME_ESTIMATES = {
    "low": "~5 min",
    "medium": "~5-10 min",
    "high": "~15-20 min",
}
RANDOMIZER = random.SystemRandom()
RESEARCH_TASK_MARKERS = (
    "scientific",
    "research",
    "benchmark",
    "audit",
    "validation",
    "replay",
    "autonomous",
    "result",
)
SUPPORT_TASK_MARKERS = (
    "documentation",
    "workflow",
    "maintainer",
    "contributor",
    "code_quality",
    "repository",
    "agent",
)


@dataclass(frozen=True)
class MissionSelection:
    """A compact view of the recommended mission/action pair."""

    mode: str
    mission: dict[str, Any] | None
    action: dict[str, Any] | None
    alternatives: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class MissionTaskCandidate:
    """A live task recommendation derived from canonical task YAML files."""

    task_id: str
    title: str
    type: str
    priority: str
    difficulty: str
    status: str
    mode: str
    parallel_hint: str

    def to_json(self) -> dict[str, str]:
        """Return a compact JSON-safe representation."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "type": self.type,
            "priority": self.priority,
            "difficulty": self.difficulty,
            "status": self.status,
            "mode": self.mode,
            "parallel_hint": self.parallel_hint,
            "estimated_time": _estimated_time(self.difficulty),
        }


def load_current_missions(root: Path) -> dict[str, Any]:
    """Load the machine-readable mission board."""
    path = root / "missions" / "current.yaml"
    with path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("missions/current.yaml must contain a mapping")
    return payload


def _mission_actions_for_mode(
    mission: dict[str, Any],
    mode: str,
) -> tuple[dict[str, Any], ...]:
    inactive_statuses = {"blocked", "done", "review_ready"}
    return tuple(
        action
        for action in mission.get("actions", [])
        if isinstance(action, dict)
        and action.get("mode") == mode
        and str(action.get("status", "")).lower() not in inactive_statuses
    )


def _task_mode(entry: TaskBoardEntry) -> str:
    task_type = entry.type.lower()
    if any(marker in task_type for marker in RESEARCH_TASK_MARKERS):
        return "research"
    if any(marker in task_type for marker in SUPPORT_TASK_MARKERS):
        return "support"
    return "support"


def _parallel_hint(entry: TaskBoardEntry) -> str:
    return (
        "Parallel-safe if assigned to a separate branch/worktree and no other "
        f"agent is editing {entry.type} artifacts."
    )


def _estimated_time(difficulty: str) -> str:
    return DIFFICULTY_TIME_ESTIMATES.get(difficulty, "~5-20 min")


def _candidate_sort_key(candidate: MissionTaskCandidate) -> tuple[int, int, int, str, int]:
    return (
        *_candidate_rank_key(candidate),
        int(candidate.task_id.removeprefix("TASK-")),
    )


def _candidate_rank_key(candidate: MissionTaskCandidate) -> tuple[int, int, int, str]:
    mode_rank = 0 if candidate.mode == "research" else 1
    return (
        mode_rank,
        PRIORITY_RANK.get(candidate.priority, 9),
        DIFFICULTY_RANK.get(candidate.difficulty, 9),
        candidate.type,
    )


def _ranked_candidates(
    candidates: list[MissionTaskCandidate],
    *,
    shuffle_equal_rank: bool,
) -> tuple[MissionTaskCandidate, ...]:
    ordered = sorted(candidates, key=_candidate_sort_key)
    if not shuffle_equal_rank:
        return tuple(ordered)

    ranked: list[MissionTaskCandidate] = []
    index = 0
    while index < len(ordered):
        rank = _candidate_rank_key(ordered[index])
        group: list[MissionTaskCandidate] = []
        while index < len(ordered) and _candidate_rank_key(ordered[index]) == rank:
            group.append(ordered[index])
            index += 1
        if len(group) > 1:
            RANDOMIZER.shuffle(group)
        ranked.extend(group)
    return tuple(ranked)


def task_candidates(
    root: Path,
    *,
    mode: str = "research",
    limit: int = 5,
    shuffle_equal_rank: Optional[bool] = None,
) -> tuple[MissionTaskCandidate, ...]:
    """Return live task candidates from canonical task YAML files.

    The mission YAML remains useful for stable campaign lanes and guardrails,
    but live work options should come from the task registry so agents do not
    depend on a hand-maintained "current task" field.
    """
    entries = load_board_entries(root)
    candidates: list[MissionTaskCandidate] = []
    for entry in entries:
        if entry.status != "READY":
            continue
        entry_mode = _task_mode(entry)
        if mode in {"research", "audit"} and entry_mode != "research":
            continue
        if mode == "support" and entry_mode != "support":
            continue
        candidates.append(
            MissionTaskCandidate(
                task_id=entry.task_id,
                title=entry.title,
                type=entry.type,
                priority=entry.priority,
                difficulty=entry.difficulty,
                status=entry.status,
                mode=entry_mode,
                parallel_hint=_parallel_hint(entry),
            )
        )

    if mode == "research" and candidates:
        # Keep support READY tasks visible as lower-ranked alternatives when
        # research READY tasks exist, but never let them decide whether the
        # research fallback should fire.
        for entry in entries:
            if entry.status != "READY":
                continue
            entry_mode = _task_mode(entry)
            if entry_mode != "support":
                continue
            candidates.append(
                MissionTaskCandidate(
                    task_id=entry.task_id,
                    title=entry.title,
                    type=entry.type,
                    priority=entry.priority,
                    difficulty=entry.difficulty,
                    status=entry.status,
                    mode=entry_mode,
                    parallel_hint=_parallel_hint(entry),
                )
            )

    if mode in {"research", "audit"} and not candidates:
        # If there is no science-lane READY task, show the highest-priority
        # READY support tasks as alternatives without pretending they are the
        # research default.
        for entry in entries:
            if entry.status != "READY":
                continue
            candidates.append(
                MissionTaskCandidate(
                    task_id=entry.task_id,
                    title=entry.title,
                    type=entry.type,
                    priority=entry.priority,
                    difficulty=entry.difficulty,
                    status=entry.status,
                    mode=_task_mode(entry),
                    parallel_hint=_parallel_hint(entry),
                )
            )

    should_shuffle = mode in {"research", "audit"} if shuffle_equal_rank is None else shuffle_equal_rank
    return _ranked_candidates(candidates, shuffle_equal_rank=should_shuffle)[:limit]


def select_mission(payload: dict[str, Any], mode: str | None = None) -> MissionSelection:
    """Select the highest-ranked mission/action for a mode."""
    selected_mode = mode or str(payload.get("default_mode", "research"))
    if selected_mode not in SUPPORTED_MODES:
        raise ValueError(f"Unsupported mission mode: {selected_mode}")

    if selected_mode in {"support", "maintainer"}:
        actions_key = "support_actions" if selected_mode == "support" else "maintainer_actions"
        actions = tuple(action for action in payload.get(actions_key, []) if isinstance(action, dict))
        return MissionSelection(
            mode=selected_mode,
            mission=None,
            action=actions[0] if actions else None,
            alternatives=actions[1:],
        )

    missions = tuple(
        mission
        for mission in sorted(
            payload.get("missions", []),
            key=lambda item: int(item.get("rank", 999)),
        )
        if isinstance(mission, dict)
    )
    for mission in missions:
        actions = _mission_actions_for_mode(mission, selected_mode)
        if not actions:
            continue
        recommended = next(
            (action for action in actions if bool(action.get("recommended"))),
            actions[0],
        )
        alternatives = tuple(action for action in actions if action is not recommended)
        for other_mission in missions:
            if other_mission is mission:
                continue
            alternatives += _mission_actions_for_mode(other_mission, selected_mode)
        return MissionSelection(
            mode=selected_mode,
            mission=mission,
            action=recommended,
            alternatives=alternatives,
        )

    return MissionSelection(mode=selected_mode, mission=None, action=None, alternatives=())


def mission_json(payload: dict[str, Any], mode: str | None = None, *, root: Path | None = None) -> str:
    """Render a compact JSON response for coding agents."""
    selection = select_mission(payload, mode)
    live_candidates = task_candidates(root, mode=selection.mode) if root is not None else ()
    data = {
        "default_mode": payload.get("default_mode"),
        "selected_mode": selection.mode,
        "policy": payload.get("policy", {}),
        "recommended": {
            "mission": selection.mission.get("id") if selection.mission else None,
            "mission_title": selection.mission.get("title") if selection.mission else None,
            "action": selection.action.get("id") if selection.action else None,
            "label": selection.action.get("label") if selection.action else None,
            "task_id": selection.action.get("task_id") if selection.action else None,
            "priority": selection.action.get("priority") if selection.action else None,
            "difficulty": selection.action.get("difficulty") if selection.action else None,
            "expected_outputs": selection.action.get("expected_outputs", [])
            if selection.action
            else [],
            "forbidden": selection.mission.get("forbidden", []) if selection.mission else [],
        },
        "alternatives": [
            {
                "action": action.get("id"),
                "label": action.get("label"),
                "priority": action.get("priority"),
                "task_id": action.get("task_id"),
            }
            for action in selection.alternatives
        ],
        "live_task_candidates": [candidate.to_json() for candidate in live_candidates],
        "task_visibility_policy": {
            "executor_modes": "Only READY tasks are executable candidates.",
            "review_ready": "REVIEW_READY tasks are hidden from executor recommendations; use maintainer review or closeout mode instead.",
            "blocked": "BLOCKED, DONE, and REJECTED tasks are never offered as executor candidates.",
        },
        "parallel_work_policy": {
            "single_checkout": "Use one active task at a time in a single checkout.",
            "parallel_agents": "Use separate branches or git worktrees and choose disjoint artifact surfaces.",
            "coordination": "Do not guess new task ids during parallel work; use proposals or maintainer-assigned tasks.",
            "candidate_order": "Equal-rank research/audit candidates may rotate so parallel agents do not all pick the same first task.",
        },
        "global_forbidden": payload.get("global_forbidden", []),
    }
    return json.dumps(data, indent=2, sort_keys=False)


def render_human_mission(payload: dict[str, Any], mode: str | None = None, *, root: Path | None = None) -> str:
    """Render a concise human-readable mission menu."""
    selection = select_mission(payload, mode)
    live_candidates = task_candidates(root, mode=selection.mode) if root is not None else ()
    mode_info = payload.get("modes", {}).get(selection.mode, {})
    lines = [
        "APL Mission Control",
        "",
        f"Mode: {mode_info.get('label', selection.mode)}",
        str(mode_info.get("description", "")),
        "",
    ]

    if selection.mission is not None:
        task_suffix = (
            f" ({selection.action['task_id']})"
            if selection.action and selection.action.get("task_id")
            else ""
        )
        lines.extend(
            [
                "Recommended now:",
                f"{selection.mission.get('title')} — {selection.action.get('label') if selection.action else 'no action'}{task_suffix}",
                "",
                "Why this mission:",
            ]
        )
        lines.extend(f"- {item}" for item in selection.mission.get("why_now", []))
        lines.extend(["", "Guardrails:"])
        lines.extend(f"- {item}" for item in selection.mission.get("forbidden", []))
    elif selection.action is not None:
        suffix = (
            f" ({selection.action['task_id']})"
            if selection.action.get("task_id")
            else ""
        )
        lines.extend(["Recommended now:", f"{selection.action.get('label')}{suffix}", ""])
        if selection.action.get("command"):
            lines.append(f"Command: {selection.action['command']}")
    else:
        lines.append("No recommended action is configured for this mode.")

    if selection.alternatives:
        lines.extend(["", "Alternatives:"])
        for index, action in enumerate(selection.alternatives[:5], start=1):
            suffix = f" ({action['task_id']})" if action.get("task_id") else ""
            lines.append(f"{index}. {action.get('label')}{suffix}")

    if live_candidates:
        lines.extend(["", "Live task candidates from task registry:"])
        for index, candidate in enumerate(live_candidates, start=1):
            lines.append(
                f"{index}. {candidate.task_id} — {candidate.title} "
                f"[{candidate.priority}/{candidate.difficulty}, "
                f"{_estimated_time(candidate.difficulty)}, {candidate.mode}]"
            )
        lines.extend(
            [
                "",
                "Parallel work:",
                "- one local checkout should usually run one task at a time",
                "- multiple agents can work in parallel via separate branches or worktrees",
                "- avoid overlapping artifact surfaces in parallel PRs",
                "- equal-rank research/audit task options may rotate between runs",
            ]
        )
    lines.extend(
        [
            "",
            "Task visibility:",
            "- executor agents should list and choose only READY tasks",
            "- REVIEW_READY tasks belong to maintainer review/closeout, not new executor work",
            "- BLOCKED, DONE, and REJECTED tasks are not available to start",
        ]
    )

    lines.extend(
        [
            "",
            "Suggested commands:",
            "- python3 scripts/apl_mission.py --json",
            "- python3 scripts/apl_mission.py --agent-prompt",
            "- python3 scripts/apl_mission.py --mode support",
            "- python3 scripts/apl_mission.py --mode maintainer",
        ]
    )
    return "\n".join(lines)


def render_agent_prompt(payload: dict[str, Any], *, root: Path | None = None) -> str:
    """Render a copy-paste prompt that asks an agent to run the full PR loop."""
    selection = select_mission(payload, None)
    live_candidates = task_candidates(root, mode=selection.mode) if root is not None else ()
    mission_title = selection.mission.get("title") if selection.mission else "the recommended APL mission"
    action_label = selection.action.get("label") if selection.action else "the recommended action"
    task_id = selection.action.get("task_id") if selection.action else None
    candidate_block = ""
    if live_candidates:
        rendered_candidates = "\n".join(
            f"- {candidate.task_id}: {candidate.title} "
            f"({candidate.priority}/{candidate.difficulty}, {_estimated_time(candidate.difficulty)})"
            for candidate in live_candidates
        )
        candidate_block = (
            "\n\nCurrent executable READY task candidates from the task registry:\n"
            f"{rendered_candidates}"
        )
    task_instruction = (
        f"Use canonical task {task_id} and create its task branch before editing files."
        if task_id
        else "If the action has no task_id, create a task proposal before editing implementation files."
    )
    return f"""You are working in Autonomous Physics Lab.

Start in Agent First Research Mode.

1. Read AGENTS.md and docs/agent-task-protocol.md.
2. Run `python3 scripts/apl_mission.py --json`.
3. Choose the recommended research mission unless the maintainer gave a stricter task.
4. Recommended mission now: {mission_title}.
5. Recommended action now: {action_label}.
6. {task_instruction}
7. Execute the full loop autonomously: inspect evidence, test or audit the hypothesis, preserve negative results, update sandbox/review artifacts, run validation, generate a review bundle, then commit only after the files are ready, push the task branch, and open a draft PR when GitHub access is available.
7a. Missing `gh`, missing GitHub auth, or restricted network access is not a reason to stop before editing files. At the end, try repository helpers, available GitHub/MCP tools, or GitHub CLI; if a needed command is blocked by permissions, request permission/escalation for that command before falling back to exact maintainer-run commands for `git push`, `gh pr create`, PR-number review, and `gh pr ready`.
8. Keep outputs sandbox-only unless a canonical task explicitly allows promotion.
9. Do not promote claims, rewrite canonical results, or use breakthrough-style wording.
10. If the work is support/review/closeout rather than research, run the explicit mode: `python3 scripts/apl_mission.py --mode support` or `--mode maintainer`.
11. If multiple agents are working locally, use separate branches or worktrees and choose disjoint artifact surfaces.
12. When reporting available tasks, list only executable READY tasks. Do not offer REVIEW_READY tasks as options for executor work; those belong to maintainer review or closeout.
{candidate_block}

Return the selected mission, changed files, validation results, limitations, and PR-ready summary."""


def render_onboarding_prompt(payload: dict[str, Any], *, root: Path | None = None) -> str:
    """Render a copy-paste prompt for a guided first agent response."""
    selection = select_mission(payload, None)
    live_candidates = task_candidates(root, mode=selection.mode) if root is not None else ()
    mission_title = selection.mission.get("title") if selection.mission else "the recommended APL mission"
    action_label = selection.action.get("label") if selection.action else "the recommended action"
    candidate_block = ""
    if live_candidates:
        rendered_candidates = "\n".join(
            f"- {candidate.task_id}: {candidate.title} "
            f"({candidate.priority}/{candidate.difficulty}, {_estimated_time(candidate.difficulty)})"
            for candidate in live_candidates
        )
        candidate_block = (
            "\n\nCurrent executable READY task candidates from the task registry:\n"
            f"{rendered_candidates}"
        )
    return f"""You are working in Autonomous Physics Lab.

Start in Agent First Research Mode with onboarding.

1. Read AGENTS.md and docs/agent-task-protocol.md.
2. Run `python3 scripts/apl_mission.py --json`.
3. Do not edit files yet.
4. Briefly explain why the recommended mission is scientifically useful.
5. Recommended mission now: {mission_title}.
6. Recommended action now: {action_label}.
7. Show 3-5 executable READY options with estimated time and difficulty.
8. Recommend one option, ask whether to start it, and wait for the user's choice.
9. After the user chooses, run the selected task autonomously through branch, implementation, validation, review bundle, and final commit after the files are ready. Then push and open a draft PR using repository helpers, available GitHub/MCP tools, or GitHub CLI when access is available; if a needed command is blocked by permissions, request permission/escalation for that command. If PR creation still cannot complete, do not stop before editing files, and instead provide exact maintainer-run `git push`, `gh pr create`, PR-number review, and `gh pr ready` commands at the end.
10. Keep outputs sandbox-only unless a canonical task explicitly allows promotion.
11. Do not promote claims, rewrite canonical results, or use breakthrough-style wording.
{candidate_block}

When the work is complete, summarize what changed, the scientific or workflow value of the result, validation results, limitations, and the best next task to continue."""
