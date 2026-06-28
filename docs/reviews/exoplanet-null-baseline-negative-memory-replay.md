# Exoplanet Null-Baseline Negative-Control Memory Replay

- Task: `TASK-0867`
- Source memory: `AGENT-RUN-0050` and
  `docs/reviews/exoplanet-null-baseline-family-audit.md`
- Replay command:
  `python3 scripts/run_exoplanet_null_baseline_family_audit.py --snapshot data/exoplanets/exo-0001-pscomppars-snapshot.yaml --out <untracked-replay-output>/metrics.json --report <untracked-replay-output>/report.md --agent-run <untracked-replay-output>/agent_run.yaml --limitations <untracked-replay-output>/limitations.md --preflight <untracked-replay-output>/preflight.md --review-summary <untracked-replay-output>/review_summary.md --review <untracked-replay-output>/review.md`
- Verdict: `NEGATIVE_CONTROL_MEMORY_REPLAY_PASS`

## Scope

This is a cross-tool replay of the exoplanet null-baseline family audit on the
committed `EXO-0001` PSCompPars snapshot. It does not fetch live rows, inspect a
new value-bearing snapshot, refit the CK-style baseline, add candidate formulas,
or create any `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*` artifact.

The replay checks the existing negative/control memory: in the highlighted
true-mass slices, deterministic nearest-radius null controls match or beat the
frozen CK17-style baseline, so the campaign remains monitor-only until the
snapshot or coverage gate materially changes.

## Replay Drift

The replayed JSON is semantically identical to the stored metrics up to normal
floating-point serialization noise. Maximum absolute numeric drift across all
numeric leaves was `3.89e-16`; no field drifted by more than `1.0e-12`.

| Axis | Slice | Published rows | Replay rows | Published CK17 RMSE | Replay CK17 RMSE | Best null | Classification | Drift |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- | ---: |
| `true_mass_with_transit_radius` | `compact_radius_lt1p5Re` | `92` | `92` | `0.263350` | `0.263350` | `nearest_radius_neighbor` | `null_family_matches_or_beats_ck17` | `<1e-12` |
| `true_mass_with_transit_radius` | `sub_neptune_radius_1p5_4Re` | `340` | `340` | `0.204175` | `0.204175` | `nearest_radius_neighbor` | `null_family_matches_or_beats_ck17` | `<1e-12` |
| `true_mass_with_transit_radius` | `jovian_radius_8_16Re` | `567` | `567` | `0.083354` | `0.083354` | `nearest_radius_neighbor` | `null_family_matches_or_beats_ck17` | `<1e-12` |
| `true_mass_with_transit_radius` | `hot_jupiter_period_lt10d_radius_ge8Re` | `445` | `445` | `0.069788` | `0.069788` | `nearest_radius_neighbor` | `null_family_matches_or_beats_ck17` | `<1e-12` |
| `minimum_mass_with_transit_radius` | `compact_radius_lt1p5Re` | `0` | `0` | `n/a` | `n/a` | `None` | `underpowered_slice` | `0` |
| `minimum_mass_with_transit_radius` | `sub_neptune_radius_1p5_4Re` | `2` | `2` | `0.207728` | `0.207728` | `uncertainty_band_median` | `underpowered_slice` | `<1e-12` |
| `minimum_mass_with_transit_radius` | `jovian_radius_8_16Re` | `0` | `0` | `n/a` | `n/a` | `None` | `underpowered_slice` | `0` |
| `minimum_mass_with_transit_radius` | `hot_jupiter_period_lt10d_radius_ge8Re` | `0` | `0` | `n/a` | `n/a` | `None` | `underpowered_slice` | `0` |

The true-mass highlighted slices all keep the same classification:
`null_family_matches_or_beats_ck17`. The minimum-mass slices remain
underpowered.

## Negative-Control Interpretation

Replay supports preserving the existing public-safe negative/control memory:

> On the committed EXO-0001 PSCompPars snapshot, nearest-radius null baselines
> match or beat the frozen CK17-style baseline in the highlighted true-mass
> slices. The apparent residual stress is control-sensitive, so APL should not
> reopen a positive residual-scoring lane on this snapshot.

The nearest-radius neighbor is a diagnostic control that uses observed radius;
it is not a prospective model. Its role is to show that the highlighted CK-style
residual surfaces are control-sensitive, not to provide a deployable exoplanet
predictor.

## Result-Promotion Recommendation

No canonical promotion in this task. Preserve this as negative/control memory
until a later maintainer-approved task explicitly packages it as a negative
`RESULT-*` or a future snapshot materially changes the row coverage and control
surface.

Recommended current state:

- keep exoplanet residual discovery monitor-only;
- preserve true-mass/minimum-mass separation;
- preserve nearest-radius null competition in any later factory or scoring
  runner;
- do not pool true-mass and minimum-mass rows into headline metrics;
- do not infer composition, habitability, atmosphere, target priority,
  discovery, or a universal mass-radius law.

## Output Routing

- Canonical destination: `docs/reviews/exoplanet-null-baseline-negative-memory-replay.md`.
- Review tier: none; replay/routing note only.
- Gate A: not attempted; no canonical result artifact.
- Gate B-like status: `PASS` for memory replay with only sub-`1e-12`
  floating-point serialization drift.
- Claim impact: none.
- Prediction impact: none.
- Knowledge impact: none.
- Result impact: no mutation.
- Publication blocker: maintainer-approved promotion task required before any
  negative/control memory becomes a canonical `RESULT-*`; otherwise keep it as
  sandbox/review memory.

## Final Verdict

`AGENT-RUN-0050` replays successfully. The exoplanet null-baseline memory
remains valid as control-sensitive negative evidence for the current EXO-0001
snapshot, not as a claim or scoring-lane restart.
