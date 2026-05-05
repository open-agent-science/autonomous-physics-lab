# Autonomous Physics Lab — Context Bundle

Generated: 2026-05-05 15:30 UTC  
Mode: core  
Repo: gladunrv/autonomous-physics-lab

This file bundles the core project instructions, strategy, and current
task board into one document for use with chat-based LLMs or as a
quick agent orientation file.

For the live repository see: https://github.com/gladunrv/autonomous-physics-lab


────────────────────────────────────────────────────────────────────────

# Agent & Contributor Rules
<!-- source: AGENTS.md -->

# AGENTS.md

## Project

This repository is `autonomous-physics-lab`.

Autonomous Physics Lab is an open-source scientific engine for generating,
testing, simulating, falsifying, scoring, and reusing physics hypotheses.

It is not a chatbot. It is a hypothesis-testing machine.

## Core Principle

LLMs may propose, explain, and organize hypotheses, but numerical and symbolic
claims must be verified by deterministic code.

Never trust an LLM-generated formula without validation.

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
- `docs/task-proposal-protocol.md`
- `docs/agent-operating-model.md`
- `tasks/ACTIVE.md`
- `tasks/TASK-TEMPLATE.yaml`
- `tasks/proposals/TASK-PROPOSAL-TEMPLATE.yaml`

Do not treat `CODEX_TASK.md` as the single source of truth for active work.
Do not invent task branch, commit, PR, or task-state formats locally.
Use `docs/agent-task-protocol.md`.
Use `docs/task-proposal-protocol.md` when suggesting new task ideas that do
not yet have a maintainer-assigned canonical `TASK-XXXX` id.
Use `docs/maintainer-review-agent.md` when the maintainer wants structured PR
review or task closeout help.

Before starting implementation, agents must create a working task branch using
the canonical branch format. Agents must not begin editing repository files,
staging changes, or otherwise performing task work on `main`.

## Task Proposal Rule

If no existing `READY` task fits and the maintainer did not explicitly assign a
canonical `TASK-XXXX` id, agents should create a proposal under
`tasks/proposals/` instead of guessing the next task number.

Normal agents should not assign canonical task ids during parallel work.

Maintainers may create canonical ids directly. Maintainer-directed review or
task-admin agents may do so only on explicit maintainer instruction.

## Original MVP

The first MVP was `Pendulum Formula Discovery`.

Goal:

1. Generate exact pendulum period data.
2. Fit correction formulas.
3. Compare models.
4. Score accuracy and complexity.
5. Produce a reproducible report.

## Current Benchmark Scope

The repository currently has two working benchmark slices:

- `EXP-0001` — `Pendulum Formula Discovery`
- `EXP-0002` — `Damped Oscillator Regime Verification`
- `EXP-0001/RUN-0002` — theory-aware pendulum near-separatrix follow-up

Use that broader benchmark scope when updating docs, status snapshots, and
contributor guidance during pre-public validation.

## Planning Files

To continue work consistently, use these project documents:

- `docs/strategy.md` for the strategic compass;
- `docs/agent-task-protocol.md` for the canonical execution protocol;
- `docs/agent-operating-model.md` for the shared agent workflow;
- `tasks/ACTIVE.md` for the live task board;
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

AI assistance should be recorded in PR metadata, not in git co-author trailers.

Maintainer review and task closeout may be assisted by a maintainer-run review
agent, but that agent must not auto-merge PRs, promote claims, or mark tasks
`DONE` before maintainer review and merge.

