"""Mission-first onboarding helpers for agents and contributors."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import yaml


SUPPORTED_MODES = ("research", "audit", "support", "maintainer")


@dataclass(frozen=True)
class MissionSelection:
    """A compact view of the recommended mission/action pair."""

    mode: str
    mission: dict[str, Any] | None
    action: dict[str, Any] | None
    alternatives: tuple[dict[str, Any], ...]


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
    return tuple(
        action
        for action in mission.get("actions", [])
        if isinstance(action, dict) and action.get("mode") == mode
    )


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


def mission_json(payload: dict[str, Any], mode: str | None = None) -> str:
    """Render a compact JSON response for coding agents."""
    selection = select_mission(payload, mode)
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
        "global_forbidden": payload.get("global_forbidden", []),
    }
    return json.dumps(data, indent=2, sort_keys=False)


def render_human_mission(payload: dict[str, Any], mode: str | None = None) -> str:
    """Render a concise human-readable mission menu."""
    selection = select_mission(payload, mode)
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


def render_agent_prompt(payload: dict[str, Any]) -> str:
    """Render a copy-paste prompt that asks an agent to run the full PR loop."""
    selection = select_mission(payload, None)
    mission_title = selection.mission.get("title") if selection.mission else "the recommended APL mission"
    action_label = selection.action.get("label") if selection.action else "the recommended action"
    task_id = selection.action.get("task_id") if selection.action else None
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
7. Execute the full loop autonomously: inspect evidence, test or audit the hypothesis, preserve negative results, update sandbox/review artifacts, run validation, generate a review bundle, and prepare a PR.
8. Keep outputs sandbox-only unless a canonical task explicitly allows promotion.
9. Do not promote claims, rewrite canonical results, or use breakthrough-style wording.
10. If the work is support/review/closeout rather than research, run the explicit mode: `python3 scripts/apl_mission.py --mode support` or `--mode maintainer`.

Return the selected mission, changed files, validation results, limitations, and PR-ready summary."""
