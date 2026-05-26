# AGENT_PUBLISHED Result Template

Use this guide when a task produced a deterministic engine run that should be
published as a canonical `RESULT-*` artifact under
`review_tier: AGENT_PUBLISHED`.

Start from:

- [`results/RESULT-TEMPLATE.agent-published.yaml`](../../results/RESULT-TEMPLATE.agent-published.yaml)
- [`docs/result-promotion-protocol.md`](../result-promotion-protocol.md)

## Required Boundary

An `AGENT_PUBLISHED` result means:

- the artifact is agent-published evidence;
- it is not yet independently replayed by a second agent;
- it is not maintainer-reviewed interpretation;
- it does not promote a claim by itself.

Keep this qualifier visible in the PR summary, result limitations, and output
routing section.

## Gate A Checklist

Before opening the PR, replace every placeholder and set each applicable
`agent_proposal_evaluation.gates_checked` key honestly:

- `deterministic_run`
- `verification_block_populated`
- `input_hashes_recorded`
- `limitations_listed`
- `engine_version_and_commit_pinned`
- `schema_validation_passes`
- `no_protected_artifact_rewrite`
- `no_forbidden_overclaim_wording`
- `dataset_provenance_valid`

If any required gate is false, do not publish the result as a live `RESULT-*`.
Report the publication as blocked and leave the evidence in the appropriate
sandbox or review artifact.

## PR Output Routing

Use this shape in the PR body:

```text
Task verdict: <VALID | VALID_IN_RANGE | PARTIALLY_VALID | INCONCLUSIVE | OVERFITTED | FALSIFIED>
Canonical destination: results/EXP-XXXX/RUN-XXXX/result.yaml
Review tier: AGENT_PUBLISHED
Gate A status: pass
Gate B status: not attempted
Claim impact: no claim status transition
Knowledge impact: no knowledge promotion
Limitations / blockers: <scope limits and any remaining replay needs>
```
