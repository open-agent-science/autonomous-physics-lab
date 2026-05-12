# Post-AME2020 Nuclear Time-Split Benchmark Review

**Task:** `TASK-0188`
**Agent run:** `AGENT-RUN-0007`
**Status:** activation-guard dry run
**Boundary:** no active benchmark metrics

## Summary

`TASK-0188` is now represented by deterministic benchmark helper code and a
reviewable agent-run artifact, but the post-AME2020 benchmark is not activated.

The reason is intentional: `TASK-0187` committed a reviewed source manifest,
not row-level holdout values. The manifest explicitly says that active
time-split scoring requires a later reviewed row-level import with source
artifact checksum, unit mapping, measured/extrapolated flags, and row-level
exclusion reasons.

## What Was Implemented

- `physics_lab/registry/post_ame2020_holdout.py` defines:
  - metric calculation for future row-level time-split rows;
  - activation assessment for the post-AME2020 source manifest;
  - a frozen `HYP-PROPOSAL-0021` candidate specification;
  - a mutation guard that rejects post-hoc formula changes.
- `AGENT-RUN-0007` records the dry-run activation state.
- Tests cover metric calculation, mutation rejection, inactive source-manifest
  state, and the committed dry-run metrics artifact.

## What Was Not Done

No row-level post-AME2020 masses were committed.

No frozen baseline, sandbox candidate, or comparator was evaluated on
post-AME2020 rows.

No canonical result, claim, accepted knowledge note, or dataset was promoted.

## Current Verdict

`INCONCLUSIVE`

This is a correct conservative result for the current repository state. It
prevents APL from accidentally treating a source manifest as a benchmark.

## Required Next Step

Commit a reviewed row-level holdout dataset:

`data/nuclear_masses/post_ame2020_holdout.yaml`

That dataset must include:

- source artifact checksum;
- extraction method;
- exact unit mapping;
- measured versus extrapolated flags;
- AME2020 comparison flags;
- exclusion reasons for rows not included in primary scoring.

Only after that import can active TASK-0188 metrics be computed and reviewed.
