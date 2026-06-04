# Exoplanet Second-Snapshot Ingestion Dry-Run — Review (TASK-0536)

Review note for `TASK-0536`. This is a deterministic ingestion-mechanics dry-run
for the Exoplanet Mass-Radius second-snapshot path. It does not fetch live
archive data, does not add real second-snapshot row values, does not score target
planets, and does not run mass-radius residual metrics.

## Inputs

- Task: `TASK-0536`
- No-live-fetch protocol: `docs/exoplanet-second-snapshot-no-live-fetch-protocol.md`
- Target freeze: `data/exoplanets/second_snapshot_target_freeze.yaml`
- First pinned snapshot metadata: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Existing deterministic loader fixture:
  `tests/fixtures/exoplanets/synthetic_pscomppars_snapshot.yaml`
- Prior synthesis:
  `docs/reviews/exoplanet-control-aware-go-no-go-synthesis.md`

## Dry-Run Method

The dry-run reuses the committed synthetic PSCompPars fixture instead of adding a
new real-data-like snapshot. That fixture is already explicitly marked as
`synthetic_dry_run`, has `live_external_fetch_allowed: false`, and carries a
fake-source warning. Reusing it keeps the task inside the no-live-fetch and
no-future-row-values boundary while still exercising the loader path.

The dry-run checks three ingestion properties:

1. **Checksum replay.** The embedded normalized checksum is replayed through
   `normalized_snapshot_checksum`, and checksum drift is already covered by the
   existing loader tests.
2. **Row-class separation.** The synthetic fixture preserves distinct true-mass,
   minimum-mass, model-derived, and excluded row states through
   `load_and_filter` summaries.
3. **No-peek separation.** The target-freeze artifact is loaded only for blocked
   field and axis metadata. No future row values, residual scores, target ranks,
   or reveal metrics are computed.

## Dry-Run Assertions Added

The `TASK-0536` tests cover:

- no live fetch and no future values in the target-freeze artifact;
- no prediction registry, canonical result, claim, or knowledge promotion from
  the target freeze;
- separate true-mass and minimum-mass target axes;
- blocked comparison fields are metadata-only and not scored;
- the synthetic fixture keeps true-mass, minimum-mass, model-derived, and
  excluded rows in separate states;
- checksum replay is deterministic for the dry-run fixture.

## Blocked Until Later

The following remain blocked until `TASK-0529` defines the reopen coverage gate
and a maintainer approves a real pinned second-snapshot task:

1. live NASA Exoplanet Archive or PSCompPars fetch;
2. real second-snapshot row normalization;
3. inspection of second-snapshot row values;
4. mass-radius residual metrics on a second snapshot;
5. compact-radius, host-context, or mass-quartile residual pilots;
6. target scoring or reveal-style evaluation;
7. prediction, result, claim, or knowledge promotion.

## Output Routing

- **Verdict:** `INCONCLUSIVE`
- **Artifact tier:** sandbox-only / ingestion-readiness evidence
- **Gate A / Gate B:** not attempted
- **Prediction registry impact:** none
- **Canonical result impact:** none
- **Claim impact:** none
- **Knowledge impact:** none

## Limitations

- This is a replayability and guardrail dry-run, not a scientific benchmark.
- The task does not pin or inspect a real second snapshot.
- The task does not change the Exoplanet campaign posture by itself.
- Local validation could not be executed in this connector-only session; the PR
  records the required validation commands for maintainer or CI replay.
