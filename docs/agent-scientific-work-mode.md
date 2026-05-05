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
