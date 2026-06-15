# Exoplanet EXO-0003 Trigger Decision After Monitor

**Task:** `TASK-0745`
**Campaign:** Exoplanet Mass-Radius Benchmark
**Mode:** planning only; no row values, no residual metrics, no acquisition
**Decision:** `EXO0003_REMAINS_MONITOR_ONLY_NO_SCOUT`

## Scope

This note decides whether the `TASK-0715` source-version monitor result should
open an `EXO-0003` metadata scout, a coverage-gate amendment, or any residual
work. It uses only the committed monitor output, the source-version monitor
contract, and the frozen second-snapshot reopen coverage gate.

This task does not fetch, inspect, normalize, store, or score value-bearing
planet rows. It does not run CK17-style replay, residual metrics, habitability,
composition, atmosphere, target-priority, prediction, planet-law, `RESULT-*`,
`PRED-*`, claim, or knowledge work.

## Inputs Reviewed

- [TASK-0715 monitor run](exoplanet-source-version-monitor-run-2026-06-13.md)
- [Exoplanet source-version monitor contract](../runbooks/exoplanet-source-version-monitor-contract.md)
- [EXO-0003 trigger plan](exoplanet-third-snapshot-trigger-plan.md)
- [Gate-revision go/no-go](exoplanet-gate-revision-go-no-go.md)
- [Second-snapshot reopen coverage gate](../../data/exoplanets/second_snapshot_reopen_coverage_gate.yaml)
- [Exoplanet campaign page](../campaigns/exoplanet-mass-radius.md)

## Monitor Evidence

`TASK-0715` recorded `NO_NOTIFY`:

| Signal | Observed | Trigger status |
| --- | ---: | --- |
| `raw_default_flag` count | 6298 | equals pinned `EXO-0002` baseline |
| compact true-mass aggregate | 132 | below 150 floor |
| sub-Neptune true-mass aggregate | 461 | below 510 practical target |
| Jovian true-mass aggregate | 646 | below 851 practical target |
| hot-Jupiter true-mass aggregate | 494 | below 668 practical target |
| minimum-mass transit-radius aggregate | 5 | below 150 floor |
| TAP aggregate availability | true | no query-breakage trigger |
| release marker | PS 1.1b / PSCompPars 1.1d, 2025-10-16 | no source-version trigger |

The raw row count did not grow above `EXO-0002`, no declared slice crossed its
metadata trigger floor, the committed query family remained available, and no
source-version marker required query-amendment review.

## Decision

`EXO-0003` remains **monitor-only**.

Do not open a metadata-only scout from this monitor result. The monitor contract
requires `NO_NOTIFY` when all comparators are unchanged, and explicitly says not
to open tasks, PRs, or acquisition work in that case.

Do not amend the coverage gate. The frozen gate remains scientifically sound:
per-axis separation, a 150-row per-axis slice floor, 50% material growth, host
context coverage floors, and null-baseline competition are the right blockers.
Lowering those floors after seeing continued shortfall would turn a prospective
gate into an exploratory one.

Do not run residual or baseline replay. The current monitor output is metadata
evidence for continued pause, not a material source snapshot.

## Future Trigger Policy

The next Exoplanet action should be only a scheduled or maintainer-approved
source-version monitor run under the existing contract. A metadata scout becomes
justified only if a future monitor records at least one `NOTIFY_*` class:

| Future notify class | Follow-up allowed |
| --- | --- |
| `NOTIFY_SOURCE_VERSION_CHANGE` | metadata scout for source/version and aggregate gates |
| `NOTIFY_RAW_ROW_GROWTH` | metadata scout comparing slice aggregates to frozen floors |
| `NOTIFY_SLICE_THRESHOLD_PLAUSIBLE` | `EXO-0003` metadata preflight, still no acquisition |
| `NOTIFY_QUERY_BREAKAGE` | infrastructure/query review, not acquisition |
| `NOTIFY_QUERY_AMENDMENT_CANDIDATE` | separate query-amendment review |

Elapsed time alone is not a trigger. A metadata scout must still avoid
value-bearing rows, planet names, row previews, residuals, target lists, and
scientific-interest ranking.

## Task Recommendation

No future metadata-only scout task is recommended now. No coverage-gate
amendment task is recommended now.

`TASK-0745` should move to `REVIEW_READY` with the campaign posture set to
monitor-only. The next executor-facing Exoplanet work should wait for a future
monitor notification or explicit maintainer direction outside the current
`NO_NOTIFY` result.

## Output Routing Summary

- **Task verdict:** `EXO0003_REMAINS_MONITOR_ONLY_NO_SCOUT`.
- **Canonical destination:** this review note,
  `docs/reviews/exoplanet-exo0003-trigger-decision-after-monitor.md`.
- **Review tier:** metadata-trigger planning review; no `RESULT-*` or `PRED-*`
  artifact.
- **Gate A status:** not attempted.
- **Gate B status:** not applicable.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Publication blocker:** Exoplanet residual scoring remains blocked until a
  future source-version monitor records a material `NOTIFY_*` trigger and a
  maintainer-approved metadata preflight clears the frozen gate without row
  peeking.
