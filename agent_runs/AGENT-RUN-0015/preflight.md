# AGENT-RUN-0015 Preflight

**Task:** TASK-0286  
**Lane:** nuclear mid-mass and isotope-chain gap scout  
**Mode:** sandbox-only autonomous research pilot

## Inputs Checked

- `tasks/TASK-0286-run-nuclear-midmass-isotope-gap-scout.yaml`
- `results/EXP-0012/RUN-0001/result.yaml`
- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`
- `docs/reviews/nuclear-prediction-registry-coverage-audit.md`
- `data/nuclear_masses/nuclear_prediction_registry_coverage.yaml`

## Guardrails

- Live external fetch: not allowed and not used.
- Prediction registry writes: not allowed and not used.
- Canonical `RESULT-*`, claims, and knowledge promotion: not allowed and not used.
- Candidate verdicts are sandbox triage labels only.

## Plan

1. Generate bounded mid-mass and isotope-chain residual candidate ideas (8 total).
2. Reject leakage-prone, row-memorizing, or duplicate ideas before execution (3 rejections).
3. Execute 5 candidates: 4 mid-mass / isotope-chain hypotheses plus 1 near-null control.
4. Fit candidates on frozen NMD-0002 residuals vs `RESULT-0015::model_fitted_semi_empirical`.
5. Evaluate on the committed post-AME2020 row-level holdout as a retrospective stress surface.
6. Report primary, mid-mass, light, heavy, and isotope-chain subset deltas plus frontier-contrast.
7. Preserve negative, inconclusive, and near-null controls.
8. Report limitations and the promotion boundary.
