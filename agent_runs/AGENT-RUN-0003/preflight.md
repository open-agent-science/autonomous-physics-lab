# Preflight - AGENT-RUN-0003

## Campaign Scope

- Campaign profile: `campaign_profiles/dimensional-analysis-validator.yaml`
- Autonomy status: `WHITELISTED_LIMITED`
- Claim ceiling: sandbox-only
- Promotion boundary: no canonical result and no claim promotion

## Proposal Checks

- Generated hypothesis proposals: `8`
- Executed hypothesis proposals: `5`
- Rejected before execution: `3`
- Experiment proposal: `experiment_proposals/dimensional-analysis/EXP-PROPOSAL-0003-validator-boundary-batch.yaml`

## Quality Gate

| Check | Status | Notes |
| --- | --- | --- |
| Campaign scope | `PASS` | Uses the whitelisted dimensional-analysis validator profile. |
| Claim ceiling | `PASS` | All proposal files and run manifest are sandbox-only. |
| Input references | `PASS` | References profile, quality gate, current challenge set, and relevant notes. |
| Method | `PASS` | Uses `physics_lab.engines.dimensions.validate_item`. |
| Metrics | `PASS` | Records expected verdict, observed verdict, agreement, and rejection count. |
| Failure conditions | `PASS` | Records duplicate, scope, and semantic-boundary failures. |
| Baseline or null | `PASS` | Uses current challenge-set expected-verdict baseline and SI validator behavior. |
| Limitations | `PASS` | Names MVP, known-limit, and sandbox-only limits. |
| Promotion boundary | `PASS` | Does not change canonical `results/`, `claims/`, `hypotheses/`, `experiments/`, or `knowledge/`. |

## Status

`PASS`
