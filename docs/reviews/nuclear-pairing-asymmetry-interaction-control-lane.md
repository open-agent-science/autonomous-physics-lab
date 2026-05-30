# Nuclear Pairing-Asymmetry Interaction Control Lane

**Task:** `TASK-0474`
**Agent run:** `AGENT-RUN-0046`
**Campaign:** `nuclear-mass-surface`
**Verdict:** `NEGATIVE_RESULT` (maps to agent_run schema `FALSIFIED`)
**Sandbox only:** true

## Candidate

- Feature: `interaction = pairing_sign(Z,N) * ((N-Z)/A)` (closed-form, residual-free).
- Fit: `r_corr = beta * interaction` via least squares on the 11-row NMD-0002 training slice. `beta = +1.9170 MeV`.

## Aggregate MAE (MeV)

| Surface | baseline | candidate | smooth_a | asymmetry_only | pairing_only | matched_degree_random |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `training_lstsq` | 2.8245 | 2.8396 | 2.7999 | 2.8349 | 2.8245 | 2.8372 |
| `primary_holdout` | 4.5526 | 4.5653 | 4.5117 | 4.5279 | 4.5526 | 4.5626 |
| `full_known` | 4.4904 | 4.5032 | 4.4501 | 4.4671 | 4.4904 | 4.5006 |

## Coefficient Stability (leave-one-out)

- LOO folds: 11
- mean beta: 1.9597 MeV
- std beta: 6.3248 MeV
- sign-flip count vs mean: 1 (threshold 2)

## Verdict Rationale

- full_known candidate vs baseline: -0.0128 MeV
- Candidate fails the 0.25 MeV survival margin on full_known vs baseline.

## Per-Subset Behavior (full_known)

| Subset | count | baseline MAE | candidate MAE | delta |
| --- | ---: | ---: | ---: | ---: |
| `double_magic` | 5 | 3.0219 | 2.8769 | 0.1450 |
| `light_a_lt_50` | 24 | 1.8723 | 1.8167 | 0.0556 |
| `magic_n` | 17 | 4.9920 | 4.9285 | 0.0636 |
| `magic_z` | 13 | 3.5843 | 3.4572 | 0.1271 |
| `neutron_rich` | 162 | 5.3198 | 5.3449 | -0.0252 |

## Leakage Audit

- Feature uses only `Z`, `N`, and `A` through pairing sign and neutron excess. No baseline residual, error rank, candidate-fit residual, source-status, or future comparison row enters feature construction. PASS
- `beta` is fit by closed-form least squares on training only; no candidate-fit residual feeds controls. ✅
- All four controls (smooth_a, asymmetry_only, pairing_only, matched_degree_random) share the same fit and evaluation surfaces. ✅
- Coefficient stability LOO uses only training-row exclusion; no candidate-fit residual feeds the stability check. ✅

## Custom Verdict Vocabulary

Per the TASK-0474 specification, this lane uses a custom verdict set capped at `BOUNDED_DIAGNOSTIC`. No registry expansion is authorized regardless of outcome; the Nuclear controls-first gauntlet (TASK-0333) remains in force.

| Custom verdict | Meaning | Maps to schema |
| --- | --- | --- |
| `BOUNDED_DIAGNOSTIC` | candidate beat baseline + all four controls and is sign-stable, but the lane caps here (no registry expansion) | `REVIEW_NEEDED` |
| `CONTROL_DOMINATED` | at least one control matches the candidate within the margin | `REVIEW_NEEDED` |
| `FRAGILE_INCONCLUSIVE` | coefficient sign flips under LOO or a control MAE is undefined | `INCONCLUSIVE` |
| `NEGATIVE_RESULT` | candidate fails the 0.25 MeV survival margin against baseline | `FALSIFIED` |

## Promotion Boundary

- `sandbox_only: true`
- `writes_canonical_result: false`
- `claim_promotion_allowed: false`
- `prediction_registry_allowed: false`
- Required next step: maintainer review before any follow-up. No `PRED-XXXX`, `RESULT-XXXX`, `CLAIM-XXXX`, or `KNOW-XXXX` artifact is created by this run.

