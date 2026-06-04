# Norris-Bawendi 1996 CdSe Digitization Preflight Package

Task: `TASK-0563`
Source ID: `norris-bawendi-1996-prb-cdse-band-edge`
DOI: `10.1103/PhysRevB.53.16338`
Package status: `BLOCKED_PENDING_LEGITIMATE_SOURCE_COPY_AND_TOOL_RUN`

## Scope

This package prepares the deterministic digitization artifact shape for the
Norris-Bawendi 1996 CdSe source path. It contains no source figure, PDF, raster
panel, extracted coordinates, converted values, or `qd-*.yaml` rows.

The source is already verified as `figure_derived`; a row-producing pass must
therefore use a WebPlotDigitizer-class tool and preserve axis calibration,
extracted point coordinates, uncertainty notes, and point-level inclusion
state.

## Source Locator

- Citation: Norris, D. J.; Bawendi, M. G. (1996), "Measurement and Assignment
  of the Size-Dependent Optical Spectrum in CdSe Quantum Dots," Physical Review
  B 53, 16338-16346.
- DOI: `10.1103/PhysRevB.53.16338`
- DOI URL: `https://doi.org/10.1103/PhysRevB.53.16338`
- Material: CdSe quantum dots
- Expected source class: figure-derived optical spectrum / size-series surface
- Candidate property axes: `absorption_peak_eV`, `bandgap_eV`

## Current Blockers

This package is not row-ready because the following conditions are still
missing:

- legitimate source copy available to the curator;
- explicit redistribution decision for any source panel or intermediate image;
- target figure/panel confirmation;
- WebPlotDigitizer-class tool run and tool version;
- axis calibration anchors;
- extracted point coordinates;
- coordinate and publication uncertainty notes;
- per-point inclusion/exclusion decision;
- reviewer replay of the extraction.

Do not use this package to unblock row curation or benchmarking until the CSV
templates are replaced with real, reviewed extraction artifacts.

## Artifact Files

The current files are templates only:

- `axis_calibration_template.csv`
- `extracted_points_template.csv`
- `extraction_ledger_template.csv`

Expected row-producing filenames after a future approved tool run:

- `axis_calibration.csv`
- `extracted_points.csv`
- `extraction_ledger.csv`
- `notes.md`

Do not commit APS PDFs, raw figure images, screenshots, or rasterized panels
unless redistribution permission is explicit.

## Point-State Vocabulary

Use exactly these point states in a future extraction ledger:

- `included`: calibrated point is admissible for a later row-curation task;
- `excluded_overlap`: plotted point cannot be read separately from overlap;
- `excluded_axis_ambiguous`: axis value or unit is not independently readable;
- `excluded_source_ambiguous`: point is attributed to a prior source that is not
  separately registered;
- `excluded_model_or_assignment`: point is assignment-derived/model-only rather
  than direct measurement;
- `excluded_uncertainty`: coordinate or publication uncertainty is too large or
  unavailable;
- `review_needed`: point requires human review before row curation.

## Uncertainty Notes

A future extraction must record both:

- digitization read uncertainty from the calibrated plot coordinates; and
- publication/source uncertainty or an explicit `absent_in_source` note.

If uncertainty cannot be recorded per point, the point must remain excluded or
`review_needed`; it must not become a measurement row by default.

## Guardrails

- No LLM-estimated graph coordinates.
- No values recalled from memory.
- No polynomial-generated or fitted-curve-derived rows.
- No quantum-size-effect benchmark run from this package.
- No synthesis, device, biomedical, prediction, claim, result, or knowledge
  artifact.
