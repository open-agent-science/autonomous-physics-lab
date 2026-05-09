# Agent Run AGENT-RUN-0004 - Anharmonic Autonomous Pilot

## Scope

This sandbox run tests whether the autonomous research loop generalizes to the
anharmonic oscillator benchmark after `EXP-0011` was added in `TASK-0159`.

It uses:

- `campaign_profiles/anharmonic-oscillator.yaml`
- `hypothesis_proposals/anharmonic/`
- `experiment_proposals/anharmonic/EXP-PROPOSAL-0004-anharmonic-sandbox-batch.yaml`
- `physics_lab.engines.anharmonic_oscillator`

It is not a canonical result and does not update `RESULT-0014`, any claim, any
accepted knowledge note, or the canonical anharmonic experiment definition.

## Proposal Triage

| Proposal | Status | Decision | Reason |
| --- | --- | --- | --- |
| `HYP-PROPOSAL-0014` Pade epsilon ratio | `REVIEW_READY` | Executed | New ratio-aware family with a clear comparison to `RESULT-0014`. |
| `HYP-PROPOSAL-0015` amplitude-squared collapse | `REVIEW_READY` | Executed | Negative control that intentionally ignores `lambda` and should fail outside the train slice. |
| `HYP-PROPOSAL-0016` cubic epsilon extension | `REJECTED` | Not executed | High-overlap train-fit extension that does not teach enough for the first two-execution pilot. |
| `HYP-PROPOSAL-0017` negative-lambda softening | `REJECTED` | Not executed | Outside the positive-`lambda` benchmark scope. |
| `HYP-PROPOSAL-0018` quartic-only collapse | `REJECTED` | Not executed | Redundant with the chosen axis-collapse negative control. |
| `HYP-PROPOSAL-0019` critical-pole epsilon | `REJECTED` | Not executed | Adds unnecessary singularity framing to a bounded low-overclaim pilot. |

This satisfies the pilot constraint of generating at least five proposals and
explicitly rejecting weak, redundant, or out-of-scope items before sandbox
execution.

## Sandbox Execution

Both executed candidates replay the deterministic `EXP-0011` reference surface
on the same train, holdout, and stress slices used by `RESULT-0014`.

| Candidate | Expected | Observed | Holdout mean rel. error | Stress mean rel. error | Detail |
| --- | --- | --- | ---: | ---: | --- |
| Pade epsilon ratio | `VALID` | `VALID` | `0.000123` | `0.001146` | Beats the current canonical holdout mean (`0.001102`) inside sandbox evidence only. |
| Amplitude-squared collapse | `OVERFITTED` | `OVERFITTED` | `0.050361` | `0.103366` | Confirms that collapsing the `lambda` axis does not generalize. |

The second row is the required negative result. It shows that the benchmark
surface is rich enough to reject a candidate that looks loosely plausible on a
very narrow train slice.

## Metrics

- Generated proposals: `6`
- Executed sandbox candidates: `2`
- Rejected before execution: `4`
- Stronger-than-current-canonical holdout candidates: `1`
- Negative or partial executed candidates: `1`
- Canonical result artifacts changed: `false`
- Claim artifacts changed: `false`

## Verdict

`SANDBOX_PASS`

The pilot shows that the autonomous loop can now:

- propose a new anharmonic candidate family;
- preserve a negative control as useful sandbox evidence;
- reject scope-expanding and duplicate-shaped ideas before execution; and
- package the outcome without touching canonical scientific memory.
