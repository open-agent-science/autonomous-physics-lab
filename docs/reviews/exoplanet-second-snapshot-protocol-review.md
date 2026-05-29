# Exoplanet Second-Snapshot Protocol Review

**Task:** `TASK-0393`  
**Protocol:** `docs/exoplanet-second-snapshot-no-live-fetch-protocol.md`  
**Review class:** protocol and workflow review  
**Status:** planning-only review

## Review Scope

This review checks whether the second-snapshot protocol preserves the
repository's no-peek and verification-first discipline before any future
PSCompPars refresh is acquired or scored.

The review does not fetch live data, inspect newer catalog rows, rerun the
existing benchmark, or promote claims.

## Verified Protocol Boundaries

The protocol correctly:

- separates pre-reveal freezing from future ingestion and scoring;
- preserves the existing ADQL query contract surface;
- requires explicit source URL and checksum recording;
- freezes baseline, metric, and slice definitions before acquisition;
- blocks post-hoc metric or slice tuning after row inspection;
- keeps true-mass and minimum-mass residual axes separated;
- preserves blocker outcomes as protocol-level failures rather than forcing
  positive interpretation;
- prevents the second snapshot from becoming a live-fetch convenience path.

## Required Freeze Surface Before Acquisition

The following benchmark surfaces must exist before any future second-snapshot
acquisition:

| frozen surface | required before acquisition |
| --- | --- |
| baseline family | yes |
| comparator baselines | yes |
| residual hypotheses | yes |
| metric set | yes |
| split definitions | yes |
| exclusion rules | yes |
| success/null/blocker rules | yes |
| output routing expectations | yes |

Changing any of these after row inspection invalidates the prospective/reveal
claim surface and downgrades the run to exploratory-only status.

## No-Peek Discipline Review

The protocol preserves the repository's no-peek discipline because:

- the query contract is frozen before acquisition;
- row inspection is not allowed before maintainer approval;
- baseline and metric selection cannot adapt to the new snapshot;
- the reveal path is separated from ingestion convenience;
- acquisition metadata and checksums become part of the review surface.

## Remaining Risks

Residual risks still exist even with a frozen reveal protocol:

- source-schema drift may break field mapping;
- archive-side corrections may change row semantics without obvious field-name
  changes;
- small-count slices may collapse below useful interpretability thresholds;
- host-star metadata incompleteness may still bias split-level interpretation;
- future ingestion tasks may accidentally mix exploratory analysis with frozen
  prospective evaluation.

These are protocol-management risks, not evidence of a scientific discovery or
failure.

## Recommended Follow-Up Sequence

The next preferred sequence is:

1. maintainer review and merge of the no-live-fetch protocol;
2. explicit pre-reveal package freeze task if additional benchmark surfaces are
   needed;
3. maintainer-approved ingestion-only task with checksum recording;
4. separate scoring/reveal task against the frozen benchmark package.

A combined ingestion-and-scoring task should be avoided unless the maintainer
explicitly approves a tightly controlled reveal flow.

## Verdict

`VALID_IN_RANGE`

The protocol is internally consistent for a conservative pre-reveal exoplanet
benchmark workflow and aligns with the repository's verification-first,
no-live-fetch, and no-post-hoc-tuning constraints.

## Output Routing Summary

- task verdict: `VALID_IN_RANGE`;
- canonical destination: protocol review documentation only;
- review tier: `none`;
- Gate A status: not attempted;
- Gate B status: not attempted;
- claim impact: no claim change;
- knowledge impact: no knowledge change;
- result artifact impact: no `results/` artifacts modified.
