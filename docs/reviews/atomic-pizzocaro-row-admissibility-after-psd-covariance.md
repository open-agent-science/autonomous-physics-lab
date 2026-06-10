# Atomic Pizzocaro Row Admissibility After PSD Covariance

**Task:** `TASK-0686`  
**Campaign:** `atomic-clock-residuals`  
**Decision:** `AGGREGATION_BLOCKER_PRESERVED`  
**Selected route:** option **(c)** — preserve the aggregation blocker  
**Review date:** 2026-06-10

## Scope

This review re-decides Pizzocaro VLBI window→benchmark-row admissibility now
that `TASK-0666` committed the source-derived PSD covariance approximation.
It uses only committed Pizzocaro artifacts, the per-window ledger, the
covariance approximation, and the Atomic covariance policy.

It does not aggregate window values, compute Beloy↔Pizzocaro cross-source
metrics, fit constants drift, add `acr-*.yaml` rows, create results, or promote
claims.

## Inputs Reviewed

| Input | Role |
| --- | --- |
| `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/vlbi_source_derived_psd_covariance_approximation.yaml` | `TASK-0666` PSD approximation artifact |
| `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/vlbi_per_window_diagnostic_ledger.yaml` | ten committed VLBI windows with values and component uncertainties |
| `data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml` | Beloy reference row `ACR-0001-ROW-003` (Yb/Sr) |
| `docs/reviews/atomic-pizzocaro-vlbi-row-aggregation-covariance-gate.md` | `TASK-0627` prior aggregation gate |
| `docs/reviews/atomic-baseline-readiness-after-pizzocaro-covariance.md` | `TASK-0667` baseline-readiness rerun |
| `docs/reviews/atomic-pizzocaro-source-derived-psd-covariance.md` | `TASK-0666` covariance review |
| `docs/reviews/atomic-first-benchmark-covariance-policy.md` | `TASK-0486` covariance states |
| `docs/reviews/atomic-pizzocaro-source-to-row-extraction-ledger.md` | `TASK-0615` row-surface ledger |
| `TASK-0456` | blocked first benchmark consumer |

## What TASK-0666 Changed

`TASK-0666` committed `ACLOCK-PIZZOCARO-VLBI-COV-APPROX-0001` with:

- `covariance_state: COV_SOURCE_DERIVED_PSD_APPROX`
- frozen row order for ten VLBI windows;
- deterministic diagonal and off-diagonal reconstruction from committed
  component uncertainties;
- PSD pass for both `rho_clock = 1` and `rho_clock = 0` sensitivity bounds;
- explicit `sensitivity_only: true`, `aggregates_windows: false`,
  `writes_acr_benchmark_rows: false`.

This resolves the **cross-window covariance reconstruction** gap that
`TASK-0627` recorded as `COV_BLOCKED_SHARED_SYSTEMATICS` for inter-window
combination semantics. It does **not** commit a benchmark row, a summary
aggregate value, or a Beloy↔Pizzocaro comparison metric.

## Option Assessment

The task requires choosing exactly one of three routes.

### Option (a) — single frozen Pizzocaro summary row

**Rejected.**

Reasons:

1. No repository-owned aggregation recipe is committed. The source exposes
   ten correlated VLBI windows, but neither inverse-variance weighting, robust
   averaging, nor Figure 2b summary selection is frozen.
2. `TASK-0666` explicitly sets `aggregates_windows: false` and forbids writing
   cross-window aggregate metrics from this artifact.
3. Figure 2b `Thiswork` VLBI history rows remain
   `SUMMARY_DERIVED_HISTORY_COMPARATOR` surfaces without campaign-window fields;
   they are not admissible as the row-of-record per `TASK-0615`.
4. A single summary row derived from ten correlated windows would still require
   propagating uncertainty through the committed approximation matrix; that
   recipe is not committed as a row-ingestion artifact.

### Option (b) — per-window Beloy↔Pizzocaro consistency surface

**Rejected for benchmark admission in this pass.**

Reasons:

1. Beloy `ACR-0001-ROW-003` publishes an **absolute frequency ratio**
   (`value_kind: frequency_ratio`, campaign aggregate 2017-11 to 2018-06).
