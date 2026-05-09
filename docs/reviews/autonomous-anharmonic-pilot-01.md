# Autonomous Anharmonic Pilot 01

## Scope

This is the first sandbox-only autonomous research pilot for the anharmonic
oscillator benchmark. It tests whether the repository-native autonomous loop
can generalize from pendulum and dimensional-validator work to the new
nonlinear mechanics surface added by `EXP-0011`.

It uses:

- `campaign_profiles/anharmonic-oscillator.yaml`
- `experiments/EXP-0011-anharmonic-oscillator-period.yaml`
- `results/EXP-0011/RUN-0001/result.yaml`
- `hypothesis_proposals/anharmonic/`
- `experiment_proposals/anharmonic/`
- `agent_runs/AGENT-RUN-0004/`

No canonical `claims/`, `hypotheses/`, `experiments/`, `knowledge/`, or
`results/` files are changed.

## Proposal Triage

| Proposal | Status | Decision | Reason |
| --- | --- | --- | --- |
| `HYP-PROPOSAL-0014` Pade epsilon ratio | `REVIEW_READY` | Executed | New ratio-aware family with a direct comparison path to `RESULT-0014`. |
| `HYP-PROPOSAL-0015` amplitude-squared collapse | `REVIEW_READY` | Executed | Purpose-built negative control for benchmark-axis collapse. |
| `HYP-PROPOSAL-0016` cubic epsilon extension | `REJECTED` | Not executed | High-overlap train-fit extension that would spend pilot budget on a narrow family tweak. |
| `HYP-PROPOSAL-0017` negative-lambda softening | `REJECTED` | Not executed | Outside the current positive-`lambda` campaign profile. |
| `HYP-PROPOSAL-0018` quartic-only collapse | `REJECTED` | Not executed | Redundant once one axis-collapse negative control is already selected. |
| `HYP-PROPOSAL-0019` critical-pole epsilon | `REJECTED` | Not executed | Adds singularity framing that the first bounded-slice anharmonic pilot does not need. |

This satisfies the pilot requirement of at least five generated proposals and
explicit rejection of weak or out-of-scope items before sandbox execution.

## Sandbox Execution

The selected two candidates were executed against the deterministic `EXP-0011`
reference surface and stored in `agent_runs/AGENT-RUN-0004/metrics.json`.

| Candidate | Expected | Observed | Agreement | Holdout mean rel. error |
| --- | --- | --- | --- | ---: |
| Pade epsilon ratio | `VALID` | `VALID` | yes | `0.000123` |
| Amplitude-squared collapse | `OVERFITTED` | `OVERFITTED` | yes | `0.050361` |

The first row is the most interesting sandbox observation: the Pade family
beats the current canonical holdout mean from `RESULT-0014`, but only inside
sandbox evidence. The second row is the most important negative result: a
candidate that drops `lambda` does not generalize and is correctly preserved as
negative evidence instead of being filtered away.

## Metrics

- Generated proposals: `6`
- Executed sandbox candidates: `2`
- Rejected before execution: `4`
- Stronger-than-current-canonical holdout candidates: `1`
- Negative or partial executed candidates: `1`
- Canonical result artifacts changed: `false`
- Claim artifacts changed: `false`

## Preflight Summary

The pilot passes the shared research quality gate:

- campaign profile id is recorded;
- claim ceiling is sandbox-only;
- input references and code references are named;
- train, holdout, and stress metrics are reported;
- rejected proposals have explicit triage reasons; and
- no canonical result, claim, hypothesis, experiment, or accepted knowledge is changed.

## Maintainer Decision Requested

Recommended outcome:

- retain `AGENT-RUN-0004` as sandbox evidence;
- do not promote claims or canonical results;
- keep `HYP-PROPOSAL-0015` as negative evidence that the benchmark rejects axis-collapse families;
- consider a later canonical comparison task for `HYP-PROPOSAL-0014` if a maintainer wants to widen the benchmark family set.

## Promotion Boundary

This pilot does not create canonical scientific evidence. Any future promotion
requires a separate maintainer-reviewed task that updates canonical benchmark
memory or creates a reproducible `RESULT-*` artifact.
