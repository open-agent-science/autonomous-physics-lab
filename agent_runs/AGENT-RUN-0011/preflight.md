# Preflight - AGENT-RUN-0011

## Campaign Scope

- Campaign profile: `campaign_profiles/nuclear-mass-surface.yaml`
- Autonomy status: `WHITELISTED_LIMITED`
- Claim ceiling: sandbox-only
- Promotion boundary: no canonical result and no claim promotion

## Proposal Checks

- Generated hypothesis proposals: `5`
- Executed hypothesis proposals: `2` (`HYP-PROPOSAL-0038`, `HYP-PROPOSAL-0041`)
- Rejected before execution: `3` (`HYP-PROPOSAL-0039`, `HYP-PROPOSAL-0040`, `HYP-PROPOSAL-0042`)
- Experiment proposal: `experiment_proposals/nuclear-mass/EXP-PROPOSAL-0008-nuclear-pairing-batch.yaml`
- In-batch negative control: `HYP-PROPOSAL-0041`

## Quality Gate

| Check | Status | Notes |
| --- | --- | --- |
| Campaign scope | `PASS` | Uses the nuclear-mass profile, the pinned measured slice, the reviewed structured-holdout protocol, and the reviewed row-level post-AME2020 holdout. |
| Claim ceiling | `PASS` | All proposal files and the run manifest are sandbox-only. |
| Input references | `PASS` | References RESULT-0015, NMD-0002, the post-AME2020 holdout dataset, AGENT-RUN-0006, AGENT-RUN-0008 (HYP-PROPOSAL-0022 negative-control reference), AGENT-RUN-0009, AGENT-RUN-0010, the holdout protocol, and the robustness gate. |
| Method | `PASS` | Deterministic NMD-0002 4-holdout cross-validation and a single full-NMD-0002 fit for the post-AME2020 evaluation. Linear-additive corrections only; no nonlinear knobs, no per-shell or per-chain indicators, no per-row indicators. |
| Metrics | `PASS` | Records per-holdout MAE/RMSE deltas, feature activation counts on 295 post-AME2020 rows (including per-class counts for HYP-PROPOSAL-0041), per-subset MAE (adding `even_even` and `odd_odd` subsets relative to the neutron-rich lane), uncertainty-normalized error, and the external HYP-PROPOSAL-0022 negative-control comparison. |
| Triage budget | `PASS` | Executes exactly two candidates and rejects three before sandbox execution. |
| Leakage review | `PASS` | `HYP-PROPOSAL-0040` (N=82 pairing override) and `HYP-PROPOSAL-0042` (per-nuclide override) explicitly rejected because they would memorize the `AGENT-RUN-0008` worst-residual cluster or directly memorize rows. `HYP-PROPOSAL-0039` rejected on complexity (free-power nonlinear knob). Executed features are a single linear A-inverse term and three orthogonal one-hot parity-class indicators; neither targets a specific shell, chain, or nuclide. |
| Subset failure criterion | `PASS` | Per-subset MAE and feature activation are recorded for every executed candidate; aggregate MAE is not used as the sole verdict signal. The pairing lane adds `even_even` and `odd_odd` subsets so per-class behavior is auditable. |
| In-batch negative control | `PASS` | `HYP-PROPOSAL-0041` is recorded as the in-batch negative control. The observed structured verdict is `OVERFITTED`, confirming overfit detection is symmetric in this lane. |
| Limitations | `PASS` | States sandbox-only scope, tiny-slice training risk, retrospective time-split caveat, A-inverse sign-colinearity with the baseline pairing term, and one-row anchoring of `c_oo` for the in-batch negative control. |
| Promotion boundary | `PASS` | Does not change canonical `results/`, `claims/`, `hypotheses/`, `experiments/`, `knowledge/`, or datasets. |

## Status

`PASS`
