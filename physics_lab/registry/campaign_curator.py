"""Maintainer-facing Scientific Campaign Director helpers.

The Scientific Campaign Director (formerly Scientific Campaign Curator) is
intentionally advisory: it summarizes campaign state for a maintainer or a
maintainer-run AI agent, recommends scientific direction, and designs the next
research cycle, but it does not execute experiments, promote claims, merge PRs,
or rewrite canonical artifacts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.active_board import TaskBoardEntry, load_board_entries
from physics_lab.registry.campaigns import campaign_catalog_path, load_campaign_catalog
from physics_lab.registry.mission_control import load_current_missions


SUPPORTED_CAMPAIGN_CURATOR_MODES = ("cycle-review", "planning")
SUPPORTED_CAMPAIGN_CURATOR_ROLES = ("director", "curator")
SUPPORTED_CAMPAIGN_CURATOR_OUTPUTS = ("brief", "json", "agent")
ACTIVE_CAMPAIGN_ACTIVITY_STATUSES = frozenset(
    {
        "active",
        "active_limited",
        "active_monitor",
        "active_support",
    }
)

CAMPAIGN_PROPOSAL_DIRS = {
    "nuclear-mass-surface": "nuclear-mass",
    "anharmonic-oscillator": "anharmonic",
    "dimensional-validator": "dimensional-analysis",
    "pendulum-formula-falsification": "pendulum",
    "particle-mass-relations": "particle-mass",
}

CAMPAIGN_KEYWORDS = {
    "nuclear-mass-surface": (
        "nuclear",
        "ame",
        "nuclide",
        "pairing",
        "odd-even",
        "shell",
        "residual",
    ),
    "anharmonic-oscillator": ("anharmonic", "oscillator", "period"),
    "dimensional-validator": ("dimensional", "validator"),
    "pendulum-formula-falsification": ("pendulum",),
}


@dataclass(frozen=True)
class CampaignEvidence:
    """Compact campaign artifact reference."""

    kind: str
    identifier: str
    title: str
    path: str
    verdict: str | None = None
    task_id: str | None = None


@dataclass(frozen=True)
class CampaignTaskRecommendation:
    """Compact live or proposed next step for a campaign."""

    task_id: str | None
    title: str
    priority: str
    difficulty: str
    status: str
    reason: str


@dataclass(frozen=True)
class CampaignCuratorBrief:
    """Serializable campaign steering memo."""

    campaign_id: str
    campaign_title: str
    role_name: str
    accepted_aliases: tuple[str, ...]
    mode: str
    maintainer_facing: bool
    advisory_only: bool
    director_objective: tuple[str, ...]
    portfolio_health_notes: tuple[str, ...]
    campaign_verdict: dict[str, str]
    recent_evidence: tuple[CampaignEvidence, ...]
    what_we_learned: tuple[str, ...]
    promising_directions: tuple[str, ...]
    do_not_repeat: tuple[str, ...]
    recommended_next_tasks: tuple[CampaignTaskRecommendation, ...]
    suggested_agent_assignments: tuple[str, ...]
    mission_file_update_recommendations: tuple[str, ...]
    overclaim_public_wording_notes: tuple[str, ...]
    guardrails: tuple[str, ...]
    source_paths: tuple[str, ...]

    def to_json_data(self) -> dict[str, Any]:
        """Return a JSON-safe representation."""
        return asdict(self)


@dataclass(frozen=True)
class CampaignScopeEntry:
    """One campaign selected for a focused curator session."""

    campaign_id: str
    title: str
    status: str
    domain: str
    surface_type: str
    lifecycle_stage: str
    activity_status: str
    primary_pool: str
    secondary_pools: tuple[str, ...]
    recommended_parallel_agents: int
    current_stage: str


@dataclass(frozen=True)
class CampaignCuratorScopeBrief:
    """Serializable focused campaign-scope memo."""

    scope_kind: str
    role_name: str
    accepted_aliases: tuple[str, ...]
    maintainer_facing: bool
    advisory_only: bool
    filters: dict[str, str | bool | None]
    matching_campaigns: tuple[CampaignScopeEntry, ...]
    session_guidance: tuple[str, ...]
    guardrails: tuple[str, ...]

    def to_json_data(self) -> dict[str, Any]:
        """Return a JSON-safe representation."""
        return asdict(self)


def build_campaign_brief(
    root: Path,
    *,
    campaign_id: str | None = None,
    mode: str = "cycle-review",
    role: str = "director",
) -> CampaignCuratorBrief:
    """Build an advisory campaign-level steering brief."""
    if mode not in SUPPORTED_CAMPAIGN_CURATOR_MODES:
        supported = ", ".join(SUPPORTED_CAMPAIGN_CURATOR_MODES)
        raise ValueError(
            f"Unsupported Scientific Campaign Curator mode: {mode}. Use: {supported}"
        )
    if role not in SUPPORTED_CAMPAIGN_CURATOR_ROLES:
        supported = ", ".join(SUPPORTED_CAMPAIGN_CURATOR_ROLES)
        raise ValueError(
            f"Unsupported campaign role: {role}. Use: {supported}"
        )

    root = root.resolve()
    mission_payload = load_current_missions(root)
    campaign = _select_campaign(mission_payload, campaign_id)
    selected_campaign_id = str(campaign.get("id", campaign_id or "unknown"))
    campaign_title = str(campaign.get("title", selected_campaign_id))
    board_entries = load_board_entries(root)
    source_paths = _source_paths(root, selected_campaign_id)
    evidence = _campaign_evidence(root, selected_campaign_id)
    live_tasks = _recommended_tasks(board_entries, selected_campaign_id, campaign)

    return CampaignCuratorBrief(
        campaign_id=selected_campaign_id,
        campaign_title=campaign_title,
        role_name=(
            "Scientific Campaign Director"
            if role == "director"
            else "Scientific Campaign Curator"
        ),
        accepted_aliases=(
            "Scientific Campaign Curator",
            "campaign-director",
            "campaign-curator",
            "localized equivalents of Scientific Campaign Director/Curator",
        ),
        mode=mode,
        maintainer_facing=True,
        advisory_only=True,
        director_objective=_director_objective(role),
        portfolio_health_notes=_portfolio_health_notes(board_entries, live_tasks),
        campaign_verdict=_campaign_verdict(campaign, evidence, live_tasks),
        recent_evidence=evidence,
        what_we_learned=_what_we_learned(selected_campaign_id, evidence),
        promising_directions=_promising_directions(selected_campaign_id, live_tasks),
        do_not_repeat=_do_not_repeat(selected_campaign_id, campaign),
        recommended_next_tasks=live_tasks,
        suggested_agent_assignments=_agent_assignments(selected_campaign_id, live_tasks),
        mission_file_update_recommendations=_mission_update_recommendations(
            selected_campaign_id,
            campaign,
            live_tasks,
        ),
        overclaim_public_wording_notes=_overclaim_notes(selected_campaign_id),
        guardrails=_guardrails(selected_campaign_id, campaign),
        source_paths=source_paths,
    )


def build_campaign_scope_brief(
    root: Path,
    *,
    pool: str | None = None,
    domain: str | None = None,
    stage: str | None = None,
    active_only: bool = False,
    role: str = "director",
) -> CampaignCuratorScopeBrief:
    """Build an advisory focused-session brief from campaign metadata filters."""
    if role not in SUPPORTED_CAMPAIGN_CURATOR_ROLES:
        supported = ", ".join(SUPPORTED_CAMPAIGN_CURATOR_ROLES)
        raise ValueError(f"Unsupported campaign role: {role}. Use: {supported}")

    root = root.resolve()
    catalog = load_campaign_catalog(campaign_catalog_path(root))
    selected = tuple(
        _scope_entry(campaign)
        for campaign in catalog.get("campaigns", [])
        if _matches_scope_filters(
            campaign,
            pool=pool,
            domain=domain,
            stage=stage,
            active_only=active_only,
        )
    )
    return CampaignCuratorScopeBrief(
        scope_kind="campaign_scope",
        role_name=(
            "Scientific Campaign Director"
            if role == "director"
            else "Scientific Campaign Curator"
        ),
        accepted_aliases=(
            "Scientific Campaign Curator",
            "campaign-director",
            "campaign-curator",
            "localized equivalents of Scientific Campaign Director/Curator",
        ),
        maintainer_facing=True,
        advisory_only=True,
        filters={
            "pool": pool,
            "domain": domain,
            "stage": stage,
            "active_only": active_only,
        },
        matching_campaigns=tuple(
            sorted(
                selected,
                key=lambda item: (
                    item.primary_pool,
                    item.domain,
                    item.lifecycle_stage,
                    item.campaign_id,
                ),
            )
        ),
        session_guidance=_scope_session_guidance(pool=pool, domain=domain, stage=stage),
        guardrails=_scope_guardrails(),
    )


def render_campaign_brief(brief: CampaignCuratorBrief) -> str:
    """Render a maintainer-readable campaign steering memo."""
    lines = [
        "# Scientific Campaign Director Brief",
        "",
        f"Campaign: {brief.campaign_title} (`{brief.campaign_id}`)",
        f"Mode: `{brief.mode}`",
        f"Role: maintainer-run {brief.role_name} for scientific campaign direction",
        f"Aliases: {', '.join(brief.accepted_aliases)}",
        "",
        "## Director Objective",
    ]
    lines.extend(f"- {item}" for item in brief.director_objective)

    lines.extend(
        [
            "",
            "## Portfolio Health / Agent Capacity",
        ]
    )
    lines.extend(f"- {item}" for item in brief.portfolio_health_notes)

    lines.extend(
        [
            "",
            "## Current Campaign Verdict",
        ]
    )
    for key, value in brief.campaign_verdict.items():
        lines.append(f"- {key.replace('_', ' ')}: {value}")

    lines.extend(["", "## Recent Evidence"])
    lines.extend(_render_evidence(evidence) for evidence in brief.recent_evidence)

    lines.extend(["", "## What We Learned"])
    lines.extend(f"- {item}" for item in brief.what_we_learned)

    lines.extend(["", "## Promising Directions"])
    lines.extend(f"- {item}" for item in brief.promising_directions)

    lines.extend(["", "## Negative / Do-Not-Repeat Directions"])
    lines.extend(f"- {item}" for item in brief.do_not_repeat)

    lines.extend(["", "## Recommended Next Tasks"])
    for item in brief.recommended_next_tasks:
        prefix = item.task_id or "proposal"
        lines.append(
            f"- `{prefix}` — {item.title} "
            f"({item.priority}/{item.difficulty}, {item.status}): {item.reason}"
        )

    lines.extend(["", "## Suggested Agent Assignments"])
    lines.extend(f"- {item}" for item in brief.suggested_agent_assignments)

    lines.extend(["", "## Mission File Update Recommendation"])
    lines.extend(f"- {item}" for item in brief.mission_file_update_recommendations)

    lines.extend(["", "## Overclaim / Public Wording Notes"])
    lines.extend(f"- {item}" for item in brief.overclaim_public_wording_notes)

    lines.extend(["", "## Guardrails"])
    lines.extend(f"- {item}" for item in brief.guardrails)

    lines.extend(["", "## Source Paths"])
    lines.extend(f"- `{item}`" for item in brief.source_paths)
    return "\n".join(lines)


def render_campaign_scope_brief(brief: CampaignCuratorScopeBrief) -> str:
    """Render a focused campaign-scope brief."""
    lines = [
        "# Scientific Campaign Director Scope Brief",
        "",
        f"Role: maintainer-run {brief.role_name} focused session",
        f"Filters: `{json.dumps(brief.filters, sort_keys=True)}`",
        "",
        "## Matching Campaigns",
    ]
    if brief.matching_campaigns:
        for campaign in brief.matching_campaigns:
            secondary = (
                f"; secondary pools: {', '.join(campaign.secondary_pools)}"
                if campaign.secondary_pools
                else ""
            )
            lines.append(
                f"- `{campaign.campaign_id}` — {campaign.title} "
                f"({campaign.domain}, {campaign.surface_type}, "
                f"{campaign.lifecycle_stage}, {campaign.activity_status}; "
                f"primary pool: {campaign.primary_pool}{secondary}; "
                f"capacity: {campaign.recommended_parallel_agents})"
            )
    else:
        lines.append("- No campaigns matched these filters.")

    lines.extend(["", "## Session Guidance"])
    lines.extend(f"- {item}" for item in brief.session_guidance)

    lines.extend(["", "## Guardrails"])
    lines.extend(f"- {item}" for item in brief.guardrails)
    return "\n".join(lines)


def campaign_brief_json(brief: CampaignCuratorBrief) -> str:
    """Render campaign brief JSON for agents."""
    return json.dumps(brief.to_json_data(), indent=2, sort_keys=False)


def campaign_scope_brief_json(brief: CampaignCuratorScopeBrief) -> str:
    """Render campaign scope brief JSON for agents."""
    return json.dumps(brief.to_json_data(), indent=2, sort_keys=False)


def render_campaign_role_instructions(brief: CampaignCuratorBrief) -> str:
    """Render activation instructions for a Scientific Campaign Director agent."""
    task_lines = "\n".join(
        f"- {item.task_id or 'proposal'}: {item.title} ({item.reason})"
        for item in brief.recommended_next_tasks
    )
    guardrail_lines = "\n".join(f"- {item}" for item in brief.guardrails)
    objective_lines = "\n".join(f"- {item}" for item in brief.director_objective)
    capacity_lines = "\n".join(f"- {item}" for item in brief.portfolio_health_notes)
    return f"""You are the APL Scientific Campaign Director.
