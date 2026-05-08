# Scientific Microtask Queues

This directory stores campaign-specific scientific microtask queues for APL.

These queues exist so humans and coding agents can contribute useful
verification-first scientific work in small chunks without inventing a new
canonical task for every narrow subproblem.

## Current Queues

- `pendulum-formula-falsification.yaml`
- `particle-mass-relations.yaml`
- `dimensional-analysis-validator.yaml`
- `thought-experiment-consistency.yaml`
- `diffusion-scaling.yaml`

## Queue Summary

| Queue ID | Campaign Status | Tasks | Low | Medium | High |
|---|---|---|---|---|---|
| diffusion-scaling | planning_only_future_campaign | 5 | 5 | 0 | 0 |
| dimensional-analysis-validator | planning_complete_implementation_pending | 10 | 7 | 3 | 0 |
| particle-mass-relations | active_with_narrow_results | 10 | 5 | 5 | 0 |
| pendulum-formula-falsification | active | 10 | 9 | 1 | 0 |
| thought-experiment-consistency | planning_active | 5 | 2 | 3 | 0 |

## How To Use These Queues

1. Pick one campaign queue.
2. Select one small item or a tightly related batch.
3. Keep the PR within one campaign.
4. Report limitations and claim ceiling explicitly.
5. Mark uncertain results as `REVIEW_NEEDED`.

## What These Queues Are Not

- not canonical `TASK-XXXX` files;
- not evidence by themselves;
- not permission to promote claims;
- not a substitute for benchmark implementation tasks.

## Review Rule

Microtask work should be easy to review.

If a batch is too large to explain quickly, it should probably be split or
turned into a larger canonical task.

## Scaling Readiness

The current queue files are seed queues. For daily multi-agent usage, use the
batching guidance in `docs/agent-scientific-work-mode.md` and the scaling note
in `docs/notes/microtask-scaling-readiness.md`.

Current guidance:

- single-item PRs for interpretation-heavy or source-sensitive work;
- `2-3` item batches for shared formula-family or comparison context;
- `3-5` item batches for homogeneous dataset or challenge-entry additions;
- repeatable formula-search attempts only within one campaign and with
  explicit metrics, novelty check, failure mode, and verdict.

The next infrastructure step is `TASK-0112`, which covers append-only
microtask run/claim records, expanded queues, and repeatable scientific search
loops.
