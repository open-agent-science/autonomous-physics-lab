# Autonomous Pendulum Pilot 01

## Scope

This is the first sandbox-only autonomous research pilot for the pendulum
formula falsification campaign.

It uses:

- `campaign_profiles/pendulum-formula-falsification.yaml`
- `docs/autonomous-research-loop.md`
- `docs/research-quality-gate.md`
- `agent_runs/`
- `hypothesis_proposals/pendulum/`
- `experiment_proposals/pendulum/`

No canonical `claims/`, `hypotheses/`, `experiments/`, `knowledge/`, or
`results/` files are changed.

## Proposal Triage

| Proposal | Status | Decision | Reason |
| --- | --- | --- | --- |
| `HYP-PROPOSAL-0001` rational x-pole | `REVIEW_READY` | Executed | Bounded rational family is related to PFF-001 and not covered by the linear gauntlet. |
| `HYP-PROPOSAL-0002` theta2 baseline | `REVIEW_READY` | Executed | Useful negative-control candidate for preserving failed sandbox evidence. |
| `HYP-PROPOSAL-0003` odd-theta term | `REJECTED` | Not executed | Violates the expected even symmetry of the ideal pendulum period ratio. |
| `HYP-PROPOSAL-0004` free-pole rational | `REJECTED` | Not executed | Unbounded pole search is too unstable for the first pilot without stronger constraints. |
| `HYP-PROPOSAL-0005` high-degree theta polynomial | `REJECTED` | Not executed | Duplicates known gauntlet territory and adds complexity without a clear novelty case. |

This satisfies the pilot constraint of at least five generated proposals, at
least three explicit rejections, and at most two sandbox executions.

## Sandbox Executions

### AGENT-RUN-0001

Candidate:

`(1 + a*x) / (1 - b*x)`, where `x = sin^2(theta/2)`.

Fitted coefficients:

- `a = -0.3433549926706056`
- `b = 0.5926785232733237`

| Slice | Mean relative error | Max relative error |
| --- | ---: | ---: |
| Train | `1.119074e-05` | `4.484870e-05` |
| Test | `8.588075e-04` | `2.681596e-03` |
| Stress | `6.102625e-02` | `2.228621e-01` |

Verdict:

`SANDBOX_PASS`

Review note:

The candidate beats the theta2 negative baseline on the configured test slice,
but it does not beat the current `t4_x1` reference candidate. It should remain
sandbox memory unless a maintainer wants a later rational-family gauntlet task.

### AGENT-RUN-0002

Candidate:

`1 + a*theta^2`.

Fitted coefficient:

- `a = 0.06582273609859844`

| Slice | Mean relative error | Max relative error |
| --- | ---: | ---: |
| Train | `4.383396e-04` | `1.552664e-03` |
| Test | `6.937606e-03` | `1.515048e-02` |
| Stress | `9.325947e-02` | `2.497787e-01` |

Verdict:

`SANDBOX_FAIL`

Review note:

This is retained as negative sandbox evidence. It shows the pilot can preserve
failed candidates instead of reporting only positive-looking outputs.

## Preflight Summary

All selected proposals include:

- campaign profile id;
- assumptions;
- variables or parameter definitions;
- exact reference or baseline plan;
- failure criteria;
- limitations;
- overclaim-risk handling;
- explicit promotion boundary.

The rejected proposals are still proposal files so reviewers can audit what was
excluded and why.

## Maintainer Decision Requested

Recommended outcome:

- retain both agent runs as sandbox evidence;
- do not promote claims or canonical results;
- treat the rational candidate as optional future follow-up, not as a public
  success story;
- use this PR as the first test of the autonomous research loop and sandbox
  evidence layout.

## Promotion Boundary

This pilot does not create canonical scientific evidence. Any future promotion
would require a separate maintainer-reviewed task that creates a canonical
experiment and reproducible `RESULT-*` artifact.
