# Agent Run AGENT-RUN-0012 - Shell-Neighborhood Nuclear Scout

**Task:** `TASK-0278`
**Status:** `SANDBOX_COMPLETE`
**Claim boundary:** sandbox-only; no canonical result, claim, knowledge, or
prediction registry artifact is updated.

## Scope

This run evaluates bounded shell-neighborhood residual probes around magic
numbers using the frozen `RESULT-0015` fitted semi-empirical baseline. It is a
follow-up scout, not a reveal workflow and not a registry expansion.

Nine candidates were generated. Six were executed and three were rejected
before sandbox evaluation:

| Candidate | Decision | Formula / reason |
| --- | --- | --- |
| `SHELL-SCOUT-001` | executed | `r_corr = beta_z*s_z2 + beta_n*s_n2` |
| `SHELL-SCOUT-002` | executed | `r_corr = beta_n*s_n2` |
| `SHELL-SCOUT-003` | executed | `r_corr = beta_z*s_z2` |
| `SHELL-SCOUT-004` | executed | `r_corr = beta_c*(s_n2 - s_z2)` |
| `SHELL-SCOUT-005` | executed | `r_corr = beta_p*(s_z2*s_n2)` |
| `SHELL-SCOUT-006` | executed | near-null control, `r_corr = 0.0` |
| `SHELL-SCOUT-007` | rejected | N=82-only switch, post-hoc leakage risk |
| `SHELL-SCOUT-008` | rejected | free sigma grid, nonlinear overfit risk |
| `SHELL-SCOUT-009` | rejected | binary threshold sweep duplicate |

## Method

`scripts/run_nuclear_shell_neighborhood_scout.py` fits each executed linear
correction on the NMD-0002 residual slice and evaluates it on the pinned
post-AME2020 primary holdout. Metrics are reported for the primary set and
shell-relevant subsets (`magic_any`, `magic_z`, `magic_n`, `near_magic`,
`heavy_a_ge_100`).

## Results

Baseline post-AME2020 primary MAE: `4.552568580201034 MeV`.

| Candidate | Verdict | Primary delta MAE | Magic-any delta | Near-magic delta |
| --- | --- | ---: | ---: | ---: |
| `SHELL-SCOUT-001` | `OVERFITTED` | +0.046661 | -0.259043 | +0.113324 |
| `SHELL-SCOUT-002` | `PARTIALLY_VALID` | -0.061969 | -0.399304 | -0.169340 |
| `SHELL-SCOUT-003` | `PARTIALLY_VALID` | -0.091504 | -0.323554 | -0.249196 |
| `SHELL-SCOUT-004` | `OVERFITTED` | +0.072127 | +0.008609 | +0.188883 |
| `SHELL-SCOUT-005` | `PARTIALLY_VALID` | -0.071641 | -0.279310 | -0.181235 |
| `SHELL-SCOUT-006` | `INCONCLUSIVE` | +0.000000 | +0.000000 | +0.000000 |

## Interpretation

The neutron-only, proton-only, and double-neighborhood product probes improve
aggregate and shell-neighborhood MAE slightly on this retrospective diagnostic
surface. The paired Z+N and contrast variants regress at least one key subset
and are marked `OVERFITTED`. The near-null control preserves the expected zero
delta.

These are small retrospective residual shifts, not predictive evidence. Any
future selection would need a separate reviewed task, broader source review, and
explicit no-claim wording.
