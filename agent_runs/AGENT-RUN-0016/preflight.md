# AGENT-RUN-0016 Preflight

**Task:** TASK-0288  
**Lane:** nuclear shell-axis adversarial stress scout  
**Mode:** sandbox-only autonomous research pilot

## Inputs Checked

- `tasks/TASK-0288-run-nuclear-shell-axis-adversarial-stress-scout.yaml`
- `results/EXP-0012/RUN-0001/result.yaml`
- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`
- `docs/reviews/nuclear-scout-lane-synthesis-after-pred-0062.md`
- `docs/reviews/nuclear-shell-neighborhood-variant-scout-001.md`
- `docs/reviews/nuclear-midmass-isotope-gap-scout-001.md`
- `docs/reviews/nuclear-prediction-registry-coverage-audit.md`

## Guardrails

- Live external fetch: not allowed and not used.
- Prediction registry writes: not allowed and not used.
- Canonical `RESULT-*`, claims, and knowledge promotion: not allowed and not used.
- Candidate verdicts are sandbox triage labels only.

## Plan

1. Re-evaluate the strongest post-PRED-0062 shell-axis sandbox signals as adversarial stress candidates (STRESS-SHELL-001 proton-only Gaussian, STRESS-SHELL-002 proton x neutron product, STRESS-SHELL-003 neutron-only Gaussian overlap diagnostic).
2. Add three adversarial controls: a sign-inverted proton-axis control (STRESS-SHELL-004), a shuffled proton-axis control with cyclic-shift-5 (STRESS-SHELL-005), and a near-null sanity control (STRESS-SHELL-006).
3. Reject three free-knob or duplicate-search candidates before execution (STRESS-SHELL-007 free-sigma, STRESS-SHELL-008 per-magic-number offsets, STRESS-SHELL-009 SHELL-SCOUT-001 additive re-test).
4. Fit candidates on frozen NMD-0002 residuals vs `RESULT-0015::model_fitted_semi_empirical`.
5. Evaluate on the committed post-AME2020 row-level holdout as a retrospective stress surface.
6. Report primary, magic_Z, magic_N, heavy, mid-mass, light, neutron-rich, frontier-contrast, and registry-repeat chain-neighbor subset deltas.
7. Record a repeated-target-pressure block that names the four overrepresented registry targets, confirms they are absent from the holdout, and lists the six chain-neighbor holdout rows.
8. Preserve negative, sign-inverted, shuffled, and near-null controls.
9. Report limitations and the promotion boundary.
