# Koide Baseline Planning

**Task:** `TASK-0082`
**Type:** `benchmark_planning` — planning only, no implementation
**Related track:** `docs/notes/particle-mass-relation-track.md`
**Updated after:** EXP-0007 (neutrino Koide, INVALID) and EXP-0008 (quark Koide, INVALID)

---

## Purpose

Before any broader Koide-style search or claim promotion, APL needs at least
one explicit baseline that puts numerical results in context. Without a
baseline, a statement like "Q = 0.666664 for charged leptons" has no
calibration: it is unknown whether this is remarkable, expected, or an artefact
of looking only at a favourable triplet.

This document defines three baseline designs for Koide-style evaluation and
states the conditions under which each applies.

---

## Current State of the Koide Track

| Experiment | Sector | Q value | Gap to 2/3 | Verdict |
|------------|--------|--------:|-----------|---------|
| EXP-0004 | Charged leptons (e, μ, τ) | 0.666664 | −0.000003 | VALID |
| EXP-0005 | Tau holdout prediction | — | Δm = 0.039 MeV | VALID |
| EXP-0007 | Neutrinos (NH / IH) | ≤ 0.584 | 70.7σ / 421,889σ below | INVALID |
| EXP-0008 | Up quarks (u, c, t) | 0.849 | 159.2σ above | INVALID |
| EXP-0008 | Down quarks (d, s, b) | 0.731 | 8.8σ above | INVALID |

Q = 2/3 appears to be specific to charged leptons. Baselines are needed to
quantify how surprising this specificity is.

---

## Baseline Design 1 — Analytic Q Range Prior

### What it is

The Koide quantity Q = (m₁+m₂+m₃)/(√m₁+√m₂+√m₃)² is bounded analytically:

- **Lower bound:** Q = 1/3 when all three masses are equal (by Cauchy-Schwarz equality).
- **Upper bound:** Q → 1 when one mass dominates the other two (ratio → ∞).

The range is therefore [1/3, 1], width 2/3.

### Comparison rule

For a precision window of half-width ε around the target Q = 2/3, the fraction
of the accessible Q range covered is:

```
f(ε) = 2ε / (1 − 1/3) = 3ε
```

| ε (half-width) | Fraction of Q range |
|---------------|-------------------|
| 0.1 | 30% |
| 0.01 | 3% |
| 0.001 | 0.3% |
| 3×10⁻⁵ (charged leptons) | 0.009% |

### Calibration purpose

This baseline does not model realistic mass distributions. It simply states the
prior width of the Q space. A result within 3×10⁻⁵ of 2/3 occupies less than
0.01% of the range — this is a necessary but not sufficient signal that the
charged-lepton result is non-trivial.

### Guardrail interaction

This baseline is conservative: it does not penalise cherry-picking, free
parameters, or scheme choices. The fraction 0.009% should be paired with the
number of triplets evaluated; if many triplets were tried, the analytic range
alone does not establish significance.

---

## Baseline Design 2 — Log-Uniform Random Triplet Baseline

### What it is

Sample mass triplets (m₁, m₂, m₃) where each mass is drawn independently from
a log-uniform distribution over a relevant range, then compute Q for each
triplet and record what fraction land within ε of a target value.

### Eligible pool

Masses drawn from log-uniform over [m_e, m_t] = [0.511 MeV, 172,690 MeV] — the
full charged-fermion mass range of the Standard Model.

### Comparison rule

For each sampled triplet:
1. Sort masses m₁ ≤ m₂ ≤ m₃.
2. Compute Q = (Σmᵢ) / (Σ√mᵢ)².
3. Record whether |Q − 2/3| < ε.

Repeat N ≥ 10,000 times. Report:
- empirical fraction within ε of 2/3 as a function of ε;
- the empirical Q distribution (histogram);
- comparison: how many standard deviations is the charged-lepton Q from the
  random-triplet mean?

### Calibration purpose

This baseline provides a realistic null distribution for Q over the SM fermion
mass range. It answers: "If you picked three random fermion-scale masses, how
often would you accidentally land near Q = 2/3?"

Unlike Baseline 1, it reflects the shape of Q under hierarchical mass
distributions typical of SM particles.

### Guardrail interaction

This baseline should be reported alongside any Koide-style triplet search. If
the fraction of random triplets near 2/3 is non-negligible, that weakens the
interpretation of any one result. The baseline penalises implicit cherry-picking
by requiring comparison against all equally valid random draws.

### Implementation note (future)

