# Nuclear Shell-Axis Full-Known Retrospective Audit

**Task:** `TASK-0310`  
**Agent run:** `agent_runs/AGENT-RUN-0018/`  
**Script:** `scripts/run_nuclear_shell_axis_full_known_audit.py`  
**Metrics:** `agent_runs/AGENT-RUN-0018/metrics.json`  
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`

## Scope

This review records a sandbox-only retrospective audit of the shell-axis
candidate family after the shell-axis reveal source-manifest attempt did not
produce an acceptable post-registration reveal source.

The audit uses only committed repository data:

- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`
- `results/EXP-0012/RUN-0001/result.yaml`

It does not fetch live measurements, reveal-score `PRED-0063` through
`PRED-0068`, write prediction registry entries, modify canonical results, or
promote claims.

## Train, Holdout, And Full-Known Surfaces

| Surface | Rows | Role |
| --- | ---: | --- |
| NMD-0002 training slice | 11 | Fit shell-axis coefficients. |
| Post-AME2020 primary holdout | 295 | Primary retrospective holdout behavior. |
| Full-known unique committed surface | 306 | Combined audit surface. |

The full-known surface is the unique union of the NMD-0002 measured training
slice and the post-AME2020 primary holdout rows. This keeps the audit
retrospective and committed-data-only.

Baseline MAE on the audit surfaces:

| Surface | Baseline MAE MeV |
| --- | ---: |
| Training slice | 2.824522 |
| Primary holdout | 4.552569 |
| Full-known | 4.490449 |

## Candidate Triage

Nine candidate ideas were considered. Six were executed; three were rejected
before execution to preserve the overfit boundary.

| Candidate | Decision | Role |
| --- | --- | --- |
| `FULLKNOWN-SHELL-001` | executed | proton-axis Gaussian shell proximity |
| `FULLKNOWN-SHELL-002` | executed | proton x neutron product shell proximity |
| `FULLKNOWN-SHELL-003` | executed | neutron-axis Gaussian overlap diagnostic |
| `FULLKNOWN-SHELL-004` | executed | sign-inverted proton-axis control |
| `FULLKNOWN-SHELL-005` | executed | shuffled-feature cyclic-shift-5 control |
| `FULLKNOWN-SHELL-006` | executed | near-null / baseline-reference control |
| `FULLKNOWN-SHELL-007` | rejected | free-sigma proton Gaussian |
| `FULLKNOWN-SHELL-008` | rejected | per-magic-number offsets |
| `FULLKNOWN-SHELL-009` | rejected | duplicate additive shell-axis re-test |

## Results

Negative delta means lower retrospective MAE than the frozen baseline. Positive
delta means regression.

| Candidate | Full-known ΔMAE MeV | Holdout ΔMAE MeV | Training ΔMAE MeV | Magic Z ΔMAE MeV | Magic N ΔMAE MeV | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `FULLKNOWN-SHELL-001` | -0.086092 | -0.091504 | +0.059043 | -0.158489 | -0.326992 | `PARTIALLY_VALID` |
| `FULLKNOWN-SHELL-002` | -0.070030 | -0.071641 | -0.026837 | -0.001094 | -0.376547 | `PARTIALLY_VALID` |
| `FULLKNOWN-SHELL-003` | -0.060145 | -0.061969 | -0.011248 | -0.022180 | -0.512894 | `PARTIALLY_VALID` |
| `FULLKNOWN-SHELL-004` | +0.127546 | +0.127005 | +0.142063 | +0.459333 | +0.453871 | `INCONCLUSIVE` |
| `FULLKNOWN-SHELL-005` | -0.000039 | -0.000047 | +0.000178 | -0.000021 | -0.000197 | `INCONCLUSIVE` |
| `FULLKNOWN-SHELL-006` | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | `INCONCLUSIVE` |

## Worst Regressions

| Candidate | Worst subset regression |
| --- | --- |
| `FULLKNOWN-SHELL-001` | light A<50: +0.104064 MeV |
| `FULLKNOWN-SHELL-002` | light A<50: +0.148840 MeV |
| `FULLKNOWN-SHELL-003` | light A<50: +0.259976 MeV |
| `FULLKNOWN-SHELL-004` | registry-repeat chain neighbor: +0.824735 MeV |
| `FULLKNOWN-SHELL-005` | light A<50: +0.000256 MeV |
| `FULLKNOWN-SHELL-006` | none: +0.000000 MeV |

The light-subset regressions are preserved because the audit must not report
only aggregate improvement. They do not erase the primary holdout
improvements, but they keep the result bounded and sandbox-only.

## Control Behavior

`FULLKNOWN-SHELL-004` applies the negated proton-axis coefficient. It regresses
full-known MAE by `0.127546 MeV`, primary-holdout MAE by `0.127005 MeV`, and
the registry-repeat chain-neighbor subset by `0.824735 MeV`. That is the
expected direction for a sign-inverted control; it is not evidence for
promotion.

`FULLKNOWN-SHELL-005` uses a cyclic-shift-5 shuffled feature. Its largest
reported subset magnitude is `0.000256 MeV`, so the row-feature correspondence
stress collapses to a near-noise-floor effect.

`FULLKNOWN-SHELL-006` is the near-null / baseline-reference control and
returns exactly zero deltas.

## Rejections Preserved

- `FULLKNOWN-SHELL-007`, free-sigma proton Gaussian: rejected because sigma
  tuning is a nonlinear free knob on the 11-row training slice.
- `FULLKNOWN-SHELL-008`, per-magic-number offsets: rejected because one offset
  per magic number inflates degrees of freedom and risks memorizing the
  training slice.
- `FULLKNOWN-SHELL-009`, additive shell-axis re-test: rejected because the
  additive combined shell-axis form is already preserved as an overfit
  negative result in prior scout synthesis.

## Interpretation

The retrospective full-known audit keeps the shell-axis lane alive as
sandbox-review evidence: the three primary shell-axis candidates improve the
full-known surface by roughly `0.060` to `0.086 MeV` and the primary holdout by
roughly `0.062` to `0.092 MeV`.

The strongest candidate, `FULLKNOWN-SHELL-001`, still carries two important
limits:

- it regresses the training slice by `0.059043 MeV`;
- its worst subset regression is the light A<50 subset at `0.104064 MeV`.

Those limits matter. The correct conclusion is not promotion, but a stronger
bounded audit record: shell-axis remains the best current nuclear sandbox
surface while reveal scoring stays blocked behind source-manifest review.

## Limitations

- Candidate coefficients are fit on only 11 NMD-0002 rows.
- Post-AME2020 rows are retrospective time-split evidence, not strict blind
  prediction.
- The full-known surface is committed repository data, not a future
  measurement reveal.
- Subset behavior is uneven and must stay visible.
- No prediction registry entries are created, updated, deleted, or scored.
- No canonical results, claims, or knowledge entries are promoted.

## Verdict

`SANDBOX_PASS`

The shell-axis family survives the full-known committed-data audit as small,
bounded retrospective evidence with preserved null controls and visible subset
regressions. It should remain sandbox-only until a separate maintainer-reviewed
task authorizes any next step.

