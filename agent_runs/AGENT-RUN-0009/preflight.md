# Preflight - AGENT-RUN-0009

## Campaign Scope

- Campaign profile: `campaign_profiles/nuclear-mass-surface.yaml`
- Autonomy status: `WHITELISTED_LIMITED`
- Claim ceiling: sandbox-only
- Promotion boundary: no canonical result and no claim promotion

## Proposal Checks

- Generated hypothesis proposals: `5`
- Executed hypothesis proposals: `2` (`HYP-PROPOSAL-0028`, `HYP-PROPOSAL-0029`)
- Rejected before execution: `3` (`HYP-PROPOSAL-0030`, `HYP-PROPOSAL-0031`, `HYP-PROPOSAL-0032`)
- Experiment proposal: `experiment_proposals/nuclear-mass/EXP-PROPOSAL-0006-nuclear-shell-batch.yaml`

## Quality Gate

| Check | Status | Notes |
| --- | --- | --- |
| Campaign scope | `PASS` | Uses the nuclear-mass profile, the pinned measured slice, the reviewed holdout protocol, and the reviewed row-level post-AME2020 holdout. |
| Claim ceiling | `PASS` | All proposal files and the run manifest are sandbox-only. |
| Input references | `PASS` | References RESULT-0015, NMD-0002, the post-AME2020 holdout dataset, AGENT-RUN-0006, AGENT-RUN-0008, the holdout protocol, and the robustness gate. |
| Method | `PASS` | Deterministic NMD-0002 4-holdout cross-validation and a single full-NMD-0002 fit for the post-AME2020 evaluation. Shell-proximity Gaussian width is frozen at design time. |
| Metrics | `PASS` | Records per-holdout MAE and RMSE deltas, feature activation counts on 295 post-AME2020 rows, per-subset MAE on the time-split surface, and the comparison boundary to RESULT-0015. |
| Triage budget | `PASS` | Executes exactly two candidates and rejects three before sandbox execution. |
| Leakage review | `PASS` | `HYP-PROPOSAL-0031` was explicitly rejected because it would memorize the post-AME2020 In/Sb N=82 cluster. The two executed features use symmetric magic-number proximity and are independent of any retrospective worst-residual list. |
| Limitations | `PASS` | States sandbox-only scope, tiny-slice limits, and the need for a later canonical comparison task. |
| Promotion boundary | `PASS` | Does not change canonical `results/`, `claims/`, `hypotheses/`, `experiments/`, `knowledge/`, or datasets. |

## Status

`PASS`
