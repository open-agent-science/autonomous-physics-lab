# Almeida 2023 InP Optical Deterministic Source-Artifact Package

Task: `TASK-0741`
Source ID: `almeida-2023-nano-letters-inp-optical`
DOI: `10.1021/acs.nanolett.3c02630`
Package status: `LICENSE_CLEARED_AND_SOURCE_CHECKSUMMED__SIZE_AXIS_DIGITIZATION_PENDING`

## Scope

This package records the deterministic, license-cleared source-artifact state
for the Almeida 2023 InP optical size-series. It contains **no committed
publisher PDF**, no raster figure panel, and no fabricated `qd-*.yaml` rows.

It advances the two blockers the source manifest previously named for this
source:

1. **License recheck** — previously "promising but artifact-gated; CC-BY posture
   indicated." Now **confirmed CC-BY 4.0** on the version-of-record (see the
   review note); redistribution of attributed extracted data is permitted.
2. **Source bytes for checksum pinning** — previously "no valid article/SI
   source bytes were obtained." A maintainer-supplied local copy of the article
   and SI is now available off-repository, and the SHA-256 checksums are pinned
   below.

The remaining blocker is **only** the size-axis figure digitization: the
per-sample edge length / volume is exposed in TEM histograms (SI Figure S2b) and
the sizing curve (Figure 1b), not in a numerical table, so it requires a
WebPlotDigitizer-class tool run. The optical-energy axis is deterministically
available from the figure panel labels and the text and is recorded below.

## Source Locators

- Citation: Almeida, G.; van der Poll, L.; Evers, W. H.; Szoboszlai, E.; Vonk,
  S. J. W.; Rabouw, F. T.; Houtepen, A. J. (2023), "Size-Dependent Optical
  Properties of InP Colloidal Quantum Dots," Nano Letters 23 (18), 8697-8703.
- DOI: `10.1021/acs.nanolett.3c02630`
- DOI URL: `https://doi.org/10.1021/acs.nanolett.3c02630`
- License: Creative Commons Attribution 4.0 International (CC-BY 4.0),
  version-of-record, zero embargo (confirmed via PMC `PMC10540257` and Crossref).
- Material: InP colloidal quantum dots (core-only, tetrahedral)
- Source class: `digitization_required` (figure-derived), not `table_derived`.

## Pinned Source Checksums (PDF not committed)

Maintainer-supplied local copies, hashed for verification. The PDFs themselves
are **not** vendored in the repository.

| Role | Filename (local) | SHA-256 |
| --- | --- | --- |
| Supporting Information (canonical ACS filename) | `nl3c02630_si_001.pdf` | `2d0080214d9f7116561cbd80659d40463f868b57ca211179f5d854d12ad265ee` |
| Article copy A | `size-dependent-optical-properties-of-inp-colloidal-quantum-dots (1).pdf` | `dcd8ee5ef4fadb364aa55b9031828165f87016defcf77f183e1615fbe7ab8f39` |
| Article copy B | `Size-Dependent-Optical-Properties-of-InP-Colloidal-Quantum-Dots.pdf` | `8ba8de0cca3bf45a8f6b46c6cf9d10dcd3b0c2309652c7272af574fe98ae8112` |

The two article copies are distinct mirror bytes (institutional-repository vs
publisher copies legitimately differ); the ACS version-of-record should be the
canonical article pin. The SI hash is unambiguous (canonical ACS SI filename).

## Deterministic Optical-Energy Anchors (size pending)

The six size-series samples are labeled in SI Figure S2 by their measured
first-absorption-peak wavelength `λ1s` (a stated label, not an axis read). These
convert to `E1s` by `E1s(eV) = 1239.84 / λ1s(nm)` (exact). These are the
**optical-energy axis only**; they are **not** benchmark rows because the
per-sample size is not yet extracted.

| Sample `λ1s` (nm) | `E1s` (eV) | Per-sample size (edge length / volume) |
| ---: | ---: | --- |
| 460 | 2.695 | `L = 1.5 nm` (text: smallest dot, 5 In atoms) — only complete (size, energy) anchor stated in text |
| 480 | 2.583 | pending figure digitization (SI Fig. S2b histogram) |
| 510 | 2.431 | pending figure digitization |
| 550 | 2.254 | pending figure digitization |
| 580 | 2.138 | pending figure digitization |
| 620 | 2.000 | pending figure digitization |

Consistency check: the article states `E1s` spans `2.0-2.7 eV (620-460 nm)`,
matching the table above.

## Remaining Blocker (size axis only)

Producing >=6 clean direct (size, energy) rows still requires:

- a WebPlotDigitizer-class tool run on SI Figure S2b (edge-length histograms,
  per-sample mean edge length) and/or Figure 1b (sizing-curve data points), with
  recorded tool/version, axis calibration anchors, extracted coordinates,
  coordinate + publication uncertainty, and per-point inclusion state;
- reviewer replay of that extraction.

Do **not** substitute the analytical sizing equation
(`E1s = 1.33 + 1.219 V^-0.251`) or estimated histogram-peak coordinates for
measured per-sample sizes — both are excluded by the task contract. When the
digitization lands, curate `qd-*.yaml` seeds and add a `data/DATA_LICENSES.yaml`
entry (CC-BY 4.0, attribution) before re-running the `TASK-0293` readiness gate.

## Attribution (required by CC-BY 4.0 on reuse)

Data adapted from Almeida et al., Nano Letters 2023, 23, 8697-8703
(doi:10.1021/acs.nanolett.3c02630), licensed CC-BY 4.0. Optical-energy anchors
above are derived from the figure panel labels and article text.
