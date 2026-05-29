# Exoplanet Compact-Radius Benchmark Card

## Short Version

APL maintains a benchmark-only exoplanet mass-radius failure map on a pinned
NASA Exoplanet Archive PSCompPars snapshot. In the current sandbox audit set,
the compact-radius slice (`R < 1.5 R_earth`) is the strongest matched-control
survivor under a frozen Chen-Kipping-style baseline.

This is a reproducible benchmark diagnostic, not a claim about planet
composition, habitability, target priority, atmospheric physics, or a new
mass-radius law.

## What Was Tested

- A frozen Chen-Kipping-style mass-radius baseline was evaluated against the
  committed PSCompPars snapshot.
- The interpretable headline axis is true-mass planets with transit-radius
  measurements.
- The compact/sub-Neptune matched-control audit checks whether three radius
  slices survive matched cohorts, residual-shift controls, and deterministic
  negative controls.
- A separate Codex replay reproduced the compact-radius matched-control metrics
  exactly from committed inputs.

## Current Result

| Item | Current value |
| --- | ---: |
| Snapshot rows | `6291` |
| Eligible true-mass/transit-radius rows | `1207` |
| Eligible true-mass log10 RMSE | `0.15817019267448623` |
| Compact-radius slice | `R < 1.5 R_earth` |
| Compact-radius count | `92` |
| Compact-radius log10 RMSE | `0.2633500276766559` |
| Adverse control | `per_class_median` |
| Delta vs adverse control | `0.025679576629077605` |
| Control margin | `0.022` |
| Scorecard verdict | `BENCHMARK_SUMMARY_ONLY` |
| Claim-candidate eligibility | `BLOCK` |

Plain-language reading:

- The compact-radius slice is the only current slice that survives the matched
  and deterministic negative-control panel within the scorecard-approved
  wording boundary.
- The sub-Neptune slice (`1.5 <= R/R_earth < 4`) and combined compact/sub-Neptune
  slice (`R < 4 R_earth`) remain control-sensitive and inconclusive.
- The minimum-mass/transit-radius axis is structurally underpowered in this
  snapshot and is not part of the headline metric.

## Evidence Trail

- [Exoplanet campaign page](../campaigns/exoplanet-mass-radius.md)
- [Public science dashboard](../campaigns/public-science-dashboard.md)
- [Failure-map result-promotion scorecard](../reviews/exoplanet-failure-map-result-promotion-scorecard.md)
- [Scorecard machine-readable review](../reviews/exoplanet-failure-map-result-promotion-scorecard.review.yaml)
- [Compact/sub-Neptune matched-control audit](../reviews/exoplanet-compact-subneptune-matched-control-audit.md)
- [Independent compact-radius replay](../reviews/exoplanet-compact-radius-independent-replay.md)
- [AGENT-RUN-0042 metrics](../../agent_runs/AGENT-RUN-0042/metrics.json)
- [Pinned PSCompPars snapshot metadata](../../data/exoplanets/exo-0001-pscomppars-snapshot.yaml)

## Safe Wording

The following wording is safe for README summaries, issue comments, and
scientist-facing discussion:

> APL reports a benchmark-only compact-radius residual diagnostic on a pinned
> PSCompPars snapshot. The compact-radius slice (`R < 1.5 R_earth`) is the
> strongest current matched-control survivor under the frozen Chen-Kipping-style
> baseline, and an independent Codex replay reproduced the sandbox metrics
> exactly. The scorecard verdict is `BENCHMARK_SUMMARY_ONLY`, not a claim
> candidate.

## Forbidden Wording

Do not say or imply that this artifact:

- identifies a new exoplanet mass-radius law;
- predicts habitability, biosignatures, planet composition, atmospheric
  properties, or target priority;
- globally falsifies Chen-Kipping or any broad mass-radius relation;
- proves that compact planets have anomalous physics;
- creates a `CLAIM-*`, `KNOW-*`, `PRED-*`, or canonical `RESULT-*` artifact.

## Limitations

- The evidence remains sandbox benchmark memory, not a promoted result or
  claim.
- The normalized-snapshot checksum gap remains open until `TASK-0446` or a
  successor task closes it.
- The scorecard still requires human review before any public interpretation is
  strengthened beyond `BENCHMARK_SUMMARY_ONLY`.
- Matched controls are diagnostic slices, not causal adjustments.
- The benchmark uses a single committed snapshot; a future second-snapshot
  protocol is needed before cross-snapshot or reveal-style claims.
- The current evidence is tied to true-mass/transit-radius rows and keeps
  minimum-mass rows out of headline metrics.

## Next Validation Steps

- Close the normalized PSCompPars snapshot checksum gap (`TASK-0446`).
- Keep the evidence card linked from the public science dashboard and campaign
  page.
- Use the second-snapshot no-live-fetch protocol before any future
  external-comparability or prediction-readiness story.
- Keep all follow-up work benchmark-only unless a later maintainer-reviewed
  task explicitly authorizes a stronger output class.

## Output Routing

- Task verdict: `BENCHMARK_SUMMARY_ONLY`
- Canonical destination: `docs/results/exoplanet-compact-radius-benchmark-card.md`
- Review tier: `none`
- Gate A status: not attempted
- Gate B status: not applicable to a canonical result; independent sandbox
  replay exists in `docs/reviews/exoplanet-compact-radius-independent-replay.md`
- Claim impact: no claim change
- Knowledge impact: no knowledge change
- Result artifact impact: no canonical `RESULT-*` created or edited
