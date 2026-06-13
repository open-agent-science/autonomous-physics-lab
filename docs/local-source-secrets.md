# Local Source Secrets

This document defines the cross-campaign pattern for maintainer-held API keys,
tokens, cookies, or other local credentials used only for source acquisition.

APL should prefer public, key-free, redistributable sources. When a useful
source is key-gated, the correct response is not an immediate scientific
blocker. The agent should first surface the exact local secret requirement to
the maintainer, provide a safe setup command, and continue only after the
maintainer confirms the key is available or unavailable.

## Local File Pattern

Use a local env file in the repository checkout:

```bash
cp .apl-local-secrets.env.example .apl-local-secrets.env
chmod 600 .apl-local-secrets.env
```

Fill only the variables needed for maintainer-run acquisition tasks. The filled
`.apl-local-secrets.env` file is ignored by git and must never be committed,
pasted into PRs, or printed in logs.

To activate it for one shell session:

```bash
set -a; . ./.apl-local-secrets.env; set +a
```

That activation syntax is POSIX-shell specific. Agents should prefer the
repository helper below because it works across macOS, Linux, Windows,
PowerShell, Codex, Claude Code, and other agent shells.

To check whether a key exists without printing it:

```bash
python3 scripts/apl_local_secrets.py status --require MP_API_KEY
```

To run a key-gated acquisition command with local secrets loaded into the child
process:

```bash
python3 scripts/apl_local_secrets.py run -- python3 <acquisition-script>.py
```

The helper does not export variables to the parent shell and does not print
secret values. The child command must still avoid logging environment contents.

For dedicated agent worktrees, the helper checks `APL_LOCAL_SECRETS_FILE` first,
then the current checkout, then parent directories. That lets a maintainer keep
one local `.apl-local-secrets.env` in the main checkout while task
worktrees under `.worktrees/` reuse it without copying secrets. If an agent is
running in a separate clone, set `APL_LOCAL_SECRETS_FILE` to the local file path
or create that clone's own ignored `.apl-local-secrets.env`.

## Agent Handshake

When a task needs a local key or other maintainer-held credential, the agent
must follow this order:

1. Name the exact environment variable required by the runbook or source
   contract, for example `MP_API_KEY`.
2. Tell the maintainer why it is needed and which acquisition task/runbook will
   use it.
3. Provide the local setup pattern using `.apl-local-secrets.env`; do not ask
   for the key to be pasted into a PR, task YAML, GitHub issue, or committed
   file.
4. Verify only presence (`SET` / `not set`) and never print the value.
5. Use `scripts/apl_local_secrets.py` for cross-platform presence checks and
   child-process runs unless a maintainer explicitly chooses another local
   secret store.
6. Run the key-gated acquisition only in an explicitly approved maintainer-run
   acquisition task.
7. Record a blocker only after the maintainer says the key, access, or
   permission is unavailable, or after the safe setup path fails.

## Campaign Requirements Block

Runbooks and source-acquisition task files may declare local requirements using
this shape:

```yaml
local_secret_requirements:
  - env_var: MP_API_KEY
    provider: Materials Project
    used_for: "maintainer-run snapshot acquisition"
    required_by:
      - "docs/runbooks/materials-snapshot-acquisition-runbook.md"
    storage: ".apl-local-secrets.env or shell environment"
    agent_visibility: "presence-only; never print or commit the value"
```

Use one entry per provider. Do not store secret values, partial secret values,
or screenshots of dashboards in the repository.

## Current Known Secret Variables

| Environment variable | Provider | Campaign / use | Notes |
| --- | --- | --- | --- |
| `MP_API_KEY` | Materials Project | Materials Property Residuals source snapshots (`MD-0001`, `MD-0002`) | Personal API key. Keep local; never commit. |

Add new rows only when a reviewed source-acquisition runbook introduces a new
key-gated source.

## Non-Goals

- Do not move local research keys into GitHub Actions secrets unless a separate
  maintainer-approved CI/self-hosted-runner task explicitly requires it.
- Do not run live key-gated fetches inside benchmark runners or ordinary
  research tasks.
- Do not treat a missing local key as a scientific negative result.
