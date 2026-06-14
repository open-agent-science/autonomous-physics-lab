
# AGENT-RUN-0070 - Stellar M-L Route 2 Local-Extractor Benchmark

**Task:** `TASK-0740`
**Outcome:** `SANDBOX_PASS`

## Summary

This run executes the first sandbox-only Stellar mass-luminosity Route 2
benchmark against locally regenerated DEBCat component rows. It uses the pinned
DEBCat checksum, the committed extractor contract, frozen physical-binary-system
lanes, and the predeclared single-alpha primary baseline
`L/L_sun = (M/M_sun)^3.5` over `0.5 <= M/M_sun < 2.0`.

No raw `debs.dat`, full normalized DEBCat row file, full manifest, `RESULT-*`,
`PRED-*`, `CLAIM-*`, or `KNOW-*` artifact is committed.

## Decision

- Classification: `SANDBOX_PASS`.
- Rationale: Primary-range holdout formula MAE beats the predeclared train-median null.
- Primary-range holdout rows: `132`.
- Primary-range holdout MAE: `0.347101` dex.
- Train-median null holdout MAE: `0.44492` dex.

## Primary-Range Lane Metrics

| lane | count | MAE dex | median residual dex | frac <=0.2 dex | beats null |
| --- | --- | --- | --- | --- | --- |
| train | 254 | 0.313852 | 0.15585 | 0.5 | n/a |
| validation | 103 | 0.316253 | 0.14125 | 0.466019 | True |
| holdout | 132 | 0.347101 | 0.141623 | 0.515152 | True |

## Sensitivity Notes

- Direct-luminosity and derived-luminosity rows are reported separately in
  `metrics.json`.
- Out-of-primary-range rows are diagnostic only and do not drive the run verdict.
- Unknown or evolved spectral-stage flags are retained as explicit subset
  labels rather than filtered after residual inspection.

## Output Routing Summary

- Task verdict: `SANDBOX_PASS`.
- Canonical destination: `agent_runs/AGENT-RUN-0070/metrics.json`,
  `agent_runs/AGENT-RUN-0070/report.md`, and
  `docs/reviews/stellar-ml-route2-local-benchmark.md`.
- Review tier: `none`.
- Gate A status: `not_attempted`.
- Gate B status: `not_applicable`.
- Claim impact: `none`.
- Knowledge impact: `none`.
- Result impact: `no RESULT artifact created`.
- Publication blocker: `sandbox-only first empirical benchmark; full DEBCat rows remain local-only under Route 2`.
