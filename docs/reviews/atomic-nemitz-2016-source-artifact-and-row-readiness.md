# Atomic Nemitz 2016 Source Artifact And Row Readiness

**Task:** `TASK-0452`
**Campaign:** Atomic-Clock Residuals
**Source under review:** Nemitz, N., et al., "Frequency ratio of Yb and Sr clocks with 5 x 10^-17 uncertainty at 150 seconds averaging time", Nature Photonics 10, 258 (2016); arXiv:1601.04582
**Verdict:** `SOURCE_ARTIFACT_PINNED_ROWS_BLOCKED`

## Scope

This task attempted to ingest Nemitz et al. 2016 / RIKEN Yb/Sr as the second
independent direct-ratio source for Atomic-Clock Residuals. It pins the correct
redistributable arXiv source artifact and checksum, but it does **not** add
`ACR-0002` rows because the source/version gate is not fully cleared.

No drift fit, constants-variation constraint, Beloy-vs-Nemitz comparison,
prediction entry, canonical result, claim, or knowledge artifact is created.

## Source Locator Correction

The prior triage and `TASK-0452` text named Nemitz 2016 but cited
`arXiv:1403.5836`. That arXiv record is Akamatsu et al. 2014 / Optics Express,
not Nemitz et al. 2016. The correct Nemitz source is:

- arXiv: `1601.04582`
- DOI: `10.1038/nphoton.2016.20`
- Nature Photonics: volume 10, pages 258-261 (2016)

Therefore this PR deliberately commits
`data/atomic_clocks/source_artifacts/2016-nemitz-riken/arxiv-1601.04582.pdf`
instead of the erroneous `arxiv-1403.5836.pdf` path from the older triage text.
Committing the wrong PDF would silently pin the wrong source family.

## Artifact Pin

- PDF: `data/atomic_clocks/source_artifacts/2016-nemitz-riken/arxiv-1601.04582.pdf`
- SHA-256 sidecar: `data/atomic_clocks/source_artifacts/2016-nemitz-riken/arxiv-1601.04582.sha256`
- SHA-256: `9835ebc240296cdb9a70e94448fb5761292fd1d7146a4f17ed6c22cf497b33ce`
- Provenance: `data/atomic_clocks/source_artifacts/2016-nemitz-riken/provenance.yaml`
- Nature version-of-record PDF: not committed; DOI citation only.

## Gates

| Gate | Status | Evidence |
| --- | --- | --- |
| Correct source identity | `PASS_WITH_CORRECTION` | arXiv:1601.04582 title/authors/DOI match Nature Photonics public page; arXiv:1403.5836 is Akamatsu 2014. |
| Redistributable artifact | `PASS` | arXiv preprint PDF committed with checksum sidecar. |
| Nature PDF redistribution | `PASS` | Nature PDF not committed; DOI only. |
| Public abstract value check | `PASS` | Nature public page and arXiv abstract expose the same ratio statement: R = 1.207507039343337749(55), fractional uncertainty 4.6e-17. |
| Table-level arXiv-vs-Nature drift check | `BLOCKER` | Public Nature page does not expose full Table 1 uncertainty budget; maintainer-side version-of-record table comparison is still required before rows. |
| TASK-0344 uncertainty semantics from arXiv | `PARTIAL_PASS` | arXiv Table 1 exposes total, statistical, systematic, and per-component uncertainty terms. |
| Campaign window lock | `BLOCKER_FOR_ROW` | arXiv text says ten measurements over four months, but exact calendar start/end is not stated in the extracted text. |

## Row Readiness

Rows are **not** added in this PR.

The arXiv PDF exposes enough material for a future row curation pass:

- direct ratio orientation: `nu_Yb / nu_Sr`;
- ratio value: `1.207507039343337749(43)sys(35)stat` and abstract shorthand `(55)`;
- total fractional uncertainty: `4.6e-17`;
- statistical uncertainty: `28.6e-18`;
- systematic uncertainty from Table 1 quadrature: approximately `36.0e-18`;
- per-systematic components for Yb effects, Sr effects, laser-to-laser link, and gravitational shift;
- row class: direct optical frequency-ratio measurement.

But row curation remains blocked because TASK-0452 requires all of the source,
version-drift, and uncertainty gates to pass before `ACR-0002` rows are
committed. The table-level Nature comparison and exact campaign-window lock are
not complete from committed/open artifacts alone.

## Source Manifest Update

`data/atomic_clocks/source_manifest.yaml` is updated from
`triage_only_no_values` to `source_artifact_pinned_rows_blocked` for Nemitz 2016.
The manifest now records the corrected arXiv locator, checksum, provenance path,
and the blockers that still prevent value-bearing rows.

## Required Follow-up

Before `data/atomic_clocks/acr-0002-nemitz-2016-direct-ratio.yaml` can be added:

1. A maintainer with Nature Photonics version-of-record access must compare the
   committed arXiv PDF against the Nature PDF for all row-defining fields,
   including Table 1 corrections and uncertainty contributions.
2. The row curation task must lock the campaign window without guessing calendar
   months from prose.
3. The row curation task must decide how to represent the paper's value notation
   `(43)sys(35)stat` versus the combined `(55)` uncertainty shorthand.
4. The row curation task must preserve the direct/derived separation because the
   paper also discusses alpha-variation sensitivity as interpretation, not as a
   direct measurement row.

## Output-Routing Summary

- **Task verdict:** `SOURCE_ARTIFACT_PINNED_ROWS_BLOCKED`.
- **Canonical destination:** source artifact package under
  `data/atomic_clocks/source_artifacts/2016-nemitz-riken/`, updated
  `data/atomic_clocks/source_manifest.yaml`, and this review file.
- **Review tier:** `none` for RESULT/PRED; source-artifact review only.
- **Gate A status:** not attempted.
- **Gate B status:** not attempted.
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Publication blocker:** value-bearing row publication is blocked pending
  table-level arXiv-vs-Nature drift review and campaign-window lock.

## Limitations

- This PR used the public Nature article page rather than a local
  version-of-record PDF; it therefore cannot clear the table-level version-drift
  gate.
- The arXiv PDF has a recoverable uncertainty table, but row curation is held
  until the version-of-record table is checked.
- The previous triage's arXiv ID typo is corrected in manifest metadata, but
  older review prose remains historical context rather than silently rewritten.

