# Quantum Almeida Fixed-Model LOO Stress Test

Task: `TASK-0816`

## Method

This run uses only the six committed Almeida 2023 InP rows. It compares the
zero-parameter published Almeida reference against one predeclared low-
flexibility diagnostic, `E = E_Almeida_fixed(L) + b_train`, and one negative
control, the training-set mean energy.

## LOO Metrics

| Held-out row | fixed abs error (eV) | offset abs error (eV) | constant abs error (eV) | fitted offset (eV) |
| --- | ---: | ---: | ---: | ---: |
| `almeida-2023-inp-460nm` | 0.068261883 | 0.083815694 | 0.413800000 | 0.015553811 |
| `almeida-2023-inp-480nm` | 0.077631072 | 0.091255853 | 0.279400000 | -0.013624780 |
| `almeida-2023-inp-510nm` | 0.118561341 | 0.140372175 | 0.097000000 | -0.021810834 |
| `almeida-2023-inp-550nm` | 0.013350348 | 0.017921851 | 0.115400000 | 0.004571504 |
| `almeida-2023-inp-580nm` | 0.056678002 | 0.069915037 | 0.254600000 | 0.013237035 |
| `almeida-2023-inp-620nm` | 0.048395010 | 0.059975446 | 0.420200000 | 0.011580436 |

## Summary

- Fixed-reference LOO MAE: `0.063812943 eV`
- Additive-offset LOO MAE: `0.077209343 eV`
- Constant-mean LOO MAE: `0.263400000 eV`
- Offset minus fixed LOO MAE: `0.013396400 eV`
- Original five-train-row fixed train MAE: `0.066896529 eV`
- Original five-train-row offset train MAE: `0.069212617 eV`
- Original 620 nm holdout fixed error: `0.048395010 eV`
- Original 620 nm holdout offset error: `0.059975446 eV`

## Verdict

`QUANTUM_LOO_STRESS_UNSTABLE`

The one-parameter offset does not improve the original training rows and
worsens the original one-point holdout and the six-fold LOO mean error relative
to the zero-parameter fixed Almeida reference. This is methodology memory only
and does not unblock `TASK-0226`.
