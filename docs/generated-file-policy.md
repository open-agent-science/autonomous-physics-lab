# Generated File Policy

This is a **standing architectural policy** for generated and static files in
Autonomous Physics Lab. It is in force by default and applies to all future work
— including sessions that lack any specific context — until a task explicitly
changes it. It is a general principle, not a one-off reaction to a single case.
It is also recorded as a core rule in
[architecture.md](architecture.md#generated-state-and-agent-data-access-standing-policy).

## The principle

**Generated, frequently-changing state must not be committed as an agent-facing
data source. Agents read data through a governed script entry point or from the
canonical source files.**

Why: a **script entry point** (e.g. `apl_mission.py`,
`apl_task_campaign_index.py`) is a single, governable access point — it always
reflects current state, and the rules for what agents see can be updated in one
place. A committed **static file** is a frozen copy that drifts from its source,
becomes a second source of truth, and forces churn to keep fresh. Prefer the
entry point; reserve static files for human browsing.

## The rule

- **Agents** get current state by:
  - running the **generator/script on demand** (e.g.
    `python3 scripts/apl_task_campaign_index.py`,
    `python3 scripts/apl_mission.py`), or
  - reading the **canonical source files** directly
    (`tasks/TASK-*.yaml`, `campaign_profiles/*.yaml`, `missions/current.yaml`,
    `campaigns/catalog.yaml`).
- **Humans** may use committed static files for browsing. Agents may also read
  them, but must treat a script/source query as the source of truth for current
  state — a committed static file can be stale.

## What is allowed

- **Scripts/helpers that print a view on demand.** Preferred for any
  agent-facing view (lane index, capacity, mission). No freshness burden.
- **Committed *human-facing* navigation that is auto-regenerated** by the
  post-merge `Sync Active Board` GitHub Action — currently `docs/task-views/*.md`.
  These stay fresh on `main` automatically; agents must **not** hand-maintain
  them or depend on their freshness inside a feature branch.
- **A generated catalog with a `--check` gate** (e.g. `campaigns/catalog.yaml`
  via `generate_campaign_catalog.py --check`) when it changes only with its
  declared source and is validated in CI — it is portfolio metadata, not a
  per-task board.

## What is forbidden

- **Committing a new generated or cache file as the agent data source**,
  especially one that changes on most task PRs (a "board-like" artifact). This is
  the `tasks/ACTIVE.md` / `campaigns/task-index.yaml` mistake. Expose it through
  an on-demand script instead.
- **Requiring agents to refresh a committed generated file in their task PR** to
  keep it current. If keeping it fresh needs manual effort per PR, it should not
  be committed.
- **Depending on a committed generated file's freshness** for correctness in
  agent logic.

## Quick test before committing a generated file

Ask: *"Does this file change on most task PRs, and is it meant for agents to
read?"*

- **Yes** → do not commit it; expose it through an on-demand script.
- It is human navigation **and** auto-regenerated post-merge → allowed
  (`docs/task-views/*.md`).
- It is source-coupled portfolio metadata with a CI `--check` → allowed
  (`campaigns/catalog.yaml`).

## See also

- [notes/generated-task-navigation-architecture-decision.md](notes/generated-task-navigation-architecture-decision.md) — TASK-0470 (ACTIVE.md retirement)
- [notes/static-task-index-retrospective.md](notes/static-task-index-retrospective.md) — TASK-0510 retrospective
- [agent-task-protocol.md](agent-task-protocol.md) — forbidden actions
- [maintainer-review-agent.md](maintainer-review-agent.md) — required checks
