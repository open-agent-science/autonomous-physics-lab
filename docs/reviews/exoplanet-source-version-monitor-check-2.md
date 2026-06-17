# Exoplanet Source-Version Monitor Check 2

Task: `TASK-0781`
Domain: Exoplanet Mass-Radius Benchmark
Mode: metadata-only source-version monitor
Verdict: `NO_NOTIFY`

## Monitor Record

```text
monitor_run_utc: 2026-06-17T22:04:26Z
pinned_snapshot_id: EXO-0002
query_contract_sha256: 28b8baf9f14e4ba544658fccbad5ef1271a21f91228afe8afff4db968512acf8
release_notes_marker: PS 1.1b current and PSCompPars 1.1d current, both dated 2025-10-16; release-notes page reachable with HTTP 200 and no Last-Modified header returned
raw_default_flag_count: 6298
slice_aggregates: {compact: 132, sub_neptune: 461, jovian: 646, hot_jupiter: 494, min_mass: 5}
tap_available: true
notify_class: NO_NOTIFY
recommended_action: Keep EXO-0003 acquisition paused; no metadata scout, gate review, query amendment, residual scoring, or acquisition task is triggered by this run.
value_bearing_fetch_performed: false
```

## Scope

This run followed the source-version monitor contract in
`docs/runbooks/exoplanet-source-version-monitor-contract.md`. It used only NASA
Exoplanet Archive release-note markers and aggregate TAP `COUNT(*)` queries.
No individual rows, names, row previews, residuals, rankings, acquisition
payloads, or value-bearing PS/PSCompPars records were fetched, stored, logged,
or inspected.

Inputs reviewed:

- `docs/runbooks/exoplanet-source-version-monitor-contract.md`
- `docs/reviews/exoplanet-source-version-monitor-run-2026-06-13.md`
- `docs/reviews/exoplanet-exo0003-trigger-decision-after-monitor.md`
- `docs/exoplanet-second-snapshot-no-live-fetch-protocol.md`
- `data/exoplanets/second_snapshot_reopen_coverage_gate.yaml`
- `data/exoplanets/snapshot_plans/pscomppars_query.adql`
- `data/exoplanets/snapshot_plans/pscomppars_mass_provenance_map.yaml`
- NASA Exoplanet Archive PS/PSCompPars release notes
- NASA Exoplanet Archive TAP sync endpoint

## Monitor Command Context

The monitor used bounded metadata checks only:

- Release-note page reachability and current release marker search.
- TAP aggregate availability through the public sync endpoint.
- Aggregate `COUNT(*)` queries over `ps` with `default_flag = 1`.
- True-mass and minimum-mass aggregate lanes kept separate by the committed
  `pl_bmassprov` mapping.

The TAP queries returned only integer counts. The local sandbox blocked the
first outbound request, so the same metadata-only requests were rerun with
network approval. No row-valued response was requested.

## Aggregate Metadata Counts

| Metadata aggregate | Count | Prior monitor | Trigger floor |
| --- | ---: | ---: | ---: |
| `raw_default_flag` | `6298` | `6298` | exact EXO-0002 baseline |
| `published_confirmed` | `6224` | `6224` | context only |
| `true_mass_transit_radius` | `1509` | `1509` | context only |
| `minimum_mass_transit_radius` | `5` | `5` | `150` and growth |
| `compact_true_mass` | `132` | `132` | `150` |
| `sub_neptune_true_mass` | `461` | `461` | `510` |
| `jovian_true_mass` | `646` | `646` | `851` |
| `hot_jupiter_true_mass` | `494` | `494` | `668` |

The raw default-flag aggregate exactly matches the EXO-0002 pinned baseline.
The current release markers remain in the same current-version family observed
by the prior monitor: PS `1.1b` and PSCompPars `1.1d`, both dated
`2025-10-16`. The slice aggregates are unchanged from the prior monitor and do
not reach their trigger floors.

## Decision

Notify class: `NO_NOTIFY`.

Rationale:

1. The raw default-flag count equals the pinned EXO-0002 baseline.
2. No declared slice aggregate crosses its practical trigger floor.
3. TAP aggregate queries remain available for the committed metadata checks.
4. The observed current source-version markers do not require a metadata scout,
   gate review, query amendment, acquisition, or residual replay.

EXO-0003 remains monitor-only. Residual scoring stays closed.

## Output Routing

Canonical destination: this review note,
`docs/reviews/exoplanet-source-version-monitor-check-2.md`.

Review tier: source-version monitor only. Gate A is not attempted because no
dataset, metric, prediction, or result artifact is produced. Gate B is not
applicable.

Prediction or reveal readiness impact: none. The run does not create a
prediction, reveal task, acquisition authorization, result artifact, claim
artifact, or knowledge-promotion artifact.

Publication blocker: EXO-0003 acquisition remains blocked by insufficient
metadata evidence for material source growth or a reviewed gate change.
