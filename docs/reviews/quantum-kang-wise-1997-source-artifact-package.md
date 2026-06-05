# Quantum Kang-Wise 1997 Source-Artifact Package Review

**Task:** `TASK-0588`
**Campaign:** Quantum Size Effects
**Source ID:** `kang-wise-1997-prb-pbs-band-edge`
**Verdict:** `BLOCKED_SOURCE_ARTIFACT_NOT_ADMISSIBLE`

## Scope

This review packages or rejects Kang-Wise 1997 only as a source-artifact
candidate for future Quantum Size Effects row curation. It does not transcribe
measurement values, add `qd-*.yaml` rows, run figure digitization, compute
baseline residuals, or promote any result, claim, or knowledge artifact.

## Inputs Reviewed

- `data/quantum_dots/source_manifest.yaml`
- `docs/reviews/quantum-kang-wise-1997-pbs-source-path.md`
- `docs/reviews/quantum-open-direct-table-source-triage.md`
- `docs/reviews/quantum-pmc-arxiv-direct-table-source-attempt.md`
- `docs/reviews/quantum-norris-bawendi-1996-digitization-runner.md`
- `docs/quantum-direct-source-artifact-intake.md`
- `docs/quantum-direct-measurement-digitization-protocol.md`
- `docs/campaigns/quantum-size-effects.md`
- Optica primary article page:
  <https://opg.optica.org/josab/abstract.cfm?uri=josab-14-7-1632>
- Optica journal article reuse license summary:
  <https://opg.optica.org/content/library/portal/item/license_v2>

## Method

1. Re-read the committed campaign and manifest memory for the Kang-Wise source
   path, including the TASK-0400 correction from the earlier PRB/APS locator
   to the Optica/JOSA B locator.
2. Checked the current Optica publisher page for locator, access state,
   exposed article metadata, visible table captions, visible table content
   class, figure/table access state, and PDF access state.
3. Checked Optica's article-reuse license summary for whether a publisher PDF,
   table, or figure can be redistributed in this repository.
4. Compared the source against the intake checklist in
   `docs/quantum-direct-source-artifact-intake.md`.
5. Preserved a blocker rather than adding a source-artifact directory because
   the source does not meet the admissibility conditions for row curation.

## Source Locator

- Article: Kang, I.; Wise, F. W. "Electronic structure and optical properties
  of PbS and PbSe quantum dots." *Journal of the Optical Society of America B*
  14, 1632-1646 (1997).
- DOI: `10.1364/JOSAB.14.001632`
- Publisher locator:
  <https://opg.optica.org/josab/abstract.cfm?uri=josab-14-7-1632>
- Manifest source id: `kang-wise-1997-prb-pbs-band-edge`

The manifest source id retains historical `prb` wording, but the committed
manifest and TASK-0400 review already correct the actual locator to Optica
JOSA B. This task does not rename the source id because that would be a
separate migration touching existing memory.

## Access And Redistribution Decision

The Optica article page reports the article as not accessible in this session,
with PDF access behind the publisher access controls. The page also reports
that figure files and article tables require subscription or account access.

Optica's reuse summary states that publisher-formatted journal PDFs are under
the publisher copyright/license unless another explicit license applies; for
subscription journal content, personal copying is limited and systematic
reproduction or distribution is prohibited. This task found no article-specific
open license or repository-compatible permission for committing the article,
tables, figures, or full extracted content.

Decision:

- `redistribution_decision`: `metadata_only`
- `publisher_pdf_committed`: `false`
- `publisher_tables_committed`: `false`
- `publisher_figures_committed`: `false`
- `checksum_sha256`: `PENDING_NOT_RETRIEVED`
- `checksum_feasibility`: feasible only after a legitimate maintainer-provided
  or otherwise permission-compatible source copy exists

## Direct Table Or Figure Status

The visible publisher page lists:

- `Figures (13)`
- `Tables (2)`
- `Equations (71)`

