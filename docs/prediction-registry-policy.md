# Prediction Registry Policy

> See also [`result-promotion-protocol.md`](./result-promotion-protocol.md)
> for the master multi-class output protocol. The generic
> `prediction.schema.json` introduced there allows the registry to extend
> beyond nuclear masses to any domain that needs a pre-registration lane.
> This policy remains authoritative for registry layout and the no-peek
> freeze rules.

## Purpose

This policy defines the repository-native rules for storing **prospective**
nuclear-mass predictions.

The registry is the place for forecasts that are frozen before later
measurements are reviewed. Its job is to preserve a visible before/after
boundary without confusing that boundary with claim promotion.

## What The Registry Is For

Use the prediction registry when a contributor or agent wants to record:

- a future nuclear-mass forecast for named target nuclides;
- the frozen model state used to make that forecast;
- the exact prediction values and their uncertainty semantics;
- the later reveal conditions under which the forecast may be compared.

The registry is appropriate only for **before-measurement** predictions.

## What The Registry Is Not For

The registry must not be used to:

- store retrospective time-split benchmarks as if they were blind prediction;
- promote claims before later reviewed comparison;
- rewrite canonical `results/`, `claims/`, or `knowledge/`;
- pull live external measurements during registration;
- treat a registered forecast as evidence of discovery.

Retrospective post-AME2020 evaluation remains a separate evidence class:

- useful;
- reviewable;
- stronger than unrestricted post hoc fitting;
- but still not the same thing as a prediction registered before later
  measurements are known.

## Entry Layout

Registry entries live under:

```text
prediction_registry/nuclear_masses/PRED-XXXX.yaml
```

Each entry must include:

1. **Identity**
   - prediction id;
   - title;
   - campaign profile id;
   - task id;
   - registry status.
2. **Timestamp and ownership**
   - `registered_at_utc`;
   - contributor id;
   - agent id or human execution mode.
3. **Frozen source state**
   - git commit;
   - model reference;
   - baseline reference;
   - training/source dataset references;
   - holdout/prediction protocol references;
   - explicit `live_external_fetch_allowed: false`.
4. **Target set**
   - named nuclide list;
   - `Z`, `N`, `A`;
   - predicted value;
   - unit semantics.
5. **Uncertainty semantics**
   - whether the entry contains a point estimate only, numeric uncertainty,
     interval-like bound, or heuristic confidence note.
6. **Reveal conditions**
   - what later reviewed source or dataset allows comparison;
   - who controls reveal;
   - explicit no-peek rule.
7. **Limitations and review boundary**
   - pre-reveal no-claim wording;
   - post-reveal maintainer-review requirement.

## Required Status And Wording

For now, a newly registered prediction should use:

- `registry_status: REGISTERED`
- `evidence_class: prospective_prediction_registry`

Required wording boundary:

- no claim promotion before later comparison;
- no canonical result before later comparison;
- no "proved", "confirmed", "breakthrough", or equivalent language;
- no wording that calls a retrospective time-split benchmark a blind
  prediction.

## Reveal Rule

A later measurement comparison is a **separate reviewed step**.

For nuclear-mass prediction entries, the operational checklist for that step is
defined in
[Nuclear Prediction Reveal Protocol](./nuclear-prediction-reveal-protocol.md).

That later step must:

- reference the original `PRED-XXXX` entry unchanged;
- cite the reviewed measured-data source;
- record whether the target list or frozen model changed after registration
  (the answer should be no; if not, the deviation must stay visible);
- keep comparison wording range-aware and limitation-aware.

Registration alone does not create a result package.

## Current Nuclear-Mass Campaign Rule

For the nuclear-mass surface campaign:

- retrospective post-AME2020 evaluation remains governed by
  `docs/nuclear-mass-holdout-protocol.md` and the robustness gate;
- prospective predictions belong only in
  `prediction_registry/nuclear_masses/`;
- `TASK-0205` may create first entries only after this policy exists and a
  maintainer chooses the frozen model and target list.

## Validation

Registry entries should validate against:

- `physics_lab/schemas/nuclear_mass_prediction.schema.json`
- repository validation via `python3 -m physics_lab.cli validate-repo .`

The template file is guidance. Individual `PRED-*.yaml` entries are the
artifacts that should later be frozen, reviewed, and compared.
