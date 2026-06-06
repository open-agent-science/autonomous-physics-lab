# AGENT-RUN-0067 - Nuclear F2 Independent Replay And Control Ledger

**Task:** `TASK-0612`
**Replay verdict:** `REPLAY_MATCH`

## Summary

This run independently replays the committed TASK-0553 F2 controls-first scoring
(committed code, committed NMD-0003 measured data, the frozen stratified readiness
gate) and verifies that it reproduces the committed `AGENT-RUN-0060` metrics
exactly. It then records a control ledger so a later task can decide F2's fate. It
creates no prediction, reveal score, RESULT, CLAIM, KNOW, or discovery wording.

## Replay Check

- Full metrics deep-equal vs `AGENT-RUN-0060`: `True`.
- Candidate surface metrics match: `True`.
- Mismatch count: `0`.

### Candidate F2 surfaces (committed == replayed)

| surface | baseline MAE | corrected MAE | MAE improvement |
| --- | ---: | ---: | ---: |
| `train_loo` | `1.822262` | `1.618879` | `0.203383` |
| `validation_holdout` | `1.899279` | `1.705814` | `0.193465` |
| `full_known` | `1.845344` | `1.644933` | `0.200411` |

## Control Ledger

Controls: `matched_random`, `smooth_a`, `asymmetry_only`, `cluster_label_shuffle`.

| lane | full-known MAE improvement (MeV) |
| --- | ---: |
| `candidate_f2_finer_taxonomy` | `0.200411` |
| `asymmetry_only` (best control) | `0.001151` |
| `matched_random` | `-0.009373` |
| `smooth_a` | `-0.003254` |
| `cluster_label_shuffle` | `-0.006792` |

- Survival-margin rule: `0.25` MeV.
- Candidate minus best control: `0.19926` MeV.
- Survival margin clears: `False`.
- Validation holdout regresses: `False`.
- F2 scoring verdict: `DIAGNOSTIC_ONLY_CONTROL_DOMINATED`.

## Why Diagnostic-Only

The F2 candidate improves the full-known surface by `0.200411` MeV, but the best
control (`asymmetry_only`) already explains `0.001151` MeV, leaving a survival
margin of `0.19926` MeV below the `0.25` MeV controls-first threshold. F2 is
control-dominated and stays diagnostic-only; this replay authorizes no promotion,
prediction, reveal score, or claim.

## Output Routing Summary

- Task verdict: `REPLAY_MATCH`.
- Canonical destination: `agent_runs/AGENT-RUN-0067/metrics.json`, `agent_runs/AGENT-RUN-0067/report.md`, `docs/reviews/nuclear-f2-independent-replay-and-control-ledger.md`.
- Review tier: `none`.
- Gate A status: `not_attempted`.
- Gate B status: `not_applicable`.
- Claim impact: `none`.
- Knowledge impact: `none`.
- Result impact: `no RESULT artifact created`.
