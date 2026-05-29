# AGENT-RUN-0043 Preflight

Compliance with the controls-first gauntlet (`docs/notes/nuclear-controls-first-hypothesis-gauntlet.md`):

- Hypothesis family: F2 (high-error cluster) under residual-free labels per `docs/nuclear-residual-feature-no-leakage-contract.md`.
- Allowed inputs: Z, N, A, magic-distance (from published magic-number list), asymmetry (N - Z) / A. No baseline residual or any residual-derived quantity enters label construction.
- Forbidden inputs (none used): target residual, baseline error rank, candidate-fit residual, source-status flag, future comparison rows.
- Baseline: RESULT-0015 frozen semi-empirical coefficients. No candidate-fit residuals feed neighbor aggregates.
- Controls (both run end-to-end): matched_random cluster-label permutation + smooth_a linear (`r = a + b * A`).
- Leave-one-out logic: each training row's candidate correction uses the mean of OTHER training rows in the same cluster.
- Holdout: post-AME2020 primary holdout rows use the full training-slice cluster mean. Holdout rows never enter the fit.
- Failure condition declared before scoring: candidate must beat baseline by ≥ 0.25 MeV on full_known MAE and beat both controls by the same margin; primary-holdout regression demotes the verdict to DIAGNOSTIC_ONLY.
- Output routing: this agent_runs/ bundle + docs/reviews/nuclear-residual-free-high-error-cluster-hypothesis-audit.md. No PRED/CLAIM/KNOW/RESULT artifacts.
- Wording boundary: forbidden terms include discovery, new nuclear law, broad formula, first-principles. Verdict vocabulary fixed at {BOUNDED_FOLLOWUP_CANDIDATE, DIAGNOSTIC_ONLY, NEGATIVE_RESULT, INCONCLUSIVE}.