After committing, agents should generate a review bundle:

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
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
git diff --exit-code
```

If a change touches CLI behavior, include a smoke test.
If a change touches scientific formulas, include a numerical regression test.
For branch naming, commit messages, PR titles, task-state transitions, and the
standard execution flow, use `docs/agent-task-protocol.md`.


────────────────────────────────────────────────────────────────────────

# Claude Code Entry Point
<!-- source: CLAUDE.md -->

# Claude Entry Point

Read these files first:

1. `AGENTS.md`
2. `docs/agent-task-protocol.md`
3. `tasks/ACTIVE.md`
4. `docs/strategy.md`

Do not invent branch, PR, or commit formats.
Use `docs/agent-task-protocol.md`.
Use branch format `agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug>`.
If the maintainer did not assign a canonical `TASK-XXXX` id, use
`docs/task-proposal-protocol.md` and branch format
`agent/<contributor-id>/<agent-id>/propose-task-<short-slug>` for new task
ideas.
Claude is a tool identifier, not a substitute for the human contributor id.


────────────────────────────────────────────────────────────────────────

# Project Strategy
<!-- source: docs/strategy.md -->

# Strategy

## Current Phase

`v0.1-private-alpha — scientific campaign and contributor workflow validation`

## Mission

Build verification-first scientific infrastructure for testing, falsifying,
scoring, and reusing physics hypotheses.

APL is not trying to generate dramatic claims on demand. It is trying to make
scientific work reproducible, reviewable, and reusable through deterministic
code and version-controlled evidence.

## Strategic Shift

The repository is no longer focused mainly on bootstrap infrastructure work.
That base now exists well enough to support a new emphasis:

- curate active scientific campaigns with clear scope and honest limitations;
- onboard contributors into a branch-based, reviewable workflow;
- improve project-level orientation so results, tasks, and risks stay legible;
- keep public-launch work gated behind validation and review discipline.

## Current Priorities

1. Curate scientific campaigns rather than broadening into many unfinished
   benchmark ideas at once.
2. Prepare and maintain a clear Mission Control and campaign-map layer so new
   contributors can see what APL is trying to do and where evidence already
   exists.
3. Keep Koide and particle-mass work falsification-first, narrow in scope, and
   resistant to numerology overclaim.
4. Improve visual result summaries and contributor-facing navigation around the
   strongest current evidence.
5. Continue the private contributor pilot and maintainer review loop before any
   public rollout.
6. Prepare public launch only after the explicit gates in
   [public-release-gates.md](./public-release-gates.md) are satisfied.

## Current Goal

Demonstrate that APL can run honest scientific campaigns and a disciplined
contributor workflow at the same time, without relaxing verification standards
or overstating benchmark results.

## Current North-Star Outcomes

- campaign-oriented scientific work with explicit boundaries, current evidence,
  and next-safe-task surfaces;
- reproducible results that preserve failure modes and limitation wording;
- contributor onboarding that does not require tribal knowledge to understand
  tasks, review expectations, or release posture.

Current visible evidence includes:

- the pendulum gauntlet result package from `EXP-0001/RUN-0003`;
- charged-lepton Koide reproduction from `EXP-0004/RUN-0004`;
- the tau holdout benchmark from `EXP-0005/RUN-0005`.

These results are useful because they are reviewable and reproducible, not
because they justify expansive scientific claims.

## Current Execution Model

The repository uses a shared task pool with branch-based execution.

- a task defines the contract;
- an agent or human picks one atomic task;
- validation runs before handoff;
- task files and board state remain the coordination layer;
- maintainer review stays the decision point for merge and closeout.

The repository remains private until the release gates are satisfied and a
maintainer decides the narrative matches the evidence.

## Non-Goals

- Do not frame narrow benchmark outputs as discovery-level physics.
- Do not describe particle-mass results as explanations of mass generation.
- Do not claim universal validity from configured-range validation.
- Do not add dashboard, public API, literature ingestion, or public task
  network before current campaign and workflow gates are met.
- Do not use LLM prose as a substitute for deterministic validation.

## Decision Rule

When choosing between faster expansion and stronger verification, choose
stronger verification.


────────────────────────────────────────────────────────────────────────

# Mission Control (Current Phase)
<!-- source: docs/mission-control.md -->

# Mission Control

## What APL Is Trying To Do

Autonomous Physics Lab (APL) is verification-first scientific infrastructure.
Its job is to make physics hypotheses testable, falsifiable, reproducible, and
reviewable through deterministic code and version-controlled evidence.

APL is currently in:

`v0.1-private-alpha — scientific campaign and contributor workflow validation`

The repository stays private while current campaigns, contributor workflow, and
public-release gates are still being validated.

## What APL Is Not Trying To Do

- It is not a chatbot for speculative physics claims.
- It is not treating numerically interesting fits as discovery-level evidence.
- It is not presenting benchmark fits as complete explanations of particle masses.
- It is not presenting range-limited benchmarks as globally valid theories.
- It is not public-launch ready yet.

## Active Campaigns

APL currently organizes work around four contributor-facing campaign surfaces:

| Campaign | Status | Why it exists | Best starting point |
| --- | --- | --- | --- |
| [Pendulum Formula Falsification](./campaigns/pendulum-formula-falsification.md) | Active with canonical results | Stress-test approximation discovery against an exact reference with explicit failure modes | [pendulum-gauntlet-100-summary.md](./results/pendulum-gauntlet-100-summary.md) |
| [Particle Mass Relations](./campaigns/particle-mass-relations.md) | Active with narrow benchmark results | Test whether impressive mass relations survive disciplined, falsification-first handling | [koide-tau-holdout.md](./results/koide-tau-holdout.md) |
| [Dimensional Analysis Validator](./campaigns/dimensional-analysis-validator.md) | Planning complete, implementation pending | Build a quality floor for future formula and benchmark work | [dimensional-analysis-challenge-set.md](./notes/dimensional-analysis-challenge-set.md) |
| [Thought-Experiment Consistency](./campaigns/thought-experiment-consistency.md) | Planning active, no canonical run yet | Extend APL into consistency checks that do not depend on curve fitting alone | [thought-experiment-consistency-suite.md](./notes/thought-experiment-consistency-suite.md) |

## Current Results

The clearest current repository-level results are:

1. [Pendulum Gauntlet 100](./results/pendulum-gauntlet-100-summary.md) —
   100 deterministic pendulum candidate formulas evaluated with stored
   leaderboard, diagnostics, and precision audit.
2. [Koide charged-lepton reproduction](./results/koide-charged-lepton-reproduction.md)
   — a narrow dataset-based reproduction benchmark with uncertainty-aware
   comparison.
3. [Koide tau holdout](./results/koide-tau-holdout.md) — a historical
   holdout-style benchmark associated with `RESULT-0006`, kept narrow and
   explicitly non-explanatory.

These results matter because they are reproducible and reviewable. They do not
authorize exact symbolic proof, universal scope, or deeper physical
explanation by themselves.

## How Contributors Can Plug In

The current contributor workflow is branch-based and task-driven.

Operational entry points:

- [tasks/ACTIVE.md](../tasks/ACTIVE.md) for the live board of canonical tasks;
- [tasks/microtasks/README.md](../tasks/microtasks/README.md) for campaign-specific scientific microtask queues;
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
- `python3 -m physics_lab.cli sync-active-board .` for keeping the active board
  aligned with task YAML files;
- maintainer review and closeout tooling for review bundles and handoff.

Low-risk contribution patterns right now:

- improve status, roadmap, onboarding, or campaign documentation;
- tighten wording, diagnostics, or visual summaries around existing results;
- complete one small batch from a single scientific microtask queue;
- work on planning or validation tasks that do not churn canonical result
  artifacts.

## What Not To Claim

- Do not describe APL as having resolved physics.
- Do not describe the repository as having made a discovery-level physical breakthrough.
- Do not call pendulum approximations exact or globally valid.
- Do not treat charged-lepton or tau-holdout benchmarks as explanations of
  particle masses.
- Do not describe planning-only campaigns as implemented benchmark systems.
- Do not present the repository as public before the release gates are met.

## Read Order For New Contributors

1. [README.md](../README.md)
2. [docs/mission-control.md](./mission-control.md)
3. [docs/campaigns/README.md](./campaigns/README.md)
4. [docs/status.md](./status.md)
5. [tasks/ACTIVE.md](../tasks/ACTIVE.md)
6. [docs/agent-task-protocol.md](./agent-task-protocol.md)


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
4. [../tasks/ACTIVE.md](../tasks/ACTIVE.md)
5. the matching `tasks/TASK-XXXX-*.yaml` file when working on a canonical task
6. [./strategy.md](./strategy.md)

Use [./agent-operating-model.md](./agent-operating-model.md) and
[./contributing-workflow.md](./contributing-workflow.md) for supporting
context, not as competing protocol definitions.

## Pick a Task

1. Start with one atomic task that is already `READY`.
2. Do not start a second task unless a human explicitly asks for it or the work
   is clearly independent.
3. Do not start `REVIEW_READY`, `BLOCKED`, or `REJECTED` tasks unless a human
   explicitly redirects you.
4. If no existing task fits, ask for or propose a new task before doing
   substantial work.

## Task Proposals

If no existing `READY` task fits, do not guess the next canonical task number
during parallel work.

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

- prefer one campaign queue at a time;
- one PR may complete a small batch of related microtasks from the same
  campaign;
- do not mix many campaigns in one microtask PR unless the maintainer asks;
- do not create many new canonical `TASK-XXXX` files just to represent tiny
  queue items;
- do not promote claims from microtask outputs;
- report limitations for every completed item;
- if uncertain, mark the output `REVIEW_NEEDED`.

Use [./agent-scientific-work-mode.md](./agent-scientific-work-mode.md) for the
practical operating pattern.

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
- `REJECTED`: the task should not proceed in its current form.

Rules:

- An agent may move `READY -> IN_PROGRESS`.
- An agent may move `IN_PROGRESS -> REVIEW_READY`.
- Only a maintainer should move `REVIEW_READY -> DONE`.
- A maintainer may use a maintainer-run review agent to assist review and
  closeout, but the agent output is advisory rather than autonomous.
- If blocked, set `BLOCKED` and explain why in the task file, board, or PR.
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

After implementation and validation:

1. push the task branch only when a human or workflow expects a PR;
2. open one PR for one task branch;
3. use the required PR title format;
4. complete the repository PR template;
5. include limitations, validation results, and artifact-impact notes;
6. move the task to `REVIEW_READY`.

## Pull Request Requirements

Every PR should include:

- Task ID
- task file path
- branch name
- contributor id
- GitHub username
- agent tool
- model/version if known
- agent session id
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
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
git diff --exit-code
```

