# Use Your Agent

## Purpose

This guide is the contributor-facing entrypoint for people who want to explore
APL with Codex, Claude Code, or another coding agent.

The goal is not to let an agent improvise physics claims. The goal is to let
an agent help with reproducible, reviewable work inside the repository's
protocol.

## Quickstart: Start In Research Mode

Run the onboarding entrypoint first:

```bash
python3 scripts/apl_mission.py --onboarding
```

This starts **Research Mode** with a gentler first step: the agent should
explain the current scientific mission, show a few `READY` options, estimate
effort, recommend one, and wait for your choice before editing files.

For a coding agent, use:

```bash
python3 scripts/apl_mission.py --json
python3 scripts/apl_mission.py --onboarding
python3 scripts/apl_mission.py --agent-prompt
```

Use support mode only when you intentionally want docs, tests, packaging,
microtasks, or other non-research work:

```bash
python3 scripts/apl_mission.py --mode support
```

Use maintainer mode for review and closeout assistance:

```bash
python3 scripts/apl_mission.py --mode maintainer
```

The default contribution path is mission-first:

| Path | Use when | Expected output |
| --- | --- | --- |
| Research mission | You want the agent to help with science work | bounded hypothesis test, replay, audit, source review, or sandbox artifact |
| Assigned `READY` task | A maintainer already chose the task | one branch, one PR, validation evidence |
| Support mode | You intentionally want docs, tests, packaging, or queue hygiene | narrow non-research improvement |
| Proposal | No existing task fits the idea | task proposal, not an invented task id |

For a first run, prefer onboarding. It gives the user a pause point before the
agent starts editing files.

## One-Task One-Branch Discipline

Every contribution must follow this flow — no exceptions:

1. Pick one `READY` task, one approved microtask batch, or one proposal.
2. Create one branch or worktree for that task.
3. Change only files that belong to the task scope.
4. Run validation and record what passed or failed.
5. Open one PR with the repository template.
6. Wait for maintainer review; do not merge your own PR.

**Branch format:** `agent/<contributor-id>/<agent-id>/task-<number>-<short-slug>`

Example: `agent/akutenyov/claude/task-0120-use-your-agent-quickstart-diagrams`

Never work directly on `main`, invent a canonical task id, or mix unrelated
tasks into one branch.

## What the Review Cycle Looks Like

After you push your branch and open a PR, here is what happens:

1. GitHub CI checks the PR.
2. The maintainer or review agent reads the diff, artifacts, limits, and task
   fit.
3. If CI or review fails, fix the same branch and push again.
4. If review passes, the maintainer merges.
5. Closeout marks the task `DONE`, syncs navigation, and preserves the result
   or negative result in public memory.

The important rule: the agent prepares evidence; the maintainer decides merge.

## Before You Start

Read these first:

1. [README.md](../README.md)
2. Run `python3 scripts/apl_mission.py --onboarding`
3. [docs/current-missions.md](./current-missions.md)
4. [docs/mission-control.md](./mission-control.md)
5. [tasks/ACTIVE.md](../tasks/ACTIVE.md)
6. [docs/agent-task-protocol.md](./agent-task-protocol.md)
7. [docs/agent-catalog.md](./agent-catalog.md)

If you want a shorter session with safe work, also open:

- [docs/agent-work-menu.md](./agent-work-menu.md)
- [tasks/microtasks/README.md](../tasks/microtasks/README.md)
- [docs/private-agent-challenge-pack.md](./private-agent-challenge-pack.md)

## What Your Agent Can Help With

Good starting work:

- research replay, split-sensitivity checks, and adversarial audits;
- bounded sandbox hypothesis tests under an approved campaign;
- negative result preservation and PR-ready result drafts;
- documentation and onboarding improvements when support mode is selected;
- validation, wording, and contributor-workflow tasks.

New contributors can use the
[Private Agent Challenge Pack](./private-agent-challenge-pack.md) as a bounded
practice path before taking broader work.

Avoid starting with:

