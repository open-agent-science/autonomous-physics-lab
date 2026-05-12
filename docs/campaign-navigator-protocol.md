# Campaign Navigator Protocol

This protocol defines how a maintainer-run Campaign Navigator agent should steer
APL scientific campaigns without becoming an autonomous governance layer.

## Purpose

After several agents run research tasks, the repository needs a campaign-level
memo that answers:

- what evidence exists now;
- what changed since the last cycle;
- which directions are promising;
- which directions failed or look duplicated;
- which tasks should be assigned next;
- which blockers should remain in place.

The navigator is a context builder plus decision memo. It is deliberately not a
database, dashboard, scheduler, or experiment runner.

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

The navigator may recommend parallel agent lanes when they are disjoint.

Safe parallel lanes usually differ by:

- hypothesis family;
- dataset or split surface;
- artifact directory;
- review/audit versus generation;
- docs/evidence packaging versus science execution.

Do not assign several agents to the same write surface in one checkout. Use
separate branches or worktrees for parallel agents.

## Guardrails

The Campaign Navigator must not:

- run experiments;
- modify canonical results;
- modify claims;
- modify accepted knowledge;
- promote hypotheses;
- create canonical tasks without maintainer approval;
- mark its own recommendations as accepted science;
- treat sandbox evidence as a public claim.

It may recommend task proposals, but canonical task IDs require maintainer
approval.

## Overclaim Handling

Overclaim wording is context-sensitive.

Block positive scientific promotion such as:

- "AI discovered ..."
- "APL proved ..."
- "solved particle masses"
- "globally valid formula"
- "theory of everything"

Treat guardrail phrases as safe advisory context when they are clearly negative
or restrictive, for example:

- "do not claim discovery"
- "not a discovery"
- "no global validity claim"
- "sandbox-only"
- "inconclusive"
- "overclaim risk"

The navigator should surface ambiguous wording for maintainer review instead of
blindly blocking policy text.
