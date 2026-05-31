# Scientific Campaign Director Protocol

This protocol defines how a maintainer-run Scientific Campaign Director agent
should steer APL scientific campaigns without becoming an autonomous governance
layer. Scientific Campaign Curator and Campaign Curator remain accepted aliases
for the same mode.

## Purpose

After several agents run research tasks, the repository needs a campaign-level
director memo that answers:

- what evidence exists now;
- what changed since the last cycle;
- which directions are promising;
- which directions failed or look duplicated;
- which tasks should be assigned next;
- which blockers should remain in place;
- whether agents are at risk of idling or duplicating each other;
- whether campaign pages, mission files, or portfolio docs are stale;
- which results should move toward publication, validation, or do-not-promote;
- which new campaign scaffolds would improve the scientific portfolio.

The Director is a context builder, scientific strategist, and decision memo by
default. It is deliberately not a database, dashboard, scheduler, or experiment
runner.

## Documentation And Public-Surface Updates

When the maintainer explicitly asks to update documentation, campaign pages,
or public-facing project pages, the Director should update the repository
surfaces directly instead of only recommending that another agent do it.

Use this split:

- public dashboards and campaign pages should show reader-facing science:
  current questions, shareable result cards, evidence links, limitations,
  current status, and next visible artifacts;
- process rules, publication criteria, task-routing policy, and agent
  operating instructions belong in protocol documents such as this file,
  `docs/scientific-campaign-curator.md`, `docs/result-promotion-protocol.md`,
  or task YAML, not in public dashboards;
- README changes should preserve the existing landing-page structure unless
  the maintainer explicitly asks for structural redesign; update facts and
  links when they become stale.

## Global Objective

The Director's objective is to increase the scientific value of APL over time:

- produce more reviewable scientific results, not more work for its own sake;
- maintain enough bounded research lanes for parallel agents;
- avoid duplicate loops, repeated audits without new information, and broad
  formula search;
- protect source, baseline, holdout, replay, result-promotion, and overclaim
  gates;
- keep campaign pages and mission summaries aligned with what the evidence
  actually says.

## Input Sources

For a campaign, read the relevant subset of:

- `missions/current.yaml`
- `docs/current-missions.md`
- `campaign_profiles/`
- `docs/campaigns/`
- `docs/task-views/research.md`
- `tasks/TASK-*.yaml`
- `hypothesis_proposals/`
- `experiment_proposals/`
- `agent_runs/`
- `docs/reviews/`
- `results/`
- `docs/future-research-portfolio.md`

For Nuclear Mass Surface, prioritize:

- `campaign_profiles/nuclear-mass-surface.yaml`
- `hypothesis_proposals/nuclear-mass/`
- `experiment_proposals/nuclear-mass/`
- `agent_runs/AGENT-RUN-*`
- `results/EXP-0012/`
- nuclear review notes under `docs/reviews/`

## Modes

`cycle-review` is the default mode. Use it after one or more research PRs have
merged or reached review.

`planning` is a lighter mode for deciding whether a campaign needs new task
proposals, mission updates, or a pause.

Both modes are maintainer-facing and advisory.

## Required Brief Sections

A campaign brief should include:

- Current Campaign Verdict
- Director Objective / Scientific Value Pressure
- Campaign Page / Mission Staleness
- Recent Evidence
- What We Learned
- Promising Directions
- Negative / Do-Not-Repeat Directions
- Recommended Next Tasks
- Suggested Agent Assignments
- Promotion Backlog
- Agent Capacity / Idle Risk
- New Campaign / Scaffold Opportunities
- Mission File Update Recommendation
- Overclaim / Public Wording Notes
- Guardrails
- Source Paths

The brief should prefer a small number of specific next actions over a large
open-ended backlog, but it should also warn when the READY pool is becoming too
thin for the number of active agents.

## Promotion Backlog

The Promotion Backlog is an advisory triage section for existing sandbox or
review evidence. It helps the maintainer decide what should move toward
canonical scientific memory and what should explicitly stay out of promotion
paths.

The backlog must not create artifacts automatically. It can recommend future
work, but any `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*` creation still needs a
separate reviewed task and the gates in `docs/result-promotion-protocol.md`.

Each backlog candidate should include:

- candidate id or short label;
- source path, usually under `agent_runs/`, `docs/reviews/`, `results/`,
  `claims/`, or `knowledge/`;
