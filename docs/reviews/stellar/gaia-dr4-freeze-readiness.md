# Gaia DR4 Stellar-Transfer Freeze Readiness

- Task: `TASK-1029`
- Campaign: textbook formula audit, Stellar M-L lane
- Review date: 2026-07-15
- Mode: value-blind pre-release planning
- Verdict: **`HOLD_FIELDS_NOT_READY`**

## Decision

The route is scientifically coherent, and an official draft Gaia DR4 data
model is now available. It names component-mass fields and source-level
luminosity fields, but it does not establish an admissible route from the two
component masses in `nss_masses` to bolometric luminosities for those same two
components. The documented `fluxratio` is a G-band ratio, not a reviewed
bolometric decomposition. A source-level FLAME luminosity therefore cannot be
silently copied to either component or split after inspecting release values.

The functional prediction cannot yet be frozen because same-component target
semantics, the resulting eligible-system count, and the minimum coverage rule
remain unresolved. This is a narrower blocker than missing field names. No
Gaia DR4 row, target identity, or pre-release mass/luminosity value was queried.

The admissible event trigger remains state-based:

> Gaia DR4 is officially published, or ESA publishes an official DR4 draft
> data model containing the required mass and luminosity semantics.

The draft-model part of that trigger is satisfied. It does not by itself
authorize value access: the same-component luminosity gate, value-blind
identity freeze, and final functional freeze must all pass first.

## Official Metadata Gate

Only the official ESA/Gaia prerelease artifact and official Gaia pages were
used. The artifact was retrieved on 2026-07-15 without committing source bytes.

Pinned prerelease artifact:

- landing page: <https://www.cosmos.esa.int/web/gaia/dr4-prerelease>
- ZIP: <https://anonftp.cosmos.esa.int/pub/GAIA_PUBLIC_DATA/Gaia_DR4/dr4-prerelease/gaia-dr4-prerelease-draft-data-model_2026-06-26.zip>
- ZIP size: `2840832` bytes
- ZIP SHA-256: `d807eae98acbeec0a0af2ce6a5d7d352298df6f270a1f13207cc8d1becf42c66`
- inner PDF: `gaia-dr4-prerelease-draft-data-model.pdf`
- PDF SHA-256: `8c33055c122eb3f5ef6ac64e8624e6c11a1e261f6fa4108c635296b52feeb043`
- license instructions: <https://www.cosmos.esa.int/web/gaia-users/license>

| Required evidence | Official draft state | Freeze consequence |
| --- | --- | --- |
| Release event | DR4 remains forthcoming | No release values may be read |
| Draft data model | Official 2026-06-26 ZIP and PDF are checksum-pinned above | Field names can be reviewed against this version |
| Component dynamical mass | `nss_masses.m1` and `nss_masses.m2`, with lower/upper confidence fields, are defined | Candidate mass inputs exist; admissible solution provenance still needs a frozen rule |
| Source luminosity | `lum_flame` and `lum_flame_spec`, with confidence fields, are defined as source/star luminosities | They are not documented as separate luminosities for the `m1` and `m2` components |
| Flux ratio | `fluxratio` is explicitly the secondary-to-primary ratio in the G band | It cannot be treated as a bolometric luminosity ratio without a separately reviewed transformation |
| Same-component join | No reviewed mapping in this task binds both masses to two component bolometric luminosities | Primary scientific blocker |
| Joint eligible count | Not computable without reading values and applying the unresolved join | Minimum reveal coverage remains an explicit pre-access blocker |

Supporting official pages:

- ESA/Gaia DR4 landing page: <https://www.cosmos.esa.int/web/gaia/data-release-4>
- ESA/Gaia DR4 content overview: <https://www.cosmos.esa.int/web/gaia/dr4>
- Gaia ESA Archive: <https://gea.esac.esa.int/archive/>
- Gaia data access policy: <https://www.cosmos.esa.int/web/gaia/data-access>

## Candidate Functional Freeze

The following target-independent payload is fixed from `RESULT-0022` and may
be used by a later registration task only after the remaining blockers are
closed. It does not name or rank stars and is not a registered prediction.

