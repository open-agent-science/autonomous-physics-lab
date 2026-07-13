# TASK-1027: Kim 2020 CdSe value-blind source artifact

## Scope and freeze

This package converts the TASK-0988 scout lead
([quantum-next-direct-source-scout.md](../quantum-next-direct-source-scout.md))
into a reviewable, value-blind source artifact for Kim et al. 2020,
"Influence of Size and Shape Anisotropy on Optical Properties of CdSe Quantum
Dots" (*Nanomaterials* 10(8), 1589). It records exact source identity, rights,
figure/axis inventory, morphology and uncertainty semantics only.

No figure was cropped or digitized, no row was transcribed, no `qd-*.yaml`
data was created, no size law was fitted, no transfer metric was rerun, and no
RESULT, PRED, CLAIM, or KNOW artifact was created or changed. Numeric values
printed in the article (per-sample diameters, dispersions, energies, Stokes
shifts, FWHMs) were deliberately not copied into any committed file.

## Pinned source identity

Retrieval date for all artifacts: `2026-07-13`. Retrieved bytes live in a
temporary, uncommitted cache; only locators and SHA-256 digests are recorded
(same pattern as the TASK-0989 stellar package). The committed intake fields
are in
[source_artifacts/kim-2020-nanomaterials-cdse-optical/README.md](../../../data/quantum_dots/source_artifacts/kim-2020-nanomaterials-cdse-optical/README.md)
and the source registry entry is in
[source_manifest.yaml](../../../data/quantum_dots/source_manifest.yaml).

| Artifact | Locator | Bytes | SHA-256 | Notes |
| --- | --- | ---: | --- | --- |
| Version-of-record PDF | `https://mdpi-res.com/d_attachment/nanomaterials/nanomaterials-10-01589/article_deploy/nanomaterials-10-01589.pdf` | 1,368,239 | `2dab8a6b4db18af88f7175ac0773747fe1aeb15d88f951a4a8536cdc2dd73edb` | Publisher CDN deployment of the VoR; first page confirms title, authors, journal, DOI `10.3390/nano10081589`, published 2020-08-12 |
| Europe PMC JATS full text | `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7466547/fullTextXML` | 62,029 | `6642fed609ad6540b61ca856d293d2b469c5ed7be9323479c9b76b023f668244` | Structured full text used for the figure/semantics inventory |
| Crossref work metadata | `https://api.crossref.org/works/10.3390/nano10081589` | 12,087 | `6b3a36ba7160d7c3d12a54bc64b846ec358d569ee562e778e8ac64eca6526e9c` | Live-index snapshot of the access date; carries the vor license record |
| PMC OA service record | `https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC7466547` | — | not asserted | Confirms `license="CC BY"`, `retracted="no"`, and the official OA package locator `ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/f1/56/PMC7466547.tar.gz` |

Access limitations recorded honestly: `www.mdpi.com` article pages refuse
scripted retrieval (Akamai "Access Denied"), the `pmc.ncbi.nlm.nih.gov`
article page is behind a browser-verification wall (not bypassed), and FTP
egress is blocked in the task sandbox, so the official PMC OA tar.gz is a
locator without an asserted checksum. None of these blocks the package: the
VoR bytes, license, and structured full text are pinned through the publisher
CDN, Crossref, the PMC OA service, and Europe PMC.

## Rights posture

- Version-of-record license: **CC BY 4.0** (Crossref `license` with
  `content-version: vor`, start 2020-08-12; JATS license block; PMC OA record
  `CC BY`). Attribution required.
- Retained artifacts: every retained (cached) artifact is covered by CC BY
  4.0 (article PDF, JATS full text) or is API metadata (Crossref, PMC OA
  record).
- Redistribution decision: `metadata_only`. CC BY 4.0 would permit vendoring
  the PDF with attribution, but the campaign intake protocol keeps publisher
  bytes uncommitted unless a maintainer explicitly decides otherwise. No
  DATA_LICENSES entry is needed because no third-party dataset bytes are
  committed.

## Figure, sample, and axis inventory (value-blind)

Sample identifiers: `CdSe-1` (growth 5 s), `CdSe-2` (1 min), `CdSe-3`
(5 min), `CdSe-4` (60 min); synthesized by hot injection, stored in toluene,
HRTEM prepared from chloroform solution on carbon-coated Cu grids.

| Surface | Content | Axis semantics | Provenance class expectation |
| --- | --- | --- | --- |
| Figure 1(a–d) | HRTEM images (Cs-corrected JEM-ARM200F), shape anisotropy marked with dotted lines | image scale in nm | context only; not a row surface |
| Figure 1(e–h) | Per-sample size-distribution histograms with Gaussian fits; per-sample mean diameter ± dispersion also stated in caption/body text | `diameter_nm` (HRTEM Gaussian-fit mean per sample) | `digitization_required` for distributions; text-stated per-sample means are a possible text-derived summary class — extraction-preflight decision |
| Figure 2(a–d) | XRD patterns (Cu Kα), per-facet fitting curves, mixed zinc-blende/wurtzite semantics | diffraction angle | context for morphology; not a row surface |
| Figure 3a | Absorption (dashed) and fluorescence (solid) spectra per sample (FLAME-S spectrometer) | photon energy/wavelength vs intensity | `digitization_required`; candidate axes `absorption_peak_eV` and `emission_peak_eV`, kept separate |
| Figure 3b | Stokes shifts and FWHMs vs size | derived quantities | analysis-derived; separate class; not primary rows |
| Figure 4(a–d) | Absorption and differential-absorption (DA) spectra; first–sixth excitonic transitions extracted via sixth-derivative DA analysis | transition energies | analysis-derived provenance class; must not be conflated with raw `absorption_peak_eV` |
| Figure 5 | Size-dependent electron/hole quantum levels with fitting curves | energy vs size | model-fit class (calibration risk); not direct rows |