This baseline does not require a new engine. It can be implemented in a single
script using `numpy` and the engine function `koide_q_real` from
`physics_lab/engines/koide_quark.py`. Expected runtime: < 1 second.

---

## Baseline Design 3 — SM Particle Enumeration Baseline

### What it is

Enumerate all unordered triplets from a fixed set of SM fundamental fermions,
compute Q for each, and report the distribution. No sampling — exhaustive over
the declared pool.

### Eligible pool (17 particles, PDG 2024 central values)

| Particle | Mass (MeV) | Type |
|----------|----------:|------|
| νe, νμ, ντ | scenario-dependent | neutrinos (NH best-fit) |
| e | 0.511 | charged lepton |
| μ | 105.66 | charged lepton |
| τ | 1776.86 | charged lepton |
| u | 2.16 | quark (MS-bar, 2 GeV) |
| d | 4.67 | quark (MS-bar, 2 GeV) |
| s | 93.4 | quark (MS-bar, 2 GeV) |
| c | 1270 | quark (MS-bar, mc) |
| b | 4183 | quark (MS-bar, mb) |
| t | 172690 | quark (pole) |

Total triplets from 10 non-neutrino particles: C(10,3) = 120.
Including 3 neutrinos (NH scenario): C(13,3) = 286.

**Forbidden triplets** (per TASK-0039 guardrails):
- cross-family triplets (lepton + quark) — forbidden by default;
- triplets with incompatible mass types or schemes.

After applying guardrails, the eligible intra-family triplets are:
- Charged leptons: C(3,3) = 1
- Up quarks: C(3,3) = 1
- Down quarks: C(3,3) = 1
- Neutrinos: C(3,3) = 1

Total: 4 intra-family triplets (already evaluated in EXP-0004 / EXP-0007 / EXP-0008).

### Comparison rule

For each eligible triplet: compute Q and rank by |Q − 2/3|. Report the full
table. This shows how the charged-lepton result ranks among all co-eligible
triplets.

### Calibration purpose

Within the guardrail-compliant pool, charged leptons are the only triplet with
Q ≈ 2/3. All other intra-family triplets miss by at least 8.8σ. This makes
the charged-lepton result rank 1 of 4 — a necessary result for a unique
observation, but also means the search space is too narrow for statistical
significance from enumeration alone.

This baseline motivates Baseline 2 (random draws): to assess significance one
must compare against a realistic larger pool, not just the four intra-family
triplets.

---

## How These Baselines Interact with Scoped Verdict Wording

APL's verdicts for particle-mass results are scoped by design. Adding baseline
context does not change verdicts — it adds calibration. The intended wording
pattern is:

> "Q = 0.666664 for charged leptons (VALID). Under the log-uniform random
> triplet baseline, fewer than X% of random SM-scale triplets land within
> this window of 2/3, suggesting the result is not easily explained by
> chance sampling of the Q range."

The baseline does **not** license:
- the word "discovery";
- cross-family generalisation;
- explanatory claims about mass generation;
- claim promotion from DRAFT to CONFIRMED without maintainer review.

---

## Priority Order for Implementation

| Baseline | Implementation cost | Scientific value | Recommended order |
|----------|-------------------|-----------------|-----------------|
| Analytic range (B1) | zero — already computed | Gives quick context | Include in any result report |
| SM enumeration (B3) | trivial — 4 triplets done | Completes the family survey | Already done via EXP-0004/0007/0008 |
| Log-uniform random (B2) | ~20 lines of numpy | Provides null distribution | First new implementation needed |

---

## What This Planning Does Not Cover

- GUT-scale or RGE-unified masses: testing whether Koide holds at a common
  renormalization scale is a separate experiment, not covered here.
- Cross-family triplets: explicitly forbidden by default per TASK-0039.
- Composite particles (hadrons): high-risk territory; deferred.
- Non-equal-phase Brannen extensions with additional free parameters: already
  tested in EXP-0008; planning for further extensions is out of scope here.
- Koide-like formulas with different target values (Q ≠ 2/3): possible future
  falsifier track, not planned here.

---

## Recommended Next Steps

1. **Implement Baseline 2 (log-uniform random)** as a microtask or small
   canonical experiment. No new workflow needed — uses existing engine.
2. **Add B1 analytic fraction to EXP-0004/0007/0008 result reports** as a
   supplementary calibration note (low-effort update).
3. **Reference this baseline design** in any future Koide-style triplet search
   task (e.g., TASK-0040 when it moves from PROPOSED to READY).
