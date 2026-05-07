# Particle Mass Relations

## Goal

Turn Koide-like and other particle-mass relations into a falsification-first
benchmark track. The purpose is to test whether a relation stays meaningful
after explicit dataset provenance, uncertainty propagation, holdout checks,
baseline comparisons, and complexity penalties are applied.

## Why It Matters

Particle-mass numerology is exactly the kind of domain where APL's discipline
matters most:

- numerical closeness can be impressive but misleading;
- cherry-picked triplets can look profound without surviving baseline checks;
- scheme and scale choices can change the story materially;
- holdout tests are more informative than retrospective fits.

If APL can stay honest here, its broader verification posture becomes much more
credible.

## Current Results

This campaign now has a coherent set of narrow, reproducible benchmark
surfaces:

- `TASK-0036` created the explicit particle-mass dataset scaffold.
- `TASK-0037` produced `EXP-0004/RUN-0004` (`RESULT-0005`), a charged-lepton
  Koide reproduction benchmark with uncertainty-aware wording.
- `TASK-0038` produced `EXP-0005/RUN-0005` (`RESULT-0006`), a historical tau
  holdout benchmark under the stored charged-lepton Koide assumption.
- `TASK-0093` produced `EXP-0007/RUN-0001` (`RESULT-0009`), a direct neutrino
  extension falsification under PDG 2024 / NuFIT 5.3 inputs.
- `TASK-0088` produced `EXP-0008/RUN-0001` (`RESULT-0010`), a quark-sector
  cascade falsification under the documented mixed-scale PDG dataset.
- `TASK-0039` and `TASK-0042` added search-design and numerology guardrails.
- `TASK-0040` remains `PROPOSED`, which is intentional: broader falsifier
  implementation should stay downstream of the guardrails.

Current narrow evidence:

- charged-lepton Koide reproduction observed `Q = 0.6666644634145`, close to
  `2/3` within propagated uncertainty;
- tau holdout prediction differs from the measured tau mass by about
  `3.90e-02` MeV and stays within the combined one-sigma uncertainty band;
- neutrino follow-up testing keeps `Q_max` below `2/3` for both known
  orderings in the stored setup;
- quark follow-up testing keeps both tested sectors above `2/3` in the stored
  setup;
- these are scoped benchmark and falsification outputs, not explanatory claims.

Start here:

- [Koide Campaign Summary](../results/koide-campaign-summary.md)
- [Charged-Lepton Koide Reproduction](../results/koide-charged-lepton-reproduction.md)
- [Historical Tau Holdout Prediction](../results/koide-tau-holdout.md)
- [Koide Neutrino Falsification](../results/koide-neutrino-falsification.md)
- [Koide Quark Cascade Falsification](../results/koide-quark-cascade-falsification.md)
- [Negative Results Registry](../negative-results-registry.md)
- [Particle Mass Relation / Koide Track](../notes/particle-mass-relation-track.md)
- [Particle mass numerology guardrails](../notes/particle-mass-numerology-guardrails.md)

## Open Questions

- What is the smallest safe next implementation step after the current
  charged-lepton, tau, neutrino, and quark result package?
- How should quark scheme/scale handling be encoded before any broader search?
- Which baseline families should every Koide-like triplet search beat before a
  result is considered interesting?
- How aggressive should the default complexity penalty be for tuned exponents,
  constants, or mixed-family constructions?
- Which verdict wording best preserves narrow scope for historical holdout
  benchmarks?

## Recommended Tasks

- packaging and wording work that keeps the current campaign legible without
  promoting claims;
- future data or baseline tasks that preserve explicit source policy and
  overclaim guardrails;
- `TASK-0040` only after the maintainer explicitly moves it into executable
  status.

## Recommended Contributor Types

- particle-physics data curators;
- uncertainty-propagation and statistics contributors;
- scientific safety reviewers;
- benchmark designers comfortable with null models and baselines.

## What Not To Claim

- Do not say Koide-like relations explain the origin of particle masses.
- Do not generalize charged-lepton results across all particle families.
- Do not treat one narrow holdout as evidence of deeper structure by itself.
- Do not turn neutrino or quark falsifications into a blanket statement about
  every possible Koide-like variant.
- Do not skip source, mass-type, scheme, or scale bookkeeping.
- Do not treat fit quality alone as evidence of discovery.

## Visualization Ideas

- stage map from dataset scaffold -> reproduction -> holdout -> search ->
  falsifier;
- uncertainty-bar plot for observed `Q` versus `2/3`;
- tau predicted vs measured comparison with uncertainty bands;
- baseline-versus-relation scorecards for future search tasks;
- risk matrix showing where overclaim enters the workflow.
