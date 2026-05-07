# Koide Quark Cascade — Falsification Result

## Scope

`TASK-0088` extends the Koide campaign into a quark-sector follow-up using the
stored PDG 2024 quark-mass dataset and a Brannen-style phase extension test.

This result is narrow:

- up-type and down-type quark triplets only;
- mixed-scale PDG-backed quark masses as stored in the repository;
- one tested phase-family setup plus the standard `Q = 2/3` target;
- no renormalization-group running to a common comparison scale.

## Canonical Result

- Result: `RESULT-0010`
- Run: `RUN-0001`
- Experiment: `EXP-0008`
- Hypothesis: `HYP-0008`
- Overall verdict: `INVALID`

## Primary Outcome

| Sector | Tested quantity | Observed value | Gap to `2/3` | Gap in `σ` | Reaches `2/3`? |
| --- | --- | ---: | ---: | ---: | --- |
| Up (`u,c,t`) | `Q_std = Q_min` | `0.848981` | `+0.182314` | `159.2σ` | No |
| Down (`d,s,b`) | `Q_std = Q_min` | `0.731497` | `+0.064830` | `8.8σ` | No |

Under the tested parameterization, the phase scan cannot lower either sector to
the charged-lepton target.

## Why It Fails in Scope

For the tested phase family,

`Q(δ) = (Σm) / |√m₁ + √m₂·e^{iδ} + √m₃·e^{2iδ}|²`

the denominator is maximized at `δ = 0`. That means `Q` is minimized at the
standard real-valued formula, so `Q_min = Q_std`.

Since both quark sectors already satisfy `Q_std > 2/3`, the phase scan cannot
reach the charged-lepton target under this setup.

## Relation to the Rest of the Koide Campaign

| Surface | Outcome in scope |
| --- | --- |
| Charged leptons (`EXP-0004`) | Reproduced in scope |
| Tau holdout (`EXP-0005`) | Reproduced in scope |
| Neutrino extension (`EXP-0007`) | Falsified in scope, `Q_max < 2/3` |
| Quark cascade (`EXP-0008`) | Falsified in scope, `Q_min > 2/3` |

The neutrino and quark follow-ups fail on opposite sides of the charged-lepton
target, which is useful as campaign evidence but still does not justify a
global statement about every possible Koide-like extension.

## What This Does and Does Not Mean

What it means:

- the stored quark-sector follow-up does not reproduce the charged-lepton
  Koide target under the encoded dataset and phase assumptions;
- both up-type and down-type sectors remain outside `2/3` by clear margins.

What it does not mean:

- it does not rule out all alternative quark-sector constructions;
- it does not settle scale-unification questions for quark masses;
- it does not justify a claim that only charged leptons can ever satisfy a
  Koide-like relation under some other definition.

## Limitations

- Quark masses are used at mixed renormalization scales, exactly as documented
  in the canonical run artifacts.
- No RGE running is applied to place all quark masses on one common scale.
- Only one class of phase-modified formulas is tested.
- Brannen equal-spacing `Q_B` is discussed for context but is a distinct
  quantity from the phase-scan target.

## Canonical Artifacts

- [Campaign summary](./koide-campaign-summary.md)
- [result.yaml](../../results/EXP-0008/RUN-0001/result.yaml)
- [report.md](../../results/EXP-0008/RUN-0001/report.md)
- [metrics.json](../../results/EXP-0008/RUN-0001/metrics.json)
- [review_summary.md](../../results/EXP-0008/RUN-0001/review_summary.md)
- [review_metadata.yaml](../../results/EXP-0008/RUN-0001/review_metadata.yaml)
- [Negative Results Registry](../negative-results-registry.md)
