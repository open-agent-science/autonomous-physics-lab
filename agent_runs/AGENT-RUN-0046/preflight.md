# AGENT-RUN-0046 Preflight

Compliance with the controls-first gauntlet (`docs/notes/nuclear-controls-first-hypothesis-gauntlet.md`):

- Hypothesis family: fresh pairing-asymmetry interaction under the controls-first gauntlet.
- Allowed inputs: Z, N, A, pairing sign, and neutron excess, all deterministic residual-free functions of committed row identifiers.
- Forbidden inputs (none used): target residual, baseline error rank, candidate-fit residual, source-status, future comparison rows.
- Baseline: RESULT-0015 frozen semi-empirical coefficients.
- Four controls run end-to-end: smooth_a + asymmetry_only + pairing_only + matched_degree_random.
- Coefficient stability LOO reported.
- Failure condition declared before scoring: candidate must beat baseline by ≥ 0.25 MeV on full_known AND beat all four controls by the same margin AND have ≤ 1 LOO sign flip; otherwise verdict drops to CONTROL_DOMINATED, FRAGILE_INCONCLUSIVE, or NEGATIVE_RESULT.
- Output routing: this agent_runs/ bundle + docs/reviews/nuclear-pairing-asymmetry-interaction-control-lane.md.
- Custom verdict vocabulary caps at BOUNDED_DIAGNOSTIC; no registry expansion or PRED entry is authorized.
- Wording boundary: forbidden terms include discovery, new nuclear law, broad formula, nuclear-law wording, or breakthrough framing.
