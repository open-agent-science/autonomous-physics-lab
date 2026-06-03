# Exoplanet Second-Snapshot Acquisition Package

**Task:** `TASK-0554`
**Campaign:** Exoplanet Mass-Radius
**Status:** review-ready acquisition package; no live fetch
**Verdict:** `SECOND_SNAPSHOT_ACQUISITION_PACKAGE_READY`

## Scope

This task prepares a source-acquisition package for a future NASA Exoplanet
Archive / PSCompPars second snapshot. It follows the acquisition lane while
keeping acquisition, row curation, and residual scoring separate.

Reviewed inputs:

- `docs/reviews/exoplanet-second-snapshot-ingestion-dry-run.md`
- `data/exoplanets/second_snapshot_reopen_coverage_gate.yaml`
- `data/exoplanets/second_snapshot_target_freeze.yaml`
- `docs/exoplanet-second-snapshot-no-live-fetch-protocol.md`
- `docs/source-acquisition-lane.md`
- `data/exoplanets/snapshot_plans/pscomppars_query.adql`

No live archive request was run. No second-snapshot row values were fetched,
committed, inspected, summarized, or scored.

## Package Added

`docs/runbooks/exoplanet-second-snapshot-acquisition-runbook.md` records the
future approved acquisition procedure:

- exact TAP endpoint;
- exact committed query contract;
- selected fields;
- required acquisition manifest fields;
- row-class rules for true mass, minimum mass, model-derived, and excluded
  rows;
- checksum and no-peek attestation requirements;
- stop conditions.

`data/exoplanets/second_snapshot_manifest.yaml` records the metadata-only
manifest shape for the future acquisition:

- `live_fetch_performed: false`;
- source surface and query-contract SHA-256;
- selected fields grouped by identity, planet observables, and host context;
- planned raw and normalized artifact paths;
- checksum fields left `null` until an approved acquisition fills them;
- row-class separation rules;
- blockers that prevent scoring until timestamp, row counts, checksums, and
  no-peek attestation are present.

## Frozen Query Contract

The future acquisition must use:

- endpoint: `https://exoplanetarchive.ipac.caltech.edu/TAP/sync`;
- query file: `data/exoplanets/snapshot_plans/pscomppars_query.adql`;
- query SHA-256:
  `4364d83855a19cfc638f733b4aea32c1873af9b78338f0b84a9b25f51e0de3e4`.

Any query change requires a pre-acquisition amendment PR before the fetch.

## Boundaries Preserved

- No real second-snapshot rows were added.
- No target values were inspected.
- No mass-radius residual metric, target score, prediction, result, claim, or
  knowledge artifact was created.
- True-mass, minimum-mass, model-derived, and excluded rows remain separate
  states.
- The package does not auto-unblock a future reveal; it gives the maintainer or
  approved acquisition actor the exact manifest fields to fill.

## Output-Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `SECOND_SNAPSHOT_ACQUISITION_PACKAGE_READY`; not a
  benchmark result or scientific claim.
- **Canonical destination:** `docs/runbooks/exoplanet-second-snapshot-acquisition-runbook.md`,
  `data/exoplanets/second_snapshot_manifest.yaml`, and this review note.
- **Review tier:** `none`.
- **Gate A status:** not attempted.
- **Gate B status:** not attempted.
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge promotion.
- **Result artifact impact:** no `results/` artifact created or modified.
- **Limitations / blockers:** future acquisition still needs maintainer
  approval, live retrieval, raw and normalized checksums, row counts, and
  no-peek attestation before any row curation or scoring task can use the
  second snapshot.
