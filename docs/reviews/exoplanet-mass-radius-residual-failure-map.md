# Exoplanet Mass-Radius Residual Failure Map

**Task:** `TASK-0362`  
**Baseline task:** `TASK-0361`  
**Agent run:** `AGENT-RUN-0032`  
**Campaign profile:** `exoplanet-mass-radius`  
**Snapshot:** `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`  
**Evidence class:** sandbox-only residual packaging  
**Verdict:** `INCONCLUSIVE`

## Scope

This review packages the residual structure from the first committed
Exoplanet Mass-Radius benchmark into a failure map. It does not rerun the
catalog ingestion, fetch live archive rows, refit the Chen-Kipping baseline,
add prediction entries, promote claims, or create habitability,
biosignature, or target-priority outputs.

The input benchmark compared a frozen Chen-Kipping 2017 piecewise median
baseline against a per-class median null baseline on the committed
PSCompPars snapshot.

## Dataset And Axis Boundary

| surface | value |
| --- | ---: |
| Total snapshot rows | 6291 |
| Pre-filter included rows | 6157 |
| Post-filter included rows | 4301 |
| Mass relative-uncertainty threshold | 0.30 |
| Radius relative-uncertainty threshold | 0.15 |

Residual axes remain separated:

| axis | CK log10 RMSE | null log10 RMSE | delta null - CK | row count | interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| `true_mass_with_transit_radius` | 0.158170 | 0.242713 | +0.084543 | 1207 | CK beats the null floor on this axis. |
| `minimum_mass_with_transit_radius` | 0.207728 | 0.031917 | -0.175811 | 2 | Blocked as an interpretable success metric because `M sin i` has only two post-filter rows here and the null floor is lower. |

The overall benchmark verdict stays `INCONCLUSIVE`: one eligible axis clears
the null floor, while the separate minimum-mass axis does not.

## Failure Map By Planet Class

### True-Mass With Transit Radius

| class | count | CK log10 MAE | CK log10 RMSE | CK bias | status |
| --- | ---: | ---: | ---: | ---: | --- |
| terran | 39 | 0.068160 | 0.124740 | -0.018562 | Weak: useful table row, but sample is small. |
| neptunian | 588 | 0.130712 | 0.182790 | -0.064723 | Robust failure region: largest class-level RMSE and negative bias. |
| jovian | 580 | 0.080224 | 0.130933 | -0.018134 | More stable than neptunian, but still not a claim surface. |

### Minimum-Mass With Transit Radius

| class | count | CK log10 MAE | CK log10 RMSE | CK bias | status |
| --- | ---: | ---: | ---: | ---: | --- |
| neptunian | 2 | 0.152214 | 0.207728 | -0.152214 | Blocked by count and `M sin i` semantics. |

## Failure Map By Radius Regime

The radius-regime map is the clearest true-mass failure surface.

| radius regime | count | CK log10 MAE | CK log10 RMSE | CK bias | status |
| --- | ---: | ---: | ---: | ---: | --- |
| compact `<1.5 R_earth` | 92 | 0.162467 | 0.263350 | -0.146837 | Robust failure region; highest RMSE among supported radius regimes. |
| sub-Neptune `1.5-4 R_earth` | 340 | 0.140835 | 0.204175 | -0.100080 | Robust failure region; aligns with the transition surface flagged by the regime scout. |
| intermediate `4-8 R_earth` | 97 | 0.159223 | 0.202360 | -0.028622 | Weak-to-moderate; enough rows for review but not enough for strong wording. |
| giant `>=8 R_earth` | 678 | 0.070459 | 0.091450 | +0.001496 | Comparatively stable residual region. |

Negative bias means the observed radius is smaller than the frozen
Chen-Kipping radius in log space on average. That is a residual-map
diagnostic, not a new planet-composition claim.

## Detection Method And Mass Provenance

