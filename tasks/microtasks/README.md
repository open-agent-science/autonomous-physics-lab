# Scientific Microtask Queues

This directory stores campaign-specific scientific microtask queues for APL.

These queues exist so humans and coding agents can contribute useful
verification-first scientific work in small chunks without inventing a new
canonical task for every narrow subproblem.

## Current Queues

- `pendulum-formula-falsification.yaml`
- `particle-mass-relations.yaml`
- `nuclear-mass-surface.yaml`
- `dimensional-analysis-validator.yaml`
- `thought-experiment-consistency.yaml`
- `diffusion-scaling.yaml`

## Queue Summary

Refresh this generated table after queue metadata changes:

```bash
python3 scripts/generate_microtask_queue_summary.py
```

Queue items may include `status: completed` or `status: retired` when prior
notes, run records, or newer canonical tasks make them no longer available for
new work. Completed and retired items stay in queue files for traceability, but
agents should pick from the available count in the generated table.

<!-- BEGIN AUTO MICROTASK QUEUE SUMMARY -->

| Queue | Campaign | Campaign Status | Available | Completed | Retired | Risk Levels | Selection Guidance |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| [`diffusion-scaling`](diffusion-scaling.yaml) | diffusion-scaling | `planning_only_future_campaign` | 5 / 5 | 0 | 0 | `low` | Prefer planning, falsification, units, and limitation notes. |
| [`dimensional-analysis-validator`](dimensional-analysis-validator.yaml) | dimensional-analysis-validator | `active_with_validator_and_pilot` | 4 / 11 | 7 | 0 | `low`, `medium` | Prefer new boundary cases, repeatable classification runs, and assumption-explicit examples not already covered by existing notes. |
| [`nuclear-mass-surface`](nuclear-mass-surface.yaml) | nuclear-mass-surface | `active_baseline_and_sandbox_guarded` | 5 / 8 | 1 | 2 | `low`, `medium` | Prefer replay, audit, evidence-card, provenance, and guardrail tasks before any second sandbox batch. |
| [`particle-mass-relations`](particle-mass-relations.yaml) | particle-mass-relations | `active_with_narrow_results` | 6 / 11 | 5 | 0 | `low`, `medium` | Prefer falsification-first, source-aware, and uncertainty-aware items. |
| [`pendulum-formula-falsification`](pendulum-formula-falsification.yaml) | pendulum-formula-falsification | `active` | 7 / 11 | 4 | 0 | `low`, `medium` | Prefer narrow approximation, diagnostics, and wording tasks. |
| [`thought-experiment-consistency`](thought-experiment-consistency.yaml) | thought-experiment-consistency | `planning_active` | 5 / 5 | 0 | 0 | `low`, `medium` | Prefer assumption formalization and invariant mapping. |

<!-- END AUTO MICROTASK QUEUE SUMMARY -->

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

## Run Registry

Use `microtask_runs/` for append-only claim and outcome records. Queue files stay
stable campaign backlogs; routine claims should add run records rather than
rewriting queue entries.

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
- holdout-style attempts should follow
  `docs/blind-holdout-benchmark-protocol.md` with a visible pre-reveal package
  and reveal record.

The current infrastructure step is `TASK-0112`, which adds append-only
microtask run/claim records, expanded queues, and repeatable scientific search
loops.