Use `--output-dir` for routine example runs so committed canonical artifacts do
not change accidentally.

Before opening a PR, also generate a review bundle for the maintainer:

```bash
./scripts/apl_review_bundle.sh
```

This produces `_snapshots/review_<branch>_<timestamp>.md` with the full diff
vs `main`, commit list, and changed-file summary.

For task proposal PRs, the lighter validation path from
[./task-proposal-protocol.md](./task-proposal-protocol.md) is acceptable.

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
- help close a merged task by updating the task file and
  synchronizing [../tasks/ACTIVE.md](../tasks/ACTIVE.md).

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
5. Do not edit [../tasks/ACTIVE.md](../tasks/ACTIVE.md) for routine task
   status transitions. Task YAML is the canonical source of truth; the board is
   a maintainer-synchronized snapshot.
6. If the task itself changes active-board behavior or presentation, update the
   board and run `python3 -m physics_lab.cli sync-active-board .` as part of
   that scoped task.
7. Make the smallest reproducible change that satisfies the task.
8. Run the required validation commands.
9. Set the task to `REVIEW_READY` when implementation and validation are done.
10. Leave clear maintainer review notes and limitations.

After merge, maintainer closeout may also:

11. set the task to `DONE`;
12. run `python3 -m physics_lab.cli sync-active-board .` so
    [../tasks/ACTIVE.md](../tasks/ACTIVE.md) reflects the new task state;