| Field | Frozen candidate |
| --- | --- |
| Anchor | `RESULT-0022`, `results/EXP-0015/RUN-0001/result.yaml` |
| Quantity | Per-component `log10(L/L_sun)` from per-component `log10(M/M_sun)` |
| Functions | `alpha=3.5`, `alpha=4.0`, and train-fitted `alpha=4.526004`; intercept `0.0` for each |
| Formula version | `result0022_stellar_ml_log_power_v1` |
| Mass eligibility | Direct dynamical component mass; `0.5 <= M/M_sun < 2.0`; required uncertainty fields present |
| Stellar eligibility | Main-sequence-compatible and both components resolved under one predeclared solution route |
| Luminosity eligibility | Bolometric luminosity for the same component as the mass, with a predeclared provenance and uncertainty route |
| Primary metric | System-grouped MAE in `log10(L/L_sun)` dex; both components stay in one system unit |
| Missing fields | Exclude before scoring with a machine-readable reason; never impute, refit, or substitute model-derived mass or luminosity |
| Tuning boundary | No coefficient, regime, comparator, threshold, provenance route, eligibility rule, or wording change after value access |

### Exact RESULT-0022 null

The comparator is the train-only per-mass-band median used by the deterministic
RESULT-0022 engine, not a new Gaia-fitted baseline:

| Mass band | Half-open range | Frozen train count | Frozen median `log10(L/L_sun)` |
| --- | --- | ---: | ---: |
| `low` | `[0.5, 1.0)` | 26 | `-0.5165` |
| `solar` | `[1.0, 2.0)` | 76 | `0.5770` |

The frozen global fallback median is `0.4235`; it may be used only for an
unexpected band label, which must also be reported as a protocol anomaly. The
committed RESULT-0022 holdout null MAE is `0.331817 dex`.

### Decision and coverage blockers

The headline candidate rule is: report each frozen function against the exact
null above and accept a transfer advantage only when its system-grouped MAE is
more than `0.04 dex` below the null. Otherwise return `INVALID` when coverage
is adequate or `INCONCLUSIVE` when coverage/compatibility is inadequate. No
coefficient may be selected from Gaia outcomes.

The minimum number of eligible independent systems is deliberately
**unfrozen**. It is a blocker, not permission to choose a sample-size threshold
after release. A later value-blind freeze task must set it before the first
Gaia DR4 target-value query. The same task must pin the exact data-model
version, admissible solution enums, units, confidence handling, component join,
formula serialization, and exclusion vocabulary.

The pre-access timing rule is strict: all functional payload, identity,
coverage, and same-component luminosity decisions must be committed and
review-approved before any target mass or luminosity value is queried. Prior
value access routes the lane to contamination review instead of retrospective
freeze registration.

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

The future manifest must contain `system_id`, Gaia source identifiers for both
components where available, aliases, coordinates and reference epoch, match
method, evidence references, match status, ambiguity reason, and final
blind-eligibility status. This task does not build that manifest.

## Registry Compatibility

The generic `physics_lab/schemas/prediction.schema.json` can carry a model
reference, target quantity, reveal conditions, and limitations. Domain-specific
functional and whole-system fields may be stored in a reviewed extension; a
new core schema is optional and is not a blocker for this readiness decision.
Any extension must still preserve formula serialization, coefficients, units,
eligibility/missing-field rules, event identity, leakage policy, comparator,
decision rule, and an explicitly empty pre-release target list.

## Stops And Follow-On Shapes

Stop the route if final semantics provide no same-component dynamical mass and
bolometric luminosity route, no value-blind DEBCat identity boundary, or any
workflow would require post-release tuning.

Bounded follow-ons, only after maintainer assignment:

1. `Gaia same-component luminosity gate`: decide whether official metadata can
   bind two dynamical masses to two bolometric component luminosities without
   outcome-driven decomposition; pin exact solution enums and units.
2. `DEBCat-to-Gaia identity freeze`: build the value-blind whole-system
   identity manifest without reading mass or luminosity values.
3. `Gaia functional freeze registration`: set the minimum independent-system
   count, freeze the exact payload above, and register it before value access.
4. `Gaia reveal scoring`: separate reviewed task after every pre-access gate
   passes.

A schema helper may be added if it reduces ambiguity, but it is not a required
predecessor to the scientific gates.

## Output Routing

This packet changes prospective readiness only. It creates no DR4 dataset,
target list, `PRED`, `RESULT`, `CLAIM`, or `KNOW` artifact and does not alter
`RESULT-0022`. `HOLD_FIELDS_NOT_READY` now means that same-component
bolometric-luminosity semantics and pre-access coverage remain unresolved; it
is neither a failed stellar relation nor evidence that the future transfer
will succeed.
