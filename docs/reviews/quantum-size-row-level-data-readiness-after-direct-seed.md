# Quantum Size-Effect Row-Level Readiness After Direct Seed (TASK-0293)

**Gate verdict:** `PASS` — a real-measurement (non-calibration) direct seed of
six rows is now committed, second-agent audited, and schema-valid. TASK-0225
(first benchmark) moves `BLOCKED -> READY`.

## Direct seed

`data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml` — six InP colloidal
quantum dot `(edge length, E1s)` rows from Almeida et al., Nano Letters 2023
(doi:10.1021/acs.nanolett.3c02630, CC-BY 4.0).

## Row classification (per TASK-0293 requirement)

All six included rows are **digitised figure points of real measurements**, not
calibration-derived:

- Edge length L = SI Figure S2b TEM edge-length distribution mean (real TEM
  measurement), deterministically extracted (gray-histogram weighted centroid).
- E1s = 1239.84 / lambda1s from the published first-absorption-peak labels (real
  optical measurement).

This is distinct from the existing `qd-0001` (Yu 2003) and `qd-0002` (Moreels
2009) rows, which are calibration-derived from published sizing *formulas*. The
gate's purpose — prevent unblocking the benchmark from calibration-derived rows
alone — is satisfied: qd-0003 is a measurement-vs-model dataset.

| lambda1s (nm) | E1s (eV) | edge length L (nm) | +/- (nm) | class |
| --- | --- | --- | --- | --- |
| 460 | 2.695 | 1.498 | 0.282 | digitised_figure_point (TEM) |
| 480 | 2.583 | 2.002 | 0.272 | digitised_figure_point (TEM) |
| 510 | 2.431 | 2.602 | 0.446 | digitised_figure_point (TEM) |
| 550 | 2.254 | 2.787 | 0.361 | digitised_figure_point (TEM) |
| 580 | 2.138 | 3.136 | 0.309 | digitised_figure_point (TEM) |
| 620 | 2.000 | 4.112 | 0.432 | digitised_figure_point (TEM) |

## Provenance and audit

- Two independent deterministic extractions by two independent agents agree:
  Figure 2b sizing curve (`extract_almeida_sizing.py`) and SI Figure S2b TEM
  histograms (`extract_s2b_histograms.py`). The five non-620 samples cross-check
  to <= 0.62 Angstrom (<= 0.06 nm). VERDICT: CLEAN_6.
- Both extractors are byte-reproducible; rasters/PDF not vendored (SHA + locator
  only); CC-BY 4.0 declared in `data/DATA_LICENSES.yaml`.
- Smallest dot 1.50 nm matches the source text; values monotonic; on the
  published fit within scatter.

## Readiness decision

- Row-count floor (>= 6 admissible direct rows): **met** (6/6 included).
- Provenance: real-measurement (figure-digitised TEM), not calibration-derived.
- Gate: **PASS**. TASK-0225 `BLOCKED -> READY`.

## TASK-0225 first-benchmark recommendation

- **Property axis:** `absorption_peak_eV` (E1s) vs tetrahedral edge length L.
- **Dataset:** `qd-0003-almeida-2023-inp-optical.yaml` (6 InP rows). Keep
  `qd-0001`/`qd-0002` (CdSe/CdTe/CdS/PbS, calibration-derived) out of the InP
  benchmark unless explicitly used as a separate calibration-derived contrast.
- **Material:** InP only (single material; no material holdout in this first
  pass).
- **Size-range holdout:** hold out the largest dot (lambda620, L=4.11 nm) or the
  smallest (lambda460, L=1.50 nm) to test extrapolation beyond the trained range.
- **Negative controls:** (a) size-label shuffle; (b) global-mean / constant-E1s
  baseline the candidate must beat; (c) report against the published
  `E = 1.33 + 9.128 L^-0.684` fit as an external reference (do not fit it).
- **Uncertainty:** propagate the per-row size uncertainty (0.27-0.45 nm) into the
  residual interpretation; 6 rows is a small set — report this as a limitation.

## Limitations

- Figure-digitised (not source-table) provenance; six rows is a small benchmark.
- Single material (InP). Generalization across materials is out of scope here.
- No baseline fit, hypothesis search, or claim is performed by this gate task.

## Output routing

- Task verdict: readiness gate PASS; first direct seed admitted.
- Canonical destination: this review + `qd-0003` (source curation).
- Claim / knowledge impact: none.
- Next: run TASK-0225 (baseline residual benchmark); TASK-0226/0276 follow.
