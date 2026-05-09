# Autonomous Dimensional Validator Pilot 01

## Scope

This is the second sandbox-only autonomous research pilot. It tests whether the
repository-native autonomous loop generalizes beyond pendulum work to the
dimensional-analysis validator campaign.

It uses:

- `campaign_profiles/dimensional-analysis-validator.yaml`
- `docs/autonomous-research-loop.md`
- `docs/research-quality-gate.md`
- `hypothesis_proposals/dimensional-analysis/`
- `experiment_proposals/dimensional-analysis/`
- `agent_runs/AGENT-RUN-0003/`

No canonical `claims/`, `hypotheses/`, `experiments/`, `knowledge/`, or
`results/` files are changed.

## Proposal Triage

| Proposal | Status | Decision | Reason |
| --- | --- | --- | --- |
| `HYP-PROPOSAL-0006` RC time constant | `REVIEW_READY` | Executed | Low-risk VALID item using supported derived units. |
| `HYP-PROPOSAL-0007` LC angular frequency | `REVIEW_READY` | Executed | Exercises sqrt handling over derived SI units. |
| `HYP-PROPOSAL-0008` distance plus velocity | `REVIEW_READY` | Executed | Clear INVALID negative-control item. |
| `HYP-PROPOSAL-0009` dimensionless ratio | `REVIEW_READY` | Executed | Checks SUSPICIOUS boundary for dimensionless-only variables. |
| `HYP-PROPOSAL-0010` projectile range limit fail | `REVIEW_READY` | Executed | Demonstrates KNOWN_LIMIT_FAIL boundary where dimensions alone pass. |
| `HYP-PROPOSAL-0011` Compton wavelength | `REJECTED` | Not executed | Duplicate-shaped candidate overlapping the physical constants verification track. |
| `HYP-PROPOSAL-0012` natural-unit E = m | `REJECTED` | Not executed | Outside current SI-focused profile scope. |
| `HYP-PROPOSAL-0013` Rayleigh-Jeans approximation | `REJECTED` | Not executed | Cross-track duplicate risk with approximation-breakdown work. |

This satisfies the pilot constraint of at least five generated proposals and
explicit duplicate or weak-item rejection before sandbox execution.

## Sandbox Execution

The selected five items were executed through
`physics_lab.engines.dimensions.validate_item` and stored under
`agent_runs/AGENT-RUN-0003/metrics.json`.

| Item | Expected | Observed | Agreement |
| --- | --- | --- | --- |
| RC time constant | `VALID` | `VALID` | yes |
| LC angular frequency | `VALID` | `VALID` | yes |
| Distance plus velocity | `INVALID` | `INVALID` | yes |
| Dimensionless ratio | `SUSPICIOUS` | `SUSPICIOUS` | yes |
| Projectile range missing angle dependence | `KNOWN_LIMIT_FAIL` | `VALID` | yes, by known-limit relaxed rule |

The projectile-range row is the most important limitation check. It keeps the
dimension-only result (`VALID`) separate from the curated expected label
(`KNOWN_LIMIT_FAIL`), so the pilot does not imply that dimensional consistency
is enough for physical correctness.

## Metrics

- Generated proposals: `8`
- Executed sandbox classifications: `5`
- Rejected before execution: `3`
- Agreement count under current validator agreement rules: `5/5`
- Canonical result artifacts changed: `false`
- Claim artifacts changed: `false`

## Preflight Summary

The pilot passes the research quality gate:

- campaign profile id is recorded;
- claim ceiling is sandbox-only;
- input references and code references are named;
- expected and observed verdicts are separated;
- duplicate, scope, and semantic-boundary rejections are explicit;
- no canonical result, claim, hypothesis, experiment, or accepted knowledge is changed.

## Maintainer Decision Requested

Recommended outcome:

- retain `AGENT-RUN-0003` as sandbox evidence;
- do not promote claims or canonical results;
- optionally open a later curation task for one or more executed items;
- treat the rejected proposals as useful autonomy-loop evidence, not failed
  science.

## Promotion Boundary

This pilot does not create canonical scientific evidence. Any future promotion
requires a separate maintainer-reviewed task that updates canonical challenge
memory or creates a reproducible `RESULT-*` artifact.
