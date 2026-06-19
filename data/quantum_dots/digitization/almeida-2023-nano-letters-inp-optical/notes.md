# Almeida 2023 InP Sizing-Curve Digitization Notes

Task: `TASK-0797`
Source ID: `almeida-2023-nano-letters-inp-optical`
Status: `SIZE_AXIS_DIGITIZED__DETERMINISTIC_EXTRACTION__PENDING_REVIEWER_REPLAY`
Supersedes the blocker in `tool_run_blocker.md` (raster now available; extraction run).

## What changed

`TASK-0755` left the size axis blocked because the exact Figure 1b / SI Figure
S2b raster was unavailable. A maintainer-supplied local copy of the
**version-of-record Figure 2** asset is now available off-repository (the
sizing-curve figure: panel a absorbance + InP tetrahedron, panel b
`E1s vs Edge Length` and `E1s vs Volume`). The size axis is therefore digitized
here by a deterministic image-processing extractor instead of manual clicking.

## Source provenance

- Citation: Almeida, G.; van der Poll, L.; Evers, W. H.; Szoboszlai, E.; Vonk,
  S. J. W.; Rabouw, F. T.; Houtepen, A. J. "Size-Dependent Optical Properties of
  InP Colloidal Quantum Dots," Nano Letters 2023, 23 (18), 8697-8703.
- DOI: `10.1021/acs.nanolett.3c02630`
- License: Creative Commons Attribution 4.0 International (CC-BY 4.0),
  version-of-record, zero embargo (confirmed via PMC `PMC10540257` and Crossref,
  TASK-0741). Redistribution of attributed extracted data is permitted.
- Figure used: Figure 2, panel b (the `E1s vs Edge Length` / `E1s vs Volume`
  sizing curves; *This work* filled-triangle markers).
- Asset locator: `https://pubs.acs.org/cms/10.1021/acs.nanolett.3c02630/asset/images/large/nl3c02630_0001.jpeg`
- Asset SHA-256: `3b7a37c9c5b0377f0101288f91ea4a4ae27294ab3670c6b9489224969e68e2ce`
- The publisher figure asset is **not vendored** (only checksum + locator),
  consistent with the package's no-PDF-vendoring policy.

## Method (deterministic, replayable)

Extractor: `scripts/extract_almeida_sizing.py` (numpy + Pillow + scipy.ndimage).

1. Axis calibration from auto-detected frame lines and perpendicular tick bands;
   anchors recorded in `axis_calibration.csv` (linear axes; tick spacing even).
2. Marker detection: black-but-not-red mask, restricted to each E1s band, with
   the formula/annotation/legend regions excluded. A 3x3 binary erosion removes
   thin structure (error-bar lines, *Xu et al.* open-triangle outlines, text),
   leaving the solid *This work* filled-triangle cores; the most-solid core per
   E1s band is taken and its centroid mapped through the calibration.
3. Horizontal error bars measured as the gap-tolerant black-pixel span through
   each marker centroid.

This is a WebPlotDigitizer-class extraction. It does **not** use LLM-estimated
coordinates and does **not** substitute the published sizing formula
(`E = 1.33 + 9.128 L^-0.684`, `E = 1.33 + 1.219 V^-0.251`) for measured points;
the formula is recorded only as a cross-check column (`fit_e1s_crosscheck`).

## Cross-checks (all passed)

- Smallest dot extracted at edge length **1.50 nm**, matching the README text
  anchor (lambda1s 460 nm, "L = 1.5 nm, smallest dot").
- Edge length increases monotonically as E1s decreases (physical confinement).
- Cross-panel consistency via the regular-tetrahedron relation `V ~ 0.118 L^3`.
- Measured E1s (from marker y) matches the independently known E1s anchors
  (from `E1s = 1239.84 / lambda1s`) to <= 0.01 eV.
- Points sit on the published fit within data scatter (residuals <= 0.10 eV).

## Extracted values (Edge Length panel = primary, cleaner)

| lambda1s (nm) | E1s (eV) | edge length L (nm) | +/- (nm) |
| --- | --- | --- | --- |
| 460 | 2.695 | 1.50 | 0.18 |
| 480 | 2.583 | 1.99 | 0.27 |
| 510 | 2.431 | 2.54 | 0.49 |
| 550 | 2.254 | 2.76 | 0.40 |
| 580 | 2.138 | 3.13 | 0.09 |
| 620 | 2.000 | 4.10 | 0.46 |

The Volume panel (`extracted_points.csv`) is secondary: the mid-range markers
overlap and carry wide error bars, so derive volume from edge length where a
clean value is needed.

## QC flags / limitations

- `inclusion_status = included_flag_review` marks markers with low solid-core
  pixel count (the lambda1s 620 nm / E1s 2.0 edge-length point and one volume
  point) because the *This work* filled triangle overlaps an *Xu et al.* open
  triangle; the central value is consistent with the trend, fit, and the SI
  Figure S2b lambda620 histogram (~4 nm), but it needs visual confirmation.
- Error-bar widths are best-effort reads from a 987-px asset; central size
  values are robust, uncertainties are approximate.
- Provenance tier: `deterministic_figure_extraction`. `reviewer_replay_required`
  before these become canonical `qd-*.yaml` rows.

## Reviewer replay

Obtain the CC-BY asset at the locator above (verify SHA-256), then:

```
python3 scripts/extract_almeida_sizing.py \
    --image <asset> \
    --outdir data/quantum_dots/digitization/almeida-2023-nano-letters-inp-optical
```

Output CSVs must match byte-for-byte. Any drift opens a contested-extraction
note rather than a silent edit.

## No-claim scope

Source-curation / digitization only. No baseline metric, no size-effect model
fit, no RESULT/PRED/CLAIM, no quantum-dot design, synthesis, device, or
biomedical inference. Attribution on reuse: data adapted from Almeida et al.,
Nano Letters 2023, 23, 8697-8703 (doi:10.1021/acs.nanolett.3c02630), CC-BY 4.0.
