# Stellar Mass-Luminosity OOD — Source and Baseline Plan

**Task:** TASK-0444
**Status:** source/baseline planning only (no live fetch, no snapshot pinned, no metric run)
**Campaign:** Textbook Formula Audit (`../textbook-formula-audit.md`)
**Candidate:** Slate item 1 — Stellar Mass-Luminosity (M-L) Out-of-Distribution Audit
**Mode:** `planning_only`

**Inputs reviewed:**

- `../textbook-formula-audit.md` — campaign charter and guardrails
- `../../../campaign_profiles/textbook-formula-audit.yaml` — machine-readable autonomy contract
- `../../notes/textbook-formula-audit-candidate-list.md` — ordered candidate slate
- `../../../tasks/proposals/20260528-roman-stellar-mass-luminosity-ood-source-baseline-planning.yaml` — accepted proposal
- `../../result-promotion-protocol.md` — multi-tier promotion policy
- `../../research-quality-gate.md` — shared cross-campaign quality gate

## Scope

This artifact declares the **source query, row schema, inclusion/exclusion
filter chain, frozen baseline parameters, holdout policy, and verification-gate
slate** that a future Stellar M-L audit task must use. It is the
source-and-baseline planning step (lifecycle step 1) defined in the campaign's
*Expected Audit Lifecycle*.

This task does **not** run a live Gaia fetch, does **not** pin a snapshot
checksum, does **not** ingest rows, does **not** compute any metric, does
**not** fit or refit a baseline, does **not** register a prediction, and does
**not** produce or promote a claim. The audited formula's claim status is
unaffected.

The target formula is the main-sequence mass-luminosity relation in piecewise
power-law form

```text
L / L_sun = L0_bin * (M / M_sun) ^ alpha_bin
```

audited **per mass bin**, never as a single global `alpha` fit.

## Method

1. Read the campaign charter, profile, candidate list, and the accepted
   proposal to confirm the required planning outputs and the forbidden
   actions.
2. Identified the observable surface Gaia DR3 actually provides
   (astrometry, photometry, and FLAME-derived astrophysical parameters) and
   separated **model-independent** from **model-derived** quantities.
3. Recorded the central admissibility finding (mass circularity, see F1) and
   reshaped the recommended first sample accordingly.
4. Declared the snapshot/query plan, row schema, filter chain, frozen
   baseline, holdout policy, and verification gates in advance so a later
   execution task is reviewable before any data is touched.

## F1. Critical finding — Gaia photometric/isochrone masses are circular for this audit

Gaia DR3 does **not** measure stellar mass directly. The `astrophysical_parameters`
table exposes `mass_flame`, but FLAME derives mass by fitting stellar-evolution
isochrones to the observed luminosity and effective temperature. Those
isochrones already encode a mass-luminosity relation. **Auditing the M-L
relation against `mass_flame` would test the relation against itself — a
circular benchmark with no falsification power.**

This is the same class of trap recorded for the Exoplanet campaign, where
model-inferred (e.g. Chen-Kipping forecast) masses must not be used to validate
the same forecast (`docs/reviews/exoplanet-mass-radius-source-surface-review.md`,
findings F2 and F6). The resolution is identical: label model-derived mass rows
as a distinct, **excluded** row class and require an independent mass source for
the benchmark axis.

**Consequence for the first slice:** the naive "Gaia DR3 single main-sequence
stars" sample is **inadmissible** as the benchmark mass axis. The recommended
first sample is reshaped to a **model-independent dynamical-mass sample**
(Section "Source Plan"), with Gaia DR3 supplying distances, luminosities,
metallicity proxy, and quality flags. `mass_flame` rows are retained only as a
labeled `model_inferred` control class, never as benchmark truth.

## Source Plan

The audit uses a **two-source design**. No source is fetched in this task; this
section declares what a future ingestion task must pin.

### Source A (mass axis) — model-independent dynamical masses — `SML-SRC-CLASS-001` (recommended first)

- **Content:** detached eclipsing binaries (DEBs) with masses and radii measured
  from light-curve + radial-velocity solutions, independent of stellar-model
  isochrones. Representative public compilation: DEBCat (Southworth, the
  detached-eclipsing-binary catalogue) and equivalent peer-reviewed DEB tables.
- **Why first:** DEB masses are model-independent at the few-percent level and
  span roughly `0.2-30 M_sun`, covering several of the audited mass bins. Radii
  and effective temperatures from the same solutions also seed the future
  Stefan-Boltzmann audit (slate item 4) without re-ingestion.
