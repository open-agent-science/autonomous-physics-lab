# Agent Run AGENT-RUN-0007 - Post-AME2020 Time-Split Benchmark Dry Run

## Scope

`TASK-0188` asks for a post-AME2020 time-split benchmark for the frozen nuclear
baseline and `HYP-PROPOSAL-0021`. The current repository has a reviewed source
manifest from `TASK-0187`, but it does not yet have a committed row-level
post-AME2020 holdout dataset.

This run therefore implements the benchmark guard and records an inconclusive
activation dry run.

## Inputs

- `data/nuclear_masses/post_ame2020_sources.yaml`
- `agent_runs/AGENT-RUN-0006/metrics.json`
- `hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0021-shell-dual-heavy-anchor-odd-a.yaml`
- `experiment_proposals/nuclear-mass/EXP-PROPOSAL-0005-nuclear-mass-sandbox-batch.yaml`
- `docs/nuclear-mass-robustness-gate.md`

## Activation Result

The source manifest status is `reviewed_source_manifest`, but:

- `row_level_holdout_dataset_committed` is `false`;
- `time_split_holdout_active` is `false`;
- `data/nuclear_masses/post_ame2020_holdout.yaml` does not exist.

Result:

`NOT_ACTIVATED_SOURCE_MANIFEST_ONLY`

No baseline or candidate metrics are computed against post-AME2020 rows.

## Candidate Freeze

The future time-split candidate remains frozen as:

```text
HYP-PROPOSAL-0021
r_corr = c1*m2 + c2*mh + c3*oa
parameter_count = 3
```

The helper rejects post-hoc formula mutation before a future reveal.

## Split-Sensitivity Context

`AGENT-RUN-0006` remains the current replay context:

- same-shape splits improved: `28/48`;
- regressed: `13/48`;
- tied: `7/48`;
- worst `delta_mae_mev`: `0.9480738911860487`;
- classification: `split_sensitive_partial_signal`.

## Verdict

`INCONCLUSIVE`

The benchmark contract is now guarded in code, but the scientific result is not
active until a reviewed row-level post-AME2020 holdout dataset is committed.
