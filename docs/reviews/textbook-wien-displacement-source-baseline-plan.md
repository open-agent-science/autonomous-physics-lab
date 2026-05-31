# Textbook Wien Displacement Source And Baseline Plan

Task: `TASK-0492`

Status: planning-only source/baseline preflight. No audit metrics were run, no
dataset snapshot was ingested, and no validation or falsification verdict is
claimed.

## Scope

This plan defines the admissible source, baseline, units, candidate data
routes, row schema, inclusion rules, holdout policy, and verification gates for
a future Textbook Formula Audit of the wavelength form of Wien displacement.

The future audit question must be scoped narrowly:

> For a declared blackbody-like dataset slice or exact-reference fixture, does
> the wavelength-domain peak relation `lambda_peak = b / T` agree with the
> declared peak wavelength within the pre-registered tolerance?

It must not claim that Wien displacement is universally validated or falsified.

## Formula Source And Constant Convention

Frozen baseline formula:

```text
lambda_peak = b / T
```

where:

- `lambda_peak` is the peak of spectral radiance per unit wavelength.
- `T` is thermodynamic temperature in kelvin.
- `b` is the Wien wavelength displacement law constant.

Pinned constant source:

- NIST Fundamental Physical Constants database, CODATA 2022 adjustment:
  https://www.nist.gov/pml/fundamental-physical-constants
- NIST constants search entry for "Wien wavelength displacement law constant":
  https://physics.nist.gov/cgi-bin/cuu/Results?search_for=wavelength

Baseline value for a future audit:

```text
b = 2.897771955e-3 m K
```

Use SI internally:

- temperature: K
- wavelength: m
- spectral radiance: W m^-3 sr^-1 if a spectrum is represented per unit
  wavelength
- optional display units: um or nm only after explicit conversion

Important convention boundary:

- This task uses the wavelength-domain peak. The frequency-domain peak and the
  wavelength corresponding to that frequency peak are different quantities.
- A future audit must reject rows whose source reports a frequency-domain,
  energy-domain, color-temperature, or broadband photometric peak unless the
  row explicitly includes a wavelength-domain spectral-radiance peak.
- Vacuum wavelength should be the default convention. Air wavelength rows
  require a stated refractive-index correction or exclusion.

## Candidate Data Routes

### Recommended Route A: Synthetic Exact-Reference Fixture

Use a deterministic exact-reference fixture generated from Planck spectral
radiance per unit wavelength and the same frozen constant convention. This is
the cleanest first audit route because it tests the APL plumbing, units,
peak-finding convention, and verification gates without source licensing,
instrument calibration, emissivity, or catalog-selection complications.

Fixture plan:

- Predeclare a temperature grid, for example log-spaced `T` values from
  100 K to 10000 K.
- For each temperature, compute `lambda_peak_expected_m = b / T`.
- Optionally sample Planck spectral radiance over a dense wavelength grid around
  the expected peak to test numerical peak finding independently from the
  closed-form baseline.
- Store only the generated fixture and generation script in a future task; do
  not fetch external data at runtime.

Recommended holdout:

- Sort rows by temperature.
- Use alternating log-temperature bands as train/test only for plumbing parity;
  no parameter fitting is allowed.
- Because `b` is frozen, "train" rows should only exercise parser and unit
  checks. The future metric must be reported on held-out rows.

Expected use:

- First audit run and CI fixture.
- Dimensional, monotonicity, limiting-behavior, and numerical-peak-finding
  gates.

Limitations:

- This route cannot test real-source emissivity, calibration, or non-blackbody
  failure modes.
- A pass on this route is a software/plumbing check, not empirical evidence
  about physical emitters.

### Optional Route B: NASA COBE/FIRAS CMB Monopole Spectrum

Use NASA LAMBDA COBE/FIRAS analyzed science products only after a future source
curation task pins the files, checks licensing/redistribution, and records
hashes.

Candidate source:

- NASA LAMBDA FIRAS product table:
  https://lambda.gsfc.nasa.gov/product/cobe/firas_prod_table.html

Why it is useful:

- The page lists a CMB monopole spectrum with uncertainties and related FIRAS
  calibrated spectra/covariance products.
- It is an empirical blackbody-like spectrum with an independently reported
  temperature context.

Why it is not the first recommended route:

- It gives a narrow low-temperature astrophysical slice rather than a broad
  temperature grid.
- FIRAS products are frequency/wavenumber oriented; the future audit must avoid
  confusing a frequency-domain peak with a wavelength-domain peak.
- Foreground subtraction, calibration covariance, and spectral-window effects
  must be handled before interpreting a peak.

Recommended status:

- Treat as a later empirical calibrator route, not as the first source of audit
  metrics.

### Optional Route C: NIST Spectral Irradiance Calibration Materials

Candidate source:

- NIST SP 250-89, Spectral Irradiance Calibrations:
  https://www.nist.gov/publications/sp250-spectral-irradiance-calibrations

Why it is useful:

- The NIST publication documents spectral irradiance scale realization,
  uncertainty handling, high-temperature blackbody use, Planck radiance, and
  spectral irradiance standards.

Why it is not the first recommended route:

- It is a calibration procedure/report, not a ready row-level open dataset for
  peak wavelength versus temperature.
- Extracting row-level calibrator values may require a separate source-artifact
  review and may not yield the exact row shape needed for this audit.

Recommended status:

- Use as a source-readiness reference for future laboratory calibration data,
  not as the first audit dataset.