Accepted aliases: Scientific Campaign Curator, campaign-director, campaign-curator, and localized equivalents of Scientific Campaign Director/Curator.
Natural-language requests for a scientific campaign curator/director in any language should map to this mode by concept, not by literal phrase matching.

Campaign:
{brief.campaign_id}

Your role:
Analyze and direct the current scientific campaign state for the maintainer.
You are not a task runner and not a PR review agent. Synthesize recent evidence,
identify promising and failed directions, maintain campaign-page/mission hygiene,
recommend the next research cycle, and keep useful parallel agent lanes
available without creating work-for-work loops.

Global objective:
{objective_lines}

Portfolio / capacity signals:
{capacity_lines}

Recommended next tasks:
{task_lines}

Guardrails:
{guardrail_lines}

Produce:
1. campaign verdict;
2. what we learned from recent runs;
3. promising directions;
4. negative or do-not-repeat directions;
5. recommended next 3-5 tasks or task proposals;
6. which agents should run which lanes;
7. promotion backlog: publish, validate, replay, do-not-promote;
8. what must stay blocked;
9. campaign page / mission / task-queue updates needed;
10. idle-agent or duplicate-work risks;
11. new campaign scaffold opportunities when useful;
12. overclaim risks;
13. whether missions/current.yaml should change.

