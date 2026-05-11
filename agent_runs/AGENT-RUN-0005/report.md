# Agent Run AGENT-RUN-0005 - Nuclear Mass Autonomous Pilot

## Scope

This sandbox run tests whether the autonomous research loop can produce useful,
bounded residual-correction hypotheses on the frozen nuclear-mass benchmark
after `EXP-0012` / `RESULT-0015` and the holdout protocol landed.

It uses:

- `campaign_profiles/nuclear-mass-surface.yaml`
- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `results/EXP-0012/RUN-0001/result.yaml`
- `docs/nuclear-mass-holdout-protocol.md`
- `hypothesis_proposals/nuclear-mass/`
- `experiment_proposals/nuclear-mass/EXP-PROPOSAL-0005-nuclear-mass-sandbox-batch.yaml`

It is not a canonical result and does not update `RESULT-0015`, any claim,
accepted knowledge note, canonical hypothesis, canonical experiment, or
canonical dataset.

## Proposal Triage

| Proposal | Status | Decision | Reason |
| --- | --- | --- | --- |
| `HYP-PROPOSAL-0020` shell dual heavy anchor | `REVIEW_READY` | Executed | Simple shell-aware residual family that stays compact enough for the first pilot. |
| `HYP-PROPOSAL-0021` shell dual heavy anchor plus odd-A damping | `REVIEW_READY` | Executed | Strongest bounded family found in pre-triage; improves all active holdout slices on the frozen benchmark. |
| `HYP-PROPOSAL-0022` quadratic asymmetry refinement | `REVIEW_READY` | Executed | Plausible-looking negative control chosen to test whether structured holdout catches overfit behavior. |
| `HYP-PROPOSAL-0023` oxygen-chain latch | `REJECTED` | Not executed | Too chain-specific for the first flagship pilot and redundant with the chosen negative-control role. |
| `HYP-PROPOSAL-0024` lead-actinide anchor | `REJECTED` | Not executed | Memorizes the two largest heavy residual rows directly. |
| `HYP-PROPOSAL-0025` magic-step cascade | `REJECTED` | Not executed | Too discontinuous and complex for a small first-pilot slice. |
| `HYP-PROPOSAL-0026` advanced-model surrogate | `REJECTED` | Not executed | Pulls the pilot into a comparison lane the campaign still defers. |
| `HYP-PROPOSAL-0027` live time-split fetch | `REJECTED` | Not executed | Depends on uncommitted later-measurement data and would violate pinned-source policy. |

This satisfies the pilot constraint of generating at least eight proposals,
executing at most three, and explicitly rejecting five weaker or policy-risky
items before sandbox execution.

## Active Holdouts

The pilot freezes four active holdout families from the reviewed protocol:

| Holdout | Held-out nuclides | Purpose |
| --- | --- | --- |
| `random_stratified` | `He-4`, `Fe-57`, `Pb-208` | Light / medium / heavy diagnostic split |
| `oxygen_chain` | `O-16`, `O-17` | Isotope-chain generalization check |
| `magic_heavy_region` | `Sn-120`, `Pb-208` | Heavy magic-region check |
| `neutron_rich_edge` | `Sn-120`, `Pb-208`, `U-238` | Neutron-rich extrapolation pressure |

## Sandbox Execution

All executed candidates replay the frozen `RESULT-0015` residual surface and
fit additive corrections only on the complement of each revealed holdout
subset.

| Candidate | Expected | Observed | Mean delta MAE (MeV) | Worst regression (MeV) | Detail |
| --- | --- | --- | ---: | ---: | --- |
| Shell dual heavy anchor | `PARTIALLY_VALID` | `PARTIALLY_VALID` | `-0.120` | `0.166` | Helps three structured holdouts, but the random split gets slightly worse. |
| Shell dual heavy anchor plus odd-A damping | `VALID_IN_RANGE` | `VALID_IN_RANGE` | `-0.335` | `0.000` | Improves all four active holdout slices while staying compact and sandbox-only. |
| Quadratic asymmetry refinement | `OVERFITTED` | `OVERFITTED` | `1.095` | `2.487` | Looks somewhat plausible on the oxygen chain but collapses on heavy magic and neutron-rich holdouts. |

The third row is the required negative result. It shows that structured
holdout is doing useful work even on a tiny pinned slice.

### Per-Holdout Deltas

Negative deltas improve on the frozen `RESULT-0015` baseline. Positive deltas
are regressions and must stay visible during review.

| Candidate | Holdout | Delta MAE (MeV) | Delta RMSE (MeV) |
| --- | --- | ---: | ---: |
| Shell dual heavy anchor | `random_stratified` | `0.166` | `0.178` |
| Shell dual heavy anchor | `oxygen_chain` | `-0.242` | `-0.063` |
| Shell dual heavy anchor | `magic_heavy_region` | `-0.242` | `-0.341` |
| Shell dual heavy anchor | `neutron_rich_edge` | `-0.162` | `-0.222` |
| Shell dual heavy anchor plus odd-A damping | `random_stratified` | `-0.255` | `0.098` |
| Shell dual heavy anchor plus odd-A damping | `oxygen_chain` | `-0.681` | `-0.684` |
| Shell dual heavy anchor plus odd-A damping | `magic_heavy_region` | `-0.242` | `-0.341` |
| Shell dual heavy anchor plus odd-A damping | `neutron_rich_edge` | `-0.162` | `-0.222` |
| Quadratic asymmetry refinement | `random_stratified` | `1.249` | `2.022` |
| Quadratic asymmetry refinement | `oxygen_chain` | `-0.194` | `-0.249` |
| Quadratic asymmetry refinement | `magic_heavy_region` | `2.487` | `2.897` |
| Quadratic asymmetry refinement | `neutron_rich_edge` | `0.836` | `1.318` |

## Metrics

- Generated proposals: `8`
- Executed sandbox candidates: `3`
- Rejected before execution: `5`
- Candidates that improved all active holdouts: `1`
- Negative or overfit executed candidates: `1`
- Canonical result artifacts changed: `false`
- Claim artifacts changed: `false`

## Verdict

`SANDBOX_PASS`

The pilot shows that the autonomous loop can now:

- propose multiple compact nuclear-mass residual families;
- preserve a clearly overfit family as negative evidence;
- reject narrower or policy-violating ideas before execution; and
- package the outcome without touching canonical scientific memory.
