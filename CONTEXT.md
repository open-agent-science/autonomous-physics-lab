# Autonomous Physics Lab — Context Bundle

Generated: 2026-06-11 08:23 UTC
Mode: core
Repo: open-agent-science/autonomous-physics-lab

This file bundles the core project instructions, strategy, and current
task board into one document for use with chat-based LLMs or as a
quick agent orientation file.

For the live repository see: https://github.com/open-agent-science/autonomous-physics-lab


────────────────────────────────────────────────────────────────────────

# Agent & Contributor Rules
<!-- source: AGENTS.md -->

# AGENTS.md

## Project

This repository is `autonomous-physics-lab`.

Autonomous Physics Lab is an open-source scientific engine for generating,
testing, simulating, falsifying, scoring, and reusing physics hypotheses.

It is not a chatbot. It is a hypothesis-testing machine.

## Quick Orientation (single file)

If you prefer to read the full project context in one place, run:

```bash
python3 scripts/generate_context_bundle.py
```

This writes `CONTEXT.md` — a bundle of the core instructions, strategy, and
active task board. The file is also committed to the repo root for download.

For a repository snapshot intended for the maintainer, strategy agents, or
handoff context, run the snapshot script without overriding its output
directory:

```bash
./scripts/apl_snapshot.sh
```

This writes to the canonical project-local `_snapshots/` directory. Use
`APL_SNAPSHOT_DIR=/tmp/...` only for disposable test runs, never for the final
snapshot you want the maintainer or another agent to consume.

If the repository root feels busy, use `docs/repository-map.md` to distinguish
core runtime, current-work coordination, scientific memory, legacy archives,
and local/generated checkout artifacts.

## Agent First Default

New contributors and coding agents should start with the mission entrypoint:

```bash
python3 scripts/apl_mission.py
```

Default mode is `research`. The script recommends the highest-value current
scientific mission and provides guardrails for bounded, reviewable work with
gated evidence publication when the selected task explicitly allows it.
For machine-readable context or a copy-paste agent prompt, run:

```bash
python3 scripts/apl_mission.py --output json
python3 scripts/apl_mission.py --output agent
```

Use explicit modes when the maintainer asks for non-research work:

```bash
python3 scripts/apl_mission.py --mode support
python3 scripts/apl_mission.py --mode maintainer
```

Agent First does not replace the task protocol, maintainer review agent, or
closeout flow. It only changes the default onboarding posture: research,
replay, audit, hypothesis testing, source readiness, and gated evidence
publication come before microtasks or docs-only support unless the maintainer
says otherwise.

Executor agents should treat only `READY` tasks as available work. Do not offer
`REVIEW_READY` tasks as task choices unless the maintainer explicitly asks for
review, closeout, or queue triage.

## Agent Work Paths

Choose your path based on mission mode and available token or time budget:

```mermaid
flowchart LR
    classDef quick  fill:#dbeafe,stroke:#3b82f6,color:#1e3a8a,font-weight:bold
    classDef task   fill:#dcfce7,stroke:#16a34a,color:#14532d,font-weight:bold
    classDef sci    fill:#f3e8ff,stroke:#a855f7,color:#581c87,font-weight:bold
    classDef prop   fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef finish fill:#f1f5f9,stroke:#64748b,color:#1e293b,font-weight:bold

    Start(["▶ Enter repo"]) --> Mission["🚀 apl_mission.py\nResearch Mode"]
    Mission --> Read["📋 AGENTS.md\n+ mission context"]

    Read -->|"default"| Sci["🔬 Research mission\nhypothesis · replay · audit"]:::sci
    Read -->|"support mode"| MT["⚡ Microtask"]:::quick
    Read -->|"task mode"| RT["🎯 READY task"]:::task
    Read -->|"new idea"| Prop["💡 Task proposal\ntasks/proposals/"]:::prop

    MT  --> PR["📬 branch → PR\n→ maintainer review"]:::finish
    RT  --> PR
    Sci --> PR
    Prop --> PropPR["📋 TASK-PROPOSAL PR\nwait for TASK-XXXX"]:::prop
```

All paths follow `docs/agent-task-protocol.md`. Never push directly to `main`.

## CRITICAL: Never push directly to main

Every change must go through the full task lifecycle:

1. `tasks/TASK-XXXX-*.yaml` — create or reference a task file
2. branch: `agent/<contributor-id>/<agent-id>/task-<number>-<slug>`
3. PR — open it, do not merge it yourself
4. maintainer review → merge

No exceptions for "small", "obvious", or "urgent" changes.
Documentation, scripts, config, and fixes all follow the same flow.
Pushing directly to `main` violates the repository protocol.

The only operations allowed directly on `main` are:
- post-merge task closeout (`status: DONE`)
- `CONTEXT.md` regeneration after a batch merge
- regeneration of `docs/task-views/*.md` by the
  `Sync Active Board` post-merge GitHub Action (the action commits with a
  `[skip-board-sync]` marker and never edits canonical task YAML)

## Core Principle

LLMs may propose, explain, and organize hypotheses, but numerical and symbolic
claims must be verified by deterministic code.

Never trust an LLM-generated formula without validation.

## Python Runtime

APL requires Python 3.11+ (`requires-python = ">=3.11"` in `pyproject.toml`) and
uses 3.10+ runtime features. If your system Python is older or lacks the project
dependencies, create a 3.11+ virtual environment and install the project:

