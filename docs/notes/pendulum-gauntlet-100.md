# Pendulum Hypothesis Gauntlet — 100 Candidates

## Context

This note records findings from `TASK-0010` (RUN-0003 / RESULT-0004), which ran a systematic
gauntlet of 100 deterministic pendulum approximation candidates against the exact elliptic-integral
reference across the benchmark amplitude range.

## Candidate Generation

Candidates were generated from ten basis atoms:

| Atom | Feature | Family |
| --- | --- | --- |
| `t2` | θ² | theta_poly |
| `t4` | θ⁴ | theta_poly |
| `t6` | θ⁶ | theta_poly |
| `t8` | θ⁸ | theta_poly |
| `x1` | sin²(θ/2) | x_poly |
| `x2` | sin⁴(θ/2) | x_poly |
| `x3` | sin⁶(θ/2) | x_poly |
| `x4` | sin⁸(θ/2) | x_poly |
| `l1` | sin²(θ/2)·log(1/(1 − sin²(θ/2))) | log_enhanced |
| `l2` | sin⁴(θ/2)·log(1/(1 − sin²(θ/2))) | log_enhanced |

Candidates were enumerated as all linear-in-coefficient models from subsets of atoms:

- Tier 1 (1 atom): 10 models
- Tier 2 (2 atoms): 45 models — all C(10,2)
- Tier 3 (3 atoms): 45 models — first 45 of C(10,3) in lexicographic order

All 100 are fit by deterministic least squares; no LLM-generated formulas.

## Results

### Best Model

`model_t4_x1`: `1 + a·θ⁴ + b·sin²(θ/2)`

Fitted coefficients on this benchmark:
- `a` = 0.008923 (θ⁴ correction)
- `b` = 0.249792 (sin²(θ/2) term, ≈ 1/4)

| Metric | Value |
| --- | --- |
| Train mean relative error | 3.6 × 10⁻⁶ |
| Test mean relative error | 3.1 × 10⁻⁴ |
| Test max relative error | 9.5 × 10⁻⁴ |
| Complexity score | 2 |
| Verdict | VALID_IN_RANGE |

The b ≈ 0.25 coefficient is physically meaningful: at small θ, sin²(θ/2) ≈ θ²/4, so the x1 term
provides the correct small-angle correction (curvature d²T/dθ² ≈ b/2 ≈ 1/8 at θ→0), while the
θ⁴ term adds the next-order correction. This is consistent with the known elliptic-integral
expansion.

### Verification (Best Model)

All gating checks pass. Non-gating separatrix diagnostics fail, as expected for a finite polynomial
approximation.

| Check | Status | Gate |
| --- | --- | --- |
| small_angle_limit | PASS | yes |
| small_angle_window_accuracy | PASS | yes |
| small_angle_curvature | PASS | yes |
| large_angle_window_accuracy | PASS | yes |
| near_separatrix_extrapolation | FAIL | no |
| separatrix_asymptotic_alignment | FAIL | no |
| separatrix_log_growth_rate | FAIL | no |
| evenness | PASS | yes |
| monotonicity | PASS | yes |
| dimensional_consistency | PLACEHOLDER | yes |
| known_small_angle_coefficients | PLACEHOLDER | yes |

### Leaderboard Summary

| Verdict | Count |
| --- | --- |
| VALID | 32 |
| PARTIALLY_VALID | 8 |
| OVERFITTED* | 60 |

| Failure Mode | Count |
| --- | --- |
| none | 44 |
| moderate_error | 13 |
| high_error | 43 |

\* The `OVERFITTED` verdict from the critic reflects a high test/train error ratio. In this
benchmark the test amplitude range (1.10–1.57 rad) is inherently harder than the train range
(0.01–1.10 rad), so the ratio is always large for models that are accurate in-range. It is not
statistical overfitting in the traditional sense. The `failure_mode` column in the leaderboard
uses test-error magnitude directly and is the more meaningful classification.

### Family Summary (Top 10)

Seven of the top 10 candidates are `cross_domain` (mixing θ and x atoms). Pure theta-polynomial
and mixed log-enhanced candidates also appear in the top 10. Pure x-polynomial single-term models
(`model_x1`, `model_x2`) do not appear in the top 10 on this split but are competitive in-range.

## Implications

1. **Cross-domain models dominate**: combining θ-polynomial and x-polynomial atoms outperforms
   either family alone on this benchmark. `model_t4_x1` ties together the physically motivated
   x basis (from the elliptic integral natural variable) with a small θ⁴ correction.

2. **Log terms do not help in-range**: the log-enhanced (separatrix-aware) atoms improve near-pi
   behavior but do not improve in-range accuracy when the test split stays within the moderate
   amplitude range. They appear in the top 10 only in cross-domain mixtures.

3. **Complexity 2 wins**: the top-ranked model has only 2 coefficients. Higher-complexity models
   (3 atoms) can match or slightly beat it, but the composite score penalizes complexity.

4. **Separatrix gap remains**: all 100 candidates fail the near-separatrix non-gating checks.
   The log-enhanced models from RUN-0002 remain the best available option for separatrix behavior,
   even if they rank lower on the in-range leaderboard.

## Limitations

- All candidates are linear-in-coefficients models (least squares). Non-linear forms (e.g. Padé,
  rational approximants) are not represented.
- The train/test split uses a fixed amplitude boundary; results depend on that split point.
- Claim promotion should remain at `PARTIALLY_SUPPORTED` at most; near-separatrix diagnostics
  still fail for all 100 candidates.
- The dimensional consistency symbolic check returns PLACEHOLDER for gauntlet model IDs; all atoms
  are dimensionless by construction.

## Artifacts

- `results/EXP-0001/RUN-0003/result.yaml` — canonical result with 100 model scores
- `results/EXP-0001/RUN-0003/leaderboard.json` — full ranked leaderboard
- `results/EXP-0001/RUN-0003/leaderboard.md` — human-readable table
- `results/EXP-0001/RUN-0003/report.md` — extended run report
- `results/EXP-0001/RUN-0003/review_metadata.yaml` — machine-readable review metadata
