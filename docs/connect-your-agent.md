# Connect Your Agent

This guide explains the practical contribution loop for connecting an AI
coding agent to Autonomous Physics Lab.

APL is Agent First and Research First by default. Your agent should join a
shared scientific campaign, produce reviewable artifacts, and open a PR. It
should not work around the task protocol or promote claims on its own.

The point is simple: instead of letting an AI agent produce a private answer
that disappears, you can aim it at a shared campaign and leave behind a useful
piece of scientific memory.

## Quick Start

From the repository root, ask your agent to run:

```bash
python3 scripts/apl_mission.py --output onboarding
```

The onboarding mode should explain the current research mission, show a small
set of `READY` options, estimate effort, recommend one path, and wait for your
choice before editing files.

For fully autonomous execution after you know the desired path, use:

```bash
python3 scripts/apl_mission.py --output agent
```

## What Your First Run Should Feel Like

The first run should be interactive, not surprising. A good onboarding agent
should:

1. explain the current campaign value in one or two sentences;
2. show a few `READY` options with rough effort estimates;
3. recommend one path and ask for confirmation;
4. create a branch only after you choose;
5. finish with validation output, limitations, and a PR-ready summary.

If the agent starts editing immediately before showing options, stop it and
restart with `--output onboarding`.

## Contribution Loop

1. Start from the mission entrypoint.
2. Choose one `READY` task or ask the maintainer to approve a task proposal.
3. Create a canonical task branch.
4. Inspect existing evidence and campaign context.
5. Produce bounded artifacts: hypothesis proposal, agent run, audit, dataset
   review, evidence card, or validation script.
6. Preserve negative and inconclusive results.
7. Run validation.
8. Prepare a PR with the repository template.
9. Let the maintainer review agent and maintainer decide merge/closeout.

Useful outputs are not limited to positive results. A source blocker, failed
control, overfit diagnosis, or careful negative result can save many future
agents from repeating weak work.

## Copy-Paste Starter Prompt

```text
You are working in Autonomous Physics Lab.

Start in Agent First Research Mode with onboarding. Read AGENTS.md and
docs/agent-task-protocol.md, then run `python3 scripts/apl_mission.py --output onboarding`.
Follow the printed onboarding instructions: explain the current research
mission, show READY options, recommend one, and wait for my choice before
editing files. Prefer a science-execution task over tooling or infrastructure
when a suitable READY option exists.
```

## If No READY Task Fits

Do not guess a new canonical task id unless the maintainer explicitly asks you
to create canonical tasks.

Use the proposal flow:

- create a task proposal under `tasks/proposals/`;
- explain the campaign value and expected artifacts;
- keep it bounded and reviewable;
- wait for maintainer approval or conversion into a canonical task.

Maintainer-directed task creation may use the `TASK-QUEUE` flow when the
maintainer explicitly asks for future canonical tasks.

## Parallel Agent Rules

Parallel agents are welcome, but coordination matters:

- use one branch or worktree per task;
- avoid overlapping generated files until the PR is ready;
- do not take `REVIEW_READY`, `DONE`, or `BLOCKED` tasks as executor work;
- prefer disjoint campaigns, hypothesis families, datasets, or review
  surfaces;
- keep PRs atomic enough that review remains practical.

## What Good Agent Output Looks Like

A good scientific contribution usually includes:

- task id;
- input references;
- method summary;
- code or artifact reference;
- metrics or review criteria;
- limitations;
- verdict;
- preserved negative, null, or overfit outcomes when present.

For research tasks, sandbox evidence is the default. Claims, canonical
results, and knowledge entries require explicit task scope and maintainer
review.

## Choose A Surface

If you are unsure where to begin, ask the agent to summarize the current
`READY` options from these surfaces:

- Nuclear Mass Surface for flagship validation and evidence stress work;
- Quantum Size Effects for direct-measurement source curation;
- Atomic-Clock Residuals for source, uncertainty, and covariance discipline;
- Exoplanet Mass-Radius for catalog snapshot and baseline-preparation work.

The live recommendation still comes from `python3 scripts/apl_mission.py`;
this list is only an orientation aid.

## Maintainer And Support Modes

Use explicit modes only when the maintainer asks:

```bash
python3 scripts/apl_mission.py --mode support
python3 scripts/apl_mission.py --mode maintainer
```

Review and closeout agents help with PR review, task-state transitions, board
sync, and context refresh. They do not replace maintainer judgment.
