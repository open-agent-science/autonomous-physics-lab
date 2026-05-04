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

This campaign already has narrow, reproducible progress:

- `TASK-0036` created the explicit particle-mass dataset scaffold.
- `TASK-0037` produced `EXP-0004/RUN-0004` (`RESULT-0005`), a charged-lepton
  Koide reproduction benchmark with uncertainty-aware wording.
- `TASK-0038` produced `EXP-0005/RUN-0005` (`RESULT-0006`), a historical tau
  holdout benchmark under the exact Koide assumption.
- `TASK-0039` and `TASK-0042` added search-design and numerology guardrails.
- `TASK-0040` remains `PROPOSED`, which is intentional: broader falsifier
  implementation should stay downstream of the guardrails.

Current narrow evidence:

- charged-lepton Koide reproduction observed `Q = 0.6666644634145`, close to
  `2/3` within propagated uncertainty;
- tau holdout prediction differs from the measured tau mass by about
  `3.90e-02` MeV and stays within the combined one-sigma uncertainty band;
- both results are scoped benchmark outputs, not explanatory claims.

Start here:

- [Charged-Lepton Koide Reproduction](../results/koide-charged-lepton-reproduction.md)
- [Historical Tau Holdout Prediction](../results/koide-tau-holdout.md)
- [Particle Mass Relation / Koide Track](../notes/particle-mass-relation-track.md)
- [Particle mass numerology guardrails](../notes/particle-mass-numerology-guardrails.md)

## Open Questions

- What is the smallest safe next implementation step after the current
  charged-lepton results?
- How should quark scheme/scale handling be encoded before any broader search?
- Which baseline families should every Koide-like triplet search beat before a
  result is considered interesting?
- How aggressive should the default complexity penalty be for tuned exponents,
  constants, or mixed-family constructions?
- Which verdict wording best preserves narrow scope for historical holdout
  benchmarks?

## Recommended Tasks

- `TASK-0058` — tighten scoped verdict wording for the tau holdout benchmark.
- `TASK-0059` — prepare a cautious public summary package for the tau holdout
  result after wording is disciplined.
- `TASK-0040` only after the maintainer explicitly moves it into executable
  status.
- future data or baseline tasks that preserve explicit source policy and
  overclaim guardrails.

## Recommended Contributor Types

- particle-physics data curators;
- uncertainty-propagation and statistics contributors;
- scientific safety reviewers;
- benchmark designers comfortable with null models and baselines.

## What Not To Claim

- Do not say Koide-like relations explain the origin of particle masses.
- Do not generalize charged-lepton results across all particle families.
- Do not treat one narrow holdout as evidence of deeper structure by itself.
- Do not skip source, mass-type, scheme, or scale bookkeeping.
- Do not treat fit quality alone as evidence of discovery.

## Visualization Ideas

- stage map from dataset scaffold -> reproduction -> holdout -> search ->
  falsifier;
- uncertainty-bar plot for observed `Q` versus `2/3`;
- tau predicted vs measured comparison with uncertainty bands;
- baseline-versus-relation scorecards for future search tasks;
- risk matrix showing where overclaim enters the workflow.
