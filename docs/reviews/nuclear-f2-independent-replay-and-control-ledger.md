# Nuclear F2 Independent Replay And Control Ledger

**Task:** `TASK-0612`
**Campaign:** Nuclear Mass Surface
**Status:** diagnostic-only replay
**Replay verdict:** `REPLAY_MATCH`
**Run:** `agent_runs/AGENT-RUN-0067/metrics.json`

## Scope

TASK-0553 found a large F2 finer-taxonomy diagnostic improvement on the committed
NMD-0003 measured surface but kept the lane diagnostic-only because the
controls-first survival margin was not cleared. This task independently replays
that scoring — committed code, committed data, the frozen NMD-0003 stratified
gate — and verifies it reproduces the committed `AGENT-RUN-0060` metrics exactly,
then records a control ledger for the next decision (promotion preflight, deeper
ablation, or explicit do-not-promote memory).

It does not fetch live data, refit any new model or feature family, score the
post-AME2020 reveal, or create PRED / reveal-score / RESULT / CLAIM / KNOW or
discovery wording. A non-reproducing replay is reported as
`BLOCKED_REPLAY_MISMATCH` and stops before any interpretation.

## Replay Method

The committed `run_f2_controls_first_scoring` entry point is re-executed and its
output is compared structurally (json-normalized) against the committed
`agent_runs/AGENT-RUN-0060/metrics.json`. The candidate F2 lane's `train_loo`,
`validation_holdout`, and `full_known` MAE/RMSE surfaces are additionally verified
field-by-field.

## Replay Result

- Full metrics deep-equal vs `AGENT-RUN-0060`: `True` (mismatch count `0`).
- Candidate surface metrics match: `True`.

| surface | baseline MAE | corrected MAE | MAE improvement |
| --- | ---: | ---: | ---: |
| `train_loo` | `1.822262` | `1.618879` | `0.203383` |
| `validation_holdout` | `1.899279` | `1.705814` | `0.193465` |
| `full_known` | `1.845344` | `1.644933` | `0.200411` |

The reported F2 validation and full-known improvements are independently
reproduced; the diagnostic signal is real and replayable.

## Control Ledger

The controls-first contract scores the F2 candidate against four predeclared
controls and survives only if its full-known MAE improvement beats the best
control by at least the `0.25` MeV survival margin.

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

## Why The Verdict Stays Diagnostic-Only

The F2 candidate clearly beats every control's full-known improvement, so the
signal is not a pure label artifact. However, the controls-first contract requires
an absolute survival margin of at least `0.25` MeV over the best control, and the
candidate's `0.19926` MeV margin falls short of that threshold. Under the frozen
contract F2 is therefore control-dominated and remains diagnostic-only: this
replay authorizes no promotion, prediction, reveal score, or claim.

## Decision Input For The Next Task

- The F2 diagnostic improvement is replayable and not control-explained, but it
  does not clear the predeclared `0.25` MeV survival margin.
- A follow-up may consider a bounded ablation or a promotion preflight that keeps
  the controls-first contract, or explicit do-not-promote memory. No such decision
  is made here.

## Limitations

- Retrospective AME2020 measured-row replay only; no post-AME2020 reveal scoring.
- Replays committed TASK-0553 code and data under the frozen NMD-0003 stratified
  gate; it introduces no new fit, feature family, or label.
- Sandbox replay evidence only; no PRED, reveal score, RESULT, CLAIM, KNOW, or
  discovery wording is created.

## Output Routing Summary

- Task verdict: `REPLAY_MATCH`.
- Canonical destination: `agent_runs/AGENT-RUN-0067/metrics.json`,
  `agent_runs/AGENT-RUN-0067/report.md`, this review.
- Review tier: `none`.
- Gate A status: `not_attempted`.
- Gate B status: `not_applicable`.
- Claim impact: `none`.
- Knowledge impact: `none`.
- Result impact: `no RESULT artifact created`.
