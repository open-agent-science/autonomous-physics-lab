# Exoplanet Second-Snapshot Reopen Coverage Gate

**Task:** `TASK-0529`
**Campaign:** `exoplanet_mass_radius`
**Protocol class:** pre-reveal reopen-coverage gate
**Status:** no live fetch, no second snapshot acquired, no future rows inspected, no scoring
**Verdict:** `VALID_IN_RANGE` (protocol/gate definition only)

## Scope

`TASK-0515` recorded `NO_GO_PRESERVE_NEGATIVE_CONTROL_MEMORY`: no further
compact-radius residual or host-context pilot should run on the current pinned
PSCompPars snapshot, and the campaign should reopen a residual lane only after a
materially changed pinned snapshot **or an explicitly revised coverage gate**.

This document defines that gate. It declares the concrete, frozen coverage
criteria a future second snapshot must satisfy before any residual-hypothesis
lane may reopen. It uses committed repository memory only. It does not fetch
live data, add a second snapshot, inspect future rows, compute metrics, fit a
correction model, or create `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*`
artifacts.

It is upstream of any future reveal task and complements, without replacing:

- `docs/exoplanet-second-snapshot-no-live-fetch-protocol.md` (TASK-0393);
- `docs/reviews/exoplanet-second-snapshot-target-freeze.md` and
  `data/exoplanets/second_snapshot_target_freeze.yaml` (TASK-0482);
- `docs/reviews/exoplanet-control-aware-go-no-go-synthesis.md` (TASK-0515).

## Why A Coverage Gate Is Needed

Both the no-live-fetch protocol and the target freeze refer to a "pre-declared
sample-size floor" as a blocker condition, but neither file actually declares
the numeric floor. The target-freeze limitations explicitly defer it: "any
sample-size floors must be locked before future reveal scoring." This gate locks
those floors so a future reveal cannot pick them after seeing rows.

The decision context from the committed evidence:

- the compact-radius slice (`R < 1.5 R_earth`) has **92 eligible rows**
  (`TASK-0480`);
- mass-quartile bins on that slice fall **below the 30-row interpretation
  floor** (`TASK-0480`);
- no compact-radius host-context axis is benchmark-usable at the current
  interpretation floor (`TASK-0481`);
- nearest-radius null baselines match or beat the frozen CK17-style baseline in
  the compact, sub-Neptune, Jovian-radius, and hot-Jupiter true-mass slices
  (`TASK-0483`).

So the residual stress is both **control-sensitive** and **underpowered**.
Reopening therefore requires more eligible rows *and* survival against the null
family, evaluated per mass axis.

## Frozen Gate Criteria

All criteria are frozen before any future row inspection. They are evaluated
**per axis** — true-mass / transit-radius and minimum-mass (`M sin i`) /
transit-radius are never pooled. A lane reopens only on the specific axis and
slice that passes. Any change to these criteria after row inspection makes the
run exploratory rather than prospective, per the no-live-fetch protocol.

### Gate 0 — Materially changed pinned snapshot (prerequisite)

A residual lane may reopen only against a maintainer-approved, checksum-pinned
**new** PSCompPars snapshot acquired under the no-live-fetch protocol and the
target-freeze rule. Re-running on `EXO-0001` never reopens a lane, regardless of
the criteria below.

### Gate 1 — Per-bin interpretation floor

Any scored sub-slice (mass quartile, host-context bin, regime bin) must contain
**at least 30 eligible rows on the scored axis** to be interpreted. This reuses
the floor already declared by `TASK-0480`; bins below it are context-only and
cannot drive a verdict.

### Gate 2 — Per-axis scored-slice floor

For a **partitioned** residual lane (one that sub-divides a slice into bins) to
reopen on a given slice, that slice must contain **at least 150 eligible rows on
the scored axis**.

Rationale: a minimally informative partitioned analysis needs at least four
interpretable bins at the 30-row floor (4 x 30 = 120) plus margin for
exclusions. 150 is also materially above the current 92-row compact slice, so it
cannot be met by noise-level drift on the same targets.

### Gate 3 — Material-growth requirement

The eligible per-axis row count for the slice must **increase by at least 50%**
over the `EXO-0001` eligible count for that same slice and axis (and must still
clear the Gate 2 floor). For the compact true-mass slice this means materially
more than ~1.5 x 92 ≈ 138 eligible rows. A slice that was already above the
floor must still show real growth, not catalog churn, to count as "materially
changed."

### Gate 4 — True-mass / minimum-mass separation (hard)

Each axis is evaluated and reported separately, with separate row counts,
metrics, blockers, and wording. No pooled headline metric may average true-mass
and minimum-mass rows. A lane that passes on one axis does not authorize the
other axis.

