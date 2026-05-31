# Atomic Second-Source Fallback Triage

**Task:** `TASK-0485`
**Campaign:** Atomic-Clock Residuals
**Verdict:** `FALLBACK_SOURCES_TRIAGED_ROWS_BLOCKED`

## Scope

`TASK-0452` pinned the corrected Nemitz 2016 / RIKEN Yb/Sr arXiv artifact but
left value-bearing rows blocked pending table-level arXiv-vs-Nature
version-drift review and campaign-window lock. This review ranks fallback
second-source candidates in case Nemitz remains blocked.

This is a metadata-only triage. It does not fetch source artifacts, copy
frequency-ratio values, add measurement rows, fit drift, compare sources,
derive constants-variation constraints, create `RESULT` artifacts, or promote
claims.

## Inputs

- `tasks/TASK-0485-triage-atomic-second-source-fallbacks.yaml`
- `tasks/TASK-0452-ingest-atomic-nemitz-2016-yb-sr-source.yaml`
- `docs/reviews/atomic-second-direct-ratio-source-triage.md`
- `docs/reviews/atomic-nemitz-2016-source-artifact-and-row-readiness.md`
- `docs/reviews/atomic-clock-direct-ratio-source-artifact-review.md`
- `docs/notes/atomic-clock-source-candidates.md`
- `data/atomic_clocks/source_manifest.yaml`
- `data/atomic_clocks/schema.md`

## Ranking Criteria

Fallback candidates are ranked by:

1. Direct-ratio status: primary direct optical-frequency ratio beats
   review-summary or derived-constraint rows.
2. Independence from the currently pinned Beloy 2021 / BACON source surface.
3. Species-pair usefulness for the load-bearing Beloy Yb/Sr row.
4. Recoverable access path: stable archive, DOI, supplement, license, checksum
   path, and retrieval-date plan.
5. Uncertainty semantics: total/statistical/systematic components,
   confidence-label wording, and per-systematic budget visibility.
6. Covariance visibility: explicit shared-systematic or correlation notes, or
   enough source text to justify a conservative covariance policy.
7. Version-drift risk: whether arXiv/preprint, publisher version, supplement,
   and evaluation tables can be compared before row publication.

## Ranked Fallback Candidates

| Rank | Candidate | Direct-ratio status | Access path status | Uncertainty semantics | Covariance visibility | Version-drift risk | Triage decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Pizzocaro et al. 2020 / INRIM Yb/Sr | Likely primary direct frequency-ratio measurement for the same neutral-clock species pair as Nemitz and Beloy. | Not pinned in this repository. Future task must verify DOI, any open archive or supplement, retrieval date, license, and checksum strategy before copying values. | Promising but unverified here; future task must confirm total, statistical, systematic, confidence-label, and bound-style fields from the source artifact. | Unknown until source artifact and supplement are reviewed. Treat as blocked if covariance/shared-systematic language exists but cannot be recovered. | Medium: publisher, preprint, and supplement agreement must be checked before rows. | Strongest fallback if Nemitz rows stay blocked. Same species-pair utility makes it the best direct replacement candidate. |
| 2 | Lange et al. 2021 / PTB Yb+ E3/Cs | Primary direct measurement candidate, but not a neutral Yb/Sr cross-check. It broadens the campaign to ion-to-microwave comparison semantics. | Not pinned. Future task must verify stable source locator, supplement availability, redistribution path, retrieval date, and checksum policy. | Potentially recoverable from a primary measurement paper, but this review does not inspect values or tables. | Must be reviewed carefully because Cs reference semantics and possible systematic links differ from neutral optical ratios. | Medium-high: row class may be direct, but benchmark use needs explicit separation from Yb/Sr replay goals. | Admissible as a breadth fallback, not as the first replacement for Nemitz's Yb/Sr replay role. |
| 3 | McGrew et al. 2018 / Yb-Sr-Hg ratio surface | Primary direct-ratio source candidate noted by earlier APL review as an alternative source-artifact lane. | Not pinned. Future task must verify exact archive, DOI, supplement, license, and checksum path. | Unknown in this task; source artifact review must verify row-level uncertainty fields before ingestion. | Unknown until the source artifact is reviewed; multi-ratio surfaces usually require explicit covariance or shared-systematic notes. | High for independence if the source surface overlaps the later Beloy/BACON ecosystem; future task must document lab/campaign independence before using it as a second-source replay control. | Useful fallback only if the independence and covariance story can be made explicit. Lower rank than Pizzocaro and Lange. |
| 4 | Schwarz et al. 2020 / PTB Yb+ E2/E3 | Direct transition-ratio candidate inside one ion species, but weaker as a cross-clock or cross-lab replay control. | Not pinned. Source artifact and supplement path would need a new review. | Unknown in this task. | Unknown; within-ion transition comparisons may have shared-systematic structure that must be made visible. | Medium. | Keep as a later specialist fallback; not preferred for resolving the Atomic second-source blocker. |
| 5 | BIPM / CCTF recommended frequency values | Review-summary or evaluation table, not a primary direct row by default. | Public evaluation path may exist, but exact source-list and combination rules must be recoverable. | Evaluation uncertainties are not enough unless source-level semantics and combination rules are explicit. | Correlation and combination visibility are the central blocker. | High because annual/recommended values can change and may mix source classes. | Not admissible as a direct second-source row unless reclassified as `review_summary` with full provenance and combination rules. |

