# TASK-1052: Kim 2020 CdSe size and optical extraction

## Scope

This task executed the frozen
[extraction contract](../../../data/quantum_dots/source_artifacts/kim-2020-nanomaterials-cdse-optical/extraction_contract.yaml)
for the four Kim et al. 2020 CdSe samples. It re-pinned the source, transcribed
the four text-stated HRTEM summaries, and ran two independent Figure 3(a)
WebPlotDigitizer sessions for the absorption and fluorescence peak positions.

The canonical task output is the
[extraction ledger](../../../data/quantum_dots/digitization/kim-2020-nanomaterials-cdse-optical/extraction_ledger.yaml).
No source PDF, embedded JPEG, stitched figure, or panel crop is committed.

## Input references

- Task: `TASK-1052`.
- Source ID: `kim-2020-nanomaterials-cdse-optical`.
- DOI: `10.3390/nano10081589`.
- Frozen preflight:
  [kim-2020-cdse-extraction-preflight.md](kim-2020-cdse-extraction-preflight.md).
- Source intake:
  [kim-2020-cdse-source-artifact.md](kim-2020-cdse-source-artifact.md).
- Frozen machine contract:
  [extraction_contract.yaml](../../../data/quantum_dots/source_artifacts/kim-2020-nanomaterials-cdse-optical/extraction_contract.yaml).

## Source re-pinning

All three official objects were fetched again on 2026-07-15 UTC before any
value extraction. Every object remained byte-identical to TASK-1043.

| Artifact | Bytes | SHA-256 | Outcome |
| --- | ---: | --- | --- |
| Version-of-record PDF | 1,368,239 | `2dab8a6b4db18af88f7175ac0773747fe1aeb15d88f951a4a8536cdc2dd73edb` | exact match |
| Europe PMC JATS | 62,029 | `6642fed609ad6540b61ca856d293d2b469c5ed7be9323479c9b76b023f668244` | exact match |
| Crossref snapshot | 12,087 | `6b3a36ba7160d7c3d12a54bc64b846ec358d569ee562e778e8ac64eca6526e9c` | exact match |

## Method

`pdfimages` showed that Figure 3 is stored on PDF page 5 as two vertically
adjacent JPEG objects. Objects 35 and 36 were extracted outside the repository,
appended top-to-bottom without resampling, and loaded into WPD as a 1478 by 913
pixel composite with SHA-256
`100e9f4cb1cd82aa18033523edd382e146115f6b60be4317e441ccd6b09567e7`.
An origin-preserving Figure 3(a) crop (`650x913+0+0`) was also generated as a
checksum cross-check; it is 650 by 913 pixels with SHA-256
`975fd9d33a14106dc7b42c8917aeeba86c591ca4c4c49087cd3c99dc54585c12`.

The composite was loaded into the official `https://apps.automeris.io/wpd4/`
build, which identifies itself as WebPlotDigitizer 4.8. The image stayed on localhost.
Two fresh sessions were used:

- Pass A: printed x ticks 1.8 and 3.0 eV; left panel-frame endpoints for a
  diagnostic 0-to-1 y normalization.
- Pass B: printed x ticks 2.1 and 2.7 eV; right panel-frame endpoints for the
  same diagnostic y normalization.
- Each pass used separate absorption and emission datasets and recorded one
  point per sample and curve role.

The tests in
[test_quantum_size_effects.py](../../../tests/test_quantum_size_effects.py)
recompute observation counts, sample pairing, required point provenance,
source checksums, pass agreement, blocker state, and the licence declaration.
No fit, residual metric, split assignment, or physical-law test was run.

## Extracted surface

The HRTEM values are text-stated mean diameter plus size-distribution
dispersion, not standard errors. Optical values below are diagnostic means of
the two WPD sessions; the parenthesized value is the article-text cross-check.

