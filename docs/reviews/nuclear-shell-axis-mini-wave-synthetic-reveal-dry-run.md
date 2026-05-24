# Nuclear Shell-Axis Mini-Wave Synthetic Reveal Dry-Run

**Task:** TASK-0304
**Status:** review (dry-run plumbing only; no real reveal scored)
**Target batch:** `shell-axis-balanced-001`
**Registry entries:** `PRED-0063` through `PRED-0068`
**Inputs:**

- `examples/nuclear_shell_axis_mini_wave_synthetic_reveal.yaml`
- `tests/test_nuclear_shell_axis_mini_wave_reveal.py`
- `physics_lab/engines/nuclear_prediction_reveal.py`
- `prediction_registry/nuclear_masses/PRED-0063.yaml` .. `PRED-0068.yaml`
- `docs/reviews/nuclear-shell-axis-prospective-mini-wave-review.md`
- `docs/reviews/nuclear-shell-axis-mini-wave-source-preflight.md` (TASK-0303)
- `docs/reviews/nuclear-prediction-synthetic-reveal-dry-run.md` (TASK-0273)
- `docs/nuclear-prediction-reveal-protocol.md`
- `docs/nuclear-reveal-source-readiness-checklist.md`

## Scope

This dry-run specialises the generic nuclear synthetic-reveal harness
for the `shell-axis-balanced-001` mini-wave so that a future real reveal
task (TASK-0305 or successor) inherits a pre-reviewed scoring shape for:

- six prediction registry entries scored side-by-side (three candidate
  families plus three controls);
- partial-reveal handling across measured, non-measured, predates, and
  unrevealed rows;
- candidate-vs-baseline and candidate-vs-negative-control reporting;
- registry-immutability checks during scoring.

All values used here are **fabricated toy values** committed to the
fixture under
`examples/nuclear_shell_axis_mini_wave_synthetic_reveal.yaml`. They are
not nuclear-mass measurements. They must not be cited as measured,
evaluated, or extrapolated values. They are scoring plumbing only.

The dry-run does not pin an external source, does not fetch live data,
does not edit any `PRED-*.yaml` entry, does not score a real reveal, and
does not unblock TASK-0305.

## Fixture Shape

The toy source ships six rows that span four eligibility classes:

| Nuclide | `value_semantics` | per-row override | expected class |
| --- | --- | --- | --- |
| `V-70` | `measured_synthetic` | — | `ELIGIBLE_SYNTHETIC` |
| `Mn-75` | `measured_synthetic` | — | `ELIGIBLE_SYNTHETIC` |
| `Ag-129` | `measured_synthetic` | — | `ELIGIBLE_SYNTHETIC` |
| `Sb-135` | `measured_synthetic` | — | `ELIGIBLE_SYNTHETIC` |
| `Co-77` | `extrapolated_synthetic` | — | `NON_MEASURED_VALUE_ONLY` |
| `Cd-130` | `measured_synthetic` | `source_available_utc: 2026-05-19` | `SOURCE_PREDATES_REGISTRATION` |
| `Cu-81` | (omitted from source) | — | `TARGET_NOT_REVEALED` |
| `Cs-139` | (omitted from source) | — | `TARGET_NOT_REVEALED` |

The fixture-level `source_available_utc` is `2026-06-15T00:00:00Z`,
which is after each entry's `registered_at_utc` of `2026-05-20T00:00:00Z`.
The `Cd-130` row overrides this with `2026-05-19T00:00:00Z` to exercise
the per-row predates branch deterministically.

The four eligible nuclides cover both the proton-rich light region
(`V-70`, `Mn-75`) and the N=82 / above-N=82 heavy region (`Ag-129`,
`Sb-135`), giving the dry-run two coverage strata without any real
measurement.

Synthetic toy values are placed close to the primary candidate's
predicted values:

| Nuclide | `PRED-0063` predicted (MeV) | toy synthetic (MeV) | `PRED-0063` signed error (MeV) |
| --- | ---: | ---: | ---: |
| `V-70` | 36.931305 | 37.431305 | -0.500000 |
| `Mn-75` | 25.975783 | 26.275783 | -0.300000 |
| `Ag-129` | -35.025159 | -34.625159 | -0.400000 |
| `Sb-135` | -56.365918 | -55.765918 | -0.600000 |

