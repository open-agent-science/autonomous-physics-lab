# Quantum Almeida 2023 Deterministic Source-Artifact Package (TASK-0741)

**Task:** `TASK-0741`
**Campaign:** `quantum-size-effects`
**Source:** Almeida et al., "Size-Dependent Optical Properties of InP Colloidal
Quantum Dots," Nano Letters 2023, 23 (18), 8697-8703,
doi:`10.1021/acs.nanolett.3c02630`.
**Package:** `data/quantum_dots/digitization/almeida-2023-nano-letters-inp-optical/`
**Verdict:** `LICENSE_CLEARED_AND_SOURCE_CHECKSUMMED__SIZE_AXIS_DIGITIZATION_PENDING`
— deterministic source-artifact package committed; precise size-axis blocker
preserved; no fabricated rows; no publisher PDF committed.

## Decision Selected: Almeida CC-BY Route

The maintainer selected the Almeida 2023 route for the Quantum source go/no-go
decision (over the Vossmeyer route and over the calibration-consistency waiver),
and supplied the article and SI PDFs locally. This task executes that route.

## License Cleared (recheck complete, positive)

The source manifest previously recorded the Almeida license as "promising but
artifact-gated; CC-BY posture indicated; recheck required." The recheck is now
complete and positive, from two independent authoritative surfaces:

| Surface | Finding |
| --- | --- |
| PMC `PMC10540257` (full text) | "Creative Commons Attribution 4.0 International (CC BY 4.0)"; applies to article, figures, and Supporting Information. |
| Crossref publisher metadata (ACS) | `https://creativecommons.org/licenses/by/4.0/` attached to the version-of-record (`vor`), start 2023-09-06, zero embargo. |

The article header also prints "This article is licensed under CC-BY 4.0."
Under CC-BY 4.0, extracted/adapted data may be committed and redistributed with
attribution. This clears the redistribution gate for this source.

## Source Bytes Checksummed (second blocker cleared)

The manifest previously recorded "no valid article/SI source bytes were obtained
for checksum pinning." A maintainer-supplied local copy is now available
off-repository and is checksum-pinned in the package README. The PDFs are not
vendored; only SHA-256 hashes and locators are recorded (one article PDF and the
canonical ACS SI). A given article PDF is one mirror of the CC-BY 4.0
version-of-record; other mirrors may differ in bytes, so a future verifier
should re-confirm against the copy it fetches.

## What Was Deterministically Extracted

The six size-series samples are labeled in SI Figure S2 by their measured
first-absorption-peak wavelength `λ1s` (an explicit printed label, not an axis
read). `E1s(eV) = 1239.84 / λ1s(nm)` is exact:

| `λ1s` (nm) | `E1s` (eV) |
| ---: | ---: |
| 460 | 2.695 |
| 480 | 2.583 |
| 510 | 2.431 |
| 550 | 2.254 |
| 580 | 2.138 |
| 620 | 2.000 |

The article text additionally states one complete (size, energy) pair: the
smallest dot has edge length `L = 1.5 nm` (5 In atoms) and `E1s = 2.70 eV`
(460 nm). This matches the table.

These are the **optical-energy axis only** and are recorded as source evidence,
**not** as benchmark rows.

## Why No Direct (size, energy) Rows Are Committed

Almeida 2023 exposes the size axis through figures, not a numerical table:

- per-sample edge length / volume appears only as TEM size-distribution
  histograms (SI Figure S2b);
- the size to energy relationship is published as a fitted sizing curve
  (Figure 1b; `E1s = 1.33 + 1.219 V^-0.251`).

The `TASK-0741` contract forbids using calibration polynomials / sizing
equations and forbids LLM-estimated figure coordinates. Reading a per-sample
mean edge length off a histogram is an estimated-coordinate operation and is
therefore not performed. Producing >=6 clean direct (size, energy) rows requires
a WebPlotDigitizer-class tool run on Figure S2b / Figure 1b with recorded axis
calibration, extracted coordinates, uncertainty, per-point inclusion state, and
reviewer replay. That tool run is the single remaining blocker.

## Recommended Follow-Up

A single bounded follow-up task: run the WebPlotDigitizer-class digitization of
the Almeida size axis (Figure S2b mean edge lengths and/or Figure 1b data
points), pair the digitized sizes with the deterministic `E1s` anchors above,
curate `qd-*.yaml` direct-measurement seeds with morphology `tetrahedral` and
`edge_length_nm` / `volume_nm3` size semantics (TASK-0637 schema), add a
`data/DATA_LICENSES.yaml` CC-BY 4.0 entry, and re-run the `TASK-0293`
row-readiness gate. This route is now license-clear and source-pinned, so it no
longer needs another source decision — only the tool run and review.

## Limitations

- No direct (size, energy) rows are committed; the size axis is figure-only.
- The optical-energy anchors are exact stated labels, not a full spectrum
  digitization; line-width / second-transition data are not extracted here.
- The article PDF is one mirror of the version-of-record; other mirrors may
  differ in bytes, so re-confirm the checksum against the fetched copy.
- This package makes no quantum-dot design, material, device, or biomedical
  claim and promotes no benchmark, result, prediction, or claim.

## Output-Routing Summary

- **Task verdict:** `PARTIALLY_VALID` — license-cleared, source-checksummed
  deterministic package; precise size-axis digitization blocker preserved.
- **Canonical destination:** this review note plus
  `data/quantum_dots/digitization/almeida-2023-nano-letters-inp-optical/README.md`
  and the updated `data/quantum_dots/source_manifest.yaml` Almeida entry;
  `TASK-0741` moves to `REVIEW_READY`.
- **Review tier:** `none`; no `RESULT-*` or `PRED-*` artifact.
- **Gate A status:** not attempted. **Gate B status:** not applicable.
- **Claim impact:** no claim change.
- **Knowledge impact:** campaign routing only; no knowledge entry.
- **Result artifact impact:** no `results/` artifact created or modified; no
  `qd-*.yaml` row committed.
- **Publication blocker:** direct InP rows remain blocked on the size-axis
  figure digitization tool run and the `TASK-0293` readiness gate.
