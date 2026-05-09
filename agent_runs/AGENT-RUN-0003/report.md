# Agent Run AGENT-RUN-0003 - Dimensional Validator Pilot

## Scope

This sandbox run tests whether the autonomous research loop generalizes from
pendulum proposals to the dimensional-analysis validator campaign.

It uses:

- `campaign_profiles/dimensional-analysis-validator.yaml`
- `hypothesis_proposals/dimensional-analysis/`
- `experiment_proposals/dimensional-analysis/EXP-PROPOSAL-0003-validator-boundary-batch.yaml`
- `physics_lab.engines.dimensions.validate_item`

It is not a canonical result and does not update `RESULT-0007`, the live
challenge set, any claim, or accepted knowledge.

## Proposal Triage

| Proposal | Status | Decision | Reason |
| --- | --- | --- | --- |
| `HYP-PROPOSAL-0006` RC time constant | `REVIEW_READY` | Executed | Low-risk cross-domain VALID candidate using supported derived units. |
| `HYP-PROPOSAL-0007` LC angular frequency | `REVIEW_READY` | Executed | Exercises square-root handling over supported derived units. |
| `HYP-PROPOSAL-0008` distance plus velocity | `REVIEW_READY` | Executed | Negative-control INVALID candidate with explicit dimension mismatch. |
| `HYP-PROPOSAL-0009` dimensionless ratio | `REVIEW_READY` | Executed | Checks the current SUSPICIOUS heuristic boundary. |
| `HYP-PROPOSAL-0010` projectile range limit fail | `REVIEW_READY` | Executed | Known-limit example where dimension-only validation should compute VALID. |
| `HYP-PROPOSAL-0011` Compton wavelength | `REJECTED` | Not executed | Duplicate-shaped candidate overlapping the physical constants verification track. |
| `HYP-PROPOSAL-0012` natural-unit E = m | `REJECTED` | Not executed | Outside the SI-focused validator profile. |
| `HYP-PROPOSAL-0013` Rayleigh-Jeans approximation | `REJECTED` | Not executed | Cross-track duplicate risk with approximation-breakdown probes. |

This satisfies the pilot constraint of generating 5 to 10 proposals and
explicitly rejecting duplicates or weak items before sandbox execution.

## Sandbox Method

Each executed item was passed to `physics_lab.engines.dimensions.validate_item`.
The item payloads and observed verdicts are stored in
`agent_runs/AGENT-RUN-0003/metrics.json`.

The reproducibility test
`tests/test_dimensional_validator_pilot.py` reloads those payloads and checks
that current source recomputes the stored verdicts and agreement flags.

## Sandbox Classifications

| Item | Formula | Expected | Observed | Agrees | Detail |
| --- | --- | --- | --- | --- | --- |
| `DAV-PILOT-001` | `tau = R * Ccap` | `VALID` | `VALID` | yes | `LHS = RHS = T` |
| `DAV-PILOT-002` | `omega = 1 / sqrt(Lind * Ccap)` | `VALID` | `VALID` | yes | `LHS = RHS = T^-1` |
| `DAV-PILOT-003` | `x = d + v` | `INVALID` | `INVALID` | yes | `Add/Sub of incompatible dimensions: L vs L T^-1` |
| `DAV-PILOT-004` | `score = a / b` | `SUSPICIOUS` | `SUSPICIOUS` | yes | `All variables dimensionless; no physical scale check.` |
| `DAV-PILOT-005` | `range = v**2 / g` | `KNOWN_LIMIT_FAIL` | `VALID` | yes | `LHS = RHS = L` |

The final row is intentionally not a physical success claim. It demonstrates a
known limitation: the dimension-only validator computes `VALID`, while the
curated expected label preserves the missing-assumption failure mode.

## Metrics

- Generated proposals: `8`
- Executed sandbox classifications: `5`
- Rejected before execution: `3`
- Agreement count under current validator agreement rules: `5/5`
- Canonical result artifacts changed: `false`
- Claim artifacts changed: `false`

## Verdict

`SANDBOX_PASS`

The pilot shows that the autonomous loop can generate, triage, execute, and
package dimensional-analysis sandbox work without promoting claims or changing
canonical result memory.