- broad engine rewrites;
- public-launch claims;
- unscoped formula speculation;
- multiple unrelated tasks in one branch.

## Safe Ways To Contribute

### 1. Start From A Research Mission

Run:

```bash
python3 scripts/apl_mission.py --onboarding
```

Follow the recommended mission unless the maintainer assigned something more
specific. Keep work sandbox-only and reviewable.

### 2. Pick One READY Task

Open [tasks/ACTIVE.md](../tasks/ACTIVE.md) and choose one task with:

- `status: READY`
- atomic scope
- no obvious overlap with another open PR

Do not offer `REVIEW_READY` tasks to executor agents as "available" work.
Those tasks are waiting for maintainer review, merge, or closeout. Use
maintainer mode when the goal is review or closeout.

Then follow the branch-first workflow from
[docs/agent-task-protocol.md](./agent-task-protocol.md).

### 3. Use Support Mode For Microtasks

If you have a shorter support session, use:

- `python3 scripts/apl_mission.py --mode support`
- [tasks/microtasks/README.md](../tasks/microtasks/README.md)
- [docs/agent-scientific-work-mode.md](./agent-scientific-work-mode.md)

Stick to one campaign queue at a time and keep the output narrow.

## Before Reviewing Core Results

If your first goal is to verify the current major benchmark surface rather
than start new task work, run the bounded replay script:

```bash
python3 scripts/reproduce_core_results.py
```

It regenerates the selected public-facing core results into `/tmp`, writes a
summary file, and leaves canonical `results/` artifacts untouched. See
[docs/reproducibility-capsules.md](./reproducibility-capsules.md) for expected
metrics, caveats, and the intentionally skipped Muon g-2 stress-test lane.

## Minimum Rules Your Agent Must Follow

- do not work directly on `main`
- do not invent a new task id
- do not promote a claim without maintainer review
- do not rewrite canonical `results/` artifacts casually
- do not say "AI resolved physics"
- do not use "proof" or discovery-framing language for benchmark results
- do not hide limitations

## Practical Prompt Pattern

If you are using a coding agent, a good starting prompt is:

```text
You are working in Autonomous Physics Lab.

Start in Agent First Research Mode with onboarding. Read AGENTS.md and
docs/agent-task-protocol.md, then run `python3 scripts/apl_mission.py --onboarding`.
Explain the current research mission briefly, show a few READY options with
estimated time, recommend one, and wait for my choice before editing files.
When listing available work, include only READY tasks; do not offer REVIEW_READY
tasks as executor options. After I choose, execute the selected task
autonomously: create the task branch, inspect evidence, test or audit the
hypothesis, preserve negative results, run validation, generate a review
bundle, and prepare a PR. Keep outputs sandbox-only unless a canonical task
explicitly allows promotion. Do not promote claims, rewrite canonical results,
or use breakthrough-style wording.
```

For full autonomous execution, replace `--onboarding` with `--agent-prompt`.

If you are using support mode, run `python3 scripts/apl_mission.py --mode support`
and give the agent the selected task or queue item.

## What a Good Agent Output Looks Like

A good contribution should leave behind:

- a clear branch tied to one task;
- changed files that match the task scope;
- explicit validation results;
- limitation wording where needed;
- a reviewable PR body using the repository template.

## Where To Ask the Agent To Start

Best first destinations:

- `python3 scripts/apl_mission.py --onboarding`
- [docs/current-missions.md](./current-missions.md)
- [docs/mission-control.md](./mission-control.md)
- [docs/results/visual-summary.md](./results/visual-summary.md)
- [docs/results/koide-campaign-summary.md](./results/koide-campaign-summary.md)
- [docs/negative-results-registry.md](./negative-results-registry.md)
- [tasks/ACTIVE.md](../tasks/ACTIVE.md)

These give the agent a better current snapshot than asking it to infer project
state from old commits.

## Final Reminder

Agents are useful here because they can help execute the workflow, not because
they replace deterministic validation or maintainer judgment.

Use the agent to create momentum. Keep the repository, the artifacts, and the
claims as the source of truth.