## Row Schema For Future Audit

Minimum row fields:

| Field | Type | Units | Required | Notes |
| --- | --- | --- | :-: | --- |
| `row_id` | string | none | yes | Stable unique id. |
| `source_id` | string | none | yes | Source artifact or fixture id. |
| `route` | enum | none | yes | `synthetic_planck`, `cobe_firas`, `nist_calibration`, or later approved route. |
| `temperature_K` | float | K | yes | Thermodynamic temperature. |
| `temperature_uncertainty_K` | float/null | K | yes | Null only for exact synthetic rows. |
| `lambda_peak_observed_m` | float | m | yes | Declared or measured wavelength-domain peak. |
| `lambda_peak_uncertainty_m` | float/null | m | yes | Null only for exact synthetic rows. |
| `lambda_convention` | enum | none | yes | `vacuum`, `air_corrected`, or `unknown`. |
| `spectral_axis` | enum | none | yes | Must be `wavelength`. |
| `spectral_quantity` | enum | none | yes | Must identify per-wavelength spectral radiance/irradiance/exitance. |
| `instrument_or_generator` | string | none | yes | Instrument name or deterministic fixture generator. |
| `calibration_reference` | string | none | yes | DOI, URL, or committed source-artifact path. |
| `source_file_sha256` | string | none | yes | Required for all non-synthetic source files. |
| `retrieved_at_utc` | string/null | UTC | yes | Required for non-synthetic source files. |
| `notes` | string | none | no | Assumption notes and exclusions. |

Derived fields for a future runner:

- `lambda_peak_baseline_m = b / temperature_K`
- `relative_error = (lambda_peak_observed_m - lambda_peak_baseline_m) /
  lambda_peak_baseline_m`
- `combined_uncertainty_m` from source uncertainty propagation when available

## Inclusion And Exclusion Rules

Include rows only when all of the following are true:

- `temperature_K > 0`
- wavelength-domain peak is explicitly reported or deterministically generated
- spectral axis is wavelength, not frequency or energy
- units are convertible to SI without ambiguity
- blackbody or blackbody-like assumption is declared
- source artifact is pinned before metrics are run

Exclude rows when any of the following are true:

- peak is reported only in frequency, wavenumber, photon energy, color index, or
  broadband filter space
- source reports an effective temperature without a corresponding measured or
  generated wavelength-domain peak
- non-thermal emission lines dominate the spectrum
- emissivity correction is unknown for a non-ideal emitter
- source license or provenance is not reviewable
- the row is derived from a live external fetch during the audit task

## Verification Gates

A future audit must run and report the following gates before any per-slice
verdict:

1. Dimensional consistency
   - `b / T` must have dimensions of length.
   - All source wavelengths and temperatures must convert to SI.

2. Constant convention gate
   - The runner must use the frozen NIST/CODATA wavelength displacement
     constant.
   - The frequency-domain Wien constant must not be substituted.

3. Peak-domain gate
   - The row must represent a wavelength-domain peak.
   - Frequency-domain or broadband peaks are excluded, not converted with
     `lambda = c / nu`.

4. Monotonicity gate
   - For rows sorted by `T`, predicted `lambda_peak` must decrease as
     temperature increases.
   - Synthetic fixture rows should satisfy this exactly.

5. Limiting-behavior gate
   - As `T` increases, `lambda_peak` approaches shorter wavelengths.
   - As `T` decreases, `lambda_peak` shifts to longer wavelengths.
   - The audit must report whether the chosen temperature window stays within
     the spectral coverage of the source.

6. Range-validity gate
   - For empirical rows, the predicted peak must fall inside the measured
     spectral window with margin.
   - Rows whose predicted peak is outside the source coverage are range failures,
     not evidence against the formula.

7. Uncertainty gate
   - For empirical rows, compare residuals against propagated temperature and
     wavelength uncertainty.
   - If uncertainty is missing, mark the empirical slice `INCONCLUSIVE`.

8. Negative-control gate
   - Include at least one deterministic wrong-constant or wrong-domain control,
     such as using the frequency-domain peak constant against wavelength-domain
     rows.
   - The control is diagnostic only and must not be used to tune `b`.

## Recommended Future Task Split

1. Synthetic fixture task
   - Create the deterministic fixture and runner.
   - Report only software/gate behavior.
   - Expected output: sandbox agent run plus review note; no claim promotion.

2. FIRAS source-artifact task
   - Pin NASA LAMBDA files, checksums, license/provenance, and row extraction
     semantics.
   - Do not compute final audit metrics in the source task.

3. Empirical audit task
   - Run the predeclared runner against pinned empirical rows.
   - Preserve negative or inconclusive outcomes.
   - Publish a RESULT only if the task explicitly authorizes Gate A result
     publication.

## Output Routing

- Task verdict: `not_applicable`.
- Canonical destination: review note under `docs/reviews/`.
- Review tier: `none`.
- Gate A status: not attempted.
- Gate B status: not attempted.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Publication blocker: this is a planning artifact only; no dataset snapshot,
  deterministic audit run, or result schema artifact exists yet.

## Limitations

- No external source files were downloaded or pinned.
- No peak-finding code was implemented.
- No metric was computed.
- No empirical dataset route is approved until a future source curation task
  pins files, licenses, checksums, and row semantics.
- The recommended synthetic route can test APL mechanics but cannot establish
  empirical support for any physical emitter class.
