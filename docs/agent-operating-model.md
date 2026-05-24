# Agent Operating Model

## Read First

Every human or coding agent should read these files in order before starting:

1. [README.md](../README.md)
2. [AGENTS.md](../AGENTS.md)
3. [docs/agent-task-protocol.md](./agent-task-protocol.md)
4. [docs/open-agent-network.md](./open-agent-network.md)
5. [docs/status.md](./status.md)
6. [docs/strategy.md](./strategy.md)
7. [tasks/ACTIVE.md](../tasks/ACTIVE.md)

Then use [docs/architecture-index.md](./architecture-index.md) and
[docs/contributing-workflow.md](./contributing-workflow.md) as needed.
If you need a compact map of active agent roles and maintainer automation
surfaces, also open [docs/agent-catalog.md](./agent-catalog.md).

## Core Idea

Agents do not own domains permanently.

Tasks own the contract:

- scope;
- expected files;
- validation commands;
- accepted outputs;
- scientific constraints.

Any compatible agent may work on a task if it follows the same repository
protocol.

## Local And Parallel Work Mode

The repository supports parallel contributors, but a single local checkout
should stay sequential by default.

That means:

- only one task should usually be marked `IN_PROGRESS` at a time in the local
  repository state;
- a second task may be started out of order only if it does not depend on the
  first task and does not touch the same artifact surface;
- if in doubt, finish the current atomic task first.

For actual multi-agent work, use separate branches or git worktrees:

- one task branch per agent;
- disjoint artifact surfaces whenever possible;
- no shared edits to generated files such as `tasks/ACTIVE.md` and `CONTEXT.md`
  until the PR is ready;
- no guessed canonical task ids during parallel work.

`python3 scripts/apl_mission.py --json` exposes several live task candidates so
maintainers can assign independent work in parallel without treating
`missions/current.yaml` as a hand-maintained live queue.

The same JSON includes a warning-only READY science task pool health summary.
Use [docs/task-queue-health-policy.md](./task-queue-health-policy.md) for the
target pool size, independence rules, and maintainer response when
`task_queue_needed` is true.

## Task Rules

Work on one atomic task at a time.

A task is atomic when it has:

- clear file changes;
- a clear validation protocol;
- a clear commit scope;
- no hidden assumptions that require an additional untracked follow-up.

## Task Input Modes

Tasks may use more than one input shape.

Use science references when the task directly operates on a real benchmark:

- `hypothesis_id`
- `experiment_id`

Use planning metadata instead when the task is setting up future work or
contributor process and is not actually about an existing benchmark:

- `mode: planning_only`
- `related_domain`
- `related_objects`
- `planning_context`

Use workflow metadata when the task coordinates contributor flow, review
discipline, or branch-based execution rather than a specific experiment:

- `mode: workflow`
- `related_objects`
- `planning_context`

Do not attach planning or workflow tasks to unrelated benchmark objects just to
satisfy schema shape.

## Task States

Active task execution should use the canonical states from
[agent-task-protocol.md](./agent-task-protocol.md):

- `READY`
- `IN_PROGRESS`
- `REVIEW_READY`
- `DONE`
- `BLOCKED`
- `REJECTED`

`PROPOSED` may still appear for backlog ideas that are not yet executable.

The live human-readable board is [tasks/ACTIVE.md](../tasks/ACTIVE.md).
It is a generated snapshot backed by canonical task YAML files, not the
primary source of truth for routine task-state transitions.

When using repository-wide snapshots such as `scripts/apl_snapshot.sh`,
treat the generated "Current Authoritative State" layer as the primary source
of truth. That layer is derived from canonical task YAML, experiment YAML, and
committed result artifacts. Large repository tree dumps, task dumps, result
dumps, and knowledge dumps remain useful for deep audit, but they are archive
context and should not override the structured current-state summary.

## Choosing a Task

1. Start with a `READY` task from [tasks/ACTIVE.md](../tasks/ACTIVE.md).
2. Do not pick `BLOCKED` or `REVIEW_READY` tasks unless a human explicitly asks
   for review work.
3. Do not create a new task until you confirm no existing `READY` task already
   covers the same outcome.

## Claiming a Task

Before substantial work:

1. update the corresponding `TASK-*.yaml` status to `IN_PROGRESS`;
2. do not edit `tasks/ACTIVE.md` for ordinary task-state changes;
3. note local handoff details in PR metadata or supporting docs if useful.

After completion:

1. set the task to `REVIEW_READY`;
2. update `docs/status.md` or `docs/next-steps.md` if project reality changed.
3. leave `tasks/ACTIVE.md` to maintainer sync unless the task explicitly
   changes board behavior.
4. wait for maintainer review before the task becomes `DONE`.

## Validation Protocol

Minimum validation before handoff:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli validate-repo .
```

For benchmark or workflow changes, also run:

```bash
python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped
```

If canonical artifacts or repository rules changed, also run:

```bash
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
```

## Commit Discipline

Use the canonical branch, commit, and PR formats from
[agent-task-protocol.md](./agent-task-protocol.md). Do not mix unrelated task
work into one commit.

## New Task Proposal

If no existing task fits, create a proposal under `tasks/proposals/` using
[docs/task-proposal-protocol.md](./task-proposal-protocol.md) and
[tasks/proposals/TASK-PROPOSAL-TEMPLATE.yaml](../tasks/proposals/TASK-PROPOSAL-TEMPLATE.yaml).

Do not guess the next canonical `TASK-XXXX` id during parallel work.

A new task proposal should:

- align with [docs/strategy.md](./strategy.md);
- be atomic;
- include accepted outputs;
- include validation commands;
- avoid hidden benchmark or claim expansion.

Create a canonical `tasks/TASK-XXXX-*.yaml` file only when the maintainer
explicitly assigns or approves the canonical id.

If the maintainer asks you to create one or more canonical tasks for future
work, use a `TASK-QUEUE` branch and PR instead of creating another task whose
only purpose is to create those tasks. The queued tasks should remain `READY`,
`BLOCKED`, or `PROPOSED`; do not mark them `REVIEW_READY` unless the same PR
actually implements their accepted outputs.

## Forbidden Without Human Review

- claim promotion;
- new "discovery" language;
- dashboard or web API work;
- literature ingestion;
- multi-agent runtime infrastructure;
- broad theory-of-everything framing;
- silent regeneration of canonical results without explanation.

## Handoff Rule

Leave the repository in a state where the next agent can continue by reading:

- [docs/status.md](./status.md)
- [docs/agent-task-protocol.md](./agent-task-protocol.md)
- [docs/strategy.md](./strategy.md)
- [tasks/ACTIVE.md](../tasks/ACTIVE.md)

The next contributor should not need to reconstruct intent from git history.
