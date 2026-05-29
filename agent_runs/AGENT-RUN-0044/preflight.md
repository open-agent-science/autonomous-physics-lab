# AGENT-RUN-0044 Preflight

Compliance with the controls-first gauntlet (`docs/notes/nuclear-controls-first-hypothesis-gauntlet.md`):

- Hypothesis family: closed-form residual-free boundary-distance feature per the F1/F5 spirit of `docs/nuclear-residual-feature-no-leakage-contract.md`.
- Allowed inputs: Z, N, A (and the derived asymmetry/boundary distance).
- Forbidden inputs (none used): target residual, baseline error rank as a feature, candidate-fit residual, source-status, future comparison rows.
- Baseline: RESULT-0015 frozen semi-empirical coefficients.
- Controls run end-to-end: matched_high_error_non_neutron_rich + sign_inverted_boundary + isotope_chain_transfer.
- Failure condition declared before scoring: candidate must beat baseline by ≥ 0.25 MeV on full_known and beat both numerical controls by the same margin; isotope-chain transfer rate must be ≥ 0.5; primary-holdout regression demotes the verdict to DIAGNOSTIC_ONLY.
- Output routing: this agent_runs/ bundle + docs/reviews/nuclear-neutron-rich-boundary-transfer-hypothesis-lane.md.
- Wording boundary: forbidden terms include discovery, new nuclear law, broad formula, anomaly explanation.
