# Atomic Yb/Sr Source-Limited Consistency Memory Card

- Task: `TASK-0767`
- Campaign: `atomic-clock-residuals`
- Type: source-limited consistency / negative-memory card (no `RESULT`/`PRED`)
- Decision lineage: `TASK-0456` (diagnostic) → `TASK-0756`
  (`CONSISTENCY_NEGATIVE_MEMORY_CARD` route) → `TASK-0767` (this card)
- Review tier: `none`

## Purpose

This card preserves the completed Beloy 2021 / Nemitz 2016 Yb/Sr cross-source
consistency diagnostic as durable, source-limited scientific memory **without**
promoting it to a canonical result. It records why rerunning the same two-row
metric is not useful and what would have to change before the Atomic Yb/Sr
benchmark axis is reopened.

It computes no new metrics, fetches no sources, and edits no data rows,
covariance files, claims, knowledge, or result artifacts.

## Diagnostic Recorded

The diagnostic compared two independent absolute Yb/Sr frequency-ratio rows
under an exploratory diagonal-only covariance assumption
(`COV_DIAGONAL_ONLY_DECLARED`):

| Role | Source | Row id | Ratio value | Total 1σ (fractional) |
| --- | --- | --- | --- | ---: |
| Reference | Beloy 2021 / BACON | `ACR-0001-ROW-003` | `1.2075070393433378482` | `6.8e-18` |
| Target | Nemitz 2016 / RIKEN | `ACR-0002-ROW-001` | `1.207507039343337749` | `4.56e-17` |

| Comparison quantity | Value |
| --- | ---: |
| Absolute difference (ref − target) | `9.92e-17` |
| Fractional difference | `8.215e-17` |
| Combined 1σ (diagonal-only) | `5.567e-17` |
| `|z|` score | `1.7819` |
| No-tension `|z|` threshold | `2.0` |
| Uncertainty dominance ratio (target/reference) | `6.71×` |

Verdict recorded by the diagnostic:
`CONSISTENT_WITHIN_UNCERTAINTY_EXPLORATORY_SOURCE_LIMITED`.

Source evidence (committed only): `agent_runs/AGENT-RUN-0071/metrics.json`,
`agent_runs/AGENT-RUN-0071/report.md`, and the benchmark review note
[`atomic-yb-sr-cross-source-consistency-benchmark.md`](atomic-yb-sr-cross-source-consistency-benchmark.md).

## Why This Is Not Promoted

The reading "the two independent Yb/Sr ratios are consistent at the probed
precision" is defensible only as an exploratory, source-limited diagnostic. The
publication blockers from the route decision
([`atomic-yb-sr-benchmark-result-path-decision.md`](atomic-yb-sr-benchmark-result-path-decision.md))
remain:

- **Two rows only.** One row per source; this is not a population-level
  consistency test.
- **Uncertainty dominance.** The Nemitz 2016 total uncertainty dominates the
  comparison by about `6.7×`, so the test is limited by Nemitz and does **not**
  exercise Beloy's finer (≈18-digit) precision.
- **Source-limited precision.** The probed precision is set by the weaker row.
- **Covariance boundary.** The off-diagonal term is assumed zero. Beloy/BACON
  and Nemitz/RIKEN are fully independent (no shared clock, comb, network link, or
  geopotential systematic), so the diagonal-only assumption is defensible for an
  exploratory diagnostic but is explicitly **not** a headline covariance model.

## No-Claim Wording

This memory card is **not** any of the following, and must not be cited as such:

- not a constants-drift result;
- not a new-constant or new-physics result;
- not an anomaly detection or anomaly explanation;
- not a prediction (`PRED-*`) entry;
- not a canonical `RESULT-*` artifact;
- not a `CLAIM-*` or `KNOW-*` promotion.

It is durable negative/no-tension memory: Beloy and Nemitz are consistent within
the declared diagonal-only uncertainty model at the probed, Nemitz-limited
precision, and that outcome should prevent repeated reruns of the same two-row
diagnostic.

## Do-Not-Repeat Boundary

- Do **not** rerun the Beloy/Nemitz two-row metric as a fresh benchmark task; the
  result is already recorded here.
- Do **not** convert this diagnostic into a `RESULT`, prediction, or claim under
  the current two-row, Nemitz-dominated, diagonal-only conditions.

## Reopen Condition (Future Gate)

Reopen the Atomic Yb/Sr benchmark axis only when at least one of the following
materially reduces the current blocker:

1. a finer-precision **independent absolute Yb/Sr source row** that does not let
   the Nemitz uncertainty dominate the comparison (i.e., moves the axis beyond
   two source rows or tests Beloy-level precision); **or**
2. a **maintainer-approved aggregation contract** (e.g., an admissible third
   absolute-ratio source, or a reviewed off-diagonal covariance model) that
   changes the two-row / source-limited / diagonal-only conditions.

Until then, Pizzocaro-class material remains diagnostic-only and does not reduce
the absolute-row benchmark from two sources to three (see
[`atomic-pizzocaro-yb-sr-extraction-ledger-gate.md`](atomic-pizzocaro-yb-sr-extraction-ledger-gate.md)).

## Output Routing

- Task verdict: `not_applicable` (negative-memory packaging; no new metric).
- Canonical destination: this card,
  `docs/reviews/atomic-yb-sr-source-limited-consistency-memory-card.md`.
- Review tier: `none`.
- Gate A status: `not_attempted` (blocked by underpowered rows, source-limited
  precision, and exploratory diagonal-only covariance).
- Gate B status: `not_applicable`.
- Claim impact: none; no claim created or changed.
- Knowledge impact: none; no knowledge entry created or changed.
- Result artifact impact: none; no `RESULT`/`PRED` created, and no data,
  covariance, claim, or knowledge file edited.
- Limitations / blockers: two-row population, Nemitz-dominated uncertainty
  (`~6.7×`), and diagonal-only covariance. Promotion stays blocked pending the
  reopen condition above; any future `RESULT` package needs a maintainer-approved
  Gate A path and scope wording. See
  [`docs/result-promotion-protocol.md`](../result-promotion-protocol.md).