Do not:
- run experiments;
- promote claims;
- modify canonical results;
- invent unsupported scientific conclusions;
- auto-create canonical task files without maintainer approval;
- create busywork just because agents are available;
- recommend repeated audits without new evidence, new controls, or a promotion/blocker decision;
- recommend broad formula search without holdout, time-split, and robustness gates.
"""


def render_campaign_scope_role_instructions(brief: CampaignCuratorScopeBrief) -> str:
    """Render activation instructions for a focused campaign-scope session."""
    campaign_lines = "\n".join(
        (
            f"- {item.campaign_id}: {item.title} "
            f"({item.domain}; {item.lifecycle_stage}; primary pool {item.primary_pool})"
        )
        for item in brief.matching_campaigns
    )
    guidance_lines = "\n".join(f"- {item}" for item in brief.session_guidance)
    guardrail_lines = "\n".join(f"- {item}" for item in brief.guardrails)
    return f"""You are the APL Scientific Campaign Director for a focused campaign session.
Use the same Scientific Campaign Director role, but restrict attention to the campaign
set selected by the metadata filters below. Do not invent Group A/B/C aliases; use
stable pool/domain/stage/activity metadata from campaign_profiles/_catalog.yaml.

Filters:
{json.dumps(brief.filters, indent=2, sort_keys=True)}

