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
| [RESULT-0010](../results/EXP-0008/RUN-0001/result.yaml) | EXP-0008 | HYP-0008 | Tested quark-sector Koide cascade reaches Q = 2/3 | Down: 8.8σ gap · Up: 159.2σ gap | INVALID | 2026-05-06 |
| [RESULT-0011](../results/EXP-0009/RUN-0001/result.yaml) | EXP-0009 | HYP-0009 | Standard Koide Q = 2/3 survives encoded charged-fermion family survey | Down: 8.8σ gap · Up: 159.2σ gap | INVALID | 2026-05-08 |

---

## Scope-Memory Entries

Scope-memory entries preserve a verified boundary on an existing result without
creating a new result or changing the existing result's verdict or metrics.

| Evidence | Dataset | Scope boundary | Key metrics | Classification |
|----------|---------|----------------|-------------|----------------|
| [TASK-0789 preflight](reviews/materials-md0002-family-holdout-stress-preflight.md) | MD-0002 stable ternary oxides | The cation-pair-mean baseline is useful when cation-pair families are represented in training, but does not establish transfer to fully unseen pairs. | Standard frozen split MAE: 0.201; unseen-pair holdout MAE: 0.637 vs null 0.654 eV/atom | Negative / scope memory |

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

### RESULT-0010 — Koide Quark Cascade Follow-up

**Hypothesis:** `HYP-0008` — A Brannen-style quark-sector follow-up can reach
the charged-lepton Koide target `Q = 2/3`.

**Experiment:** `EXP-0008` / `RUN-0001`

**What was tested:** Whether up-type and down-type quark triplets can satisfy
the charged-lepton Koide target under the stored PDG 2024 mixed-scale dataset
and the tested phase-family setup.

**Why it was falsified:**

For the tested parameterization, `Q` is minimized at the standard real-valued
case, so `Q_min = Q_std`. Both quark sectors still remain above `2/3`:

| Sector | `Q_min` | Gap to `2/3` | Gap in `σ` |
|--------|--------:|-------------:|-----------:|
| Up (`u,c,t`) | 0.848981 | 0.182314 | **159.2σ** |
| Down (`d,s,b`) | 0.731497 | 0.064830 | **8.8σ** |

No tested phase rotation reaches the charged-lepton target for either sector.

**Scope:** Mixed-scale PDG quark masses and one tested Brannen-style
phase-family only. Does not rule out every alternative quark-sector
construction or common-scale reformulation.

**Artifacts:**
- [Public summary](results/koide-quark-cascade-falsification.md)
- [result.yaml](../results/EXP-0008/RUN-0001/result.yaml)
- [report.md](../results/EXP-0008/RUN-0001/report.md)
- [metrics.json](../results/EXP-0008/RUN-0001/metrics.json)

---

### RESULT-0011 — Particle-Mass Relation Falsifier MVP

**Hypothesis:** `HYP-0009` — The standard Koide target `Q = 2/3` survives
guardrail-compliant charged fermion family tests.

**Experiment:** `EXP-0009` / `RUN-0001`

**What was tested:** Whether the fixed standard Koide relation remains valid
across the encoded within-family charged-fermion triplets: charged leptons,
up-type quarks, and down-type quarks. The MVP adds source-explicit inputs,
first-order uncertainty propagation, deterministic log-uniform random-baseline
calibration, and a fixed low complexity-penalty ledger.

**Why it was falsified:**

Charged leptons remain within propagated uncertainty, but both encoded quark
families miss the fixed target outside propagated uncertainty:

| Family | `Q` | Gap to `2/3` | Gap in `σ` |
|--------|----:|-------------:|-----------:|
| Charged leptons (`e,mu,tau`) | 0.666664 | 0.000002 | **0.43σ** |
| Up quarks (`u,c,t`) | 0.848981 | 0.182314 | **159.2σ** |
| Down quarks (`d,s,b`) | 0.731497 | 0.064830 | **8.8σ** |

**Scope:** Fixed standard Koide relation only, encoded charged-fermion family
triplets only, and stored PDG-backed quark inputs with their documented mixed
scheme/scale limitations. Does not rule out every modified Koide-like
construction, common-scale quark reformulation, or exploratory relation family.

**Artifacts:**
- [report.md](../results/EXP-0009/RUN-0001/report.md)
- [result.yaml](../results/EXP-0009/RUN-0001/result.yaml)
- [metrics.json](../results/EXP-0009/RUN-0001/metrics.json)

---

### MD-0002 Cation-Pair Family-Holdout Scope Boundary

**Existing result:** [RESULT-0021](../results/EXP-0014/RUN-0001/result.yaml),
the scope-limited MD-0002 formation-energy cation-pair baseline.

**Boundary evidence:** [TASK-0789 family-holdout
preflight](reviews/materials-md0002-family-holdout-stress-preflight.md).
This was a deterministic preflight over committed rows, not a new metric run.

**What the existing evidence establishes:** On the standard frozen split, the
cation-pair-mean baseline has holdout MAE `0.200606` eV/atom (`0.201` rounded).
This is useful within the frozen MD-0002 slice when cation-pair families are
represented in training.

**What does not transfer:** On a disjoint holdout of 27 fully unseen
cation-pair families (119 rows), every pair misses the lookup table, so the
baseline falls back to the global train mean. Its MAE is `0.636977` eV/atom
(`0.637` rounded), versus `0.653596` eV/atom (`0.654` rounded) for the
global-median null. The comparison does not establish model-specific
out-of-family transfer; the standard-split advantage is bounded to known
cation-pair membership rather than extrapolation to unseen keys.

**Scope:** Computed-DFT formation energies for the committed MD-0002 stable
ternary-oxide slice only. This is negative/scope memory for a lookup baseline,
not a materials-discovery, design, synthesis, device, experimental-validation,
or universal-law statement. It does not evaluate a transfer-capable descriptor
model.

**Output routing:** Destination is this negative/scope-memory registry. No
`RESULT-*`, `PRED-*`, `CLAIM-*`, `KNOW-*`, source-row, holdout, or golden-result
artifact is created or modified. Overclaim risk is controlled by the
computed-DFT, slice-limited, lookup-baseline wording. Promotion blocker: none;
this is memory-only packaging of existing evidence.

---

## How to Add an Entry

When a new experiment produces a clean negative result:

1. Add a row to the Registry table above.
2. Add a full entry section below the table.
3. Ensure `result.yaml` has `best_verdict: INVALID` or `INCONSISTENT`.
4. Link from `docs/result-artifacts-index.md` navigation guide.
5. Do not promote a falsification as a discovery-level claim.
