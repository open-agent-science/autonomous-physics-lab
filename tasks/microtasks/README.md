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
