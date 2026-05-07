# Hypothesis Register Pilot — 01

**Task:** `TASK-0081`
**Date:** 2026-05-06
**Status:** COMPLETE

---

## Purpose

This document records the first pilot of the hypothesis register workflow.
The goal is to show how an HRE entry moves from `PROPOSED` to one of four
outcomes: `FORMALIZED` (ready for experiment planning), `PROMOTED` (experiment
assigned), deferral (needs more data or theory), or `REJECTED` (duplicate or
falsified).

This pilot does not run benchmarks. It produces one concrete next-step
artifact and identifies the right path for each of the five seed entries.

---

## Assessment of Seed Entries

### HRE-0001 — Koide-like mass relation for neutrinos

**Domain:** particle_physics  
**Form:** (√m₁ + √m₂ + √m₃)² / (m₁ + m₂ + m₃) = 3/2 (equivalent to Q = 2/3)

**Assessment: CLOSE — already tested by EXP-0007.**

EXP-0007 / RUN-0001 (RESULT-0009) directly tested whether Q = 2/3 holds for
any physically admissible neutrino mass triplet under PDG 2024 / NuFIT 5.3
data. The result was a clean falsification: NH gap 70.7σ, IH gap 421,889σ.

The HRE-0001 mathematical form `(√m₁+√m₂+√m₃)² / (m₁+m₂+m₃) = 3/2` is
algebraically equivalent to Q = 2/3. The entry is therefore covered by the
existing experiment. Recommended action: update status to `REJECTED` with
a reference to RESULT-0009.

**Next step:** Mark REJECTED, reference EXP-0007.

---

### HRE-0002 — Leading-order period correction for weakly anharmonic oscillator

**Domain:** classical_mechanics  
**Form:** T(A) ≈ T₀ · (1 + (3λ/4k²) · A²)

**Assessment: SELECTED FOR PILOT.**

This entry is the strongest candidate for formalization in the current set:

- Deterministically testable with existing APL simulation infrastructure.
- Clear falsification boundary: error > 1% for λA²/k < 0.1.
- Connects directly to the pendulum campaign (EXP-0001/RUN-0002 near-separatrix
  work), which already has a working ODE engine.
- Does not require particle-mass data or uncertain experimental inputs.
- Perturbative regime is explicit in the assumptions; no overclaim risk.

A draft experiment plan is attached as the next-step artifact (see below).

**Next step:** Move to `FORMALIZED`. Create draft experiment plan.

---

### HRE-0003 — Wien displacement generalisation for modified Planck spectrum

**Domain:** thermodynamics  
**Form:** λ_max · T = hc / (k_B · W(n)) where W(n) solves n = x / (1 − e^{−x})

**Assessment: FORMALIZE-READY (deferred pending campaign capacity).**

The entry is well-scoped and deterministically testable via numerical
optimization. The falsification test is clear. However, the thermodynamics
domain has no active campaign in APL and no existing workflow engine for
spectral calculations. Formalizing now would produce a draft with no near-term
execution path.

Recommended action: leave at `PROPOSED`. Revisit when a thermodynamics or
constants-verification campaign is activated.

**Next step:** Defer. No action this pilot.

---

### HRE-0004 — Relativistic KE correction threshold at β > 0.115

**Domain:** special_relativity  
**Form:** |KE_rel − KE_newt| / KE_rel > 0.01 for β > 0.115

**Assessment: FORMALIZE-READY (pedagogical, low priority).**

The threshold β ≈ 0.115 is derivable analytically from the Taylor expansion
of γ. The numerical verification is a one-function Python script. The entry
is correct and cleanly scoped, but serves a pedagogical rather than scientific
purpose — it confirms a known textbook result, not a novel pattern.

Recommended action: suitable for a `FORMALIZED → PROMOTED` path within the
approximation-breakdown-probes microtask track (TASK-0050), but lower priority
than HRE-0002.

**Next step:** Defer to microtask track. No full pilot needed.

---

### HRE-0005 — Fine-structure constant derivable from CODATA constants to 1e-9

**Domain:** fundamental_constants  
**Form:** α = e² / (4πε₀ħc)

**Assessment: FORMALIZE-READY (verification exercise, definitionally true).**

This entry tests CODATA consistency rather than a physical hypothesis. It is
definitionally true given a self-consistent set of CODATA values, so it cannot
be falsified in a scientifically interesting way. It is useful as a
worked-example in the physical-constants verification track (TASK-0049).

Recommended action: suitable as a quick verification example within TASK-0049.
Not the right entry for a full pilot of the hypothesis lifecycle, because
there is no genuine uncertainty to test.

**Next step:** Defer to TASK-0049 microtask queue. No full pilot needed.

---

## Pilot Selection: HRE-0002

HRE-0002 (anharmonic oscillator period correction) is chosen for the pilot
because:

1. It is falsifiable — the 1% error threshold at λA²/k < 0.1 is a concrete
   failure criterion, not an identity.
2. It extends an existing campaign — the pendulum ODE infrastructure already
   exists in `physics_lab/engines/`.
3. It demonstrates the key workflow step — `PROPOSED → FORMALIZED → experiment
   plan` — without requiring new data sources.
4. It avoids overclaim risk — the perturbative assumption is explicit and
   the claim ceiling is conservative.

---

## Next-Step Artifact

See [anharmonic-period-experiment-plan.md](../drafts/anharmonic-period-experiment-plan.md)
for the draft experiment plan for HRE-0002.

This draft is not a canonical `EXP-XXXX` file. It must be reviewed and
accepted by a maintainer before a task is opened to run the experiment.

---

## Workflow Gap Identified

No gap was found in the protocol document itself. One observation:

The protocol allows any agent to move `PROPOSED → FORMALIZED` but does not
specify what artifact must accompany that transition. This pilot treats a
draft experiment plan as the required artifact. Future contributors should
use the same pattern: a `FORMALIZED` entry without a linked plan draft should
be considered incomplete.

---

## Actions Taken

| Entry | Old Status | New Status | Rationale |
|-------|-----------|-----------|-----------|
| HRE-0001 | PROPOSED | REJECTED | Covered by EXP-0007 / RESULT-0009 |
| HRE-0002 | PROPOSED | FORMALIZED | Selected for pilot; draft plan attached |
| HRE-0003 | PROPOSED | PROPOSED | Deferred — no active campaign |
| HRE-0004 | PROPOSED | PROPOSED | Deferred — pedagogical, low priority |
| HRE-0005 | PROPOSED | PROPOSED | Deferred — definitionally true, use TASK-0049 queue |
