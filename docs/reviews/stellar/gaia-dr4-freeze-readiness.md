# Gaia DR4 Stellar-Transfer Freeze Readiness

- Task: `TASK-1029`
- Campaign: textbook formula audit, Stellar M-L lane
- Review date: 2026-07-14
- Mode: value-blind pre-release planning
- Verdict: **`HOLD_FIELDS_NOT_READY`**

## Decision

The route is scientifically coherent but cannot be frozen yet. The official
ESA/Gaia pages describe expected DR4 products, including non-single-star and
astrophysical-parameter products, but the DR4 draft data model is not published
at the review boundary. Exact column names, units, uncertainty semantics,
eligible solution types, and the count of sources carrying both component mass
and luminosity therefore remain unverified. No Gaia DR4 row, target identity,
or pre-release value was queried.

The admissible event trigger is state-based, not a calendar date:

> Gaia DR4 is officially published, or ESA publishes an official DR4 draft
> data model containing the required mass and luminosity semantics.

A target release date, news item, or secondary summary does not satisfy this
trigger.

## Official Metadata Gate

Only official ESA/Gaia metadata was used. The pages were accessed on
2026-07-14.

| Required evidence | Official metadata state | Freeze consequence |
| --- | --- | --- |
| Release event | DR4 remains a forthcoming release on the official landing page | Event trigger not satisfied |
| Product inventory | The official content overview lists expected main, NSS, and astrophysical-parameter products | Product families are plausible, not field-frozen |
| Draft/final data model | The official page says a draft model will be published in advance; no draft is linked | Exact field contract unavailable |
| Component dynamical mass | Expected NSS mass/orbit products are described, but exact DR4 fields, units, bounds, and solution qualifiers are not final | Required semantics unverified |
| Bolometric luminosity | Expected astrophysical-parameter products are described, but exact DR4 luminosity field, unit, provenance, and uncertainty fields are not final | Required semantics unverified |
| Two-mass solution types | Expected NSS content includes binary solutions, but the exact admissible two-component solution vocabulary is not frozen | Eligibility rule cannot bind to final enums |
| Joint source count | General source counts are described, but no official count is available for sources carrying both admissible component masses and luminosity | Minimum reveal coverage cannot be assessed |

Official sources:

- ESA/Gaia DR4 landing page: <https://www.cosmos.esa.int/web/gaia/data-release-4>
- ESA/Gaia DR4 content overview: <https://www.cosmos.esa.int/web/gaia/dr4>
- Gaia ESA Archive: <https://gea.esac.esa.int/archive/>
- Gaia data access policy: <https://www.cosmos.esa.int/web/gaia/data-access>

## Proposed Functional Freeze

This is a target-independent payload shape for a later task. It does not name
or rank stars and is not a registered prediction.

| Field | Frozen proposal |
| --- | --- |
| Anchor | `RESULT-0022`, `results/EXP-0015/RUN-0001/result.yaml` |
| Quantity | `log10(L/L_sun)` predicted from `log10(M/M_sun)` |
| Functions | `alpha=3.5`, `alpha=4.0`, and train-fitted `alpha=4.526004`, all with intercept `0.0` |
| Formula version | `result0022_stellar_ml_log_power_v1` |
| Eligibility | Per-component dynamical mass; both components resolved; `0.5 <= M/M_sun <= 2.0`; main-sequence-compatible; required uncertainty fields present |
| Comparator | Frozen RESULT-0022 per-mass-band train-median null |
| Primary metric | System-level holdout MAE in dex |
| Decision rule | A function must beat the frozen null by more than `0.04 dex`; sparse or incompatible coverage routes to `INCONCLUSIVE` |
| Missing fields | Exclude before scoring with a machine-readable reason; never impute, refit, or substitute model-derived mass |
| Tuning boundary | No coefficient, regime, comparator, threshold, provenance route, or wording change after the event trigger |

The later freeze must pin the exact source commit, data-model version, formula
serialization, units, uncertainty handling, and minimum system count before any
DR4 value is read. If bolometric luminosity is absent but radius and effective
temperature semantics are final, a separate pre-reveal task may assess a
Stefan-Boltzmann route. It must not be selected after inspecting values.

## DEBCat Leakage Policy

`RESULT-0022` was built from DEBCat, so a Gaia row belonging to any DEBCat
system is not independent evidence. Leakage control is whole-system and
value-blind:

1. Freeze a DEBCat identity manifest from committed system identities before
   querying DR4 values.
2. Resolve aliases using stable identifiers and documented coordinate/epoch
   evidence; do not use mass or luminosity similarity for identity matching.
3. Keep both binary components in one identity unit.
4. Exclude every confirmed or probable DEBCat system from the primary blind
   score. A confirmed overlap may appear only in a separately labelled
   in-sample diagnostic.
5. Route unresolved one-to-many or coordinate-epoch ambiguity to
   `AMBIGUOUS_IDENTITY`; do not score it.

The future identity manifest must contain `system_id`, Gaia source identifiers
for both components where available, aliases, coordinates and reference epoch,
match method, evidence references, match status, ambiguity reason, and final
blind-eligibility status. This task does not build that manifest.

## Registry Compatibility

The generic `physics_lab/schemas/prediction.schema.json` can record a model
reference, target quantity, reveal conditions, and limitations. It does not,
however, require a target-independent functional-prediction payload or encode
the whole-system leakage and post-trigger immutability fields above. The
current policy also describes named targets as the normal registration shape.

Therefore a later schema task should add a Stellar functional-prediction
extension before registration. It should require formula serialization,
coefficient and unit locks, eligibility and missing-field rules, event-trigger
identity, system-level leakage policy, comparator and decision rule, and an
explicit empty pre-release target list. This registry gap is real but is not
the primary verdict because field semantics already block preparation.

## Stops And Follow-On Shapes

Stop the route if final DR4 semantics provide no admissible two-component
dynamical masses, no compatible bolometric luminosity route, no value-blind
DEBCat identity boundary, or any workflow would require post-release tuning.

Bounded follow-ons, only after maintainer assignment:

1. `Gaia DR4 field-identity gate`: pin the official data model and exact field,
   unit, uncertainty, solution-type, and source-count semantics.
2. `Stellar functional-prediction schema`: add and test the domain extension;
   no prediction registration.
3. `DEBCat-to-Gaia identity freeze`: build the value-blind whole-system
   identity manifest without reading mass or luminosity values.
4. `Gaia functional freeze registration`: register the approved payload before
   reveal-value access.
5. `Gaia reveal scoring`: separate reviewed task after all freezes pass.

## Output Routing

This packet changes prospective readiness only. It creates no DR4 dataset,
target list, `PRED`, `RESULT`, `CLAIM`, or `KNOW` artifact and does not alter
`RESULT-0022`. `HOLD_FIELDS_NOT_READY` means wait for official field semantics;
it is neither a failed stellar relation nor evidence that the future transfer
will succeed.
