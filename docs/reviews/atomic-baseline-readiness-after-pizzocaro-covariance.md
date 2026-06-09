# Atomic Baseline-Readiness Gate After Pizzocaro Covariance Approximation

**Task:** `TASK-0667`
**Campaign:** `atomic-clock-residuals`
**Mode:** planning only (scientific validation gate)
**Gate verdict:** `PINNED_DATASET` — not `BASELINE_READY`; second Yb/Sr benchmark row still missing

## Scope

This gate reruns the Atomic baseline-readiness decision now that `TASK-0666`
landed the Pizzocaro VLBI source-derived PSD covariance approximation. It decides
whether the committed Beloy / Pizzocaro / Nemitz / Lange source surfaces support a
narrow Yb/Sr cross-source consistency benchmark (`TASK-0456`), using only
committed artifacts. It runs no cross-source metric, fits no constants drift, adds
no row, creates no result, and promotes no claim.

## Evidence Reviewed

| Input | Role |
| --- | --- |
| `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/vlbi_source_derived_psd_covariance_approximation.yaml` | `TASK-0666` covariance artifact (the new evidence). |
| `docs/reviews/atomic-pizzocaro-source-derived-psd-covariance.md` | `TASK-0666` review; verdict `PSD_APPROXIMATION_COMMITTED_SENSITIVITY_ONLY`. |
| `docs/reviews/atomic-pizzocaro-vlbi-row-aggregation-covariance-gate.md` | `TASK-0627`; `BLOCKER_PRESERVED`, no single summary row. |
| `docs/reviews/atomic-first-benchmark-covariance-policy.md` | `TASK-0486` covariance-state policy. |
| `docs/reviews/atomic-baseline-readiness-gate-after-nemitz-loader-holdout.md` | `TASK-0455` prior gate; `PINNED_DATASET`. |
| `docs/reviews/atomic-cross-source-benchmark-blocker-map.md` | `TASK-0653` blocker map. |
| `data/atomic_clocks/` committed rows | Only `acr-0001` Beloy 2021 exists. |
| `docs/campaigns/atomic-clock-residuals.md` | Campaign maturity framing. |

## What TASK-0666 Changed

`TASK-0666` committed a deterministic Pizzocaro VLBI covariance approximation over
the ten committed campaign windows. Both clock-correlation sensitivity bounds
(`rho_clock = 1` fully correlated and `rho_clock = 0` uncorrelated) pass the PSD
check. Under the `TASK-0486` policy this clears the bar for
`COV_SOURCE_DERIVED_PSD_APPROX` — **sensitivity-only** correlated metrics with a
mandatory `approximate covariance` label — but explicitly **not**
`COV_EXACT_COMMITTED`.

Crucially, the artifact is a covariance matrix, **not a benchmark row**. It
records `aggregates_windows: false`, `writes_acr_benchmark_rows: false`,
`benchmark_allowed: false`, and `sensitivity_only: true`. It does not resolve the
`TASK-0627` aggregation blocker: it neither collapses the ten correlated windows
into one summary row nor admits them as independent benchmark rows.

## Source-Surface State

| Source | Family | Committed benchmark row? | Covariance state | Benchmark role |
| --- | --- | --- | --- | --- |
| Beloy 2021 / BACON (`acr-0001`) | Yb/Sr direct ratio | Yes — 3 sandbox direct rows, manifest roles assigned | `COV_SOURCE_DERIVED_PSD_APPROX` (sensitivity-only) | `cross_source_reference` (ready anchor) |
| Pizzocaro 2020 / INRIM (VLBI) | Yb/Sr direct ratio | **No** — per-window diagnostic ledger + PSD covariance approximation only | `COV_SOURCE_DERIVED_PSD_APPROX` available, but no admitted row | Most-developed `cross_source_target` candidate; row admission undecided |
| Nemitz 2016 / RIKEN | Yb/Sr direct ratio | **No** `acr-0002` — source artifact pinned, rows blocked | not applicable until a row exists | Alternative `cross_source_target` |
| Lange/PTB Yb+ E3/Cs | Yb+ (separate family) | No | not applicable | Does **not** unblock the Yb/Sr benchmark |

The committed-row inventory is unchanged from the prior gate: `acr-0001` (Beloy)
is still the **only** value-bearing direct-ratio row. No `acr-0002` exists.

