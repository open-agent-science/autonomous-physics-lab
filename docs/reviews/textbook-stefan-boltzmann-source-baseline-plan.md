# Textbook Stefan-Boltzmann Source And Baseline Plan

Task: `TASK-0493`

Status: planning-only source/baseline preflight. No audit metrics were run, no
dataset snapshot was ingested, and no validation or falsification verdict is
claimed.

## Scope

This plan defines the source, constants, baseline formula, candidate data
routes, row schema, inclusion rules, holdout policy, verification gates, and
public wording boundaries for a future Textbook Formula Audit of the
Stefan-Boltzmann law.

The future audit question must be scoped narrowly:

> For a declared blackbody exact-reference fixture, or for a pinned stellar
> sample with independent radius, effective temperature, and luminosity
> evidence, does `L = 4 * pi * R^2 * sigma * Teff^4` agree with the reference
> luminosity within the pre-registered tolerance?

It must not claim that the Stefan-Boltzmann law is universally validated or
falsified.

## Formula Source And Constant Convention

Frozen baseline formula for a spherical emitter:

```text
L = 4 * pi * R^2 * sigma * T^4
```

Equivalent surface-flux form:

```text
P = sigma * A * T^4
```

where:

- `L` or `P` is radiated power in watts.
- `R` is radius in meters for the spherical form.
- `A` is emitting area in square meters for the surface-flux form.
- `T` or `Teff` is thermodynamic or effective temperature in kelvin.
- `sigma` is the Stefan-Boltzmann constant.

Pinned constant source:

- NIST Fundamental Physical Constants database, CODATA 2022 adjustment:
  https://www.nist.gov/pml/fundamental-physical-constants
- NIST constants search entry for "Stefan-Boltzmann constant":
  https://physics.nist.gov/cgi-bin/cuu/Results?search_for=Stefan-Boltzmann

Baseline value for a future audit:

```text
sigma = 5.670374419e-8 W m^-2 K^-4
```

Use SI internally:

- radius: m
- area: m^2
- temperature: K
- luminosity or power: W

Optional display units such as `R_sun` and `L_sun` are allowed only after an
explicit conversion. The recommended nominal Solar constants are:

- `R_sun = 6.957e8 m` (IAU nominal solar radius)
- `L_sun = 3.828e26 W` (IAU nominal solar luminosity)

## Candidate Data Routes

### Recommended Route A: Synthetic Exact-Reference Blackbody Fixture

Use a deterministic exact-reference fixture as the first audit route. This is
the safest first step because it tests units, constants, parser behavior,
uncertainty propagation, and verification gates without catalog selection,
extinction, bolometric correction, or circularity risk.

Fixture plan:

- Predeclare a grid over radius and temperature, for example:
  - `R` from `0.1 R_sun` to `100 R_sun`;
  - `T` from `2500 K` to `40000 K`.
- Generate `luminosity_expected_W = 4 * pi * R^2 * sigma * T^4`.
- Store the generated fixture and generation script in a future task.
- Do not fit `sigma`, `R`, `T`, or any scale factor from the fixture.

Recommended holdout:

- Use alternating radius-temperature grid blocks as train/test only for
  software parity.
- Because the formula and constant are frozen, "train" rows may only exercise
  parsing and unit checks.
- Report final checks on held-out grid blocks.

Expected use:

- First CI-safe runner and review note.
- Dimensional, monotonicity, radius-scaling, temperature-scaling, and
  wrong-exponent negative-control gates.

Limitation:

- A pass on this route is a software and convention check, not empirical
  evidence about stars or physical blackbody emitters.

### Recommended Route B: Independent Stellar Calibrator Slice

Use an empirical stellar slice only after a future source-curation task pins
all source files, hashes, licenses, and row semantics.

Preferred source shape:

- detached eclipsing binaries or interferometric angular-diameter calibrators
  with independently measured radius and effective temperature;
- Gaia DR3 or equivalent public astrometry/photometry for distance and context;
- bolometric flux or luminosity from a source path that is not computed by
  reusing the same radius-temperature Stefan-Boltzmann formula under audit.

Why this route matters:

- It gives a public-friendly stellar audit that pairs naturally with the
  Stellar Mass-Luminosity planning surface.
- It can expose practical failure surfaces: evolved stars, extinction,
  temperature-scale mismatch, bolometric correction uncertainty, metallicity,
  and radius provenance.

