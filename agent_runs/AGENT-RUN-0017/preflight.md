# AGENT-RUN-0017 Preflight

**Task:** TASK-0289  
**Lane:** nuclear asymmetry-frontier adversarial stress scout  
**Mode:** sandbox-only autonomous research pilot

## Inputs Checked

- `TASK-0289`
- `results/EXP-0012/RUN-0001/result.yaml`
- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`
- `docs/reviews/nuclear-neutron-rich-variant-scout-001.md`
- `docs/reviews/nuclear-scout-lane-synthesis-after-pred-0062.md`
- `docs/reviews/nuclear-midmass-isotope-gap-scout-001.md`
- `docs/reviews/nuclear-prediction-registry-coverage-audit.md`

## Guardrails

- Live external fetch: not allowed and not used.
- Prediction registry writes: not allowed and not used.
- Canonical `RESULT-*`, claims, and knowledge promotion: not allowed and not used.
- Candidate verdicts are sandbox triage labels only.
- The expected-overfit neighbor (ASYM-STRESS-003) is preserved as an
  intentional negative control rather than rejected before execution.

## Plan

1. Generate bounded asymmetry-frontier candidate ideas (9 total).
2. Reject free-exponent, per-Z-slopes, and threshold-sweep ideas before
   execution (3 rejections).
3. Execute 6 candidates: re-evals of NR-SCOUT-003 and NR-SCOUT-004, the
   matched quadratic+cubic overfit-neighbor pair NR-SCOUT-005, a
   sign-inverted adversarial control, a clipped asymmetry above 0.25
   variant, and a near-null sanity control.
4. Fit candidates on frozen NMD-0002 residuals vs
   `RESULT-0015::model_fitted_semi_empirical`.
5. Evaluate on the committed post-AME2020 row-level holdout as a
   retrospective stress surface.
6. Report primary, asymmetry-greater-than 0.20 and 0.25, N-Z greater than
   20 and 30, heavy, mid-mass, light, and AME2020 measured/extrapolated
   subset deltas plus a frontier-contrast metric and a deterministic
   lane-recommendation block.
7. Preserve negative, inconclusive, and near-null controls; explicitly
   confirm the OVERFITTED outcome of ASYM-STRESS-003 and the negated
   coefficient of ASYM-STRESS-004.
8. Report limitations and the promotion boundary.