### Gate 5 — Host-context coverage criterion

A host-context residual lane may reopen only if the chosen frozen host-context
field yields **at least 3 populated bins, each with at least 30 eligible rows on
the scored axis** (so at least ~90 rows spread across ≥3 bins, not concentrated
in one). This directly answers the `TASK-0481` finding that no host-context axis
was benchmark-usable at the current floor.

### Gate 6 — Null-baseline competition (decisive)

The pre-registered residual hypothesis must **beat the nearest-radius
null-baseline family** (the `TASK-0483` controls), not merely the frozen
CK17-style baseline, on the frozen slice and axis, using the frozen metric set
(log10-radius MAE/RMSE and, where uncertainty support exists, z-score
summaries). The improvement must exceed the slice's sampling/bootstrap
uncertainty.

If the null family matches or beats the hypothesis within uncertainty, the lane
**stops on control match** and does not reopen, regardless of how many rows it
has. This is the criterion that produced the original `NO_GO`.

## Lanes That Remain Do-Not-Repeat Unless The Gate Passes

The following lanes (from `TASK-0515`) stay do-not-repeat. They may reopen only
when Gate 0 holds and the lane's specific axis/slice passes Gates 1-6:

- another positive-framed CK17-style compact-radius residual pilot;
- compact-radius host-context coarse-bin audits at the current coverage floor;
- compact-radius mass-quartile localization on the same 92 eligible rows;
- positive interpretation of the coarse upper-mass-half diagnostic;
- an Exoplanet Research Factory candidate sprint that treats nearest-radius
  nulls as decorative controls;
- any pooled headline metric that mixes true-mass and minimum-mass rows.

The Research Factory adapter remains `CONTRACT_ONLY` until a future snapshot
clears this gate for a concrete lane.

## What Passing The Gate Does And Does Not Authorize

Passing the gate authorizes **reopening a bounded, pre-registered residual lane**
for scoring under the no-live-fetch protocol and target freeze. It does not by
itself authorize:

- any prediction-registry entry, claim, knowledge entry, or `RESULT-*` artifact;
- composition, habitability, biosignature, atmosphere, target-priority, or
  universal mass-radius-law wording;
- changing the baseline, metric set, slice thresholds, bin scheme, or null rule
  after row inspection;
- pooling mass axes.

A passing lane that then clears its pre-registered null and sample-size criteria
on the new snapshot may be described only as a bounded, slice-scoped prospective
result, per the no-live-fetch protocol's success wording.

## Machine-Readable Gate

The frozen numeric criteria are mirrored in
`data/exoplanets/second_snapshot_reopen_coverage_gate.yaml` for deterministic
reuse by a future reveal task, consistent with the
`second_snapshot_target_freeze.yaml` style. The YAML carries no future row
values.

## Limitations

- This is a gate definition, not a reveal: no second snapshot is acquired,
  inspected, or scored.
- The numeric floors (30-row per-bin, 150-row per-axis-slice, +50% growth, ≥3
  host-context bins) are conservative declarations frozen before reveal. A
  maintainer may revise them only through a pre-reveal amendment merged before
  acquisition, never after row inspection.
- The exact `pl_bmassprov` true-mass vs minimum-mass mapping and the per-slice
  `EXO-0001` baseline counts used by Gate 3 must be computed deterministically
  from committed `EXO-0001` rows by the future reveal task; this gate does not
  enumerate them.
- This gate does not resolve the normalized `EXO-0001` checksum gap noted by the
  promotion scorecard.

## Public Wording Boundary

Safe wording:

> The Exoplanet Mass-Radius campaign now has a frozen reopen-coverage gate. A
> residual lane reopens only on a materially changed, checksum-pinned snapshot
> whose eligible per-axis slice clears declared row-count floors and then beats
> the nearest-radius null baseline family. Until then the campaign preserves its
> control-sensitive negative result.

Do not infer composition, habitability, atmosphere, biosignatures, target
priority, anomalous physics, discovery, or a universal mass-radius law.

## Output Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `VALID_IN_RANGE` (protocol/gate definition; no scientific
  claim).
- **Canonical destination:** this review note plus
  `data/exoplanets/second_snapshot_reopen_coverage_gate.yaml`.
- **Review tier:** `none` (no `RESULT-*` or `PRED-*` artifact).
- **Gate A status:** not attempted. **Gate B status:** not attempted.
- **Claim impact:** no claim change. **Knowledge impact:** no knowledge change.
- **Result artifact impact:** no `results/` artifact created or modified.
- **Limitations / blockers:** no live fetch performed; floors are pre-reveal
  declarations amendable only before acquisition; per-slice `EXO-0001` baseline
  counts and `pl_bmassprov` mapping are deferred to the future reveal task.
</content>