13. add a dry-run note when the merged PR belongs to a contributor pilot.

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


────────────────────────────────────────────────────────────────────────

# Active Task Board
<!-- source: tasks/ACTIVE.md -->

# Active Task Board

## CURRENT STRATEGY

APL is verification-first scientific infrastructure.

Current phase: `v0.1-private-alpha — scientific campaign and contributor workflow validation`

Current goal:

- active scientific campaigns with conservative result wording
- private contributor pilot and maintainer review workflow validation
- public release only after explicit gates are satisfied

The repository remains private until
[../docs/public-release-gates.md](../docs/public-release-gates.md) are
satisfied.

Use [../docs/strategy.md](../docs/strategy.md) as the strategic compass and
[../docs/agent-task-protocol.md](../docs/agent-task-protocol.md) as the
canonical execution protocol. Use
[../docs/agent-operating-model.md](../docs/agent-operating-model.md) for
supporting workflow context and handoff norms.

Repository-level orientation now starts with
[../docs/mission-control.md](../docs/mission-control.md) and
[../docs/campaigns/README.md](../docs/campaigns/README.md) before drilling
into task-level work.

For new task ideas without a maintainer-assigned canonical `TASK-XXXX` id, use
the proposal-first flow in [../docs/task-proposal-protocol.md](../docs/task-proposal-protocol.md).