This placement is intentional: it lets the dry-run demonstrate the
candidate-vs-negative-control shape (the sign-inverted control should
register a *larger* MAE than the primary candidate, and the test suite
asserts exactly that).

## Coverage Shape

`run_synthetic_reveal_dry_run` returns the following coverage for the
six registry entries × eight target nuclides = 48 target rows:

| Field | Value |
| --- | ---: |
| `entry_count` | 6 |
| `target_rows` | 48 |
| `eligible_rows` | 24 |
| `unrevealed_rows` | 12 |
| `ineligible_rows` | 12 |

Eligibility-status breakdown (counts across all six entries):

| Status | Count |
| --- | ---: |
| `ELIGIBLE_SYNTHETIC` | 24 |
| `TARGET_NOT_REVEALED` | 12 |
| `NON_MEASURED_VALUE_ONLY` | 6 |
| `SOURCE_PREDATES_REGISTRATION` | 6 |

The same nuclide produces the same eligibility status across every
PRED entry. A real reveal must preserve this property; if a label
shifts per entry without an explicit reason, the readiness-checklist
gate has been violated.

## Per-PRED Metrics

The engine produces a `signed_error_mev` per eligible row. The table
below summarises per-entry MAE and RMSE computed from the dry-run
output (four eligible rows per entry; no peek-rule weighting).

| Entry | Role | Eligible rows | MAE (MeV) | RMSE (MeV) |
| --- | --- | ---: | ---: | ---: |
| `PRED-0063` | candidate primary (proton-axis Gaussian) | 4 | 0.450000 | 0.463681 |
| `PRED-0064` | candidate companion (proton × neutron product) | 4 | 0.476271 | 0.487568 |
| `PRED-0065` | candidate diagnostic (neutron-axis Gaussian) | 4 | 1.086428 | 1.193234 |
| `PRED-0066` | sign-inverted control | 4 | 0.629283 | 0.791669 |
| `PRED-0067` | near-null control | 4 | 0.162157 | 0.225328 |
| `PRED-0068` | frozen baseline reference | 4 | 0.162157 | 0.225328 |

Aggregate metrics across all 24 eligible rows: MAE = 0.494382 MeV,
RMSE = 0.658890 MeV, mean signed error = −0.200689 MeV.

### Candidate-vs-Baseline Semantics

The frozen baseline reference `PRED-0068` and the near-null control
`PRED-0067` carry identical predicted values per the mini-wave
registration, so they produce identical metrics against any source.
That equivalence is what makes them paired controls for the candidate
families.

For each candidate family, the candidate-vs-baseline comparison is the
signed metric difference at the same eligible nuclides:

| Candidate | Candidate MAE (MeV) | Baseline (`PRED-0068`) MAE (MeV) | Δ MAE (MeV) |
| --- | ---: | ---: | ---: |
| `PRED-0063` | 0.450000 | 0.162157 | +0.287843 |
| `PRED-0064` | 0.476271 | 0.162157 | +0.314114 |
| `PRED-0065` | 1.086428 | 0.162157 | +0.924271 |

A positive Δ MAE means the candidate is *worse* than the baseline on
the synthetic source. In this dry-run the synthetic source is placed
near the primary candidate's predictions; the baseline reference
happens to be closer in the toy-arithmetic sense because the synthetic
offsets sum closer to the baseline values than to the candidate
corrections. This is plumbing arithmetic, not scientific evidence.

### Candidate-vs-Negative-Control Semantics

The sign-inverted control `PRED-0066` flips the proton-axis Gaussian
correction relative to `PRED-0063`. A genuine candidate signal should
*shrink* MAE relative to the sign-inverted control; a non-signal would
leave them comparable.

| Candidate | Candidate MAE (MeV) | Sign-inverted (`PRED-0066`) MAE (MeV) | Δ MAE (MeV) |
| --- | ---: | ---: | ---: |
| `PRED-0063` | 0.450000 | 0.629283 | −0.179283 |

A negative Δ MAE means the candidate is *better* than the sign-inverted
control. The test suite explicitly asserts this direction for the
primary candidate. The real reveal must preserve the same comparison
shape; if a future real reveal reports candidate MAE that does not
beat the sign-inverted control, that is preserved negative evidence,
not a tuning signal.