Row-table reality: the JATS full text contains **zero** `table-wrap` and
**zero** `supplementary-material` elements, and the PMC OA record lists only
the article package. There is no printed row table and no SI file, so any
future row extraction is `digitization_required` under
[docs/quantum-direct-source-artifact-intake.md](../../quantum-direct-source-artifact-intake.md)
§3.2 (deterministic tool with axis calibration; no eyeballing).

## Morphology and uncertainty semantics

- The article explicitly reports size-dependent shape anisotropy
  (mixed zinc-blende/wurtzite structure; rod-like/hexagonal habits marked in
  HRTEM). Morphology must therefore remain `unknown_non_spherical`, and
  anisotropic particles must not be coerced to an equivalent sphere unless a
  later task predeclares and reviews a geometry rule (task requirement).
- Expected uncertainty route: the size axis carries per-sample Gaussian-fit
  dispersion stated in the text/caption; the optical spectra carry no stated
  per-point uncertainties in the text; DA-extracted transition energies carry
  method-level uncertainty that the article discusses qualitatively via
  anisotropy-induced estimation error. The extraction preflight must decide
  per-row uncertainty semantics before any `qd-*.yaml` row exists.
- Axis separation rule honored: `absorption_peak_eV`, `emission_peak_eV`, and
  any bandgap interpretation are separate candidate axes; none may be
  inferred from another; DA transitions form a separate analysis-derived
  class.

## Counts

| Quantity | Value |
| --- | ---: |
| Committed value rows | 0 |
| Digitized points | 0 |
| Figures cropped or re-rendered | 0 |
| Metrics, fits, or transfers run | 0 |
| RESULT/PRED/CLAIM/KNOW mutations | 0 |
| Source registry entries added | 1 (`kim-2020-nanomaterials-cdse-optical`) |

## Verdict

**`SOURCE_ARTIFACT_READY_FOR_EXTRACTION_PREFLIGHT`.** Source identity, VoR
license (CC BY 4.0), figure/sample inventory, morphology semantics, and the
uncertainty route are pinned; nothing blocks a bounded deterministic
extraction-preflight task. This verdict does not authorize row extraction,
digitization, size-law fitting, transfer metrics, or any benchmark use.

## Stop conditions honored

Work stopped before: cropping/digitizing figures, transcribing rows, creating
`qd-*.yaml` data, fitting any size law, rerunning ZnSe/InP transfer metrics,
or creating RESULT/PRED/CLAIM/KNOW artifacts.

## Limitations

- The Crossref response is a live-index snapshot; its digest pins the access
  date, not an upstream version number.
- The official PMC OA tar.gz was not fetched (sandbox FTP egress blocked), so
  its checksum is not asserted; the VoR PDF digest covers byte identity.
- MDPI and PMC article HTML pages were not scraped (bot walls); identity was
  established from the VoR PDF first page, Crossref, PMC OA service, and
  Europe PMC JATS instead.
- Per-sample text-stated mean diameters were seen during inspection but not
  recorded; their admissibility class (text-derived summary vs digitization)
  is intentionally left to the extraction preflight.

## Bounded next-task shape (extraction preflight)

1. Re-verify the pinned digests; fetch the PMC OA package if egress allows
   and record its checksum.
2. Decide the admissibility class for the text-stated per-sample mean
   diameters (with dispersions) vs Figure 1(e–h) histogram digitization.
3. Predeclare the deterministic digitization tool, axis-calibration
   procedure, per-point provenance fields, and uncertainty ledger for
   Figure 3a (and, separately, whether DA-derived transitions are in scope at
   all).
4. Predeclare the anisotropy geometry rule (or explicitly keep
   `unknown_non_spherical` with no equivalent-sphere conversion).
5. Stop before benchmark split design, scoring, or any transfer rerun; those
   remain separate tasks after row curation.

## Output routing

- Task verdict: `not_applicable` (source curation; package-level outcome is
  `SOURCE_ARTIFACT_READY_FOR_EXTRACTION_PREFLIGHT`).
- Canonical destination: this review note, the source-artifact README under
  `data/quantum_dots/source_artifacts/kim-2020-nanomaterials-cdse-optical/`,
  and one registry entry in `data/quantum_dots/source_manifest.yaml`.
- Review tier: none (source curation only).
- Gate A: not attempted (no publishable RESULT/PRED exists).
- Gate B: not attempted (nothing replayable exists at this stage).
- Claim impact: none.
- Knowledge impact: none; the extraction-preflight follow-up remains a
  maintainer decision.
- Publication blockers: none for this package itself; row curation stays
  blocked until a maintainer-approved extraction-preflight task passes.
