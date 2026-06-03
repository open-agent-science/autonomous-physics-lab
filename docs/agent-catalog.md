# Agent Catalog

This page is the shortest repository-native map of the agent roles, helper
flows, and maintainer automation surfaces that already exist in APL.

Use it when you want to answer:

- "Which agent should I use for this kind of work?"
- "Is this a real workflow we already support, or only a future idea?"
- "Where is the canonical documentation for this agent path?"

## Quick Split

APL currently has three broad families:

- contributor-facing task agents
- maintainer-facing review and automation agents
- repository-architecture-facing roles (cross-protocol design and audit)

The contributor side helps humans and coding agents complete scoped work.
The maintainer side helps with review, queue triage, post-merge closeout, and
campaign-level research steering. The architecture side keeps protocols,
schemas, agent-role definitions, and safety guardrails coherent across the
whole repository.

## Role Profiles Under `agents/`

Each active agent role has a compact, activation-ready YAML profile under
[`agents/<role-id>.yaml`](../agents/). The profile is the single source
of truth for the role's identity, scope, goals, allowed tools, scripts,
restrictions, and cross-role invocation rules. The narrative in this
catalog and the deep authoritative protocols under `docs/` remain the
detail layer; the profile is what an agent loads at session start when
the maintainer asks it to act in that role.

Profile format and conventions are documented in
[`agents/README.md`](../agents/README.md); the canonical shape is
[`agents/AGENT-TEMPLATE.yaml`](../agents/AGENT-TEMPLATE.yaml) and the
JSON schema is `physics_lab/schemas/agent.schema.json`.

When an agent path below has a matching profile, it is linked under a
`Role profile:` line. Paths without a profile carry
`Role profile: not yet authored`.

## Contributor-Facing Agent Paths

### 1. Canonical Task Execution Agent (Researcher)

Use this path when a contributor wants to pick one `READY` task and carry it
to `REVIEW_READY` on a normal task branch.

- Typical work: code, docs, workflow tasks, campaign packaging, validation
- Role profile: [`agents/researcher.yaml`](../agents/researcher.yaml)
- Primary docs:
  - [AGENTS.md](../AGENTS.md)
  - [agent-task-protocol.md](./agent-task-protocol.md)
  - [agent-operating-model.md](./agent-operating-model.md)

Status: active and used routinely.

### 2. Task Proposal Agent

Use this path when no existing `READY` task fits and the contributor needs to
propose a new narrow task without guessing a canonical `TASK-XXXX` id.

- Typical work: proposal-only PRs under `tasks/proposals/`
- Role profile: [`agents/task-proposal-agent.yaml`](../agents/task-proposal-agent.yaml)
- Primary docs:
  - [task-proposal-protocol.md](./task-proposal-protocol.md)
  - [agent-task-protocol.md](./agent-task-protocol.md)

Status: active and used routinely.

### 3. Scientific Microtask Agent

Use this path for one small queue item or a tiny same-queue batch from
`tasks/microtasks/`.

- Typical work: notes, dataset audits, challenge-set updates, small campaign
  support steps
- Role profile: [`agents/microtask-agent.yaml`](../agents/microtask-agent.yaml)
- Primary docs:
  - [scientific-micro-task-protocol.md](./scientific-micro-task-protocol.md)
  - [agent-scientific-work-mode.md](./agent-scientific-work-mode.md)
  - [use-your-agent.md](./use-your-agent.md)

Status: active and used routinely.

### 4. New Contributor / Use-Your-Agent Path

Use this path when a human is new to the repository and wants a safe first
entrypoint before choosing a task or microtask.

- Typical work: onboarding, low-risk starter tasks, narrow contributor setup
- Role profile: not yet authored (onboarding helper rather than a single
  activated role; promotion to a dedicated profile would require a
  separate task)
- Primary docs:
  - [use-your-agent.md](./use-your-agent.md)
  - [agent-work-menu.md](./agent-work-menu.md)
  - [task views](task-views/research.md)

Status: active and recommended for new contributors.

## Maintainer-Facing Agent Paths

### 5. Maintainer Review And Closeout Agent

Use this path when the maintainer wants a structured PR review or post-merge
task closeout recommendation.

- Typical work: review open PRs, classify them, run closeout after merge
- Role profile: [`agents/review-agent.yaml`](../agents/review-agent.yaml)
- Primary docs:
  - [maintainer-review-agent.md](./maintainer-review-agent.md)
  - [review-checklists/maintainer-pr-review-checklist.md](./review-checklists/maintainer-pr-review-checklist.md)
  - [review-checklists/task-closeout-checklist.md](./review-checklists/task-closeout-checklist.md)

Status: active and heavily used.

### 6. Scientific Campaign Director / Campaign Curator

Use this path when the maintainer wants a campaign-level research brief after a
wave of hypothesis proposals, sandbox runs, reviews, or result artifacts.

- Typical work: summarize campaign evidence, identify promising and failed
  directions, recommend the next 2-5 tasks, suggest parallel agent lanes,
  maintain campaign-page hygiene, and keep useful agent work available without
  creating busywork
- Role profile: [`agents/scientific-curator.yaml`](../agents/scientific-curator.yaml)
- Primary docs:
  - [scientific-campaign-curator.md](./scientific-campaign-curator.md)
  - [campaign-curator-protocol.md](./campaign-curator-protocol.md)
- Helper script:
  - `python3 scripts/apl_campaign_curator.py --campaign nuclear-mass-surface`
  - `python3 scripts/apl_campaign_curator.py --role director --campaign nuclear-mass-surface`
  - `python3 scripts/apl_campaign_curator.py --role curator --campaign nuclear-mass-surface`
  - `python3 scripts/apl_campaign_curator.py --role director --campaign nuclear-mass-surface --output agent`

