# Reproduction Benchmark Artifact Shape

Task: `TASK-0048`  
Status: draft documentation note for maintainer review

## Purpose

APL now needs two benchmark artifact shapes:

- fit-oriented benchmark artifacts for workflows like pendulum discovery and
  damped-oscillator verification;
- reproduction-style benchmark artifacts for explicit-dataset comparisons such
  as the first charged-lepton Koide benchmark.

This note explains when to use the reproduction-style shape instead of forcing
small explicit-dataset benchmarks into train/test fit semantics.

## Use Fit-Oriented Artifacts When

Use the existing fit-style shape when the benchmark genuinely has:

- candidate models or formulas to rank;
- train/test or in/out-of-sample split semantics;
- a best model chosen from a score table;
- per-model score rows in a leaderboard.

That remains the correct shape for:

- pendulum formula discovery;
- pendulum gauntlet runs;
- damped-oscillator regime verification as currently implemented.

## Use Reproduction-Style Artifacts When

Use the reproduction-style shape when the benchmark is primarily:

- an explicit dataset comparison;
- a reproduction of a declared target quantity;
- a holdout-style benchmark without a fitted model leaderboard;
- a source-aware verification task where the key output is the gap between an
  observed quantity and a declared reference value.

That is the right shape for:

- charged-lepton Koide reproduction;
- historical tau holdout benchmarking;
- future explicit-dataset particle-mass checks that compare one computed
  quantity against one or more declared targets.

## Experiment Shape

Reproduction-style experiment specs should:

- reference explicit dataset inputs via `data.dataset_path`;
- describe the dataset kind instead of reusing amplitude-range or time-range
  shapes;
- use a comparator-oriented method rather than pretending to fit candidate
  models;
- declare one or more `comparison_targets`.

## Result Shape

Reproduction-style result artifacts should report:

- `comparison_summary` entries for each declared target;
- explicit observed and reference values;
- absolute and relative differences;
- an `uncertainty_summary` describing how uncertainty was propagated.

They should not be forced to invent:

- `train_range`;
- `test_range`;
- `best_model_id`;
- fit-oriented `scores` arrays.

## Backward Compatibility Rule

This new reproduction-style artifact shape does not replace the fit-oriented
shape. It lives alongside it.

Contributors should choose the artifact shape that matches the actual benchmark
semantics. If a task does not have a real model-ranking workflow, it should not
pretend to have one just to satisfy an older schema shape.
