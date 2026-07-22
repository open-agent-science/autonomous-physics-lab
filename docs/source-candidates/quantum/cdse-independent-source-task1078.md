# Independent CdSe Direct-Row Source Scout

Task: `TASK-1078`
Campaign: Quantum Size Effects

## Verdict

`STOP_NO_INDEPENDENT_ROUTE`

Five candidate publications were reviewed and none satisfies the frozen route
gate: independent sample provenance, at least six sample-resolved direct size
plus optical observations on one property axis, stable source bytes, usable
rights, and explicit uncertainty and morphology semantics.

No candidate is selected. No values, publisher bytes, source-manifest entry,
dataset rows, model fit, or score were created.

## Admission Gate

A route is eligible only when all of the following are true before extraction:

1. The source reports at least six distinct CdSe samples with both a direct
   measured size axis and one clearly named optical property axis.
2. Size is not inferred from the same optical relation later being tested.
3. Absorption, emission, and bandgap identities stay separate.
4. The article or supplement has stable retrievable bytes and a future
   SHA-256 pinning route.
5. Reuse terms permit a factual extraction, and the future ledger can preserve
   uncertainty and morphology semantics.
6. Figure-only evidence is eligible only when both axes can be calibrated and
   a two-pass extraction can be frozen before points are read.

The existing Norris-Bawendi, Murray, and Yu pathways were not reopened. This
scout evaluates a distinct bounded slate.

## Candidate Ledger

| Candidate | DOI / version | Artifact class | Metadata-only candidate count | Rights posture | Kim-2020 overlap | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| Lim, Schleife, and Smith (2017), *Optical determination of crystal phase in semiconductor nanocrystals* | [10.1038/ncomms14849](https://doi.org/10.1038/ncomms14849), version of record plus [publisher SI](https://static-content.springer.com/esm/art%3A10.1038%2Fncomms14849/MediaObjects/41467_2017_BFncomms14849_MOESM559_ESM.pdf) | Open article and tabular SI | 10 optical observations across two phase series; 0 direct measured size-plus-optical pairs | CC BY 4.0 | Same material only; distinct publication and phase-series provenance | Reject: the tabulated optical transition is used as a size proxy; no direct sample-resolved measured size table clears the gate. |
| Allahverdi (2023), *Optical Detection of Cadmium Selenide Quantum Dots via Absorption Spectroscopy and Transmission Electron Microscopy* | [10.20290/estubtdb.1096269](https://doi.org/10.20290/estubtdb.1096269), [institutional article record](https://dergipark.org.tr/en/pub/estubtdb/article/1096269) | Article body, spectra, and limited TEM figure | 6 optical samples; 1 sample has a direct TEM size comparison | Primary article is retrievable; an explicit reusable-data license was not verified | Same material only; distinct synthesis series | Reject: most sizes are calculated from the Yu absorption relation, so the six-sample surface is calibration-derived rather than direct. |
| Poudyal et al. (2025), *Size-dependent fluorescence properties of CdSe quantum dots* | [10.1016/j.ssc.2025.115993](https://doi.org/10.1016/j.ssc.2025.115993), [publisher version](https://www.sciencedirect.com/science/article/pii/S0038109825001681) | Publisher article | 3 samples; 0 verified direct measured size-plus-optical pairs | Elsevier version of record; no reusable open license verified | Same material only; distinct publication | Reject: below six samples and reported sizes are absorption-calibration estimates. |
| Kashyout et al. (2012), *CdSe Quantum Dots for Solar Cell Devices* | [10.1155/2012/952610](https://doi.org/10.1155/2012/952610), [publisher version](https://onlinelibrary.wiley.com/doi/10.1155/2012/952610) | Open article with body table | 4 sample rows; 0 verified direct measured size-plus-optical pairs | Article states an attribution license | Same material only; distinct synthesis series | Reject: below six samples and the size entries are calculated from the absorption sizing relation. |
| Sharma et al. (2010), *Surfactant mediated optical properties of cytosine capped CdSe quantum dots* | [10.1016/j.matlet.2010.02.045](https://doi.org/10.1016/j.matlet.2010.02.045), [institutional author record](https://digitalcommons.mtu.edu/michigantech-p/6865/) | Publisher article plus institutional author copy | 3 direct size-plus-absorption samples | Institutional copy is retrievable; publisher redistribution terms require a fresh rights check | Same material only; distinct capped-sample series | Reject: direct size semantics are promising, but the series is below the six-sample admission floor. |

Counts above are source-structure metadata only. No energy, wavelength, size,
uncertainty, or fitted value was transcribed.

## Candidate-Specific Retrieval And Checksum Plans

### Lim 2017

- Retrieve the version-of-record HTML and publisher-hosted SI PDF.
- Record DOI, publication version, byte length, retrieval timestamp, and
  SHA-256 for both artifacts in a future source package.
- Exact blocker: the SI tables expose optical transition series and synthesis
  conditions, not six direct measured size-plus-optical sample pairs. Optical
  calibration cannot be relabelled as a direct size axis.

### Allahverdi 2023

- Retrieve the Dergipark versioned PDF from the institutional article record
  and pin its SHA-256 after a license review.
- Keep the absorption axis separate from any TEM morphology diagnostic.
- Exact blocker: direct TEM coverage exists for only one of the six optical
  samples; the remaining size labels are formula-derived.

### Poudyal 2025

- Use the DOI and PII as version identifiers; fetch publisher bytes only after
  access and reuse terms are resolved, then pin the exact artifact SHA-256.
- Exact blocker: three samples are below the coverage floor, and the size axis
  is derived from an optical sizing calibration.

### Kashyout 2012

- Retrieve the DOI-pinned version-of-record PDF, verify the article license on
  the fetched copy, and record its SHA-256 before any extraction.
- Exact blocker: four rows are below the coverage floor and use calculated,
  not independently measured, size entries.

### Sharma 2010

- Resolve whether future factual extraction should cite the publisher version
  or the institutional author copy, then checksum the reviewed artifact.
- Preserve TEM and XRD size semantics separately if a later source package is
  ever considered.
- Exact blocker: only three direct size-plus-absorption samples are exposed,
  below the six-sample minimum; publisher reuse terms also need review.

## Stop Rationale

Selecting Allahverdi merely because it has six optical samples would create a
circular benchmark: the size axis for most samples is generated by an optical
sizing relation. Selecting Sharma would preserve direct-size semantics but
would waive the predeclared sample-count floor. Neither exception is allowed.

The bounded search therefore stops without a route. A later scout should use a
new candidate slate and should prioritize a primary table or body-text series
with at least six microscopy-, scattering-, or diffraction-sized samples.

## Scope And Limitations

This is a source-admissibility decision, not evidence about CdSe size effects.
It does not validate a size law, support cross-source transfer, recommend a
material, or say anything about device performance. Candidate counts do not
substitute for row-level source review.

## Output Routing

- Canonical destination: this source-candidate adjudication.
- Source manifest: unchanged because no candidate cleared admission.
- Dataset impact: none; no values or rows were created.
- Gate A / Gate B: not attempted and not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: no reviewed candidate combines six direct
  size-plus-optical samples with stable bytes, rights, and preserved semantics.