Status: active maintainer-facing advisory mode. It must not run experiments,
promote claims, create canonical tasks without explicit maintainer approval, or
replace PR review. If the maintainer explicitly asks it to create or formalize
tasks, it may act as a bounded task-admin helper for that turn.

### 7. Maintainer Routine / Manual / Action Modes

These are execution modes for maintainer automation rather than separate
scientific agents.

- Routine mode: periodic queue sweep
- Manual mode: targeted maintainer request
- Action mode: bounded low-risk actions such as closeout PR preparation
- Role profile: not yet authored (operating modes layered on top of the
  Review Agent role rather than a separate single role)

Primary docs:
- [automation/maintainer-routine-mode.md](./automation/maintainer-routine-mode.md)
- [automation/maintainer-manual-mode.md](./automation/maintainer-manual-mode.md)
- [automation/maintainer-action-mode.md](./automation/maintainer-action-mode.md)

Status: active as file-backed operating modes.

### 8. Proposal Triage / PR Queue / Closeout Sweep Roles

These are documented maintainer automation roles used to organize routine work:

- proposal acceptance triage
- open PR queue triage
- task closeout sweep

- Role profile: not yet authored (automation roles layered on top of the
  Review Agent role; promotion to dedicated profiles is a future task)
- Primary doc:
  - [maintainer-automation-architecture.md](./maintainer-automation-architecture.md)

Status: real and documented, but best understood as automation roles layered
on top of the maintainer review system rather than completely separate product
surfaces.

## Repository-Architecture-Facing Agent Paths

### 9. Architect

Use this path when the maintainer wants cross-protocol design, bottleneck
analysis, safety review, refactoring proposals, or agent-role organisation
across the repository as a whole.

- Typical work: protocol audits, schema and template hygiene, agent-role
  design, removal of unused or duplicated artifacts, bottleneck analysis,
  cross-protocol PR review
- Role profile: [`agents/architect.yaml`](../agents/architect.yaml)
- Primary docs:
  - [strategy.md](./strategy.md)
  - [result-promotion-protocol.md](./result-promotion-protocol.md)
  - [agent-task-protocol.md](./agent-task-protocol.md)
  - [agent-operating-model.md](./agent-operating-model.md)

Status: active. Proactive mode: the Architect may open small cleanup PRs
on own initiative; larger architectural changes (new schemas, role
redefinitions, protocol rewrites, removing or renaming a public artifact)
still require joint decision with the maintainer before execution. The
Architect never merges and never promotes scientific claims.

### 10. Data Acquisition / Source-Pinning

Use this path when the maintainer wants to acquire, snapshot, pin, checksum, or
license-clear a published data source for a campaign, or to prepare a runbook so
the maintainer can run a key-gated or access-restricted fetch locally.

- Typical work: bounded public/key-free snapshot acquisition with checksum and
  source manifest entry; runbook preparation for key-gated maintainer-run
  fetches; precise access/license blocker preservation
- Role profile: [`agents/data-acquisition.yaml`](../agents/data-acquisition.yaml)
- Primary docs:
  - [source-acquisition-lane.md](./source-acquisition-lane.md)
  - [published-source-dataset-standard.md](./published-source-dataset-standard.md)
  - [fresh-data-intake-protocol.md](./fresh-data-intake-protocol.md)

Status: active, maintainer-run. Never curates rows, never commits secrets or
copyrighted artifacts, never live-fetches inside benchmark code, and never
promotes claims. Rows require a separate row-curation task.

## Planned Future Specialized Agents

The repository also names several future automation surfaces:

- code review sweep agent
- security sweep agent
- release readiness agent

- Role profile: not yet authored for any of the planned roles.
- Primary doc:
  - [maintainer-automation-architecture.md](./maintainer-automation-architecture.md)

Status: planned, not the first thing a new contributor should rely on.

## Practical Reading Paths

### If you are a new human contributor

Read:

1. [use-your-agent.md](./use-your-agent.md)
2. [agent-task-protocol.md](./agent-task-protocol.md)
3. [task views](task-views/research.md)

### If you are a coding agent starting normal task work

Read:

1. [AGENTS.md](../AGENTS.md)
2. [agent-task-protocol.md](./agent-task-protocol.md)
3. [agent-operating-model.md](./agent-operating-model.md)
4. the selected `tasks/TASK-XXXX-*.yaml`

### If you are a maintainer reviewing PRs

Read:

1. [maintainer-review-agent.md](./maintainer-review-agent.md)
2. [maintainer-automation-architecture.md](./maintainer-automation-architecture.md)
3. the appropriate file in [automation/](./automation)

### If you are a maintainer steering a research campaign

Read:

1. [scientific-campaign-curator.md](./scientific-campaign-curator.md)
2. [campaign-curator-protocol.md](./campaign-curator-protocol.md)
3. run `python3 scripts/apl_campaign_curator.py --campaign nuclear-mass-surface`

### If you are an architect-mode agent

Read:

1. [`agents/architect.yaml`](../agents/architect.yaml) — role profile
2. [strategy.md](./strategy.md)
3. [result-promotion-protocol.md](./result-promotion-protocol.md)
4. [agent-task-protocol.md](./agent-task-protocol.md)

## One-Sentence Rule

If you are not sure which path applies:

- contributors start from `READY` tasks or microtasks
- maintainers start from the review agent for PRs, closeout for merged tasks,
  and Scientific Campaign Curator for research-cycle steering
- proposals are for ideas, not for active implementation
