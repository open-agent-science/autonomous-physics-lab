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
- reduce duplicated status surfaces, digest pages, and task-list filler that
  create future cleanup work;
- review whether the scientific workflow and campaign architecture are helping
  or slowing the path to reviewable results;
- avoid duplicate loops, repeated audits without new information, and broad
  formula search;
- protect source, baseline, holdout, replay, result-promotion, and overclaim
  gates;
- keep campaign pages and mission summaries aligned with what the evidence
  actually says.

## Science-Output Funnel Requirement

Each Director cycle should identify the nearest durable scientific output for
every active campaign it discusses. The output can be a positive result, but it
does not have to be. Negative results, source blockers, reusable datasets,
independent replays, and campaign stop/go decisions are valid scientific
outputs when they prevent weaker future work or make evidence reusable.

Use this routing order before recommending new candidate generation:

1. **Promotion/replay check:** Is there existing sandbox evidence that should
   be replayed, promoted, rejected, or frozen as negative memory?
2. **Source-to-row check:** Is the campaign blocked because rows, checksums,
   source locator, license, uncertainty, covariance, or direct-vs-derived class
   are unresolved?
3. **Dataset/publication check:** Is there a source-pinned dataset candidate
   that needs reuse metadata, split sensitivity, or result-promotion review?
4. **Factory/adapter check:** Would a reusable bounded factory or adapter
   shorten a repeated workflow across campaigns without weakening controls?
5. **Only then candidate generation:** Add new hypothesis or factory attempts
   only when the upstream gates are clear and the candidate family is disjoint
   from exhausted lanes.

If a campaign has a strong diagnostic signal, the Director must recommend a
route decision: replay, ablation, result-promotion preflight, or explicit
do-not-promote memory. Leaving it as "interesting" without a next gate is a
failure of direction.

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

For focused director sessions across more than one campaign, use
`campaign_profiles/_catalog.yaml` metadata rather than informal group aliases.
The supported filters are:

- `curator.primary_pool`;
- `domain`;
- `lifecycle_stage`;
- `activity_status` via the `--active-only` helper.

`secondary_pools` are handoff context, not automatic ownership. A campaign can
move to another primary pool only through an explicit maintainer or Scientific
Director PR that updates its campaign profile and explains the transfer reason.

## Modes

`cycle-review` is the default mode. Use it after one or more research PRs have
merged or reached review.

`planning` is a lighter mode for deciding whether a campaign needs new task
proposals, mission updates, or a pause.

Both modes are maintainer-facing and advisory.

## Focused Sessions

When the maintainer wants several curator sessions to split the portfolio, use
the campaign curator helper instead of naming Group A/B/C:

```bash
python3 scripts/apl_campaign_curator.py --pool source_data_benchmark
python3 scripts/apl_campaign_curator.py --domain astrophysics --active-only
python3 scripts/apl_campaign_curator.py --stage source_readiness --output json
python3 scripts/apl_campaign_curator.py --pool prediction_reveal --output agent
```

Focused sessions should analyze only the matching campaigns unless the
maintainer explicitly broadens scope. They should still obey the normal
scientific-output filter: recommend only work that advances a source gate,
dataset, baseline, holdout, replay/control, negative memory, result promotion,
prediction/reveal readiness, or campaign go/no-go decision.

Do not create committed `docs/campaign-views/` files just to support focused
sessions. Those views are a separate product decision; focused sessions can use
the catalog and CLI filters directly.

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
- Scientific Architecture / Workflow Efficiency
- Promotion Backlog
- Agent Capacity / Idle Risk
- New Campaign / Scaffold Opportunities
- Mission File Update Recommendation
- Overclaim / Public Wording Notes
- Guardrails
- Source Paths

When the maintainer asks for a portfolio-level cycle rather than a single
campaign brief, include a short `Science-Output Funnel` section that lists the
nearest durable output and bottleneck for each active campaign.

The brief should prefer a small number of specific next actions over a large
open-ended backlog, but it should also warn when the READY pool is becoming too
thin for the number of active agents.

