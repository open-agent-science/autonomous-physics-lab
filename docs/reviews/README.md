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

The accepted cutover policy is shard-forward:

- existing flat-root files under `docs/reviews/` stay at their current public
  provenance paths;
- new review notes go under a topic subfolder such as `materials/`, `nuclear/`,
  `exoplanet/`, `atomic/`, `quantum/`, `stellar/`, `textbook/`, `frb/`,
  `thermoml/`, `dimensional/`, `particle/`, `workflow/`, `release/`, or
  `cross-campaign/`;
- `README.md` remains the only routine flat-root file added or edited here;
- navigation should be recursive and on demand, for example:

```bash
python3 scripts/apl_reviews_inventory.py
```

Do not commit a generated `INDEX.md`, manifest, or rolling inventory for review
navigation. Review inventory is query output, not a second source of truth.

Do not bulk-move the legacy flat-root files as routine cleanup. A physical
migration would require a dedicated audited task that updates every hard and
soft reference in the same rollout.

## Archive Policy

Archive logically before archiving physically. When an older review is
superseded, prefer a short status note in the file or in the newer review that
points to the replacement, for example `Status: superseded by
docs/reviews/<domain>/<new-note>.md`. Do not move legacy reviews into an
`archive/` directory just because they are old; their paths are part of the
provenance trail.

## Referencing Old Reviews

Review agents and Scientific Campaign Director notes should reference old
reviews by direct relative links. Do not duplicate old reviews into new summary
pages. A new review may include a short "Inputs reviewed" list and a route
decision, then point to the older files that carry the detailed provenance.

Generated task navigation lives under `docs/task-views/` and is refreshed by
automation after merge. Do not treat this README as a task board.
