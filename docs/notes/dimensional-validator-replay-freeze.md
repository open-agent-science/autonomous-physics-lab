# Dimensional Validator Replay Freeze

Task: `TASK-0134`
Status: REVIEW_READY

## Root Cause

`EXP-0006/RUN-0006` was recorded as a 50-item MVP benchmark, but the
experiment pointed at the live challenge-set curation file:
`knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml`.

Later microtask and curation work expanded that live file to 70 items. Current
source replay therefore loaded the expanded curation surface and reported
`65/70`, while the canonical stored artifact remained `49/50`. The schema
status issue from the initial audit had already been repaired by allowing the
workflow to express the inconclusive-item tolerance as `PASS`/`FAIL`; the
remaining scientific drift was benchmark-scope drift.

## Prevention Rule

Canonical `EXP-0006` replay now uses a frozen MVP input:
`knowledge/challenge_sets/dimensional_analysis_challenge_set_mvp_50.yaml`.

The live curation file remains available for future challenge-set expansion,
but new entries do not change `RESULT-0007`. Any future benchmark expansion
must be an intentional rebaseline task with a new result surface or an explicit
reviewed update to the experiment contract.

The experiment contract also records:

- `benchmark_scope: frozen_mvp_50`
- `expected_item_count: 50`
- `source_challenge_set_path: ../knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml`

The workflow raises an error if the configured benchmark input no longer
contains the expected number of items.

## Claim Ceiling

The safe claim remains limited to the frozen 50-item MVP benchmark:

> Under the frozen `EXP-0006/RUN-0006` MVP challenge-set scope, the
> dimensional validator agrees with 49 of 50 curated labels.

No claim is made about the expanded live curation surface until a future
benchmark task intentionally validates and packages it.
