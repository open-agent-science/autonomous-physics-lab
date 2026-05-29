# AGENT-RUN-0045 Preflight

Compliance with the controls-first gauntlet (`docs/notes/nuclear-controls-first-hypothesis-gauntlet.md`):

- Hypothesis family: F3 (shell-axis) under residual-free interaction form per `docs/nuclear-residual-feature-no-leakage-contract.md`.
- Allowed inputs: Z, N, magic-distance (from published magic-number list).
- Forbidden inputs (none used): target residual, baseline error rank, candidate-fit residual, source-status, future comparison rows.
- Baseline: RESULT-0015 frozen semi-empirical coefficients.
- Four controls run end-to-end: smooth_a + asymmetry_only + parity_only + matched_degree_random.
- Coefficient stability LOO reported.
- Failure condition declared before scoring: candidate must beat baseline by ≥ 0.25 MeV on full_known AND beat all four controls by the same margin AND have ≤ 1 LOO sign flip; otherwise verdict drops to CONTROL_DOMINATED, FRAGILE_INCONCLUSIVE, or NEGATIVE_RESULT.
- Output routing: this agent_runs/ bundle + docs/reviews/nuclear-magic-distance-interaction-control-lane.md.
- Custom verdict vocabulary caps at SHELL_ADJACENT_DIAGNOSTIC; no registry expansion or shell-axis PRED entry reuse is authorized.
- Wording boundary: forbidden terms include discovery, new nuclear law, broad formula, shell-axis breakthrough.