```bash
python3.11 -m venv .venv
# activate: `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows)
pip install -e ".[dev]"
```

Run `ruff`, `pytest`, and `python -m physics_lab.cli ...` with that interpreter.
The minimum version lives in one place (`physics_lab/_runtime.py`); helper paths
that use 3.10+ features fail fast with an actionable message, and
`python3 scripts/apl_agent_doctor.py` reports whether the active interpreter meets
the requirement. APL is intentionally single-runtime; do not add Python <3.11
compatibility shims.

## Cross-Platform Compatibility

APL must run on Linux, macOS, and Windows so third-party agents can contribute.
CI runs on Linux only, so agents are responsible for writing portable code:
use `pathlib.Path` (never hardcoded `/`), `tempfile` (never `/tmp`),
`Path.home()` (never `HOME`), `sys.executable` (never hardcoded `python3`),
argument-list subprocesses with `shell=False`, and `encoding="utf-8"`. Do not
add `.sh` scripts on the task-execution or review critical path without a
cross-platform (Python) equivalent. See
[docs/cross-platform-compatibility.md](docs/cross-platform-compatibility.md).

## Public Scientific Memory

The project must maintain a public scientific memory.

New hypotheses, claims, experiments, results, tasks, and reusable knowledge
should be stored in version-controlled files.

The system must distinguish between:

- hypothesis: an unverified proposal;
- claim: a statement supported by evidence;
- result: output of a reproducible experiment;
- knowledge: reusable, reviewed information;
- theory: a structured collection of connected claims and hypotheses.

Do not promote a hypothesis to knowledge without validation.

## Open Agent Network

The project should support external agents and humans contributing work.

Tasks should be represented as structured YAML files and, later, GitHub issues
or API jobs.

Agents may propose hypotheses, run simulations, falsify models, improve
formulas, or review results.

Maintainer-run review agents may also review pull requests and perform task
closeout after merge, but they do not make final scientific or merge
decisions automatically.

Every agent output must include:

- task id;
- input references;
- method;
- code reference;
- metrics;
- limitations;
- verdict.

For research, validation, benchmark, source-curation, prediction, result,
claim, or knowledge-facing tasks, the final output must also include an
output-routing summary following `docs/result-promotion-protocol.md`: canonical
destination, review tier when applicable, Gate A/Gate B status when applicable,
claim impact, knowledge impact, and any publication blocker. Missing tooling or
source provenance blocks publication; it does not authorize unsupported prose
claims.

No anonymous unverifiable scientific claim should be accepted as a result.

## Shared Task Pool

Agents do not own permanent roles in this repository.

Instead:

- the task defines the contract;
- any compatible agent may pick a `READY` task;
- agents should prefer one atomic task at a time;
- tasks may be taken out of order only when they do not depend on each other or
  create artifact conflicts.

Use these files as the shared coordination layer:

- `docs/strategy.md`
- `docs/agent-task-protocol.md`
- `docs/agent-task-claiming.md` — lightweight GitHub-native task-claiming ledger; declare a claim before substantial work so parallel agents do not collide on the same task or write surface.
- `docs/task-proposal-protocol.md`
- `docs/agent-operating-model.md`
- `docs/result-promotion-protocol.md` — master mapping rule from task verdict to canonical output class; required reading before writing any final task output (replaces the default "write only an `AGENT-RUN-*`" pattern).
- `docs/repository-map.md` — human-facing map of root paths, scientific memory, legacy archives, and local/generated artifacts.
- `agents/README.md` — index of agent role profiles (`agents/<role-id>.yaml`). When the maintainer asks the agent to act in a role (in any language), the agent matches the request against each role file's `activation.intent`, loads the matching profile as its first action, and applies that role for the session.
- `docs/task-views/research.md`
- `docs/task-views/support.md`
- `docs/task-views/release.md`
- `docs/task-views/watchlist.md`
- `docs/task-views/blocked.md`
- `tasks/TASK-TEMPLATE.yaml`
- `tasks/proposals/TASK-PROPOSAL-TEMPLATE.yaml`

The generated files under `docs/task-views/` are the human navigation surface
for current work (the legacy `tasks/ACTIVE.md` full board was retired — see
TASK-0470/TASK-0473; use `git log` for history and `apl_mission.py` for the
agent entry point). They are derived from canonical
`tasks/TASK-*.yaml` files and regenerated automatically on `main` by the
`Sync Active Board` GitHub Action after any push that touches `tasks/**` or
`missions/current.yaml`. Agents do not commit regenerated versions of these
files from a task PR; the action handles that on `main`. Maintainers may
still run `python3 -m physics_lab.cli sync-active-board .` by hand in a
dedicated board-sync PR when the action is disabled or for explicit audits.

Do not add committed static files primarily for agent routing when the content
changes frequently. Agents may use committed human-facing navigation and may
call scripts, CLI filters, or snapshot generation to get current state, but
volatile agent-facing query output should remain dynamic rather than becoming a
second generated board in the committed tree. See
`docs/reviews/static-agent-facing-generated-index-postmortem.md`.

Do not treat `CODEX_TASK.md` as the single source of truth for active work.
Do not invent task branch, commit, PR, or task-state formats locally.
Use `docs/agent-task-protocol.md`.
Use `docs/task-proposal-protocol.md` when suggesting new task ideas that do
not yet have a maintainer-assigned canonical `TASK-XXXX` id.
Use `docs/maintainer-review-agent.md` when the maintainer wants structured PR
review or task closeout help.
Use `docs/agent-catalog.md` when you need the shortest map of which agent
paths, maintainer automation roles, and entrypoints already exist.

Before starting implementation, agents must create a working task branch using
the canonical branch format. Agents must not begin editing repository files,
staging changes, or otherwise performing task work on `main`.

When two or more agent sessions are (or might soon be) active in the same
repository checkout, prefer a dedicated `git worktree` per task so that
`HEAD` and untracked files do not leak between sessions. Use
[`docs/notes/agent-worktree-discipline.md`](docs/notes/agent-worktree-discipline.md)
for the helpers (`scripts/apl_new_worktree.sh`) and the optional
[`scripts/apl_branch_precondition.py`](scripts/apl_branch_precondition.py)
check that catches "wrong branch / surprise files" before any commit.

See [`docs/notes/agent-discipline-collected.md`](docs/notes/agent-discipline-collected.md)
for the collected agent-discipline learnings index (worktree usage,
mock-first testing, dependent-PR serialisation, harness-artifact handling).

## Task Proposal Rule

If no existing `READY` task fits and the maintainer did not explicitly assign a
canonical `TASK-XXXX` id, agents should create a proposal under
`tasks/proposals/` instead of guessing the next task number.

Normal agents should not assign canonical task ids during parallel work.

External agents should also preserve actionable signals they discover while
working. Bugs, validation bottlenecks, cross-platform failures, protocol gaps,
optimization opportunities, source leads, blockers, and scientific ideas should
be routed to a durable artifact before handoff: a task proposal, a
domain-specific research proposal, or a lightweight GitHub issue when the agent
cannot safely edit the repository. Do not formalize every passing thought, but
do not leave useful follow-up work only in chat or PR prose.

Maintainers may create canonical ids directly. Maintainer-directed review or
task-admin agents may do so only on explicit maintainer instruction.

When the maintainer explicitly asks an agent to create canonical tasks for
future work, use the `TASK-QUEUE` flow instead of creating an extra task whose
only purpose is to create those tasks. `TASK-QUEUE` PRs may add or update
canonical task files that remain `READY`, `BLOCKED`, or `PROPOSED`; they must
not mark those future tasks as completed or implement their accepted outputs in
the same PR.

## Original MVP

The first MVP was `Pendulum Formula Discovery`.

Goal:

1. Generate exact pendulum period data.
2. Fit correction formulas.
3. Compare models.
4. Score accuracy and complexity.
5. Produce a reproducible report.

## Current Benchmark Scope

The repository currently has eleven canonical experiment files:

- `EXP-0001` — `Pendulum Formula Discovery`
- `EXP-0002` — `Damped Oscillator Regime Verification`
- `EXP-0004` — `Charged-Lepton Koide Reproduction`
- `EXP-0005` — `Historical Tau Holdout Prediction`
- `EXP-0006` — `Dimensional Analysis Validator MVP`
- `EXP-0007` — `Neutrino Koide Consistency Test`
- `EXP-0008` — `Quark Koide Cascade — Brannen Phase Extension Test`
- `EXP-0009` — `Particle-Mass Relation Falsifier MVP`
- `EXP-0010` — `Muon g-2 Formula-Search Stress Test`
- `EXP-0011` — `Anharmonic Oscillator Period Benchmark`
- `EXP-0012` — `Nuclear Mass Baseline Residual Benchmark`

For public-facing summaries, keep the benchmark surface conservative:
completed benchmarks, falsifications, and sandbox pilots are reviewable
evidence, not automatic discovery claims. `EXP-0010` should be described only
as a guarded empirical formula-search stress test with explicit
multiple-testing and numerology limitations. `EXP-0012` is the current
research-first validation surface, but nuclear residual candidates remain
sandbox-only unless reviewed and promoted by a maintainer.

Use that broader benchmark scope when updating docs, status snapshots, and
contributor guidance during pre-public validation.

## Planning Files

To continue work consistently, use these project documents:

- `docs/strategy.md` for the strategic compass;
- `docs/agent-task-protocol.md` for the canonical execution protocol;
- `docs/agent-operating-model.md` for the shared agent workflow;
- `docs/task-views/research.md`, `docs/task-views/support.md`, and
  `docs/task-views/release.md` for lane-specific current work;
- `docs/implementation-plan.md` for the broader phased strategy;
- `docs/next-steps.md` for the current short-term execution queue;
- `docs/backlog.md` for deferred or medium-term work.

If you complete a meaningful block of work or if priorities change, update the
planning files so the next contributor can continue without reconstructing
project state from commits alone.

## Architecture

Use this package structure:

```text
physics_lab/
  cli.py
  engines/
    symbolic.py
    simulation.py
    formula_discovery.py
    scoring.py
    critic.py
  registry/
    hypotheses.py
    claims.py
    experiments.py
    tasks.py
  workflows/
    runner.py
```

## Scientific Rules

Every hypothesis test should try to produce:

- input hypothesis;
- assumptions;
- equations;
- generated or loaded data;
- fitted model;
- validation range;
- error metrics;
- failure cases;
- verdict.

Prefer this verdict vocabulary:

- VALID
- PARTIALLY_VALID
- INVALID
- OVERFITTED
- INCONCLUSIVE

For hypothesis lifecycle states, prefer:

- PROPOSED
- FORMALIZED
- TESTING
- VALID_IN_RANGE
- PARTIALLY_VALID
- FALSIFIED
- OVERFITTED
- INCONCLUSIVE
- INTEGRATED

## Pendulum MVP Requirements

Implement the first workflow for pendulum period approximation.

The exact pendulum period ratio is:

`T / T0 = (2 / pi) * K(k^2)`

`k = sin(theta / 2)`

where:

- `theta` is amplitude in radians;
- `K` is the complete elliptic integral of the first kind;
- `T0 = 2*pi*sqrt(L/g)`.

Compare at least these model families:

1. `1 + a*theta^2`
2. `1 + a*theta^2 + b*theta^4`
3. `1 + a*sin(theta/2)^2`
4. `1 + a*x + b*x^2` where `x = sin(theta/2)^2`

For each model, report:

- fitted coefficients;
- mean relative error;
- max relative error;
- train range;
- test range;
- complexity score;
- final verdict.

## Coding Rules

- Use Python 3.11+.
- Prefer small, pure functions.
- Keep scientific calculations in Python, not in LLM text.
- Use NumPy, SciPy, and SymPy for math.
- Avoid hidden global state.
- Avoid unnecessary abstractions in v0.1.
- Do not add web frameworks yet.
- Do not add dashboard yet.
- Do not integrate ScienceClaw, OpenClaw, or LabClaw yet.
- Prepare adapters later, but keep v0.1 standalone.

## Git Commit Rules for Agents

Agents may create git commits only when the maintainer explicitly asks for it.

Agents must create and switch to a task branch before doing any repository
work for a task.

Agents must not work on `main`.

Agents must commit only on a task branch, never directly on `main`.

Before committing, agents must run:

```bash
git status --short
git diff
```

Agents should stage only files relevant to the current task. Prefer explicit
file paths over broad staging.

Use commit messages in this format:

`<type>(task-XXXX): <short meaningful summary>`

Examples:

- `docs(task-0033): standardize contributor-agent identity format`
- `feat(task-0011): add numerical precision audit`
- `test(task-0017): add dimensional challenge validation`
- `fix(task-0018): support planning-only task inputs`

Allowed commit types:

- `docs`
- `feat`
- `fix`
- `test`
- `refactor`
- `chore`

Agents must not:

- commit directly to `main`
- merge branches
- rebase shared branches
- force-push
- create tags
- mark their own task as `DONE`
- use `Co-Authored-By` for AI agents

`git push` requires explicit maintainer approval.

When the maintainer asks an agent to "prepare a PR", "run the task through
PR", "execute the selected task autonomously", or otherwise requests the full
task lifecycle in the current turn, that request is explicit approval to commit
on the current task branch, push that task branch, and open a draft pull
request for that task. This approval applies only to the selected task branch.
It does not allow pushing `main`, force-pushing, merging, tagging, or pushing
unrelated branches.

For canonical task execution (`TASK-XXXX`), "do/take/run this task" means the
full task lifecycle by default: implement the task, validate it, commit it,
push the task branch, and publish a draft PR. Completed task work must not be
left only in a local worktree unless the maintainer explicitly asks for
local-only, no-PR, or planning-only work. Non-task requests keep the normal
explicit commit/push/PR rules.

Before starting implementation for a full PR lifecycle request, agents may run:

```bash
python3 scripts/apl_pr_capability_check.py
```

This check is advisory, not a pre-work gate or task blocker. Missing `gh`,
missing GitHub auth, or restricted agent network access must not stop the
agent before implementation. Do not pause before editing files just because
the agent cannot publish a PR itself. Instead, create the task branch first,
complete the local task work, run validation, and commit only after the files
are ready for maintainer review. At the end, the agent should choose the best
available publication path: repository PR helpers, an available GitHub/MCP
tool, or GitHub CLI. If a needed `git`/`gh`/review command is blocked by the
sandbox or missing approval, the agent should request the required permission
or escalation for that specific command instead of silently falling back. Only
if the agent still cannot publish after trying the available tool path or
permission request should it provide exact maintainer-run commands for
`git push`, `gh pr create`, review-agent execution after a PR number exists,
and `gh pr ready` when CI and review pass. Do not treat a pushed branch, local
commit, staged diff, title, or PR body as a completed pull request lifecycle;
if the agent cannot create the PR directly, the final response must say what
was attempted and include the manual publication commands.

When Python, Git, GitHub CLI, proxy, or Windows shell setup looks inconsistent,
run the read-only doctor before inventing local fixes:

```bash
python3 scripts/apl_agent_doctor.py
```

The doctor is diagnostic only. It does not install packages, mutate global
`PATH`, store credentials, relax validation, or replace the PR helpers and task
protocol. Use its output to choose the next safe troubleshooting step.

Codex sessions may omit Homebrew paths from `PATH`. Use repository helpers such
as `scripts/apl_pr_capability_check.py` and `scripts/apl_task_pr_helper.py`
instead of calling bare `gh`; they check common GitHub CLI locations such as
`/opt/homebrew/bin/gh` and `/usr/local/bin/gh`.

Agents should open task PRs as drafts while validation and review are still in
progress. After GitHub CI is green and the PR-number review agent returns
`MERGE_OK`, agents should mark the PR ready for review with
`gh pr ready <number>` or give the maintainer that exact command if the agent
lacks GitHub access. If CI fails, the review agent blocks, or the agent is
still applying fixes, keep the PR in draft and report the next command or
blocker.

Before opening a PR, choose the helper that matches the PR kind:

- canonical `TASK-XXXX`: `python3 scripts/apl_task_pr_helper.py`
- task proposal: `python3 scripts/apl_proposal_pr_helper.py`
- microtask: `python3 scripts/apl_microtask_pr_helper.py`
- task closeout: `python3 scripts/apl_closeout_pr_helper.py`
- task queue: use the repository PR template and `TASK-QUEUE` branch/title
  rules; do not mark newly queued tasks `REVIEW_READY` or implement them in the
  same PR.

Before opening a canonical task PR, agents should prefer the repository-native
Python helper instead of hand-writing branch/title/body metadata:

```bash
python3 scripts/apl_task_pr_helper.py prepare-current \
  --task-id TASK-XXXX \
  --contributor-id <contributor-id> \
  --github-username <github-username> \
  --agent-id <agent-id> \
  --human-reviewer <maintainer-github-username> \
  --summary "What changed, in narrow verification-first terms." \
  --body-file .apl-pr-body.md
```

`prepare-current` uses the actual current branch and diff, so it catches
non-canonical branch names and incomplete PR bodies before a bad draft PR is
opened. It works through Python on Windows, macOS, and Linux and does not add a
shell-script critical path.

If `git add` or `git commit` fails inside Codex with
`.git/index.lock: Operation not permitted`, treat it as a sandbox permission
issue and retry the same git command with escalation. Do not tell the
maintainer to edit or delete `.git/index.lock` unless a separate check confirms
that a stale lock file exists and no git process is running.

AI assistance should be recorded in PR metadata, not in git co-author trailers.

Maintainer review and task closeout may be assisted by a maintainer-run review
agent, but that agent must not auto-merge PRs, promote claims, or mark tasks
`DONE` before maintainer review and merge.

After committing, agents may optionally generate a review bundle (a full
diff-vs-`main` snapshot for the maintainer). It is not a required PR step:

```bash
./scripts/apl_review_bundle.sh
```

## Testing Rules

Add tests for:

- exact pendulum data generation;
- model fitting;
- scoring;
- CLI smoke run.

Tests must be fast.
Do not make tests depend on external APIs.

## Completion Expectations

Before marking work complete, run:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
git diff --exit-code
```

`python3 -m pytest` runs in parallel by default via `pytest-xdist` (installed
with the dev extras: `pip install -e ".[dev]"`), matching CI on Windows,
macOS, and Linux. For a faster cross-platform inner loop while iterating, run
`python3 scripts/validate_fast.py` (lint, strict repository validation, then
the non-`full_repo` tests with a slowest-ten timing report). Use
`python3 -m pytest -n0` to force a serial run when debugging a single test.
For narrow task PRs, run the task YAML validation commands first and use
`python3 scripts/apl_task_validation_plan.py --task TASK-XXXX` for advisory
diff-aware guidance. If parallel pytest fails in a Windows sandbox, run
`python3 scripts/apl_agent_doctor.py --probe-pytest-runtime --no-gh-auth-check`;
do not automatically replace a narrow PR's validation with a serial full-suite
run. Use targeted `-n0` debugging and keep broad cross-platform coverage in CI.
Treat test ordering as a staged-lane concern: run cheap deterministic gates
first and keep slow `full_repo` smoke tests at the end. Do not add dependencies
between individual tests merely to control their parallel execution order.
Tests with measured xdist resource or path sensitivity belong in the
same `xdist_group`, which keeps them on one worker while unrelated tests
continue in parallel.

If a change touches CLI behavior, include a smoke test.
If a change touches scientific formulas, include a numerical regression test.
For branch naming, commit messages, PR titles, task-state transitions, and the
standard execution flow, use `docs/agent-task-protocol.md`.


────────────────────────────────────────────────────────────────────────

# Claude Code Entry Point
<!-- source: CLAUDE.md -->

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
5. `docs/task-views/research.md`
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


────────────────────────────────────────────────────────────────────────

# Project Strategy
<!-- source: docs/strategy.md -->

# Strategy

## Current Phase

`v0.2-public-alpha candidate — multi-campaign agent research network hardening`

The repository is still gated by maintainer review and release discipline, but
the strategic center has moved from a single flagship/private-alpha dry run to a
multi-campaign network where many agents can safely work in parallel.

The next capability milestone after `v0.2` is **`v0.3` — the Research Factory
Layer**: a reusable bounded workflow that turns one-lane audits into
high-throughput, controls-first candidate generation routed into negative and
shortlist memory (no automatic claims). Exit criteria and sequencing are in
[roadmap.md](./roadmap.md) (`v0.3 — Research Factory Layer`).

## Mission

Build verification-first scientific infrastructure for testing, falsifying,
scoring, and reusing physics hypotheses.

## Strategic North Star

Open Agent Science is the umbrella goal: prove that human-owned AI agents can
produce reproducible, reviewable, citable scientific outputs in shared public
memory.

Autonomous Physics Lab is the first domain proof-of-work for that goal:
physics-first, verification-first, and campaign-based. APL should show that
agents can preserve evidence, failures, limitations, replays, predictions, and
review tiers without turning every interesting pattern into a claim.

APL is not trying to generate dramatic claims on demand. It is trying to make
scientific work reproducible, reviewable, and reusable through deterministic
code and version-controlled evidence.

APL is also being shaped as an open agent network for science: many humans can
connect their AI agents to shared campaigns, while the repository coordinates
tasks, sandbox evidence, negative results, prediction registries, review gates,
and public scientific memory.

## Strategic Shift

The repository is no longer focused mainly on bootstrap infrastructure work or a
single scientific lane. The base now exists well enough to support a new
emphasis:

- maintain many safe, bounded, data-backed research lanes rather than minimizing
  task count for its own sake;
- distinguish good task growth (campaign-scoped, gated, dataset-backed lanes)
  from bad task sprawl (open-ended work without baselines, holdouts, or review
  gates);
- turn high-quality sandbox evidence into `AGENT_PUBLISHED` and
  `AGENT_VALIDATED` scientific memory when explicit result-promotion gates pass;
- curate active and preparing campaigns with clear source state, allowed work,
  forbidden work, and honest limitations;
- keep public-launch work gated behind validation, review discipline, and
  conservative claim boundaries.

## Current Priorities

1. Operate APL as a multi-campaign open agent research network, not as a small
   collection of isolated local experiments.
2. Keep Nuclear Mass Surface as the flagship science track,
   using baseline residual maps, shell-closure diagnostics, holdout discipline,
   post-AME2020 time-split validation, and conservative correction-term framing
   instead of broad discovery claims.
3. Promote Exoplanet Mass-Radius as the active secondary benchmark surface:
   pinned snapshots, baseline comparisons, residual failure maps, and
   selection-effect audits are useful without claiming a new planet law.
4. Prepare new campaign lanes through source-first scaffolds before hypothesis
   batches: Textbook Formula Audit, Quantum Size Effects, and Atomic-Clock
   Residuals.
5. Treat Materials Property Residuals as an emerging reusable-dataset and
   benchmark-readiness lane: `MD-0001` is source-pinned and replayable, but
   benchmark promotion remains blocked until controls, split sensitivity, and
   reuse metadata make a narrower result path credible.
6. Validate the contributor and agent workflow with measurable gates:
   task-based PRs, scientific sandbox PRs, independent replay or audit PRs,
   clean review-helper behavior, closeout, gated result publication, and zero
   automatic claim promotion.
7. Prepare and maintain a clear Mission Control and campaign-map layer so new
   contributors can see what APL is trying to do and where evidence already
   exists.
8. Treat open-agent-network coordination as a first-class design goal: many
   agents may work in parallel, but only through task contracts, disjoint
   branches or worktrees, disjoint artifact surfaces, evidence gates, and
   maintainer review.
9. Keep Koide and particle-mass work falsification-first, narrow in scope, and
   resistant to numerology overclaim.
10. Improve visual result summaries, campaign summaries, and contributor-facing
   navigation around the strongest current evidence, including negative-result
   surfaces.
11. Package the current result layer into a coherent v0.2 story without
   relaxing scope or limitation wording.
12. Use [blind-holdout-benchmark-protocol.md](./blind-holdout-benchmark-protocol.md)
   for future prediction-style benchmarks that need a visible before/after
   target reveal boundary.
13. Distinguish retrospective time-split benchmarks from prospective prediction:
   post-AME2020 nuclear-mass evaluation is a stronger holdout surface, while
   true future predictions require a pre-registered prediction artifact.
14. Prepare public launch only after the explicit gates in
   [public-release-gates.md](./public-release-gates.md) are satisfied.

Future research direction is curated through
[future-research-portfolio.md](./future-research-portfolio.md). The current
portfolio should be read as a campaign portfolio, not a scarcity list:
`ACTIVE` lanes should stay bounded and data-backed; `PREPARE` lanes should
build source, schema, baseline, and holdout readiness; `GUARDRAIL` and
`WATCHLIST` lanes should not become implementation work without a new
maintainer-approved task and stronger gates.

## Current Goal

Demonstrate that APL can run honest scientific campaigns, gated evidence
publication, and multi-agent contributor work at the same time, without
relaxing verification standards or overstating benchmark results.

## Steering Metric

Task throughput is not the north-star metric. APL should optimize for durable
scientific-output throughput: reproducible `RESULT-*` artifacts, preserved
negative and inconclusive evidence, registered predictions awaiting reveal,
agent-validated replays, maintainer-reviewed scoped claims, and reusable
knowledge. A healthy campaign is not the one with the most activity; it is the
one that steadily converts bounded work into reviewable scientific memory while
making blockers and failed ideas visible.

Near public-alpha, the most important metrics are:

- `AGENT_PUBLISHED`, `AGENT_VALIDATED`, maintainer-reviewed, and externally
  replicated artifacts that remain clearly tiered;
- independent replay PRs and adversarial audit PRs;
- reusable source-pinned datasets with citation and reuse metadata;
- negative, null, overfit, or inconclusive results that prevent repeated weak
  work;
- external contributors or agent operators who can reproduce the branch,
  validation, review, and closeout loop without private context.

## Current North-Star Outcomes

- campaign-oriented scientific work with explicit boundaries, current evidence,
  and next-safe-task surfaces;
- reproducible results that preserve failure modes and limitation wording;
- contributor onboarding that does not require tribal knowledge to understand
  tasks, review expectations, or release posture.

Current visible evidence includes:

- the pendulum gauntlet result package from `EXP-0001/RUN-0003`;
- charged-lepton Koide reproduction from `EXP-0004/RUN-0004`;
- the tau holdout benchmark from `EXP-0005/RUN-0005`;
- the dimensional-analysis validator MVP result from `EXP-0006/RUN-0006`;
- the neutrino and quark Koide falsification results from `EXP-0007/RUN-0001`
  and `EXP-0008/RUN-0001`;
- the negative-results registry as a maintained output surface;
- the nuclear-mass baseline and sandbox autonomy surface, including split
  sensitivity replay, as a flagship validation track that still requires
  stronger time-split evidence before any broader scientific claim.

These results are useful because they are reviewable and reproducible, not
because they justify expansive scientific claims.

## Current Execution Model

The repository uses a shared task pool with branch-based execution.

- a task defines the contract;
- an agent or human picks one atomic task;
- multiple agents can work in parallel when branches, worktrees, and artifact
  surfaces stay disjoint;
- validation runs before handoff;
- task files and board state remain the coordination layer;
- maintainer review stays the decision point for merge and closeout.

The repository remains private until the release gates are satisfied and a
maintainer decides the v0.2 narrative matches the evidence.

## Non-Goals

- Do not frame narrow benchmark outputs as discovery-level physics.
- Do not describe particle-mass results as explanations of mass generation.
- Do not collapse scoped reproductions and scoped falsifications into a single
  global statement about all Koide-like ideas.
- Do not claim universal validity from configured-range validation.
- Do not add dashboard, public API, literature ingestion, or public task
  network before current campaign and workflow gates are met.
- Do not turn `WATCHLIST` topics from
  [future-research-portfolio.md](./future-research-portfolio.md) into
  implementation work without a new maintainer task and stronger guardrails.
- Do not use LLM prose as a substitute for deterministic validation.

## Decision Rule

When choosing between faster expansion and stronger verification, choose
stronger verification.


────────────────────────────────────────────────────────────────────────

# Current Missions
<!-- source: docs/current-missions.md -->

# Current Missions

APL uses an **Agent First / Research First / Parallel Work** entrypoint.

The default path for a new coding agent is not "scan every file and pick
something small." The default path is:

```bash
python3 scripts/apl_mission.py --output onboarding
```

Onboarding mode should explain the current scientific mission, show a few
`READY` options with estimated effort, recommend one, and wait before editing
files. For autonomous agent context after the user already understands the
flow, use:

```bash
python3 scripts/apl_mission.py --output agent
```

The older `--onboarding` and `--agent-prompt` aliases are preserved for
compatibility, but new docs should prefer the explicit `--output ...` form.

Support, review, and closeout work remain explicit:

```bash
python3 scripts/apl_mission.py --mode support
python3 scripts/apl_mission.py --mode maintainer
```

Mission policy and campaign guardrails live in
[`../missions/current.yaml`](../missions/current.yaml). Live task candidates
come from canonical `tasks/TASK-*.yaml` files through the mission script. For
lighter navigation than the full generated board, use:
[`public-science-dashboard.md`](./campaigns/public-science-dashboard.md),
[`research.md`](./task-views/research.md),
[`support.md`](./task-views/support.md),
[`release.md`](./task-views/release.md),
[`watchlist.md`](./task-views/watchlist.md), and
[`blocked.md`](./task-views/blocked.md).

For parallel-capacity planning — how many agents fit each lane — read each
campaign's `agent_capacity` block in
[`campaign_profiles/_catalog.yaml`](../campaign_profiles/_catalog.yaml) (the
generated portfolio index) and
query the on-demand task-to-campaign index
(`python3 scripts/apl_task_campaign_index.py`).

## Recommended Mission Now

**Exoplanet Mass-Radius Benchmark** remains the default near-term
public-safe benchmark story, but it is not currently a residual-scoring lane.
`TASK-0515` records `NO_GO_PRESERVE_NEGATIVE_CONTROL_MEMORY`, and the later
`EXO-0002` coverage gate did not reopen scoring. The active path is now
negative/control result-publication preflight, source-version monitoring, and
an `EXO-0003` acquisition trigger, not another current-snapshot residual pilot.

Recommended default: start with the live `research` recommendation from
`python3 scripts/apl_mission.py --output onboarding`. Right now the strongest
science path is the post-gate data-to-benchmark wave: Materials `MD-0002`
acquisition and validation, Atomic Nemitz `ACR-0002` row curation, Stellar M-L
DEBCat Route 2 / row curation, and Quantum source-artifact handoff. Exoplanet
remains monitor-only until a material source-version trigger appears; do not
run another current-snapshot residual pilot.
At handoff, agents should route the output through
[`result-promotion-protocol.md`](./result-promotion-protocol.md): state the
verdict, destination, review tier, Gate A/B status, limitations, and blockers.

Nuclear Mass Surface remains the flagship validation challenge, but the latest
controls-first lanes landed as negative, inconclusive, diagnostic-only,
chain-local, or validation-regressing memory. The best Nuclear work now is
reveal-readiness, F2/factory result routing, and only tightly bounded
controls-first follow-up. Quantum Size Effects remains source-artifact gated:
Almeida and Vossmeyer are promising but still need checksum/source-copy
decisions before row curation. Atomic-Clock Residuals should now prioritize
Nemitz `ACR-0002`; the Pizzocaro PSD covariance artifact is useful diagnostic
evidence, but its row-admissibility gate preserved the aggregation blocker. New
campaign ideas should enter through source/schema/baseline scaffolds first,
not broad hypothesis batches.

## Current Mission Shape

APL currently has one flagship validation campaign, one active secondary
benchmark surface, two source-readiness surfaces, one public-friendly
formula-audit scaffold, and one emerging reusable-dataset lane. That mix is
deliberate:
some agents can stress the strongest current evidence, others can build
source/baseline discipline, and curators can prepare new campaign lanes without
turning watchlist topics into formula-search work.

| Surface | Role right now | Good agent work |
| --- | --- | --- |
| [Nuclear Mass Surface](./campaigns/nuclear-mass-surface.md) | Flagship validation challenge with baseline residuals, sandbox scouts, frozen predictions, no-leakage contract, reveal-readiness blockers, and several negative/control lanes | reveal-readiness matrix, F2/factory result routing, and new lanes only when controls and stop conditions are predeclared |
| [Exoplanet Mass-Radius](./campaigns/exoplanet-mass-radius.md) | Public-safe benchmark surface with pinned snapshots, null-baseline controls, external-reviewer capsule, and closed current-snapshot residual scoring | preserve negative/control memory and define source-version or `EXO-0003` trigger work before any new residual audit |
| [Quantum Size Effects](./campaigns/quantum-size-effects.md) | Source-readiness campaign before any measurement benchmark; Vossmeyer and Almeida are promising but source-artifact blocked | Vossmeyer source-copy handoff, Almeida checksum/reuse decision, and direct-row readiness gates |
| [Atomic-Clock Residuals](./campaigns/atomic-clock-residuals.md) | High-precision fresh-data surface with Beloy rows, real-row loader, synthetic dry-run, Nemitz/Pizzocaro/Lange source surfaces, and covariance policy | Nemitz `ACR-0002` row curation first; Pizzocaro remains diagnostic-only unless an observable-harmonization contract lands |
| [Textbook Formula Audit](./campaigns/textbook-formula-audit.md) | Public verifier lane with exact-reference fixtures and a Gate-B-validated Stefan-Boltzmann software/convention result; empirical audits remain gated | DEBCat Route 2 storage decision, normalized component rows, then Stellar M-L empirical audit |
| [Materials Property Residuals](./campaigns/materials-property-residuals.md) | Emerging reusable-dataset lane with `MD-0001`, independent replay, controls, split sensitivity, and authorized `MD-0002` acquisition | Execute `MD-0002` maintainer-gated acquisition, validate holdout binding, then run the formation-energy benchmark |

Mature quality-floor tracks still matter: Pendulum, Dimensional Analysis, and
Particle Mass Relations keep the repository honest about exact references,
falsification, and overclaim resistance. They are not the default landing-page
focus unless the maintainer asks for replay, documentation, or benchmark
hygiene work.

## Campaign Portfolio Direction

APL should grow by adding bounded campaign lanes, not by asking agents to search
open-endedly. Good growth means each lane has a source surface, baseline,
holdout or replay discipline, allowed work, forbidden work, and a clear
promotion route for evidence.

Near-term portfolio shape:

| Portfolio role | Campaigns | Notes |
| --- | --- | --- |
| Flagship validation challenge | Nuclear Mass Surface | Keep reveal scoring blocked until a no-peek source passes. Preserve local-curvature, pairing-asymmetry, magic-parity, mixed shell-axis transfer, factory no-shortlist, and broad-refit validation regression as negative/inconclusive memory unless a later review creates a narrower publication artifact. |
| Default public benchmark story | Exoplanet Mass-Radius | Preserve the current pinned-snapshot compact-radius surface as negative/control memory; continue source-version discipline and reopen residual audits only after a materially changed snapshot or approved trigger. |
| Prepare/source-readiness | Quantum Size Effects | Stay direct-row/source-artifact first before modeling or fitting; Vossmeyer and Almeida need source-copy/checksum decisions. |
| Pinned-dataset to benchmark-readiness | Atomic-Clock Residuals | Curate Nemitz `ACR-0002` or explicitly preserve the blocker; do not use Pizzocaro as a benchmark row without harmonization. |
| Public-friendly verifier lane | Textbook Formula Audit | Use exact-reference fixtures and DEBCat source gates first; Route 2 and row curation must land before empirical M-L metrics. |
| Emerging reusable-dataset lane | Materials Property Residuals | Treat `MD-0001` as source-pinned dataset memory; `MD-0002` is now the strongest near-term data-to-benchmark path. |
| Guardrail/watchlist | g-2, Hubble, broad constants, particle-mass formula search | Keep schema, admissibility, or falsification-first only unless a maintainer creates a stronger gated task. |

## Default Research Mode

Research Mode is for:

- bounded hypothesis tests;
- replay and split-sensitivity checks;
- adversarial audits of sandbox evidence;
- source and provenance review;
- negative, null, overfit, or inconclusive result preservation;
- PR-ready result, evidence, or blocker artifacts.

Research Mode is now evidence-publication aware, but not claim-promotion
driven. Agents publish reproducible evidence only when task scope and gates
allow it; agents validate each other; maintainers endorse interpretation; and
external data confirms predictions. Claim status transitions and knowledge
endorsement remain maintainer-only in Phase 1.

The broader organization frame is Open Agent Science. APL is the first physics
proof-of-work: agents should optimize for citable, replayable scientific memory
and visible limitations, not for raw task count or dramatic discovery wording.

## Parallel Agent Policy

Multiple agents can work in parallel when they increase coverage rather than
duplicate effort.

Use these rules:

- one local checkout should usually run one task at a time;
- parallel local agents should use separate branches or git worktrees;
- prefer disjoint campaigns, datasets, hypothesis families, or review
  surfaces;
- same-campaign parallel work is allowed only when artifact surfaces are
  clearly separated;
- executor agents should offer only `READY` tasks as available work;
- `REVIEW_READY`, `DONE`, and `BLOCKED` tasks are for review, closeout, or
  maintainer triage, not new executor work;
- do not guess new canonical task ids during parallel work unless the
  maintainer explicitly asks for canonical task creation.

## What To Avoid Right Now

- Do not run Nuclear reveal scoring until a source-grade post-freeze data
  release passes the reveal source gate.
- Do not treat retrospective Nuclear audits as future blind validation.
- Do not present `LOCAL-CURVATURE-001` as a surviving Nuclear no-leakage
  candidate after `TASK-0394`; route it through negative/inconclusive memory.
- Do not start the Quantum baseline benchmark until direct measurement rows or
  an explicit weaker calibration-consistency scope is approved.
- Do not fit atomic-clock or anomaly-style campaigns before source and
  covariance semantics are reviewable.
- Do not present exoplanet regime scouts as corrections or planet-composition
  discoveries; after the null-baseline family audit, compact-radius is public-
  safe only as a control-sensitive benchmark diagnostic with scorecard
  limitations attached.
- Do not run Textbook Formula Audit metrics until the selected formula has a
  source/baseline/holdout plan.

## Copy-Paste Agent Prompt

Generate the current prompt with:

```bash
python3 scripts/apl_mission.py --output agent
```

Short onboarding version:

```text
You are working in Autonomous Physics Lab.

Start in Agent First Research Mode with onboarding. Read AGENTS.md and
docs/agent-task-protocol.md, then run `python3 scripts/apl_mission.py --output onboarding`.
Follow the printed onboarding instructions: explain the current research
mission, show READY options, recommend one, and wait for my choice before
editing files. Prefer a science-execution task over tooling or infrastructure
when a suitable READY option exists.
```


────────────────────────────────────────────────────────────────────────

# Machine-Readable Missions
<!-- source: missions/current.yaml -->

default_mode: research
updated: "2026-06-02"

curator_cycle:
  decision: updated
  updated: "2026-06-02"
  source: "TASK-0531"
  note: >
    Mission guidance now reflects the latest merged science wave. Nuclear
    remains the flagship validation challenge, but TASK-0517 found no
    control-surviving NMD-0003 factory shortlist and TASK-0531 showed that a
    simple broad-surface NMD-0003 refit regresses on the validation holdout.
    The next Nuclear path is a baseline-family and split/domain gate before
    another residual-feature sprint. Exoplanet remains preserved as
    negative/control memory until a second-snapshot coverage gate and dry-run
    are reviewed, while Atomic and Quantum continue through source gates.

policy:
  name: "Agent First, Research First, Parallel Work"
  summary: >
    New contributors and coding agents should start from the highest-value
    reviewable research mission by default. Support, microtask, review, and
    closeout lanes remain available as explicit modes. Multiple agents are
    encouraged to work in parallel across different campaigns, or within the
    same campaign when they use separate branches/worktrees and disjoint
    hypothesis families, datasets, or artifact surfaces. Agents publish
    reproducible evidence when gates pass, agents validate each other,
    maintainers endorse interpretation, and external data confirms predictions.
  defaults:
    - "Start in research mode unless the maintainer explicitly asks for support, review, or closeout."
    - "Prefer hypothesis testing, replay, falsification, or sandbox result drafts over docs-only work."
    - "Use docs/result-promotion-protocol.md at handoff to state verdict, destination, review tier, Gate A/B status, limitations, and blockers."
    - "Keep outputs sandbox-only unless the task scope and result-promotion gates explicitly allow AGENT_PUBLISHED or AGENT_VALIDATED RESULT/PRED artifacts."
    - "Keep claim status transitions and knowledge endorsement maintainer-only in Phase 1."
    - "Prefer several bounded parallel science lanes over one oversized catch-all task when multiple agents are available."
    - "Parallel agents may work inside the same campaign when their hypothesis lanes and write surfaces are disjoint."
    - "Never promote claims, rewrite canonical results, or use breakthrough-style wording automatically."
  maintainer_modes_preserved:
    - review
    - closeout
    - support

global_forbidden:
  - "no automatic claim promotion"
  - "no direct pushes to main"
  - "no canonical result rewrites unless the task explicitly requires it"
  - "no breakthrough, proof-style, or unlimited-scope wording"
  - "no speculative Hubble, g-2, or constants formula-search flagship work"

modes:
  research:
    label: "Research Mode"
    description: "Default lane for autonomous scientific work: audit, replay, hypothesis testing, sandbox runs, result-routing, and reviewable PR artifacts."
  audit:
    label: "Research Audit Mode"
    description: "Adversarial validation of existing sandbox evidence before follow-up work expands the surface."
  support:
    label: "Support Mode"
    description: "Infrastructure, docs, test, packaging, and microtask work. Useful, but not the default for scientific contributors."
  maintainer:
    label: "Maintainer Mode"
    description: "Review, merge recommendation, closeout, board sync, and context-refresh assistance. Advisory only."

missions:
  - id: nuclear-mass-surface
    title: "Nuclear Mass Surface"
    rank: 2
    status: flagship_validation
    scientific_value: high
    risk: medium
    recommendation: "Flagship validation challenge. The NMD-0003 large-surface factory sprint produced control-dominated negative memory with no shortlist, and the first broad-surface NMD-0003 refit improved train/full metrics while regressing on the validation holdout. The next positive-result path is a baseline-family and split/domain gate before any more expressive residual families or prediction-freeze work."
    why_now:
      - "real AME-style nuclear-mass dataset surface exists"
      - "frozen baseline and holdout protocol exist"
      - "AGENT-RUN-0005 and HYP-PROPOSAL-0021 exist as sandbox-only evidence"
      - "independent audit exists and AGENT-RUN-0006 now captures split-sensitivity replay evidence"
      - "a review-ready robustness gate defines allowed follow-up, negative controls, and promotion blockers"
      - "AGENT-RUN-0007 now records a conservative source-manifest-only guard with INCONCLUSIVE verdict"
      - "AGENT-RUN-0008 now records active retrospective post-AME2020 time-split evidence with INCONCLUSIVE verdict"
      - "PRED-0063 through PRED-0068 now freeze the shell-axis-balanced-001 prospective mini-wave"
      - "source preflight and synthetic reveal mechanics are done, but TASK-0307 found no acceptable post-registration source manifest"
      - "AGENT-RUN-0018 now records the full-known-data retrospective audit without prospective reveal scoring"
      - "TASK-0333 fixed shell-axis as diagnostic-only, so fresh hypothesis lanes should replace additional shell-axis slicing"
      - "TASK-0394 falsified LOCAL-CURVATURE-001 under the bounded no-leakage/control panel, so local-curvature is now negative/inconclusive memory unless TASK-0428 narrows the publication boundary"
      - "TASK-0474 and TASK-0475 landed as negative/control results, while TASK-0476 showed shell-axis transfer is mixed and chain-local rather than broadly predictive"
      - "TASK-0507 ran the first Research Factory sprint on NMD-0002 and produced no shortlist: the current 11-row training slice is underpowered for strong residual-law conclusions"
      - "TASK-0479 identified NMD-0003 source-gated AME2020 measured training data as the blocker before another meaningful Nuclear factory sprint"
      - "TASK-0516 landed the NMD-0003 source-gated AME2020 measured training surface with 2309 committed rows and frozen holdout exclusions"
      - "TASK-0517 ran the first NMD-0003 Research Factory sprint: 73 generated candidates, 72 executed, 0 shortlisted, and the strongest apparent gains rejected by matched random-slice controls"
      - "TASK-0518 confirmed NMD-0002 perturbation survival remains INCONCLUSIVE control evidence, not independent validation"
      - "TASK-0531 froze the first NMD-0003 broad-surface baseline refit and found a validation-holdout regression: useful sandbox evidence, but not a promotable baseline improvement"
    forbidden:
      - "do not promote HYP-PROPOSAL-0021 to a claim automatically"
      - "do not describe the residual candidate as breakthrough physics"
      - "do not run additional second-batch expansions before adversarially reviewing the completed narrow lanes"
      - "do not call retrospective post-AME2020 evaluation strict blind prediction"
      - "do not promote internal split wins unless the robustness gate and external-style validation both allow it"
      - "do not run active post-AME2020 metrics without a committed row-level holdout dataset"
      - "do not promote any second-batch sandbox candidate after TASK-0204 without a maintainer-approved follow-up task"
      - "do not score PRED-0063 through PRED-0068 before source preflight, no-peek review, and explicit maintainer approval"
      - "do not add more shell-axis PRED entries before the mini-wave reveal-readiness implications are reviewed"
      - "do not treat shell-axis diagnostic evidence as a reason to stop Nuclear hypothesis testing"
      - "do not present LOCAL-CURVATURE-001 as a surviving no-leakage Nuclear candidate after TASK-0394"
    actions:
      - id: row-level-post-ame2020-holdout
        label: "Add reviewed row-level post-AME2020 holdout dataset before active time-split metrics"
        task_id: TASK-0196
        mode: research
        status: done
        priority: high
        difficulty: high
        recommended: false
        expected_outputs:
          - "data/nuclear_masses/post_ame2020_holdout.yaml"
          - "tests/test_post_ame2020_holdout_dataset.py"
          - "docs/notes/post-ame2020-holdout-dataset-review.md"
      - id: post-ame2020-time-split-benchmark
        label: "Review active retrospective post-AME2020 time-split evidence before any second nuclear batch"
        task_id: TASK-0197
        mode: research
        status: done
        priority: high
        difficulty: high
        recommended: false
        expected_outputs:
          - "agent_runs/AGENT-RUN-0008/metrics.json"
          - "agent_runs/AGENT-RUN-0008/report.md"
          - "docs/reviews/post-ame2020-time-split-benchmark-result.md"
      - id: nuclear-validation-queue
        label: "Finish Nuclear negative-result packaging and preflight decisions before another hypothesis burst"
        task_id: null
        mode: research
        priority: high
        difficulty: medium
        recommended: true
        expected_outputs:
          - "Treat AGENT-RUN-0018 as sandbox retrospective evidence only"
          - "Treat TASK-0333 as the stop point for the shell-axis audit loop"
          - "Treat TASK-0394 as a no-leakage falsification for LOCAL-CURVATURE-001 unless TASK-0428 identifies a narrower negative-result publication artifact"
          - "Treat TASK-0449 as inconclusive residual-free high-error cluster memory; do not repeat the same taxonomy as a near-miss"
          - "Use live_task_candidates before naming any remaining READY Nuclear hypothesis lane"
          - "Use live_task_candidates from python3 scripts/apl_mission.py --output json"
          - "Keep at least five independent READY scientific tasks available across three active campaigns when possible"
          - "Use docs/result-promotion-protocol.md to decide whether the final output is sandbox-only, RESULT/PRED draft, review note, source artifact, or task proposal"
          - "Publish RESULT/PRED artifacts only when the selected task explicitly allows it and Gate A or maintainer-approved manual Gate A review passes"
          - "Keep TASK-0305 blocked until a future source manifest satisfies the no-peek checklist"
          - "Use the TASK-0448 gauntlet for any future maintainer-approved controls-first Nuclear lane"
          - "Treat TASK-0450 and TASK-0451 as review-ready negative/control-dominated sandbox memory, not executable READY options"
          - "Treat TASK-0474 and TASK-0475 as additional negative/control memory, not promising formula candidates"
          - "Treat TASK-0476 as evidence that shell-axis behavior is chain-local and mixed under leave-family-out transfer"
          - "Prefer TASK-0477, TASK-0478, and TASK-0479 over new broad Nuclear fitting lanes"
          - "Treat TASK-0517 as completed control-dominated negative memory: do not rerun the same NMD-0003 factory sprint without a new baseline or new approved feature family"
          - "Keep post_ame2020_holdout.yaml out of training; use it only through explicit retrospective/reveal-style validation tasks"
          - "Treat TASK-0518 as completed NMD-0002 uncertainty-control memory, not as independent validation data"
          - "TASK-0531 shows simple broad-surface NMD-0003 refit is not enough: validation holdout MAE regressed, so Nuclear needs TASK-0535-style baseline-family and split/domain gating before another factory sprint"
          - "New Nuclear hypothesis lanes must predeclare leakage checks, negative controls, and stop conditions before candidate fitting"
        validation:
          - "python3 -m ruff check ."
          - "python3 -m pytest"
          - "python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings"
      - id: audit-agent-run-0005
        label: "Adversarially audit AGENT-RUN-0005 / HYP-PROPOSAL-0021"
        mode: audit
        priority: high
        difficulty: medium
        expected_outputs:
          - "docs/reviews/adversarial-review-AGENT-RUN-0005.md"
      - id: second-bounded-nuclear-batch
        label: "Second bounded nuclear sandbox lanes completed; adversarially review them before more expansion"
        mode: future
        status: review_required
        priority: medium
        difficulty: high
        gated_by:
          - maintainer-reviewed-split-sensitivity-replay
          - audit-agent-run-0005
          - nuclear-robustness-gate-review
          - reviewed-row-level-post-ame2020-holdout-dataset
          - reviewed-post-ame2020-time-split-benchmark
          - use-narrow-task-0200-0201-0202-lanes-before-unblocking-umbrella
          - adversarial-review-task-0204
      - id: nuclear-prediction-variant-expansion
        label: "Completed historical PRED-0021+ variant expansion; do not expand registry again before reveal-readiness review"
        task_id: null
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        gated_by:
          - prediction-registry-policy-task-0189
          - first-prediction-slate-task-0205
        expected_outputs:
          - "use READY TASK-0228 through TASK-0237 as parallel lanes"
          - "each lane adds two frozen PRED-0021+ entries plus pre-reveal validation"
          - "no live external fetch, reveal comparison, claim promotion, or retrospective metric framing"
      - id: nuclear-deformation-proxy-lane
        label: "Run Nuclear deformation-proxy hypothesis lane"
        task_id: TASK-0338
        mode: research
        status: review_ready
        priority: high
        difficulty: high
        recommended: false
        expected_outputs:
          - "sandbox mini-loop with controls and verdict"
      - id: nuclear-local-curvature-lane
        label: "Run Nuclear local residual curvature hypothesis lane"
        task_id: TASK-0339
        mode: research
        status: review_ready
        priority: high
        difficulty: high
        recommended: false
        expected_outputs:
          - "sandbox mini-loop with chain-transfer diagnostics"
      - id: nuclear-odd-even-shell-lane
        label: "Run Nuclear odd-even shell-interaction hypothesis lane"
        task_id: TASK-0340
        mode: research
        status: review_ready
        priority: high
        difficulty: high
        recommended: false
        expected_outputs:
          - "interaction candidates compared to pairing-only and shell-only controls"
      - id: nuclear-boundary-lane
        label: "Run Nuclear measured/extrapolated boundary hypothesis lane"
        task_id: TASK-0341
        mode: research
        status: review_ready
        priority: medium
        difficulty: high
        recommended: false
        expected_outputs:
          - "source-status diagnostics or blocker review"
      - id: nuclear-uncertainty-weighted-lane
        label: "Run Nuclear uncertainty-weighted residual lane"
        task_id: TASK-0342
        mode: research
        status: review_ready
        priority: medium
        difficulty: medium
        recommended: false
        expected_outputs:
          - "uncertainty preflight and weighted residual diagnostics"
      - id: nuclear-high-error-cluster-lane
        label: "Preserve Nuclear high-error cluster lane as diagnostic-only history"
        task_id: TASK-0449
        mode: research
        status: review_ready
        priority: high
        difficulty: high
        recommended: false
        expected_outputs:
          - "TASK-0449 residual-free taxonomy is INCONCLUSIVE under current training sparsity"
          - "do not repeat the same cluster taxonomy without a declared finer taxonomy or larger curated training slice"

  - id: quantum-size-effects
    title: "Quantum Size Effects"
    rank: 4
    status: active_data_readiness
    scientific_value: medium
    risk: medium
    recommendation: "Active second campaign: prioritize direct-measurement data readiness or an explicit calibration-consistency waiver before any baseline benchmark."
    why_now:
      - "campaign scaffold, dataset schema, holdout protocol, and source manifest exist"
      - "calibration-derived row-level seeds exist, but measurement-grade rows are still missing"
      - "the campaign is visually explainable and can become a real-data benchmark once provenance is fixed"
      - "TASK-0491 can decide whether a weaker calibration-consistency path is allowed without unblocking the direct-row benchmark"
    forbidden:
      - "do not run autonomous formula search before a frozen baseline exists"
      - "do not treat calibration-derived rows as direct measurement evidence"
      - "do not include synthesis recipes, chemical handling guidance, biomedical claims, or device claims"
    actions:
      - id: quantum-direct-digitization-package
        label: "Prepare a quantum direct-measurement digitization or table-value package"
        task_id: TASK-0325
        mode: research
        status: done
        priority: high
        difficulty: high
        expected_outputs:
          - "auditable digitization package, direct row seed, or explicit blocker review"
      - id: quantum-calibration-waiver-decision
        label: "Review TASK-0326 waiver decision before creating any calibration-consistency benchmark"
        task_id: null
        mode: research
        status: done
        priority: medium
        difficulty: medium
        recommended: false
        expected_outputs:
          - "use docs/reviews/quantum-calibration-consistency-waiver-decision.md after merge"
          - "keep TASK-0225 blocked unless a future maintainer-approved scope change lands"
      - id: quantum-jasieniak-source-artifact
        label: "Review TASK-0334 Jasieniak 2011 source-artifact package before unblocking row curation"
        task_id: null
        mode: research
        status: review_ready
        priority: high
        difficulty: high
        expected_outputs:
          - "use docs/reviews/quantum-jasieniak-2011-source-artifact-package.md after merge"
          - "keep TASK-0336, TASK-0293, and TASK-0225 blocked until a checksum-pinned SI/table extraction or deterministic digitisation artifact is reviewed"
      - id: quantum-calibration-consistency-scope
        label: "Define calibration-curve consistency benchmark scope"
        task_id: TASK-0335
        mode: research
        status: done
        priority: high
        difficulty: medium
        expected_outputs:
          - "calibration-only benchmark scope without metrics"
      - id: quantum-open-direct-source-triage
        label: "Triage open quantum-dot direct table sources"
        task_id: TASK-0347
        mode: research
        status: review_ready
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "ranked alternative direct-source candidates without row values"
      - id: quantum-norris-bawendi-source-artifact
        label: "Norris/Bawendi source-artifact review completed; direct rows still blocked"
        task_id: TASK-0489
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "source artifact/blocker review landed without synthetic or calibration-derived row promotion"
          - "keep direct-row curation blocked until a deterministic table or digitization artifact is approved"
      - id: quantum-digitization-fixture-dry-run
        label: "Run quantum figure-digitization fixture dry-run"
        task_id: TASK-0490
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "synthetic fixture that tests digitization mechanics without claiming real measurement rows"
      - id: quantum-calibration-consistency-scorecard
        label: "Define Quantum calibration-consistency go/no-go scorecard"
        task_id: TASK-0491
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "explicit decision on whether a weaker calibration-consistency benchmark may exist separately from TASK-0225"

  - id: atomic-clock-residuals
    title: "Atomic Clock Residuals"
    rank: 3
    status: active_pinned_dataset
    scientific_value: medium
    risk: medium
    recommendation: "Active third campaign: move from Beloy PINNED_DATASET toward BASELINE_READY by adding the real-row loader, resolving the Nemitz row-level source blocker, separating direct and derived rows, and dry-running cross-source mechanics before any benchmark."
    why_now:
      - "fresh-data source policy exists"
      - "atomic-clock campaign scaffold and schema sketch exist"
      - "high-precision repeated measurements can support future freeze/reveal work if provenance is handled first"
      - "Beloy 2021 direct-ratio rows are committed as sandbox-only ACR-0001 with source artifact, checksum, and provenance"
      - "TASK-0402 added a PSD source-derived covariance approximation for the Beloy cross-ratios"
      - "TASK-0403 selected Nemitz 2016 / RIKEN Yb/Sr as the strongest independent second-source candidate"
      - "TASK-0452 pinned the correct Nemitz 2016 arXiv source artifact but kept ACR-0002 value rows blocked pending table-level version-drift and campaign-window checks"
      - "TASK-0454 defined the first Atomic holdout/no-peek manifest"
      - "TASK-0486 defined conservative covariance policy states for the first benchmark"
    forbidden:
      - "do not ingest real clock values before source-manifest, checksum, version-drift, and uncertainty review"
      - "do not claim constants drift, new constants, or new physics"
      - "do not mix direct frequency ratios with derived constraints without explicit flags"
      - "do not run the Yb/Sr consistency benchmark before BASELINE_READY is declared"
    actions:
      - id: atomic-source-manifest-template
        label: "Add atomic-clock source manifest template with no numerical values"
        task_id: TASK-0327
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "metadata-only source manifest template and review note"
      - id: atomic-synthetic-loader
        label: "Add synthetic-only atomic-clock loader dry-run"
        task_id: TASK-0328
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "fabricated-row loader validation with no real-data claims"
      - id: atomic-primary-source-review
        label: "Review atomic-clock direct frequency-ratio source class"
        task_id: TASK-0330
        mode: research
        status: done
        priority: high
        difficulty: medium
        expected_outputs:
          - "value-free source-class admissibility review"
      - id: atomic-derived-source-review
        label: "Review atomic-clock derived drift/constraint source class"
        task_id: TASK-0331
        mode: research
        status: done
        priority: high
        difficulty: medium
        expected_outputs:
          - "value-free derived-constraint source-class review"
      - id: atomic-real-row-readiness
        label: "Run atomic-clock real-row source gate"
        task_id: TASK-0332
        mode: research
        status: done
        priority: high
        difficulty: medium
        expected_outputs:
          - "go/no-go gate before first real atomic-clock row seed"
      - id: atomic-covariance-semantics
        label: "Review atomic-clock covariance and uncertainty semantics"
        task_id: TASK-0344
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "value-free uncertainty and covariance source semantics"
      - id: atomic-nemitz-second-source-ingestion
        label: "Nemitz 2016 Yb/Sr source artifact pinned; value rows remain blocked"
        task_id: TASK-0452
        mode: research
        status: done
        priority: high
        difficulty: high
        recommended: false
        expected_outputs:
          - "correct arXiv:1601.04582 artifact, checksum, provenance, and explicit row-level blocker"
          - "ACR-0002 rows remain blocked by version-of-record table review and campaign-window lock"
      - id: atomic-real-row-loader
        label: "Add Atomic real direct-row loader and schema reconciliation"
        task_id: TASK-0453
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "deterministic loader/tests for committed direct_measurement rows"
      - id: atomic-holdout-no-peek-manifest
        label: "Define Atomic holdout and no-peek manifest"
        task_id: TASK-0454
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "campaign-level row-role and no-peek manifest before benchmark consumers run"
      - id: atomic-fallback-source-triage
        label: "Atomic second-source fallback triage completed"
        task_id: TASK-0485
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "ranked fallback direct-ratio sources without value-bearing rows"
          - "Pizzocaro 2020 identified as the best fallback candidate, but Atomic remains source-blocked until row-level provenance and covariance semantics are resolved"
      - id: atomic-first-benchmark-covariance-policy
        label: "Atomic first-benchmark covariance policy landed"
        task_id: TASK-0486
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "policy for exact, source-derived PSD, diagonal-only, and blocked covariance states"
          - "future benchmarks must declare covariance state before metrics"
      - id: atomic-direct-derived-separation
        label: "Audit Atomic direct-vs-derived row separation"
        task_id: TASK-0487
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "policy/audit artifact that prevents direct ratios and derived constraints from sharing one residual axis"
      - id: atomic-synthetic-cross-source-dry-run
        label: "Add Atomic synthetic cross-source dry-run"
        task_id: TASK-0488
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "fabricated-row cross-source pipeline check with covariance-state labels"
      - id: atomic-baseline-readiness-gate
        label: "Rerun Atomic baseline-readiness gate"
        task_id: TASK-0455
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "BASELINE_READY / PINNED_DATASET / SOURCE_BLOCKED go-no-go after TASK-0452 through TASK-0454"
      - id: atomic-yb-sr-cross-source-benchmark
        label: "Run first Atomic Yb/Sr cross-source consistency benchmark"
        task_id: TASK-0456
        mode: research
        status: blocked
        priority: high
        difficulty: high
        recommended: false
        expected_outputs:
          - "first narrow Atomic consistency benchmark only if TASK-0455 declares BASELINE_READY"

  - id: exoplanet-mass-radius
    title: "Exoplanet Mass-Radius Benchmark"
    rank: 1
    status: active_science_output_sprint
    scientific_value: high
    risk: medium
    recommendation: "Default near-term science-output sprint: preserve the current compact-radius residual surface as negative/control memory and reopen only after a materially changed pinned snapshot or coverage gate is reviewed."
    why_now:
      - "public catalog data can support a recognizable, visual benchmark once source policy is pinned"
      - "standard mass-radius baselines create a clear comparison anchor"
      - "planet class, discovery method, host-star context, and measurement quality provide natural holdouts"
      - "the campaign can produce useful failure maps without claiming a new planet law"
      - "pinned PSCompPars snapshot, loader dry-run, first baseline, residual scouts, and selection-effect audits now exist"
      - "TASK-0427 found the compact-radius slice (R < 1.5 R_earth) to be the strongest earlier matched-control diagnostic"
      - "TASK-0404 scored the current artifact set as BENCHMARK_SUMMARY_ONLY, not claim-candidate"
      - "TASK-0480 found the mass-quartile compact-radius scout underpowered but left an upper-mass-half diagnostic hint"
      - "TASK-0482 froze the second-snapshot target set and reveal conditions without live fetching"
      - "TASK-0484 packaged an external-reviewer replication capsule around the current benchmark metrics"
      - "TASK-0483 found that nearest-radius null baselines match or beat CK17-style residuals across the highlighted true-mass slices, so the compact-radius story is control-sensitive"
      - "TASK-0515 recorded NO_GO_PRESERVE_NEGATIVE_CONTROL_MEMORY for another compact-radius residual or host-context pilot on the current pinned snapshot"
    forbidden:
      - "do not fetch live archive data before a pinned snapshot policy exists"
      - "do not run mass-radius metrics before schema and holdout protocol exist"
      - "do not claim habitability, biosignatures, planet prioritization, or discovery of a universal planet law"
      - "do not mix true mass, minimum mass, and model-derived values without explicit row-class flags"
      - "do not present compact/sub-Neptune matched-control survival as a canonical result, prediction, composition claim, habitability claim, or planet-law claim"
    actions:
      - id: exoplanet-null-baseline-family-audit
        label: "Run exoplanet null-baseline family audit"
        task_id: TASK-0483
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "compare CK17-style residuals against deterministic null baselines on the committed snapshot only"
          - "separate compact-radius, sub-Neptune, Jovian-radius, hot-Jupiter, true-mass, and minimum-mass axes when available"
          - "preserve control-sensitive and underpowered verdicts without composition, habitability, or new-law claims"
      - id: exoplanet-host-context-preflight
        label: "Preflight compact-radius host-context residual slice"
        task_id: TASK-0481
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "agent_runs/AGENT-RUN-0051 and docs/reviews/exoplanet-compact-radius-host-context-preflight.md report field coverage and missingness"
          - "no compact-radius host-context axis is benchmark-usable under the current coarse-bin floor"
          - "future host-context work must be framed as conditional/underpowered unless a new task declares a narrower missingness analysis"
      - id: exoplanet-control-aware-go-no-go
        label: "Review host-context preflight and decide whether any compact-radius residual follow-up remains warranted"
        task_id: TASK-0515
        mode: research
        status: review_ready
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "compare TASK-0481 host-context coverage against TASK-0483 null-baseline controls"
          - "either define a narrow conditional follow-up or demote compact-radius host context to negative/control memory"
          - "keep all wording benchmark-only with no composition, habitability, atmosphere, target-priority, claim, prediction, or knowledge promotion"
      - id: exoplanet-negative-control-memory
        label: "Preserve Exoplanet negative/control memory until a materially changed snapshot or coverage gate exists"
        task_id: null
        mode: research
        status: configured
        priority: high
        difficulty: medium
        recommended: true
        expected_outputs:
          - "do not repeat compact-radius residual, host-context coarse-bin, or mass-quartile localization pilots on the current pinned snapshot"
          - "keep the Exoplanet Research Factory adapter contract-only"
          - "reopen the campaign only after a reviewed later pinned snapshot or explicitly revised coverage gate"
      - id: exoplanet-compact-radius-mass-quartile-scout
        label: "Compact-radius mass-quartile scout is underpowered; use only as diagnostic memory"
        task_id: TASK-0480
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "verdict INCONCLUSIVE because quartile bins fall below the interpretation floor"
          - "upper-mass-half residual stress is directional diagnostic only, not a planet-physics conclusion"
      - id: exoplanet-second-snapshot-target-freeze
        label: "Second-snapshot target freeze landed"
        task_id: TASK-0482
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "freeze target set, row fields, checksums, and reveal conditions before any future second-snapshot data comparison"
      - id: exoplanet-external-reviewer-capsule
        label: "External-reviewer replication capsule landed"
        task_id: TASK-0484
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "scientist-readable replay commands and exact current benchmark metrics"
          - "scorecard remains BENCHMARK_SUMMARY_ONLY"
      - id: exoplanet-source-schema-scaffold
        label: "Scaffold exoplanet mass-radius source surface"
        task_id: TASK-0337
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "value-free exoplanet data README and source-manifest template"
          - "mass-radius row schema or schema sketch"
          - "holdout protocol and source-surface review"
          - "no live rows, metrics, prediction registry entries, or claims"
      - id: exoplanet-pscomppars-ingestion-plan
        label: "Prepare Exoplanet PSCompPars snapshot ingestion plan"
        task_id: TASK-0345
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "value-free retrieval and inclusion plan before any row fetch"
      - id: exoplanet-baseline-protocol
        label: "Define Exoplanet mass-radius baseline protocol"
        task_id: TASK-0346
        mode: research
        status: done
        priority: medium
        difficulty: medium
        recommended: false
        expected_outputs:
          - "baseline, metrics, holdout, and negative-control protocol without rows"
      - id: exoplanet-compact-subneptune-control
        label: "Compact/sub-Neptune matched-control audit landed (TASK-0427); follow-up is deeper compact-slice pilot or cross-tool Gate B replay"
        task_id: null
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "PR #609 (merged) added agent_runs/AGENT-RUN-0042 and docs/reviews/exoplanet-compact-subneptune-matched-control-audit.md"
          - "next action: open a cross-tool Gate B replay task on scripts/run_exoplanet_compact_subneptune_matched_control_audit.py or a deeper compact-slice (R<1.5 R_earth) pilot"
      - id: exoplanet-result-promotion-scorecard
        label: "Exoplanet failure-map result-promotion scorecard landed (TASK-0404); verdict BENCHMARK_SUMMARY_ONLY"
        task_id: null
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "docs/reviews/exoplanet-failure-map-result-promotion-scorecard.md + companion result_candidate_review.yaml record the BENCHMARK_SUMMARY_ONLY verdict and forbid claim-candidate framing"
          - "TASK-0427 confirmed as a strengthening prerequisite for compact/sub-Neptune wording, not a blocker"
      - id: exoplanet-second-snapshot-protocol
        label: "Second-snapshot no-live-fetch protocol landed (TASK-0393)"
        task_id: null
        mode: research
        status: done
        priority: medium
        difficulty: medium
        recommended: false
        expected_outputs:
          - "docs/exoplanet-second-snapshot-no-live-fetch-protocol.md freezes acquisition, checksums, no-peek, metrics, slices, and true-mass vs M sin i boundaries"
          - "TASK-0446/TASK-0447 are now landed context; future second-snapshot work still needs a maintainer-approved ingestion-only task"
      - id: exoplanet-compact-radius-independent-replay
        label: "Independent replay of compact-radius matched-control audit landed"
        task_id: null
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "TASK-0445 records an independent replay verdict for scripts/run_exoplanet_compact_subneptune_matched_control_audit.py"
          - "review before any public wording update; no claim promotion and benchmark-summary wording only"
      - id: exoplanet-normalized-checksum-gap
        label: "Close normalized PSCompPars snapshot checksum gap"
        task_id: TASK-0446
        mode: research
        status: done
        priority: medium
        difficulty: medium
        recommended: false
        expected_outputs:
          - "stable normalized checksum semantics or explicit blocker review"
          - "no live fetch and no row-value changes"
      - id: exoplanet-benchmark-evidence-card
        label: "Shareable exoplanet benchmark evidence card landed"
        task_id: null
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "TASK-0447 packages docs/results/exoplanet-compact-radius-benchmark-card.md"
          - "review before broad reuse; scorecard-approved public wording with limitations attached"

  - id: textbook-formula-audit
    title: "Textbook Formula Audit"
    rank: 5
    status: active_scaffold
    scientific_value: medium
    risk: low
    recommendation: "Use Textbook Formula Audit as a public-friendly planning surface: keep Stellar M-L as landed planning memory, then prepare Wien and Stefan-Boltzmann source/baseline plans before any metrics."
    why_now:
      - "TASK-0438 landed the campaign scaffold, profile, and candidate slate"
      - "famous formulas are easy for contributors to understand and share"
      - "each audit can be bounded by source, range, assumptions, verification gates, and OOD failure map"
      - "Stellar Mass-Luminosity on Gaia DR3 is the best first slice because it is recognizable, public-data-backed, and naturally range-limited"
      - "TASK-0492 and TASK-0493 keep the next famous-formula audits source/baseline-first instead of metric-first"
    forbidden:
      - "do not claim any textbook formula is universally right or wrong"
      - "do not run metrics before source, schema, baseline, holdout, and verification gates are declared"
      - "do not turn this campaign into broad symbolic-regression or formula-discovery work"
    actions:
      - id: textbook-stellar-ml-source-baseline-plan
        label: "Stellar Mass-Luminosity OOD source and baseline plan landed"
        task_id: TASK-0444
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "Gaia DR3 source/query plan without live fetch"
          - "row schema, baseline parameters, holdout policy, and verification gates"
          - "no audit metrics, result, claim, or discovery framing"
          - "docs/campaigns/textbook-formula-audit/stellar-mass-luminosity-ood-source-baseline-plan.md is landed planning memory"
      - id: textbook-wien-displacement-plan
        label: "Plan Textbook Formula Audit for Wien displacement"
        task_id: TASK-0492
        mode: research
        status: done
        priority: high
        difficulty: medium
        recommended: false
        expected_outputs:
          - "source/baseline/holdout plan without metrics or universal formula wording"
      - id: textbook-stefan-boltzmann-plan
        label: "Plan Textbook Formula Audit for Stefan-Boltzmann law"
        task_id: TASK-0493
        mode: research
        status: done
        recommended: false
        priority: high
        difficulty: medium
        expected_outputs:
          - "source/baseline/holdout plan without metrics or universal formula wording"

  - id: anharmonic-oscillator
    title: "Anharmonic Oscillator Period Benchmark"
    rank: 6
    status: methodology_validation
    scientific_value: high
    risk: low
    recommendation: "Use as the safest nonlinear benchmark for new autonomous hypothesis loops."
    why_now:
      - "nonlinear but controlled physics surface"
      - "perturbative baseline and numerical reference are available"
      - "low numerology risk compared with particle-physics formula search"
    forbidden:
      - "do not call approximation candidates exact or globally valid"
      - "do not skip harmonic-limit or holdout checks"
    actions:
      - id: anharmonic-replay-and-compare
        label: "Replay anharmonic benchmark and compare candidate limits"
        mode: research
        priority: high
        difficulty: medium
        expected_outputs:
          - "docs/reviews/anharmonic-replay-comparison.md"
      - id: anharmonic-autonomous-followup
        label: "Generate and filter new bounded anharmonic candidate hypotheses"
        mode: research
        priority: medium
        difficulty: high

  - id: dimensional-analysis-validator
    title: "Dimensional Analysis Validator"
    rank: 7
    status: quality_floor
    scientific_value: medium
    risk: low
    recommendation: "Use as a broad quality-floor track for formula sanity checks and adversarial edge cases."
    why_now:
      - "canonical MVP benchmark exists"
      - "new challenge items are easy to review"
      - "validator failures improve future research gates"
    forbidden:
      - "do not treat dimensional validity as physical truth"
      - "do not mix many unrelated challenge families in one PR"
    actions:
      - id: dimensional-boundary-cases
        label: "Generate hard dimensional boundary cases and validator limitations"
        mode: research
        priority: medium
        difficulty: medium
        expected_outputs:
          - "knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml"
          - "docs/notes/dimensional-validator-boundary-cases.md"

support_actions:
  - id: release-signoff
    label: "Review the release validation and public wording signoff artifact"
    task_id: null
    priority: high
  - id: private-agent-challenge-pack
    label: "Use the private agent challenge pack for invited-contributor onboarding"
    command: "Read docs/private-agent-challenge-pack.md"
    priority: medium
  - id: coverage-helper
    label: "Run the report-only coverage helper"
    command: "python3 scripts/apl_coverage_report.py"
    priority: medium

maintainer_actions:
  - id: review-pr
    label: "Review a PR with the deterministic maintainer review helper"
    command: "python3 scripts/apl_review_pr.py --pr <number> --task TASK-XXXX"
  - id: closeout-task
    label: "Prepare post-merge task closeout after maintainer merge"
    command: "python3 scripts/apl_closeout_task.py --task TASK-XXXX --pr <number> --apply --sync-board"
  - id: closeout-sweep
    label: "Find merged tasks that are ready for closeout"
    command: "python3 scripts/apl_closeout_sweep.py"


────────────────────────────────────────────────────────────────────────

# Mission Control (Current Phase)
<!-- source: docs/mission-control.md -->

# Mission Control

## What APL Is Trying To Do

Autonomous Physics Lab (APL) is verification-first scientific infrastructure.
Its job is to make physics hypotheses testable, falsifiable, reproducible, and
reviewable through deterministic code and version-controlled evidence.

APL is also an open agent network for science: many contributors can connect
their AI agents to shared scientific campaigns, and accepted outputs become
public scientific memory rather than isolated local chat artifacts.

<p align="center">
  <img src="figures/autonomous-physics-lab-workflow-concept.png" alt="Autonomous Physics Lab verification-first workflow for AI agents" width="100%">
</p>

## Agent First Entry Point

New contributors and coding agents should start from the mission script:

```bash
python3 scripts/apl_mission.py --output onboarding
```

Onboarding mode keeps the first run human-friendly: it explains the current
research mission, shows a few `READY` options, estimates effort, recommends
one path, and waits before editing files.

Explicit non-default lanes:

```bash
python3 scripts/apl_mission.py --mode support
python3 scripts/apl_mission.py --mode maintainer
```

This keeps maintainer review and closeout automation intact while making the
normal contributor path research-first.

For humans, the practical path is:

1. read the short project pitch in [README.md](../README.md);
2. run `python3 scripts/apl_mission.py --output onboarding`;
3. choose one `READY` task or ask the agent to explain the options;
4. review the PR evidence and limitations before merge.

Use [Connect Your Agent](./connect-your-agent.md) for the contribution loop and
[Use Your Agent](./use-your-agent.md) for agent prompt guidance.

## What APL Is Not Trying To Do

- It is not a chatbot for speculative physics claims.
- It is not treating numerically interesting fits as claim-level evidence.
- It is not presenting benchmark fits as complete explanations of particle masses.
- It is not presenting range-limited benchmarks as globally valid theories.

## Active Campaigns

APL currently organizes work around one flagship validation campaign, several
fresh-data source surfaces, and older benchmark/falsification surfaces that
still define the project's quality floor:

If you are new, start with the first four rows. They are the current
public-facing research surfaces. The later rows are still important, but they
are either quality-floor benchmarks or planning/watchlist surfaces.

| Campaign | Status | Why it exists | Best starting point |
| --- | --- | --- | --- |
| [Nuclear Mass Surface](./campaigns/nuclear-mass-surface.md) | Flagship validation campaign, sandbox-only candidates and prospective predictions | Test nuclear residual candidates with frozen baselines, robustness gates, prediction registry discipline, and future reveal-readiness | [nuclear-mass-pilot-summary.md](./results/nuclear-mass-pilot-summary.md) |
| [Quantum Size Effects](./campaigns/quantum-size-effects.md) | Source-readiness campaign | Build a direct-measurement row-level data surface before any baseline benchmark is allowed | [quantum-size-effects-campaign-plan.md](./notes/quantum-size-effects-campaign-plan.md) |
| [Atomic-Clock Residuals](./campaigns/atomic-clock-residuals.md) | Fresh-data source surface | Establish manifest, covariance, and source-admissibility discipline for high-precision clock data | [atomic-clock-source-candidates.md](./notes/atomic-clock-source-candidates.md) |
| [Exoplanet Mass-Radius Benchmark](./campaigns/exoplanet-mass-radius.md) | Emerging catalog-snapshot benchmark surface | Test whether mass-radius residual structure survives source, provenance, and holdout discipline | [exoplanet-mass-radius-baseline-protocol.md](./exoplanet-mass-radius-baseline-protocol.md) |
| [Fresh Physics Data Axes](./campaigns/fresh-physics-data-axes.md) | Planning and intake layer | Keep future campaigns focused on less-saturated source surfaces instead of formula mining old tables | [fresh-data-source-policy.md](./notes/fresh-data-source-policy.md) |
| [Anomaly Registry](./campaigns/anomaly-registry.md) | Planning scaffold, not a joint-fit campaign | Define admissible anomaly records and guardrails before any cross-anomaly modeling | [anomaly-registry-admissibility.md](./notes/anomaly-registry-admissibility.md) |
| [Pendulum Formula Falsification](./campaigns/pendulum-formula-falsification.md) | Active with canonical results | Stress-test approximation search against an exact reference with explicit failure modes | [pendulum-gauntlet-100-summary.md](./results/pendulum-gauntlet-100-summary.md) |
| [Particle Mass Relations](./campaigns/particle-mass-relations.md) | Active with scoped reproductions and falsifications | Test whether impressive mass relations survive disciplined, falsification-first handling | [koide-neutrino-falsification.md](./results/koide-neutrino-falsification.md) |
| [Dimensional Analysis Validator](./campaigns/dimensional-analysis-validator.md) | Active with canonical MVP result | Build a quality floor for future formula and benchmark work | [RUN-0006 report](../results/EXP-0006/RUN-0006/report.md) |
| [Thought-Experiment Consistency](./campaigns/thought-experiment-consistency.md) | Planning active, no canonical run yet | Extend APL into consistency checks that do not depend on curve fitting alone | [thought-experiment-consistency-suite.md](./notes/thought-experiment-consistency-suite.md) |

## Current Results

The clearest current repository-level results are:

1. [Pendulum Gauntlet 100](./results/pendulum-gauntlet-100-summary.md) —
   100 deterministic pendulum candidate formulas evaluated with stored
   leaderboard, diagnostics, and precision audit.
2. [Dimensional Analysis Validator MVP](../results/EXP-0006/RUN-0006/report.md)
   — a canonical 50-item validator benchmark with 49/50 agreement under
   explicit MVP limits.
3. [Koide charged-lepton reproduction](./results/koide-charged-lepton-reproduction.md)
   — a narrow dataset-based reproduction benchmark with uncertainty-aware
   comparison.
4. [Koide tau holdout](./results/koide-tau-holdout.md) — a historical
   holdout-style benchmark associated with `RESULT-0006`, kept narrow and
   explicitly non-explanatory.
5. [Koide neutrino falsification](./results/koide-neutrino-falsification.md)
   and [Negative Results Registry](./negative-results-registry.md) — clean
   falsification surfaces for the original neutrino extension and related
   particle-mass follow-ups.
6. [`RESULT-0010` quark cascade falsification](./notes/koide-quark-cascade.md)
   — the current quark-sector falsification result under stored dataset and
   scale assumptions.
7. [`RESULT-0011` particle-mass relation falsifier MVP](../results/EXP-0009/RUN-0001/report.md)
   — fixed-target Koide family-survival falsification with uncertainty,
   baseline, and complexity-penalty reporting.
8. [Anharmonic Oscillator Period Benchmark](./results/anharmonic-oscillator-summary.md)
   — `EXP-0011` nonlinear mechanics benchmark with perturbative and empirical
   baselines, kept range-limited.
9. [Nuclear Mass Baseline](./results/nuclear-mass-baseline-summary.md) and
   [Nuclear Mass Pilot Summary](./results/nuclear-mass-pilot-summary.md) —
   `EXP-0012` baseline evidence plus sandbox-only autonomous pilot and
   retrospective post-AME2020 checks. `AGENT-RUN-0007` is only an
   `INCONCLUSIVE` source-manifest guard, while `AGENT-RUN-0008` remains
   sandbox-only retrospective time-split evidence.

The nuclear prediction registry is a prospective forecast surface, not a
result surface: `PRED-0001` through `PRED-0068` are frozen entries awaiting
future maintainer-reviewed reveal data.

These results matter because they are reproducible and reviewable. They do not
authorize exact symbolic certainty, universal scope, or deeper physical
explanation by themselves.

## How Contributors Can Plug In

The current contributor workflow is branch-based and task-driven.

Operational entry points:

- [docs/open-agent-network.md](./open-agent-network.md) for the coordination
  model behind shared campaign work;
- [docs/current-missions.md](./current-missions.md) and
  `python3 scripts/apl_mission.py` for the Agent First mission menu;
- [docs/external-reviewer-replication-guide.md](./external-reviewer-replication-guide.md)
  for outside reviewers who want to replay or sanity-check the strongest
  evidence before learning the contributor workflow;
- [docs/agent-work-menu.md](./agent-work-menu.md) for a fast time-budgeted
  menu of safe, reviewable work (30 min / 1 h / 2 h);
- [docs/task-views/research.md](./task-views/research.md) for generated current-work navigation; use `git log` for task history;
- [tasks/microtasks/README.md](../tasks/microtasks/README.md) for campaign-specific scientific microtask queues;
- [docs/negative-results-registry.md](./negative-results-registry.md) for the
  current falsification index;
- [docs/agent-task-protocol.md](./agent-task-protocol.md) for branch, task,
  PR, validation, and task-state rules;
- [docs/agent-scientific-work-mode.md](./agent-scientific-work-mode.md) for
  spare-budget scientific work mode;
- [docs/scientific-micro-task-protocol.md](./scientific-micro-task-protocol.md)
  for queue and batching rules;
- [tasks/proposals/README.md](../tasks/proposals/README.md) for the
  proposal-first workflow when no canonical task fits;
- [docs/private-contributor-pilot.md](./private-contributor-pilot.md) for the
  invited private contributor flow;
- the `Sync Active Board` post-merge GitHub Action keeps the active board
  and `docs/task-views/*.md` aligned with task YAML files on `main`;
- `python3 -m physics_lab.cli sync-active-board .` remains available for
  maintainer dry-runs and explicit board-sync PRs;
- maintainer review and closeout tooling for review bundles and handoff.

Low-risk contribution patterns right now:

- improve status, roadmap, onboarding, or campaign documentation;
- tighten wording, diagnostics, or visual summaries around existing results;
- complete one small batch from a single scientific microtask queue;
- work on planning or validation tasks that do not churn canonical result
  artifacts.

## What Not To Claim

- Do not describe APL as having finalized physics.
- Do not describe the repository as having produced a validated physical result.
- Do not call pendulum approximations exact or globally valid.
- Do not treat charged-lepton or tau-holdout benchmarks as explanations of
  particle masses.
- Do not turn neutrino or quark falsifications into a blanket claim about all
  possible Koide variants.
- Do not turn the particle-mass falsifier MVP into a blanket claim about all
  possible mass-relation formulas.
- Do not present `EXP-0010` muon g-2 output as a validated, explanatory,
  or flagship public result.
- Do not describe planning-only campaigns as implemented benchmark systems.

## Read Order For New Contributors

1. Run `python3 scripts/apl_mission.py --output onboarding` for the current research-first mission.
2. [README.md](../README.md)
3. [docs/current-missions.md](./current-missions.md)
4. [docs/mission-control.md](./mission-control.md)
5. [docs/campaigns/README.md](./campaigns/README.md)
6. [docs/status.md](./status.md)
7. [docs/task-views/research.md](./task-views/research.md)
8. [docs/agent-task-protocol.md](./agent-task-protocol.md)


────────────────────────────────────────────────────────────────────────

# Agent Task Protocol
<!-- source: docs/agent-task-protocol.md -->

# Agent Task Protocol

This document defines the canonical task-execution protocol for Codex, Claude
Code, humans, and other agents working in this repository.

Do not invent branch names, commit formats, PR titles, or task-state
transitions locally. Use this document.

## Read Order

Before starting a task, read:

1. [../AGENTS.md](../AGENTS.md)
2. [./agent-task-protocol.md](./agent-task-protocol.md)
3. [./task-proposal-protocol.md](./task-proposal-protocol.md) when proposing a new task idea
4. the relevant generated lane view under
   [./task-views/research.md](./task-views/research.md),
   [./task-views/support.md](./task-views/support.md), or
   [./task-views/release.md](./task-views/release.md)
5. [./task-views/research.md](./task-views/research.md) for the generated current-work navigation
6. the matching `tasks/TASK-XXXX-*.yaml` file when working on a canonical task
7. [./strategy.md](./strategy.md)

`docs/task-views/*.md` are the generated current-work navigation surfaces, and
`git log` is the task history. (The legacy `tasks/ACTIVE.md` full board was
retired — see TASK-0470/TASK-0473.)

Use [./agent-operating-model.md](./agent-operating-model.md) and
[./contributing-workflow.md](./contributing-workflow.md) for supporting
context, not as competing protocol definitions.

## Pick a Task

1. Start with one atomic task that is already `READY`.
2. Do not start a second task unless a human explicitly asks for it or the work
   is clearly independent.
3. Do not start `REVIEW_READY`, `BLOCKED`, `SUPERSEDED`, or `REJECTED` tasks
   unless a human explicitly redirects you.
4. If no existing task fits, ask for or propose a new task before doing
   substantial work.
5. Before substantial work on the chosen task, declare a claim per
   [./agent-task-claiming.md](./agent-task-claiming.md). The lightweight,
   GitHub-native claiming ledger prevents two agents from implementing the same
   `TASK-XXXX` or writing the same `agent_runs/`, `results/`, or
   `docs/reviews/` path.

When an executor agent reports "available tasks", it should list only
`READY` tasks. `REVIEW_READY` tasks are not available executor work; they belong
to maintainer review, merge decisions, or post-merge closeout. Mention
`REVIEW_READY` items only when the maintainer explicitly asks for review,
closeout, or queue triage.

For guided onboarding, use:

```bash
python3 scripts/apl_mission.py --output onboarding
```

The onboarding path dynamically tries to exclude `READY` tasks that already
have an open claim, an open PR, or a merged PR pending local closeout. This is
stdout-only coordination state; do not commit a generated availability cache.
When GitHub CLI or network metadata is unavailable, onboarding reports that it
is showing local registry-only options. Agents must then perform the manual
pre-claim search from `docs/agent-task-claiming.md` before starting work.

For an explicit live check from another output mode, add
`--github-availability auto` or use `--github-availability required` when a
registry-only fallback should fail clearly. If an approved Codex sandbox sets
the known loopback blocker proxy, add `--ignore-suspicious-proxy`; this clears
only blocker-valued proxy variables for the child GitHub CLI process.

## Task Proposals

If no existing `READY` task fits, do not guess the next canonical task number
during parallel work.

## Preserve External-Agent Signals

External agents should not leave actionable discoveries only in chat output,
PR prose, or private reasoning. When an agent notices a repository bug,
validation bottleneck, cross-platform failure, protocol ambiguity, optimization
opportunity, source lead, blocker, or scientific idea that is worth preserving,
it must route that signal into a durable coordination surface before handoff:

- create a `tasks/proposals/*.yaml` artifact when the idea may become future
  repository work but does not yet have a maintainer-assigned canonical task id;
- create the appropriate research proposal artifact when the signal is a new
  hypothesis, benchmark idea, source path, dataset lane, or scientific control
  rather than immediate maintenance work;
- open or reference a GitHub issue when the agent cannot safely edit the
  repository, when the signal is primarily operational coordination, or when a
  lightweight external report is the right first step;
- create a `TASK-QUEUE` item only when the maintainer explicitly asked for
  canonical future tasks.

Do not formalize every speculative thought. Formalize signals that are
actionable, likely to recur, likely to block another agent, or scientifically
useful enough that losing them would slow the project. If a signal is
intentionally advisory-only, say that explicitly in the handoff.

Default rule:

- create a proposal under `tasks/proposals/`
- let the maintainer accept it before assigning `TASK-XXXX`

Proposal file format:

`tasks/proposals/YYYYMMDD-<contributor-id>-<short-slug>.yaml`

Proposal branch format:

`agent/<contributor-id>/<agent-id>/propose-task-<short-slug>`

Proposal PR title format:

`TASK-PROPOSAL: <short title>`

Default proposal PR scope:

- one or more `tasks/proposals/*.yaml` files in a proposal-only PR

Use a multi-proposal PR when the ideas are tightly coupled, come from the same
salvage pass, or when the maintainer explicitly asks for a batch. Split the
PR when the proposals are unrelated or the batch stops being lightweight.

Use [./task-proposal-protocol.md](./task-proposal-protocol.md) and
[../tasks/proposals/TASK-PROPOSAL-TEMPLATE.yaml](../tasks/proposals/TASK-PROPOSAL-TEMPLATE.yaml).

Only the maintainer may assign canonical ids directly unless a maintainer-run
task-admin or review agent is explicitly told to do so.

When the maintainer explicitly asks an agent to create canonical `TASK-XXXX`
files for future work, use the `TASK-QUEUE` lane instead of creating a separate
"task to create tasks." The newly queued executable tasks should usually remain
`READY`, `BLOCKED`, or `PROPOSED`; they are not treated as completed by the
queue PR.

Task-queue branch format:

`agent/<contributor-id>/<agent-id>/task-queue-<short-slug>`

Task-queue PR title format:

`TASK-QUEUE: <short summary>`

Task-queue PR scope:

- new or updated canonical `tasks/TASK-XXXX-*.yaml` files;
- synced generated task navigation (`docs/task-views/*.md`);
- optional protocol or planning docs needed to explain the queue.

Do not use `TASK-QUEUE` for normal contributor ideas without maintainer
approval; those still go through `TASK-PROPOSAL`. Do not use `TASK-QUEUE` to
implement the newly queued task's accepted outputs in the same PR.

If rescuing useful ideas from a stale or superseded PR:

- create fresh proposal file(s) under `tasks/proposals/`;
- start from a clean `propose-task-...` branch immediately;
- do not reuse a generic docs/task branch just because it already exists;
- open a clean replacement `TASK-PROPOSAL` PR and then close the stale PR;
- a salvage batch is allowed when the rescued ideas are closely related and
  the replacement PR stays proposal-only.

## Scientific Microtask Queues

Default execution still starts from canonical `TASK-XXXX` items.

Exception:

- when a maintainer explicitly asks for spare token or time budget work;
- when the maintainer invokes agent scientific work mode;
- when a narrow campaign-facing contribution is better handled as a small queue
  item than as a brand-new canonical task.

In those cases, agents may work from `tasks/microtasks/*.yaml` and the rules in
[./scientific-micro-task-protocol.md](./scientific-micro-task-protocol.md).

Microtask rules:

- before selecting queue work, run
  `python3 scripts/apl_microtask_pr_helper.py status --queue-id <queue-id>` and
  pick from the effective `available` list, not from queue YAML alone;
- prefer one campaign queue at a time;
- one PR may complete a small batch of related microtasks from the same
  campaign;
- do not mix many campaigns in one microtask PR unless the maintainer asks;
- do not create many new canonical `TASK-XXXX` files just to represent tiny
  queue items;
- do not promote claims from microtask outputs;
- report limitations for every completed item;
- if uncertain, mark the output `REVIEW_NEEDED`.

Microtask branch formats:

- single item:
  `agent/<contributor-id>/<agent-id>/microtask-<microtask-id>-<short-slug>`
- small same-queue batch:
  `agent/<contributor-id>/<agent-id>/microtask-batch-<queue-id>--<short-slug>`

Microtask PR title format:

`microtask(<queue-id>): <short description>`

Examples:
- `microtask(DAV-001): add DA-017 gravitational acceleration to challenge set`
- `microtask(PFF-002): classify near-separatrix failure for gauntlet candidate`
- `microtask(PMR-001): audit electron mass dataset entry against PDG source`
- `microtask(dimensional-analysis-validator): add DAV-003 DAV-004 DAV-008 challenge entries`

Microtask PRs do not require a canonical `TASK-XXXX` file. They use the
`fast review` lane in `docs/maintainer-review-agent.md`.
Use the repository PR template, delete unused sections, and fill in the
microtask queue metadata instead of leaving canonical task placeholders in the
PR body.

Use [./agent-scientific-work-mode.md](./agent-scientific-work-mode.md) for the
practical operating pattern.

## PR Helper Map

APL has several PR shapes. Use the helper that matches the PR kind instead of
forcing every PR through the canonical task helper.

| PR kind | Use this helper | Branch shape |
| --- | --- | --- |
| Canonical `TASK-XXXX` implementation | `python3 scripts/apl_task_pr_helper.py prepare-current ...` | `agent/<contributor-id>/<agent-id>/task-XXXX-<short-slug>` |
| Task proposal | `python3 scripts/apl_proposal_pr_helper.py scaffold/preflight/create ...` | `agent/<contributor-id>/<agent-id>/propose-task-<short-slug>` |
| Microtask | `python3 scripts/apl_microtask_pr_helper.py status/scaffold/preflight ...` | `agent/<contributor-id>/<agent-id>/microtask-...` |
| Task closeout | `python3 scripts/apl_closeout_pr_helper.py scaffold/preflight ...` | `agent/<contributor-id>/<agent-id>/closeout-<short-slug>` |
| Task queue | Use the repository PR template and canonical `TASK-QUEUE` branch/title rules; do not mark newly queued tasks `REVIEW_READY` or implement them in the same PR | `agent/<contributor-id>/<agent-id>/task-queue-<short-slug>` |

The helpers are mechanical guardrails, not scientific reviewers. They format and
preflight branches, titles, bodies, metadata, and obvious PR-shape mistakes.
They do not decide whether a scientific result is true, whether a task should be
accepted, or whether a PR should merge.

For closeout behavior, task YAML may optionally set `closeout: auto` or
`closeout: review`. Omitted is equivalent to `auto`; `review` opts the task out
of safe auto-closeout and keeps it on the manual maintainer closeout path.
`TASK-CLOSEOUT` is separate: it is the PR kind marker for closeout PR titles and
metadata, not a task id and not a value for the task YAML field.

## Canonical Task PR Helper

Before opening a canonical task PR, prefer the Python helper over ad-hoc
`gh pr create` commands. The helper is cross-platform and catches the common
publication mistakes before GitHub review: wrong branch shape, mismatched task
id, missing PR template sections, missing metadata, and missing strict
validation mention.

After committing task work on the canonical task branch, run:

```bash
python3 scripts/apl_task_pr_helper.py prepare-current \
  --task-id TASK-XXXX \
  --contributor-id <contributor-id> \
  --github-username <github-username> \
  --agent-id <codex|claude|other-agent-id> \
  --human-reviewer <maintainer-github-username> \
  --summary "What changed, in narrow verification-first terms." \
  --body-file .apl-pr-body.md
```

If `prepare-current` reports errors, fix them before creating the PR. In
particular, do not open a PR from a `feature/...` or other non-canonical branch
for canonical task work. Use the printed expected branch as the branch target.

Then create the draft PR using the helper-generated body:

```bash
python3 scripts/apl_task_pr_helper.py create \
  --branch agent/<contributor-id>/<agent-id>/task-XXXX-<short-slug> \
  --title "TASK-XXXX: <task title>" \
  --body-file .apl-pr-body.md
```

The older `scaffold`, `preflight`, `create`, and `ready` subcommands remain
available. `prepare-current` is the recommended final pre-publication check
because it uses the actual current branch and current diff.

## Task Status Protocol

Use these execution states:

- `READY`: approved, scoped, and available to start.
- `IN_PROGRESS`: actively being worked on by one contributor or agent.
- `REVIEW_READY`: implementation is complete, validation ran, and maintainer
  review is required.
- `DONE`: maintainer-reviewed and accepted. Agents must not mark their own task
  `DONE`.
- `BLOCKED`: work cannot continue until a dependency, decision, or external
  action is resolved. State the blocker clearly.
- `SUPERSEDED`: the task was valid when created, but a newer task,
  architecture, or reviewed workflow replaced it. Do not execute it; follow the
  replacement task or create a fresh scoped task if the old idea becomes useful
  again.
- `REJECTED`: the task should not proceed in its current form.

Rules:

- An agent may move `READY -> IN_PROGRESS`.
- An agent may move `IN_PROGRESS -> REVIEW_READY`.
- A task PR may update its own `tasks/TASK-XXXX-*.yaml` lifecycle status and
  synchronize generated task navigation when that status changes.
- Do not change unrelated task statuses or generated task navigation except
  when the maintainer explicitly requested queue triage, closeout, unblock, or
  stale-task cleanup.
- Only a maintainer should move `REVIEW_READY -> DONE`.
- A maintainer may use a maintainer-run review agent to assist review and
  closeout, but the agent output is advisory rather than autonomous.
- If blocked, set `BLOCKED` and explain why in the task file, board, or PR.
- If old work is replaced by a better lane, set `SUPERSEDED` rather than
  leaving it in `BLOCKED` or marking it `REJECTED`.
- `PROPOSED` may still appear in backlog planning, but it is not an executable
  task state for active task execution.

## Branch Naming

Use exactly this format:

`agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug>`

Examples:

- `agent/roman/codex/task-0011-numerical-audit`
- `agent/roman/claude/task-0017-dimensional-challenge`
- `agent/ihor/human/task-0032-public-result-package`

Field meanings:

- `contributor-id`: the human responsible for the PR and review loop.
- `agent-id`: the execution mode or tool, such as `codex`, `claude`,
  `cursor`, `human`, or `other`.

Rules:

- lowercase only
- no spaces
- no underscores
- include the task number
- keep the slug short
- do not invent fantasy agent identities as the canonical id

Historical note:

- older private-pilot branches may still use `agent/<agent-id>/...`
- do not rename old branches or rewrite history just to match the new format

For task proposals, use:

`agent/<contributor-id>/<agent-id>/propose-task-<short-slug>`

## Branch-First Rule

Before making any repository change for a task:

1. confirm the current task is `READY`;
2. create the task branch using the canonical naming format;
3. switch to that branch;
4. only then edit files, run task-related generators, or stage changes.

Agents must not implement task work on `main`.

If an agent notices that work started on `main` by mistake, it should stop and
move the current worktree state onto a correctly named task branch before
continuing.

## Commit Message Format

Use exactly this format:

`<type>(task-<task-number>): <short summary>`

Examples:

- `feat(task-0011): add numerical precision audit`
- `docs(task-0014): plan thought experiment suite`
- `fix(task-0018): support planning-only task inputs`
- `test(task-0017): add dimensional challenge tests`

Allowed commit types:

- `feat`
- `fix`
- `refactor`
- `docs`
- `test`
- `chore`

Keep commits narrow. Do not mix unrelated tasks in one commit.

## Commit Permission

Agents may commit only when explicitly instructed.

For this repository, maintainer wording such as "prepare a PR", "run the task
through PR", "execute the selected task autonomously", or "full task lifecycle"
counts as explicit current-turn approval to commit on the selected task branch,
push that branch, and open a draft PR. This approval does not allow pushing
`main`, force-pushing, merging, tagging, or touching unrelated branches.

A commit means the agent believes the task is ready for maintainer review.

After committing, the task status should be `REVIEW_READY`, not `DONE`.

`DONE` is set only by the maintainer after review and merge.

## Pull Request Title Format

Use exactly this format:

`TASK-0011: Audit numerical precision vs model residual`

The PR must stay within one task scope and make the linked task easy to review.

For task proposals, use:

`TASK-PROPOSAL: <short title>`

## Open a Pull Request

"Open a PR" means creating the GitHub pull request and returning its URL when
the agent has GitHub access. It does not mean only preparing a branch, commit,
title, body, or pushed branch. When a full PR lifecycle was requested, the
final response must include either a PR URL or exact maintainer-run commands to
publish the prepared branch and PR from a local console.

Before starting implementation for a full PR lifecycle request, optionally
check whether the environment can open a PR:

```bash
python3 scripts/apl_pr_capability_check.py
```

This check is advisory. It must never be used as a pre-edit gate. Missing
`gh`, missing GitHub auth, restricted network access, or a sandbox that cannot
push should not block local task execution or cause the agent to ask the user
whether to continue before implementation. Create the task branch first, do
the local work, run validation, and commit only after the intended files are
ready for maintainer review.

At the end, the agent should try to publish through the best available
agent-driven path before falling back to manual commands:

1. Use repository helpers such as `scripts/apl_task_pr_helper.py` where
   possible.
2. Use an available GitHub/MCP connector or GitHub CLI when configured.
3. If `git commit`, `git push`, `gh pr create`, `gh pr edit`, `gh pr view`,
   `gh pr ready`, or `python3 scripts/apl_review_pr.py` is blocked by sandbox
   permissions or missing command approval, request the needed permission or
   escalation for that specific command.
4. Provide manual maintainer-run commands only after the available tool path
   and any appropriate permission request cannot complete the publication.

Fallback commands to give the maintainer when direct publication is not
available:

```bash
git push origin agent/<contributor-id>/<agent-id>/task-XXXX-<short-slug>
gh pr create --draft --base main --head agent/<contributor-id>/<agent-id>/task-XXXX-<short-slug> --title "TASK-XXXX: <short title>" --body-file /path/to/apl-pr-body.md
python3 scripts/apl_review_pr.py --pr <number>
gh pr ready <number>
```

The agent should also offer to help the maintainer set up access, for example
by suggesting `gh auth login` or a `GH_TOKEN`/`GITHUB_TOKEN`, but setup is not
required for completing local validation work.

If Python, Git, GitHub CLI, proxy settings, or Windows shell startup look
inconsistent, run the read-only agent doctor before adding local workaround
steps:

```bash
python3 scripts/apl_agent_doctor.py
```

The doctor reports environment diagnostics only. It does not install packages,
mutate global `PATH`, store credentials, relax validation, or replace the task
protocol. Use it to identify the next safe troubleshooting step, then continue
with the standard PR helper flow.

Use the repository PR helpers instead of calling bare `gh` in Codex sessions.
Codex may omit Homebrew paths from `PATH`; the helpers search common GitHub CLI
locations such as `/opt/homebrew/bin/gh` and `/usr/local/bin/gh`.

Task PRs should start as drafts while validation, CI, and PR-number review are
still in progress. After GitHub CI is green and
`python3 scripts/apl_review_pr.py --pr <number>` returns `MERGE_OK`, mark the
PR ready for review. If the agent cannot update GitHub directly, provide the
maintainer with `gh pr ready <number>`. Keep the PR as draft if any validation,
CI, or review blocker remains.

After implementation and validation:

1. push the task branch only when a human or workflow expects a PR;
2. open one PR for one task branch;
3. use the required PR title format;
4. complete the repository PR template before creating the PR;
5. include limitations, validation results, and artifact-impact notes;
6. move the task to `REVIEW_READY`.

Do not open task PRs with a short ad hoc `--body` such as only `Summary` and
`Validation`. Prepare a body file from `.github/pull_request_template.md`, fill
the required sections, and use that body file when creating the PR:

```bash
python3 scripts/apl_task_pr_helper.py scaffold \
  --task-id TASK-XXXX \
  --contributor-id <contributor-id> \
  --github-username <github-username> \
  --agent-id <agent-id> \
  --human-reviewer <reviewer> \
  --slug <short-slug> \
  --description "<short title>" \
  --summary "<verification-first summary>" \
  --body-file /tmp/apl-pr-body.md
python3 scripts/apl_task_pr_helper.py preflight \
  --branch "agent/<contributor-id>/<agent-id>/task-XXXX-<short-slug>" \
  --title "TASK-XXXX: <short title>" \
  --body-file /tmp/apl-pr-body.md
python3 scripts/apl_task_pr_helper.py create \
  --branch "agent/<contributor-id>/<agent-id>/task-XXXX-<short-slug>" \
  --title "TASK-XXXX: <short title>" \
  --body-file /tmp/apl-pr-body.md
```

After the PR exists, run the PR-number review, not only branch preflight:

```bash
python3 scripts/apl_review_pr.py --pr <number>
```

After CI is green and the PR-number review returns `MERGE_OK`, mark the draft
ready:

```bash
python3 scripts/apl_task_pr_helper.py ready --pr <number>
```

For the bounded finish step, agents may use the repository finish gate helper
instead of repeating the review, CI, and ready commands by hand:

```bash
python3 scripts/apl_pr_finish_gate.py --pr <number>
```

The helper first runs `python3 scripts/apl_review_pr.py --pr <number>`, then
checks GitHub PR checks through `gh pr checks --json`, and only then calls
`gh pr ready <number>`. It leaves the PR draft if the review verdict is not
`MERGE_OK`, if checks are pending or failing, or if GitHub status cannot be
loaded. For a non-mutating preflight, use:

```bash
python3 scripts/apl_pr_finish_gate.py --pr <number> --dry-run
```

When `scripts/apl_agent_doctor.py` reports the known loopback blocker proxy
(`127.0.0.1:9` or `localhost:9`) and network access is allowed, add
`--ignore-suspicious-proxy` to `apl_task_pr_helper.py create` or `ready`.
The flag is opt-in, applies only to the child `gh` command, and does not remove
legitimate proxy configuration or mutate the parent shell.

## Pull Request Requirements

Every PR should include:

- Task ID
- task file path
- branch name
- contributor id
- GitHub username
- agent tool
- model/version if known
- human reviewer
- summary
- changed files
- validation commands
- scientific claim impact
- result artifact impact
- maintainer review notes

Use the repository PR template.

## Required Validation

Run these commands before handoff:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
git diff --exit-code
```

Use `--output-dir` for routine example runs so committed canonical artifacts do
not change accidentally.

`python3 -m pytest` runs in parallel by default via `pytest-xdist` (part of the
dev extras: `pip install -e ".[dev]"`), matching CI on Windows, macOS, and
Linux. For a faster cross-platform inner loop use
`python3 scripts/validate_fast.py` (lint, strict repository validation, then
non-`full_repo` tests with a slowest-ten timing report). Add
`-n0` to force a serial run when debugging a single test. For a narrow task
PR, start with the validation commands declared in its task YAML and use
`python3 scripts/apl_task_validation_plan.py --task TASK-XXXX` for advisory
diff-aware guidance. If a Windows sandbox blocks parallel pytest, run
`python3 scripts/apl_agent_doctor.py --probe-pytest-runtime --no-gh-auth-check`.
Do not automatically replace a narrow PR's validation with a serial full-suite
run: use targeted `-n0` debugging and let CI provide broad cross-platform
coverage.

Treat test priority as a staged-lane concern. Run cheap deterministic gates
before the parallel pytest layer and keep slow `full_repo` smoke tests at the
end. Do not introduce dependencies between individual tests merely to control
their xdist scheduling order. Put tests with measured xdist resource or path
sensitivity in the same `xdist_group`, which keeps them on one worker while
unrelated tests continue in parallel.

Before opening a PR, agents may optionally generate a review bundle for the
maintainer. This is no longer a required step and its absence is not flagged by
the PR preflight:

```bash
python3 scripts/apl_review_bundle.py
```

This produces `_snapshots/review_<branch>_<timestamp>.md` with the full diff
vs `main`, commit list, and changed-file summary.

For microtask PRs, contributors and their agents may also use
`python3 scripts/apl_microtask_pr_helper.py` to scaffold canonical branch/title
metadata and run a local preflight check before maintainer review.

For canonical task PRs, use `python3 scripts/apl_task_pr_helper.py` to scaffold
and preflight the template-based PR body before creating the draft PR.

For task proposal PRs, the lighter validation path from
[./task-proposal-protocol.md](./task-proposal-protocol.md) is acceptable.

When a task creates concrete artifact paths, replace any placeholder validation
commands in that task's YAML before moving the task to `REVIEW_READY`.
Examples include replacing `<new-result-path>` with the exact
`results/EXP-XXXX/RUN-XXXX/result.yaml` path or replacing `<queue-id>` with the
specific queue id used by the PR. Placeholders may remain only in task
templates, future `READY` tasks, or proposal files that are not being handed off
as completed work.

## Cross-Platform Compatibility

APL must run on Linux, macOS, and Windows so third-party agents can contribute,
even though CI runs on Linux only. When a task touches code or tooling, keep it
portable:

- build paths with `pathlib.Path` / `os.path.join`, never hardcoded `/`;
- use `tempfile` for temporary paths, never hardcoded `/tmp`;
- use `Path.home()` (not `HOME`) and `sys.executable` (not literal `python3`);
- call subprocesses with an argument list and `shell=False`; avoid shell-only
  features;
- always pass `encoding="utf-8"` to file reads and writes;
- do not add a `.sh` script on the task-execution or review critical path
  without a cross-platform (Python) equivalent — and do not add a `.sh` script
  that is merely a thin wrapper around one or two commands.

See [./cross-platform-compatibility.md](./cross-platform-compatibility.md) for
the full standard and the audit of existing shell scripts.

## End-Of-Task Output Routing

At the end of any research, validation, benchmark, source-curation, prediction,
or claim-facing task, add a short output-routing summary before handoff. This
summary tells the maintainer what the task produced and where it belongs in
the scientific memory.

Use [./result-promotion-protocol.md](./result-promotion-protocol.md) as the
canonical routing rule. The summary should state:

- task verdict: `VALID`, `VALID_IN_RANGE`, `PARTIALLY_VALID`, `INCONCLUSIVE`,
  `OVERFITTED`, `FALSIFIED`, or `not_applicable`;
- canonical destination: sandbox-only `agent_runs/`, `results/`, `prediction_registry/`,
  `claims/`, `knowledge/`, source artifact, review note, or task proposal;
- review tier when applicable: `AGENT_PUBLISHED`, `AGENT_VALIDATED`,
  `MAINTAINER_REVIEWED`, `EXTERNAL_REPLICATED`, `LEGACY_UNTIERED`, or `none`;
- Gate status when applicable: Gate A pass/fail/not attempted, Gate B
  pass/fail/not attempted;
- claim impact: no claim change, new `DRAFT` claim only, evidence reference
  only, or maintainer-only status transition requested;
- knowledge impact: no knowledge change, task proposal only, or maintainer-only
  knowledge entry requested;
- limitations and blockers, especially missing tooling, source provenance, or
  validation gaps.

If the task produced only sandbox evidence, say so explicitly. Do not turn a
sandbox note into a prose claim. If Gate A or Gate B tooling is missing or
fails, report the publication as blocked instead of bypassing the gate with
unsupported wording.

Agents may create `AGENT_PUBLISHED` or `AGENT_VALIDATED` artifacts only when
the task scope and [./result-promotion-protocol.md](./result-promotion-protocol.md)
allow it. Claim status transitions remain maintainer-only in Phase 1. Do not
auto-merge PRs that publish tiered artifacts.

## Maintainer Review And Closeout

Maintainers may use [./maintainer-review-agent.md](./maintainer-review-agent.md)
for two explicit modes:

1. pre-merge review for an open PR;
2. post-merge closeout for moving a merged task to `DONE`.

The maintainer review agent may:

- verify PR metadata, scope, validation, accepted outputs, and review bundle
  integrity;
- surface repository-safety and security-sensitive changes for maintainer review;
- return `MERGE_OK`, `NEEDS_CHANGES`, or `BLOCKED`;
- help close a merged task by updating the task file and synchronizing
  generated task navigation
  ([./task-views/research.md](./task-views/research.md),
  [./task-views/support.md](./task-views/support.md), and
  [./task-views/release.md](./task-views/release.md)).

The maintainer review agent must not:

- merge PRs;
- promote claims automatically;
- rewrite scientific verdicts;
- rewrite result artifacts unless the task explicitly required it and the
  maintainer approved that scope.

## Task Execution Flow

1. Read the files listed above.
2. Confirm the task is `READY` and atomic.
3. Create and switch to the branch using the required naming format before any
   repository edits.
4. Set the task status to `IN_PROGRESS` in the task file.
5. Do not hand-edit the generated `docs/task-views/*.md` for routine task
   status transitions. Task YAML is the canonical source of truth; the views
   are a maintainer-synchronized snapshot regenerated automatically by the
   post-merge `Sync Active Board` GitHub Action after each merge to `main`.
6. Do not commit regenerated versions of `docs/task-views/*.md` from a task PR.
   They are generated from canonical task YAML files and the post-merge action
   keeps them in sync on `main`.
7. Agents may run `python3 -m physics_lab.cli sync-active-board .` locally
   for visual confirmation of how their task YAML change will render, but
   should **not** stage or commit the resulting regeneration on a task PR
   branch. `validate-repo --strict --fail-on-warnings` reports a stale
   `docs/task-views/*.md` as `INFO` (not `ERROR`) by
   default, so a non-regenerated branch passes strict validation. Set
   `APL_ENFORCE_BOARD_STALENESS=1` only when explicitly auditing the
   action's output. If strict validation ever reports generated board
   staleness as an error during a routine task PR, treat that as a validation
   configuration issue to report or fix, not as permission to commit generated
   navigation churn. If a local sync or validation comparison leaves generated
   board files dirty, do not stage them; remove those generated diffs before
   creating the review bundle.
8. Do not add committed static files whose primary consumer is another agent
   and whose content changes with ordinary task churn. For agent routing,
   queue filtering, campaign-lane mapping, conflict scans, or current-state
   summaries, prefer scripts/CLI output, snapshot sections, or CI artifacts.
   Commit generated output only when it is canonical source or explicit
   human-facing navigation with a defined regeneration owner. See
   [static-agent-facing-generated-index-postmortem.md](./reviews/static-agent-facing-generated-index-postmortem.md).
9. Make the smallest reproducible change that satisfies the task.
10. Run the required validation commands.
11. Set the task to `REVIEW_READY` when implementation and validation are
    done.
12. Leave clear maintainer review notes and limitations.

After merge, maintainer closeout may also:

13. set the task to `DONE`;
14. let the post-merge `Sync Active Board` GitHub Action regenerate
    the generated task views
    ([./task-views/research.md](./task-views/research.md),
    [./task-views/support.md](./task-views/support.md), and
    [./task-views/release.md](./task-views/release.md)). The action runs on
    every push to `main` that touches `tasks/**` or `missions/current.yaml`
    and pushes a `chore(board-sync): … [skip-board-sync]` commit only when a
    regeneration diff exists. Maintainers may still run
    `python3 -m physics_lab.cli sync-active-board .` by hand in a dedicated
    board-sync PR when the action is disabled or needs a manual audit;
15. add a dry-run note when the merged PR belongs to a contributor pilot.

## AI Agent Attribution

AI agents (Claude Code, Codex, Cursor, or any LLM tool) are execution tools,
not git co-authors. Record them in PR metadata, not in git commit history.

Rules:

- Do **not** add `Co-Authored-By` trailers for AI agents in commit messages.
- Record agent involvement in the **Agent / Contributor Metadata** section of
  the PR description (see PR template).
- The human contributor remains the git author and the responsible reviewer.
- Git history must reflect only human authors.
- Agents must not invent their own identity format for branches, PRs, or
  attribution fields.

## Scientific Claim Restrictions

- Do not promote claims automatically.
- Do not strengthen claim status without maintainer review and evidence.
- Do not present a numerical fit as a discovery without deterministic support.
- Keep range limits, assumptions, and failure modes explicit.
- Do not change committed `results/` artifacts unless the task explicitly
  requires it and the PR explains why.

## Forbidden Actions

- do not work directly on `main`
- do not begin task implementation before creating and switching to a task branch
- do not invent local branch, commit, or PR formats
- do not mark your own task `DONE`
- do not use a review agent to bypass maintainer merge or claim-review authority
- do not start unrelated tasks in the same branch or PR
- do not add dashboard, web API, database, ingestion, or runtime infrastructure work
- do not make the repository public
- do not promote claims or knowledge without review
- do not silently rewrite canonical scientific artifacts
- do not introduce platform-specific code (bash-only critical-path scripts,
  hardcoded `/tmp`, hardcoded `python3`, hardcoded `/` paths, or `HOME` reads)
  without a cross-platform equivalent; see
  [./cross-platform-compatibility.md](./cross-platform-compatibility.md)

## Standard Prompt

Use this prompt when assigning work to an agent:

```text
Execute TASK-0011 according to AGENTS.md and docs/agent-task-protocol.md.
Use contributor id: roman.
Use agent id: codex.
Create the task branch before making any repository changes.
Do not start any other task.
```


────────────────────────────────────────────────────────────────────────

# Agent Scientific Work Mode
<!-- source: docs/agent-scientific-work-mode.md -->

# Agent Scientific Work Mode

## Purpose

This document explains how a human or coding agent should contribute small
scientific work units from APL's campaign queues.

Use this mode when a maintainer says things like:

- use spare token budget;
- do a small useful science task;
- pick something narrow from a campaign;
- make progress without starting a large implementation task.

## Default Strategy

Prefer campaign micro-task queues under `tasks/microtasks/`.

Start here:

1. `tasks/microtasks/README.md`
2. one campaign queue file
3. `docs/scientific-micro-task-protocol.md`
4. the related campaign page under `docs/campaigns/`

## How To Pick Work

Choose the smallest item that:

- stays inside one campaign;
- does not require new engine code;
- can be reviewed on its own;
- has a clear limitation statement.

Good choices:

- one pendulum candidate-family note;
- one Koide triplet computation with scope notes;
- one dimensional-analysis challenge entry;
- one thought-experiment assumption formalization;
- one diffusion-scaling falsification note.

## Batching Guidance

One PR may complete a small batch of related micro-tasks from the same
campaign.

Recommended batch size:

- `1-3` items for interpretation-heavy tasks;
- `3-5` items for tightly related dataset or challenge-set additions.

Do not mix multiple campaigns in one micro-task PR unless the maintainer asks
for it explicitly.

Use batching to reduce repeated context-gathering and review overhead, not to
make broad claims. Prefer a batch when all items share the same notation,
source files, validation command, and claim ceiling.

Suggested batch shapes:

| Work type | Suggested batch size |
| --- | ---: |
| Dataset or challenge entries in one queue | `3-5` |
| Formula-family proposals in one campaign | `2-3` |
| Candidate comparison or failure-mode notes | `1-2` |
| Source-aware particle-mass audits | `1-2` |
| Thought-experiment formalization | `1` |
| Repeatable formula-search attempts | `3-10` attempts, one campaign only |

Split the PR if the batch needs different background context for each item, if
the changed files cross campaign boundaries, or if one item would block the
rest in review.

When multiple agents may work during the same day, check recent open PRs,
existing `microtask_runs/` records, result notes, and campaign notes before
selecting a microtask. Avoid taking an item that already appears in an open PR,
claimed run record, completed run record, or recently merged note.

## Repeatable Search Loops

Some scientific work should be intentionally repeatable: an agent proposes a
new formula, dataset slice, threshold, or falsification condition, runs the
deterministic check, and publishes the outcome even if the candidate fails.

For repeatable work, create or update an append-only run record under
`microtask_runs/<queue-id>/` and record:

- campaign id and microtask id or run-family id;
- candidate formula, parameter slice, or hypothesis variant;
- input references and code references;
- method;
- metrics;
- failure mode or limitation;
- verdict or `REVIEW_NEEDED`;
- novelty check against existing notes, results, or run logs.

Failed attempts are useful scientific memory when they are reproducible and
specific. They should be stored as scoped negative or limitation notes rather
than erased as "no result".

## Required Safety Behavior

Agents must:

- report limitations;
- keep claim language conservative;
- state assumptions explicitly;
- mark uncertain outputs as `REVIEW_NEEDED`;
- prefer reviewable notes over overconfident conclusions.

Agents must not:

- promote claims;
- change canonical result artifacts casually;
- treat one micro-task as proof of a broader theory;
- turn spare-budget work into unplanned engine implementation.

## Suggested Output Pattern

For each completed micro-task, include:

- micro-task id;
- input references;
- method;
- limitation note;
- verdict or `REVIEW_NEEDED`.

If a PR completes several micro-tasks, add a short section for each item rather
than merging them into one vague summary.

## Escalation Rule

Escalate to a maintainer or reviewer when:

- the task starts to look like a new benchmark implementation;
- the wording pressure pushes toward a stronger scientific claim;
- the correct interpretation depends on domain judgment rather than a
  deterministic check;
- the work no longer fits a narrow one-session batch.
