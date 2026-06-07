# Reviews Directory

`docs/reviews/` stores durable review records: campaign decisions,
result-promotion preflights, source-readiness reviews, negative-result memory,
maintainer-review protocols, and benchmark or dataset publication decisions.

These files are public repository memory. They are not generated task views and
should not be rewritten into a single rolling summary page.

## Retention Classes

Use these classes when adding a new review:

- Public scientific memory: result-promotion reviews, benchmark gates,
  falsification notes, negative-result cards, prediction/reveal readiness, and
  source-readiness decisions that affect what evidence may be cited later.
- Campaign reviews: campaign-level route decisions, scope decisions, lane
  synthesis, factory-fit reviews, and campaign-specific blocker maps.
- Source and dataset reviews: source artifact admissibility, citation/reuse
  posture, checksum/version readiness, row-schema readiness, and no-peek or
  holdout decisions.
- Architecture or workflow reviews: postmortems, PR/review-helper audits,
  agent-workflow decisions, and repository-maintenance reviews.
- Historical reviews: older decision records that remain useful as provenance
  even when a later task supersedes their route.

Do not delete or move older reviews just because the active recommendation has
changed. Preserve them as provenance and point to the newer review from the
newer task or PR.

## Naming And Future Grouping

Keep new review names topic-first and stable, for example:

- `materials-md0002-holdout-manifest-scaffold.md`
- `nuclear-f2-diagnostic-result-publication-preflight.md`
- `exoplanet-source-version-monitor-contract.md`

Do not start a bulk migration into subfolders until a link audit proves it is
safe. If the directory becomes too noisy, the preferred future grouping is by
topic subfolder such as `materials/`, `nuclear/`, `exoplanet/`, `atomic/`,
`quantum/`, and `workflow/`. Year or quarter folders are secondary; they help
archive cadence but make campaign trails harder to scan.

## Referencing Old Reviews

Review agents and Scientific Campaign Director notes should reference old
reviews by direct relative links. Do not duplicate old reviews into new summary
pages. A new review may include a short "Inputs reviewed" list and a route
decision, then point to the older files that carry the detailed provenance.

Generated task navigation lives under `docs/task-views/` and is refreshed by
automation after merge. Do not treat this README as a task board.
