# First Contributor Runbook

This runbook is for invited contributors working in `v0.1-private-alpha`.
It covers the shortest safe path from clone to pull request.

## 1) Clone the repository

Use HTTPS:

```bash
git clone https://github.com/open-agent-science/autonomous-physics-lab.git
cd autonomous-physics-lab
```

## 2) Create and activate a local environment

On Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3) Install dependencies

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## 4) Read project rules before starting

Read these files in order:

1. `AGENTS.md`
2. `docs/agent-task-protocol.md`
3. `docs/status.md`
4. `docs/strategy.md`
5. `docs/task-views/research.md`

## 5) Pick one READY task

Choose one atomic task from the `READY` section in `docs/task-views/research.md`.
Do not start multiple tasks in one branch.

## 6) Create a task branch

Required branch format:

`agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug>`

Example:

```bash
git checkout -b agent/gladunrv/codex/task-0023-first-contributor-runbook
```

Use your lowercased GitHub username first when available, then the execution
tool id. If no GitHub username is available, use a stable maintainer-approved
short id.

Do this before editing repository files. Do not work on `main`.

## 7) Run validation before handoff

Use the quick local script first:

```bash
./scripts/validate_quick.sh
```

Then run the full required validation set:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
git diff --exit-code
```

## 8) Generate a review bundle

Before opening PR, generate the maintainer review snapshot:

```bash
python3 scripts/apl_review_bundle.py
```

This creates:

`_snapshots/review_<branch>_<timestamp>.md`

## 9) Open a pull request

Use one PR for one task branch and keep scope atomic.
Fill in the Agent / Contributor Metadata block in the PR template so both the
human owner and the execution tool are recorded.

PR title format:

`TASK-0023: Create first contributor runbook`

Commit message format:

`<type>(task-<task-number>): <short summary>`

Example:

`docs(task-0023): add first contributor runbook`


## Onboarding Checklist

- Clone repository and enter project directory.
- Create and activate `.venv`.
- Install `.[dev]` dependencies.
- Read `AGENTS.md` and `docs/agent-task-protocol.md`.
- Pick one `READY` task from `docs/task-views/research.md`.
- Create branch with the required naming pattern.
- Run quick validation.
- Run full required validation before PR handoff.
- Generate review bundle.
- Open one PR tied to one task.

## First-Contributor Workflow Note

Keep the first contribution small, explicit, and review-friendly.
Prefer documentation or narrow workflow tasks first, then move to broader tasks
after one successful PR cycle.
