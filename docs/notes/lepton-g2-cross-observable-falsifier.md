# Lepton g-2 Cross-Observable Falsifier

**Status:** IMPLEMENTED UNDER TASK-0227 (sandbox-only)
**Implementation Task:** `TASK-0227`
**Upstream:** `EXP-0010` (muon g-2 formula-search stress test, `TASK-0127`)
**Guardrail Hardening Reference:** `TASK-0147`

---

## 1. Purpose

`EXP-0010` is a guarded muon g-2 formula-search stress test. It surfaced one
guardrail-screened hit (`α³ × (mμ/me)⁻² × (mμ/mτ)⁻²`, the F4 family) and one
unscreened reference hit (`(1/3) × (α/π)³ × (mμ/mπ⁰)²`, the F3 family).

A surviving formula-search hit on a single observable is, by itself, evidence
of *nothing*. Numerology pressure is high. To keep `EXP-0010` honest we need
at least one cross-observable consistency check before any candidate is
discussed as a potential mechanism. This falsifier is that check, targeting
the electron anomalous magnetic moment `a_e`.

The cross-check is **not** a new formula-search campaign. It does not search
for electron g-2 formulas, does not promote any candidate to a claim, and does
not aggregate `Δa_e` across α sources as if they shared a Standard Model
input.

## 2. Inputs

Source-data file: [`data/particle_physics/electron_g2.yaml`](../../data/particle_physics/electron_g2.yaml)

It records:

- the most precise direct `a_e` measurement (Fan et al. 2023);
- the SM prediction evaluated with α(Cs) (Parker 2018);
- the SM prediction evaluated with α(Rb) (Morel 2020);
- the resulting `Δa_e` residuals `Δa_e(Cs)` and `Δa_e(Rb)`.

Δa_e changes sign between the two α sources:

| Residual | Δa_e | σ | Notes |
|---|---|---|---|
| `delta_a_e_cs` | −1.02 × 10⁻¹² | 0.27 × 10⁻¹² | ~3.8σ tension with α(Cs) |
| `delta_a_e_rb` |  +0.34 × 10⁻¹² | 0.16 × 10⁻¹² | ~2σ tension with α(Rb) |

The α-source dependence is exactly why a single residual is not a safe target.
Any candidate that matches one row but not the other is flagged as
`overfit`.

## 3. Cross-Check Procedure

For each registered muon-g-2 candidate from `EXP-0010`:

1. Build the **electron analog** by formal substitution `m_μ → m_e`. Mass
   ratios involving `m_μ` translate to electron-scale equivalents using
   `m_e/m_τ = (m_μ/m_τ) × (m_e/m_μ)` and the same for `m_e/m_π⁰`.
2. Evaluate the analog with the same `α`, `m_μ/m_e`, etc. constants used in
   `EXP-0010`.
3. Compare the analog prediction against both `Δa_e(Cs)` and `Δa_e(Rb)`.

The candidate registry is intentionally narrow:

| Candidate | Muon-side formula | Notes |
|---|---|---|
| `F4_hit` | `α^3 × (m_μ/m_e)^-2 × (m_μ/m_τ)^-2` | F4 guardrail-screened hit |
| `F3_one_third` | `(1/3) × (α/π)^3 × (m_μ/m_π⁰)^2` | F3 rational candidate |
| `naive_msq_scaling` | `Δa_μ × (m_e/m_μ)^2` | Same-mechanism mass-squared baseline |

Adding candidates requires a new maintainer-approved task. The cross-check
is a falsifier surface, not a fishing net.

## 4. Verdict Vocabulary

Each candidate receives one of four verdicts:

- **`null`** — the predicted analog `|Δa_e|` is below 0.5σ of every Δa_e
  residual. The candidate is too small for the current measurement to
  distinguish, so the cross-check is uninformative.
- **`inconsistent`** — every Δa_e residual has |z| > 3σ relative to the
  prediction. The candidate is incompatible with both α-source rows.
- **`overfit`** — the prediction agrees with one α-source row at ≤ 2σ and
  disagrees with the other at > 3σ. "Working only for the right α" is a
  cherry-picking failure mode, not evidence.
- **`review_needed`** — anything else (marginal or ambiguous outcomes).

The global verdict collapses the per-candidate results to the most
conservative single label, in order `INCONSISTENT_AT_ELECTRON` ← `OVERFIT_SUSPECT`
← `REVIEW_NEEDED` ← `NULL`.

## 5. Current Output

Running `physics_lab.engines.lepton_g2_cross_check.run_cross_check()` against
the committed data file yields:

| Candidate | Electron analog value | Cs comparison | Rb comparison | Verdict |
|---|---|---|---|---|
| `F4_hit` | ≈ 4.7 (dimensionless) | z ≈ 10¹³ | z ≈ 10¹³ | `inconsistent` |
| `F3_one_third` | ≈ 6.0 × 10⁻¹⁴ | rel ≈ 0.22σ | rel ≈ 0.37σ | `null` |
| `naive_msq_scaling` | ≈ 5.8 × 10⁻¹⁴ | rel ≈ 0.22σ | rel ≈ 0.36σ | `null` |

**Global verdict:** `INCONSISTENT_AT_ELECTRON`.

What this means:

- The `EXP-0010` F4 muon hit is dramatically *not* a generic lepton-anomaly
  formula. Under `m_μ → m_e` the structure that fit `Δa_μ` produces an
  electron prediction ~12 orders of magnitude away from `Δa_e`. This is a
  clean negative result on the cross-observable consistency check.
- The F3 `c = 1/3` candidate and the naive `m²` scaling baseline both produce
  electron predictions below current `Δa_e` measurement precision. The
  cross-check cannot rule them in or out at this observable; it is reported
  as `null`, not as support.

The result is sandbox-only. It does not modify `CLAIM-0008`, it does not
promote any candidate, and it does not change `EXP-0010`'s stress-test
framing. The intended use is as one of several guardrail-hardening checks
listed in [`docs/notes/g2-anomaly-formula-search-design.md`](./g2-anomaly-formula-search-design.md).

## 6. Forbidden Uses

- Do not present any candidate as an electron g-2 explanation, formula, or
  BSM signal.
- Do not aggregate `Δa_e(Cs)` and `Δa_e(Rb)` as if they shared an SM input.
- Do not characterise the F4 inconsistency as evidence "against new physics"
  — the cross-check rules out a *formula-search analog*, not a physical
  mechanism that could behave differently across leptons.
- Do not introduce electron-g-2 formula-search families. The falsifier is not
  a launching pad for a new flagship campaign.
- Do not expand the candidate registry without a new maintainer-approved
  task.

## 7. Files

- Engine: [`physics_lab/engines/lepton_g2_cross_check.py`](../../physics_lab/engines/lepton_g2_cross_check.py)
- Tests: [`tests/test_lepton_g2_cross_check.py`](../../tests/test_lepton_g2_cross_check.py)
- Data: [`data/particle_physics/electron_g2.yaml`](../../data/particle_physics/electron_g2.yaml)
- Upstream design: [`docs/notes/g2-anomaly-formula-search-design.md`](./g2-anomaly-formula-search-design.md)