For spare token or time budget scientific work, use
[../tasks/microtasks/README.md](../tasks/microtasks/README.md) together with
[../docs/agent-scientific-work-mode.md](../docs/agent-scientific-work-mode.md).
Prefer one small batch from one campaign queue rather than mixing campaigns in
one PR.

<!-- BEGIN AUTO TASK STATUS BOARD -->

> This task-status snapshot is generated from canonical task YAML files.
> Edit `tasks/TASK-*.yaml` for routine status transitions, then run
> `python3 -m physics_lab.cli sync-active-board .` on the maintainer branch.

## READY

- `TASK-0030` — Record first friend contributor dry run (`contributor_pilot`, priority `medium`, difficulty `low`)
- `TASK-0047` — Reduce closeout PR conflicts around active board sync (`maintainer_workflow`, priority `high`, difficulty `medium`)
- `TASK-0055` — Add experiment flow diagram to architecture docs (`documentation`, priority `medium`, difficulty `low`)
- `TASK-0058` — Standardize scoped verdict wording for tau holdout (`scientific_safety_review`, priority `high`, difficulty `low`)
- `TASK-0063` — Generate static visual result pack for Pendulum and Koide (`scientific_visualization`, priority `high`, difficulty `medium`)
- `TASK-0078` — Add Agent Work Menu for spare-token scientific work (`contributor_experience`, priority `high`, difficulty `low`)
- `TASK-0081` — Run first hypothesis register pilot through an APL next-step flow (`workflow_pilot`, priority `medium`, difficulty `medium`)
- `TASK-0082` — Add Koide baseline planning for guarded next-step evaluation (`benchmark_planning`, priority `medium`, difficulty `medium`)

## IN_PROGRESS

None.

## REVIEW_READY

None.

## DONE RECENTLY

