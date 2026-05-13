# Review: Autonomous Nuclear Pairing and Odd-Even Batch 01

**Agent run:** `AGENT-RUN-0011`
**Task:** `TASK-0201`
**Campaign:** nuclear-mass-surface
**Lane:** pairing and odd-even residual corrections
**Status:** SANDBOX_COMPLETE — awaiting maintainer review

---

## Purpose

This review document summarises the sandbox findings from the first pairing and
odd-even residual correction batch for the nuclear-mass-surface campaign.
It is written to support maintainer review of the batch PR and to preserve the
negative-result record in project scientific memory.

---

## What Was Tested

Two residual correction families were executed against the frozen RESULT-0015
semi-empirical baseline using the NMD-0002 structured holdout protocol and the
reviewed post-AME2020 primary holdout (295 rows):

1. **HYP-PROPOSAL-0038 — Differential even-even / odd-odd pairing**
   `r_corr = c_ee * η_ee(N,Z) + c_oo * η_oo(N,Z)`
   Allows the even-even enhancement and odd-odd suppression to have independent
   amplitudes, beyond the symmetric assumption in the standard pairing term.

2. **HYP-PROPOSAL-0039 — Wigner energy term for N=Z nuclei**
   `r_corr = w * δ(N=Z) / A`
   Adds an extra-binding correction for self-conjugate nuclei where the standard
   Bethe-Weizsäcker formula underestimates binding.

Three additional proposals were rejected before execution:
- HYP-PROPOSAL-0040 (data-sparsity overfit)
- HYP-PROPOSAL-0041 (collinearity with baseline pairing)
- HYP-PROPOSAL-0042 (feature redundancy)

---

## Key Findings

### Structured holdout (NMD-0002, 4 folds)

| Candidate | Improved | Regressed | Worst regression | Verdict |
|-----------|--------:|----------:|-----------------:|---------|
| HYP-PROPOSAL-0038 | 1 | 3 | +1.07 MeV | OVERFITTED |
| HYP-PROPOSAL-0039 | 1 | 1 | +0.54 MeV | INCONCLUSIVE |

### Post-AME2020 primary evaluation (n=295)

Baseline MAE: 4.553 MeV

| Candidate | Primary delta MAE | Activation |
|-----------|------------------:|-----------|
| HYP-PROPOSAL-0038 | +0.088 MeV | 68/295 (ee), 71/295 (oo) |
| HYP-PROPOSAL-0039 | +0.001 MeV | 3/295 (N=Z only) |

---

## Why Both Candidates Failed

**HYP-PROPOSAL-0038 (OVERFITTED):**
NMD-0002 contains exactly one odd-odd nucleus (N-14, Z=7, N=7). In most
holdout folds the c_oo coefficient is either fitted on 1 data point or
extrapolated with zero odd-odd training rows. The resulting coefficient
(c_oo ≈ 4.2 MeV on the full slice) is unreliable and produces a 1.07 MeV
regression on the `random_stratified` fold. This is a data-structure failure,
not a physics finding.

**HYP-PROPOSAL-0039 (INCONCLUSIVE):**
The Wigner energy is a real physical effect, but the post-AME2020 evaluation
surface is dominated by neutron-rich nuclides. Only 3 of 295 rows have N=Z.
The fitted Wigner coefficient (w ≈ 13.0 MeV per 1/A unit) is non-trivial on
the training surface but produces a negligible global MAE delta (+0.001 MeV)
because most rows have zero feature activation.

---

## Relation to Prior Batches

| Batch | Lane | Verdict | Candidate status |
|-------|------|---------|-----------------|
| AGENT-RUN-0005 (TASK-0170) | Initial pilot | SANDBOX_PASS | HYP-PROPOSAL-0021 sandbox-only |
| AGENT-RUN-0006 (TASK-0183) | Split-sensitivity replay | SANDBOX_PASS | HYP-PROPOSAL-0021 split-sensitive |
| AGENT-RUN-0008 (TASK-0197) | Post-AME2020 time-split | INCONCLUSIVE | HYP-PROPOSAL-0021 regresses primary |
| AGENT-RUN-0009 (TASK-0200) | Shell-aware lane | SANDBOX_PASS | HYP-PROPOSAL-0028/0029 OVERFITTED |
| AGENT-RUN-0010 (TASK-0202) | Neutron-rich lane | SANDBOX_PASS | HYP-PROPOSAL-0033/0034 OVERFITTED |
| **AGENT-RUN-0011 (TASK-0201)** | **Pairing/odd-even lane** | **SANDBOX_PASS** | **HYP-PROPOSAL-0038 OVERFITTED, 0039 INCONCLUSIVE** |

---

## Robustness Gate Outcomes

| Candidate | Gate outcome |
|-----------|-------------|
| HYP-PROPOSAL-0038 | `BLOCK_PROMOTION` |
| HYP-PROPOSAL-0039 | `ALLOW_ONLY_AS_NEGATIVE_CONTROL` |

---

## Maintainer Review Notes

- This batch closes the pairing/odd-even lane at the current NMD-0002 data
  scale. The negative results are informative: simple pairing-class indicators
  cannot produce stable residual corrections from 11 training rows.

- HYP-PROPOSAL-0039 is not ruled out physically; it is ruled out as a useful
  correction on the current neutron-rich evaluation surface. A broader dataset
  with balanced N=Z coverage would be needed to evaluate the Wigner term.

- No follow-up second batch is recommended from this lane without a
  maintainer-reviewed broader dataset.

- The batch does not change the overall campaign status. TASK-0201 accepts
  negative results as valid sandbox output per the campaign guardrails.

---

## Scope Statement

All conclusions in this review apply only to the configured sandbox scope:

- Training: NMD-0002 (11 nuclides, measured only)
- Holdout: post-AME2020 primary (295 rows, retrospective)
- Baseline: RESULT-0015 fitted semi-empirical model

No claim, canonical result, or hypothesis is promoted by this batch.
