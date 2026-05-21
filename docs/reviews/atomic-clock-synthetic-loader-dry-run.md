# Atomic-Clock Synthetic Loader Dry Run

**Task:** `TASK-0328`
**Example:** `data/atomic_clocks/synthetic_loader_dry_run.yaml`
**Loader:** `physics_lab/engines/atomic_clock_residuals.py`
**Evidence class:** synthetic-only loader validation

## Scope

This dry run exercises the Atomic-Clock Residuals schema boundary with
fabricated rows only. It does not ingest real frequency ratios, drift
constraints, source values, benchmark outputs, prediction registry entries,
claims, or knowledge artifacts.

## Fixture

The example file contains three synthetic rows:

| Row | Purpose | Class |
| --- | --- | --- |
| `ACLOCK-SYN-ROW-0001` | fabricated direct-ratio-shaped row | `synthetic_dry_run` |
| `ACLOCK-SYN-ROW-0002` | fabricated repeated-comparison-shaped row | `synthetic_dry_run` |
| `ACLOCK-SYN-ROW-0003` | fabricated derived-constraint-shaped row | `synthetic_dry_run` |

Every row has `classification.synthetic: true`, `holdout.split:
synthetic_only`, synthetic source metadata, uncertainty semantics, and a
limitation note. The fabricated values are intentionally not physically
meaningful.

## Loader Checks

The loader validates that:

- the dataset is explicitly tied to `TASK-0328`;
- benchmark and claim-promotion flags are false;
- every row uses `row_class: synthetic_dry_run`;
- direct measurement and review-summary flags are false;
- derived synthetic rows preserve `derived_constraint` metadata;
- required observable, uncertainty, source, holdout, and limitation fields are
  present;
- row IDs are unique.

## Boundary

This PR creates loader mechanics only. It does not make Atomic Clock Residuals
benchmark-ready and does not weaken the source-manifest requirement for future
real rows.

## Verdict

`SYNTHETIC_LOADER_READY`

The fabricated fixture and loader provide a deterministic dry run for future
atomic-clock schema work. Real atomic-clock data remain blocked until a later
source-review task approves provenance, uncertainty semantics, and holdout or
reveal boundaries.
