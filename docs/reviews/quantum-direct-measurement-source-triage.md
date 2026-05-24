# Quantum Direct-Measurement Source Triage

**Task:** TASK-0298
**Status:** review (no row-level dataset curation performed)
**Inputs reviewed:**

- `data/quantum_dots/source_manifest.yaml`
- `data/quantum_dots/qd-0001-yu-2003-absorption.yaml`
- `data/quantum_dots/qd-0002-moreels-2009-pbs-absorption.yaml`
- `physics_lab/schemas/quantum_dot_size_effect.schema.json`
- `docs/quantum-size-effect-holdout-protocol.md`
- `docs/reviews/quantum-size-row-level-data-readiness-for-baseline.md`
- `docs/reviews/quantum-size-yu-2003-row-level-seed-review.md`
- `docs/reviews/quantum-size-moreels-2009-pbs-row-level-extension-review.md`
- `docs/reviews/quantum-size-source-manifest-seed-review.md`
- `docs/campaigns/quantum-size-effects.md`
- `tasks/TASK-0291-curate-quantum-direct-measurement-absorption-seed.yaml`
- `tasks/TASK-0292-curate-quantum-direct-measurement-band-edge-seed.yaml`

## Scope

This triage helps the next Quantum Size Effects dataset agents decide which
registered sources are tractable measurement-grade inputs for TASK-0291 (direct
absorption seed) and TASK-0292 (direct band-edge seed). It does not curate any
row, fetch live data, redistribute tables, update claims, or unblock TASK-0225.

The triage assumes the row-level readiness gate result from TASK-0283:
calibration-derived rows alone keep TASK-0225 blocked, and any direct-
measurement seed must distinguish primary observations from sizing polynomials
or composition-confounded photoluminescence references.

## Classification Vocabulary

Each registered source is classified along two axes:

1. **Provenance class**
   - `likely_direct_measurement` — primary TEM + spectroscopy / electrochemistry
     observations are reported as discrete data points in tables or figures.
   - `calibration_derived` — the public surface is a fitted sizing polynomial
     or empirical formula, even if the underlying paper also reports discrete
     measurements behind the fit.
   - `theory_or_model_only` — no primary measurement data; theoretical model
     parameters and equations only.
   - `core_shell_or_confounded` — primary measurements exist but the material
     family or property semantics confound a single-material residual axis for
     the first benchmark.
   - `unsuitable` — none of the above categories apply, or the source is not
     usable for any first-benchmark axis.
2. **Extractable form**
   - `table_values` — discrete tabulated (size, energy) rows.
   - `figure_points` — discrete points readable from a published figure with a
     reasonable digitisation pass.
   - `calibration_formula` — only a closed-form sizing relation is exposed.
   - `model_equation` — theoretical equation, not measurement data.

The classifications below are based on the existing review notes for qd-0001
and qd-0002, the source-manifest metadata, and publicly available abstracts.
A curator running TASK-0291 or TASK-0292 must verify the actual table or
figure structure inside each publication before extracting rows.

## Per-Source Triage

### S1. `yu-2003-cm-absorption`

