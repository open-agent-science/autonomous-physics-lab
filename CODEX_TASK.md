# Agent Task Entry Point

This file is kept for Codex and other agent compatibility.

Do not treat it as the single source of truth for active work.

Read these files in order:

1. `AGENTS.md`
2. Run `python3 scripts/apl_mission.py --json`
3. `docs/agent-task-protocol.md`
4. `docs/current-missions.md`
5. `docs/status.md`
6. `docs/strategy.md`
7. `tasks/ACTIVE.md`
8. `docs/agent-operating-model.md`

Then:

- start from the recommended research mission unless the maintainer assigned a
  stricter task or support/review mode;
- follow `docs/agent-task-protocol.md` and the task contract;
- run the required validation commands;
- update task state and planning docs if project reality changed.

For support work, run `python3 scripts/apl_mission.py --mode support`.
For maintainer review or closeout assistance, run
`python3 scripts/apl_mission.py --mode maintainer`.

If no existing task fits and the maintainer did not assign a canonical
`TASK-XXXX` id, create a proposal
using `docs/task-proposal-protocol.md` and
`tasks/proposals/TASK-PROPOSAL-TEMPLATE.yaml` instead of guessing the next task
number.
Do not invent branch, PR, or commit formats locally.
Use canonical task branch format
`agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug>`.
Use task-proposal branch format
`agent/<contributor-id>/<agent-id>/propose-task-<short-slug>`.
Codex is a tool identifier, not the human owner of the PR.
