# Quantum Next Direct-Source Scout

**Task:** `TASK-0988`
**Campaign:** Quantum Size Effects
**Scope:** one new direct-measurement source route after `RESULT-0029`
**Verdict:** `SOURCE_LIMITED_MONITOR`

## Scope And Non-Goals

This note evaluates exactly one source route that adds a new direct
measurement surface beyond the committed Almeida InP and Toufanian ZnSe
surfaces. It records source identity, measurement semantics, access, reuse,
and row-readiness only.

This scout does not download or vendor source bytes, transcribe values, create
`qd-*.yaml` rows, digitize figures, fit a size law, rerun the ZnSe/InP
transfer, or create a `RESULT`, `PRED`, `CLAIM`, or `KNOW` artifact.

## Selected Route

**Kim et al. (2020), "Influence of Size and Shape Anisotropy on Optical
Properties of CdSe Quantum Dots"**

| Field | Assessment |
| --- | --- |
| Source locator | DOI `10.3390/nano10081589`; publisher article: <https://www.mdpi.com/2079-4991/10/8/1589>; PMC mirror: <https://pmc.ncbi.nlm.nih.gov/articles/PMC7466547/> |
| Material | CdSe; independent source surface, separate from Almeida InP and Toufanian ZnSe |
| Measurement type | Optical absorption with HRTEM size characterization |
| Property axis | Candidate `absorption_peak_eV`; emission is a separate axis and is not part of this route |
| Size axis | HRTEM-derived average particle diameter in nm; morphology must remain `unknown_non_spherical` because the paper reports shape anisotropy |
| Likely row surface | Four growth-time samples; exact row count and per-row provenance require a later source-artifact review |
| Data surface | HRTEM images and size histograms in Figure 1; absorption/fluorescence spectra in Figure 3; differential-absorption transition extraction in Figure 4; size-dependent transition plot in Figure 5; no printed row table was confirmed in the article text |
| Access and reuse | Open access; the article states a Creative Commons Attribution (CC BY) license. Exact figure and any supplementary-file reuse terms must still be checked at intake |
| Expected provenance | Direct size measurement plus experimentally observed optical transition features processed from spectra; not a sizing-equation calibration and not a device-context route |

## Evidence Checked

The primary article reports that HRTEM and XRD were used to characterize
size-dependent CdSe structure, and that electronic transition energies were
extracted from differential-absorption spectra. It identifies four samples
with different growth times and presents their size distributions and optical
spectra on Figures 1, 3, and 4. The article also explicitly reports shape
anisotropy, so a future row task must not silently coerce the samples to a
spherical geometry.

The article is a plausible direct-measurement route because the size axis comes
from microscopy and the optical axis comes from measured absorption spectra.
The spectral feature extraction is an analysis step, but it is not the same as
back-solving particle size from an optical sizing equation. The source is not
yet row-ready because the source surfaces are figure/text based, the exact
source artifact has not been checksum-pinned in this repository, and the
per-row measurement and uncertainty ledger has not been reviewed.

## Admissibility And Limits

| Gate | Decision |
| --- | --- |
| New information after `RESULT-0029` | Pass: new CdSe source and new direct HRTEM/optical surface |
| Direct size measurement | Plausible: HRTEM histogram-based size characterization |
| Optical property semantics | Plausible for `absorption_peak_eV`; keep emission separate |
| Calibration-derived risk | Not identified for the size axis; verify that no model-derived size is copied during curation |
| Device-context contamination | None identified; this is a material characterization study, not a device/laser route |
| License | CC BY stated for the article; exact artifact and figure terms still require intake verification |
| Machine-readable row readiness | Not established; figures/text require a deterministic extraction package |
| Current benchmark eligibility | Not eligible for rows, holdout use, or metrics |

## Required Follow-Up Shape

If the maintainer accepts this route, the next task should be a bounded,
value-blind source-artifact package:

1. Pin the exact article and any permitted supplementary or figure files and
   record SHA-256 only for files actually obtained under a confirmed reuse
   posture.
2. Record axis calibration, extraction-tool version, sample identifiers,
   morphology, diameter semantics, and per-point uncertainty for the HRTEM and
   absorption surfaces.
3. Keep `absorption_peak_eV`, `emission_peak_eV`, and any bandgap interpretation
   in separate property axes.
4. Preserve the reported anisotropy; do not convert to an equivalent sphere
   without a reviewed geometry rule.
5. Add rows only after the source-artifact and row-readiness gates pass. A
   later benchmark task must separately predeclare its split, controls, and
   promotion route.

Until that follow-up passes, this route remains a monitor-only source lead.
It does not reopen the failed effective-mass transfer or authorize a new
correction search.

## Limitations

- No source bytes, screenshots, figures, or supplementary files were added.
- No numeric values were copied into repository data files.
- No checksum was fabricated or recorded for an un-fetched artifact.
- No dataset row, benchmark metric, transfer result, claim, or knowledge entry
  changed.
- The exact row count, uncertainty fields, and figure extraction precision
  remain to be established by a future source-artifact task.

## Output Routing Summary

- **Canonical destination:** source-readiness review note under `docs/reviews/`.
- **Review tier:** not applicable; this is source curation only.
- **Gate A:** not attempted.
- **Gate B:** not attempted.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Dataset impact:** none; `data/quantum_dots/` is unchanged.
- **Publication blocker:** deterministic source-artifact and row-readiness
  evidence are still required before any future curation.

## Verdict

`SOURCE_LIMITED_MONITOR`

## Sources

- Kim, S. H. et al. (2020), *Nanomaterials* 10(8), 1589:
  <https://doi.org/10.3390/nano10081589>
- Publisher full text and license statement:
  <https://www.mdpi.com/2079-4991/10/8/1589>
- PMC full-text mirror:
  <https://pmc.ncbi.nlm.nih.gov/articles/PMC7466547/>
