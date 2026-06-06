# Exoplanet Third-Snapshot Trigger Plan

Task: `TASK-0599`
Domain: Exoplanet mass-radius residuals
Mode: planning only
Verdict: `WAIT_FOR_MATERIAL_TRIGGER`

## Context

EXO-0002 did not materially reopen the declared Exoplanet residual lane. The
second-snapshot coverage check found only a small post-filter increase, no
slice cleared the reopen threshold, and the baseline replay was intentionally
not run. EXO-0003 should therefore be triggered by source/material evidence,
not by another routine catalog pull.

Inputs reviewed:

- `docs/reviews/exoplanet-second-snapshot-reopen-coverage-check.md`
- `docs/reviews/exoplanet-second-snapshot-baseline-replay-preflight.md`
- `data/exoplanets/second_snapshot_reopen_coverage_gate.yaml`
- `docs/runbooks/exoplanet-second-snapshot-acquisition-runbook.md`

## Acquisition Trigger

Do not acquire EXO-0003 until all of the following are true:

1. A new pinned PSCompPars source snapshot can be identified with a stable
   archive timestamp, release marker, or equivalent source-version evidence.
2. The intended query contract still matches the second-snapshot runbook, or a
   separate query-amendment review has already been accepted.
3. A metadata-only scout has credible evidence that at least one declared
   residual slice can clear both the absolute floor and the growth threshold.
4. The scout can be performed without inspecting target values, residuals,
   metrics, habitability labels, composition labels, or priority labels.

The elapsed-time trigger is conservative: wait for a material source-version
change or for a maintainer-approved metadata scout window after EXO-0002. Time
alone is not sufficient if the source has no evidence of material row growth.

## Slice Growth Thresholds

The current reopen gate requires a per-axis floor of 150 eligible rows and at
least 50 percent growth versus the EXO-0001 slice baseline. For EXO-0003, the
trigger should be evaluated slice-by-slice, with no pooling across slices.

Practical targets:

- Compact-radius slice: must reach at least 150 eligible rows.
- Sub-Neptune slice: must reach at least 510 eligible rows.
- Jovian slice: must reach at least 851 eligible rows.
- Hot-Jupiter slice: must reach at least 668 eligible rows.
- Low-count mass-axis slices: must still reach the 150-row floor and satisfy
  the 50 percent growth rule.

If the metadata scout cannot make one of these thresholds plausible, EXO-0003
should wait.

## Recommended Next Exoplanet Action

Recommended path: wait for a material source trigger, then run a metadata-only
EXO-0003 preflight task before any snapshot acquisition.

Allowed next task:

- Check only source version, row-count potential, query compatibility, checksum
  feasibility, and gate threshold plausibility.

Forbidden before the trigger clears:

- Live value-bearing snapshot acquisition.
- Residual metrics or baseline replay.
- Formula, habitability, composition, or target-priority claims.
- Relaxing the gate inside an acquisition task.

If maintainers want faster Exoplanet progress, the correct route is a separate
gate-revision review that changes the declared scientific target. It should not
be folded into EXO-0003 acquisition.

## Output Routing

This task does not authorize a dataset row package, benchmark replay, canonical
result, prediction, or claim. It only defines the trigger for a future
acquisition decision.

Review tier: source/reopen planning.
Gate A: not attempted.
Gate B: not applicable.
Promotion status: no promotion.
