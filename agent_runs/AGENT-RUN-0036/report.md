# AGENT-RUN-0036 - Exoplanet compact/sub-Neptune residual pilot

- Task: TASK-0390
- Campaign profile: exoplanet-mass-radius
- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Verdict: **SANDBOX_PASS**

## Boundary

Sandbox-only pilot using committed snapshot rows and frozen CK17 residuals. True-mass/transit-radius rows are the primary interpretable axis. Minimum-mass rows are diagnostic-only. The run does not infer composition, habitability, biosignatures, target priority, or universal planet laws.

## Eligible Axis

- Total rows in snapshot: 6291
- Pre-filter included: 6157
- Post-filter included: 4301
- Eligible true-mass/transit-radius rows: 1207
- Diagnostic minimum-mass/transit-radius rows: 2
- True-mass CK17 log10 RMSE = 0.158170, MAE = 0.104430, bias = -0.040844

## Generated Hypotheses

- Generated: 6; executed: 3
- Minimum hypothesis row count: 30
- Survival margin: 0.022
- Shuffled-label seed: 20260526

### CSN-001 - `compact_radius_lt1p5Re` (executed_hypothesis)

Compact true-mass/transit-radius rows with R/Re < 1.5 have larger frozen CK17 residual stress than the eligible true-mass surface and matched controls.

- Candidate slice: count 92, log10 RMSE 0.263350, MAE 0.162467, bias -0.146837

| control | count | log10 RMSE | log10 MAE | log10 bias |
| --- | ---: | ---: | ---: | ---: |
| per_class_median | 92 | 0.237670 | 0.138324 | -0.116977 |
| shuffled_label | 92 | 0.103012 | 0.082234 | -0.016860 |
| matched_size_neighbor | 92 | 0.174080 | 0.111370 | -0.063845 |

- **Outcome:** `residual_stress_above_eligible_and_controls`
- candidate log10 RMSE = 0.26335002767665594; eligible log10 RMSE = 0.1581701926744863; adverse control = per_class_median (log10 RMSE = 0.23767045104757828); survival margin = 0.022.

### CSN-002 - `sub_neptune_radius_1p5_4Re` (executed_hypothesis)

Sub-Neptune true-mass/transit-radius rows with 1.5 <= R/Re < 4 retain residual stress after class and sample-size controls.

- Candidate slice: count 340, log10 RMSE 0.204175, MAE 0.140835, bias -0.100080

| control | count | log10 RMSE | log10 MAE | log10 bias |
| --- | ---: | ---: | ---: | ---: |
| per_class_median | 340 | 0.188046 | 0.124063 | -0.046610 |
| shuffled_label | 340 | 0.169996 | 0.106734 | -0.053247 |
| matched_size_neighbor | 340 | 0.172277 | 0.128443 | -0.053553 |

- **Outcome:** `residual_stress_above_eligible_only`
- candidate log10 RMSE = 0.20417461029825093; eligible log10 RMSE = 0.1581701926744863; adverse control = per_class_median (log10 RMSE = 0.1880462173538035); survival margin = 0.022.

### CSN-003 - `compact_or_sub_neptune_radius_lt4Re` (executed_hypothesis)

The combined compact/sub-Neptune radius surface with R/Re < 4 is tested as a bounded high-stress envelope.

- Candidate slice: count 432, log10 RMSE 0.218126, MAE 0.145442, bias -0.110038

| control | count | log10 RMSE | log10 MAE | log10 bias |
| --- | ---: | ---: | ---: | ---: |
| per_class_median | 432 | 0.199651 | 0.127100 | -0.061596 |
| shuffled_label | 432 | 0.165763 | 0.109539 | -0.038015 |
| matched_size_neighbor | 432 | 0.172662 | 0.124807 | -0.055745 |

- **Outcome:** `residual_stress_above_eligible_only`
- candidate log10 RMSE = 0.21812633379546398; eligible log10 RMSE = 0.1581701926744863; adverse control = per_class_median (log10 RMSE = 0.1996507108287507); survival margin = 0.022.

### CSN-004 - `neptunian_sub_neptune_overlap` (generated_only)

Neptunian CK17-class rows inside the sub-Neptune radius range are generated as a narrower overlap hypothesis.

- Candidate slice: count 328, log10 RMSE 0.165159, MAE 0.123097, bias -0.083095

- **Outcome:** `generated_not_executed`
- Hypothesis generated and candidate stats recorded, but not executed under the 1-3 hypothesis execution budget.

### CSN-005 - `compact_subneptune_tight_radius_uncertainty` (generated_only)

Compact/sub-Neptune rows with reported radius relative uncertainty <= 5% are generated as a measurement-quality sensitivity hypothesis.

- Candidate slice: count 288, log10 RMSE 0.170218, MAE 0.120124, bias -0.077493

- **Outcome:** `generated_not_executed`
- Hypothesis generated and candidate stats recorded, but not executed under the 1-3 hypothesis execution budget.

### CSN-006 - `compact_subneptune_cool_host` (generated_only)

Compact/sub-Neptune rows around cool hosts (Teff < 5200 K) are generated as a selection-sensitive host-context hypothesis.

- Candidate slice: count 219, log10 RMSE 0.233687, MAE 0.143807, bias -0.111231

- **Outcome:** `generated_not_executed`
- Hypothesis generated and candidate stats recorded, but not executed under the 1-3 hypothesis execution budget.

## Output Routing

- Task verdict: `SANDBOX_PASS` if any executed hypothesis exceeds both the eligible surface and adverse controls by the configured margin; otherwise `INCONCLUSIVE`.
- Canonical destination: sandbox-only `agent_runs/` and review note.
- Review tier: none; no `RESULT-*`, `PRED-*`, claim, or knowledge file.
- Gate A: not attempted because this task requested sandbox evidence, not canonical result publication.
- Gate B: not attempted.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
