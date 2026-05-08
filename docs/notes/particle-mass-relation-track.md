# Particle Mass Relation / Koide Track

Task: `TASK-0013`  
Type: `benchmark_planning`  
Domain: particle physics  
Status: active campaign — see experiment results below

**Completed experiments:** EXP-0004 (VALID), EXP-0005 (VALID), EXP-0007 (INVALID), EXP-0008 (INVALID), EXP-0009 (INVALID)
**Baseline design:** `docs/notes/koide-baseline-planning.md` (TASK-0082)

---

## Purpose

This document defines a falsification-first APL task track around Koide-like
particle mass relations.

The track is interesting because the charged-lepton Koide relation is:

- compact and historically notable;
- numerically precise for charged lepton pole masses;
- strong enough to support a real holdout-style benchmark story;
- risky enough that APL must guard against numerology and post hoc fitting.

APL should treat this direction as a benchmark for distinguishing signal from
coincidence, not as a shortcut to "solving particle masses."

---

## What APL Can Test

APL can test whether a proposed particle-mass relation:

- reproduces a known in-family relation under explicit assumptions;
- survives uncertainty propagation;
- makes a usable holdout prediction;
- outperforms random or weakly structured baselines;
- remains competitive after a formula-complexity penalty;
- stays meaningful when mass definitions, schemes, and scales are made explicit.

This makes the direction a good fit for APL's verification-first mission.

---

## What APL Must Not Claim

APL must not claim that a good fit:

- explains the origin of particle masses;
- establishes new physics;
- generalizes across all particle families;
- survives scale or scheme changes without testing;
- is meaningful if it only appears after cherry-picking triplets or constants.

No claim promotion should happen automatically, and no benchmark result should
be framed as a discovery from fitting alone.

---

## Why Baselines And Penalties Are Required

Particle-mass numerology is an unusually high-risk domain for false positives.

The track therefore requires:

- random baselines for triplet search and relation search tasks;
- holdout validation for prediction-style tasks;
- uncertainty propagation wherever mass inputs have measurement uncertainty;
- explicit data-source recording for every mass value;
- explicit mass-type recording such as `pole` or `running`;
- formula-complexity penalties for parameters, constants, tuned exponents,
  family mixing, and flexible functional forms.

The goal is not to find a pretty equation. The goal is to test whether a
relation retains value after the usual numerology loopholes are closed.

---

## Data-Source Policy

Primary particle-mass data should come from explicit, versioned PDG-backed
sources or an equally explicit maintainer-approved source.

Every dataset or benchmark artifact in this track should record:

- particle name;
- family;
- mass value;
- mass unit;
- uncertainty;
- source citation;
- mass type;
- scheme and scale when applicable;
- notes about interpretation limits.

APL should not mix incompatible mass definitions silently.

---

## Family-Specific Cautions

### Charged leptons

Charged leptons are the best first benchmark target because their pole masses
are well defined and precise enough for high-quality uncertainty-aware checks.

### Quarks

Quark masses need special care because running masses depend on the chosen
renormalization scheme and scale. A relation that looks strong under one
definition may weaken or disappear under another. Quark tasks must therefore
record scheme and scale explicitly.

### Neutrinos

Absolute neutrino masses are not fully known, so neutrino benchmarks must work
through scenario analysis, bounds, or explicitly stated assumptions rather than
pretending to have complete ground-truth inputs.

### Composite particles

Baryons and mesons are much riskier exploratory territory because binding
effects dominate naive constituent-mass narratives. If explored later, they
should be isolated as high-risk exploratory tasks rather than mixed into the
core benchmark by default.

---

## Staged Roadmap

### Stage 1 — Dataset Scaffold

Create a particle-mass dataset scaffold with explicit field definitions and
source policy, but no formula claims.

### Stage 2 — Charged-Lepton Reproduction

Reproduce the charged-lepton Koide quantity

`Q = (m_e + m_mu + m_tau) / (sqrt(m_e) + sqrt(m_mu) + sqrt(m_tau))^2`

and report how closely it matches `2/3` under explicit uncertainty handling.

### Stage 3 — Historical Tau Holdout

Use `m_e`, `m_mu`, and the exact Koide assumption to solve for `m_tau`, then
compare the predicted tau mass against the measured value as a benchmarked
holdout test.

### Stage 4 — Koide-Like Triplet Search Design

Define which particle-family combinations are allowed, which are forbidden by
default, and how random baselines, uncertainty propagation, and overfit checks
must work before search is implemented.

### Stage 5 — Falsifier MVP

Only after the above planning and guardrails are in place should APL implement
the first particle-mass relation falsifier workflow.

### Stage 6 — Full Family Survey (completed)

EXP-0007 tested neutrinos; EXP-0008 tested up and down quarks. Together with
EXP-0004 and EXP-0005 for charged leptons, this completes a full survey of all
SM fundamental fermion families under the standard Koide formula.

Result: Q = 2/3 is specific to charged leptons. All other families miss by
at least 8.8σ under PDG 2024 masses.

### Stage 7 — Baseline Calibration and Falsifier MVP (completed)

Define and implement random and enumeration baselines so that the charged-lepton
result can be put in statistical context. See `docs/notes/koide-baseline-planning.md`.
`EXP-0009/RUN-0001` implements the first fixed-target falsifier MVP with
uncertainty propagation, deterministic log-uniform random-baseline calibration,
and a fixed low complexity-penalty ledger.

---

## Task Track

The repository already uses `TASK-0035` for maintainer-review refactoring, so
this Koide / particle-mass track starts at the next available ids:

- `TASK-0036` — particle mass dataset scaffold *(done)*
- `TASK-0037` — reproduce Koide charged-lepton relation *(done, EXP-0004)*
- `TASK-0038` — historical tau holdout prediction *(done, EXP-0005)*
- `TASK-0039` — Koide-like triplet search design *(done)*
- `TASK-0040` — particle mass relation falsifier MVP *(review ready, EXP-0009)*
- `TASK-0041` — mass-formula complexity penalty design *(done)*
- `TASK-0042` — numerology guardrails for particle mass relations *(done)*
- `TASK-0082` — Koide baseline planning *(this note)*
- `TASK-0088` — quark Koide cascade (EXP-0008) *(done, INVALID)*

After `TASK-0040`, broader search should remain gated on review of `RESULT-0011`
and should not expand into cross-family or tuned-formula search without explicit
search accounting.

---

## Non-Goals For This Planning Task

- Do not implement the benchmark yet.
- Do not assign a final experiment id yet.
- Do not create result artifacts yet.
- Do not add scientific claims.
- Do not promote claims.
- Do not use discovery language such as "solved particle masses."
