# Nuclear Magic-Distance Z×N Interaction Control Lane

**Task:** `TASK-0475`
**Agent run:** `AGENT-RUN-0047`
**Campaign:** `nuclear-mass-surface`
**Verdict:** `NEGATIVE_RESULT` (maps to agent_run schema `FALSIFIED`)
**Sandbox only:** true

## Candidate

- Feature: `interaction = pairing_sign(Z,N) * max(exp(-z_dist^2/8), exp(-n_dist^2/8))` (closed-form, residual-free).
- Fit: `r_corr = beta * interaction` via least squares on the 11-row NMD-0002 training slice. `beta = +0.6717 MeV`.

## Aggregate MAE (MeV)

| Surface | baseline | candidate | smooth_a | asymmetry_only | parity_only | magic_distance_only | shuffled_label |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `training_lstsq` | 2.8245 | 2.8274 | 2.7999 | 2.8349 | 2.2156 | 2.8836 | 3.2321 |
| `primary_holdout` | 4.5526 | 4.5981 | 4.5117 | 4.5279 | 4.6258 | 4.4663 | 4.4822 |
| `full_known` | 4.4904 | 4.5345 | 4.4501 | 4.4671 | 4.5392 | 4.4094 | 4.4373 |

## Coefficient Stability (leave-one-out)

- LOO folds: 11
- mean beta: 0.6676 MeV
- std beta: 0.4760 MeV
- sign-flip count vs mean: 1 (threshold 2)

## Verdict Rationale

- full_known candidate vs baseline: -0.0440 MeV
- Candidate fails the 0.25 MeV survival margin on full_known vs baseline.

## Per-Subset Behavior (full_known)

| Subset | count | baseline MAE | candidate MAE | delta |
| --- | ---: | ---: | ---: | ---: |
| `double_magic` | 5 | 3.0219 | 2.6938 | 0.3281 |
| `light_a_lt_50` | 24 | 1.8723 | 1.9429 | -0.0706 |
| `magic_n` | 17 | 4.9920 | 4.8949 | 0.0971 |
| `magic_z` | 13 | 3.5843 | 3.5098 | 0.0745 |
| `neutron_rich` | 162 | 5.3198 | 5.3518 | -0.0320 |

## Leakage Audit

- Feature uses only `Z`, `N` (via parity and magic-distance from the published magic-number list). No `A`, baseline residual, error rank, candidate-fit residual, source-status, or future comparison row enters feature construction. ✅
- `beta` is fit by closed-form least squares on training only; no candidate-fit residual feeds controls. ✅
- All five controls (smooth_a, asymmetry_only, parity_only, magic_distance_only, shuffled_label) share the same fit and evaluation surfaces. ✅
- Coefficient stability LOO uses only training-row exclusion; no candidate-fit residual feeds the stability check. ✅

## Custom Verdict Vocabulary

Per the TASK-0475 specification, this lane uses a custom verdict set capped at `BOUNDED_DIAGNOSTIC`. No registry expansion is authorized regardless of outcome; the shell-axis post-audit decision (TASK-0333) remains in force.

| Custom verdict | Meaning | Maps to schema |
| --- | --- | --- |
| `BOUNDED_DIAGNOSTIC` | candidate beat baseline + all five controls and is sign-stable, but the lane caps here (no registry expansion) | `REVIEW_NEEDED` |
| `CONTROL_DOMINATED` | at least one control matches the candidate within the margin | `REVIEW_NEEDED` |
| `FRAGILE_INCONCLUSIVE` | coefficient sign flips under LOO or a control MAE is undefined | `INCONCLUSIVE` |
| `NEGATIVE_RESULT` | candidate fails the 0.25 MeV survival margin against baseline | `FALSIFIED` |

## Promotion Boundary

- `sandbox_only: true`
- `writes_canonical_result: false`
- `claim_promotion_allowed: false`
- `prediction_registry_allowed: false`
- Required next step: maintainer review before any follow-up. No `PRED-XXXX`, `RESULT-XXXX`, `CLAIM-XXXX`, or `KNOW-XXXX` artifact is created by this run.

