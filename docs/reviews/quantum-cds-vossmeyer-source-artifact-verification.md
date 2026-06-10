# Quantum CdS Vossmeyer 1994 Source-Artifact Verification

**Task:** `TASK-0687`  
**Campaign:** Quantum Size Effects  
**Source candidate:** `vossmeyer-1994-jpc-cds-absorption`  
**DOI:** `10.1021/j100082a044`  
**Decision:** `BLOCKER_SOURCE_ARTIFACT_NOT_COMMITTED`  
**Review date:** 2026-06-10

## Scope

This review verifies the access path and direct-table status for Vossmeyer
et al. 1994 (CdS nanoclusters) without transcribing table values, committing
publisher PDFs, adding `qd-*.yaml` rows, running baselines, or promoting claims.

It builds on:

- `docs/reviews/quantum-size-direct-absorption-seed-review.md` (Yu 2003 cites
  Vossmeyer 1994 for CdS small-cluster Figure 2 points)
- `docs/quantum-direct-measurement-digitization-protocol.md`
- `docs/quantum-direct-source-artifact-intake.md`
- `data/quantum_dots/source_manifest.yaml`

No article PDF, table image, checksum, or measurement row was committed in
this task.

## Inputs Reviewed

- `TASK-0687`
- `docs/reviews/quantum-second-open-direct-table-source-scout.md` (`TASK-0656`
  landed Prasad 2017 as the second open direct-table scout; Vossmeyer remains
  a separate CdS-family candidate referenced by Yu 2003 provenance notes)
- ACS article landing page for DOI `10.1021/j100082a044`
- OpenAlex, Semantic Scholar, Europe PMC, PubMed, and Crossref metadata
- HZB bibliographic repository record
- Secondary bibliographic abstract surfaces (IPPT PAN partner index)

## Method

1. Re-read the task contract and Quantum direct-measurement guardrails.
2. Probed publisher, index, and repository locators for a committable open
   access path. An ACS institutional subscription alone is not treated as a
   committable repository path.
3. Recorded table-surface status from abstract-level and bibliographic
   secondary evidence only. No primary PDF text extraction was performed
   because no legitimate open or maintainer-provided full text was available
   in this verification session.
4. Added a metadata-only excluded manifest entry documenting locators,
   expected row class, and blockers for a future source-artifact task.

## Source Locator

| Field | Value |
| --- | --- |
| Article | CdS Nanoclusters: Synthesis, Characterization, Size Dependent Oscillator Strength, Temperature Shift of the Excitonic Transition Energy, and Reversible Absorbance Shift |
| Authors | Vossmeyer, T.; Katsikas, L.; Giersig, M.; Popovic, I. G.; Diesner, K.; Chemseddine, A.; Eychmüller, A.; Weller, H. |
| Journal | The Journal of Physical Chemistry |
| Year / volume / pages | 1994; 98 (31); 7665-7673 |
| DOI | `10.1021/j100082a044` |
| ACS landing page | `https://pubs.acs.org/doi/abs/10.1021/j100082a044` |
| ACS PDF locator | `https://pubs.acs.org/doi/pdf/10.1021/j100082a044` |
| HZB bibliographic record | `https://www.helmholtz-berlin.de/pubbin/oai_publication?ID=-3292` |

Retrieval date for this metadata review: `2026-06-10`.

## Access Path Verification

| Surface | Result | Committable for APL? |
| --- | --- | --- |
| ACS article page | Subscriber/purchase gated; free first page only; institution access unavailable in this session | **No** — ACS subscription or pay-per-view is not a committable path |
| ACS PDF URL | Publisher PDF behind access controls | **No** |
| Europe PMC | 0 hits for DOI | **No** |
| PubMed | No indexed entry | **No** |
| OpenAlex | `is_oa: false`; no repository full text | **No** |
| Semantic Scholar | `isOpenAccess: false`; OA PDF status `CLOSED` | **No** |
| HZB repository | Bibliographic metadata only; no open PDF link surfaced | **No** |
| TechnoRep (Belgrade) | Index record exists; session blocked by verification gate | **No** — not verified as open full text |
| Maintainer-provided copy | Not supplied in this task | **Pending** — only admissible if a future task checksum-pins a maintainer-approved sandbox copy without committing the publisher PDF unless license policy allows |

