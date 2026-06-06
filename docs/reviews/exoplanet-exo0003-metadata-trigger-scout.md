# Exoplanet EXO-0003 Metadata Trigger Scout

Task: `TASK-0629`
Domain: Exoplanet Mass-Radius Benchmark
Mode: metadata-only source trigger scout
Verdict: `WAIT`

## Scope

This scout checks whether a future `EXO-0003` snapshot is scientifically
justified before any value-bearing PS/PSCompPars acquisition. It performs only
source-document and aggregate `COUNT(*)` checks. It does not fetch, commit,
normalize, preview, or inspect planet rows. It does not compute residuals,
baseline metrics, target rankings, habitability labels, composition labels, or
claims.

Inputs reviewed:

- `docs/reviews/exoplanet-third-snapshot-trigger-plan.md`
- `docs/reviews/exoplanet-second-snapshot-negative-memory-routing.md`
- `data/exoplanets/second_snapshot_reopen_coverage_gate.yaml`
- `docs/runbooks/exoplanet-second-snapshot-acquisition-runbook.md`
- NASA Exoplanet Archive Archive 2.0 release notes:
  `https://exoplanetarchive.ipac.caltech.edu/docs/ps-pscp_release_notes.html`
- NASA Exoplanet Archive PS/PSCompPars column definitions:
  `https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html`
- NASA Exoplanet Archive PSCompPars calculation notes:
  `https://exoplanetarchive.ipac.caltech.edu/docs/pscp_calc.html`

Metadata check date: `2026-06-06`.

## Source Version And Query Compatibility

The NASA Exoplanet Archive release notes show current Planetary Systems (`PS`)
and Planetary Systems Composite Parameters (`PSCompPars`) table versions dated
October 16, 2025, and TAP service support for both `PS` and `PSCompPars`.
Archive documentation was last updated May 27, 2026.

The committed APL query contract remains byte-bound to:

```text
data/exoplanets/snapshot_plans/pscomppars_query.adql
```

That contract selects from `ps`, not `pscomppars`:

```sql
FROM ps
WHERE default_flag = 1
```

The live TAP endpoint accepted aggregate queries against `ps`, and the required
fields used by the committed query remain queryable for metadata purposes.
However, the naming mismatch is still important: if maintainers intend EXO-0003
to switch from the committed `ps` query to the literal `pscomppars` table, that
requires `QUERY_AMENDMENT_REVIEW` before any acquisition. This scout does not
make that amendment because the current count evidence does not justify snapshot
preflight.

Checksum feasibility remains good for a future acquisition: the TAP endpoint can
return a deterministic CSV response under the existing runbook shape, and the
existing EXO-0002 manifest already records raw and normalized checksums for the
same query-contract family. No checksum is created here because no value-bearing
snapshot is fetched.

## Aggregate Metadata Counts

The scout used aggregate TAP `COUNT(*)` queries only. No row values were fetched
or committed.

| Metadata aggregate | Count |
| --- | ---: |
| `ps` rows with `default_flag = 1` | `6298` |
| `Published Confirmed` rows | `6224` |
| True-mass transit-radius aggregate | `1449` |
| Minimum-mass transit-radius aggregate | `3` |
| Compact true-mass radius slice, `R < 1.5 R_earth` | `127` |
| Sub-Neptune true-mass radius slice, `1.5 <= R < 4 R_earth` | `445` |
| Jovian true-mass radius slice, `8 <= R < 16 R_earth` | `622` |
| Hot-Jupiter true-mass slice, `P < 10 d` and `8 <= R < 16 R_earth` | `489` |

These are permissive metadata aggregates over current `ps` fields, not the
committed APL loader's full post-filter result. They are useful as trigger
upper-bound checks only.

For comparison, EXO-0002 already recorded `6298` raw rows. The current
`default_flag = 1` aggregate therefore shows no raw source-row growth relative
to the last committed snapshot. The permissive slice aggregates also fail the
practical trigger targets from `TASK-0599`:

| Declared trigger target | Required | Metadata aggregate | Trigger plausible |
| --- | ---: | ---: | --- |
| Compact true-mass slice | at least `150` | `127` | no |
| Sub-Neptune true-mass slice | at least `510` | `445` | no |
| Jovian true-mass slice | at least `851` | `622` | no |
| Hot-Jupiter true-mass slice | at least `668` | `489` | no |
| Minimum-mass transit-radius lane | at least `150` and growth | `3` | no |

Because these permissive aggregate counts already miss the trigger targets, a
full value-bearing snapshot would not be justified by this scout.

## Decision

Recommended outcome: `WAIT`.

Rationale:

1. There is no raw-row source growth versus EXO-0002 under the committed
   `default_flag = 1` query family.
2. No declared residual slice plausibly clears the floor/growth trigger targets
   even under permissive aggregate counting.
3. The query remains executable, so there is no urgent endpoint failure to
   repair.
4. The `ps` versus `PSCompPars` naming mismatch should be handled only if a
   future source trigger first makes acquisition scientifically worthwhile.

`SNAPSHOT_PREFLIGHT_READY` is not selected. `QUERY_AMENDMENT_REVIEW` is not
selected because the current trigger does not require a query change before the
lane stays closed. `GATE_REVISION_REVIEW` is not selected because the existing
negative/control memory remains internally consistent; lowering the gate would
be a separate scientific-policy decision, not a metadata-trigger result.

## Output Routing

Canonical destination: this review note.

Review tier: source/reopen planning only. Gate A is not attempted because no
dataset, residual metric, prediction, or result is produced. Gate B is not
applicable.

Claim impact: none. No exoplanet mass-radius law, composition inference,
habitability inference, target priority, prediction, or planet-discovery claim
is created.

Knowledge impact: none. The Exoplanet lane remains closed until a materially
changed source snapshot or a separately reviewed gate amendment exists.

Publication blocker: EXO-0003 acquisition remains blocked by insufficient
metadata evidence for material row growth.
