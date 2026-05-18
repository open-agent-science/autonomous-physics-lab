# AGENT-RUN-0016 Review Summary

## Verdict

`REVIEW_READY` for sandbox review.

## Method

`scripts/run_nuclear_shell_axis_stress_scout.py` loads the frozen
`RESULT-0015::model_fitted_semi_empirical` coefficients, computes NMD-0002
baseline residuals, fits bounded shell-axis residual features, and evaluates
candidate residuals on the committed post-AME2020 holdout rows. The scout
re-evaluates SHELL-SCOUT-003 (proton-only Gaussian), SHELL-SCOUT-005 (proton x
neutron product), and SHELL-SCOUT-002 (neutron-only Gaussian) as
STRESS-SHELL-001/002/003, and adds three adversarial controls:
STRESS-SHELL-004 (sign-inverted proton-only), STRESS-SHELL-005 (cyclic-shift-5
shuffled proton-only), and STRESS-SHELL-006 (near-null sanity control). Subset
metrics cover primary, magic-axis, near-magic, mid-mass, light, heavy,
neutron-rich, frontier-contrast, registry-repeat-target, and
registry-repeat-chain-neighbor diagnostics.

## Metrics

- Generated candidates: 9
- Executed candidates: 6 (3 re-evaluations + 3 adversarial controls)
- Rejected before execution: 3
- Verdict counts: `PARTIALLY_VALID` 4, `INCONCLUSIVE` 2
- Preserved near-null control: `STRESS-SHELL-006`
- Sign-inverted control `STRESS-SHELL-004` regressed primary, magic, heavy, and chain-neighbor subsets as expected; this is consistent with the original shell-axis signal direction.
- Shuffled control `STRESS-SHELL-005` collapsed every subset delta to a near-noise-floor magnitude (sub-milli-MeV), which is the expected sandbox behavior when the row-feature correspondence is destroyed.

## Repeated-target pressure

The four overrepresented registry targets (Ni-76 with 18 entries, Ca-55,
Ga-85, and Zn-80 with 14 entries each) are absent from the post-AME2020
holdout. The `registry_repeat_chain_neighbor` subset contains six holdout
rows (Ni-74, Ni-75, Ca-54, Ga-83, Ga-84, Zn-79); chain-neighbor deltas track
the same direction as the primary and magic-axis deltas for the three
shell-axis candidates and are noted as fragile small-subset diagnostics.

## Limitations

The run is retrospective, sandbox-only, and small-sample. It should not be
used to promote a nuclear mass claim, rewrite canonical results, or register
frozen predictions without a separate reviewed task. Adversarial controls are
sandbox-triage diagnostics; a `PARTIALLY_VALID` label is not a discovery
claim, and the shuffled control's `PARTIALLY_VALID` label reflects strict
triage rules rather than physical signal.