## Deduplication And Scientific Output Filter

Before recommending a new task or documentation surface, the Director must
apply this filter:

1. **Deduplicate first.** If the information belongs on an existing campaign
   page, public dashboard, mission file, task, review note, result artifact, or
   protocol, update that surface instead of creating a new digest/status page.
2. **Name the output path.** Every recommended task must advance at least one
   concrete scientific output path: source gate, dataset, baseline, holdout,
   replay/control, negative memory, result promotion, prediction/reveal
   readiness, or campaign go/no-go decision.
3. **Reject filler.** Do not add tasks merely to reach a numeric READY target,
   keep agents occupied, or make a task list look substantial.
4. **Prefer replacement over addition.** A new documentation surface is
   acceptable only if it removes a drift source, replaces an older surface, or
   directly unlocks a scientific workflow.

When a proposed task fails this filter, the Director should say so plainly and
either fold the update into an existing task/page or drop it.

## Scientific Architecture / Workflow Efficiency Review

Every Director cycle should include a short architecture/workflow judgment when
the campaign is not producing results at the desired rate. The purpose is to
decide whether the current process is an efficient path to scientific output,
not to design infrastructure by default.

The Director should check:

- whether source intake, dataset contracts, holdout rules, replay gates, or
  result-promotion gates are the current bottleneck;
- whether task shapes are too broad, too fragmented, duplicated, or sequenced
  poorly for parallel agents;
- whether agents are spending most effort on documentation/audit loops instead
  of source gates, baselines, controls, replay, negative memory, or promotion
  decisions;
- whether a reusable adapter, protocol, or queue would reduce repeated work
  across campaigns without creating a new drift surface;
- which smallest workflow change would most improve time-to-result while
  preserving source provenance, controls, and conservative wording.

Recommended workflow changes must be tied to a concrete scientific output path.
If the best answer is "run the existing task, not more architecture," the
Director should say that.

Workflow efficiency must be a scientific non-regression. The Director must not
recommend a faster workflow if it weakens source provenance, uncertainty
handling, holdout/no-peek boundaries, controls, replay requirements,
result-promotion gates, or overclaim policy.

When the same structural bottleneck appears in two or more campaign tasks,
reviews, validation loops, or handoffs, the Director should route it into a
task proposal or research/source proposal instead of repeating the same status
warning. The proposal should name the problem, repeated evidence, affected
campaigns or workflows, proposed process change, risks, non-goals, and the
maintainer decision needed. This escalation is advisory: the Director still
must not assign canonical task ids, bypass gates, or create busywork when the
right answer is to execute an existing task.

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
- create duplicate digests, dashboards, status pages, or filler task waves when
  existing surfaces can be updated instead;
- recommend a task without naming the scientific output path it advances;
- ignore workflow or architecture bottlenecks when they are why a campaign is
  not producing scientific results;
- optimize workflow by weakening source provenance, uncertainty handling,
  holdout/no-peek boundaries, controls, replay requirements, result-promotion
  gates, or overclaim policy;
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
- use `docs/task-views/*.md`, `apl_mission.py`, snapshots, or CLI/query
  helpers to inspect current work, but do not commit regenerated task views or
  volatile agent-facing query output from the task-admin PR;
- explain why each task belongs in the next campaign cycle.

Required constraints:

- use only maintainer-assigned task numbers or safely select unused task numbers
  from the current local registry;
- keep each task narrow enough for one PR or one clearly bounded agent run;
- include accepted outputs, validation commands, and dependency notes;
- keep claim promotion out of the task unless the maintainer explicitly
  authorizes a separate promotion/review task;
- route final outputs through `docs/result-promotion-protocol.md`;
- state the scientific output path each task advances and reject tasks that only
  duplicate an existing status/digest surface;
- include workflow/architecture changes only when they remove a real bottleneck
  or shorten the path to a reviewable scientific output;
- reject workflow shortcuts that weaken source provenance, uncertainty
  handling, holdout/no-peek boundaries, controls, replay requirements,
  result-promotion gates, or overclaim policy;
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
