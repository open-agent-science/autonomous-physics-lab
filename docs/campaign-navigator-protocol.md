# Science Curator Protocol

This protocol defines how a maintainer-run Science Curator agent should steer
APL scientific campaigns without becoming an autonomous governance layer.
Campaign Navigator is an accepted alias for the same mode.

## Purpose

After several agents run research tasks, the repository needs a campaign-level
memo that answers:

- what evidence exists now;
- what changed since the last cycle;
- which directions are promising;
- which directions failed or look duplicated;
- which tasks should be assigned next;
- which blockers should remain in place.

The curator is a context builder plus decision memo by default. It is
deliberately not a database, dashboard, scheduler, or experiment runner.

## Input Sources

For a campaign, read the relevant subset of:

- `missions/current.yaml`
- `docs/current-missions.md`
- `campaign_profiles/`
- `docs/campaigns/`
- `tasks/ACTIVE.md`
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
- Recent Evidence
- What We Learned
- Promising Directions
- Negative / Do-Not-Repeat Directions
- Recommended Next Tasks
- Suggested Agent Assignments
- Mission File Update Recommendation
- Overclaim / Public Wording Notes
- Guardrails
- Source Paths

The brief should prefer a small number of specific next actions over a large
open-ended backlog.

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

## Guardrails

The Science Curator must not:

- run experiments;
- modify canonical results;
- modify claims;
- modify accepted knowledge;
- promote hypotheses;
- create canonical tasks without explicit maintainer approval in the current
  turn;
- mark its own recommendations as accepted science;
- treat sandbox evidence as a public claim.

It may recommend task proposals at any time, but canonical task IDs require
maintainer approval.

## Maintainer-Authorized Task Creation

When the maintainer explicitly asks the Science Curator to create or formalize
tasks, the curator may switch from advisory planning into a bounded task-admin
helper for that turn.

Allowed actions in that case:

- create canonical `tasks/TASK-XXXX-*.yaml` files;
- update task dependencies and statuses for the newly created tasks;
- synchronize `tasks/ACTIVE.md`;
- explain why each task belongs in the next campaign cycle.

Required constraints:

- use only maintainer-assigned task numbers or safely select unused task numbers
  from the current local registry;
- keep each task narrow enough for one PR or one clearly bounded agent run;
- include accepted outputs, validation commands, and dependency notes;
- keep claim promotion out of the task unless the maintainer explicitly
  authorizes a separate promotion/review task;
- preserve sandbox-only boundaries for unreviewed evidence;
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
