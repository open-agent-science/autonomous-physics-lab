# Result Artifacts Index

This document is a compact navigation guide for all canonical result runs in
the repository. It is intended to help contributors understand what each run
produced without modifying any result artifacts.

> **Important:** Do not edit files under `results/` based on this index.
> This document is read-only reference material. All result artifacts are
> canonical and must not be changed outside of a dedicated task PR.

---

## Run Inventory

| Result ID | Run | Experiment | Title | Best Verdict |
|-----------|-----|------------|-------|--------------|
| RESULT-0001 | EXP-0001/RUN-0001 | EXP-0001 | Pendulum Formula Discovery | VALID_IN_RANGE |
| RESULT-0003 | EXP-0001/RUN-0002 | EXP-0001 | Pendulum Formula Discovery | VALID_IN_RANGE |
| RESULT-0004 | EXP-0001/RUN-0003 | EXP-0001 | Pendulum Formula Discovery — Gauntlet (100 Candidates) | VALID_IN_RANGE |
| RESULT-0002 | EXP-0002/RUN-0001 | EXP-0002 | Damped Oscillator Regime Verification | VALID_IN_RANGE |
| RESULT-0005 | EXP-0004/RUN-0004 | EXP-0004 | Charged-Lepton Koide Reproduction | VALID |
| RESULT-0006 | EXP-0005/RUN-0005 | EXP-0005 | Historical Tau Holdout Prediction | VALID |

---

## EXP-0001 / RUN-0001 — Pendulum Formula Discovery

**Result ID:** `RESULT-0001`
**Hypothesis:** `HYP-0001`
**Task:** `TASK-0001`

### Purpose
First baseline run of the pendulum formula discovery workflow. Tests a small
set of low-order approximation families against the exact pendulum period ratio.

### Train / Test Range
- Train: 0.01 to 1.10 rad
- Test: 1.11 to 1.57 rad (up to π/2)

### Key Files
- `results/EXP-0001/RUN-0001/result.yaml` — structured result with verdicts
- `results/EXP-0001/RUN-0001/metrics.json` — per-candidate error metrics
- `results/EXP-0001/RUN-0001/report.md` — human-readable summary
- `results/EXP-0001/RUN-0001/claim_update.md` — proposed claim update
- `results/EXP-0001/RUN-0001/knowledge_update.md` — proposed knowledge update

### Main Conclusion
Best candidate (`model_theta2_theta4`) achieved `VALID_IN_RANGE` verdict within
the configured amplitude range. Lower-order candidates were `OVERFITTED` or
`PARTIALLY_VALID`.

### Limitations
- Ideal mathematical pendulum only (no damping or driving force).
- Verdicts apply only to the configured train and test amplitude ranges.
- Near-separatrix extrapolation check failed for all candidates.
- Candidate formulas limited to predefined low-order approximation families.

---

## EXP-0001 / RUN-0002 — Theory-Aware Near-Separatrix Follow-up

**Result ID:** `RESULT-0003`
**Hypothesis:** `HYP-0001`
**Task:** `TASK-0003`

### Purpose
Follow-up run that adds theory-aware candidates designed to improve near-
separatrix behavior. Tests whether incorporating elliptic-integral structure
into the approximation family improves performance near large amplitudes.

### Train / Test Range
- Train: 0.01 to 1.10 rad
- Test: 1.11 to 1.57 rad (up to π/2)

### Key Files
- `results/EXP-0001/RUN-0002/result.yaml`
- `results/EXP-0001/RUN-0002/metrics.json`
- `results/EXP-0001/RUN-0002/report.md`
- `results/EXP-0001/RUN-0002/claim_update.md`
- `results/EXP-0001/RUN-0002/knowledge_update.md`

### Main Conclusion
Theory-aware candidate `model_x_x2_log` improved near-separatrix behavior
relative to RUN-0001 but did not produce a globally valid or exact formula.
Best verdict remains `VALID_IN_RANGE`.

### Limitations
- Same ideal-pendulum assumptions as RUN-0001.
- Improvement near separatrix is relative, not absolute.
- No global validity claim is made.

---

## EXP-0001 / RUN-0003 — Pendulum Gauntlet (100 Candidates)

**Result ID:** `RESULT-0004`
**Hypothesis:** `HYP-0001`
**Task:** `TASK-0010`

### Purpose
Large-scale gauntlet run evaluating 100 deterministic candidate formulas
against the exact pendulum reference. Produces a ranked leaderboard with
composite scores, diagnostics, and a precision audit.

### Train / Test Range
- Train: 0.01 to 1.10 rad
- Test: 1.11 to 1.57 rad (up to π/2)
- Total candidates: 100

### Key Files
- `results/EXP-0001/RUN-0003/result.yaml`
- `results/EXP-0001/RUN-0003/metrics.json`
- `results/EXP-0001/RUN-0003/report.md`
- `results/EXP-0001/RUN-0003/precision_audit.md`
- `results/EXP-0001/RUN-0003/precision_audit.yaml`
- `results/EXP-0001/RUN-0003/review_metadata.yaml`

### Main Conclusion
Top candidate `model_t4_x1` reached approximately `3.1e-4` mean relative
residual. A dedicated precision audit confirmed that error is model residual,
not numerical reference noise. Best verdict is `VALID_IN_RANGE`.

