# Atomic Synthetic Cross-Source Benchmark Dry Run

**Task:** `TASK-0488`  
**Campaign:** `atomic-clock-residuals`  
**Fixture:** `data/atomic_clocks/synthetic_cross_source_dry_run.yaml`  
**Status:** fabricated values only; no real benchmark unblocked

## Scope

This dry run exercises the Atomic-Clock Residuals cross-source benchmark
plumbing with fabricated rows only. It does not read, compare, approximate, or
copy real Beloy or Nemitz values. It does not compute a real Yb/Sr consistency
metric, fit constants drift, create `RESULT-*` artifacts, register
predictions, or promote claims.

## Fixture Design

The fixture contains three fabricated Yb/Sr-shaped rows:

| Row | Role | Covariance state |
| --- | --- | --- |
| `ACLOCK-XSR-SYN-ROW-0001` | synthetic source-alpha anchor | `COV_SYNTHETIC_DIAGONAL_ONLY_DECLARED` |
| `ACLOCK-XSR-SYN-ROW-0002` | synthetic source-beta comparator | `COV_SYNTHETIC_SOURCE_DERIVED_PSD_APPROX` |
| `ACLOCK-XSR-SYN-ROW-0003` | synthetic shifted-ratio negative control | synthetic negative-control family |

Every row is `row_class: synthetic_dry_run`, has
`classification.synthetic: true`, uses `holdout.split: synthetic_only`, and
preserves limitation text stating that the value is fabricated.

## Loader Checks

`load_atomic_clock_synthetic_cross_source_dataset()` validates that:

- the fixture is tied to `TASK-0488`;
- `contains_real_clock_values` is false;
- benchmark and claim-promotion flags are false;
- at least two fabricated frequency-ratio rows are present;
- every row role is synthetic and does not name real Beloy/Nemitz sources;
- covariance labels use the `COV_SYNTHETIC_*` namespace;
- the fixture explicitly says it does not unblock real benchmark work.

## Why This Does Not Unblock Real Atomic Benchmark Work

The dry run is plumbing-only. It preserves the real blockers for
`TASK-0456`:

- real second-source rows are not added by this fixture;
- real holdout/no-peek assignment is not performed;
- real covariance policy acceptance is not exercised by fabricated values;
- no real source artifact, ratio, or uncertainty comparison occurs.

## Verdict

`VALID_IN_RANGE`

The synthetic cross-source fixture and targeted tests exercise row roles,
covariance-state labels, and no-peek flags without weakening the real Atomic
source-readiness boundary.

## Output Routing Summary

- task verdict: `VALID_IN_RANGE`;
- canonical destination: synthetic fixture, loader helper, tests, and this
  review note;
- review tier: `none`;
- Gate A status: not attempted;
- Gate B status: not attempted;
- claim impact: no claim change;
- knowledge impact: no knowledge change;
- result artifact impact: no `results/` artifacts modified;
- limitations / blockers: real Atomic benchmark work remains blocked until
  source, loader, holdout, and covariance gates pass on committed real rows.