- Citation: Yu, Qu, Guo, Peng (2003). *Chem. Mater.* 15, 2854–2860.
  DOI [10.1021/cm034081k](https://doi.org/10.1021/cm034081k).
- Manifest property: `absorption_peak_eV`. Materials: CdTe, CdSe, CdS.
- Manifest measurement_type: `optical_absorption`.
- Current dataset use: qd-0001 as a calibration-derived seed using the
  published sizing polynomials.
- **Provenance class:** `likely_direct_measurement` *and* `calibration_derived`.
  The publication reports both the empirical sizing polynomials and the
  underlying first-exciton absorption peak wavelengths versus TEM-measured
  diameters for the size series. qd-0001 currently exposes only the polynomial
  evaluation.
- **Extractable form:** `table_values` for the per-material absorption peak
  positions tied to TEM diameters; `figure_points` as a fallback if a value is
  only shown in a figure panel and not duplicated in a table.
- **Caveats:**
  - Curator must record `source_table_ref` for each direct row and explicitly
    distinguish a direct table value from any polynomial-derived value.
  - Some diameters may only appear inside a figure; figure-derived rows must
    note the digitisation method and quantisation uncertainty.
  - Reported diameters carry TEM uncertainty; curator should preserve the
    uncertainty as reported, not flatten it.
- **First-attempt recommendation:** **YES** for TASK-0291. Yu 2003 is the
  single best direct-absorption candidate: three independent materials, a
  bounded size range, and a published baseline already in qd-0001 that the new
  seed would intentionally *not* reuse for residual computation. A re-curated
  direct seed (qd-0003 or similar) should keep qd-0001 in place as an explicit
  calibration-derived comparison surface and not overwrite it.

### S2. `moreels-2009-acs-nano-pbs-absorption`

- Citation: Moreels et al. (2009). *ACS Nano* 3, 3023–3030.
  DOI [10.1021/nn900863a](https://doi.org/10.1021/nn900863a).
- Manifest property: `absorption_peak_eV`. Materials: PbS.
- Manifest measurement_type: `optical_absorption`.
- Current dataset use: qd-0002 as a calibration-derived seed using Eq. 4 with
  the published constants.
- **Provenance class:** `likely_direct_measurement` *and* `calibration_derived`.
  The publication provides Eq. 4 as a fit; the underlying PbS size series
  reports first-exciton absorption energies versus TEM diameters as discrete
  values, with additional element-analysis context that should be ignored for
  the residual axis.
- **Extractable form:** likely `table_values` for the size series; possibly
  `figure_points` where a value is shown only in a panel.
- **Caveats:**
  - Curator must keep the `absorption_peak_eV` residual axis clean and
    exclude concentration calibration, element analysis, and extinction-
    coefficient fields from row-level data.
  - PbS first-exciton transitions are very size-sensitive at small diameters;
    nominally identical "small" sizes from different syntheses should not be
    treated as duplicates.
- **First-attempt recommendation:** **secondary candidate** for TASK-0291.
  Useful for broadening material coverage beyond cadmium chalcogenides once Yu
  2003 has been re-curated as a direct seed. Should not be the first attempt
  if the curator only has time for one source; the gate analysis already
  notes that PbS-only material holdouts are structurally weaker than the Cd-
  chalcogenide-versus-PbS split.

### S3. `jasieniak-2011-acs-nano-band-edge`

- Citation: Jasieniak, Califano, Watkins (2011). *ACS Nano* 5, 5888–5902.
  DOI [10.1021/nn201681s](https://doi.org/10.1021/nn201681s).
- Manifest property: `bandgap_eV`. Materials: CdSe, CdTe, PbS, PbSe.
- Manifest measurement_type: `electrical_transport` (band-edge spectroscopy;
  see manifest note about preserving derivation from valence and conduction
  band-edge measurements).
- Current dataset use: none. No qd-*.yaml file currently uses this source.
- **Provenance class:** `likely_direct_measurement`. Band-edge values are
  reported as primary measurements via photoelectron / electrochemical
  techniques; bandgap is the derived `Ec − Ev`.
- **Extractable form:** mixed `table_values` and `figure_points`. Several
  panels report band-edge positions versus size for each material family;
  some discrete size points are read from figures rather than tabulated.
- **Caveats:**
  - Any row exposed as `property_kind: bandgap_eV` must carry provenance fields
    showing the underlying `E_VB` and `E_CB` and the method used (PESA, CV, or
    similar). The manifest entry already records this requirement.
  - Mixing this source with Yu 2003 or Moreels 2009 on a single residual axis
    is forbidden by the holdout protocol; band-edge rows belong to a separate
    dataset surface and a separate first-benchmark configuration.
  - Curator must not relabel optical absorption or photoluminescence peaks
    from other sources as bandgap to inflate row count.
- **First-attempt recommendation:** **YES** for TASK-0292. Jasieniak 2011 is
  currently the only registered band-edge source. If discrete band-edge rows
  for at least one material family can reach the ≥6-row threshold with clean
  provenance, this source unlocks the alternate property axis. If not, the
  task should produce a review-only note (per its requirements) rather than
  fabricate a dataset file.

### S4. `dabbousi-1997-jpcb-emission`

- Citation: Dabbousi et al. (1997). *J. Phys. Chem. B* 101, 9463–9475.
  DOI [10.1021/jp971091y](https://doi.org/10.1021/jp971091y).
- Manifest property: `emission_peak_eV`. Materials: CdSe/ZnS core-shell.
- Manifest measurement_type: `photoluminescence`.
- Current dataset use: none. Manifest entry already marks this source
  `excluded`.
- **Provenance class:** `core_shell_or_confounded`. Even though the
  photoluminescence values are direct measurements, the CdSe/ZnS core-shell
  composition and shell passivation confound a single-material residual axis
  for the first size-effect benchmark.
- **Extractable form:** `table_values` and `figure_points` exist, but they are
  not the right axis for the first benchmark.
- **First-attempt recommendation:** **NO**. Keep excluded. Preserve as an
  explicit reference for the campaign's emission-versus-absorption discipline,
  not as a row source. A future task explicitly scoped to core-shell emission
  semantics could revisit it, but that is out of scope for TASK-0291 and
  TASK-0292.

### S5. `brus-1984-jcp-model-reference`

- Citation: Brus (1984). *J. Chem. Phys.* 80, 4403–4409.
  DOI [10.1063/1.447218](https://doi.org/10.1063/1.447218).
- Manifest property: `bandgap_eV`. Materials: CdS, CdSe.
- Manifest measurement_type: `theoretical_calculation`.
- Current dataset use: none. Manifest entry already marks this source
  `excluded`.
- **Provenance class:** `theory_or_model_only`.
- **Extractable form:** `model_equation`. No primary measurement table.
- **First-attempt recommendation:** **NO**. Keep excluded. Useful only as
  baseline-model provenance in TASK-0225; never as curated row data.

## Summary Table

| Source ID | Property axis | Provenance class | Extractable form | First-attempt for TASK-0291 / TASK-0292 |
|-----------|---------------|------------------|------------------|------------------------------------------|
| `yu-2003-cm-absorption` | absorption_peak_eV | likely_direct_measurement (also calibration_derived) | table_values; figure_points fallback | **TASK-0291 first attempt** |
| `moreels-2009-acs-nano-pbs-absorption` | absorption_peak_eV | likely_direct_measurement (also calibration_derived) | table_values; figure_points fallback | TASK-0291 secondary candidate |
| `jasieniak-2011-acs-nano-band-edge` | bandgap_eV (derived from band edges) | likely_direct_measurement | mixed table_values and figure_points | **TASK-0292 first attempt** |
| `dabbousi-1997-jpcb-emission` | emission_peak_eV | core_shell_or_confounded | n/a for first benchmark | keep excluded |
| `brus-1984-jcp-model-reference` | bandgap_eV (model) | theory_or_model_only | model_equation | keep excluded |

## Recommended Order Of Work

1. **TASK-0291 (absorption seed).** Start with Yu 2003. Re-curate the
   per-material first-exciton absorption peak rows as a new direct-measurement
   dataset file (for example `qd-0003-yu-2003-direct-absorption.yaml`), keep
   qd-0001 in place as the existing calibration-derived seed, and record per-
   row provenance so the readiness gate can distinguish the two.
2. **TASK-0291 follow-up.** If Yu 2003 yields a clean ≥6-row direct seed and
   time allows, add a Moreels 2009 PbS direct-measurement extension to broaden
   material coverage. If not, leave the PbS direct extension to a later task.
3. **TASK-0292 (band-edge seed).** Attempt Jasieniak 2011 with strict
   provenance: each row must carry `E_VB`, `E_CB`, derived `E_g`, and the
   measurement method. If discrete rows cannot reach ≥6 with clean provenance,
   produce the review-only note described in TASK-0292 and do not fabricate a
   dataset file.
4. **TASK-0293 (readiness gate re-run).** Defer until at least one of the
   above direct-measurement seeds lands; then re-run the gate per
   `docs/reviews/quantum-size-row-level-data-readiness-for-baseline.md`.

## Manifest Update Posture

This task makes no manifest edits. The current `source_manifest.yaml` is
consistent with the triage above:

- the three accepted sources (Yu 2003, Moreels 2009, Jasieniak 2011) remain
  the prioritised candidates;
- the two excluded sources (Dabbousi 1997, Brus 1984) remain excluded for the
  first benchmark with explicit rationales;
- no new candidate source is added to the manifest in this triage; new
  candidates should arrive through their own reviewed manifest update with a
  separate license-and-pinning note.

## What This Triage Does Not Authorise

- It does not fetch live data, scrape tables, or store raw figure files in
  the repository.
- It does not add or modify `qd-*.yaml` row-level data files.
- It does not unblock TASK-0225 or move it from `BLOCKED`.
- It does not promote any sandbox evidence to a claim, knowledge entry, or
  canonical result.
- It does not authorise device, synthesis, or biomedical content.
- It does not justify averaging residuals across `absorption_peak_eV`,
  `emission_peak_eV`, and `bandgap_eV` property axes.

## Limitations

- The provenance classifications above are based on review notes, manifest
  metadata, and publicly known abstracts. A TASK-0291 or TASK-0292 curator
  must verify the actual table and figure structure inside each publication
  before extracting rows.
- The recommendation that Yu 2003 yields ≥6 clean direct-absorption rows is a
  high-likelihood expectation, not a guarantee; the curator may discover that
  the discrete rows are fewer than expected or are presented only via figures.
- The Jasieniak 2011 band-edge recommendation depends on whether the
  publication exposes enough discrete sizes per material to satisfy the
  ≥6-row threshold without mixing materials.
- This triage does not estimate measurement uncertainty for any future row.

## Verdict

`PARTIALLY_VALID` — the existing source manifest already contains tractable
direct-measurement candidates for both TASK-0291 (Yu 2003 as first attempt,
Moreels 2009 as secondary) and TASK-0292 (Jasieniak 2011 as first attempt).
No additional sources are required to attempt the next direct-measurement
seeds, but the underlying row-level curation work and provenance discipline
remain non-trivial and must respect the gate constraints from TASK-0283.