Campaigns in scope:
{campaign_lines or "- No campaigns matched these filters."}

Session guidance:
{guidance_lines}

Guardrails:
{guardrail_lines}
"""


def render_campaign_agent_prompt(brief: CampaignCuratorBrief) -> str:
    """Backward-compatible alias for role activation instructions."""
    return render_campaign_role_instructions(brief)


def render_campaign_scope_agent_prompt(brief: CampaignCuratorScopeBrief) -> str:
    """Backward-compatible naming for scope role activation instructions."""
    return render_campaign_scope_role_instructions(brief)


def _scope_entry(campaign: dict[str, Any]) -> CampaignScopeEntry:
    curator = campaign.get("curator", {})
    agent_capacity = campaign.get("agent_capacity", {})
    return CampaignScopeEntry(
        campaign_id=str(campaign["id"]),
        title=str(campaign["title"]),
        status=str(campaign["status"]),
        domain=str(campaign["domain"]),
        surface_type=str(campaign["surface_type"]),
        lifecycle_stage=str(campaign["lifecycle_stage"]),
        activity_status=str(campaign["activity_status"]),
        primary_pool=str(curator["primary_pool"]),
        secondary_pools=tuple(str(pool) for pool in curator.get("secondary_pools", [])),
        recommended_parallel_agents=int(agent_capacity.get("recommended_parallel_agents", 0)),
        current_stage=str(campaign["current_stage"]),
    )


def _matches_scope_filters(
    campaign: dict[str, Any],
    *,
    pool: str | None,
    domain: str | None,
    stage: str | None,
    active_only: bool,
) -> bool:
    curator = campaign.get("curator", {})
    if pool is not None and curator.get("primary_pool") != pool:
        return False
    if domain is not None and campaign.get("domain") != domain:
        return False
    if stage is not None and campaign.get("lifecycle_stage") != stage:
        return False
    if active_only and campaign.get("activity_status") not in ACTIVE_CAMPAIGN_ACTIVITY_STATUSES:
        return False
    return True


def _scope_session_guidance(
    *,
    pool: str | None,
    domain: str | None,
    stage: str | None,
) -> tuple[str, ...]:
    guidance = [
        "Use this as a focused curator session: analyze only the matching campaigns unless the maintainer explicitly broadens scope.",
        "`--pool` matches curator.primary_pool ownership; secondary_pools are context, not automatic ownership.",
        "Recommend tasks only when they advance source gate, dataset, baseline, holdout, replay/control, negative memory, result promotion, prediction/reveal readiness, or campaign go/no-go.",
        "Campaign transfers between pools require a maintainer or Scientific Director PR; scripts must not mutate pool assignment automatically.",
    ]
    if pool == "source_data_benchmark":
        guidance.append(
            "Prioritize source artifacts, checksums, row readiness, loaders, and holdout manifests before metrics."
        )
    if pool == "prediction_reveal":
        guidance.append(
            "Prioritize frozen baselines, no-peek/reveal gates, reopen conditions, and controls-first negative memory."
        )
    if pool == "verifier_quality_floor":
        guidance.append(
            "Prioritize exact references, falsification boundaries, range limits, and public-safe verifier artifacts."
        )
    if pool == "result_promotion":
        guidance.append(
            "Prioritize Gate A/B routing, replay candidates, negative-result packaging, and maintainer decision backlogs."
        )
    if pool == "frontier_planning":
        guidance.append(
            "Keep work planning-only until source, schema, baseline, holdout, and overclaim gates exist."
        )
    if domain is not None:
        guidance.append(f"Keep the session constrained to domain `{domain}` unless a cross-domain blocker is explicit.")
    if stage is not None:
        guidance.append(f"Treat lifecycle stage `{stage}` as the session boundary for readiness decisions.")
    return tuple(guidance)


def _scope_guardrails() -> tuple[str, ...]:
    return (
        "Do not create letter-coded groups as canonical metadata.",
        "Do not add committed docs/campaign-views/ pages for this scope unless a separate task asks for generated views.",
        "Do not create busywork just because a pool has capacity.",
        "Do not weaken source, holdout, no-peek, control, replay, promotion, or overclaim gates.",
        "Do not transfer a campaign between pools without a maintainer or Scientific Director-approved PR.",
    )


def _director_objective(role: str) -> tuple[str, ...]:
    director_objective = (
        "Increase APL's scientific quality and rate of reviewable scientific results.",
        "Turn agent activity into durable scientific memory: source artifacts, RESULT/PRED candidates, validations, negative results, blockers, and campaign decisions.",
        "Keep enough bounded research lanes available for parallel agents without creating work merely to keep agents busy.",
        "Design new campaign work through source, baseline, holdout, controls, stop conditions, and result-promotion gates.",
    )
    if role == "director":
        return director_objective
    return (
        "Summarize campaign evidence and recommend the next bounded research cycle.",
        "Preserve negative, inconclusive, and blocker evidence as scientific memory.",
        "Keep recommendations advisory unless the maintainer explicitly authorizes task creation.",
    )


def _portfolio_health_notes(
    entries: tuple[TaskBoardEntry, ...],
    tasks: tuple[CampaignTaskRecommendation, ...],
) -> tuple[str, ...]:
    ready_entries = [entry for entry in entries if entry.status == "READY"]
    review_ready_entries = [entry for entry in entries if entry.status == "REVIEW_READY"]
    notes = [
        f"Live READY pool: {len(ready_entries)} tasks; current campaign-aligned recommendations: {len(tasks)}.",
        f"REVIEW_READY pool: {len(review_ready_entries)} tasks; route these to review/closeout, not new executor work.",
    ]
    if len(ready_entries) < 5:
        notes.append(
            "READY pool looks thin for parallel agents; propose source, baseline, validation, or evidence-publication tasks before agents idle."
        )
    else:
        notes.append(
            "READY pool is not empty; prefer high-signal tasks and avoid creating duplicate work."
        )
    if not tasks:
        notes.append(
            "No live campaign-aligned READY tasks were found; propose a bounded task only if it removes a real blocker or opens a useful evidence path."
        )
    return tuple(notes)


def _select_campaign(payload: dict[str, Any], campaign_id: str | None) -> dict[str, Any]:
    missions = [
        mission
        for mission in payload.get("missions", [])
        if isinstance(mission, dict)
    ]
    if campaign_id is None:
        if not missions:
            raise ValueError("missions/current.yaml does not define any missions")
        return sorted(missions, key=lambda item: int(item.get("rank", 999)))[0]
    for mission in missions:
        if mission.get("id") == campaign_id:
            return mission
    return {"id": campaign_id, "title": campaign_id, "risk": "unknown"}


def _proposal_dir(campaign_id: str) -> str:
    return CAMPAIGN_PROPOSAL_DIRS.get(campaign_id, campaign_id)


def _keywords(campaign_id: str) -> tuple[str, ...]:
    return CAMPAIGN_KEYWORDS.get(campaign_id, tuple(campaign_id.split("-")))


def _matches_campaign(text: str, campaign_id: str) -> bool:
    lowered = text.lower()
    if campaign_id == "nuclear-mass-surface" and "non-nuclear" in lowered:
        return False
    return any(keyword in lowered for keyword in _keywords(campaign_id))


def _source_paths(root: Path, campaign_id: str) -> tuple[str, ...]:
    proposal_dir = _proposal_dir(campaign_id)
    candidates = [
        "missions/current.yaml",
        "docs/current-missions.md",
        f"campaign_profiles/{campaign_id}.yaml",
        f"docs/campaigns/{campaign_id}.md",
        "docs/task-views/research.md",
        f"hypothesis_proposals/{proposal_dir}",
        f"experiment_proposals/{proposal_dir}",
        "agent_runs",
        "docs/reviews",
        "results",
    ]
    return tuple(path for path in candidates if (root / path).exists())


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    return payload if isinstance(payload, dict) else {}


def _campaign_evidence(root: Path, campaign_id: str) -> tuple[CampaignEvidence, ...]:
    evidence: list[CampaignEvidence] = []
    evidence.extend(_agent_run_evidence(root, campaign_id))
    evidence.extend(_result_evidence(root, campaign_id))
    evidence.extend(_review_evidence(root, campaign_id))
    return tuple(evidence[:12])


def _agent_run_evidence(root: Path, campaign_id: str) -> list[CampaignEvidence]:
    evidence: list[CampaignEvidence] = []
    for path in sorted((root / "agent_runs").glob("AGENT-RUN-*/agent_run.yaml")):
        payload = _load_yaml(path)
        text = json.dumps(payload, sort_keys=True)
        if payload.get("campaign_profile_id") != campaign_id and not _matches_campaign(
            text,
            campaign_id,
        ):
            continue
        evidence.append(
            CampaignEvidence(
                kind="agent_run",
                identifier=str(payload.get("id", path.parent.name)),
                title=str(payload.get("task_id", "sandbox evidence")),
                path=path.relative_to(root).as_posix(),
                verdict=str(payload.get("verdict", "")) or None,
                task_id=str(payload.get("task_id", "")) or None,
            )
        )
    return evidence[-6:]


def _result_evidence(root: Path, campaign_id: str) -> list[CampaignEvidence]:
    evidence: list[CampaignEvidence] = []
    for path in sorted((root / "results").glob("EXP-*/RUN-*/result.yaml")):
        payload = _load_yaml(path)
        text = json.dumps(payload, sort_keys=True)
        if campaign_id == "nuclear-mass-surface":
            if payload.get("experiment_id") != "EXP-0012":
                continue
        elif not _matches_campaign(text, campaign_id):
            continue
        evidence.append(
            CampaignEvidence(
                kind="result",
                identifier=str(payload.get("result_id", path.parent.name)),
                title=str(payload.get("title", "canonical result")),
                path=path.relative_to(root).as_posix(),
                verdict=str(payload.get("best_verdict", "")) or None,
                task_id=str(payload.get("task_id", "")) or None,
            )
        )
    return evidence[-3:]


def _review_evidence(root: Path, campaign_id: str) -> list[CampaignEvidence]:
    evidence: list[CampaignEvidence] = []
    for path in sorted((root / "docs" / "reviews").glob("*.md")):
        if not _matches_campaign(path.name, campaign_id):
            continue
        evidence.append(
            CampaignEvidence(
                kind="review",
                identifier=path.stem,
                title=path.stem.replace("-", " "),
                path=path.relative_to(root).as_posix(),
            )
        )
    return evidence[-3:]


def _recommended_tasks(
    entries: tuple[TaskBoardEntry, ...],
    campaign_id: str,
    campaign: dict[str, Any],
) -> tuple[CampaignTaskRecommendation, ...]:
    recommendations: list[CampaignTaskRecommendation] = []
    for entry in entries:
        if entry.status != "READY":
            continue
        combined = f"{entry.task_id} {entry.title} {entry.type}"
        if not _matches_campaign(combined, campaign_id):
            continue
        recommendations.append(
            CampaignTaskRecommendation(
                task_id=entry.task_id,
                title=entry.title,
                priority=entry.priority,
                difficulty=entry.difficulty,
                status=entry.status,
                reason="live READY task aligned with this campaign",
            )
        )

    if recommendations:
        return tuple(sorted(recommendations, key=_task_recommendation_sort_key)[:5])

    for action in campaign.get("actions", []):
        if not isinstance(action, dict):
            continue
        if str(action.get("status", "")).lower() in {"done", "blocked"}:
            continue
        if action.get("task_id") is not None:
            continue
        recommendations.append(
            CampaignTaskRecommendation(
                task_id=action.get("task_id"),
                title=str(action.get("label", action.get("id", "campaign action"))),
                priority=str(action.get("priority", "medium")),
                difficulty=str(action.get("difficulty", "medium")),
                status=str(action.get("status", "configured")),
                reason="configured mission action; confirm against live task board",
            )
        )
    return tuple(recommendations[:5])


def _task_recommendation_sort_key(
    recommendation: CampaignTaskRecommendation,
) -> tuple[int, int, int]:
    title = recommendation.title.lower()
    if "sandbox" in title or "hypothesis" in title or "residual" in title:
        lane_rank = 0
    elif "prediction" in title or "registry" in title or "validation" in title:
        lane_rank = 1
    else:
        lane_rank = 2
    priority_rank = {"high": 0, "medium": 1, "low": 2}.get(
        recommendation.priority,
        9,
    )
    difficulty_rank = {"high": 0, "medium": 1, "low": 2}.get(
        recommendation.difficulty,
        9,
    )
    return (lane_rank, priority_rank, difficulty_rank)


def _campaign_verdict(
    campaign: dict[str, Any],
    evidence: tuple[CampaignEvidence, ...],
    tasks: tuple[CampaignTaskRecommendation, ...],
) -> dict[str, str]:
    bottleneck = "maintainer decision on next bounded research lane"
    if tasks:
        bottleneck = f"next candidate task: {tasks[0].task_id or tasks[0].title}"
    return {
        "scientific_value": str(campaign.get("scientific_value", "unknown")),
        "risk": str(campaign.get("risk", "unknown")),
        "campaign_health": "active" if evidence else "needs context collection",
        "current_bottleneck": bottleneck,
        "recommended_next_action": tasks[0].title if tasks else "collect campaign context",
    }


def _what_we_learned(
    campaign_id: str,
    evidence: tuple[CampaignEvidence, ...],
) -> tuple[str, ...]:
    if campaign_id == "nuclear-mass-surface":
        return (
            "Nuclear Mass Surface is the current flagship validation campaign.",
            "Sandbox candidates can look promising on primary holdouts and still remain split-sensitive or inconclusive.",
            "Post-AME2020 checks are retrospective time-split evidence, not strict blind prediction.",
            "Recent shell/neutron-rich lanes are useful negative evidence and should not be repeated without a new bounded family.",
        )
    if evidence:
        return (
            "The campaign has reviewable artifacts that should be summarized before expanding work.",
            "Next work should preserve negative results and avoid duplicate hypothesis families.",
        )
    return ("No campaign evidence was detected; start with context collection and a narrow audit.",)


def _promising_directions(
    campaign_id: str,
    tasks: tuple[CampaignTaskRecommendation, ...],
) -> tuple[str, ...]:
    if campaign_id == "nuclear-mass-surface":
        return (
            "Pairing, odd-even, and odd-A residual corrections as the next bounded sandbox lane.",
            "Prediction registry policy before prospective forecast entries.",
            "Evidence packaging and public-doc sync after each reviewed science wave.",
            "Adversarial review after multiple second-batch outputs exist.",
        )
    if tasks:
        return tuple(f"Complete {task.task_id or task.title}: {task.title}" for task in tasks[:3])
    return ("Create a narrow task proposal before launching new experiments.",)


def _do_not_repeat(campaign_id: str, campaign: dict[str, Any]) -> tuple[str, ...]:
    base = _current_forbidden_items(campaign_id, campaign)
    if campaign_id == "nuclear-mass-surface":
        return base + (
            "Do not run broad nuclear formula search without robustness gates.",
            "Do not rerun shell-aware or neutron-rich families unless the curator identifies a new non-duplicative mechanism.",
            "Do not treat sandbox improvements as claims or accepted knowledge.",
        )
    return base + ("Do not expand the campaign without a maintainer-approved task.",)


def _agent_assignments(
    campaign_id: str,
    tasks: tuple[CampaignTaskRecommendation, ...],
) -> tuple[str, ...]:
    if tasks:
        assignments = [
            _agent_assignment_for_task(index, task)
            for index, task in enumerate(tasks[:4], start=1)
        ]
        assignments.append(
            "Keep one review/closeout-capable agent available if REVIEW_READY work accumulates; do not divert science executors into review unless asked."
        )
        return tuple(assignments)
    return (
        f"No live READY task was found for `{campaign_id}`; assign one Director/Curator pass to propose a bounded unblocker or task queue only if it opens real evidence.",
        "Do not keep agents busy with repeated audits unless a new source, control, promotion gate, or blocker decision exists.",
    )


def _agent_assignment_for_task(
    index: int,
    task: CampaignTaskRecommendation,
) -> str:
    task_ref = task.task_id or task.title
    title = task.title.lower()
    if any(marker in title for marker in ("source", "artifact", "curate", "row")):
        role = "Source-readiness agent"
    elif any(marker in title for marker in ("replay", "validate", "gate")):
        role = "Validation/replay agent"
    elif any(marker in title for marker in ("result", "publish", "prediction")):
        role = "Evidence-publication agent"
    elif any(marker in title for marker in ("audit", "control", "stress")):
        role = "Adversarial-audit agent"
    else:
        role = "Science-execution agent"
    return (
        f"{role} {index}: take `{task_ref}` on a separate branch/worktree; "
        f"expected scope is {task.priority}/{task.difficulty} and must stay within the task contract."
    )


def _mission_update_recommendations(
    campaign_id: str,
    campaign: dict[str, Any],
    tasks: tuple[CampaignTaskRecommendation, ...],
) -> tuple[str, ...]:
    if tasks:
        recommendations = [
            f"Keep `{campaign_id}` as active if `{tasks[0].task_id or tasks[0].title}` is next.",
            "After each merge, update mission wording only if the flagship action or blockers changed.",
            "Do not hand-edit a single stale task id as the sole source of truth; prefer live task candidates.",
        ]
        if campaign_id == "nuclear-mass-surface":
            recommendations.append(
                "Clean up stale blockers that still describe TASK-0196/TASK-0197 prerequisites as unmet."
            )
        return tuple(recommendations)
    return (
        "No live task was found for this campaign; consider a maintainer-approved task proposal.",
        f"Confirm whether `{campaign.get('id', campaign_id)}` should remain ranked as active.",
    )


def _overclaim_notes(campaign_id: str) -> tuple[str, ...]:
    notes = (
        "Risky words are review signals, not automatic blockers in guardrail contexts.",
        "Block positive breakthrough-style, proof-style, solution-style, or universal-scope claims.",
        "Allow negative/policy contexts such as 'do not claim' or 'not a discovery'.",
    )
    if campaign_id == "nuclear-mass-surface":
        return notes + (
            "Use sandbox-only, retrospective time-split, inconclusive, and bounded-candidate wording.",
            "Never describe residual candidates as a universal nuclear mass formula.",
        )
    return notes


def _guardrails(campaign_id: str, campaign: dict[str, Any]) -> tuple[str, ...]:
    return (
        "Scientific Campaign Director is advisory and maintainer-facing.",
        "Do not execute experiments from this mode.",
        "Do not modify canonical results, claims, or accepted knowledge.",
        "Do not auto-create canonical task files without maintainer approval.",
        "Keep sandbox evidence sandbox-only until a reviewed promotion task exists.",
        *_current_forbidden_items(campaign_id, campaign),
    )


def _current_forbidden_items(
    campaign_id: str,
    campaign: dict[str, Any],
) -> tuple[str, ...]:
    items = tuple(str(item) for item in campaign.get("forbidden", []))
    if campaign_id != "nuclear-mass-surface":
        return items
    stale_fragments = (
        "without a committed row-level holdout dataset",
        "before the real time-split benchmark is reviewed",
    )
    return tuple(
        item
        for item in items
        if not any(fragment in item for fragment in stale_fragments)
    )


def _render_evidence(evidence: CampaignEvidence) -> str:
    verdict = f", verdict `{evidence.verdict}`" if evidence.verdict else ""
    task = f", task `{evidence.task_id}`" if evidence.task_id else ""
    return (
        f"- `{evidence.kind}` `{evidence.identifier}` — {evidence.title}"
        f"{task}{verdict}: `{evidence.path}`"
    )
