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

When multiple agents may work during the same day, check recent open PRs and
campaign notes before selecting a microtask. Until APL has a dedicated
microtask run registry, avoid taking an item that already appears in an open PR
or recently merged note.

## Repeatable Search Loops

Some scientific work should be intentionally repeatable: an agent proposes a
new formula, dataset slice, threshold, or falsification condition, runs the
deterministic check, and publishes the outcome even if the candidate fails.

For repeatable work, each attempt should record:

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
