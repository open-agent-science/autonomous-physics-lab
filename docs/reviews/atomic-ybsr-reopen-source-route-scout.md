# Atomic Yb/Sr Reopen Source Route Scout

Task: `TASK-0780`
Campaign: `atomic-clock-residuals`
Mode: planning-only source / aggregation route scout
Route checked: Pizzocaro 2020 / INRIM VLBI Yb/Sr diagnostic surface
Classification: `AGGREGATION_CONTRACT_NEEDED`
Operational decision: `DO_NOT_REOPEN_NOW`
Review date: 2026-06-18

## Scope

This scout checks exactly one route against the Atomic Yb/Sr reopen condition:
whether the committed Pizzocaro VLBI source surface can reduce the current
Beloy/Nemitz two-row, source-limited, Nemitz-dominated blocker.

It uses committed repository evidence only. It does not fetch live sources,
copy values, add rows, aggregate Pizzocaro windows, rerun Beloy/Nemitz metrics,
fit constants drift, or create `RESULT`, `PRED`, `CLAIM`, or `KNOW` artifacts.

## Inputs Reviewed

| Input | Role |
| --- | --- |
| `docs/reviews/atomic-yb-sr-source-limited-consistency-memory-card.md` | Reopen condition and do-not-repeat boundary for the completed Beloy/Nemitz diagnostic. |
| `docs/reviews/atomic-yb-sr-benchmark-result-path-decision.md` | Result-path decision: preserve no-tension memory, no result promotion. |
| `docs/reviews/atomic-pizzocaro-yb-sr-extraction-ledger-gate.md` | Current Pizzocaro extraction ledger and ACR-row blocker. |
| `docs/reviews/atomic-pizzocaro-row-admissibility-after-psd-covariance.md` | Post-PSD decision preserving the aggregation blocker. |
| `docs/notes/atomic-clock-source-candidates.md` | Generic direct, derived, and review-summary source boundaries. |
| `data/atomic_clocks/source_manifest.yaml` | Current manifest status for Beloy, Nemitz, Pizzocaro, and Lange/PTB source families. |

## Route Assessment

The Pizzocaro route is attractive because it is already source-pinned and has a
rich diagnostic surface:

- Zenodo source artifacts are pinned with provenance and per-file hashes.
- Ten VLBI campaign windows are mapped in the committed diagnostic ledger.
- A source-derived PSD covariance approximation exists for sensitivity-only
  diagnostics.
- The observable-harmonization contract permits diagnostic residual-axis work.

Those facts improve diagnostic readiness, but they do not satisfy the reopen
condition from the Atomic memory card. The load-bearing blockers remain:

| Reopen requirement | Pizzocaro route state | Decision |
| --- | --- | --- |
| Independent absolute Yb/Sr source row | Not present. Pizzocaro windows are fractional-deviation diagnostic surfaces, not admitted absolute ACR rows. | blocked |
| Finer precision that tests beyond Nemitz dominance | Not established for an admissible benchmark row. No third absolute row exists to compare on the same axis. | blocked |
| Maintainer-approved aggregation contract | Not present. Existing reviews explicitly forbid collapsing ten correlated VLBI windows into one row. | needed |
| Observable harmonization for Beloy-comparable surface | Diagnostic-only residual-axis contract exists, but no benchmark-row admission. | not enough |
| Permission to rerun metrics or promote result | Not in scope and not authorized. | blocked |

## Classification

Route classification: `AGGREGATION_CONTRACT_NEEDED`.

The Pizzocaro surface cannot reopen Atomic Yb/Sr benchmark work as-is. It could
become useful only if maintainers approve a repository-owned aggregation or
observable-harmonization contract that defines:

1. whether the ten correlated VLBI windows may be summarized at all;
2. how uncertainty and cross-window covariance propagate into any summary;
3. whether the resulting surface is an ACR absolute-ratio row, a residual-axis
   diagnostic, or a sensitivity-only comparator;
4. why that route materially reduces the two-row/source-limited blocker without
   silently treating diagnostic windows as independent benchmark rows.

Until such a contract exists, the operational decision is `DO_NOT_REOPEN_NOW`.

## Stop Condition

Do not open a new Atomic benchmark task from this route. Do not rerun the
Beloy/Nemitz two-row diagnostic. Do not add Pizzocaro ACR rows. Do not promote
result, prediction, claim, or knowledge artifacts.

Allowed future work is narrower:

- a maintainer-scoped aggregation-contract review for Pizzocaro, if the
  maintainer wants to decide the ten-window aggregation question explicitly; or
- a separate source scout for a new independent absolute Yb/Sr source row whose
  publication surface already matches the ACR direct-ratio schema.

## Output Routing

- Task verdict: `AGGREGATION_CONTRACT_NEEDED` with `DO_NOT_REOPEN_NOW`
  operational routing.
- Canonical destination:
  `docs/reviews/atomic-ybsr-reopen-source-route-scout.md`.
- Review tier: `none`.
- Gate A status: not attempted; no result or prediction artifact.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Source-readiness impact: Pizzocaro remains diagnostic-only and cannot reduce
  the current Beloy/Nemitz blocker without a maintainer-approved contract.
- Publication blocker: no admissible third absolute Yb/Sr row and no approved
  aggregation contract.

## Limitations

- This scout evaluated one route only, as required; it is not a broad literature
  search for new Yb/Sr sources.
- It used committed repository evidence only.
- It did not inspect or transcribe new source values.
- It does not rule out a future Pizzocaro contract; it rules out reopening the
  benchmark under the current committed contracts.