- **Snapshot policy:** a future ingestion task must pin a single retrieval-date
  snapshot, commit or archive the raw table, and record a `raw_checksum_sha256`.
  No live fetch in any planning or audit task.
- **Provenance requirement:** each row must carry the primary publication
  reference for its mass and radius solution. Rows whose mass provenance cannot
  be recovered are refused.

### Source B (luminosity/context surface) — Gaia DR3 — `SML-SRC-CLASS-002`

Gaia DR3 supplies parallax (distance), photometry, effective temperature,
FLAME luminosity, metallicity proxy, and quality flags. It is cross-matched to
Source A by `source_id` (preferred) or by sky position within a documented
tolerance.

Declared query (ADQL against the Gaia DR3 TAP service — **declared, not run**):

```sql
SELECT
  gs.source_id,
  gs.ra, gs.dec,
  gs.parallax, gs.parallax_error, gs.parallax_over_error,
  gs.phot_g_mean_mag, gs.phot_bp_mean_mag, gs.phot_rp_mean_mag,
  gs.bp_rp,
  gs.ruwe,
  ap.teff_gspphot, ap.teff_gspphot_lower, ap.teff_gspphot_upper,
  ap.lum_flame, ap.lum_flame_lower, ap.lum_flame_upper,
  ap.mass_flame, ap.mass_flame_lower, ap.mass_flame_upper,
  ap.mh_gspphot, ap.mh_gspphot_lower, ap.mh_gspphot_upper,
  ap.evolstage_flame
FROM gaiadr3.gaia_source AS gs
JOIN gaiadr3.astrophysical_parameters AS ap
  ON gs.source_id = ap.source_id
WHERE gs.parallax_over_error > 10
  AND gs.ruwe < 1.4
  AND gs.phot_g_mean_flux_over_error > 50
  AND ap.lum_flame IS NOT NULL
```

`mass_flame` is selected **only** so the audit can label the model-inferred
control class; it is excluded from the benchmark mass axis per F1.

### Blocker condition carried forward

If a future task cannot pin a model-independent mass source that overlaps the
audited mass bins (Source A unavailable, redistribution terms unclear, or
sample too small to populate any bin), the task must **stop and write a blocker
review** at `docs/reviews/textbook-stellar-ml-source-baseline-blocker.md`
instead of substituting `mass_flame`. Substituting model-derived masses to
"unblock" the audit is forbidden (it reintroduces F1 circularity).

## Minimum Row Schema

Units are explicit. Luminosity in nominal Solar units (`L_sun = 3.828e26 W`,
IAU 2015 Resolution B3). Mass in nominal Solar units. `Teff` in kelvin. Radius
in nominal Solar units.

| Field | Meaning | Units | Required |
| --- | --- | --- | :-: |
| `row_id` | stable per-row identifier | — | yes |
| `gaia_source_id` | Gaia DR3 `source_id` (cross-match key) | — | yes |
| `mass` | stellar mass (model-independent for benchmark rows) | `M_sun` | yes |
| `mass_uncertainty` | 1-sigma mass uncertainty | `M_sun` | yes |
| `mass_class` | `dynamical_deb`, `dynamical_astrometric`, `model_inferred` | enum | yes |
| `luminosity` | bolometric luminosity | `L_sun` | yes |
| `luminosity_uncertainty` | 1-sigma luminosity uncertainty | `L_sun` | yes |
| `luminosity_source` | `gaia_lum_flame`, `deb_radius_teff`, `other` | enum | yes |
| `teff` | effective temperature | `K` | yes |
| `radius` | stellar radius (when from DEB solution) | `R_sun` | optional |
| `metallicity_proxy` | `[M/H]` proxy (`mh_gspphot` or DEB value) | dex | optional |
| `evolutionary_stage_flag` | main-sequence vs evolved indicator | enum | yes |
| `parallax_over_error` | Gaia parallax SNR (quality) | — | yes |
| `ruwe` | Gaia renormalised unit weight error (quality) | — | yes |
| `primary_reference` | publication for mass/radius solution | citation | yes |
| `inclusion_status` | `included`, `excluded:<reason>` | enum | yes |

**Uncertainty semantics:** uncertainties are 1-sigma. Asymmetric Gaia bounds
(`*_lower`/`*_upper`) must be preserved as a lower/upper pair and not silently
symmetrised. A row missing mass or luminosity uncertainty is excluded.

## Inclusion / Exclusion Filter Chain

Applied in order. The future audit task must report **pre-filter and
post-filter row counts at each step** (campaign required quality check).