Decision: **no verified open, public, institutional-mirror, PMC, or
maintainer-provided full-text path** exists for this verification session.

## Table And Direct-Measurement Status

Assessment below uses abstract-level and bibliographic secondary evidence
only. Exact table headers, units, and row count were **not** verified against
a primary PDF in this task.

| Field | Assessment |
| --- | --- |
| Material family | Pure-core CdS nanoclusters (1-thioglycerol stabilized) |
| Expected property axis | `absorption_peak_eV` via 1s-1s excitonic transition energy |
| Expected size axis | mean cluster diameter from SAXS (`diameter_nm` candidate) |
| Reported sample count | six discrete samples in abstract-level metadata |
| Reported diameter range | approximately 13, 14, 16, 19, 23, and 39 Å (abstract-level; not transcribed as rows) |
| Table surface | bibliographic sources consistently reference **Article Table 1** as the size/optical summary table |
| Expected columns (unverified) | mean cluster size, excitonic transition energy, oscillator strength |
| Measurement methods cited | SAXS for mean size; UV-vis spectroscopy for excitonic transition; not a published sizing-polynomial evaluation |
| Direct vs model-derived | **probable direct per-sample measurements**, pending primary-source PDF confirmation |
| Figure-only fallback | not required if Table 1 verification succeeds on a future primary-source pass |
| Core-shell confound | none indicated for this CdS source (contrast with excluded core-shell sources) |
| Campaign fit | strong candidate for CdS small-cluster direct rows that Yu 2003 Figure 2 attributes to prior literature |

Expected row class if Table 1 is confirmed on primary inspection:
`table_derived`.

This task does **not** upgrade the candidate to row-ready. A future
source-artifact task must verify Table 1 directly, record reuse terms, and
commit checksum metadata (or an approved extraction artifact) before any
`qd-*.yaml` curation.

## Decision

`BLOCKER_SOURCE_ARTIFACT_NOT_COMMITTED`

The source remains scientifically promising as a **CdS direct-table**
candidate, but this verification session found:

1. no committable open access path;
2. no checksum-pinned source artifact;
3. no primary-PDF confirmation of Table 1 structure beyond secondary
   bibliographic evidence.

Recommended next step: a maintainer-provided or institutionally authorized
ACS full-text verification pass that confirms Table 1 headers/units and, if
reuse policy allows, checksum-pins a sandbox copy for deterministic table
extraction. Do not transcribe values from abstract text, LLM memory, or
unverified secondary summaries.

## Limitations

- No publisher PDF, table image, or SI file was committed.
- No table values, figure coordinates, or `qd-*.yaml` rows were transcribed.
- Table 1 structure was inferred from abstract-level and bibliographic
  secondary surfaces only; primary-source confirmation is still required.
- ACS access state may differ under maintainer institutional login; such
  access still does not by itself satisfy the repository committable-path
  rule unless a maintainer-provided artifact path is explicitly approved.
- Oscillator-strength columns are useful scientifically but are outside the
  current first-pass `absorption_peak_eV` residual axis unless a future task
  scopes them explicitly.

## Output Routing

- Task verdict: `BLOCKER_SOURCE_ARTIFACT_NOT_COMMITTED`.
- Table-surface sub-verdict: `PROMISING_TABLE_DERIVED_CANDIDATE_PENDING_PRIMARY_PDF`.
- Canonical destination:
  `docs/reviews/quantum-cds-vossmeyer-source-artifact-verification.md` plus
  metadata-only excluded entry in `data/quantum_dots/source_manifest.yaml`.
- Review tier: none.
- Gate A status: not attempted; no `RESULT-*` or `PRED-*` artifact.
- Gate B status: not attempted; no independent replay target.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Dataset impact: no `qd-*.yaml` rows added or changed.
- Publication blocker: no committable open access path and no checksum-pinned
  source artifact; primary PDF table verification still required before row
  curation.
