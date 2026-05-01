# Agent Operating Model

## Read First

Every human or coding agent should read these files in order before starting:

1. [README.md](../README.md)
2. [AGENTS.md](../AGENTS.md)
3. [docs/status.md](./status.md)
4. [docs/strategy.md](./strategy.md)
5. [tasks/ACTIVE.md](../tasks/ACTIVE.md)

Then use [docs/architecture-index.md](./architecture-index.md) and
[docs/contributing-workflow.md](./contributing-workflow.md) as needed.

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

## Sequential-First Mode

The repository currently prefers sequential local work.

That means:

- only one task should usually be marked `CLAIMED` or `IN_PROGRESS` at a time
  in the local repository state;
- a second task may be started out of order only if it does not depend on the
  first task and does not touch the same artifact surface;
- if in doubt, finish the current atomic task first.

## Task Rules

Work on one atomic task at a time.

A task is atomic when it has:

- clear file changes;
- a clear validation protocol;
- a clear commit scope;
- no hidden assumptions that require an additional untracked follow-up.

## Task States

`TASK-*.yaml` may use:

- `PROPOSED`
- `READY`
- `CLAIMED`
- `IN_PROGRESS`
- `REVIEW_READY`
- `BLOCKED`
- `DONE`
- `REJECTED`

The live human-readable board is [tasks/ACTIVE.md](../tasks/ACTIVE.md).

## Choosing a Task

1. Start with a `READY` task from [tasks/ACTIVE.md](../tasks/ACTIVE.md).
2. Do not pick `BLOCKED` or `REVIEW_READY` tasks unless a human explicitly asks
   for review work.
3. Do not create a new task until you confirm no existing `READY` task already
   covers the same outcome.

## Claiming a Task

Before substantial work:

1. update `tasks/ACTIVE.md`;
2. update the corresponding `TASK-*.yaml` status to `CLAIMED` or
   `IN_PROGRESS` when appropriate;
3. note the active agent and date in the board if useful.

After completion:

1. set the task to `DONE` or `REVIEW_READY`;
2. update `tasks/ACTIVE.md`;
3. update `docs/status.md` or `docs/next-steps.md` if project reality changed.

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
python3 -m physics_lab.cli validate-repo . --strict
```

## Commit Discipline

Use small commits with clear scope:

- `feat`
- `fix`
- `refactor`
- `docs`
- `test`
- `chore`

Do not mix unrelated task work into one commit.

## New Task Proposal

If no existing task fits, create a new task from
[tasks/TASK-TEMPLATE.yaml](../tasks/TASK-TEMPLATE.yaml) and mark it
`PROPOSED`.

A new task should:

- align with [docs/strategy.md](./strategy.md);
- be atomic;
- include accepted outputs;
- include validation commands;
- avoid hidden benchmark or claim expansion.

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
- [docs/strategy.md](./strategy.md)
- [tasks/ACTIVE.md](../tasks/ACTIVE.md)

The next contributor should not need to reconstruct intent from git history.
