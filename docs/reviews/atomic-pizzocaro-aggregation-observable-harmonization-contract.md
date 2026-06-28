# Atomic Pizzocaro Aggregation And Observable-Harmonization Contract

**Task:** `TASK-0872`
**Campaign:** `atomic-clock-residuals`
**Verdict:** `REMAINS_DIAGNOSTIC_ONLY`
**Review date:** 2026-06-28

## Scope

This review drafts the contract that would be required before the ten
Pizzocaro 2020 VLBI windows could be represented by one cross-source target.
It uses only committed reviews, schema notes, and source metadata. It does not
inspect or create new value-bearing rows, aggregate the windows, run Yb/Sr
metrics, fit constants drift, or create `RESULT`, `PRED`, `CLAIM`, or
`KNOW` artifacts.

The current decision is conservative: the contract can state the required
semantics, but the committed evidence does not satisfy them. Pizzocaro remains
a ten-window, sensitivity-only diagnostic surface.

## Inputs Reviewed

| Input | Contract role |
| --- | --- |
| [Atomic Yb/Sr source-limited consistency memory card](atomic-yb-sr-source-limited-consistency-memory-card.md) | Reopen condition and two-row/source-limited boundary |
| [Atomic Yb/Sr reopen source-route scout](atomic-ybsr-reopen-source-route-scout.md) | Prior `AGGREGATION_CONTRACT_NEEDED` decision |
| [Pizzocaro per-window diagnostic ledger review](atomic-pizzocaro-per-window-diagnostic-ledger.md) | Ten-window scope, window metadata, uncertainty components, and no-aggregation boundary |
| [Pizzocaro post-PSD row-admissibility review](atomic-pizzocaro-row-admissibility-after-psd-covariance.md) | Current aggregation and row-admission blockers |
| [Pizzocaro observable-harmonization contract](atomic-pizzocaro-observable-harmonization-contract.md) | Authorized residual-axis diagnostic mapping |
| [Pizzocaro extraction-ledger gate](atomic-pizzocaro-yb-sr-extraction-ledger-gate.md) | Field-level source and row-class decision |
| [Atomic row schema](../../data/atomic_clocks/schema.md) | Direct, derived, review-summary, holdout, and source requirements |

## Existing Boundary

The committed contracts establish all of the following:

- the selected surface is the ten Figure 2a VLBI windows, with orientation
  `Yb/Sr`;
- each window is a source-reported fractional frequency-ratio deviation, not
  an admitted absolute-ratio row;
- `TASK-0706` permits a Beloy-comparable residual axis only as a
  sensitivity diagnostic and forbids cross-window aggregation;
- the committed covariance artifact is
  `COV_SOURCE_DERIVED_PSD_APPROX`, with `rho_clock = 0` and
  `rho_clock = 1` retained as separate sensitivity views;
- diagonal-only treatment is a required comparator for diagnostics, not an
  admissible aggregation covariance;
- the Figure 2b `Thiswork` summaries lack the campaign-window and
  construction semantics required for an ACR row.

This task does not weaken or replace those boundaries.

## Candidate Aggregation Routes

| Route | Required semantics | Current decision |
| --- | --- | --- |
| Source-published absolute summary | A source-backed absolute `Yb/Sr` value, campaign window, uncertainty construction, covariance/dependence notes, and row-of-record citation | **Blocked.** No such admitted surface is identified in the committed extraction contract. |
| Repository generalized least-squares aggregate | Frozen all-window inclusion, an admissible covariance matrix, an absolute reference anchor, uncertainty propagation, row-class policy, and independence accounting | **Contract definable but not executable.** The covariance and anchor remain sensitivity-only or under-specified. |
| Ten-window residual-axis diagnostic | Keep every window visible and report diagonal-only plus both approximate-covariance sensitivity views | **Authorized already.** This remains the only current Pizzocaro route. |

Selecting a route after looking at an aggregate value is forbidden. The route,
window set, covariance state, and reference-anchor policy must be frozen before
any future value-bearing task.

## Conditional Aggregation Contract

The following requirements are cumulative. Failing any one of them keeps the
surface diagnostic-only.

### 1. Source Surface And Window Rules

- Use only the ten committed Figure 2a VLBI windows.
- Include all ten windows in source order. No value-based exclusion,
  uncertainty-based trimming, robust outlier removal, or preferred-window
  selection is allowed unless a separate, predeclared source-quality rule is
  approved before values are processed.
- Do not mix VLBI with IPPP, PPP, or Figure 2b history-summary surfaces.
- Preserve each source window's start, stop, median epoch, processing path, and
  component-uncertainty provenance.
- Define the aggregate campaign interval from the earliest included start to
  the latest included stop, with the MJD-to-calendar conversion rule recorded.

### 2. Observable Orientation And Absolute Anchor

The input deviations are `d_i` on the source-reported `Yb/Sr` orientation.
An absolute aggregate is allowed only if the source record pins an absolute
reference ratio `R_0` and the exact relation between that reference and the
reported deviations. The expected mapping must be source-backed, not inferred:

```text
R_i = R_0 * (1 + d_i)
```

The future task must record:

- the exact source locator for `R_0`;
- whether `R_0` is a measured, recommended, or constructed value;
- its uncertainty and covariance with the ten windows;
- whether the same anchor enters Beloy, Nemitz, or another comparator;
- the sign and orientation convention proving that no reciprocal ratio was
  introduced.

Using the Beloy row itself as `R_0` is allowed only for the existing
diagnostic residual axis. It cannot create an independent cross-source target
or increase the campaign's independent-source count.

### 3. Covariance And Weighting

