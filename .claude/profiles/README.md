# Claude Code Permission Profiles

This directory contains committed permission profiles used to populate
`.claude/settings.local.json` (which is gitignored).

The profiles let contributors and agents choose explicitly between a safe
mode (manual approval for anything outside the committed baseline) and an
autonomous mode (no command confirmations).

Apply a profile with `scripts/apl_setup_worktree.sh`:

```bash
# Default behavior: copy personal settings.local.json from the main repo root
# to this worktree. Preserves any per-contributor allowlist accumulated outside
# the committed baseline.
./scripts/apl_setup_worktree.sh

# Safe mode: write an empty local override; rely only on the committed
# baseline allowlist in .claude/settings.json. Anything not in the baseline
# will prompt for approval. Recommended for onboarding and unfamiliar work.
./scripts/apl_setup_worktree.sh --mode safe

# Autonomous mode: allow ALL bash commands without confirmation prompts.
# Use only when you trust the agent and the task scope is clear.
./scripts/apl_setup_worktree.sh --mode autonomous
```

All three commands are idempotent: if `.claude/settings.local.json` already
exists, the script exits without overwriting.

## Profiles

### safe.json

Empty allow list. The committed `.claude/settings.json` baseline still
applies. Any command outside the baseline triggers a manual approval prompt.

This is the recommended default for:

- new contributors during onboarding;
- agents running unfamiliar workflows;
- review or audit work where command intent matters more than speed.

### autonomous.json

Adds `Bash(*)` to the allow list along with broad Read/Write/Edit access for
sandbox paths under `/tmp/apl-*` and `/private/tmp/apl-*`. Combined with the
committed baseline this means no command confirmations during a session.

This is appropriate for:

- maintainer-supervised autonomous task loops;
- long-running batch work where confirmation prompts would block progress;
- trusted agent runs on a dedicated worktree.

This mode is not appropriate for:

- shared workstations where untrusted code may execute;
- exploration of unfamiliar third-party scripts;
- onboarding sessions where the contributor is still learning the protocol.

## Scope

These profiles only configure local Claude Code permissions. They do not:

- bypass the canonical PR workflow defined in `docs/agent-task-protocol.md`;
- allow any agent to push directly to `main`;
- skip maintainer review of scientific or release-relevant changes;
- modify global Claude settings under `~/.claude/`.

Permission profiles are a friction-reduction tool, not a review-bypass tool.
