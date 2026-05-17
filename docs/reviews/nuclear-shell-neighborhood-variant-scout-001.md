# Nuclear Shell-Neighborhood Variant Scout 001

**Task:** TASK-0278
**Agent run:** `AGENT-RUN-0012`
**Code reference:** `scripts/run_nuclear_shell_neighborhood_scout.py`
**Metrics:** `agent_runs/AGENT-RUN-0012/metrics.json`
**Scope:** sandbox-only residual scout; no registry, reveal, result, claim, or
knowledge promotion.

This scout generated bounded shell-neighborhood residual candidates around the
frozen `RESULT-0015` fitted semi-empirical baseline. It uses only committed
repository data and does not fetch live measurements.

## Inputs

- Frozen baseline: `results/EXP-0012/RUN-0001/result.yaml`
- Training residual slice: `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- Retrospective diagnostic holdout: `data/nuclear_masses/post_ame2020_holdout.yaml`

The post-AME2020 holdout is repository-pinned diagnostic evidence, not a
prospective reveal source. This task does not edit
`prediction_registry/nuclear_masses/`.

## Candidate Triage

Nine bounded candidates were generated. Six were executed and three were
rejected before sandbox evaluation:

| Candidate | Decision | Formula or rejection reason |
| --- | --- | --- |
| `SHELL-SCOUT-001` | executed | `r_corr = beta_z*s_z2 + beta_n*s_n2` |
| `SHELL-SCOUT-002` | executed | `r_corr = beta_n*s_n2` |
| `SHELL-SCOUT-003` | executed | `r_corr = beta_z*s_z2` |
| `SHELL-SCOUT-004` | executed | `r_corr = beta_c*(s_n2 - s_z2)` |
| `SHELL-SCOUT-005` | executed | `r_corr = beta_p*(s_z2*s_n2)` |
| `SHELL-SCOUT-006` | executed | near-null control, `r_corr = 0.0` |
| `SHELL-SCOUT-007` | rejected | N=82-only switch; post-hoc leakage risk. |
| `SHELL-SCOUT-008` | rejected | free sigma grid; nonlinear overfit risk on 11 rows. |
| `SHELL-SCOUT-009` | rejected | binary threshold sweep duplicates continuous Gaussian candidates. |

For executed candidates, `s_z2` and `s_n2` are Gaussian proximities to the
nearest magic number on the proton and neutron axes, respectively, with
`sigma = 2`.

## Method

The runner fits linear residual corrections on the 11-row NMD-0002 residual
slice and evaluates them on the pinned post-AME2020 primary holdout. It reports
MAE/RMSE by subset, with emphasis on shell-relevant slices:

- `magic_any`
- `magic_z`
- `magic_n`
- `near_magic`
- `heavy_a_ge_100`

Baseline primary MAE on the post-AME2020 holdout is `4.552568580201034 MeV`.

## Results

| Candidate | Verdict | Primary delta MAE | Magic-any delta | Near-magic delta |
| --- | --- | ---: | ---: | ---: |
| `SHELL-SCOUT-001` | `OVERFITTED` | +0.046661 | -0.259043 | +0.113324 |
| `SHELL-SCOUT-002` | `PARTIALLY_VALID` | -0.061969 | -0.399304 | -0.169340 |
| `SHELL-SCOUT-003` | `PARTIALLY_VALID` | -0.091504 | -0.323554 | -0.249196 |
| `SHELL-SCOUT-004` | `OVERFITTED` | +0.072127 | +0.008609 | +0.188883 |
| `SHELL-SCOUT-005` | `PARTIALLY_VALID` | -0.071641 | -0.279310 | -0.181235 |
| `SHELL-SCOUT-006` | `INCONCLUSIVE` | +0.000000 | +0.000000 | +0.000000 |

Additional subset notes:

- `SHELL-SCOUT-002` improves `magic_n` by `-0.591750 MeV` and leaves
  `heavy_a_ge_100` nearly unchanged at `+0.019771 MeV`.
- `SHELL-SCOUT-003` improves `magic_z` by `-0.387579 MeV`,
  `magic_n` by `-0.291542 MeV`, and `heavy_a_ge_100` by `-0.087801 MeV`.
- `SHELL-SCOUT-005` improves `magic_n` by `-0.411085 MeV` and
  `heavy_a_ge_100` by `-0.089679 MeV`.
- `SHELL-SCOUT-001` improves `magic_any` but regresses `near_magic` and the
  primary aggregate, so it is preserved as an overfit/instability result.
- `SHELL-SCOUT-004` regresses primary, `magic_any`, and `near_magic`; it is a
  negative shell-axis contrast result.
- `SHELL-SCOUT-006` is the near-null control and exactly preserves baseline
  MAE deltas at zero.

## Interpretation

The neutron-only, proton-only, and product probes show small retrospective
improvements on the pinned post-AME2020 diagnostic surface. The effect sizes are
sub-MeV and come from residual fitting on an 11-row slice, so they are scout
signals only. They are not evidence for a new nuclear mass law and should not
be promoted without a separate reviewed task.

The overfitted and near-null outcomes are useful: they constrain which shell
feature shapes appear unstable or dormant under the current residual protocol.

## Limitations

- Sandbox-only scout; no `PRED-*`, canonical result, claim, or knowledge file is
  updated.
- The NMD-0002 fitting surface has only 11 rows.
- The post-AME2020 dataset is retrospective diagnostic evidence, not a reveal.
- Verdicts are local scout labels for triage and do not imply claim promotion.
- Shell-neighborhood features are empirical residual probes, not a physical
  shell model.

## Verdict

`REVIEW_READY` for maintainer review as a sandbox shell-neighborhood scout.

No scientific claim is promoted. The best follow-up is to continue the parallel
Nuclear scout queue with TASK-0279, rather than registering new predictions from
this scout directly.
