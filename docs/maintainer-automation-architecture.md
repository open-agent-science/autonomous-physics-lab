# Maintainer Automation Architecture

This document defines the first maintainer automation layer for Autonomous
Physics Lab.

The goal is not to create an autonomous governance bot. The goal is to reduce
routine maintainer work while keeping merge authority, scientific judgment,
and repository-risk decisions with the human maintainer.

## Why This Exists

The repository now has enough structured state that recurring maintainer work
is predictable:

- open PR triage;
- proposal acceptance screening;
- targeted PR review on request;
- merged-task closeout sweeps;
- release-readiness spot checks.

That makes the work a good fit for file-backed agent routines.

## Design Principles

1. Human authority stays at the top.
   Agents may recommend, summarize, classify, and prepare follow-up actions.
   They do not merge PRs, promote claims, or make the repository public on
   their own.

2. Deterministic checks outrank free-form judgment.
   Routine agents should prefer repository scripts, validation commands,
   review bundles, and canonical task files over narrative inference.

3. File-backed instructions beat chat-only memory.
   Periodic or manual automations should read stable instruction files from the
   repository instead of relying on reconstructed prompt history.

4. Narrow agents beat one giant agent.
   Each automation surface should have a small, legible contract and clear
   stop conditions.

5. Default to safe non-destructive behavior.
   By default, routine agents should review, summarize, and propose actions.
   Action-taking behavior should be bounded by a file-backed policy, not by
   improvised agent judgment.

## Execution Model

APL should treat maintainer automation as a small control plane with three
execution modes:

- `routine mode`
  periodic sweeps driven by an instruction file
- `manual mode`
  targeted runs triggered by a human request
- `action mode`
  policy-limited execution runs that may perform bounded maintainer actions

All three modes use the same repository rules and deterministic helpers. They
differ in trigger style, scope, and whether they may execute low-risk actions.

## Current Agent Catalog

### 1. Maintainer Review And Closeout Agent

Purpose:
- review open PRs;
- classify them as `MERGE_OK`, `NEEDS_CHANGES`, or `BLOCKED`;
- detect merged tasks that still need closeout;
- prepare or apply closeout changes after maintainer approval.

Primary docs:
- [./maintainer-review-agent.md](./maintainer-review-agent.md)
- [./review-checklists/maintainer-pr-review-checklist.md](./review-checklists/maintainer-pr-review-checklist.md)
- [./review-checklists/task-closeout-checklist.md](./review-checklists/task-closeout-checklist.md)

Primary helpers:
- `python3 scripts/apl_review_pr.py --pr <number>`
- `python3 scripts/apl_closeout_task.py --task TASK-XXXX --pr <number>`
- `python3 scripts/apl_closeout_task.py --task TASK-XXXX --pr <number> --apply`

This agent should operate with two review lanes:

- `fast review`
  for low-risk docs, planning, proposal-only, task-admin, and closeout PRs
- `deep review`
  for engines, workflows, schemas, claims, results, maintainer scripts, CI,
  automation logic, and public scientific wording

The lane must be chosen before running a full review cycle. This reduces queue
latency by keeping deep review for truly sensitive surfaces.

### 2. Proposal Acceptance Triage Agent

Purpose:
- scan open proposal PRs;
- compare them against strategy, roadmap, and blocker needs;
- recommend `accept now`, `hold`, or `reject`;
- identify when a proposal should become a canonical task.

This agent does not accept proposals automatically by default. It prepares a
maintainer recommendation and, when requested, a clean maintainer-admin PR.

### 3. Open PR Queue Agent

Purpose:
- scan the open PR queue;
- separate `merge now`, `needs follow-up`, `stale/superseded`, and `closeout-ready`;
- propose the next best merge order.

This is the best periodic agent to run first because it reduces queue entropy
for the maintainer.

### 4. Task Closeout Sweep Agent

Purpose:
- find merged PRs whose tasks still remain `REVIEW_READY`;
- verify accepted outputs in `main`;
- prepare a clean closeout batch or per-task closeout recommendation.

This agent should be conservative:
- do not mark a task `DONE` unless merge is confirmed;
- do not trust generated `docs/task-views/*.md` alone;
- always verify canonical task YAML and repository state.

### 5. Future Specialized Agents

Recommended future automation surfaces:

- `code review sweep agent`
  cross-checks open code-heavy PRs for validation gaps, test coverage, and
  review-bundle presence
- `security sweep agent`
  periodically inspects repository-safety surfaces such as maintainer scripts,
  CI workflows, execution paths, and dependency-touching changes
- `release readiness agent`
  checks whether public-release gates, campaign pages, result summaries, and
  visuals satisfy a named release milestone such as `v0.2`

These should be added incrementally, not all at once.

## Shared Contract For Routine Agents

Every maintainer automation agent should declare:

- `purpose`
- `mode`
- `inputs`
- `deterministic helpers used`
- `allowed actions`
- `not allowed`
- `output format`
- `stop conditions`

### Minimum Inputs

Depending on mode, inputs may include:

