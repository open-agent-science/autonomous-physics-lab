# AGENT-RUN-0060 - Nuclear F2 Controls-First Scoring

**Task:** `TASK-0553`
**Verdict:** `DIAGNOSTIC_ONLY_CONTROL_DOMINATED`

## Summary

This run scores the frozen residual-free F2 finer taxonomy on the committed NMD-0003 measured-row surface under the frozen stratified readiness gate. F2 remains diagnostic-only; no prediction, claim, knowledge, or result artifact is created.

## Decision Metrics

- Candidate full-known MAE improvement: `0.200411` MeV.
- Best control full-known MAE improvement: `0.001151` MeV.
- Candidate minus best control: `0.19926` MeV.
- Survival margin clears: `False`.
- Validation holdout regresses: `False`.

## F2 Candidate

| surface | baseline MAE | corrected MAE | MAE improvement |
| --- | ---: | ---: | ---: |
| `train_loo` | `1.822262` | `1.618879` | `0.203383` |
| `validation_holdout` | `1.899279` | `1.705814` | `0.193465` |
| `full_known` | `1.845344` | `1.644933` | `0.200411` |

## Output Routing Summary

- Task verdict: `DIAGNOSTIC_ONLY_CONTROL_DOMINATED`.
- Canonical destination: `agent_runs/AGENT-RUN-0060/metrics.json`, `agent_runs/AGENT-RUN-0060/report.md`, `docs/reviews/nuclear-f2-controls-first-scoring.md`.
- Review tier: `none`.
- Gate A status: `not_attempted`.
- Gate B status: `not_applicable`.
- Claim impact: `none`.
- Knowledge impact: `none`.
- Result impact: `no RESULT artifact created`.