The two visible article tables are not direct size-energy measurement tables:

- Table 1 is a parameter table for the `k . p` Hamiltonians of PbS and PbSe.
- Table 2 is a parameter table for the anisotropy perturbation operator of PbS
  and PbSe.

These are model/theory parameter tables. They do not satisfy the APL
`table_derived` evidence class because they do not expose distinct
`(diameter_nm, value_eV)` or equivalent size-energy measurement rows with row
identifiers and uncertainty semantics.

The 13 figures may contain experimental comparison points, but the figure files
are access-controlled and no deterministic WebPlotDigitizer-class package
exists. Under `docs/quantum-direct-measurement-digitization-protocol.md`, an
agent must not estimate figure points by eye or from publisher thumbnails.

## Row-Class Evidence

| Intake question | Finding | Decision |
| --- | --- | --- |
| Legitimate source artifact available? | No source copy was retrieved or provided. | Blocked |
| Source checksum available? | No retrievable artifact exists in this task. | `PENDING_NOT_RETRIEVED` |
| Redistribution terms clear for article/table/figure content? | No repository-compatible permission found. | `metadata_only` |
| Direct printed size-energy table visible? | No; visible tables are model parameters. | Not `table_derived` |
| Figure-derived route possible? | Possible only after legitimate figure access and a deterministic digitization package. | `digitization_required_but_blocked` |
| `qd-*.yaml` row curation allowed now? | No. | Blocked |

## Blocker

`BLOCKED_SOURCE_ARTIFACT_NOT_ADMISSIBLE`:

Kang-Wise 1997 is not currently admissible as a Quantum direct-row source
artifact because the repository lacks a legitimate checksum-pinned source copy,
repository-compatible redistribution permission, direct printed size-energy
tables, and a deterministic figure-digitization package. The visible publisher
tables are model-parameter tables, not measurement rows.

## Handoff Checklist

A future source-artifact or row-curation task may revisit this source only if
all of the following are true:

- a maintainer supplies a legitimate article or figure copy, or an official
  access path with compatible reuse terms is confirmed;
- the artifact filename, retrieval date, access path, and SHA-256 checksum are
  recorded under `data/quantum_dots/source_artifacts/<source_id>/`;
- a curator confirms whether any non-visible article section contains direct
  printed size-energy rows;
- if the route is figure-derived, a WebPlotDigitizer-class package is committed
  with axis calibration, extracted coordinates, point-state decisions,
  uncertainty semantics, and reviewer replay notes;
- any future row-curation task keeps model/theory parameters separate from
  direct measurement rows and does not use the visible parameter tables as
  `qd-*.yaml` observations.

Until those conditions are met, agents should not re-attempt Kang-Wise 1997 as
a table-derived row source.

## Metrics

- `rows_added`: 0
- `qd_files_added`: 0
- `source_artifact_directories_added`: 0
- `publisher_files_committed`: 0
- `baseline_metrics_computed`: 0
- `claims_promoted`: 0
- `knowledge_entries_promoted`: 0

## Limitations

- This task did not inspect a subscriber-access full article or PDF.
- This task did not run a digitization tool.
- The negative decision is about current APL source-artifact admissibility, not
  about the scientific value of the Kang-Wise paper.
- The historical source id still contains `prb`; renaming it is out of scope.

## Output Routing Summary

- Task verdict: `BLOCKED_SOURCE_ARTIFACT_NOT_ADMISSIBLE`
- Canonical destination:
  `docs/reviews/quantum-kang-wise-1997-source-artifact-package.md`
- Review tier: `none`
- Gate A status: not attempted; no result artifact or deterministic benchmark
  run was produced.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Dataset impact: no `qd-*.yaml` rows added or changed.
- Benchmark impact: no quantum-size benchmark run.
- Publication blocker: no legitimate checksum-pinned source copy, no
  repository-compatible redistribution decision, no direct printed size-energy
  table, and no deterministic figure-digitization artifact.
