# Exoplanet Source-Version Monitor Run

Task: `TASK-0715`
Domain: Exoplanet Mass-Radius Benchmark
Mode: metadata-only source-version monitor
Verdict: `NO_NOTIFY`

## Monitor Record

```text
monitor_run_utc: 2026-06-13T15:42:17Z
pinned_snapshot_id: EXO-0002
query_contract_sha256: 28b8baf9f14e4ba544658fccbad5ef1271a21f91228afe8afff4db968512acf8
release_notes_marker: PS 1.1b and PSCompPars 1.1d dated 2025-10-16; release-notes page last updated 2026-05-27
raw_default_flag_count: 6298
slice_aggregates: {compact: 132, sub_neptune: 461, jovian: 646, hot_jupiter: 494, min_mass: 5}
tap_available: true
notify_class: NO_NOTIFY
recommended_action: Keep EXO-0003 acquisition paused; no metadata scout or query-amendment review is triggered by this run.
value_bearing_fetch_performed: false
```

## Scope

This run followed the monitor contract in
`docs/runbooks/exoplanet-source-version-monitor-contract.md`. It used only NASA
Exoplanet Archive release-note markers and aggregate TAP `COUNT(*)` queries. No
individual planet rows, names, row previews, residuals, target rankings,
habitability labels, composition labels, or acquisition payloads were fetched,
stored, logged, or inspected.

Inputs reviewed:

- `docs/runbooks/exoplanet-source-version-monitor-contract.md`
- `data/exoplanets/second_snapshot_reopen_coverage_gate.yaml`
- `docs/reviews/exoplanet-exo0003-metadata-trigger-scout.md`
- `data/exoplanets/snapshot_plans/pscomppars_query.adql`
- `data/exoplanets/snapshot_plans/pscomppars_mass_provenance_map.yaml`
- NASA Exoplanet Archive PS/PSCompPars release notes:
  `https://exoplanetarchive.ipac.caltech.edu/docs/ps-pscp_release_notes.html`
- NASA Exoplanet Archive TAP sync endpoint:
  `https://exoplanetarchive.ipac.caltech.edu/TAP/sync`

## Aggregate Metadata Counts

The monitor used aggregate TAP queries only.

| Metadata aggregate | Count |
| --- | ---: |
| `raw_default_flag` | `6298` |
| `published_confirmed` | `6224` |
| `true_mass_transit_radius` | `1509` |
| `minimum_mass_transit_radius` | `5` |
| `compact_true_mass` | `132` |
| `sub_neptune_true_mass` | `461` |
| `jovian_true_mass` | `646` |
| `hot_jupiter_true_mass` | `494` |

The raw default-flag aggregate exactly matches the pinned EXO-0002 baseline of
`6298`. The release-note marker remains within the pinned reference family: PS
table release `1.1b` and PSCompPars release `1.1d`, both dated
`2025-10-16`, with the release-notes page last updated `2026-05-27`.

The permissive slice aggregates still miss the declared TASK-0599 trigger
targets:

| Declared trigger target | Required | Metadata aggregate | Trigger plausible |
| --- | ---: | ---: | --- |
| Compact true-mass slice | at least `150` | `132` | no |
| Sub-Neptune true-mass slice | at least `510` | `461` | no |
| Jovian true-mass slice | at least `851` | `646` | no |
| Hot-Jupiter true-mass slice | at least `668` | `494` | no |
| Minimum-mass transit-radius lane | at least `150` and growth | `5` | no |

## Decision

Notify class: `NO_NOTIFY`.

Rationale:

1. The raw default-flag count equals the EXO-0002 pinned baseline.
2. No declared slice aggregate crosses the practical trigger floor.
3. TAP aggregate queries remain available for the committed metadata checks.
4. No source-version marker observed in this run creates a PS/PSCompPars query
   amendment or acquisition trigger.

EXO-0003 acquisition remains paused. This monitor does not open acquisition
work, residual scoring, gate revision, query amendment, or claim promotion.

## Output Routing

Canonical destination: this review note,
`docs/reviews/exoplanet-source-version-monitor-run-2026-06-13.md`.

Review tier: source-version monitor only. Gate A is not attempted because no
dataset, metric, prediction, or result artifact is produced. Gate B is not
applicable.

Claim impact: none. No exoplanet mass-radius law, composition inference,
habitability inference, target priority, prediction, or planet-discovery claim
is created.

Knowledge impact: workflow memory only. The lane remains closed until a
materially changed source snapshot, accepted metadata scout, or separately
reviewed gate amendment exists.

Publication blocker: EXO-0003 acquisition remains blocked by insufficient
metadata evidence for material row growth.
