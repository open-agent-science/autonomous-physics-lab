# AGENT_PUBLISHED Prediction Template

Use this guide when a task freezes a prospective prediction before later
reveal and should publish a canonical `PRED-*` artifact under
`review_tier: AGENT_PUBLISHED`.

Start from:

- [`prediction_registry/PRED-TEMPLATE.agent-published.yaml`](../../prediction_registry/PRED-TEMPLATE.agent-published.yaml)
- [`prediction_registry/README.md`](../../prediction_registry/README.md)
- [`docs/result-promotion-protocol.md`](../result-promotion-protocol.md)

## Required Boundary

An `AGENT_PUBLISHED` prediction means:

- the entry is a frozen prospective registration;
- it is not a claim;
- it is not a scored result;
- it is not independently validated or maintainer-reviewed yet.

Keep this qualifier visible in the PR summary, prediction limitations, and
output routing section.

## Gate A Checklist

Before opening the PR, replace every placeholder and set each applicable
`agent_proposal_evaluation.gates_checked` key honestly:

- `no_peek_state`
- `frozen_model_reference`
- `named_target_set`
- `reveal_conditions_explicit`
- `non_claim_ceiling`
- `live_external_fetch_disabled`
- `schema_validation_passes`
- `no_forbidden_overclaim_wording`

If any required gate is false, do not publish the prediction as a live
`PRED-*`. Report the publication as blocked and keep the work as a draft or
task proposal.

## PR Output Routing

Use this shape in the PR body:

```text
Task verdict: not_applicable
Canonical destination: prediction_registry/<domain>/PRED-XXXX.yaml
Review tier: AGENT_PUBLISHED
Gate A status: pass
Gate B status: not applicable
Claim impact: no claim status transition
Knowledge impact: no knowledge promotion
Limitations / blockers: <source, target, uncertainty, and reveal limits>
```