## Recommended Fallback

If Nemitz 2016 remains row-blocked after maintainer-side version-drift review,
the next fallback ingestion task should target **Pizzocaro et al. 2020 /
INRIM Yb/Sr** first.

Rationale:

- It preserves the Yb/Sr species-pair replay role that made Nemitz useful.
- It is independent of the Beloy 2021 / BACON dataset surface in the way this
  campaign needs for single-source replay-risk reduction.
- It is more directly comparable to the Beloy Yb/Sr row than Yb+/Cs,
  Yb+ E2/E3, review-summary, or broad multi-ratio fallback candidates.
- Its blocker profile is ordinary source-curation work: artifact pinning,
  uncertainty-semantics review, covariance visibility, and version-drift
  comparison.

## Manifest Decision

No update is made to `data/atomic_clocks/source_manifest.yaml`.

The current manifest already records Nemitz as
`source_artifact_pinned_rows_blocked` and includes a planning-only note that
Pizzocaro 2020 and Lange 2021 remain candidates. This task does not pin a
source artifact, commit provenance, clear a row gate, or change source state,
so adding member-level manifest entries would overstate the readiness of the
fallbacks.

## Stop Conditions For Any Fallback Ingestion Task

A future fallback task must stop without adding rows if any of these conditions
fires:

- the source cannot be frozen with a stable locator, retrieval date, license
  note, and checksum or archive policy;
- publisher, preprint, and supplementary material disagree on row-defining
  fields;
- direct measurements are mixed with derived constants-variation constraints
  without explicit row-class separation;
- uncertainty semantics cannot be recovered for total, statistical,
  systematic, confidence-label, and bound-style fields;
- covariance, correlation, shared-systematic, or campaign-overlap language is
  present but cannot be represented explicitly;
- epoch or campaign-window semantics are ambiguous;
- the source is a review summary and the underlying source list, combination
  rules, and correlation policy are not recoverable.

## Output-Routing Summary

- **Task verdict:** `FALLBACK_SOURCES_TRIAGED_ROWS_BLOCKED`.
- **Canonical destination:** `docs/reviews/atomic-second-source-fallback-triage.md`.
- **Review tier:** `none`; this is source triage, not a `RESULT` or `PRED`
  artifact.
- **Gate A status:** not attempted.
- **Gate B status:** not attempted.
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Publication blocker:** no fallback source artifact is pinned, no values are
  copied, and no row-readiness gate is cleared.

## Limitations

- This review uses committed APL planning and prior review context only; it does
  not inspect live publisher pages, PDFs, supplements, or current archive state.
- Candidate ordering is therefore a source-curation priority ranking, not an
  admissibility verdict for value-bearing rows.
- Exact DOI, supplement, checksum, license, covariance, and uncertainty fields
  remain owned by future source-artifact tasks.
- The fallback ranking must not be cited as a composition, drift, constants,
  prediction, benchmark, or discovery claim.