| axis | split | count | CK log10 RMSE | CK bias | status |
| --- | --- | ---: | ---: | ---: | --- |
| true mass | transit | 1205 | 0.158272 | -0.040788 | Dominant supported surface. |
| true mass | transit timing variation | 2 | 0.074741 | -0.074548 | Sample-size blocked. |
| minimum mass | transit | 2 | 0.207728 | -0.152214 | Sample-size and `M sin i` blocked. |

Mass provenance is not averaged across axes. The true-mass axis has 1207
eligible true-mass rows; the minimum-mass axis has only two eligible
`minimum_mass_msini` rows after the quality filter.

## Host-Star Context

Host effective-temperature bins are available for most true-mass rows, but
some bins remain small.

| host bin | count | CK log10 MAE | CK log10 RMSE | CK bias | status |
| --- | ---: | ---: | ---: | ---: | --- |
| M `<3900 K` | 140 | 0.106719 | 0.193176 | -0.076306 | Supported, but selection effects remain likely. |
| K `3900-5200 K` | 235 | 0.133804 | 0.197335 | -0.093840 | Supported failure region. |
| G `5200-6000 K` | 492 | 0.099721 | 0.146600 | -0.047956 | Supported comparison region. |
| F `6000-7500 K` | 285 | 0.082267 | 0.113904 | +0.020702 | More stable comparison region. |
| hot `>=7500 K` | 14 | 0.132853 | 0.145129 | +0.127844 | Sample-size blocked. |
| host Teff missing | 41 | 0.129101 | 0.174934 | -0.016061 | Metadata-limited. |

These bins should be treated as residual diagnostics because host-star
properties correlate with discovery and follow-up selection.

## Uncertainty Filter Map

The true-mass axis does not improve monotonically with tighter reported
uncertainty. The tightest reported-uncertainty rows have higher RMSE than the
moderate or loose bands, which makes catalog-selection and follow-up bias a
first-order limitation.

| uncertainty band | count | CK log10 MAE | CK log10 RMSE | CK bias | status |
| --- | ---: | ---: | ---: | ---: | --- |
| tight `<=5%` | 194 | 0.123886 | 0.187349 | -0.078760 | Supported failure region; likely affected by target-selection history. |
| moderate `5-15%` | 627 | 0.099488 | 0.156610 | -0.039395 | Supported comparison band. |
| loose `>15%` | 378 | 0.093840 | 0.122158 | -0.013640 | Counterintuitively lower RMSE; interpret as catalog-selection diagnostic. |
| uncertainty missing | 8 | 0.520279 | 0.544066 | -0.520279 | Blocked by count and metadata incompleteness. |

The two-row minimum-mass axis is not interpreted as an uncertainty trend.

## Robust, Weak, And Blocked Patterns

Robust residual-map patterns:

- the true-mass/transit-radius axis clears the per-class median null floor on
  overall log10 RMSE;
- neptunian and sub-Neptune/compact radius regimes are the most visible
  failure regions in the supported true-mass axis;
- giant-radius rows are comparatively stable under the frozen baseline.

Weak patterns:

- terran, intermediate-radius, hot-host, and transit-timing slices are useful
  context but require careful count-aware wording;
- host-star bins may reflect follow-up selection as much as astrophysical
  structure;
- uncertainty-band behavior is diagnostic because tighter reported
  uncertainty does not automatically reduce residuals.

Blocked patterns:

- the minimum-mass axis cannot support success wording: it has two eligible
  rows after filtering, uses `M sin i`, and the null baseline beats CK;
- radius-only and model-inferred rows are not scored as mass-radius residual
  successes;
- no habitability, biosignature, composition-law, target-priority, prediction
  registry, claim, or canonical result wording is authorized by this map.

## Follow-Up Boundary

A later task may audit the true-mass surface more narrowly by planet class,
radius regime, host-star bin, or uncertainty band. It must preserve the
true-mass/minimum-mass separation and report sample-size blockers explicitly.

The next preferred exoplanet follow-up is a true-mass residual slice audit,
not a broad claim or a tuned replacement baseline.
