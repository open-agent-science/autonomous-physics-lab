# Exoplanet Second-Snapshot Negative-Memory Routing

**Task:** `TASK-0597`
**Campaign:** Exoplanet Mass-Radius
**Status:** negative-memory routing (docs-only)
**Verdict:** `not_applicable` (preservation/routing task)

## Purpose

This note routes the already-decided `EXO-0002` second-snapshot closed-lane
decision into the existing campaign and public surfaces, instead of creating a
new dashboard, duplicate digest, or any RESULT / CLAIM / PRED / KNOW artifact. It
records where the negative/control memory now lives and restates the no-scoring
boundary. It does not re-derive metrics; the canonical evidence already exists in
the reviews linked below.

## Canonical Closed-Lane Evidence (unchanged)

- [Second-snapshot reopen coverage check](exoplanet-second-snapshot-reopen-coverage-check.md)
  — `TASK-0580`, verdict `RESIDUAL_LANE_REMAINS_CLOSED`. No declared axis/slice
  cleared the frozen reopen coverage gate; gate stayed `BLOCKED` with zero lane
  reopens.
- [Second-snapshot baseline replay preflight](exoplanet-second-snapshot-baseline-replay-preflight.md)
  — `TASK-0582`, verdict `BLOCKED_BY_REOPEN_COVERAGE_GATE`. The frozen baseline
  replay was intentionally not run because the coverage gate failed.
- [EXO-0001/EXO-0002 snapshot delta audit](exoplanet-exo0001-exo0002-snapshot-delta-audit.md)
  — `TASK-0581`, verdict `VALID_IN_RANGE`. `EXO-0002` adds seven post-filter rows
  and one true-mass transit-radius row.
- [Second-snapshot row-class drift review](exoplanet-second-snapshot-row-class-drift.md)
  — the two overlapping rows that changed `mass_class`.

## Closed-Lane Decision (summary for routing)

- Loader counts: `EXO-0002` has 6298 raw rows, 6164 pre-filter and 4308
  post-filter included rows (1208 true-mass, 2 minimum-mass), versus `EXO-0001`'s
  4301 post-filter rows (1207 true-mass, 2 minimum-mass).
- Material growth: only seven post-filter rows and one true-mass transit-radius
  row were added. The compact-radius slice stayed at 92 rows, below the 150-row
  floor with zero growth; the minimum-mass axis remained at two rows.
- Gate blockers: `gate_2_per_axis_slice_floor`, `gate_3_material_growth`,
  `gate_5_host_context_coverage`. The reopen coverage gate stayed `BLOCKED`;
  zero lanes reopened.

## No-Scoring Boundary

`EXO-0002` did **not** authorize any of the following, and they remain closed
until a materially changed, reviewed snapshot or an explicitly revised coverage
gate exists:

- CK17 residual replay or residual-metric scoring on `EXO-0002`;
- null-baseline competition on `EXO-0002`;
- composition, habitability, atmospheric, or target-priority inference;
- prediction-registry entries, claim promotion, or canonical RESULT publication.

The Exoplanet Research Factory adapter remains contract-only until a materially
changed input surface is reviewed.

## Preserved Surfaces

The negative/control memory is preserved in existing surfaces, not a new digest:

- [Exoplanet Mass-Radius campaign](../campaigns/exoplanet-mass-radius.md) — the
  closed-lane memory paragraph and the campaign history item now read as settled
  closed-lane memory with the no-scoring boundary, replacing the prior
  active-to-do framing.
- [Public science dashboard](../campaigns/public-science-dashboard.md) — the
  Exoplanet row now states the closed-lane memory is preserved and the only
  forward step is planning an `EXO-0003` acquisition trigger (`TASK-0599`).

## Only Forward Step

Plan an `EXO-0003` acquisition trigger (`TASK-0599`). No Exoplanet residual
scoring is authorized before that path produces a reviewed, materially changed
snapshot or the coverage gate is explicitly revised.

## Output Routing Summary

- Task verdict: `not_applicable` (preservation/routing task).
- Canonical destination: existing
  [campaign](../campaigns/exoplanet-mass-radius.md) and
  [dashboard](../campaigns/public-science-dashboard.md) surfaces; this routing note.
- Review tier: `none`.
- Gate A status: `not_applicable`.
- Gate B status: `not_applicable`.
- Claim impact: `none` (no claim change).
- Knowledge impact: `none` (no knowledge change; no duplicate digest created).
- Result impact: `no RESULT artifact created`.
