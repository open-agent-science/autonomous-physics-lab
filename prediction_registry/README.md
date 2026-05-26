# Prediction Registry

The prediction registry stores **prospective** scientific forecasts that
were frozen before later measurements were reviewed.

## Layout

```
prediction_registry/
  <domain>/
    PRED-XXXX.yaml
```

Current domains:

- `nuclear_masses/` — nuclear-mass forecasts. Uses
  `physics_lab/schemas/nuclear_mass_prediction.schema.json` with extra
  nuclide-identity requirements.

Future domains may include `exoplanet_mass_radius/`,
`atomic_clock_ratios/`, etc. Each domain may extend the generic schema in
`physics_lab/schemas/prediction.schema.json` with stricter, domain-specific
target-structure requirements; if no extension exists, the generic schema
is used directly.

## What the Registry Is For

Use the registry when a contributor or agent wants to record:

- a future forecast for named targets in a specific domain;
- the frozen model and source state used to make that forecast;
- the exact predicted values and their uncertainty semantics;
- the later reveal conditions under which the forecast may be compared.

The registry is appropriate only for **before-measurement** predictions
and must record `live_external_fetch_allowed: false` in the
`source_state` block.

## What the Registry Is Not For

The registry must not be used to:

- store retrospective time-split benchmarks as if they were blind
  prediction;
- promote claims before later reviewed comparison;
- rewrite canonical `results/`, `claims/`, or `knowledge/`;
- pull live external measurements during registration;
- treat a registered forecast as evidence of discovery on its own.

## Authoritative Documents

- [`docs/prediction-registry-policy.md`](../docs/prediction-registry-policy.md)
  — original (nuclear-mass-focused) policy. Authoritative for all
  registry layout and freeze rules.
- [`docs/blind-holdout-benchmark-protocol.md`](../docs/blind-holdout-benchmark-protocol.md)
  — pre-reveal package and reveal record format used by registry
  comparisons.
- [`docs/nuclear-prediction-reveal-protocol.md`](../docs/nuclear-prediction-reveal-protocol.md)
  — domain-specific reveal protocol for nuclear-mass predictions. Other
  domains adding prediction lanes may add an analogous
  `<domain>-prediction-reveal-protocol.md` next to it.
- [`docs/result-promotion-protocol.md`](../docs/result-promotion-protocol.md)
  — master multi-class output protocol. Includes the
  `review_tier: AGENT_PROPOSED` pathway for agent-driven
  pre-registration.

## Adding a New Domain

To add a new domain (e.g. exoplanets):

1. Create `prediction_registry/<domain>/` with a short `README.md` that
   states the domain's measurement units, accepted source classes, and
   the reveal cadence the domain expects.
2. Decide whether the generic `prediction.schema.json` suffices or
   whether a domain-specific extension schema is needed (typical reason:
   domain-specific target-identity requirements such as nuclide id or
   planet host id). Add the extension schema under
   `physics_lab/schemas/` only if needed.
3. Optionally add a domain-specific reveal protocol document under
   `docs/` modelled on `nuclear-prediction-reveal-protocol.md`.
4. First registered PRED-* entry in the new domain should be reviewed by
   a maintainer (regardless of `review_tier`) because it sets the
   precedent for future agent-driven entries.
