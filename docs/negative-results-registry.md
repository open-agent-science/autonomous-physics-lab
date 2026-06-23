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
| [RESULT-0017](../results/EXP-0001/RUN-0006/result.yaml) | EXP-0001 pendulum gauntlet | The 101-candidate gauntlet overfit result is reproducible negative boundary evidence; it does not contradict the narrowed range-limited `CLAIM-0001` positive support. | Best gauntlet candidate test max relative error 0.021261; Gate B replay drift 6.89e-13 over 878 metrics | AGENT_VALIDATED overfit memory |
| [RESULT-0018 and Nuclear exhausted-lane capsule](../results/EXP-0012/RUN-0002/result.yaml) | NMD-0003 retrospective measured-row surface and related Nuclear audits | F2 is reproducible but does not clear its controls-first survival margin; shell-axis remains diagnostic-only; local-curvature fails the no-leakage gate; neutron-rich behavior does not transfer specifically beyond matched high-error controls. | F2 margin 0.199260 vs required 0.250000 MeV; local-curvature full-known delta MAE +0.0196 MeV and 0/19 subset wins | Validated negative / diagnostic memory |

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

### Pendulum RESULT-0017 Overfit Boundary Memory

**Existing validated result:** [RESULT-0017](../results/EXP-0001/RUN-0006/result.yaml),
the `AGENT_VALIDATED`, `OVERFITTED` pendulum gauntlet negative/overfit result.

**What the evidence preserves:** The 101-candidate gauntlet can find fitted
models with very low train error, but the best negative-memory candidate
(`model_t2_x4_l2`) still fails the configured verification package:
small-angle window accuracy, large-angle window accuracy, separatrix
asymptotic alignment, dimensional consistency, and known small-angle coefficient
checks are non-passing. Its configured test max relative error is `0.021261`,
and the verdict remains `OVERFITTED`.

**Gate B replay:** [TASK-0757](reviews/result-0017-pendulum-gate-b-replay.md)
replayed the committed command and preserved the `OVERFITTED` verdict. The
replay compared 878 numeric metrics with maximum absolute drift
`6.892264536872972e-13` under tolerance `1.0e-09`.

**Relationship to `CLAIM-0001`:** This negative memory does not contradict
the maintainer-reviewed `CLAIM-0001` range-limited positive support.
`CLAIM-0001` cites verification-passing positive results (`RESULT-0001`,
`RESULT-0003`, and `RESULT-0013`) and explicitly says the tested approximation
is not exact, not valid at the separatrix, and not applicable to non-ideal
pendulums. `RESULT-0017` is kept out of that positive evidence map because its
verification gate fails; it is boundary evidence about what not to repeat.

**Do-not-repeat boundary:** do not rerun broad pendulum formula search on the
same configured gauntlet as if it were a fresh positive discovery lane. Future
pendulum work should predeclare a materially different approximation family,
symbolic registry check, range boundary, or separatrix diagnostic target.

**Scope:** Ideal mathematical pendulum only. No damping, driving, finite-size,
elastic, laboratory, exactness, all-amplitude, separatrix-validity, symbolic
proof, or new-physics statement is supported.

**Output routing:** destination is this negative-results registry and the
Pendulum campaign page. No `RESULT-*`, `PRED-*`, `CLAIM-*`, `KNOW-*`, or
golden-result artifact is created or modified. RESULT-0017 remains
`AGENT_VALIDATED` / `OVERFITTED`; no new Gate A or Gate B is attempted.

---

### Nuclear Validated Negative-Memory Capsule

**Existing validated result:** [RESULT-0018](../results/EXP-0012/RUN-0002/result.yaml),
the `AGENT_VALIDATED`, `INCONCLUSIVE` F2 component-ablation diagnostic.

**What the evidence rules out under the current contracts:**

- **F2 component ablation:** the independent Gate B replay reproduced the
  result, but the full-reference advantage over the best control is
  `0.199260 MeV`, below the predeclared `0.250000 MeV` survival margin. No
  component variant cleared the margin, so another run of the same F2
  taxonomy, split, baseline, and controls is not a new scientific lane.
- **Shell-axis expansion:** the completed audit wave found fragile
  coefficients, persistent light-`A<50` regression, mixed isotope-chain
  transfer, and non-specific neutron-rich tail behavior. The lane remains
  `DIAGNOSTIC_ONLY`; further retrospective slicing is not recommended.
- **Local curvature:** `LOCAL-CURVATURE-001` became worse than the
  no-correction baseline under the bounded no-leakage implementation
  (`+0.0196 MeV` full-known delta MAE), lost to the strongest control, and won
  `0 of 19` subset comparisons. The earlier leakage-permissive positive
  framing must not be revived.
- **Neutron-rich transfer:** matched non-neutron-rich high-error controls also
  improve, sometimes more strongly, and isotope-chain transfer is mixed. This
  does not support a neutron-rich-specific correction or a broad transfer
  statement.

**Do-not-repeat boundary:** do not reopen these families on the same committed
rows, splits, baselines, labels, and controls. A later task needs a materially
different, maintainer-approved source or baseline contract and must predeclare
its controls before scoring.

**Prospective reveal blocker:** reveal scoring remains source-blocked because
no admissible measurement source postdating the `2026-05-20` freeze has been
pinned through the no-peek source gate. Re-scouting the same source surface is
not a recommended execution lane; future work waits for a genuinely new
source/version signal.

**Scope:** This capsule preserves negative and diagnostic campaign memory. It
does not modify RESULT-0018, any `PRED-*` entry, `results/golden-results.yaml`,
claims, or knowledge artifacts, and it does not establish or falsify a
universal nuclear mass law.

**Evidence trail:**

- [RESULT-0018 diagnostic memory and next-lane decision](reviews/nuclear-result0018-diagnostic-negative-memory-and-next-lane.md)
- [Shell-axis post-audit decision](reviews/nuclear-shell-axis-post-audit-decision.md)
- [Local-curvature promotion preflight](reviews/nuclear-local-curvature-result-promotion-preflight.md)
- [Neutron-rich boundary-transfer lane](reviews/nuclear-neutron-rich-boundary-transfer-hypothesis-lane.md)
- [Reveal-source manifest preflight](reviews/nuclear-reveal-source-manifest-preflight.md)

**Output routing:** destination is this negative-memory registry and the
Nuclear campaign page. RESULT/PRED/CLAIM/KNOW artifacts are unchanged.
RESULT-0018 retains `AGENT_VALIDATED` / `INCONCLUSIVE`; no new Gate A or Gate B
is attempted. The active blocker is an admissible post-freeze reveal source.

---

## How to Add an Entry

When a new experiment produces a clean negative result:

1. Add a row to the Registry table above.
2. Add a full entry section below the table.
3. Ensure `result.yaml` has `best_verdict: INVALID` or `INCONSISTENT`.
4. Link from `docs/result-artifacts-index.md` navigation guide.
5. Do not promote a falsification as a discovery-level claim.