- open PR list;
- selected PR number;
- selected task id;
- canonical task YAML files;
- `docs/task-views/*.md`;
- `docs/strategy.md`;
- `docs/roadmap.md`;
- `docs/status.md`;
- review bundles;
- GitHub CI state.

### Default Allowed Actions

Safe default actions:

- review and summarize;
- classify and prioritize;
- generate maintainer comments for optional posting;
- generate or update review bundles when local branch context exists;
- prepare closeout or admin diffs on a task branch;
- propose clean replacement PRs for stale or contaminated branches.

### Action-Mode Allowed Actions

Action mode may perform only policy-limited maintainer actions such as:

- posting a prepared English PR comment;
- closing a clearly superseded PR when a replacement PR exists;
- pushing a clean maintainer branch that only changes maintainer-workflow or
  documentation surfaces;
- opening a maintainer-admin or closeout PR for already-verified changes;
- applying task closeout for verified merged tasks when the instruction file
  explicitly allows it.

These actions should be rule-based, narrow, and auditable.

For the first practical rollout, APL should enable exactly one default action:

- prepare and open a closeout PR for verified merged tasks, then run the
  maintainer review agent on that closeout PR

This is the highest-value routine reduction step because it removes repeated
maintainer cleanup work without handing merge authority to automation.

### Default Not Allowed

Unless the maintainer explicitly asks:

- do not merge PRs;
- do not auto-comment on PRs;
- do not close PRs;
- do not push branches;
- do not promote claims;
- do not rewrite scientific verdicts;
- do not regenerate canonical result artifacts;
- do not mark the repository public.

## Three Operating Modes

## Routine Mode

Routine mode is for periodic sweeps.

Recommended triggers:

- every morning;
- after a batch of merges;
- before a maintainer review session;
- before release-readiness review.

Routine mode should usually:

1. list open PRs;
2. classify them into `merge candidates`, `needs work`, `stale/superseded`;
3. scan proposal PRs for strategic fit and blocker relevance;
4. scan merged-but-not-closed tasks;
5. return a prioritized action list;
6. stop unless the maintainer explicitly asks for edits, comments, closeout, or
   new PR preparation.

The file-backed instructions for this mode live in:
- [./automation/maintainer-routine-mode.md](./automation/maintainer-routine-mode.md)

## Manual Mode

Manual mode is for a targeted maintainer request.

Examples:

- review PR `#70`
- check whether `TASK-0024` can be closed
- scan all open PRs and suggest merge order
- prepare a closeout batch for merged tasks

Manual mode may go deeper on one surface, but it should still respect the same
human-approval boundaries.

The file-backed instructions for this mode live in:
- [./automation/maintainer-manual-mode.md](./automation/maintainer-manual-mode.md)

## Action Mode

Action mode is for periodic or ad hoc runs that should perform a bounded action
instead of only reporting.

Examples:

- post a prepared maintainer comment on a blocked PR;
- close a PR that is clearly superseded by a clean replacement;
- open a closeout PR for verified merged tasks;
- open a maintainer-admin PR that accepts a clearly approved proposal set.

The recommended first enabled action is:

1. detect verified merged tasks that still are not `DONE`
2. prepare and open a closeout PR
3. run the maintainer review agent on that closeout PR
4. stop and wait for human merge

Action mode should never infer broad authority from the fact that it can act.
It should perform only actions allowed by its instruction file and stop when a
case becomes ambiguous.

The file-backed instructions for this mode live in:
- [./automation/maintainer-action-mode.md](./automation/maintainer-action-mode.md)

## Suggested Output Shapes

Routine outputs should be compact and operational:

- `merge now`
- `review next`
- `blocked`
- `stale / superseded`
- `closeout needed`

Manual outputs may be more detailed:

- verdict;
- blockers;
- required fixes;
- recommended next action;
- optional English PR comment draft.

Action outputs should record:

- action taken;
- target PR or task;
- deterministic checks used;
- why the action was allowed under policy;
- any follow-up still requiring human review.

## Stop Conditions

The automation should stop and surface the issue to the maintainer when:

- task contract and diff disagree in a non-trivial way;
- result artifacts changed unexpectedly;
- claim promotion appears in scope;
- CI and local validation disagree;
- branch contamination suggests a clean replacement PR is safer than patching;
- a proposal touches strategy in a way that needs human judgment.
- the requested action would touch scientific claims, verdict wording, or
  canonical result artifacts without explicit maintainer approval.

## Incremental Roadmap

Recommended order for automation growth:

1. stabilize the review-and-closeout agent
2. enable closeout action mode for verified merged tasks
3. add proposal triage routine
4. add code-review sweep for validation-heavy PRs
5. add security sweep
6. add release-readiness review agent

This keeps the system useful without jumping too quickly into broad
automation.

## Governance Rule

Automation may reduce maintainer routine, but it must not dilute scientific or
repository governance.

APL should be able to say:

- which instruction file was used;
- which deterministic checks ran;
- which actions were only recommendations;
- which actions required explicit human approval.
