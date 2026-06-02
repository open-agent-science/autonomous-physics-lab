# AGENT-RUN-0054 — NMD-0002 Uncertainty Perturbation Control (TASK-0518)

Sandbox control run for the top apparent candidates from the TASK-0507 Nuclear
factory sprint. This run perturbs only the committed NMD-0002 rows; it does not
fetch data, add measurement rows, reveal predictions, or promote claims.

- Dataset: `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- Prior factory run: `agent_runs/AGENT-RUN-0052/factory_summary.yaml`
- Baseline: frozen coefficients from `results/EXP-0012/RUN-0001/result.yaml`
- Trials: 200 per perturbation mode
- Seed: 518
- Candidate set: top five TASK-0507 candidates by effective reduction

## Result

**Verdict: INCONCLUSIVE sandbox control evidence.**

The declared-uncertainty mode preserves the original top ordering at the top:
`CAND-0001` remains top-ranked in all 200 trials, and every tracked candidate
keeps the original `INCONCLUSIVE` route verdict. This shows that the apparent
top reductions are not numerically erased by the committed uncertainty values.

The coarse-floor stress mode is less stable: `CAND-0001` remains top in
184/200 trials, while `CAND-0037` becomes top in 16/200 trials. All tracked
candidates still route `INCONCLUSIVE`, so the run does not create a shortlist.

## Stability Summary

| mode | top candidate stability | route stability |
| --- | --- | --- |
| declared uncertainty | `CAND-0001` top in 200/200 trials | all tracked candidates `INCONCLUSIVE` |
| 10x coarse-floor stress | `CAND-0001` top in 184/200, `CAND-0037` top in 16/200 | all tracked candidates `INCONCLUSIVE` |

## Interpretation

NMD-0002 uncertainty perturbation does not overturn the TASK-0507 conclusion:
the top candidates remain underpowered sandbox signals, not shortlist evidence.
The 10x stress mode shows rank fragility under a deliberately amplified coarse
uncertainty floor, which reinforces the need to treat NMD-0002 as a control
surface only.

## Limitations

- NMD-0002 has only 11 rows and a 3-row holdout.
- The dataset records a coarse curated uncertainty floor rather than
  source-grade per-row uncertainties.
- Frozen baseline coefficients are reused without refit.
- Survival under perturbation is not promotion evidence.

## Output-Routing Summary

- **Verdict:** `INCONCLUSIVE`
- **Canonical destination:** sandbox evidence in `agent_runs/AGENT-RUN-0054/`
  plus review note in
  `docs/reviews/nmd0002-uncertainty-perturbation-control.md`.
- **Review tier:** not applicable.
- **Gate A / Gate B:** not applicable; no canonical result or prediction
  artifact is published.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Publication blocker:** same 11-row/3-holdout NMD-0002 power limit and coarse
  uncertainty-floor semantics.
