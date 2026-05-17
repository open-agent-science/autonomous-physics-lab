# Claude Code Permission Profiles

This directory contains committed permission profiles used to populate
`.claude/settings.local.json` (which is gitignored).

The default onboarding path uses the per-contributor `settings.local.json`
copied from the main repo root. An autonomous profile is also committed here
for trusted agent loops that should not be interrupted by per-command
approval prompts.

Apply a profile with `scripts/apl_setup_worktree.sh`:

```bash
# Default behavior: copy personal settings.local.json from the main repo root
# to this worktree. Preserves any per-contributor allowlist accumulated
# outside the committed baseline. This is the safe onboarding path.
./scripts/apl_setup_worktree.sh

# Autonomous mode: allow ALL bash commands without confirmation prompts.
# Use only when you trust the agent and the task scope is clear.
./scripts/apl_setup_worktree.sh --mode autonomous
```

Both commands are idempotent: if `.claude/settings.local.json` already
exists, the script exits without overwriting.

## Profiles

### autonomous.json

Adds `Bash(*)` to the allow list along with broad Read/Write/Edit access for
sandbox paths under `/tmp/apl-*` and `/private/tmp/apl-*`. Combined with the
committed `.claude/settings.json` baseline this means no command
confirmations during a session.

Appropriate for:

- maintainer-supervised autonomous task loops;
- long-running batch work where confirmation prompts would block progress;
- trusted agent runs on a dedicated worktree.

Not appropriate for:

- shared workstations where untrusted code may execute;
- exploration of unfamiliar third-party scripts;
- onboarding sessions where the contributor is still learning the protocol.

## Scope

The profile only configures local Claude Code permissions. It does not:

- bypass the canonical PR workflow defined in `docs/agent-task-protocol.md`;
- allow any agent to push directly to `main`;
- skip maintainer review of scientific or release-relevant changes;
- modify global Claude settings under `~/.claude/`.

The autonomous profile is a friction-reduction tool, not a review-bypass
tool.