| Sample | HRTEM summary (nm) | Absorption peak (eV) | Emission peak (eV) | Optical status |
| --- | ---: | ---: | ---: | --- |
| CdSe-1 | 2.7 +/- 0.5 (20%) | 2.5392 (2.54) | 2.4442 (2.44) | excluded |
| CdSe-2 | 3.5 +/- 0.6 (19%) | 2.4205 (2.41) | 2.3083 (2.30) | excluded |
| CdSe-3 | 3.7 +/- 0.9 (26%) | 2.3104 (2.31) | 2.1831 (2.18) | excluded |
| CdSe-4 | 4.5 +/- 0.5 (11%) | 2.1788 (2.18) | 2.0644 (2.06) | excluded |

This is exactly four size summaries, four absorption peaks, and four emission
peaks. Sample pairing, size-dispersion coverage, source-locator coverage, and
dual-pass coverage are each 100%.

## Repeatability

The repeatability calculation uses the frozen 1.8-to-3.0 eV labelled x span
and the diagnostic unit-height y span.

| Metric | Observed maximum | Frozen limit | Outcome |
| --- | ---: | ---: | --- |
| x difference / x span | 0.001799 (0.180%) | 0.005 (0.5%) | pass |
| y difference / diagnostic y span | 0.002212 (0.221%) | 0.01 (1.0%) | pass |
| point-pair pass fraction | 1.0 | 1.0 | pass |

The source-raster axis resolutions are about 0.0025 eV and 0.0013 of panel
height per pixel. One browser-display click spans about 1.77 source pixels, so
the adopted coordinate floors are conservatively rounded up to 0.0045 eV and
0.0023 of panel height. This is digitization uncertainty only. The FLAME-S
instrument uncertainty is not reported and no error bar was invented.

## Contract blocker

Figure 3(a) prints `Fluorescence (arb. units)` and `Absorption (arb. units)`
but has no numeric y tick marks. The frozen contract requires at least two y
anchors on printed tick marks. The 0-to-1 frame normalization therefore cannot
be promoted to a source-native y calibration even though the two sessions are
repeatable.

All eight optical observations are consequently `excluded`. The four
text-stated size summaries remain factual source summaries, but an incomplete
size-optical surface does not authorize a `qd-*.yaml` file. Changing the
contract after seeing the values would violate the predeclared gate.

## Semantic and rights boundaries

- Morphology remains `unknown_non_spherical`; no equivalent-sphere conversion
  was performed.
- Absorption and emission remain separate property kinds. Stokes shift, FWHM,
  differential-absorption levels, model levels, and bandgap are absent.
- The optical paragraph calls the CdSe-1 size 2.5 nm while the primary HRTEM
  paragraph reports 2.7 +/- 0.5 nm. The ledger preserves the HRTEM summary and
  sample identity without averaging the two statements.
- The version of record is CC BY 4.0. The attributed factual summaries and
  diagnostic coordinates are registered in
  [DATA_LICENSES.yaml](../../../data/DATA_LICENSES.yaml); publisher bytes remain
  uncommitted under the metadata-only source-byte posture.

## Metrics

- Source pins reproduced: 3 of 3.
- Atomic source observations recorded: 12.
- Independent passes: 2.
- Pass points with required provenance: 16 of 16.
- Repeatability pairs passing frozen numeric tolerances: 8 of 8.
- Printed y-axis anchors available: 0 of 4 required across two passes.
- Admitted optical rows: 0.
- Fits, benchmark metrics, RESULT/PRED/CLAIM/KNOW mutations: 0.

## Limitations

The panel-frame y coordinate is not a measured intensity and cannot be reused
as one. Peak locations are diagnostic coordinates only. This task does not
validate a quantum-confinement law, choose a benchmark split, estimate a
bandgap, or provide materials-design, synthesis, device, or biomedical
guidance.

## Verdict

**`UNCERTAINTY_BLOCKED`.** The dual-pass coordinate repeatability gate passes,
but the source cannot satisfy the frozen printed-y-tick calibration contract.
No optical row is publishable to the quantum-dot benchmark surface.

## Output routing

- Canonical destination: source-curation blocker ledger under
  `data/quantum_dots/digitization/kim-2020-nanomaterials-cdse-optical/`.
- Review tier: not applicable; no scientific RESULT was produced.
- Gate A: not applicable.
- Gate B: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: missing numeric Figure 3(a) y ticks required by the
  frozen calibration contract.