### Limitations
- All 100 candidates are linear-in-coefficients models fitted by least squares.
- Candidates drawn from a fixed basis of ten atoms; other functional forms not tested.
- Leaderboard ranks by composite score; top candidates may still fail separatrix diagnostics.
- No symbolic exactness claim and no global validity claim are made.

---

## EXP-0002 / RUN-0001 — Damped Oscillator Regime Verification

**Result ID:** `RESULT-0002`
**Hypothesis:** `HYP-0002`
**Task:** `TASK-0002`

### Purpose
Verification that the damped oscillator simulation correctly identifies
underdamped, critically damped, and overdamped regimes against exact analytical
solutions.

### Train / Test Range
- Train: 0.00 to 7.18 s
- Test: 7.23 to 12.00 s

### Scenarios
- `case_underdamped`: m=1.0, c=0.4, k=4.0
- `case_critical`: m=1.0, c=4.0, k=4.0
- `case_overdamped`: m=1.0, c=5.0, k=4.0

### Key Files
- `results/EXP-0002/RUN-0001/result.yaml`
- `results/EXP-0002/RUN-0001/metrics.json`
- `results/EXP-0002/RUN-0001/report.md`
- `results/EXP-0002/RUN-0001/review_metadata.yaml`

### Main Conclusion
All three damping regimes verified as `VALID` against exact linear solutions.
Best verdict is `VALID_IN_RANGE`.

### Limitations
- Linear damping only (no nonlinear damping or external driving force).
- Constant mass, damping, and stiffness assumed throughout.
- Verdicts apply only to the configured time range and scenario parameters.

---

## EXP-0004 / RUN-0004 — Charged-Lepton Koide Reproduction

**Result ID:** `RESULT-0005`
**Hypothesis:** `HYP-0004`
**Task:** `TASK-0037`

### Purpose
Narrow dataset-based reproduction of the Koide relation for charged leptons
(electron, muon, tau). Tests whether the exact Koide formula `Q = 2/3` holds
within measurement uncertainty using 2025 PDG mass values.

### Dataset
- Electron: 0.51099895 MeV ± 1.5e-10 MeV
- Muon: 105.6583755 MeV ± 2.3e-06 MeV
- Tau: 1776.93 MeV ± 0.09 MeV

### Key Files
- `results/EXP-0004/RUN-0004/result.yaml`
- `results/EXP-0004/RUN-0004/metrics.json`
- `results/EXP-0004/RUN-0004/report.md`
- `results/EXP-0004/RUN-0004/claim_update.md`
- `results/EXP-0004/RUN-0004/review_metadata.yaml`

### Main Conclusion
Observed Q = 0.666664, reference 2/3 = 0.666667. Relative difference:
3.3e-6. Result is `VALID` within stated uncertainty. This is a reproduction
benchmark, not a discovery or explanation of particle masses.

### Limitations
- Narrow dataset: three charged leptons only.
- No claim is made about why the Koide relation holds.
- Result does not extend to other particle families without separate benchmarks.
- Numerical agreement does not constitute symbolic proof.

---

## EXP-0005 / RUN-0005 — Historical Tau Holdout Prediction

**Result ID:** `RESULT-0006`
**Hypothesis:** `HYP-0005`
**Task:** `TASK-0038`

### Purpose
Historical holdout benchmark: predict the tau mass using only electron and muon
masses under the exact Koide relation, then compare against the measured tau
mass. Mirrors the historical predictive use of the Koide formula.

### Inputs
- Electron: 0.51099895 MeV ± 1.5e-10 MeV
- Muon: 105.6583755 MeV ± 2.3e-06 MeV

### Key Files
- `results/EXP-0005/RUN-0005/result.yaml`
- `results/EXP-0005/RUN-0005/metrics.json`
- `results/EXP-0005/RUN-0005/report.md`
- `results/EXP-0005/RUN-0005/review_metadata.yaml`

### Main Conclusion
Predicted tau mass: 1776.969 MeV. Measured tau mass: 1776.930 MeV. Absolute
difference: 0.039 MeV. Relative difference: 2.2e-5. Result is `VALID` within
the benchmark scope. This is a scoped holdout benchmark, not a physical
explanation or discovery-level claim.

### Limitations
- Prediction assumes exact Koide relation holds; this assumption is not
  independently justified by this benchmark.
- Predicted uncertainty (3.5e-5 MeV) is much smaller than observed difference
  (0.039 MeV), indicating the formula residual dominates over input uncertainty.
- Result does not extend to other particle families.
- No claim is made about why the Koide relation holds or whether it is exact.

---

## Artifact Navigation Guide

### To understand the pendulum campaign
Start with `EXP-0001/RUN-0003/report.md` (gauntlet summary) and
`docs/results/pendulum-gauntlet-100-summary.md`.

### To understand the particle mass campaign
Start with `EXP-0004/RUN-0004/report.md` (Koide reproduction) and
`EXP-0005/RUN-0005/report.md` (tau holdout). Read
`docs/results/koide-charged-lepton-reproduction.md` for the public summary.

### To inspect raw metrics
Each run contains `metrics.json` with per-candidate or per-scenario numerical
results. Do not modify these files.

### To inspect claim and knowledge proposals
Each run contains `claim_update.md` and `knowledge_update.md` with proposed
updates. These are proposals only — they are not promoted without maintainer
review.
