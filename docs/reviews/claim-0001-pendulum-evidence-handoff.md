# CLAIM-0001 Pendulum Evidence Handoff

- Task: `TASK-0760`
- Claim: `CLAIM-0001`
- Claim artifact: `claims/CLAIM-0001-pendulum-period-amplitude.md`
- Decision lane: maintainer Gate C review
- Handoff verdict: `MAINTAINER_DECISION_NEEDED`

## Scope

This handoff assembles existing pendulum evidence for a maintainer decision on
`CLAIM-0001`. It does not change claim status or wording, create knowledge
artifacts, create new result artifacts, rerun formula discovery, update
`results/golden-results.yaml`, or claim an exact all-amplitude pendulum
discovery.

`CLAIM-0001` is currently `DRAFT`. Its current statement is conservative:

> For an ideal mathematical pendulum, the period increases with amplitude and
> cannot be captured exactly by the small-angle approximation alone.

The evidence below supports range-aware maintainer review. It does not support
unqualified exactness, all-amplitude validity, real-lab empirical validation,
or an exhaustive formula-discovery claim.

## Positive Range-Limited Evidence

| Result | Artifact | Verdict | Range | Key evidence | Interpretation |
| --- | --- | --- | --- | --- | --- |
| `RESULT-0001` | `results/EXP-0001/RUN-0001/result.yaml` | `VALID_IN_RANGE` | train `0.0100` to `1.1002` rad; test `1.1080` to `1.5708` rad | Best model `model_theta2_theta4`; test mean relative error `0.0006349501992633444`; test max relative error `0.0018887002075346894`; verification passed. | Supports amplitude-dependent in-range approximation behavior, but not separatrix or all-amplitude validity. |
| `RESULT-0003` | `results/EXP-0001/RUN-0002/result.yaml` | `VALID_IN_RANGE` | train `0.0100` to `1.1002` rad; test `1.1080` to `1.5708` rad | Verification passed; best scored model `model_theta2_theta4`; theory-aware candidate `model_x_x2_log` reached test mean relative error `0.00011457753869838952` and test max relative error `0.00041721310311436014`. | Strengthens benchmark-scoped support and shows theory-aware terms can improve residuals, but still remains configured-range evidence. |
| `RESULT-0004` | `results/EXP-0001/RUN-0003/result.yaml`; `docs/results/pendulum-gauntlet-100-summary.md` | `VALID_IN_RANGE` | train `0.0100` to `1.1002` rad; test `1.1080` to `1.5708` rad | 100 deterministic candidate formulas; top leaderboard model `model_t4_x1`; test mean relative error `0.00030524596412228103`; test max relative error `0.0009480571262666894`; verdict counts `VALID` 32, `PARTIALLY_VALID` 8, `OVERFITTED` 60. | Demonstrates systematic deterministic search and limitation reporting; does not establish symbolic exactness or all-amplitude validity. |
| `RESULT-0013` | `results/EXP-0001/RUN-0005/result.yaml` | `VALID_IN_RANGE` | train `0.0100` to `2.1683` rad; test `2.1839` to `3.1000` rad | 102-candidate asymptotic refined gauntlet; best model `model_asymptotic_refined`; test mean relative error `2.7518720547918328e-05`; test max relative error `4.4037820702786206e-05`; small-angle, large-angle, near-separatrix, separatrix-alignment, log-growth, evenness, monotonicity, and dimensional checks passed. | Strongest positive repository evidence for range-aware `PARTIALLY_SUPPORTED` consideration, while still not a closed-form or exhaustive formula result. |

## Negative And Overfit Evidence

`RESULT-0017` is preserved as negative/overfit evidence:

- Artifact: `results/EXP-0001/RUN-0006/result.yaml`
- Review document: `docs/reviews/result-0017-pendulum-gate-b-replay.md`
- Review tier: `AGENT_VALIDATED`
- Gate B status: `PASS`
- Verdict: `OVERFITTED`
- Candidate count: `101`
- Best candidate: `model_t2_x4_l2`
- Range: train `0.0100` to `2.0985` rad; test `2.1135` to `3.0000` rad
- Test mean relative error: `0.004347`
- Test max relative error: `0.021261`
- Complexity score: `3`
- Replay comparison: `878` numeric metrics checked, maximum absolute numeric
  drift `6.892264536872972e-13` under tolerance `1.0e-09`, verdict unchanged
  as `OVERFITTED`.

At the time of this handoff, `RESULT-0017` has completed Gate B. It can be used
as validated negative memory about overfit behavior in this workflow, but not as
positive support for a stronger pendulum formula claim.

## CLAIM-0001 Wording Map

The existing `CLAIM-0001` wording has two separable parts:

1. The ideal mathematical pendulum period increases with amplitude.
2. The small-angle approximation alone cannot capture the period exactly.

The repository evidence is consistent with these conservative points when they
are interpreted as ideal-pendulum, benchmark-scoped, range-aware statements.
The strongest support comes from `RESULT-0013`, with earlier in-range support
from `RESULT-0001`, `RESULT-0003`, and `RESULT-0004`.

The evidence does not support the following wording:

- exact closed-form discovery by APL;
- formula validity across all amplitudes;
- real-laboratory empirical validation;
- exhaustive search over all plausible pendulum formula families;
- unqualified near-separatrix correctness outside the configured checks;
- treating `RESULT-0017` as a positive formula-validation result.

## Maintainer Decision Options

1. Leave `CLAIM-0001` in `DRAFT`.

   This is the most conservative option if maintainers want more review,
   stronger wording discipline, or external laboratory evidence before any
   status change.

2. Revise wording and keep `DRAFT`.

   Maintainers can narrow the statement to explicitly mention the ideal
   mathematical pendulum, configured benchmark ranges, and non-exact/non-all-range
   limitations while leaving status unchanged.

3. Promote after maintainer Gate C review.

   If maintainers accept range-aware wording, `PARTIALLY_SUPPORTED` is the
   safest candidate status. The promotion should cite the positive
   `VALID_IN_RANGE` evidence, especially `RESULT-0013`, and separately mention
   `RESULT-0017` as validated negative/overfit boundary evidence.

4. Defer promotion pending additional evidence.

   Maintainers can wait for external/lab data, broader amplitude sweeps, or
   additional independent review before changing claim status.

The original option to request Gate B replay first is no longer required for
`RESULT-0017`: `TASK-0757` completed the replay and recorded Gate B `PASS` with
`AGENT_VALIDATED` review tier.

## Recommended Maintainer Path

`PARTIALLY_SUPPORTED` is technically available under
`docs/claim-promotion-policy.md` if maintainers revise or explicitly interpret
the claim as range-aware and ideal-pendulum scoped. The repository should still
under-claim: no exact formula, no all-amplitude validity, no real-lab
empirical validation, and no exhaustive discovery language.

If maintainers do not want to revise the wording now, leave the claim in
`DRAFT` and use this handoff as the decision packet for a later Gate C review.

## Output Routing

- Canonical destination:
  `docs/reviews/claim-0001-pendulum-evidence-handoff.md`
- Claim impact: no claim file change; `CLAIM-0001` remains `DRAFT`.
- Knowledge impact: none.
- Result impact: none.
- Gate A status: not applicable; no new result artifact is published.
- Gate B status: `RESULT-0017` Gate B `PASS` already recorded by `TASK-0757`;
  no new replay was run for this task.
- Maintainer decision blocker: Gate C maintainer review is required for any
  `CLAIM-0001` wording or status promotion.
