# Atomic Yb/Sr Benchmark Result-Path Decision

**Task:** `TASK-0756`
**Campaign:** `atomic-clock-residuals`
**Decision:** `CONSISTENCY_NEGATIVE_MEMORY_CARD`
**Review date:** 2026-06-16

## Scope

This note adjudicates the route for the completed `TASK-0456` Atomic Yb/Sr
cross-source diagnostic. It uses only committed repository evidence and runs no
new metrics. It does not create or promote a `RESULT`, `PRED`, `CLAIM`, or
`KNOW` artifact.

## Evidence Reviewed

| Evidence | Role |
| --- | --- |
| `agent_runs/AGENT-RUN-0071/metrics.json` | Deterministic Beloy/Nemitz Yb/Sr diagnostic metrics. |
| `agent_runs/AGENT-RUN-0071/report.md` | Agent-run interpretation and output routing. |
| `docs/reviews/atomic-yb-sr-cross-source-consistency-benchmark.md` | Scientist-readable `TASK-0456` benchmark review note. |
| `docs/reviews/atomic-baseline-readiness-after-nemitz-acr0002.md` | `TASK-0705` gate authorizing exactly one exploratory diagonal-only diagnostic. |
| `docs/reviews/atomic-pizzocaro-yb-sr-extraction-ledger-gate.md` | `TASK-0742` gate showing Pizzocaro is diagnostic-only and blocked as an ACR row. |
| `data/atomic_clocks/source_manifest.yaml` | Current source-family readiness and blocker state. |
| `docs/result-promotion-protocol.md` | Promotion vocabulary and Gate A / Gate B boundaries. |

## Diagnostic State

`TASK-0456` compared the committed Beloy 2021 / BACON Yb/Sr reference row
against the committed Nemitz 2016 / RIKEN Yb/Sr target row under
`COV_DIAGONAL_ONLY_DECLARED`. The sources are independent, so the diagonal-only
off-diagonal assumption is defensible for an exploratory diagnostic.

The run found `|z| = 1.781891393631367`, below the predeclared `2.0`
no-tension threshold. That supports a narrow no-tension reading at the probed
precision, but it does not support result promotion:

- the comparison uses two rows only, one per source;
- the Nemitz total uncertainty dominates the comparison by about `6.7x`;
- the diagnostic does not test Beloy's finer precision;
- the covariance state is explicitly exploratory and diagonal-only;
- no constants-drift fit, new-physics inference, prediction, claim, or result
  artifact was authorized.

## Route Decision

Chosen route: `CONSISTENCY_NEGATIVE_MEMORY_CARD`.

This route preserves the finding as durable source-limited consistency memory:
Beloy and Nemitz are consistent within the declared uncertainty model, and that
negative/no-tension outcome should prevent repeated reruns of the same two-row
diagnostic. It is not promoted to a canonical `RESULT` because Gate A would be
blocked by the two-row population, source-limited precision, and exploratory
covariance state.

## Routes Not Selected

| Route | Decision |
| --- | --- |
| `RESULT_PROMOTION_PREFLIGHT` | Not selected. The diagnostic is useful but underpowered for a Gate A result package: two rows, Nemitz-dominated uncertainty, and exploratory diagonal-only covariance remain publication blockers. |
| `THIRD_SOURCE_FIRST` | Not selected as the immediate route. `TASK-0742` shows Pizzocaro cannot currently supply an admissible third absolute Yb/Sr ACR row; it is diagnostic-only unless a new absolute-ratio source or maintainer-approved aggregation contract appears. |
| `DO_NOT_PROMOTE` | Not selected as the primary route. The evidence should not be discarded; it is useful negative/no-tension memory with explicit limitations. |

## Promotion Blockers

Using the result-promotion protocol vocabulary, the blockers are:

- `underpowered_rows`: only two committed Yb/Sr rows are available for the
  benchmark axis;
- `source_blocker`: no admissible third absolute Yb/Sr source row currently
  exists;
- `source_limited`: the Nemitz uncertainty dominates the comparison and limits
  the precision being tested;
- `needs_maintainer_decision`: any later `RESULT` package would require a new
  maintainer-approved Gate A path and scope wording.

## Follow-Up Recommendation

Do not rerun the Beloy/Nemitz metric as a new benchmark task. The next useful
Atomic work is one of:

1. create a concise source-limited consistency-memory card that packages this
   decision without `RESULT` promotion; or
2. open a new source/aggregation task only if a future absolute Yb/Sr source or
   maintainer-approved aggregation contract can reduce the current blocker.

Pizzocaro may still support diagnostic sensitivity work under its existing
contract, but it does not reduce the absolute-row benchmark from two sources to
three.

## Output Routing

- Task verdict: `not_applicable` as a promotion-route adjudication gate.
- Canonical destination:
  `docs/reviews/atomic-yb-sr-benchmark-result-path-decision.md`.
- Review tier: `none`.
- Gate A status: `not_attempted`.
- Gate B status: `not_applicable`.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result artifact impact: no `RESULT` or `PRED` artifact created.
- Limitation: this decision routes existing evidence only; it does not compute
  new metrics or endorse constants-drift, new-constant, anomaly, or new-physics
  wording.