1. **Mass-provenance filter** — keep only `mass_class IN (dynamical_deb,
   dynamical_astrometric)` for the benchmark axis. `model_inferred` rows are
   retained separately as the control class.
2. **Main-sequence restriction** — exclude rows whose `evolutionary_stage_flag`
   indicates a pre-main-sequence, subgiant, giant, or post-main-sequence state.
   The main-sequence definition (e.g. an `evolstage_flame` window or an
   HR-diagram locus cut) must be declared before counts are reported.
3. **Astrometric quality floor** — `parallax_over_error > 10` and `ruwe < 1.4`
   on the Gaia cross-match.
4. **Photometric quality floor** — `phot_g_mean_flux_over_error > 50`.
5. **Metallicity range** (optional axis) — restrict to a declared `[M/H]`
   window if a metallicity-controlled slice is run; otherwise record `[M/H]`
   per row for later stratification.
6. **Uncertainty completeness** — exclude rows missing mass or luminosity
   uncertainty.

Each exclusion records an explicit `inclusion_status: excluded:<reason>` so the
post-filter sample is reconstructable.

### Reporting fields (pre/post filter)

- `n_rows_raw` — rows returned by Source A snapshot before any filter.
- `n_rows_after_provenance`, `n_rows_after_mainseq`,
  `n_rows_after_quality`, `n_rows_after_uncertainty` — counts after each step.
- `n_rows_benchmark` — final benchmark-axis rows.
- `n_rows_control_model_inferred` — retained `model_inferred` control rows.
- `n_rows_per_mass_bin` — final count per baseline mass bin (below).

## Frozen Baseline

The audited baseline is the canonical piecewise main-sequence M-L relation as
summarised in Salaris & Cassisi (2005), *Evolution of Stars and Stellar
Populations* (historical origin: Russell 1914; Eddington 1924). Parameters are
**frozen and declared here**; in-task refitting on the full snapshot is
forbidden (campaign profile `forbidden_claims`).

| Mass bin (`M/M_sun`) | `L0_bin` | `alpha_bin` |
| --- | --- | --- |
| `< 0.43` | `0.23` | `2.3` |
| `0.43 - 2` | `1.0` | `4.0` |
| `2 - 55` | `1.4` | `3.5` |
| `> 55` | `~3.2e4` (linear regime) | `1.0` |

Notes:

- These are the published textbook values, not values fit inside this campaign.
  The boundary at `55 M_sun` and the linear high-mass regime follow the
  Eddington-luminosity-limited behaviour cited in the same reference.
- The future audit reports **per-bin** verdicts. A single global `alpha`
  estimate is explicitly out of scope.
- An alternate published parameterisation (e.g. Eker et al. 2018 segmented fits)
  may be substituted **only** if its source and segment boundaries are declared
  in the audit's pre-reveal package; it must not be fit from the snapshot.

## Holdout Policy

The split axis is **mass bin** (the same axis as the baseline's piecewise
structure), with metallicity as an optional secondary stratifier.

- **Train / reference bins:** `0.43 - 2 M_sun` and `2 - 55 M_sun` — the
  best-populated, best-understood main-sequence window. Used to confirm the
  audit machinery reproduces expected behaviour.
- **Holdout (OOD) bins:** `< 0.43 M_sun` (low-mass, fully convective regime)
  and `> 55 M_sun` (high-mass, radiation-pressure-dominated regime). These are
  the out-of-distribution slices where textbook breakdowns are documented and
  where the audit has falsification value.
- **Metallicity stratification (optional):** within each mass bin, rows may be
  split by `[M/H]` quartile to expose metallicity-driven residual structure;
  the quartile boundaries are declared from the post-filter sample before any
  metric runs.
- No row is moved between train and holdout after counts are reported. The
  pre/post-filter `n_rows_per_mass_bin` fields freeze the split.

This policy keeps the convective-radiative boundary (`~0.43 M_sun`) and the
upper-MS / Eddington regime (`~55 M_sun`) on the holdout side, which is where
the campaign expects the cleanest OOD failure map.

## Verification-Gate Slate

The future audit runner must apply each gate and record `PASS` / `FAIL` with a
numeric margin (campaign required quality check). Tolerances are declared here
so the audit cannot tune them post hoc.

