# Atomic Pizzocaro VLBI Row Aggregation Covariance Gate

**Task:** `TASK-0627`
**Campaign:** Atomic Clock Residuals
**Verdict:** `BLOCKER_PRESERVED`

## Scope

This gate reviews the committed Pizzocaro 2020 Yb/Sr VLBI source artifact and
decides whether it can support a benchmark-ready Atomic row, a per-window
diagnostic ledger, or a precise blocker. It uses only committed source
artifacts, does not fetch live data, does not create an Atomic row, and does not
run a cross-source benchmark, constants-drift fit, prediction, result, claim, or
knowledge output.

## Inputs

- `docs/reviews/atomic-pizzocaro-source-to-row-extraction-ledger.md`
- `docs/reviews/atomic-pizzocaro-yb-sr-row-admissibility-gate.md`
- `docs/reviews/atomic-first-benchmark-covariance-policy.md`
- `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/Yb-Sr-ratio-measuremets.csv`
- `physics_lab/engines/atomic_clock_residuals.py`
- `docs/result-promotion-protocol.md`

## Decision

The Figure 2a VLBI time-series should **not** be collapsed into a single
benchmark row in this task.

The admissible next surface is a **per-window diagnostic ledger only**, unless a
future task reconstructs a covariance state that clears the Atomic covariance
policy. The source file exposes 10 VLBI campaign windows with `MJDstart`,
`MJDstop`, `MJDmed`, final `yVLBI=Yb/Sr`, and the component uncertainty columns
needed for row-curation discussion. However, those windows share clocks, links,
campaign systematics, deadtime/drift components, and processing-path evidence.
Treating them as independent rows would violate the shared-systematic policy,
while collapsing them into one summary row would require a frozen aggregation
and covariance recipe that is not yet committed.

## Frozen Gate State

| Field | Decision |
| --- | --- |
| Source surface | Figure 2a VLBI time-series in `Yb-Sr-ratio-measuremets.csv` |
| Ratio orientation | `Yb/Sr` |
| Window fields | `MJDstart`, `MJDstop`, `MJDmed` |
| Candidate value column | `yVLBI=Yb/Sr` |
| Uncertainty state | component uncertainties visible, covariance unresolved |
| Covariance classification | `COV_BLOCKED_SHARED_SYSTEMATICS` |
| Row route | no `data/atomic_clocks/acr-*.yaml` row in this task |
| Diagnostic route | future per-window ledger may be curated as sandbox/readiness evidence |

## Why A Single Summary Row Is Not Admissible Yet

1. The source artifact exposes window-level final ratios but does not commit a
   repository-owned rule for inverse-variance weighting, robust averaging,
   source-summary selection, or uncertainty propagation.
2. The listed uncertainty components include shared clock, comb, deadtime,
   drift, and link terms. The sign and covariance structure needed to combine
   the 10 windows is not frozen.
3. `COV_SINGLE_ROW_NO_CROSS_ROW_RISK` is not appropriate because the proposed
   single row would be derived from multiple correlated windows rather than an
   isolated published row.
4. `COV_DIAGONAL_ONLY_DECLARED` is too weak for a summary row because the known
   shared systematics are load-bearing for aggregation.
5. No loader/schema change is needed until the row route is unblocked; adding a
   direct row now would commit value-bearing semantics before the covariance
   state is defensible.

## Recommended Follow-Up

Open a narrow row-curation task that creates a machine-readable per-window
diagnostic ledger without treating the windows as independent benchmark rows.
That task should freeze:

- row order and campaign-window identifiers;
- whether each window remains diagnostic-only or can feed a source-derived
  covariance approximation;
- component uncertainty units and confidence level;
- a covariance reconstruction attempt or a documented reason it remains
  blocked;
- the exact condition under which a single summary row could move to
  `COV_SOURCE_DERIVED_PSD_APPROX` or `COV_EXACT_COMMITTED`.

If that follow-up cannot reconstruct a covariance state, keep Pizzocaro as
source-ready but row-blocked and look for a different second-source Atomic row.

## Limitations

- This review does not digitize, aggregate, or transcribe new values beyond the
  already committed CSV source artifact.
- It does not add a sandbox row-curation artifact because the current loader
  expects direct rows with committed value semantics, and this gate preserves a
  blocker rather than a row.
- The decision is specific to the committed Pizzocaro VLBI surface; it does not
  reject all Pizzocaro evidence or all Yb/Sr source paths.
- No benchmark metrics, constants-drift fits, predictions, claims, knowledge
  entries, or result artifacts are created.

## Output Routing Summary

- Task verdict: `BLOCKER_PRESERVED`.
- Canonical destination:
  `docs/reviews/atomic-pizzocaro-vlbi-row-aggregation-covariance-gate.md`.
- Review tier: `none`.
- Gate A status: `not_attempted`.
- Gate B status: `not_applicable`.
- Claim impact: `none`.
- Knowledge impact: `none`.
- Result impact: `no RESULT artifact created`.
- Publication blocker: `COV_BLOCKED_SHARED_SYSTEMATICS` and no frozen
  aggregation/covariance recipe.
