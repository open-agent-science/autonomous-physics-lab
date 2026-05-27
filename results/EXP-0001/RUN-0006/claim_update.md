# Claim Evidence Note

- Result: `RESULT-0017`
- Hypothesis: `HYP-0001`
- Experiment: `EXP-0001`
- Task: `TASK-0413`
- Claim status impact: no change; `CLAIM-0001` remains `DRAFT`
- Gauntlet candidates evaluated: 101

## Evidence Routing

The pendulum gauntlet evaluated 101 deterministic candidate formulas. The best
candidate was `model_t2_x4_l2` with verdict `OVERFITTED`. This is preserved as
agent-published negative/overfit evidence, not as support for a stronger
pendulum claim.

## Scope Language

The result is scoped to the sampled ranges used by this workflow: train
`0.0100` to `2.0985` rad, test `2.1135` to `3.0000` rad.

## Metrics

- Mean relative error (test): `0.004347`
- Max relative error (test): `0.021261`
- Complexity score: `3`

## Evidence Basis

- Passed checks: `6`
- Failed/non-passing checks: `5` including two unresolved diagnostics treated as
  non-passing for AGENT_PUBLISHED Gate A.
- Rationale: Verification checks did not fully pass, so no claim promotion is
  requested.

## Caution

Keep this as negative/overfit memory. It does not establish a closed-form,
globally valid, or exhaustive pendulum formula.
