# Claude Entry Point

## First Action in Any New Worktree

If `.claude/settings.local.json` does not exist in this directory, pick ONE
of these modes before any other work:

### Safe mode (default — recommended for onboarding)

```bash
./scripts/apl_setup_worktree.sh --mode safe
```

Writes an empty local override. Only the committed baseline in
`.claude/settings.json` is active, so any command outside the baseline still
prompts for approval. Use this when you are exploring the repository, running
unfamiliar workflows, or onboarding a new contributor.

### Autonomous mode (for trusted agent loops)

```bash
./scripts/apl_setup_worktree.sh --mode autonomous
```

Adds `Bash(*)` and broad `/tmp/apl-*` Read/Write/Edit access to the local
allow list. ALL bash commands run without confirmation prompts. Use only when
you trust the agent, the task scope is clear, and there is maintainer
supervision of the loop (for example, executing a maintainer-assigned
`TASK-XXXX` end-to-end without interactive approval).

### Personal allowlist (existing contributors)

```bash
./scripts/apl_setup_worktree.sh
```

Without `--mode`, the script copies your personal `settings.local.json` from
the main repository directory. Preserves any per-contributor allowlist you
have accumulated. If no personal file exists, the script tells you to pick
`--mode safe` or `--mode autonomous` instead.

All three commands are idempotent: they exit without overwriting if
`.claude/settings.local.json` already exists. To switch modes, remove the
file first.

See `.claude/profiles/README.md` for the full profile reference.

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
