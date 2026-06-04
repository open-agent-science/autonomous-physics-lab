# AGENT-RUN-0018 Preflight

**Task:** TASK-0310  
**Lane:** nuclear shell-axis full-known retrospective audit  
**Mode:** sandbox-only retrospective audit

## Inputs Checked

- `TASK-0310`
- `results/EXP-0012/RUN-0001/result.yaml`
- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`
- `docs/reviews/nuclear-shell-axis-stress-scout-001.md`

## Guardrails

- Live external fetch: not allowed and not used.
- Prediction registry writes: not allowed and not used.
- Canonical results, claims, and knowledge promotion: not allowed and not used.
- PRED-0063 through PRED-0068 are not reveal-scored.

## Plan

1. Fit bounded shell-axis candidates on the frozen NMD-0002 residual slice.
2. Evaluate them on training, post-AME2020 primary holdout, and full-known unique surfaces.
3. Preserve sign-inverted, shuffled-feature, and near-null/baseline-reference controls.
4. Report per-subset deltas and worst-regression summaries.
5. Keep outputs sandbox-only.