- `TASK-0083` — Add agent-ready scientific work loop follow-up tasks (merged)
- `TASK-0080` — Run first dimensional-analysis scientific microtask batch (merged)
- `TASK-0077` — Add proposal PR format and salvage guardrails (merged)
- `TASK-0076` — Add fast and deep maintainer review lanes (merged)
- `TASK-0075` — Add scientific microtask queues for agent work (merged)
- `TASK-0074` — Harden closeout protocol binding checks for automation (merged)
- `TASK-0073` — Define maintainer automation agent architecture and routine instructions (merged)
- `TASK-0071` — Support closeout batch PRs in review helper (merged)
- `TASK-0067` — Add v0.2 release-focused campaign tasks (merged)
- `TASK-0064` — Implement dimensional analysis validator MVP (merged)
- `TASK-0062` — Update project status and roadmap for scientific campaign phase (merged)
- `TASK-0061` — Create Mission Control and campaign map (merged)
- `TASK-0060` — Add open pull request list to repository snapshot (merged)
- `TASK-0057` — Reduce snapshot noise from worktrees and include proposal backlog (merged)
- `TASK-0056` — Accept selected science-track proposals into canonical tasks (merged)
- `TASK-0054` — Fix maintainer review helper temp claim path handling in git worktrees (merged)
- `TASK-0051` — Define hypothesis register schema and launch entry micro-task track (merged)
- `TASK-0050` — Define and launch approximation-breakdown probes micro-task track (merged)
- `TASK-0049` — Define and launch physical constants verification micro-task track (merged)
- `TASK-0048` — Add schema support for dataset-based particle-mass reproduction benchmarks (merged)
- `TASK-0044` — Sync active task board from task files to reduce merge conflicts (merged)
- `TASK-0043` — Add task proposal protocol and id allocation rules (merged)
- `TASK-0042` — Add numerology guardrails for particle mass relation work (merged)
- `TASK-0041` — Design complexity penalty for mass-relation formulas (merged)
- `TASK-0039` — Design Koide-like triplet search with baselines (merged)
- `TASK-0038` — Reproduce historical tau-mass holdout prediction (merged)
- `TASK-0037` — Reproduce Koide charged-lepton relation (merged)
- `TASK-0036` — Create particle mass dataset scaffold (merged)
- `TASK-0035` — Refactor maintainer review checks into smaller modules (merged)
- `TASK-0034` — Add maintainer review agent mode (merged)
- `TASK-0033` — Standardize contributor-agent identity format (merged)
- `TASK-0032` — Build public scientific result package for Pendulum Gauntlet 100 (merged)
- `TASK-0031` — Add beginner-friendly contributor task set (merged)
- `TASK-0029` — Audit project language for overclaim risk (merged)
- `TASK-0028` — Plan light-clock thought experiment consistency check (merged)
- `TASK-0027` — Create units and physical constants reference (merged)
- `TASK-0026` — Add 10 more dimensional-analysis challenge items (merged)
- `TASK-0025` — Create result artifacts index (merged)
- `TASK-0024` — Create task index table (merged)
- `TASK-0023` — Create first contributor runbook (merged)
- `TASK-0022` — Add PR review bundle snapshot script (merged)
- `TASK-0021` — Add AI agent attribution policy (merged)
- `TASK-0020` — Add pytest-timeout and validation safeguards against hanging tests (merged)
- `TASK-0019` — Standardize agent branch, commit, and pull request protocol (merged)
- `TASK-0018` — Support planning-only and workflow tasks without fake hypothesis references (merged)
- `TASK-0017` — Create a dimensional analysis challenge set (merged)
- `TASK-0015` — Plan the diffusion scaling benchmark (merged)
- `TASK-0014` — Plan a thought-experiment consistency suite (merged)
- `TASK-0013` — Plan a particle mass relation falsifier inspired by Koide-style formulas (merged)
- `TASK-0012` — Run a private multi-agent contributor dry run (merged)
- `TASK-0011` — Audit numerical precision versus model residual for the pendulum gauntlet run (merged)
- `TASK-0010` — Run pendulum hypothesis gauntlet with 100 candidate formulas (merged)
- `TASK-0008` — Add machine-readable review metadata for patch-style evidence artifacts (merged)
- `TASK-0007` — Add fail-on-warnings support for strict repository validation (merged)
- `TASK-0006` — Establish shared agent task board and operating model (merged)
- `TASK-0005` — Add artifact hash drift validation (merged)
- `TASK-0004` — Strengthen claim promotion policy (merged)
- `TASK-0003` — Add theory-aware pendulum approximation near the separatrix (merged)
- `TASK-0002` — Verify damped oscillator regimes against exact solutions (merged)
- `TASK-0001` — Find better pendulum correction formula (merged)

## PROPOSED

- `TASK-0016` — Plan an electromagnetic invariance mini-benchmark (`benchmark_planning`, priority `medium`, difficulty `medium`)
- `TASK-0040` — Build particle mass relation falsifier MVP (`scientific_falsification`, priority `high`, difficulty `high`)
- `TASK-0059` — Prepare Koide tau holdout public summary package (`documentation`, priority `medium`, difficulty `low`)

## BLOCKED

- `TASK-0065` — Finalize Koide tau holdout public result package (`release_preparation`, priority `medium`, difficulty `medium`)
- `TASK-0066` — Review v0.2 public readiness gates (`release_review`, priority `medium`, difficulty `low`)

## REJECTED

- `TASK-0009` — Plan EXP-0003 as a diffusion scaling benchmark (`benchmark_planning`, priority `high`, difficulty `medium`)

<!-- END AUTO TASK STATUS BOARD -->

## Recommended first tasks for new contributors

Prefer independent `READY` tasks with:

- documentation-only scope;
- no canonical result-artifact churn;
- no shared branch or board-maintenance coupling;
- validation that does not require regenerating benchmark outputs.

If a contributor first needs scientific context rather than a task, start with
[../docs/campaigns/README.md](../docs/campaigns/README.md) and then return to
the `READY` section.

If multiple `READY` tasks fit, pick the smallest one that does not touch the
same artifact surface as another open PR.

## DO NOT START YET

- dashboard
- web API
- arXiv or OpenAlex ingestion
- multi-agent runtime
- database backend
- public launch
- discovery-level physics claims

## PROPOSED NOTE

`PROPOSED` items are backlog ideas, not active execution tasks. Agents should
start from `READY` tasks unless a maintainer explicitly redirects them.
