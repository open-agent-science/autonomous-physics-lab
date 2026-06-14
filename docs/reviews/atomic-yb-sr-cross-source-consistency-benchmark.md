# Atomic Yb/Sr Cross-Source Consistency Benchmark (Exploratory Diagnostic)

**Task:** `TASK-0456`
**Campaign:** `atomic-clock-residuals`
**Agent run:** `agent_runs/AGENT-RUN-0071/`
**Benchmark verdict:** `CONSISTENT_WITHIN_UNCERTAINTY` — exploratory,
diagonal-only, source-limited. Not a constants-drift result, new-physics
inference, prediction, or canonical result.

## Scope and Authorization

The `TASK-0705` baseline-readiness gate
([atomic-baseline-readiness-after-nemitz-acr0002.md](atomic-baseline-readiness-after-nemitz-acr0002.md))
classified Atomic as `BASELINE_READY` for exactly one narrow shape: an
exploratory diagonal-only Yb/Sr cross-source diagnostic between
`ACR-0001-ROW-003` (Beloy 2021 / BACON) and `ACR-0002-ROW-001`
(Nemitz 2016 / RIKEN). This benchmark runs that single authorized comparison
and nothing broader.

No-peek discipline: the two rows carry the `cross_source_reference` and
`cross_source_target` splits frozen in
`data/atomic_clocks/atomic_holdout_manifest.yaml` before any value was read for
this comparison; no split, exclusion, or axis was tuned after inspecting the
values.

## Method

`scripts/atomic_yb_sr_consistency_diagnostic.py` computes a single normalized
difference (a z-score) between the two independent Yb/Sr ratios:

1. The committed ratio values are read as exact `Decimal` strings. The two
   ratios agree to ~15 leading digits and differ at the ~1e-17 level, which is
   below float64 precision relative to a value near 1.2075, so the difference is
   computed in exact decimal arithmetic rather than from float-parsed values.
2. Each source's published total fractional 1σ uncertainty is converted to an
   absolute uncertainty.
3. Under `COV_DIAGONAL_ONLY_DECLARED` (the sources are independent: no shared
   clock, comb, network link, or geopotential systematic), the combined 1σ is
   the diagonal quadrature sum.
4. `z = (R_reference − R_target) / combined_1σ`.

The `|z| < 2` no-tension threshold and the `>3×` source-limited dominance
threshold were declared in the script before the values were inspected.

## Inputs

| Input | Role |
| --- | --- |
| `data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml` | Beloy `ACR-0001-ROW-003` Yb/Sr reference row. |
| `data/atomic_clocks/acr-0002-nemitz-2016-direct-ratio.yaml` | Nemitz `ACR-0002-ROW-001` Yb/Sr target row. |
| `data/atomic_clocks/atomic_holdout_manifest.yaml` | Frozen no-peek split / row-role policy. |
| `docs/reviews/atomic-baseline-readiness-after-nemitz-acr0002.md` | `TASK-0705` gate that authorized this exploratory diagnostic. |

## Result

| Quantity | Value |
| --- | ---: |
| Beloy 2021 Yb/Sr | `1.2075070393433378482` (total 1σ `6.8e-18` fractional) |
| Nemitz 2016 Yb/Sr | `1.207507039343337749` (total 1σ `4.56e-17` fractional) |
| Difference (Beloy − Nemitz), absolute | `9.92e-17` |
| Difference, fractional | `8.215e-17` |
| Combined 1σ (diagonal-only), absolute | `5.567e-17` |
| `|z|` | `1.782` |
| Uncertainty dominance (Nemitz / Beloy) | `6.71` |

The two independent Yb/Sr ratios agree at `|z| = 1.78`, within the predeclared
`2σ` no-tension threshold. There is no tension at the probed precision.

## Interpretation and Limitations

- The comparison is **source-limited**: the Nemitz 2016 total uncertainty is
  ~6.7× the Beloy 2021 uncertainty and dominates the combined 1σ. The diagnostic
  confirms only that Nemitz 2016 is consistent with Beloy 2021 at Nemitz's
  coarser precision; it does **not** test Beloy's 18-digit precision.
- `COV_DIAGONAL_ONLY_DECLARED` forbids a headline consistency verdict. This is
  reported as exploratory diagnostic evidence carrying the independence banner.
- Two rows only (one per source); this is not a population-level consistency
  test, a constants-drift constraint, or a new-physics search.
- Source PDFs (arXiv preprints and the Nature / Nature Photonics versions of
  record) are not redistributed; only metadata, checksums, and the committed
  values are used. The Nemitz version-of-record drift cross-check
  (`NO_DRIFT`) was performed locally against a non-committed PDF.

## Output-Routing Summary

- **Task verdict:** `PARTIALLY_VALID` (valid exploratory diagnostic, source-limited).
- **Canonical destination:** this review note plus `agent_runs/AGENT-RUN-0071/`
  (`metrics.json`, `report.md`); `TASK-0456` moves to `REVIEW_READY`.
- **Review tier:** `none`; no `RESULT-*` or `PRED-*` artifact.
- **Gate A status:** not attempted. **Gate B status:** not applicable.
- **Claim impact:** no claim change.
- **Knowledge impact:** campaign routing only; no knowledge entry.
- **Result artifact impact:** no `results/` artifact created or modified.
- **Publication blocker:** exploratory diagonal-only and source-limited; a
  canonical Yb/Sr consistency result remains blocked until a finer-precision
  second source narrows the dominance ratio and a maintainer-approved Gate A
  path permits a tiered artifact.
