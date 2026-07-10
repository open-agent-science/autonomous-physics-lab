# Atomic Monitor-Only Reopen-Trigger Ledger

**Task:** `TASK-0990`
**Campaign:** `atomic-clock-residuals`
**Task verdict:** `MONITOR_LEDGER_RATIFIED`
**Review date:** 2026-07-10

## Scope

This ledger ratifies the Atomic campaign's monitor-only posture after the
source-limited `171Yb/87Sr` memory card, the McGrew/NIST blocker, the
Pizzocaro aggregation contract, the `171Yb/88Sr` isotope-mismatch blocker, and
the multi-species go/no-go contract.

It is value-blind. It fetches or transcribes no ratio values, derives no
cross-isotope ratios, runs no metrics, fits no drift, and creates no `RESULT`,
`PRED`, `CLAIM`, or `KNOW` artifact.

## Current Boundary

The committed Atomic memory remains a two-row direct `171Yb/87Sr` diagnostic:
Beloy 2021 / BACON and Nemitz 2016 / RIKEN. That memory is durable
source-limited no-tension memory only. It does not authorize repeated metric
runs, constants-drift wording, new-constant wording, anomaly wording, or result
promotion.

The standing posture is `KEEP_MONITOR_ONLY` until one of the admissible
source-trigger routes below is satisfied before any value-bearing row curation.

## Admissible Reopen Triggers

| Route | Trigger before row curation | Evidence required | Allowed future task shape |
| --- | --- | --- | --- |
| F1 direct `171Yb/87Sr` | A primary post-2021 direct absolute `171Yb/87Sr` publication with lineage distinct from Beloy/BACON, Nemitz/RIKEN, Pizzocaro/INRIM, and McGrew/NIST | Version-of-record artifact, exact isotope and transition semantics, row-of-record citation, clock/comb/network lineage, uncertainty budget, covariance and dependence notes, epoch metadata, rights, and holdout/no-peek role | Source-artifact pinning, direct-row readiness gate, then an ACR row-curation task. A benchmark task is allowed only after the row gate passes. |
| F2 separate `171Yb/88Sr` | A second independent primary `171Yb/88Sr` source, separate from the Morzynski et al. 2024 candidate, with recoverable uncertainty and lineage semantics | The same source-artifact, lineage, epoch, uncertainty, covariance, and rights evidence, plus an explicit family label proving it is not the F1 axis | Maintainer-approved separate `171Yb/88Sr` source-memory or consistency-axis task. It must not modify the committed `171Yb/87Sr` diagnostic. |
| F3 derived or harmonized multi-axis | All cumulative inputs from the multi-species contract are committed, including conversion input of record, covariance propagation policy, epoch alignment, independence accounting, uncertainty-budget visibility, and schema/row-class support | A maintainer decision opening a derived-row class, conversion provenance, correlation fields, and a rule for shared conversion-input covariance before values are processed | Protocol-first derived-axis task, followed only later by value-bearing row work if the schema and covariance gates pass. |
| Pizzocaro aggregation route | A source-backed absolute Pizzocaro summary, or a maintainer-approved repository aggregation contract with aggregation-capable covariance, absolute anchor, dependence accounting, and schema admission | Source-pinned absolute mapping or approved generalized least-squares contract, complete window inclusion rule, admissible covariance, anchor uncertainty, and row-class decision | Aggregation or row-class gate. It cannot count the ten windows as ten independent rows and cannot reduce the F1 blocker until admitted. |

## Inadmissible Shortcuts

- Do not relabel `171Yb/88Sr` as `171Yb/87Sr`.
- Do not derive an `87Sr` row from an `88Sr` row through recommended-frequency
  values unless the F3 route is explicitly opened first.
- Do not seed a benchmark axis from a single `171Yb/88Sr` source.
- Do not append McGrew/NIST or Pizzocaro material as a third direct
  `171Yb/87Sr` row under the existing evidence.
- Do not count Pizzocaro windows as independent source rows.
- Do not use diagonal-only or sensitivity-only covariance as an aggregation
  covariance of record.
- Do not rerun the Beloy/Nemitz two-row metric as a new benchmark task under
  the current evidence.
- Do not fit constants drift, create anomaly wording, or promote `RESULT`,
  `PRED`, `CLAIM`, or `KNOW` artifacts from this ledger.

## Evidence Needed Before Any Row Curation

Every future row-curation proposal must identify:

- the observable family (`F1`, `F2`, `F3`, or an approved aggregation route);
- the exact isotope pair and clock transitions;
- the version-of-record artifact and row locator;
- clock, comb, network, institution, and transfer-chain independence;
- uncertainty-budget components and covariance/dependence semantics;
- campaign epoch or window metadata;
- direct, derived, review-summary, or approved aggregate row class;
- rights and attribution status;
- holdout/no-peek role before any metric is run.

Missing evidence keeps the campaign in monitor-only source memory. It does not
authorize values-first curation.

## Output-Routing Summary

- **Canonical destination:** this source-trigger ledger,
  `docs/reviews/atomic-monitor-only-reopen-trigger-ledger.md`, plus the
  campaign-page pointer.
- **Review tier:** none.
- **Gate A / Gate B:** not applicable.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Data / result impact:** none; no data rows, metrics, result artifacts, or
  prediction artifacts are created or changed.
- **Publication blocker:** none for this ledger. Atomic remains monitor-only
  until one admissible trigger above is satisfied and authorized through a
  future task.
