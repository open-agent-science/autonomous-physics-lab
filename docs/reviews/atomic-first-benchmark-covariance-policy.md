# Atomic First-Benchmark Covariance Policy

**Task:** `TASK-0486`  
**Campaign:** `atomic-clock-residuals`  
**Policy class:** benchmark-readiness covariance protocol  
**Status:** policy only; no benchmark residuals, drift fits, or claims

## Scope

This note defines the covariance policy for the first Atomic-Clock Residuals
benchmark consumer. It is downstream of the uncertainty-semantics review and
the Beloy 2021 source-derived covariance approximation, but it does not run a
benchmark, ingest a new row, fit constants drift, or promote any claim.

The policy answers one narrow question:

> When may a future atomic-clock benchmark combine direct frequency-ratio rows,
> and how must it label the result when covariance is exact, approximated,
> absent, or blocked?

## Inputs

- `docs/reviews/atomic-clock-covariance-uncertainty-semantics.md`
- `data/atomic_clocks/acr-0001-beloy-2021-cross-ratio-covariance-approximation.yaml`
- `docs/campaigns/atomic-clock-residuals.md`
- `tasks/TASK-0455-rerun-atomic-baseline-readiness-gate.yaml`

## Covariance Handling States

Future atomic benchmark consumers must classify every candidate row family into
exactly one covariance state before computing any cross-row metric.

| State | Meaning | Minimum evidence | Allowed benchmark output |
| --- | --- | --- | --- |
| `COV_EXACT_COMMITTED` | The source publishes or deterministically defines the covariance matrix, and the matrix or exact reconstruction recipe is committed. | Row order, diagonal units, off-diagonal semantics, confidence level, checksum/provenance or deterministic recipe, and a PSD check. | Full correlated benchmark metrics, e.g. covariance-aware residual summaries or chi-square diagnostics, with no claim promotion. |
| `COV_SOURCE_DERIVED_PSD_APPROX` | A covariance approximation is reconstructed from committed source tables and passes PSD checks, but it is not a paper-published full matrix. | Deterministic recipe, row order, unit convention, PSD check, omitted-component list, and approximation limitations. | Sensitivity-only correlated metrics and side-by-side diagonal-vs-approximation diagnostics. Headline metrics must say `approximate covariance`. |
| `COV_DIAGONAL_ONLY_DECLARED` | Rows have documented per-row uncertainties, but no defensible off-diagonal covariance is available. Independence is an explicit modelling assumption, not a fact. | Per-row uncertainty semantics, confidence level, direct-vs-derived class, and a documented reason covariance is unavailable. | Diagonal-only exploratory metrics with an independence-warning banner. No combined high-precision verdict, no drift fit, and no claim promotion. |
| `COV_SINGLE_ROW_NO_CROSS_ROW_RISK` | The benchmark surface uses a single isolated direct row or a single source-family summary where no cross-row combination is performed. | Source provenance, row uncertainty semantics, and confirmation that no second correlated row enters the same metric. | Per-row residual display, source-readiness diagnostics, or single-row comparison notes. No aggregate benchmark verdict. |
| `COV_BLOCKED_SHARED_SYSTEMATICS` | Two or more rows may share clocks, campaigns, systematics, sensitivity coefficients, epochs, or source-derived evidence, and no acceptable covariance policy is available. | Evidence of shared systematics or duplicate evidence, or missing uncertainty/covariance semantics that prevents classification above. | No benchmark metric. Output must be a blocker note or readiness-gate failure only. |

## Direct-Row Policy

Direct frequency-ratio rows may enter the first benchmark only when they also
pass the existing direct-row source gates:

- source artifact and version-drift status are pinned;
- row value, units, epoch or campaign window, and confidence level are
  recoverable;
- direct rows are not mixed with derived drift or constants-variation
  constraints on the same residual axis;
- true source families, repeated campaigns, and shared-clock rows are grouped
  before any metric is computed.

If a direct row has no cross-row partner in the metric, it may use
`COV_SINGLE_ROW_NO_CROSS_ROW_RISK`. Once two rows are compared or combined, the
consumer must upgrade the state to `COV_EXACT_COMMITTED`,
`COV_SOURCE_DERIVED_PSD_APPROX`, `COV_DIAGONAL_ONLY_DECLARED`, or
`COV_BLOCKED_SHARED_SYSTEMATICS`.

## Shared-Systematic Policy

Rows sharing any of the following must not be treated as silently independent:

- a clock species or physical clock in the same campaign;
- a lab-wide network link, geopotential correction, or environmental
  systematic;
- overlapping campaign windows without separable epoch metadata;
- a derived sensitivity coefficient;
- a primary measurement reused in both a direct row and a derived row.

