# Agent Run AGENT-RUN-0009 - Shell-Aware Nuclear Sandbox Batch

**Task:** `TASK-0200`
**Lane:** shell-aware residual corrections (second nuclear sandbox batch)
**Status:** SANDBOX_COMPLETE
**Claim boundary:** sandbox-only; no canonical result, claim, or knowledge artifact is updated.

## Scope

This batch generates five shell-aware residual hypothesis proposals
(`HYP-PROPOSAL-0028` through `HYP-PROPOSAL-0032`), rejects three before
execution, and executes two:

- `HYP-PROPOSAL-0028` — continuous Gaussian shell-proximity on Z and N
  (`r_corr = c_sz * s_z + c_sn * s_n`).
- `HYP-PROPOSAL-0029` — continuous Gaussian shell-proximity on N only
  (`r_corr = c_sn * s_n`).

Shell-proximity is defined as `s_x = exp(-d(x, MAGIC)^2 / (2 * sigma^2))`
with `sigma = 2` frozen at design time. Both features fire on every NMD-0002
and post-AME2020 row, which is the deliberate departure from the strict
double-magic features of `HYP-PROPOSAL-0020` and `HYP-PROPOSAL-0021` (which
fire 0 times on the 295-row post-AME2020 primary holdout, per
`AGENT-RUN-0008`).

## Inputs

- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`
- `results/EXP-0012/RUN-0001/result.yaml` (frozen RESULT-0015 baseline)
- `agent_runs/AGENT-RUN-0006/metrics.json` (split-sensitivity context)
- `agent_runs/AGENT-RUN-0008/metrics.json` (post-AME2020 time-split context)
- `docs/nuclear-mass-holdout-protocol.md`
- `docs/nuclear-mass-robustness-gate.md`

## Method

Deterministic. For each executed family:

1. NMD-0002 4-holdout cross-validation
   (`random_stratified`, `oxygen_chain`, `magic_heavy_region`,
   `neutron_rich_edge`): fit linear coefficients on the holdout complement,
   evaluate on the holdout, report per-holdout MAE and RMSE deltas vs the
   frozen baseline residuals.
2. Post-AME2020 evaluation: fit linear coefficients once on the full
   NMD-0002 residual surface, then apply to the 295-row post-AME2020 primary
   holdout. Report feature-activation counts, per-subset MAE
   (`primary`, `magic_any`, `near_magic`, `neutron_rich_delta_ge_20`,
   `proton_rich_n_lt_z`, `heavy_a_ge_100`, `odd_a`, and AME2020 measured /
   extrapolated comparison subsets), and the top 10 absolute residuals.

All numbers are reproducible from `scripts/run_nuclear_shell_batch.py` and
the recomputation test `tests/test_nuclear_shell_batch.py`.

## Structured Holdout Result

| Candidate | Improved | Regressed | Mean delta MAE (MeV) | Worst regression (MeV) | Structured verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `HYP-PROPOSAL-0028` | 1 | 3 | +1.5701 | 2.9166 | `OVERFITTED` |
| `HYP-PROPOSAL-0029` | 3 | 1 | +0.2957 | 1.6508 | `OVERFITTED` |

Both candidates fail the structured-holdout protocol on the small NMD-0002
slice. The mean delta MAE values include the `oxygen_chain` holdout, where
the candidate magnifies residuals because shell-proximity is small at light
nuclei but training coefficients can become extreme on a 9-row complement.

## Post-AME2020 Primary Result (295 rows)

Baseline primary MAE: `4.5526 MeV`.

| Candidate | Primary delta MAE (MeV) | Magic-any | Near-magic | Neutron-rich | Proton-rich | Heavy A>=100 | Odd-A |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `HYP-PROPOSAL-0028` | +0.0467 | -0.2590 | +0.1133 | -0.0847 | +0.2585 | +0.1921 | -0.0226 |
| `HYP-PROPOSAL-0029` | -0.0620 | -0.3993 | -0.1693 | -0.1702 | +0.2174 | +0.0198 | -0.1076 |

The Z+N candidate regresses the primary MAE. The N-only candidate improves
the primary by a small margin and improves the magic-any, near-magic, and
neutron-rich subsets while regressing the proton-rich subset
(`n = 28`, baseline MAE = `1.94 MeV`).

## Feature Activation

- `HYP-PROPOSAL-0028`: `{s_z_gauss: 295, s_n_gauss: 295}`
- `HYP-PROPOSAL-0029`: `{s_n_gauss: 295}`

Both features fire on every primary row, addressing the dormant-feature
failure mode documented in `AGENT-RUN-0008`. The remaining failure modes are
structured-holdout instability on the 11-row NMD-0002 slice and one-way
proton-rich subset regression on the time-split surface.

## Worst-Case Residuals After Correction

The In/Sb N=82 cluster persists after correction. For `HYP-PROPOSAL-0029`
the top three absolute residuals on the primary holdout are:

- `Ga-84`: `|err| = 37.12 MeV`
- `In-134`: `|err| = 16.64 MeV`
- `In-132`: `|err| = 16.46 MeV`

The candidate does not resolve the worst-case region. The Ga-84 residual,
in particular, is a light-medium neutron-rich row with `s_n_gauss = 0.32`
and remains essentially untouched after the symmetric correction.

## Comparison Context

- Split-sensitivity context from `AGENT-RUN-0006` (same-shape 48-split
  enumeration of `HYP-PROPOSAL-0021`): mean delta MAE `-0.058 MeV`, worst
  delta MAE `+0.948 MeV`. The N-only candidate's `+0.62 MeV` post-AME2020
  improvement remains inside this spread; it is not out-of-spread evidence.
- Time-split context from `AGENT-RUN-0008`:
  `HYP-PROPOSAL-0021` primary delta MAE `+0.0796 MeV`,
  `HYP-PROPOSAL-0022` (negative control) primary delta MAE `-0.3886 MeV`.
  The N-only shell-proximity candidate improves the primary by less than
  one-sixth of the negative-control improvement, and exhibits the same
  one-way proton-rich subset trade.

## Verdict

`SANDBOX_PASS` for the run (sandbox protocol satisfied, no canonical
artifact changed). Scientific reading per candidate:

- `HYP-PROPOSAL-0028`: structured `OVERFITTED`, post-AME2020 primary
  regression. Gate outcome `ALLOW_ONLY_AS_NEGATIVE_CONTROL`.
- `HYP-PROPOSAL-0029`: structured `OVERFITTED`, post-AME2020 primary
  marginal improvement with proton-rich regression. Gate outcome
  `ALLOW_ONLY_AS_NEGATIVE_CONTROL` because the one-way subset trade and
  structured-protocol failure block a stronger reading.

No follow-up batch is recommended from this run alone. The continuous
shell-proximity lane has demonstrated the activation-count fix but has not
produced a robust positive lead.
