# Claude Entry Point

## First Action in Any New Worktree

If `.claude/settings.local.json` does not exist in this directory, run:

```bash
./scripts/apl_setup_worktree.sh
```

This copies the project permission allowlist from the main repository directory
so that subsequent commands run without repeated approval prompts. Safe to
re-run; exits immediately if the file already exists.

## Onboarding

Read these files first:

1. `AGENTS.md`
2. Run `python3 scripts/apl_mission.py --json`
3. `docs/agent-task-protocol.md`
4. `docs/current-missions.md`
5. `tasks/ACTIVE.md`
6. `docs/strategy.md`

Default to the recommended research mission unless the maintainer explicitly
assigns a support, review, closeout, or specific `TASK-XXXX` workflow.
For support work, run `python3 scripts/apl_mission.py --mode support`.
For maintainer review or closeout assistance, run
`python3 scripts/apl_mission.py --mode maintainer`.

Do not invent branch, PR, or commit formats.
Use `docs/agent-task-protocol.md`.
Use branch format `agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug>`.
If the maintainer did not assign a canonical `TASK-XXXX` id, use
`docs/task-proposal-protocol.md` and branch format
`agent/<contributor-id>/<agent-id>/propose-task-<short-slug>` for new task
ideas.
Claude is a tool identifier, not a substitute for the human contributor id.

## CRITICAL: Never push directly to main

**Every change — no exceptions — must follow this flow:**

1. Create or reference a `TASK-XXXX` yaml file in `tasks/`.
2. Work on a branch: `agent/<contributor-id>/<agent-id>/task-<number>-<slug>`.
3. Open a PR. Do not merge it yourself.
4. Wait for maintainer review and merge.

This applies to ALL changes: documentation, scripts, config, fixes, and
features. "Small", "obvious", or "urgent" are not exceptions.
Pushing directly to `main` is a protocol violation.
