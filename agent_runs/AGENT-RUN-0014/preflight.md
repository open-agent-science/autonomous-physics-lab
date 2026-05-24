# AGENT-RUN-0014 Preflight

**Task:** TASK-0280  
**Lane:** nuclear pairing and odd-even variant scout  
**Mode:** sandbox-only autonomous research pilot

## Inputs Checked

- `tasks/TASK-0280-run-nuclear-pairing-odd-even-variant-scout.yaml`
- `experiments/EXP-0012-nuclear-mass-baseline.yaml`
- `results/EXP-0012/RUN-0001/result.yaml`
- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`
- `docs/notes/nuclear-prediction-variant-factory.md`
- `docs/reviews/nuclear-prediction-factory-slate-002-feature-terms.md`

## Guardrails

- Live external fetch: not allowed and not used.
- Prediction registry writes: not allowed and not used.
- Canonical `RESULT-*`, claims, and knowledge promotion: not allowed and not used.
- Candidate verdicts are sandbox triage labels only.

## Plan

1. Generate bounded pairing, odd-even, parity, or local-staggering candidate ideas.
2. Reject leakage-prone or overfit-prone ideas before evaluation.
3. Fit executed candidates on frozen NMD-0002 residuals against `RESULT-0015::model_fitted_semi_empirical`.
4. Evaluate on the committed post-AME2020 row-level holdout as a retrospective stress surface.
5. Preserve negative, inconclusive, and near-null controls.
6. Report limitations and promotion boundary.
