# Anharmonic Replay Result-Promotion Preflight

Task: `TASK-0660`
Domain: Anharmonic oscillator period benchmark
Mode: planning only
Verdict: `GATE_B_REPLAY_PASSED_GATE_C_MAINTAINER_ONLY`

## Purpose

This preflight routes the mature Anharmonic benchmark evidence through
`docs/result-promotion-protocol.md`. It does not add formulas, rerun the
experiment, create claims, create predictions, or promote any scientific
artifact.

The useful decision is narrow: `RESULT-0016` already has an independent agent
replay with unchanged metrics, so additional agent-side replay is not the next
blocker. Any stronger public evidence card now needs maintainer Gate C review,
not another sandbox loop.

## Evidence Reviewed

- `experiments/EXP-0011-anharmonic-oscillator-period.yaml`
- `results/EXP-0011/RUN-0002/result.yaml`
- `docs/results/anharmonic-oscillator-summary.md`
- `campaign_profiles/anharmonic-oscillator.yaml`
- `docs/result-promotion-protocol.md`
- `docs/reviews/first-agent-validated-replay.md`
- `docs/reviews/cross-campaign-result-promotion-inventory.md`

## Current Artifact State

| Artifact | State | Preflight reading |
| --- | --- | --- |
| `RESULT-0014` / `RUN-0001` | Legacy baseline result | Useful historical result, but not the current tiered promotion target. |
| `RESULT-0016` / `RUN-0002` | `AGENT_VALIDATED`, `VALID_IN_RANGE` | Current promotion target for the Anharmonic benchmark slice. |
| `CLAIM-0009` | Draft claim candidate | Not promoted by this task; maintainer review remains required. |

`RESULT-0016` preserves the conservative scope: a one-dimensional quartic
oscillator, non-negative `lambda`, and the predeclared benchmark slices. It does
not support statements about negative `lambda`, double-well dynamics, damping,
driving, resonance, chaos, or broad dynamical regimes.

## Promotion Gate Readiness

Gate A is already satisfied for `RESULT-0016`: the result is a canonical result
artifact with declared experiment/run routing and validation context.

Gate B is already satisfied for `RESULT-0016`: the independent replay recorded
in `results/EXP-0011/RUN-0002/result.yaml` preserved the command, inputs,
metric count, verdict, and all tracked numeric metrics. The recorded
`max_abs_delta` is `0.0` across 36 compared metrics, and the verdict remained
`VALID_IN_RANGE`.

Gate C is not satisfied by this task. Gate C is a maintainer review step for
claim-level promotion. An agent may package this preflight, but must not mark
`CLAIM-0009` as promoted or rewrite canonical claim status.

## Replay Need

No additional agent replay is recommended before maintainer review. Repeating
Gate B would mainly duplicate the already preserved negative drift result. The
next meaningful action, if maintainers want stronger public routing, is a
maintainer Gate C decision on whether `CLAIM-0009` should remain draft or move
to a higher reviewed state.

No new task proposal is made here because the directly relevant
`AGENT_VALIDATED` blocker has already been cleared for `RESULT-0016`.

## Public Wording Limits

Allowed wording:

- "agent-validated replay of a conservative benchmark slice"
- "unchanged metrics under the recorded replay"
- "valid in the predeclared in-range Anharmonic benchmark regime"

Disallowed wording:

- exact or universal period law
- discovery wording
- material about negative `lambda`, double wells, damping, driving, resonance,
  chaos, or broad dynamical regimes
- any statement that the draft claim is promoted

## Output Routing Summary

- New result artifact: none
- New claim artifact: none
- New prediction artifact: none
- Knowledge registry update: none
- Current strongest supported tier: `RESULT-0016` remains `AGENT_VALIDATED`
- Next non-agent gate: maintainer Gate C review, if maintainers choose to run it