## Classification

`PINNED_DATASET` — **not** `BASELINE_READY`.

- Not `BASELINE_READY`: the first Yb/Sr consistency benchmark binds a
  `cross_source_reference` (Beloy) to a `cross_source_target` second Yb/Sr row.
  No second admissible Yb/Sr benchmark row is committed. Beloy alone is
  `COV_SINGLE_ROW_NO_CROSS_ROW_RISK` and yields no aggregate benchmark verdict.
- Not `COVARIANCE_BLOCKED` (for the Pizzocaro windows): `TASK-0666` cleared the
  covariance dimension to `COV_SOURCE_DERIVED_PSD_APPROX` (sensitivity-only).
  Covariance is no longer the load-bearing blocker.
- Not `SOURCE_BLOCKED` in the strong sense: Beloy rows are pinned, Pizzocaro
  source artifacts + per-window ledger + covariance approximation are committed,
  and Nemitz source is pinned. A viable curation route exists.

**Load-bearing remaining blocker:** `SECOND_YB_SR_BENCHMARK_ROW_MISSING`. The
Pizzocaro windows are not yet admitted as benchmark rows (`TASK-0627` aggregation
blocker still open; `TASK-0666` did not aggregate), and Nemitz `acr-0002` is not
committed.

Secondary standing constraints: any eventual Beloy↔Pizzocaro metric is
**sensitivity-only** (both sides `COV_SOURCE_DERIVED_PSD_APPROX`) and must report
diagonal-only comparators side by side with the `approximate covariance` label;
it cannot be presented as a full-covariance or paper-published result.

## Decision For TASK-0456

**Do not start `TASK-0456` yet.** It remains correctly `BLOCKED`. This gate does
not classify Atomic as `BASELINE_READY`, so it does not authorize the benchmark
shape. `TASK-0456`'s unblock condition is unchanged in substance (requires
`BASELINE_READY` plus a committed second Yb/Sr row), so its task file is left as
is.

## Single Next Task Recommendation

The shortest path to a (sensitivity-only) first benchmark is to **decide
Pizzocaro window→benchmark-row admissibility** now that the covariance
approximation exists:

- a narrow task that decides whether the committed per-window ledger plus the
  `COV_SOURCE_DERIVED_PSD_APPROX` matrix can support either (a) a single frozen
  Pizzocaro summary row via a committed aggregation recipe, or (b) a per-window
  Beloy↔Pizzocaro consistency surface, both **sensitivity-only**; or preserve the
  aggregation blocker if neither is defensible.

If that decision rejects Pizzocaro aggregation, the alternative single next task
is **Nemitz 2016 row curation** (commit `acr-0002`) under the version-of-record,
campaign-window, and uncertainty-transcription gates. Lange/PTB stays a separate
Yb+ family and does not unblock this benchmark.

## Limitations

- Committed repository evidence only; no live fetch, no value transcription, no
  metric computation.
- Does not aggregate the Pizzocaro windows or admit them as rows; that decision
  is delegated to the recommended follow-up.
- Does not edit `TASK-0456` (still `BLOCKED`) or the campaign page; the maturity
  class (`PINNED_DATASET`) is unchanged, and the campaign already lists the Yb/Sr
  benchmark under unsafe tasks.
- The covariance approximation is sensitivity-only; no exact-covariance or
  full-correlated benchmark output is authorized.

## Output-Routing Summary

- **Task verdict:** `not_applicable` for a scientific claim; readiness
  classification is `PINNED_DATASET` (not `BASELINE_READY`).
- **Canonical destination:** this review note,
  `docs/reviews/atomic-baseline-readiness-after-pizzocaro-covariance.md`.
- **Review tier:** `none`; no `RESULT-*` or `PRED-*` artifact.
- **Gate A status:** not attempted (no rows or metrics). **Gate B:** not
  applicable.
- **Claim impact:** no claim change; no constants-drift, consistency, or anomaly
  statement.
- **Knowledge impact:** no knowledge change.
- **Result artifact impact:** no `results/` artifact created or modified.
- **Publication blocker:** the first Yb/Sr benchmark stays blocked on a second
  admissible Yb/Sr benchmark row (Pizzocaro window→row aggregation decision, or
  Nemitz `acr-0002` curation). Covariance is resolved as sensitivity-only; it is
  no longer the blocker.
