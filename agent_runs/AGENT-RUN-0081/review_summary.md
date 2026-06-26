# AGENT-RUN-0081 Review Summary

## What this run is

A BOUNDED computed-DFT transfer benchmark (`TASK-0838`) of the frozen
RESULT-0021 baseline model — the exact unordered non-oxygen cation-pair
train-mean of `formation_energy_per_atom`, with a global-train-mean fallback —
across a chemically-disjoint A-site cation-family split of the committed MD-0002
stable ternary-oxide slice. The split is the route the TASK-0817 scout selected
and the MD-0002 holdout manifest pre-authorizes (`cation_pair_family`).

## Discipline confirmed

- The frozen model and descriptor were imported unchanged from
  `physics_lab/engines/materials_md0002_baseline.py` and fixed BEFORE any
  transfer error was read. No post-hoc descriptor, feature, or hyperparameter
  change was made.
- The disjoint A-site cation-family split, the controls (null / shuffled /
  per-class-median), the shuffle seeds, and the pass/fail margin (frozen model
  must beat the best control by ≥ 0.05 eV/atom on the held-out family in BOTH
  directions) were all declared before any metric was computed.
- MD-0002 rows, the frozen baseline engine, and RESULT-0021 were not edited.

## Result (honest negative)

| Direction | Frozen MAE | Best control | Best control MAE | Margin | Clears ≥0.05? |
| --- | --- | --- | --- | --- | --- |
| hold out `alkaline_earth_transition` | 0.729781 | `null_global_mean` | 0.729781 | 0.0 | no |
| hold out `alkali_transition` | 0.791686 | `per_class_median` | 0.745149 | -0.046537 | no |

The two families share **no** cation pair, so the frozen model falls back to the
global train mean on every held-out row (137/137 and 225/225). In direction 1 it
is therefore numerically identical to the null; in direction 2 it is worse than
the per-class-median control. The frozen cation-pair advantage is
**family-localized** and does NOT transfer across a disjoint A-site cation
family on this computed-DFT slice.

Per the task's honest-stop rule, the negative is recorded; nothing was refit,
re-featured, or re-split to rescue it.

## Determinism / Gate-B replayability

Re-running `scripts/run_materials_md0002_transfer.py` reproduces identical
metrics. The run pins command, code reference, input file hashes, engine
version, and git commit (see metrics.json + the review note). The test
`tests/test_materials_md0002_transfer.py` asserts the committed metrics equal a
fresh deterministic replay.

## Routing

Sandbox only. Review tier `none`. Gate A not eligible (negative transfer). Gate B
replayable but not yet independently replayed. No claim or knowledge change.