| Gate | Test | Per-bin tolerance (declared) |
| --- | --- | --- |
| **G1 Dimensional consistency** | `L0_bin * (M/M_sun)^alpha_bin` is dimensionless in Solar units; both sides reduce to `L_sun`. | exact (structural) |
| **G2 Monotonicity** | predicted `L` strictly increases with `M` within each bin. | no decreasing interval |
| **G3 Low-mass limiting behaviour** | in `< 0.43 M_sun`, baseline does not over-predict `L`; relative residual sign and magnitude reported. | median relative residual within `+/- 0.3 dex` |
| **G4 High-mass limiting behaviour** | in `> 55 M_sun`, near-linear `L ~ M` (Eddington-limited) holds; super-linear slope flagged. | fitted log-slope within `1.0 +/- 0.4` |
| **G5 Convective-radiative boundary alignment** | baseline segments are continuous (no large jump) across the `~0.43 M_sun` boundary. | `< 0.15 dex` discontinuity at boundary |
| **G6 Per-bin tolerance band** | fraction of bin rows whose baseline-relative residual falls inside the declared band. | report fraction at `0.1 dex` and `0.2 dex` bands |

Every interpreted bin must also carry **at least one matched control or
deterministic negative control** (campaign required quality check). The
suggested controls:

- a **null baseline** (per-bin median `log L`) the power-law must beat to be
  non-trivial;
- the **`model_inferred` control class** (`mass_flame` rows) reported
  separately to make the F1 circularity visible — it is expected to look
  artificially good and must not be read as evidence for the formula.

## Reuse for the Stefan-Boltzmann Audit (slate item 4)

The DEB sample (Source A) carries measured radii and effective temperatures,
and Gaia supplies independent luminosities. The same pinned snapshot therefore
seeds the future Stefan-Boltzmann audit (`L = 4 * pi * R^2 * sigma * Teff^4`)
without re-ingestion. A future task should share, not duplicate, the Source A
snapshot.

## What This Plan Does Not Do

- It does not fetch Gaia DR3, DEBCat, or any external data.
- It does not pin a snapshot checksum or retrieval date (the ingestion task's
  job).
- It does not ingest, score, or fit any row.
- It does not compute residuals, slopes, or any metric.
- It does not register a prediction, promote a claim, or assign a per-slice
  verdict to the formula.
- It does not infer composition, evolutionary fate, habitability, or any
  application-domain interpretation.
- It does not make a universal statement about the mass-luminosity relation.

## Stop Conditions Carried Forward

A future ingestion or audit task must stop and surface a blocker when:

- no model-independent mass source can populate the audited mass bins (do not
  substitute `mass_flame`);
- a source omits per-row mass provenance or uncertainty semantics;
- the main-sequence definition cannot be applied deterministically;
- redistribution terms for the mass source are unclear;
- the task requests a global single-`alpha` fit or any in-task baseline refit;
- the task requests universal-law, discovery, or application-domain wording.

## Limitations

- The recommended Source A (DEBs) is model-independent but **sample-limited**;
  the `> 55 M_sun` holdout bin may be sparsely populated, which a future task
  must report honestly rather than backfilling with model-derived masses.
- The frozen baseline is one canonical published parameterisation; an alternate
  published set may be substituted under the declared-source rule but never
  fit from the snapshot.
- This plan declares an ADQL query shape, not a pinned snapshot; column
  availability must be re-verified against the live Gaia DR3 schema at
  ingestion time.
- Metallicity stratification is optional and may be deferred if the cross-match
  yields too few rows per quartile.

## Verdict

`PARTIALLY_VALID` (planning scaffold). The source query, row schema, filter
chain, frozen baseline, holdout policy, and verification-gate slate are now
reviewable in advance. One material design constraint was resolved: the naive
Gaia-only mass axis is inadmissible (F1 circularity), so the recommended first
sample is reshaped to a model-independent dynamical-mass source with Gaia as the
luminosity/context surface. No snapshot is pinned, no metric is run, and no
formula claim is made. The next step is a maintainer-approved pinned-snapshot
ingestion task targeting `SML-SRC-CLASS-001` (model-independent masses)
cross-matched to `SML-SRC-CLASS-002` (Gaia DR3), with no metric computation in
the same task.

## Cross-References

- `../textbook-formula-audit.md` — campaign charter and guardrails
- `../../../campaign_profiles/textbook-formula-audit.yaml` — autonomy contract
- `../../notes/textbook-formula-audit-candidate-list.md` — candidate slate
- `../../../tasks/proposals/20260528-roman-stellar-mass-luminosity-ood-source-baseline-planning.yaml` — accepted proposal
- `../../result-promotion-protocol.md` — promotion-tier policy
- `../../research-quality-gate.md` — shared quality gate
