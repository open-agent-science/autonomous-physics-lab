# Nuclear Shell-Axis Prospective Mini-Wave Review

**Task:** TASK-0297  
**Registry entries:** `PRED-0063` through `PRED-0068`  
**Target batch:** `shell-axis-balanced-001`  
**Evidence class:** prospective prediction registry  
**Live external fetch allowed:** `false`

This review records a bounded prospective shell-axis mini-wave after the
TASK-0296 target-batch design was reviewed and closed. It freezes prediction
values for later source-manifest review only. It does not fetch live
measurements, score a reveal, update claims, create canonical results, or
promote the shell-axis sandbox evidence.

## Inputs

- `TASK-0296`
- `data/nuclear_masses/shell_axis_target_batch_proposal.yaml`
- `docs/reviews/nuclear-shell-axis-registry-target-batch-design.md`
- `docs/reviews/nuclear-shell-axis-stress-scout-001.md`
- `docs/nuclear-prediction-reveal-protocol.md`
- `docs/nuclear-reveal-source-readiness-checklist.md`
- `results/EXP-0012/RUN-0001/result.yaml`

## Frozen Batch

All six entries use the same eight target nuclides:

| Nuclide | Z | N | A |
| --- | ---: | ---: | ---: |
| `V-70` | 23 | 47 | 70 |
| `Mn-75` | 25 | 50 | 75 |
| `Co-77` | 27 | 50 | 77 |
| `Cu-81` | 29 | 52 | 81 |
| `Ag-129` | 47 | 82 | 129 |
| `Cd-130` | 48 | 82 | 130 |
| `Sb-135` | 51 | 84 | 135 |
| `Cs-139` | 55 | 84 | 139 |

Quantity and units are frozen as `mass_excess_mev` in `MeV`.
`uncertainty_mev` is intentionally `null` for every row.

## Registered Entries

| Entry | Role | Frozen family | Origin | Max abs correction MeV | Mean abs correction MeV |
| --- | --- | --- | --- | ---: | ---: |
| `PRED-0063` | primary candidate | proton-axis Gaussian | `STRESS-SHELL-001` | 1.026111 | 0.620889 |
| `PRED-0064` | companion candidate | proton x neutron product | `STRESS-SHELL-002` | 1.548619 | 0.732834 |
| `PRED-0065` | diagnostic candidate | neutron-axis Gaussian | `STRESS-SHELL-003` | 1.604907 | 1.232618 |
| `PRED-0066` | negative control | sign-inverted proton-axis Gaussian | `STRESS-SHELL-004` | 1.026111 | 0.620889 |
| `PRED-0067` | negative control | near-null shell-axis correction | `STRESS-SHELL-006` | 0.000000 | 0.000000 |
| `PRED-0068` | reference control | frozen baseline reference | `RESULT-0015::model_fitted_semi_empirical` | 0.000000 | 0.000000 |

The corrections are applied to the baseline binding-energy estimate before
converting to mass excess. Positive shell correction increases binding energy
and therefore lowers the frozen mass-excess point estimate.

## Frozen Prediction Values

| Entry | V-70 | Mn-75 | Co-77 | Cu-81 | Ag-129 | Cd-130 | Sb-135 | Cs-139 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `PRED-0063` | 36.931305 | 25.975783 | -4.936102 | -18.028288 | -35.025159 | -45.094460 | -56.365918 | -74.972179 |
| `PRED-0064` | 37.123834 | 25.783563 | -5.458610 | -17.941462 | -35.217379 | -45.453574 | -56.279092 | -74.967856 |
| `PRED-0065` | 36.787753 | 24.748361 | -5.514899 | -17.975603 | -36.252581 | -45.994132 | -56.313233 | -75.894517 |
| `PRED-0066` | 37.686275 | 26.730753 | -2.883881 | -15.976067 | -34.270189 | -43.683990 | -54.313697 | -74.870004 |
| `PRED-0067` | 37.308790 | 26.353268 | -3.909991 | -17.002178 | -34.647674 | -44.389225 | -55.339807 | -74.921092 |
| `PRED-0068` | 37.308790 | 26.353268 | -3.909991 | -17.002178 | -34.647674 | -44.389225 | -55.339807 | -74.921092 |

## Source Boundary

- Source commit: `9e8d7d339a4f0f432e41689862a649eb029b8575`
- Baseline: `RESULT-0015::model_fitted_semi_empirical`
- Target design: `shell-axis-balanced-001`
- Training reference: `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- Reveal references: `docs/nuclear-prediction-reveal-protocol.md` and
  `docs/nuclear-reveal-source-readiness-checklist.md`

No live external measurement source was fetched, revealed, scored, or compared
during registration.

## Reveal Conditions

A future reveal can score these entries only after a maintainer-reviewed source
manifest exists, no-peek review passes, target matching is deterministic, and
measured, unmeasured, ambiguous, and source-absent rows are separated before
scoring. Partial reveal handling must preserve the paired controls and must
not rewrite these frozen prediction values.

## Validation Notes

The registry coverage summary was regenerated in
`data/nuclear_masses/nuclear_prediction_registry_coverage.yaml`. It now reports
60 committed registry entries and 261 target rows, with highest id
`PRED-0068`.

Tests recompute `PRED-0063` through `PRED-0068` from the frozen baseline
coefficients, shell-distance formulas, product correction, and target batch.

## Limitations

- These entries are prospective registry records only.
- The shell-axis evidence basis remains sandbox-grade until later reviewed
  reveal work compares eligible rows.
- The near-null and baseline reference controls intentionally duplicate values.
- No claim, result, knowledge entry, discovery wording, or success verdict is
  introduced here.

## Verdict

`REVIEW_READY` as a bounded prospective mini-wave registration. The next
scientific step is not scoring; it is a future source-manifest/no-peek reveal
task if and only if maintainers approve an eligible measurement source.