If the shared component has a committed sign convention and uncertainty
decomposition, a source-derived covariance approximation may be allowed. If the
shared component is known to exist but cannot be signed or bounded from the
committed source artifacts, the benchmark must either:

- report a sensitivity-only diagonal-vs-approximation comparison with the
  missing component named, or
- stop as `COV_BLOCKED_SHARED_SYSTEMATICS` when the missing component is
  load-bearing for the intended metric.

## Source-Derived PSD Approximation Policy

`ACR-0001-COV-APPROX-BELOY-2021` is admissible as
`COV_SOURCE_DERIVED_PSD_APPROX` because it records:

- row order and unit convention;
- diagonal source and off-diagonal reconstruction rule;
- shared-clock sign convention;
- pairwise decomposition;
- PSD eigenvalue check;
- omitted network/geopotential/statistical limitations;
- explicit sandbox and no-claim boundaries.

This state does not make the approximation a published covariance matrix.
Any benchmark using it must report both:

- the diagonal-only result, and
- the source-derived-PSD-approximation sensitivity result.

If the two materially disagree, the stricter interpretation wins: the output is
`INCONCLUSIVE` or `BLOCKED`, not a strengthened benchmark success.

## Missing-Covariance Policy

Missing covariance is acceptable only when it is explicitly declared and
scientifically non-load-bearing.

Allowed examples:

- a single isolated direct row with no cross-row metric;
- a row-count or source-readiness diagnostic;
- an exploratory diagonal-only diagnostic whose PR title, summary, and output
  routing say that covariance is missing.

Blocked examples:

- combining two rows from the same campaign without separable epochs;
- ranking residuals across shared-clock rows while ignoring known shared
  systematics;
- fitting drift or constants variation from rows with duplicated primary
  evidence;
- publishing a headline high-precision consistency score from diagonal-only
  assumptions when a source-derived covariance is known to be possible but not
  yet reviewed.

## Allowed First-Benchmark Outputs By State

| Output class | Exact committed | Source-derived PSD approximation | Diagonal-only declared | Single row | Blocked |
| --- | --- | --- | --- | --- | --- |
| Source-readiness note | yes | yes | yes | yes | yes |
| Per-row residual display | yes | yes | yes, with warning | yes | no |
| Diagonal-only diagnostic | yes, as comparator | yes, as comparator | yes, exploratory only | not applicable | no |
| Covariance-aware metric | yes | sensitivity-only | no | no | no |
| Cross-source consistency verdict | yes, benchmark-only | `INCONCLUSIVE` unless robust to sensitivity check | no | no | no |
| Constants-drift fit | no | no | no | no | no |
| Claim or knowledge promotion | no | no | no | no | no |

## Stop Conditions

A future first-benchmark task must stop before computing or interpreting the
metric when any condition below holds:

1. A source family has multiple rows and no covariance state.
2. A row lacks confidence-level semantics or unit convention.
3. A shared systematic is known, load-bearing, and not represented in either a
   committed matrix or a declared sensitivity approximation.
4. A direct row and a derived constraint reuse the same physical evidence in
   the same residual axis.
5. A source-derived approximation fails a PSD check.
6. A diagonal-only result would be used as the primary evidence for constants
   drift, new-constant constraints, anomaly wording, or claim promotion.
7. A version-drift or campaign-window blocker remains unresolved for any row
   used in the benchmark surface.

## Required Reporting Fields

Any future atomic benchmark review must report:

- `covariance_state` for each source family;
- row order used by any covariance matrix;
- units and confidence level for every diagonal entry;
- PSD verdict for any exact or approximate covariance matrix;
- diagonal-only comparator metric when a covariance-aware metric is reported;
- sensitivity-only label when using `COV_SOURCE_DERIVED_PSD_APPROX`;
- blocker state and excluded rows when covariance is missing or ambiguous;
- explicit `no drift fit` and `no claim promotion` boundaries.

## Verdict

`VALID_IN_RANGE`

The first Atomic benchmark now has a conservative covariance policy: exact
committed covariance may support correlated benchmark diagnostics;
source-derived PSD approximations may support sensitivity-only diagnostics;
diagonal-only assumptions remain exploratory; and shared-systematic ambiguity
blocks high-precision interpretation. This policy does not authorize real
benchmark residuals, constants-drift fits, prediction entries, claims, or
knowledge promotion.

## Output Routing Summary

- task verdict: `VALID_IN_RANGE`;
- canonical destination: covariance policy review documentation;
- review tier: `none`;
- Gate A status: not attempted;
- Gate B status: not attempted;
- claim impact: no claim change;
- knowledge impact: no knowledge change;
- result artifact impact: no `results/` artifacts modified;
- limitations / blockers: the policy still requires a later benchmark-readiness
  gate to decide whether available atomic rows qualify for `BASELINE_READY`.