## Reporting Rules for the Future Real Reveal

The dry-run pre-commits the future reveal task to the following
reporting rules. These are not aspirational; they are enforced by the
test suite against the fixture, and the future real reveal must keep
the same shape.

1. **Six entries reported side by side.** A reveal artifact that
   reports `PRED-0063`, `PRED-0064`, or `PRED-0065` without
   `PRED-0066`, `PRED-0067`, and `PRED-0068` is rejected. The test
   `test_shell_axis_mini_wave_keeps_paired_controls_visible` encodes
   this rule.
2. **Per-target exclusion labels are uniform across entries.** The same
   nuclide must carry the same eligibility status under every PRED
   entry. The test
   `test_shell_axis_mini_wave_per_target_exclusions_are_uniform_across_preds`
   encodes this rule.
3. **MAE and RMSE computed per entry.** Aggregating across entries
   alone hides the candidate-vs-control comparison. The dry-run reports
   per-entry MAE/RMSE; the real reveal must do the same.
4. **Candidate-vs-baseline and candidate-vs-negative-control deltas.**
   Both deltas should be reported alongside per-entry MAE. The test
   `test_shell_axis_mini_wave_negative_control_mae_is_larger_than_primary_candidate`
   demonstrates the shape for the negative-control direction.
5. **Eligible-only scoring.** Only `ELIGIBLE_SYNTHETIC` rows (in the
   real reveal, `ELIGIBLE_MEASURED` rows) contribute to MAE/RMSE.
   `TARGET_NOT_REVEALED`, `NON_MEASURED_VALUE_ONLY`, and
   `SOURCE_PREDATES_REGISTRATION` rows must be preserved in the
   comparison table but never scored as if they were eligible.
6. **No registry mutation.** The dry-run reads `PRED-0063`..`PRED-0068`
   as bytes before and after running and asserts equality. The real
   reveal must satisfy the same property.

## What This Dry-Run Did Not Do

- It did not fetch, pin, or read any real nuclear-mass measurement
  source.
- It did not record measured values for `V-70`, `Mn-75`, `Co-77`,
  `Cu-81`, `Ag-129`, `Cd-130`, `Sb-135`, or `Cs-139`.
- It did not edit `PRED-0063`..`PRED-0068`.
- It did not modify or relax the no-peek audit gates from TASK-0303.
- It did not promote sandbox evidence to a claim, knowledge entry, or
  canonical result.
- It did not unblock TASK-0305 or any successor real-reveal task.

## Relationship to TASK-0303 and TASK-0305

- **TASK-0303** prepares source readiness (the source-manifest field
  list, archive/checksum requirements, no-peek per-PRED audit, and
  per-target classification labels). The dry-run inherits the
  partial-reveal pre-commitments recorded there.
- **TASK-0305** is the future real-reveal task. It remains blocked
  pending: (a) maintainer approval, (b) a pinned source manifest from
  TASK-0303 with every `TBD_*` placeholder replaced, (c) review of the
  no-peek audit checklist against the real source, and (d) explicit
  invocation as a separate task.

A real reveal that reuses this dry-run's fixture is forbidden; the
fixture is plumbing only and its values are not measurements.

## Limitations

- All numerical values in this review are computed from the toy fixture
  and are not scientific evidence.
- Synthetic offsets were chosen to make the primary candidate beat the
  sign-inverted control deterministically. A real reveal may show any
  direction, including null or candidate-worse-than-control outcomes,
  which the readiness checklist already treats as preserved evidence.
- The dry-run does not exercise `UNIT_SEMANTICS_AMBIGUOUS` or
  `TARGET_MATCH_AMBIGUOUS` directly; those branches will be exercised
  by a real reveal whose source can introduce them naturally.
- Per-entry MAE/RMSE arithmetic in this note ignores measurement
  uncertainty because the fixture's toy values carry no uncertainty
  field. A real reveal must handle the source's `uncertainty_fields`
  per the TASK-0303 manifest template before reporting metrics.

## Verdict

`VALID` as plumbing for the future real-reveal scoring shape.
`INCONCLUSIVE_SYNTHETIC_DRY_RUN` as the engine's intrinsic verdict for
synthetic toy values. The next step is not scoring a candidate; it is
a maintainer-approved real reveal task that satisfies TASK-0303's
source-readiness gates first.
