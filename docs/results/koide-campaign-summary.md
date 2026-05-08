# Koide Campaign Summary

## Scope

APL's Koide campaign is currently a falsification-first particle-mass track
with five canonical benchmark surfaces:

1. a charged-lepton reproduction benchmark;
2. a historical tau holdout benchmark;
3. a direct neutrino extension falsification;
4. a quark-sector cascade falsification.
5. a first falsifier MVP that applies uncertainty propagation, baseline
   calibration, and a complexity-penalty ledger to the fixed standard target.

These results share one discipline: explicit datasets, stored uncertainty or
gap metrics, and conservative verdict wording. They do not add up to a global
theory of particle masses or a blanket statement about every possible
Koide-like extension.

## Campaign Snapshot

| Surface | Canonical artifact | Outcome in scope |
| --- | --- | --- |
| Charged leptons | `EXP-0004/RUN-0004` (`RESULT-0005`) | Reproduced in scope |
| Tau holdout | `EXP-0005/RUN-0005` (`RESULT-0006`) | Reproduced in scope |
| Neutrino extension | `EXP-0007/RUN-0001` (`RESULT-0009`) | Falsified in scope |
| Quark cascade | `EXP-0008/RUN-0001` (`RESULT-0010`) | Falsified in scope |
| Falsifier MVP | `EXP-0009/RUN-0001` (`RESULT-0011`) | Cross-family survival falsified in scope |

## Reproductions in Scope

### Charged-Lepton Reproduction

- [Public result](./koide-charged-lepton-reproduction.md)
- observed `Q = 0.6666644634145`
- reference `2/3 = 0.6666666666666666`
- gap smaller than the propagated one-sigma uncertainty
- verdict: `VALID`

What this supports:

- the stored charged-lepton dataset reproduces the familiar Koide benchmark
  quantity under explicit repository assumptions.

What it does not support:

- a deeper explanation of mass generation;
- extension to other particle families;
- a claim that the relation remains strong outside this encoded benchmark.

### Historical Tau Holdout

- [Public result](./koide-tau-holdout.md)
- predicted tau mass differs from the measured value by `0.039 MeV`
- z-score `0.43σ`
- verdict: `VALID_IN_RANGE`

What this supports:

- under the stored charged-lepton Koide benchmark assumption, the historical tau holdout
  lands close to the measured tau mass for the stored PDG-backed inputs.

What it does not support:

- a global validation of Koide-like structure;
- a proof that the same behavior should survive in neutrino or quark sectors;
- a claim that historical closeness alone explains the charged-lepton spectrum.

## Falsifications in Scope

### Direct Neutrino Extension

- [Public result](./koide-neutrino-falsification.md)
- normal hierarchy maximum remains `70.7σ` below `2/3`
- inverted hierarchy maximum remains `421,889σ` below `2/3`
- verdict: `INVALID`

This is a clear falsification of the original charged-lepton Koide target
applied directly to neutrino mass eigenstates under the encoded PDG 2024 /
NuFIT 5.3 assumptions.

### Quark Cascade Follow-up

- [Public result](./koide-quark-cascade-falsification.md)
- up sector remains `159.2σ` above `2/3`
- down sector remains `8.8σ` above `2/3`
- verdict: `INVALID`

This is a clear falsification of the stored quark-sector follow-up under the
documented mixed-scale PDG dataset and the tested Brannen-style phase setup.

### Particle-Mass Relation Falsifier MVP

- [Canonical report](../../results/EXP-0009/RUN-0001/report.md)
- charged leptons remain within propagated uncertainty at `0.43σ`
- up quarks miss the fixed target by `159.2σ`
- down quarks miss the fixed target by `8.8σ`
- deterministic random-baseline and complexity-penalty details are stored in
  `metrics.json`
- verdict: `INVALID`

This falsifies cross-family survival of the fixed standard Koide target under
the encoded charged-fermion family triplets. It does not falsify every possible
Koide-like extension and does not promote any explanatory claim.

## What the Current Campaign Says

- The charged-lepton benchmark reproduces in scope.
- The historical tau holdout reproduces in scope.
- The direct neutrino extension fails in scope.
- The tested quark follow-up also fails in scope.
- The first falsifier MVP keeps the charged-lepton reproduction visible while
  recording that the fixed standard target does not survive the encoded
  charged-fermion family survey.

This makes the current campaign strongest as a reproducible benchmark and
falsification package, not as an explanatory theory package.

## What Not To Claim

- Do not say APL has explained particle masses.
- Do not say Koide is globally true or globally false.
- Do not treat one charged-lepton reproduction and one tau holdout as evidence
  for all fermion families.
- Do not treat the neutrino or quark falsifications as ruling out every
  modified Koide-like construction.
- Do not use the falsifier MVP to claim that all particle-mass numerology has
  been settled.

## Canonical Surfaces

- [Charged-Lepton Koide Reproduction](./koide-charged-lepton-reproduction.md)
- [Historical Tau Holdout Prediction](./koide-tau-holdout.md)
- [Koide Neutrino Consistency Test — Falsification Result](./koide-neutrino-falsification.md)
- [Koide Quark Cascade — Falsification Result](./koide-quark-cascade-falsification.md)
- [Particle-Mass Relation Falsifier MVP](../../results/EXP-0009/RUN-0001/report.md)
- [Negative Results Registry](../negative-results-registry.md)
