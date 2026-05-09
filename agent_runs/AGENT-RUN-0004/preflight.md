# Preflight - AGENT-RUN-0004

## Campaign Scope

- Campaign profile: `campaign_profiles/anharmonic-oscillator.yaml`
- Autonomy status: `WHITELISTED_LIMITED`
- Claim ceiling: sandbox-only
- Promotion boundary: no canonical result and no claim promotion

## Proposal Checks

- Generated hypothesis proposals: `6`
- Executed hypothesis proposals: `2`
- Rejected before execution: `4`
- Experiment proposal: `experiment_proposals/anharmonic/EXP-PROPOSAL-0004-anharmonic-sandbox-batch.yaml`

## Quality Gate

| Check | Status | Notes |
| --- | --- | --- |
| Campaign scope | `PASS` | Uses the bounded anharmonic benchmark profile and the canonical EXP-0011 slice definition. |
| Claim ceiling | `PASS` | All proposal files and the run manifest are sandbox-only. |
| Input references | `PASS` | References the campaign profile, EXP-0011, RESULT-0014, and research-quality docs. |
| Method | `PASS` | Reuses the deterministic anharmonic reference helpers from `physics_lab.engines.anharmonic_oscillator`. |
| Metrics | `PASS` | Records train, holdout, stress, rejection count, and comparison to the current canonical holdout metric. |
| Triage budget | `PASS` | Executes exactly two candidates and rejects four before sandbox execution. |
| Limitations | `PASS` | States sandbox-only scope and the need for a later canonical comparison task. |
| Promotion boundary | `PASS` | Does not change canonical `results/`, `claims/`, `hypotheses/`, `experiments/`, or `knowledge/`. |

## Status

`PASS`