For a future repository-owned aggregate, the aggregation rule must be frozen as
generalized least squares over the complete window vector:

```text
w = C^-1 1 / (1^T C^-1 1)
d_bar = w^T d
var(d_bar) = w^T C w
```

The contract requires:

- a source-published exact covariance matrix, or a separately approved
  repository covariance artifact whose status explicitly permits aggregation;
- the frozen window order and covariance units;
- positive-semidefinite and numerical-rank checks;
- an explicit rule for singular or ill-conditioned covariance. No silent
  pseudoinverse, jitter, eigenvalue clipping, or post-hoc regularization is
  allowed;
- a diagonal-only result only as a labelled sensitivity comparator, never as
  the row-of-record aggregate;
- no selection between `rho_clock = 0` and `rho_clock = 1` after seeing
  their outputs.

The current `COV_SOURCE_DERIVED_PSD_APPROX` artifact remains
`sensitivity_only: true`. Its two bounds do not choose one admissible
row-of-record covariance, so this requirement is not currently met.

### 4. Aggregate Uncertainty

If an absolute mapping is admitted, the aggregate is
`R_bar = R_0 * (1 + d_bar)`. Its uncertainty must propagate:

- `var(d_bar)` from the approved window covariance;
- the fractional uncertainty of `R_0`;
- any covariance between `R_0` and the window vector;
- any shared reference-frequency, clock, comb, link, dead-time, or drift
  contribution not already represented in `C`.

Unknown dependence is a stop condition, not permission to add uncertainties
in quadrature. The task must also prove that shared components are not counted
twice between `C` and the anchor uncertainty.

### 5. Direct-Versus-Derived Classification

A repository-computed aggregate of the ten windows is not automatically a
`direct_measurement` row.

- A source-published absolute row with complete source semantics may be
  evaluated as `direct_measurement`.
- A repository-owned combination must remain `review_summary`, or use a new
  maintainer-approved aggregate row class, with
  `classification.direct_measurement: false`,
  `classification.derived_constraint: false`, and explicit input-window and
  combination-rule provenance.
- `derived_constraint` is not appropriate: the aggregate is not a
  constants-variation or drift constraint.

The current loader and holdout policy do not admit a `review_summary` as an
independent direct-frequency-ratio target. A future task must obtain an
explicit schema/loader decision before assigning `cross_source_target`.

### 6. Independence And Holdout Role

Before a future target is frozen, the task must show that:

- the Pizzocaro measurement chain is scientifically independent of the
  comparator rows;
- no Beloy-derived central value is used to manufacture the Pizzocaro absolute
  target;
- any common recommended-frequency anchor is modelled as shared dependence;
- the row role and holdout split are frozen before metrics;
- the aggregate cannot be counted as ten independent rows or as both a summary
  and its component windows.

If independence is not demonstrated, the aggregate may remain a diagnostic
summary but cannot reduce the Beloy/Nemitz source-limited blocker.

## Current Gate Assessment

| Gate | Current state |
| --- | --- |
| Ten-window VLBI surface frozen | pass |
| Ratio orientation and residual-axis semantics | pass for diagnostics only |
| Source-backed absolute reference mapping | not established for row admission |
| Aggregation-permitted covariance | fail; current matrix is sensitivity-only |
| Frozen uncertainty propagation | fail; anchor and dependence terms unresolved |
| Direct-versus-derived row class | fail; repository aggregate is not an admitted direct row |
| Independent `cross_source_target` role | fail |

Verdict: `REMAINS_DIAGNOSTIC_ONLY`.

## Stop Conditions

Stop before aggregation or row curation if any of these conditions holds:

1. the absolute reference ratio or deviation formula is not source-pinned;
2. only diagonal or sensitivity-only covariance is available;
3. shared anchor/window dependence is unknown;
4. the aggregate row class or loader admission rule is unresolved;
5. the route depends on Beloy as its absolute anchor but is presented as an
   independent source;
6. any window is selected or removed after inspecting values;
7. IPPP, PPP, VLBI, and history summaries are mixed without a separate
   cross-processing covariance contract;
8. a task proposes Yb/Sr metrics, drift fitting, or promotion before the source,
   covariance, row-class, and holdout gates pass.

## Reopen Implications

This contract does not reopen Atomic benchmarking and does not authorize a new
Pizzocaro ACR row. Pizzocaro still contributes one diagnostic source surface,
not a third independent absolute-ratio row.

A later maintainer decision may reopen row curation only after either:

1. a source-backed absolute Pizzocaro summary with complete uncertainty and
   campaign semantics is pinned; or
2. a task explicitly approves an aggregation-capable covariance, an absolute
   anchor with dependence accounting, and a schema/loader class for the
   repository aggregate.

Until then, future work may use only the existing TASK-0706 sensitivity
diagnostic or scout a new independent absolute Yb/Sr source. No metric rerun is
recommended from this contract.

## Output Routing

- Task verdict: `REMAINS_DIAGNOSTIC_ONLY`.
- Canonical destination: this review contract.
- Review tier: `none`.
- Gate A status: not attempted; no result or prediction artifact.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Dataset impact: no value-bearing row or source artifact changed.
- Publication blocker: no aggregation-permitted covariance, source-backed
  absolute-anchor contract, admitted aggregate row class, or independent
  cross-source target.

## Limitations

- Repository evidence only; no live source or literature search.
- No Pizzocaro values were aggregated or scored.
- The formulas above define a conditional future contract, not a validated
  aggregate.
- Maintainer approval cannot substitute for missing source or dependence
  evidence; it can only choose among scientifically admissible routes.
