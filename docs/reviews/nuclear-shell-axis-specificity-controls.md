# Nuclear Shell-Axis Specificity Controls

**Task:** `TASK-0317`  
**Agent run:** `agent_runs/AGENT-RUN-0020/`  
**Script:** `scripts/run_nuclear_shell_axis_specificity_controls.py`  
**Metrics:** `agent_runs/AGENT-RUN-0020/metrics.json`  
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`  
**Evidence class:** sandbox-only retrospective specificity-control audit

## Scope

This review checks whether the `TASK-0310` shell-axis improvements are
specific to shell-proximity structure or whether similarly simple non-shell
features can match them.

The audit reuses only committed repository data:

- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`
- `results/EXP-0012/RUN-0001/result.yaml`
- `agent_runs/AGENT-RUN-0018/metrics.json`
- `agent_runs/AGENT-RUN-0019/metrics.json`

It does not fetch live data, score `PRED-0063` through `PRED-0068`, create or
edit prediction registry entries, modify canonical results, promote claims, or
write knowledge artifacts.

## Control Design

All controls were predeclared before evaluating the metrics and fit only on
the same 11-row NMD-0002 training residual slice used by `TASK-0310`.

| Control | Complexity | Role |
| --- | ---: | --- |
| `SPECIFICITY-CONTROL-000` | 0 | baseline / near-null reference |
| `SPECIFICITY-CONTROL-001` | 1 | smooth-A trend |
| `SPECIFICITY-CONTROL-002` | 1 | neutron-excess asymmetry proxy |
| `SPECIFICITY-CONTROL-003` | 1 | light-mass-region indicator |
| `SPECIFICITY-CONTROL-004` | 1 | deterministic random matched-degree feature |

The controls are diagnostic only. They are not new formula candidates for
promotion.

## Results

Negative delta means lower retrospective MAE than the frozen baseline.
Positive delta means regression.

### Shell-Axis Candidates

| Candidate | Full-known ΔMAE MeV | Holdout ΔMAE MeV | Training ΔMAE MeV | Magic-Z ΔMAE MeV | Magic-N ΔMAE MeV | Light ΔMAE MeV | Worst regression |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `FULLKNOWN-SHELL-001` | -0.086092 | -0.091504 | +0.059043 | -0.158489 | -0.326992 | +0.104064 | light `A<50`: +0.104064 MeV |
| `FULLKNOWN-SHELL-002` | -0.070030 | -0.071641 | -0.026837 | -0.001094 | -0.376547 | +0.148840 | light `A<50`: +0.148840 MeV |
| `FULLKNOWN-SHELL-003` | -0.060145 | -0.061969 | -0.011248 | -0.022180 | -0.512894 | +0.259976 | light `A<50`: +0.259976 MeV |

### Non-Shell Controls

| Control | Full-known ΔMAE MeV | Holdout ΔMAE MeV | Training ΔMAE MeV | Magic-Z ΔMAE MeV | Magic-N ΔMAE MeV | Light ΔMAE MeV | Worst regression |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `SPECIFICITY-CONTROL-000` | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | none |
| `SPECIFICITY-CONTROL-001` | -0.049223 | -0.049534 | -0.040867 | -0.013187 | -0.074624 | +0.038573 | light `A<50`: +0.038573 MeV |
| `SPECIFICITY-CONTROL-002` | -0.023366 | -0.024623 | +0.010329 | -0.040672 | -0.040074 | -0.003718 | training slice: +0.010329 MeV |
| `SPECIFICITY-CONTROL-003` | +0.013189 | +0.016965 | -0.088079 | +0.049766 | -0.009468 | +0.168159 | light `A<50`: +0.168159 MeV |
| `SPECIFICITY-CONTROL-004` | +0.028133 | +0.033245 | -0.108958 | +0.234682 | +0.269621 | +0.178236 | magic-any: +0.289878 MeV |

## Interpretation

`SHELL_SPECIFIC_BUT_BOUNDED`

The strongest shell-axis candidate, `FULLKNOWN-SHELL-001`, remains better than
the strongest non-shell control on both full-known and primary-holdout MAE:

| Comparator | Candidate | Full-known ΔMAE MeV | Holdout ΔMAE MeV |
| --- | --- | ---: | ---: |
| Best shell-axis | `FULLKNOWN-SHELL-001` | -0.086092 | -0.091504 |
| Best non-shell control | `SPECIFICITY-CONTROL-001` | -0.049223 | -0.049534 |

The result is not broad robustness. Two simple non-shell controls, smooth-A
and neutron-excess asymmetry, also improve both key aggregate surfaces. They
do not match the best shell-axis candidate under the predeclared `0.01 MeV`
comparability margin, but they keep the shell-axis interpretation bounded.

The `TASK-0316` stability audit remains decisive context: shell-axis
coefficients are fragile under exhaustive 8-of-11 resampling. Specificity
controls therefore keep the lane alive only as bounded sandbox evidence, not
as a promoted claim.

## Limitations

- All fitted coefficients use only the 11-row NMD-0002 residual slice.
- The full-known surface is committed repository data, not a future
  measurement reveal.
- Low-degree controls are diagnostic and are not promoted formula candidates.
- Light `A<50` remains a visible regression zone for all three shell-axis
  candidates.
- No prediction registry, canonical result, claim, or knowledge artifact is
  updated.

## Verdict

`SHELL_SPECIFIC_BUT_BOUNDED`

The shell-axis signal is stronger than the simple non-shell controls tested
here, but comparable low-degree controls are not completely inert and the
coefficient-fragility warning from `TASK-0316` remains active. The safe next
step is continued sandbox diagnostics, not registry expansion, reveal scoring,
or claim promotion.
