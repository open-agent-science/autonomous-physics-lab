# Exoplanet True-Mass Residual Slice Audit

**Task:** `TASK-0369`
**Agent run:** `AGENT-RUN-0034`
**Input benchmark:** `AGENT-RUN-0032` / `TASK-0361`
**Snapshot:** `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
**Evidence class:** sandbox-only residual slice audit
**Verdict:** `INCONCLUSIVE`

## Scope

This audit isolates the `true_mass_with_transit_radius` axis because that is
the only TASK-0361 axis with enough rows and a positive comparison against the
per-class median null floor. It uses committed snapshot and benchmark
artifacts only.

This task does not fetch live archive data, refit the frozen Chen-Kipping
baseline, add a prediction-registry entry, write a canonical `RESULT-*`, edit
claims or knowledge, or create habitability, biosignature, target-priority, or
discovery claims.

## Axis Boundary

| axis | eligible rows | CK log10 RMSE | null log10 RMSE | status |
| --- | ---: | ---: | ---: | --- |
| `true_mass_with_transit_radius` | 1207 | 0.158170 | 0.242713 | Supported audit surface. |
| `minimum_mass_with_transit_radius` | 2 | 0.207728 | 0.031917 | Sparse diagnostic only; excluded from headline metrics. |

The campaign-level interpretation remains `INCONCLUSIVE` because the
minimum-mass axis is not a usable success surface.

## Planet Class And Mass Regime

| slice | count | CK log10 MAE | CK log10 RMSE | CK bias | reading |
| --- | ---: | ---: | ---: | ---: | --- |
| terran | 39 | 0.068160 | 0.124740 | -0.018562 | Weak: count-limited. |
| neptunian | 588 | 0.130712 | 0.182790 | -0.064723 | Robust failure region. |
| jovian | 580 | 0.080224 | 0.130933 | -0.018134 | Comparatively stable. |

The clearest mass-regime failure is the neptunian segment. The terran segment
is lower-error but too small for broad wording.

## Radius Regime

| slice | count | CK log10 MAE | CK log10 RMSE | CK bias | reading |
| --- | ---: | ---: | ---: | ---: | --- |
| compact `<1.5 R_earth` | 92 | 0.162467 | 0.263350 | -0.146837 | Robust failure region. |
| sub-Neptune `1.5-4 R_earth` | 340 | 0.140835 | 0.204175 | -0.100080 | Robust failure region. |
| intermediate `4-8 R_earth` | 97 | 0.159223 | 0.202360 | -0.028622 | Supported but weaker. |
| giant `>=8 R_earth` | 678 | 0.070459 | 0.091450 | +0.001496 | Comparatively stable. |

Radius regime is the strongest failure-map axis. The compact and sub-Neptune
rows carry the largest CK residuals, while the giant-radius rows are the most
stable large slice.

## Detection Method And Mass Provenance

| slice | count | CK log10 RMSE | CK bias | reading |
| --- | ---: | ---: | ---: | --- |
| transit | 1205 | 0.158272 | -0.040788 | Dominant supported surface. |
| transit timing variation | 2 | 0.074741 | -0.074548 | Sample-size blocked. |

The true-mass audit is almost entirely a transit-row audit. That is a catalog
selection limitation, not a planet-law result. `minimum_mass_msini` rows stay
out of headline metrics.

## Host-Star Context

| host bin | count | CK log10 MAE | CK log10 RMSE | CK bias | reading |
| --- | ---: | ---: | ---: | ---: | --- |
| M `<3900 K` | 140 | 0.106719 | 0.193176 | -0.076306 | Supported but selection-sensitive. |
| K `3900-5200 K` | 235 | 0.133804 | 0.197335 | -0.093840 | Supported failure region. |
| G `5200-6000 K` | 492 | 0.099721 | 0.146600 | -0.047956 | Supported comparison region. |
| F `6000-7500 K` | 285 | 0.082267 | 0.113904 | +0.020702 | Comparatively stable. |
| hot `>=7500 K` | 14 | 0.132853 | 0.145129 | +0.127844 | Sample-size blocked. |
| missing Teff | 41 | 0.129101 | 0.174934 | -0.016061 | Metadata-limited. |

K-host and M-host rows look worse than F/G rows under the frozen baseline, but
the audit treats that as a selection-sensitive residual pattern.

## Uncertainty Band

| uncertainty band | count | CK log10 MAE | CK log10 RMSE | CK bias | reading |
| --- | ---: | ---: | ---: | ---: | --- |
| tight `<=5%` | 194 | 0.123886 | 0.187349 | -0.078760 | Supported failure region. |
| moderate `5-15%` | 627 | 0.099488 | 0.156610 | -0.039395 | Supported comparison band. |
| loose `>15%` | 378 | 0.093840 | 0.122158 | -0.013640 | Catalog-selection diagnostic. |
| uncertainty missing | 8 | 0.520279 | 0.544066 | -0.520279 | Metadata blocked. |

The tightest reported-uncertainty band has higher RMSE than the moderate and
loose bands. That blocks simplistic "better measurement means better baseline"
wording and points to selection effects in the committed catalog.

## Robust, Weak, And Blocked Patterns

Robust residual patterns:

- the true-mass/transit-radius axis clears the null floor overall;
- compact-radius and sub-Neptune-radius rows are the strongest supported
  failure regions;
- neptunian mass-class rows are the clearest mass-regime failure surface;
- giant-radius rows are comparatively stable.

Weak patterns:

- terran and intermediate-radius slices are useful review context but remain
  count-limited;
- host-star slices are selection-sensitive;
- uncertainty-band behavior is diagnostic because tighter reported
  uncertainty does not monotonically reduce residuals.

Blocked patterns:

- minimum-mass rows remain outside headline metrics;
- transit-timing, hot-host, and uncertainty-missing slices are sample-size or
  metadata blocked;
- radius-only and model-inferred rows are not scored as mass-radius residual
  successes.

## Follow-Up Boundary

A future task may use this audit to scope a bounded residual hypothesis around
compact/sub-Neptune radii or neptunian mass-class behavior. It must keep
minimum-mass rows separate, preserve count thresholds, and avoid habitability,
biosignature, target-priority, discovery, or new planet-law wording.