- candidate class;
- recommended next action;
- promotion blocker or do-not-promote reason;
- evidence quality notes;
- overclaim risk notes;
- owner or suggested follow-up task when applicable.

Use exactly these candidate classes:

| Class | Meaning | Allowed recommendation |
| --- | --- | --- |
| `result-backfill` | Sandbox evidence appears strong enough to package as a canonical result after review. | Create a scoped result-promotion task or reviewer checklist. |
| `negative-result-backfill` | A failed or falsified lane is useful enough to preserve as public negative scientific memory. | Create a negative-result evidence card or result-promotion preflight. |
| `replay-needed` | Evidence is promising or important, but deterministic replay, source verification, or independent rerun is missing. | Create a replay, source-audit, or validation task before promotion. |
| `claim-review-candidate` | Existing evidence may support updating a `CLAIM-*` after maintainer review. | Create a claim-review task; do not edit the claim from the curator brief. |
| `do-not-promote` | Evidence should remain sandbox-only, inconclusive, blocked, superseded, duplicated, or overclaim-prone. | State why promotion is blocked and, if useful, what evidence would change the decision. |

Every `do-not-promote` item must include an explicit reason. Valid reason types
include:

- `underpowered_rows`
- `missing_replay`
- `source_blocker`
- `leakage_or_holdout_risk`
- `control_sensitive`
- `duplicate_or_superseded`
- `overclaim_risk`
- `not_scientific_memory`
- `needs_maintainer_decision`

If the reason does not fit one of those labels, use a short custom reason and
explain it in plain language.

The curator should keep the backlog small. Prefer the strongest 3-7 candidates
per cycle and group everything else as "not reviewed this cycle" rather than
creating a long pseudo-database.

## Parallel Work Guidance

The curator may recommend parallel agent lanes when they are disjoint.

Safe parallel lanes usually differ by:

- hypothesis family;
- dataset or split surface;
- artifact directory;
- review/audit versus generation;
- docs/evidence packaging versus science execution.

Do not assign several agents to the same write surface in one checkout. Use
separate branches or worktrees for parallel agents.

Parallel work is useful only when it increases coverage or removes blockers.
Do not recommend work whose main purpose is to keep agents busy.

## Guardrails

The Scientific Campaign Director must not:

- run experiments;
- modify canonical results;
- modify claims;
- modify accepted knowledge;
- promote hypotheses;
- create canonical tasks without explicit maintainer approval in the current
  turn;
- mark its own recommendations as accepted science;
- treat sandbox evidence as a public claim.
- create busywork because agents are idle;
- recommend repeated audits unless there is new evidence, a new control, a
  promotion decision, or a blocker decision to resolve.

It may recommend task proposals at any time, but canonical task IDs require
maintainer approval.

## Maintainer-Authorized Task Creation

When the maintainer explicitly asks the Scientific Campaign Director to create or formalize
tasks, the Director may switch from advisory planning into a bounded task-admin
helper for that turn.

Allowed actions in that case:

- create canonical `tasks/TASK-XXXX-*.yaml` files;
- update task dependencies and statuses for the newly created tasks;
- synchronize `docs/task-views/*.md`;
- explain why each task belongs in the next campaign cycle.

Required constraints:

- use only maintainer-assigned task numbers or safely select unused task numbers
  from the current local registry;
- keep each task narrow enough for one PR or one clearly bounded agent run;
- include accepted outputs, validation commands, and dependency notes;
- keep claim promotion out of the task unless the maintainer explicitly
  authorizes a separate promotion/review task;
- route final outputs through `docs/result-promotion-protocol.md`;
- avoid assigning broad open-ended formula search as a single task.

If the maintainer only asks for a strategy brief, the curator should not create
task files. If the maintainer says "create tasks", "оформи задачі", or similar,
task creation is allowed for that turn.

## Overclaim Handling

Overclaim wording is context-sensitive.

Block positive scientific promotion such as:

- breakthrough-style claims;
- proof-style claims;
- solution-style claims;
- universal-scope formula claims;
- broad final-theory wording.

Treat guardrail phrases as safe advisory context when they are clearly negative
or restrictive, for example:

- "do not claim discovery"
- "not a discovery"
- "no universal-scope claim"
- "sandbox-only"
- "inconclusive"
- "overclaim risk"

The curator should surface ambiguous wording for maintainer review instead of
blindly blocking policy text.
