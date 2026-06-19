# Nuclear F6 Wigner-Cusp No-Leakage Sprint

- Task: `TASK-0777`
- Agent run: `AGENT-RUN-0075`
- Verdict: `NEGATIVE_RESULT`
- Evidence class: retrospective sandbox-only

## Method

The predeclared candidate is `beta / (1 + abs(N-Z))`. Beta is fitted only
on the frozen NMD-0003 training partition. The candidate is compared with
asymmetry-only, deterministic matched-random, and smooth-A controls.

## MAE Panels (MeV)

| panel | baseline | candidate | asymmetry | matched random | smooth A |
| --- | ---: | ---: | ---: | ---: | ---: |
| `training` | `1.822262` | `1.827482` | `1.822262` | `1.829247` | `1.822449` |
| `validation` | `1.899279` | `1.904425` | `1.899279` | `1.910896` | `1.899484` |
| `full_known` | `1.845344` | `1.850542` | `1.845344` | `1.852867` | `1.845536` |
| `post_ame2020_holdout` | `2.438877` | `2.437756` | `2.438877` | `2.437141` | `2.438869` |

## Coefficient Stability

- beta: `1.031739683` MeV
- LOO folds: `1617`
- relative std: `0.00883461`
- sign flips: `0`
- stable: `True`

## Verdict Rationale

- candidate vs control_asymmetry_only: -0.005198 MeV
- candidate vs control_matched_random: +0.002325 MeV
- candidate vs control_smooth_a: -0.005006 MeV
- Candidate does not beat every declared control by 0.25 MeV.

## No-Leakage Audit

- Candidate and controls use deterministic `Z`, `N`, `A` functions only.
- Validation and post-AME2020 rows are excluded from coefficient fitting.
- No target residual, candidate-fit residual, source-status, or live data enters a feature.
- All audit checks passed.

## Output Routing

- Canonical destination: `agent_runs/AGENT-RUN-0075/` and this review note.
- Review tier: `none`.
- Gate A: not attempted.
- Gate B: not attempted.
- Claim impact: none.
- Knowledge impact: none.
- Promotion blocker: sandbox-only task; separate authorization required.