2. Pizzocaro VLBI ledger windows publish **fractional frequency-ratio
   deviations** in dimensionless relative units (`value_yb_sr_relative`, e.g.
   `-1.43e-15`), not absolute ratios on the same observable axis.
3. No committed harmonization rule maps Pizzocaro deviation windows to the Beloy
   absolute-ratio axis for a sensitivity-only cross-source comparator.
4. Admitting ten per-window comparisons without that rule would invite
   value-on-value interpretation across incompatible observables, which the
   Atomic campaign and covariance policy forbid.
5. The per-window ledger remains valuable as **diagnostic-only** evidence with
   `COV_SOURCE_DERIVED_PSD_APPROX` for intra-Pizzocaro sensitivity, but that is
   not the same as authorizing a Beloy↔Pizzocaro benchmark surface.

A future task may still define a harmonized per-window consistency surface, but
only after committing the observable mapping and sensitivity-only comparator
contract.

### Option (c) — preserve the aggregation blocker

**Selected.**

The covariance approximation improves source readiness, but the load-bearing
blockers for benchmark row admission remain:

| Blocker | Status after TASK-0666 |
| --- | --- |
| Cross-window shared-systematic covariance | **partially resolved** for sensitivity-only intra-Pizzocaro use (`COV_SOURCE_DERIVED_PSD_APPROX`) |
| Frozen summary aggregation recipe | **still blocked** |
| Committed `acr-0002` (or equivalent) second Yb/Sr benchmark row | **still missing** |
| Beloy↔Pizzocaro observable harmonization | **still blocked** |
| `BASELINE_READY` classification | **not reached** (`PINNED_DATASET` per `TASK-0667`) |

## Decision

`AGGREGATION_BLOCKER_PRESERVED`

Do not commit a Pizzocaro summary row, do not admit per-window rows as
independent benchmark rows, and do not authorize `TASK-0456` from this review.

The committed artifacts now support:

- diagnostic per-window ledger review;
- sensitivity-only intra-Pizzocaro covariance replay via
  `vlbi_source_derived_psd_covariance_approximation.yaml`;
- future row curation only after a separate task commits either aggregation or
  observable-harmonization rules.

Any future Beloy↔Pizzocaro metric must remain **sensitivity-only**, report
**diagonal-only comparators alongside approximate-covariance diagnostics**, and
carry the `approximate covariance` label per `TASK-0486`.

## Implications For TASK-0456

`TASK-0456` remains correctly `BLOCKED`. Its unblock condition is unchanged:
Atomic must reach `BASELINE_READY` with a committed second admissible Yb/Sr
benchmark row. This review does not edit `TASK-0456` because the unblock
condition is substantively the same.

## Single Next Task Recommendation

**Primary path:** Nemitz 2016 `acr-0002` row curation under the existing source
artifact and version-of-record gates. Nemitz uses the same species pair and
absolute-ratio semantics as Beloy, so it is the shortest path to a second
committed Yb/Sr row without Pizzocaro aggregation or observable harmonization.

**Alternative path if Nemitz stays blocked:** a narrow Pizzocaro task that
commits (1) observable harmonization from fractional deviation windows to a
Beloy-comparable residual axis and (2) a frozen sensitivity-only per-window
Beloy↔Pizzocaro comparator contract — still without aggregating the ten windows
into one summary row unless a separate aggregation recipe lands first.

## Limitations

- Committed repository evidence only; no live fetch or value transcription.
- No cross-source metrics computed or interpreted.
- The diagnostic ledger's embedded `covariance.state: COV_BLOCKED_SHARED_SYSTEMATICS`
  predates the `TASK-0666` artifact; downstream consumers should treat the
  committed PSD approximation artifact as the authoritative intra-Pizzocaro
  covariance state for sensitivity-only work.
- No maintainer endorsement of consistency, drift stability, or anomaly wording.

## Output Routing

- Task verdict: `AGGREGATION_BLOCKER_PRESERVED`.
- Canonical destination:
  `docs/reviews/atomic-pizzocaro-row-admissibility-after-psd-covariance.md`.
- Review tier: `none`.
- Gate A status: not attempted; no rows or metrics.
- Gate B status: not applicable.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result artifact impact: no `results/` artifact created or modified.
- Publication blocker: no second admissible Yb/Sr benchmark row; Pizzocaro
  remains diagnostic-only despite committed PSD covariance approximation.
