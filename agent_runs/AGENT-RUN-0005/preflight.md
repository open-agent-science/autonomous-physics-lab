# Preflight - AGENT-RUN-0005

## Campaign Scope

- Campaign profile: `campaign_profiles/nuclear-mass-surface.yaml`
- Autonomy status: `WHITELISTED_LIMITED`
- Claim ceiling: sandbox-only
- Promotion boundary: no canonical result and no claim promotion

## Proposal Checks

- Generated hypothesis proposals: `8`
- Executed hypothesis proposals: `3`
- Rejected before execution: `5`
- Experiment proposal: `experiment_proposals/nuclear-mass/EXP-PROPOSAL-0005-nuclear-mass-sandbox-batch.yaml`

## Quality Gate

| Check | Status | Notes |
| --- | --- | --- |
| Campaign scope | `PASS` | Uses the bounded nuclear-mass profile, the pinned measured slice, and the reviewed holdout protocol. |
| Claim ceiling | `PASS` | All proposal files and the run manifest are sandbox-only. |
| Input references | `PASS` | References the campaign profile, holdout protocol, frozen baseline result, and research-quality docs. |
| Method | `PASS` | Reuses deterministic binding-energy residual calculations from `physics_lab.engines.nuclear_masses` and `physics_lab.engines.nuclear_mass_baselines`. |
| Metrics | `PASS` | Records per-holdout MAE and RMSE deltas, triage counts, and the comparison boundary to `RESULT-0015`. |
| Triage budget | `PASS` | Executes exactly three candidates and rejects five before sandbox execution. |
| Limitations | `PASS` | States sandbox-only scope, tiny-slice limits, and the need for a later canonical comparison task. |
| Promotion boundary | `PASS` | Does not change canonical `results/`, `claims/`, `hypotheses/`, `experiments/`, `knowledge/`, or datasets. |

## Status

`PASS`
