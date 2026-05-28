# Pendulum Claim Promotion Smoke Test

**Task:** `TASK-0416`  
**Claim:** `CLAIM-0001`  
**Hypothesis:** `HYP-0001`  
**Experiment:** `EXP-0001`  
**Verdict:** `PARTIALLY_SUPPORTED` candidate; `DRAFT` retained pending maintainer Gate C

## Scope

This review runs a scoped claim-promotion smoke test for
`CLAIM-0001: Pendulum Period Depends on Amplitude`.

It does not change the claim status. Phase 1 of the result-promotion protocol
keeps all `CLAIM-*` status transitions maintainer-only, and the task explicitly
forbids marking any claim `SUPPORTED` without maintainer approval.

## Evidence Reviewed

- `RESULT-0001` (`EXP-0001/RUN-0001`) records a deterministic pendulum formula
  benchmark with `best_verdict: VALID_IN_RANGE`, passing the in-scope
  verification gate over the configured range up to `1.5708` rad.
- `RESULT-0003` (`EXP-0001/RUN-0002`) repeats the range-limited positive
  surface with the theory-aware candidate set. Its `claim_update.md` suggests
  `PARTIALLY_SUPPORTED`, but the suggestion remains non-automatic.
- `RESULT-0013` (`EXP-0001/RUN-0005`) records a 102-candidate asymptotic
  gauntlet with `best_verdict: VALID_IN_RANGE` and all listed verification
  checks passing for the selected model over the configured range up to `3.1`
  rad.
- `RESULT-0017` (`EXP-0001/RUN-0006`) records the first pendulum
  `AGENT_PUBLISHED` negative/overfit result. Its `best_verdict` is
  `OVERFITTED`, verification does not pass, and its own claim note says
  `CLAIM-0001` should remain `DRAFT`.

## Policy Check

- Claim-promotion policy allows `PARTIALLY_SUPPORTED` only when reproducible
  evidence exists, in-scope checks pass, and the claim text explicitly remains
  range-limited or benchmark-limited.
- The current claim statement is conservative: the ideal pendulum period
  increases with amplitude and is not exactly captured by the small-angle
  approximation alone.
- The current claim body already warns that the evidence remains
  benchmark-scoped and recommends keeping the claim in `DRAFT`.
- `SUPPORTED` is not appropriate here because the evidence is still
  benchmark-scoped, some result surfaces preserve overfit failures, and no
  maintainer Gate C review has endorsed stronger wording.

## Recommended Gate C Action

If the maintainer chooses to run Gate C, the narrowest safe transition is:

- status candidate: `PARTIALLY_SUPPORTED`
- required qualifier: valid only for the ideal mathematical pendulum within the
  referenced benchmark scopes
- required evidence basis: cite positive `VALID_IN_RANGE` results separately
  from the `RESULT-0017` negative/overfit memory
- required non-claim: no exact formula, global validity, real-world damped
  pendulum, or new-physics interpretation

Suggested maintainer-reviewed wording:

> For the ideal mathematical pendulum, benchmarked against the elliptic-integral
> reference, the period depends on amplitude and range-limited correction
> formulas improve on the small-angle approximation within the sampled scopes of
> the referenced `EXP-0001` results. This does not establish a globally exact
> closed-form approximation or a claim about non-ideal pendulums.

## Output Routing

- Canonical destination: `docs/reviews/pendulum-claim-promotion-smoke-test.md`
- Review tier: not applicable; this is a claim-review recommendation, not a new
  `RESULT-*` artifact
- Gate A status: not applicable
- Gate B status: not applicable
- Gate C status: not run; maintainer-only
- Claim impact: no repository claim status transition; `CLAIM-0001` remains
  `DRAFT`
- Knowledge impact: none
- Publication blocker: maintainer Gate C review is required before any
  `CLAIM-0001` status transition

## Final Verdict

`CLAIM-0001` is a `PARTIALLY_SUPPORTED` candidate, but this PR intentionally
retains `DRAFT` status. The reviewed evidence is strong enough to justify a
maintainer Gate C discussion, not an autonomous claim promotion.
