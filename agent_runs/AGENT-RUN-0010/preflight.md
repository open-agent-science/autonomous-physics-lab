# Preflight - AGENT-RUN-0010

## Campaign Scope

- Campaign profile: `campaign_profiles/nuclear-mass-surface.yaml`
- Autonomy status: `WHITELISTED_LIMITED`
- Claim ceiling: sandbox-only
- Promotion boundary: no canonical result and no claim promotion

## Proposal Checks

- Generated hypothesis proposals: `5`
- Executed hypothesis proposals: `2` (`HYP-PROPOSAL-0033`, `HYP-PROPOSAL-0034`)
- Rejected before execution: `3` (`HYP-PROPOSAL-0035`, `HYP-PROPOSAL-0036`, `HYP-PROPOSAL-0037`)
- Experiment proposal: `experiment_proposals/nuclear-mass/EXP-PROPOSAL-0007-nuclear-neutron-rich-batch.yaml`

## Quality Gate

| Check | Status | Notes |
| --- | --- | --- |
| Campaign scope | `PASS` | Uses the nuclear-mass profile, the pinned measured slice, the reviewed structured-holdout protocol, and the reviewed row-level post-AME2020 holdout. |
| Claim ceiling | `PASS` | All proposal files and the run manifest are sandbox-only. |
| Input references | `PASS` | References RESULT-0015, NMD-0002, the post-AME2020 holdout dataset, AGENT-RUN-0006, AGENT-RUN-0008 (HYP-PROPOSAL-0022 negative-control reference), the holdout protocol, and the robustness gate. |
| Method | `PASS` | Deterministic NMD-0002 4-holdout cross-validation and a single full-NMD-0002 fit for the post-AME2020 evaluation. No nonlinear knobs and no per-shell or per-chain indicators. |
| Metrics | `PASS` | Records per-holdout MAE/RMSE deltas, feature activation counts on 295 post-AME2020 rows, per-subset MAE (including `neutron_rich_delta_ge_20` and `neutron_rich_delta_ge_30`), uncertainty-normalized error, and the negative-control reference comparison to HYP-PROPOSAL-0022. |
| Triage budget | `PASS` | Executes exactly two candidates and rejects three before sandbox execution. |
| Leakage review | `PASS` | `HYP-PROPOSAL-0035` (In/Sb chain) and `HYP-PROPOSAL-0037` (per-shell N=50/82/126 stack) explicitly rejected because they would memorize the `AGENT-RUN-0008` worst-residual cluster. Executed features are symmetric polynomials in `I = (N-Z)/A` or `max(N-Z, 0)^2 / A`; neither targets a specific shell or chain. |
| Subset failure criterion | `PASS` | Per-subset MAE and feature activation are recorded for every executed candidate; aggregate MAE is not used as the sole verdict signal. |
| Limitations | `PASS` | States sandbox-only scope, tiny-slice training risk, retrospective time-split caveat, and the asymmetric-by-design construction of HYP-PROPOSAL-0034. |
| Promotion boundary | `PASS` | Does not change canonical `results/`, `claims/`, `hypotheses/`, `experiments/`, `knowledge/`, or datasets. |

## Status

`PASS`
