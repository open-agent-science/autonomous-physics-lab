# Agent Task Entry Point

This file is kept for Codex and other agent compatibility.

Do not treat it as the single source of truth for active work.

Read these files in order:

1. `AGENTS.md`
2. `docs/agent-task-protocol.md`
3. `docs/status.md`
4. `docs/strategy.md`
5. `tasks/ACTIVE.md`
6. `docs/agent-operating-model.md`

Then:

- pick one atomic `READY` task;
- follow `docs/agent-task-protocol.md` and the task contract;
- run the required validation commands;
- update task state and planning docs if project reality changed.

If no existing task fits, propose a new one from `tasks/TASK-TEMPLATE.yaml`.
Do not invent branch, PR, or commit formats locally.
Use branch format `agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug>`.
Codex is a tool identifier, not the human owner of the PR.
