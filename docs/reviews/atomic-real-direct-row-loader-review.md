# Atomic-Clock Real Direct-Row Loader Review

**Task:** `TASK-0453`
**Domain:** `atomic_clock_residuals`
**Verdict:** `not_applicable` (loader/validation contract; no scientific verdict)
**Evidence class:** deterministic loader + targeted tests, no metrics

## Scope

This task resolves the deterministic real-row loader blocker that `TASK-0401`
identified before the Atomic-Clock Residuals campaign can become
`BASELINE_READY`. It adds a validated loader for committed
`row_class: direct_measurement` rows (the Beloy 2021 / BACON seed,
`data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml`) without changing
the existing synthetic dry-run loader behavior.

The loader is a validation/contract surface only. It does **not** fit drifts,
compute residuals, derive constants constraints, create prediction-registry
entries, write `RESULT` artifacts, or promote claims.

## What Changed

- `physics_lab/engines/atomic_clock_residuals.py`
  - Added `load_atomic_clock_direct_dataset`, with frozen dataclasses
    `AtomicClockDirectRow` and `AtomicClockDirectDataset`.
  - The synthetic loader (`load_atomic_clock_synthetic_dataset`) is unchanged.
- `tests/test_atomic_clock_real_rows.py`
  - Twelve targeted tests against the committed Beloy seed fixture, plus
    cross-checks that the two loaders stay disjoint.
- `data/atomic_clocks/schema.md`
  - Clarified the `source` vs `source_metadata` naming contract.

## Schema Reconciliation Decisions

1. **`source` vs `source_metadata`.** Real direct rows use a `source` block
   (citation, DOI, archive URL, checksum). The synthetic loader uses a
   `source_metadata` block (`source_class: synthetic_rows`). The direct loader
   requires `source` and explicitly rejects a `source_metadata` key on a direct
   row, so the historical naming drift can no longer silently pass.

2. **Required real-row groups.** Each direct row must carry `row_id`,
   `row_class`, `observable_id`, `clock_system`, `reference_system`,
   `observable`, `uncertainty`, `source`, `classification`, `holdout`, and
   `limitations`.

3. **Uncertainty contract.** Each row must provide `uncertainty.total`
   (positive number), `confidence_level_label`, `bound_style`, and
   `covariance_reference`. `covariance_group` is surfaced when present so
   downstream benchmarks can see cross-row shared-clock systematics.

4. **Classification flags.** A direct row must set `direct_measurement: true`
   and `derived_constraint`, `review_summary`, `synthetic` all `false`.
   `derived_constraint` and `review_summary` row classes are rejected by this
   loader so they cannot be silently mixed with direct measurements; they need
   their own explicit ingestion path.

5. **Sandbox boundary enforced at load time.** The loader refuses datasets that
   do not declare `scope.sandbox_only: true`, `scope.benchmark_allowed: false`,
   and `scope.claim_promotion_allowed: false`.

## Validation

```bash
python3 -m ruff check .
python3 -m pytest tests/test_atomic_clock_real_rows.py tests/test_docs_links.py
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
```

## Limitations

- Loads and validates rows only; it computes no residuals, metrics, or fits.
- Direct-measurement only. Derived constraints and review summaries are out of
  scope and intentionally rejected.
- Cross-ratio covariance is not reconstructed; the seed exposes per-clock
  systematic components as informational fields, and the loader surfaces the
  shared `covariance_group` without building a 3x3 matrix.
- Passing this loader is a necessary, not sufficient, condition for
  `BASELINE_READY`. The `TASK-0455` baseline-readiness gate must still run after
  second-source ingestion (`TASK-0452`) and the holdout/no-peek manifest
  (`TASK-0454`).

## Output Routing

- **Verdict:** `not_applicable` (tooling/validation task; no hypothesis tested).
- **Canonical destination:** source-readiness tooling under `physics_lab/` +
  review note under `docs/reviews/`; sandbox-only, no `RESULT`/`PRED`/`CLAIM`.
- **Review tier:** `none` (no tiered artifact published).
- **Gate A/Gate B:** not attempted (no result candidate produced).
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Blockers:** none introduced; removes the deterministic real-row loader
  blocker on the path to `BASELINE_READY`.