Why it is not the first route:

- Many catalog luminosities are model-derived from `R` and `Teff`, which would
  make the audit circular.
- Effective temperature is not a directly observed thermodynamic blackbody
  temperature for all stars.
- Extinction, bolometric corrections, binarity, variability, and evolutionary
  stage can dominate the residual surface.

Minimum rule:

- Any empirical row whose luminosity was calculated from the same `R` and
  `Teff` through Stefan-Boltzmann must be labeled `model_derived_circular` and
  excluded from the benchmark axis. It may be retained only as a circularity
  control class.

### Optional Route C: Laboratory Blackbody Calibration Artifacts

Candidate source:

- NIST spectral irradiance or blackbody calibration publications and source
  artifacts, if a future task can pin row-level calibrated power, area, and
  temperature data.

Recommended status:

- Keep this as a later empirical route. It may be cleaner than stellar data,
  but it needs a separate source-artifact review because publications often
  describe calibration procedures rather than redistributable row-level
  datasets.

## Route Decision

The first future audit should use **Route A** only.

Route B should be a separate later empirical audit after a pinned source task
proves that luminosity, radius, and temperature are independent enough for a
non-circular test. Route A and Route B must not be mixed in one verdict.

This separation keeps the first task simple and makes later empirical evidence
honest: exact-reference rows test APL mechanics; stellar rows test source and
assumption discipline.

## Row Schema For Future Audit

Minimum row fields:

| Field | Type | Units | Required | Notes |
| --- | --- | --- | :-: | --- |
| `row_id` | string | none | yes | Stable unique id. |
| `source_id` | string | none | yes | Source artifact or fixture id. |
| `route` | enum | none | yes | `synthetic_blackbody`, `stellar_calibrator`, `laboratory_blackbody`, or later approved route. |
| `radius_m` | float/null | m | yes | Required for spherical form. |
| `area_m2` | float/null | m^2 | yes | Required for non-spherical surface-flux form. |
| `temperature_K` | float | K | yes | Thermodynamic or effective temperature. |
| `luminosity_observed_W` | float | W | yes | Exact fixture value or independently sourced luminosity. |
| `radius_uncertainty_m` | float/null | m | yes | Null only for exact synthetic rows. |
| `temperature_uncertainty_K` | float/null | K | yes | Null only for exact synthetic rows. |
| `luminosity_uncertainty_W` | float/null | W | yes | Null only for exact synthetic rows. |
| `luminosity_provenance_class` | enum | none | yes | `exact_fixture`, `flux_distance`, `catalog_independent`, `model_derived_circular`. |
| `temperature_provenance_class` | enum | none | yes | `exact_fixture`, `spectroscopic`, `interferometric`, `photometric_model`, or source-specific label. |
| `radius_provenance_class` | enum | none | yes | `exact_fixture`, `eclipsing_binary`, `interferometric`, `model_derived`, or source-specific label. |
| `extinction_policy` | enum | none | yes | `not_applicable`, `corrected`, `uncorrected_blocker`, or `unknown_blocker`. |
| `source_file_sha256` | string/null | none | yes | Required for all non-synthetic source files. |
| `retrieved_at_utc` | string/null | UTC | yes | Required for all non-synthetic source files. |
| `inclusion_status` | enum | none | yes | `included` or `excluded:<reason>`. |
| `notes` | string | none | no | Assumption notes and exclusions. |

Derived fields for a future runner:

- `luminosity_baseline_W = 4 * pi * radius_m^2 * sigma * temperature_K^4`
- `relative_error = (luminosity_observed_W - luminosity_baseline_W) /
  luminosity_baseline_W`
- `log10_residual_dex = log10(luminosity_observed_W / luminosity_baseline_W)`
- propagated uncertainty from radius, temperature, and luminosity when present

## Inclusion And Exclusion Rules

Include rows only when all of the following are true:

- `temperature_K > 0`
- either `radius_m > 0` for spherical rows or `area_m2 > 0` for surface-flux
  rows
- luminosity or power is explicitly reported or deterministically generated
- units convert to SI without ambiguity
- source artifact or fixture generator is pinned before metrics are run
- empirical rows have reviewable uncertainty semantics
- empirical rows are non-circular for the benchmark axis

Exclude rows when any of the following are true:

- luminosity is computed from the same `R`, `T`, and `sigma` under audit
- source provides effective temperature but no independently sourced
  luminosity or radius
