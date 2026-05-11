# PFF-004: Accuracy-Complexity Tradeoff — model_t4_x1 vs model_t2_x1_x4

## Models Under Comparison

Both models are drawn from the EXP-0001/RUN-0003 gauntlet leaderboard (`results/EXP-0001/RUN-0003/result.yaml`). All metrics reported here are valid only within the configured amplitude range stated below.

### model_t4_x1

```
T/T0 = 1 + a*theta^4 + b*x     where x = sin²(θ/2)
```

Fitted coefficients: `a = 0.008923`, `b = 0.249792`

| Metric | Value |
|--------|-------|
| Complexity score | 2 |
| Train MRE | 3.58×10⁻⁶ |
| Test MRE | 3.05×10⁻⁴ |
| Composite score | 0.00254 |
| Verdict | VALID |

### model_t2_x1_x4

```
T/T0 = 1 + a*theta^2 + b*x + c*x^4     where x = sin²(θ/2)
```

Fitted coefficients: `a = 0.10759`, `b = −0.18049`, `c = 0.08044`

| Metric | Value |
|--------|-------|
| Complexity score | 3 |
| Train MRE | 7.79×10⁻⁷ |
| Test MRE | 2.14×10⁻⁵ |
| Composite score | 0.00304 |
| Verdict | VALID |

---

## Metric-by-Metric Comparison

### Which metric favors each model

**Composite score favors `model_t4_x1`:**

`model_t4_x1` achieves composite score 0.00254 vs 0.00304 for `model_t2_x1_x4`, a relative difference of ~20%. The composite score penalizes both error and complexity; the lower complexity of `model_t4_x1` (score 2 vs 3) tips the balance in its favor.

**Test MRE strongly favors `model_t2_x1_x4`:**

On the test window (1.11–1.57 rad), `model_t2_x1_x4` achieves MRE ≈ 2.14×10⁻⁵, compared to 3.05×10⁻⁴ for `model_t4_x1`. This is approximately **14× better test-set accuracy** with one additional atom.

**Train MRE also favors `model_t2_x1_x4`:**

On the train window (0.01–1.10 rad), `model_t2_x1_x4` achieves MRE ≈ 7.79×10⁻⁷ vs 3.58×10⁻⁶, approximately **4.6× better**.

---

## What the Tradeoff Means

Adding one atom (complexity 2 → complexity 3) by moving from `model_t4_x1` to `model_t2_x1_x4` produces:

- A ~14× improvement in test MRE (large-angle accuracy).
- A ~4.6× improvement in train MRE.
- A cost of 0.0005 units in composite score (composite score rises from 0.00254 to 0.00304).

In composite-score terms, `model_t4_x1` is the leaderboard winner. In raw large-angle accuracy terms, `model_t2_x1_x4` is substantially more precise within the test window. The appropriate choice between the two depends on whether the use case prioritizes parsimony (fewer atoms, lower composite score) or accuracy in the 1.11–1.57 rad range.

Neither model should be preferred without acknowledging the use-case context. Both verdicts are `VALID` within the configured range; neither is unconditionally superior.

---

## Scope of Conclusions

All conclusions in this note apply **only** to the configured amplitude ranges:

- Train window: 0.01–1.10 rad
- Test window: 1.11–1.57 rad (≈ π/2)

Neither model has been evaluated beyond π/2. The near-separatrix extrapolation diagnostic for `model_t4_x1` (FAIL, MRE ≈ 14% at θ ∈ [2.36, 3.14]) suggests both models should be treated as range-limited approximations.

---

## Limitation Statement

The comparison above is restricted to the EXP-0001/RUN-0003 configured range. No claim is made that either model represents the best possible formula for the pendulum period, the final answer for any scientific question, or that one model is universally superior to the other. The composite score weighting scheme is a heuristic; different weighting choices would shift the ranking. Both models are linear-in-coefficients, fitted by least squares from a fixed ten-atom basis; no exhaustive search over functional forms has been performed.
