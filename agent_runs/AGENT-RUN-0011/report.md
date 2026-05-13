# Agent Run AGENT-RUN-0011 — Pairing and Odd-Even Nuclear Sandbox Batch

**Task:** `TASK-0201`
**Lane:** pairing and odd-even residual corrections
**Status:** SANDBOX_COMPLETE
**Claim boundary:** sandbox-only; no canonical result, claim, or knowledge artifact is updated.

## Scope

This batch generates five pairing/odd-even residual hypothesis proposals
(`HYP-PROPOSAL-0038` through `HYP-PROPOSAL-0042`), rejects three before
execution, and executes two:

- `HYP-PROPOSAL-0038` — differential even-even / odd-odd pairing correction
  (`r_corr = c_ee * η_ee(N,Z) + c_oo * η_oo(N,Z)`).
  Allows independent constant offsets for even-even and odd-odd nuclear classes
  beyond the already-fitted baseline pairing term.

- `HYP-PROPOSAL-0039` — Wigner energy term for N=Z nuclei
  (`r_corr = w * δ(N=Z) / A`).
  A physically motivated correction for self-conjugate nuclei where
  proton-neutron T=0 pairing produces extra binding not captured by the
  standard Bethe-Weizsäcker formula.

## Inputs

- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`
- `results/EXP-0012/RUN-0001/result.yaml` (frozen RESULT-0015 baseline)
- `agent_runs/AGENT-RUN-0006/metrics.json` (split-sensitivity context)
- `agent_runs/AGENT-RUN-0008/metrics.json` (post-AME2020 time-split context)

## Method

Deterministic. For each executed family:

1. NMD-0002 four-holdout cross-validation
   (`random_stratified`, `oxygen_chain`, `magic_heavy_region`,
   `neutron_rich_edge`): fit linear coefficients on the holdout complement,
   evaluate on the holdout, report per-holdout MAE and RMSE deltas vs the
   frozen baseline residuals.
2. Post-AME2020 evaluation: fit linear coefficients once on the full
   NMD-0002 residual surface, apply to the 295-row post-AME2020 primary
   holdout. Report feature-activation counts, per-subset MAE, and top
   absolute residuals.

All numbers are reproducible from `scripts/run_nuclear_pairing_batch.py`
and the recomputation test `tests/test_nuclear_pairing_batch.py`.

## Structured Holdout Result

Baseline primary MAE (post-AME2020): **4.5526 MeV** (n=295)

| Candidate | Improved | Regressed | Mean delta MAE (MeV) | Worst regression (MeV) | Structured verdict |
|-----------|--------:|----------:|--------------------:|----------------------:|-------------------|
| `HYP-PROPOSAL-0038` | 1 | 3 | +0.3142 | +1.0693 | `OVERFITTED` |
| `HYP-PROPOSAL-0039` | 1 | 1 | +0.1179 | +0.5388 | `INCONCLUSIVE` |

### HYP-PROPOSAL-0038 per-holdout detail

| Holdout | delta MAE (MeV) |
|---------|---------------:|
| `random_stratified` | +1.0693 |
| `oxygen_chain` | −0.0737 |
| `magic_heavy_region` | +0.2573 |
| `neutron_rich_edge` | +0.0039 |

The large regression on `random_stratified` is driven by `c_oo = 4.17 MeV`
fitted on a complement that loses its only odd-odd training row (N-14) during
this fold. Without N-14 in training, the odd-odd coefficient is extrapolated
from even-even and odd-A behaviour and produces a large overcorrection on the
three holdout rows that include Pb-208 (an even-even nucleus).

### HYP-PROPOSAL-0039 per-holdout detail

| Holdout | delta MAE (MeV) |
|---------|---------------:|
| `random_stratified` | +0.5388 |
| `oxygen_chain` | −0.0674 |
| `magic_heavy_region` | 0.0000 |
| `neutron_rich_edge` | 0.0000 |

The Wigner coefficient is fitted predominantly on the He-4, O-16, and
Ca-40 N=Z rows. When Fe-57 (not N=Z) and Pb-208 (not N=Z) are the holdout,
the Wigner term produces a non-zero correction on He-4 (N=Z in holdout in
`random_stratified`), introducing a regression. The two zero-delta folds
(`magic_heavy_region`, `neutron_rich_edge`) contain no N=Z nuclei in the
holdout subset, so the Wigner term is dormant there.

## Post-AME2020 Primary Result (n=295)

Baseline primary MAE: **4.5526 MeV**

| Candidate | Primary delta MAE (MeV) | Magic-any | Near-magic | Neutron-rich (≥20) | Odd-A |
|-----------|------------------------:|----------:|-----------:|-------------------:|------:|
| `HYP-PROPOSAL-0038` | +0.0876 | — | — | — | — |
| `HYP-PROPOSAL-0039` | +0.0011 | — | — | — | — |

Full per-subset breakdown is in `agent_runs/AGENT-RUN-0011/metrics.json`.

**Feature activation on 295-row holdout:**

- `HYP-PROPOSAL-0038`: `eta_ee` active on 68/295, `eta_oo` active on 71/295
- `HYP-PROPOSAL-0039`: `wigner_n_eq_z` active on 3/295 (only N=Z rows)

The Wigner feature is near-dormant on the post-AME2020 holdout: 3 out of 295
rows have N=Z in a dataset dominated by neutron-rich nuclides. Its coefficient
(w = 13.04 MeV from full-NMD-0002 fit) produces a negligible global MAE delta
(+0.0011 MeV) despite being physically significant on the training surface.

## Negative Control Comparison

| Candidate | Post-AME2020 primary delta MAE (MeV) |
|-----------|--------------------------------------:|
| HYP-PROPOSAL-0022 (established negative control) | −0.049 (from AGENT-RUN-0008) |
| HYP-PROPOSAL-0038 (this batch) | +0.088 |
| HYP-PROPOSAL-0039 (this batch) | +0.001 |

Both candidates perform worse than the established negative-control family
HYP-PROPOSAL-0022 on the post-AME2020 primary surface. HYP-PROPOSAL-0038
regresses; HYP-PROPOSAL-0039 is effectively null.

## Robustness Gate Summary

| Field | HYP-PROPOSAL-0038 | HYP-PROPOSAL-0039 |
|-------|-------------------|-------------------|
| Outcome | `BLOCK_PROMOTION` | `ALLOW_ONLY_AS_NEGATIVE_CONTROL` |
| Baseline | RESULT-0015 | RESULT-0015 |
| Active holdouts | 4/4 reported | 4/4 reported |
| Split-sensitivity | N/A (structured failure) | N/A (dormant on holdout) |
| Leakage review | No targeted features | No targeted features |
| Complexity | 2 parameters (1 underdetermined) | 1 parameter |
| Negative control | HYP-PROPOSAL-0022 reference visible | HYP-PROPOSAL-0022 reference visible |
| Post-AME2020 status | Regresses (+0.088 MeV) | Near-null (+0.001 MeV) |
| Limitations | Sparse odd-odd training data | Near-zero activation on neutron-rich holdout |

## Rejected Proposals (before execution)

| Proposal | Rejection class |
|----------|----------------|
| HYP-PROPOSAL-0040 | Data-sparsity overfit (zero odd-Z/even-N rows in NMD-0002) |
| HYP-PROPOSAL-0041 | Near-collinearity with baseline pairing term |
| HYP-PROPOSAL-0042 | Feature redundancy with HYP-PROPOSAL-0038 η_ee |

## Conclusion

Neither executed pairing/odd-even candidate shows improvement over the frozen
RESULT-0015 baseline on the structured holdout protocol or the post-AME2020
primary surface. The pairing-lane findings are negative within the configured
sandbox scope:

- **HYP-PROPOSAL-0038** (OVERFITTED): The differential even-even / odd-odd
  correction is structurally unstable on NMD-0002 because the odd-odd class
  has a single training representative (N-14). The fitted odd-odd coefficient
  (c_oo ≈ 4.17 MeV) is effectively a single-point interpolation that collapses
  under holdout evaluation.

- **HYP-PROPOSAL-0039** (INCONCLUSIVE): The Wigner N=Z correction has a
  physically motivated coefficient on the training surface but near-zero
  activation on the post-AME2020 primary holdout. It cannot improve or worsen
  metrics that it barely touches.

No claim, canonical result, or hypothesis is promoted. Both candidates receive
`BLOCK_PROMOTION` or `ALLOW_ONLY_AS_NEGATIVE_CONTROL` under the robustness gate.
