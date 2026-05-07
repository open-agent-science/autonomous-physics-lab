# Negative Results Registry

Falsifications are first-class scientific outcomes in APL. This registry
catalogues every experiment that produced a clean negative result — a
hypothesis ruled out by the data rather than supported by it.

A falsification stored here is not a failure. It is reproducible evidence
that a specific claim does not hold under specific conditions. Future
contributors can build on these results without repeating work that has
already been done.

---

## Registry

| Result ID | Experiment | Hypothesis | Falsified claim | Key metric | Verdict | Date |
|-----------|-----------|-----------|-----------------|------------|---------|------|
| [RESULT-0009](../results/EXP-0007/RUN-0001/result.yaml) | EXP-0007 | HYP-0007 | Koide Q = 2/3 for neutrino masses | NH: 70.7σ gap · IH: 421,889σ gap | INVALID | 2026-05-06 |

---

## Entries

### RESULT-0009 — Koide Neutrino Consistency Test

**Hypothesis:** `HYP-0007` — The Koide relation Q = 2/3 is consistent with
neutrino mass-squared differences.

**Experiment:** `EXP-0007` / `RUN-0001`

**What was tested:** Whether the unmodified Koide formula
Q = (m₁+m₂+m₃)/(√m₁+√m₂+√m₃)² = 2/3 can be satisfied by any physically
admissible neutrino mass triplet under PDG 2024 / NuFIT 5.3 oscillation data,
for both normal hierarchy (NH) and inverted hierarchy (IH).

**Why it was falsified:**

Q is monotonically decreasing with the lightest neutrino mass. Its maximum
Q_max is achieved at m_lightest → 0. Since Q_max < 2/3 for both hierarchies,
no solution exists:

| Hierarchy | Q_max | Gap to 2/3 | Gap in σ |
|-----------|------:|------------|----------|
| NH (m₁ < m₂ < m₃) | 0.5840 | 0.0827 | **70.7σ** |
| IH (m₃ < m₁ < m₂) | 0.5000 | 0.1667 | **421,889σ** |

The IH Q_max ≈ 0.500 has an analytic explanation: when m₃ → 0 and m₁ ≈ m₂,
the formula reduces to a two-body system giving Q → 1/2 exactly.

**Scope:** Original Koide formula only. Does not rule out modified variants
(Brannen, Koide's own neutrino extension, phase-extended formulas).

**Artifacts:**
- [Public summary](results/koide-neutrino-falsification.md)
- [result.yaml](../results/EXP-0007/RUN-0001/result.yaml)
- [report.md](../results/EXP-0007/RUN-0001/report.md)
- [metrics.json](../results/EXP-0007/RUN-0001/metrics.json)

---

## How to Add an Entry

When a new experiment produces a clean negative result:

1. Add a row to the Registry table above.
2. Add a full entry section below the table.
3. Ensure `result.yaml` has `best_verdict: INVALID` or `INCONSISTENT`.
4. Link from `docs/result-artifacts-index.md` navigation guide.
5. Do not promote a falsification as a discovery-level claim.