- radius is model-derived from luminosity and temperature without independent
  measurement
- extinction or bolometric correction policy is missing for stellar rows
- star is unresolved multiple, strongly variable, or evolved unless the slice
  explicitly targets that class
- source license, retrieval date, or checksum is not reviewable
- the row is produced by a live external fetch during the audit task

## Holdout Policy

For Route A:

- Freeze a radius-temperature grid before generation.
- Assign held-out blocks by grid cell, not after residuals are inspected.
- Use train rows only for parser and unit validation; no parameter fitting is
  allowed.

For Route B:

- Split by source family and stellar regime before any metric:
  - reference slice: main-sequence calibrators with independent radius,
    temperature, and luminosity;
  - holdout slices: cool dwarfs, hot stars, evolved stars, high-extinction
    rows, and sparse-radius regimes;
  - excluded/control slice: `model_derived_circular` rows.
- Report row counts before and after every filter.
- Do not move rows between reference and holdout after counts are reported.

## Verification Gates

A future audit must run and report these gates before any per-slice verdict:

1. Dimensional consistency
   - `sigma * A * T^4` must reduce to watts.
   - The spherical form must use `A = 4 * pi * R^2`.

2. Constant convention gate
   - The runner must use the frozen NIST/CODATA 2022 `sigma`.
   - Solar-unit display conversions must be separated from SI computation.

3. Temperature exponent gate
   - At fixed radius, predicted luminosity must scale as `T^4`.
   - Include a wrong-exponent negative control, such as `T^3` or `T^5`.

4. Radius/area scaling gate
   - At fixed temperature, predicted luminosity must scale as `R^2` or area.
   - Include a wrong-area control for spherical rows.

5. Monotonicity gate
   - Predicted luminosity must increase with temperature at fixed radius and
     with radius at fixed temperature.

6. Circularity gate
   - Empirical rows must prove that benchmark luminosity is not computed from
     the same radius-temperature formula being audited.
   - Circular rows are controls, not evidence.

7. Range-validity gate
   - The future audit must state the temperature and radius range tested.
   - Empirical rows outside the declared stellar class become holdout or
     excluded rows, not universal evidence against the law.

8. Uncertainty gate
   - Empirical residuals must be compared against propagated uncertainty.
   - Missing uncertainty yields `INCONCLUSIVE`, not a pass/fail claim.

## Recommended Future Task Split

1. Synthetic fixture task
   - Create the deterministic fixture and runner.
   - Report software/gate behavior only.
   - Expected output: sandbox agent run plus review note; no claim promotion.

2. Empirical source-curation task
   - Pin a DEB or interferometric calibrator snapshot, Gaia/context files if
     used, source licenses, checksums, and row semantics.
   - Do not compute final audit metrics in the source task.

3. Empirical audit task
   - Run the predeclared runner against pinned empirical rows.
   - Preserve negative or inconclusive outcomes.
   - Publish a RESULT only if the task explicitly authorizes Gate A result
     publication.

## Public Wording Boundaries

Allowed:

- "This exact-reference fixture checks APL's Stefan-Boltzmann units and gates."
- "This future empirical slice would test a pinned stellar calibrator sample
  under declared assumptions."
- "Rows with circular luminosity derivation are excluded from benchmark
  evidence."

Forbidden:

- "APL validated the Stefan-Boltzmann law."
- "APL falsified the Stefan-Boltzmann law."
- "The law holds or fails for stars in general."
- Any inference about stellar evolution, composition, habitability, or
  universal blackbody behavior from this planning artifact.

## Output Routing

- Task verdict: `not_applicable`.
- Canonical destination:
  `docs/reviews/textbook-stefan-boltzmann-source-baseline-plan.md`.
- Review tier: `none`.
- Gate A status: not attempted.
- Gate B status: not attempted.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Publication blocker: this is a planning artifact only; no dataset snapshot,
  deterministic audit run, or result schema artifact exists yet.

## Limitations

- No external source files were downloaded or pinned.
- No fixture generator or runner was implemented.
- No metrics were computed.
- No empirical dataset route is approved until a future source-curation task
  proves provenance, licensing, checksums, uncertainty semantics, and
  non-circular luminosity/radius/temperature evidence.
- The recommended synthetic route can test APL mechanics but cannot establish
  empirical support for any physical emitter class.
