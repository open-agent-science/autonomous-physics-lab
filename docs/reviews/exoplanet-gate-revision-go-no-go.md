# Exoplanet Residual Gate-Revision Go/No-Go Review

- Task: `TASK-0648`
- Domain: Exoplanet Mass-Radius Benchmark
- Mode: planning-only scientific-policy decision (no row values)
- Decision: `PAUSE_EXECUTION_GATE_UNCHANGED`

## Scope

This review makes one deliberate routing decision for the Exoplanet Mass-Radius
campaign after the `EXO-0003` metadata trigger returned `WAIT`: keep the reopen
gate unchanged, propose a revised gate, or pause Exoplanet execution except
source monitoring. It reviews committed planning artifacts only. It does not
fetch rows, inspect planet values, run residual metrics, rank targets, or make
mass-radius, composition, habitability, or planet-law statements.

## Inputs reviewed

- [`exoplanet-exo0003-metadata-trigger-scout.md`](exoplanet-exo0003-metadata-trigger-scout.md) (`TASK-0629`, `WAIT`)
- [`exoplanet-third-snapshot-trigger-plan.md`](exoplanet-third-snapshot-trigger-plan.md)
- [`exoplanet-second-snapshot-negative-memory-routing.md`](exoplanet-second-snapshot-negative-memory-routing.md)
- [`second_snapshot_reopen_coverage_gate.yaml`](../../data/exoplanets/second_snapshot_reopen_coverage_gate.yaml) (`EXO-SECOND-SNAPSHOT-REOPEN-COVERAGE-GATE-0001`)

## Evidence summary (metadata-level only)

The `EXO-0003` metadata trigger scout used aggregate `COUNT(*)` checks only and
recorded:

- no raw source-row growth versus `EXO-0002` under the committed
  `default_flag = 1` query family (both at `6298` rows);
- every declared per-axis trigger slice misses its floor even under permissive
  aggregate counting (compact `127` < `150`; sub-Neptune `445` < `510`; Jovian
  `622` < `851`; hot-Jupiter `489` < `668`; minimum-mass lane `3`);
- the query endpoint is still executable, so there is no urgent failure to fix.

The reopen coverage gate is internally consistent: per-axis evaluation,
conservative pre-reveal floors (per-bin `30`, per-axis-slice `150`, `+50%`
material growth), mandatory mass-axis separation, and a decisive
null-baseline-competition gate. Its floors were frozen before row inspection.

## Options considered

1. **Keep gate unchanged (no other change).** Sound, but on its own it invites
   repeated metadata scouts that keep returning `WAIT`, which the campaign
   strategy explicitly warns against.
2. **Propose a revised (lower) gate.** Rejected. The floors were frozen before
   any row inspection. Lowering them now — after seeing that the current slices
   miss the targets — would convert a prospective gate into an exploratory,
   p-hacked one. The metadata scout already declined `GATE_REVISION_REVIEW` for
   the same reason. There is no new scientific question that a lower gate would
   answer; there is only smaller data.
3. **Pause execution except source monitoring (gate unchanged).** Selected.

## Decision and rationale

Route: **pause Exoplanet execution except source monitoring, with the reopen
coverage gate left unchanged.**

Rationale:

- The gate is scientifically sound and does not need revision; the blocker is
  insufficient source data, not a gate-design flaw.
- Re-running metadata scouts against an unchanged snapshot will keep returning
  `WAIT` and adds no information while creating quiet pressure to lower the gate.
- Lowering the gate to fit the current undersized slices would be p-hacking and
  is explicitly out of scope.
- Pausing preserves the existing negative/control memory as the campaign's
  durable contribution and keeps agent effort on campaigns that can move.

This is a scientific-policy decision, not a reveal. No gate floor, axis rule,
target freeze, or null-baseline requirement is changed.

## Source-monitoring trigger (the only Exoplanet work that should continue)

Exoplanet execution should resume only when a lightweight, metadata-only source
check shows a materially changed snapshot, specifically when **both** hold for
at least one declared axis/slice:

- raw `default_flag = 1` row count grows materially above the `EXO-0002`
  baseline of `6298`; and
- the eligible per-axis slice plausibly clears `gate_2`
  (`min_eligible_rows_per_axis_slice: 150`) and `gate_3`
  (`min_fractional_growth_vs_exo_0001: 0.5`) under permissive aggregate
  counting.

Until then, no value-bearing acquisition, no residual scoring, and no further
standalone metadata scouts are warranted. A monitoring cadence (for example,
quarterly, aligned with NASA Exoplanet Archive table releases) is sufficient.

No follow-up task is recommended, because the gate is **not** changing. A future
source-monitoring check that trips the trigger above should reopen the lane
through the existing `gate_0` material-snapshot path, not through a new gate.

## Stop conditions preserved

- Do not fetch, inspect, normalize, or score planet rows.
- Do not lower or otherwise amend the reopen coverage gate from this review.
- Do not make mass-radius law, composition, habitability, or target-priority
  statements.
- Do not treat permissive aggregate counts as eligible-row counts.

## Output routing

- Task verdict: `INCONCLUSIVE` for reopening; decisive `PAUSE_EXECUTION_GATE_UNCHANGED` for routing.
- Canonical destination: `docs/reviews/exoplanet-gate-revision-go-no-go.md`.
- Review tier: `none`; planning-only scientific-policy decision.
- Gate A status: not attempted; no `RESULT-*` or `PRED-*` artifact.
- Gate B status: not applicable.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change; the Exoplanet lane stays closed.
- Limitations / blockers: decision rests on metadata-level aggregates only; the
  lane remains blocked by insufficient source-row growth, and reopening requires
  a materially changed checksum-pinned snapshot under the existing gate.
