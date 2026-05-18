# Nuclear Shell-Axis Adversarial Stress Scout 001

**Task:** TASK-0288  
**Agent run:** `agent_runs/AGENT-RUN-0016/`  
**Script:** `scripts/run_nuclear_shell_axis_stress_scout.py`  
**Metrics:** `agent_runs/AGENT-RUN-0016/metrics.json`  
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`

## Scope

This review records a sandbox-only adversarial stress scout for the
post-PRED-0062 shell-axis lane. It re-evaluates the strongest single-parameter
sandbox signal SHELL-SCOUT-003 (proton-only Gaussian) and its cross-check
companion SHELL-SCOUT-005 (proton x neutron product), plus SHELL-SCOUT-002
(neutron-only Gaussian) as an overlap diagnostic, and pairs them with three
adversarial controls (sign-inversion, cyclic-shift-5 shuffle, near-null). It
uses only repository-pinned datasets and does not fetch live measurements,
write prediction registry entries, or promote claims.

## Candidate Triage

Nine candidate ideas were generated:

- Six bounded candidates were executed (three re-evaluations plus three
  adversarial controls).
- Three candidates were rejected before execution for free-knob overfit risk
  or duplicate-search overlap with already-documented lanes.
- The near-null control was preserved as `INCONCLUSIVE`.

| Candidate | Decision | Reason |
| --- | --- | --- |
| `STRESS-SHELL-001` | executed | proton-axis Gaussian `beta_z * s_z2` (re-eval of SHELL-SCOUT-003) |
| `STRESS-SHELL-002` | executed | proton x neutron product `beta_p * (s_z2 * s_n2)` (re-eval of SHELL-SCOUT-005) |
| `STRESS-SHELL-003` | executed | neutron-axis Gaussian `beta_n * s_n2` overlap diagnostic (re-eval of SHELL-SCOUT-002) |
| `STRESS-SHELL-004` | executed | sign-inverted proton-axis adversarial control |
| `STRESS-SHELL-005` | executed | cyclic-shift-5 shuffled proton-axis adversarial control |
| `STRESS-SHELL-006` | executed | near-null sanity control, `r_corr = 0.0` |
| `STRESS-SHELL-007` | rejected_before_execution | free-sigma proton Gaussian adds a nonlinear free knob on an 11-row residual slice |
| `STRESS-SHELL-008` | rejected_before_execution | per-magic-number offsets (7 coefficients on 11 rows) inflate degrees of freedom |
| `STRESS-SHELL-009` | rejected_before_execution | SHELL-SCOUT-001 additive form is already documented OVERFITTED in the synthesis review |

## Results

| Candidate | Description | Primary ΔMAE MeV | Magic Z ΔMAE MeV | Magic N ΔMAE MeV | Heavy A>=100 ΔMAE MeV | Chain-neighbor ΔMAE MeV | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `STRESS-SHELL-001` | proton-axis Gaussian | -0.091504 | -0.387579 | -0.291542 | -0.087801 | -0.824735 | `PARTIALLY_VALID` |
| `STRESS-SHELL-002` | proton x neutron product | -0.071641 | -0.015759 | -0.411085 | -0.089679 | -0.382745 | `PARTIALLY_VALID` |
| `STRESS-SHELL-003` | neutron-axis Gaussian | -0.061969 | -0.014413 | -0.591750 | +0.019771 | -0.611142 | `PARTIALLY_VALID` |
| `STRESS-SHELL-004` | sign-inverted proton-axis | +0.127005 | +0.670711 | +0.352300 | +0.108097 | +0.824735 | `INCONCLUSIVE` |
| `STRESS-SHELL-005` | cyclic-shift-5 shuffled proton-axis | -0.000060 | -0.000247 | -0.000216 | -0.000050 | -0.000603 | `PARTIALLY_VALID` |
| `STRESS-SHELL-006` | near-null sanity control | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | `INCONCLUSIVE` |

Frontier and additional subset deltas:

| Candidate | Mid-mass ΔMAE MeV | Light A<50 ΔMAE MeV | Frontier contrast MeV | Neutron-rich (N-Z)/A>=0.25 ΔMAE MeV |
| --- | ---: | ---: | ---: | ---: |
| `STRESS-SHELL-001` | -0.178553 | +0.181030 | -0.225167 | -0.357017 |
| `STRESS-SHELL-002` | -0.124308 | +0.172426 | -0.165681 | -0.229458 |
| `STRESS-SHELL-003` | -0.217785 | +0.347373 | -0.401357 | -0.276888 |
| `STRESS-SHELL-004` | +0.224739 | -0.099556 | +0.220468 | +0.357017 |
| `STRESS-SHELL-005` | -0.000160 | +0.000356 | -0.000313 | -0.000326 |
| `STRESS-SHELL-006` | +0.000000 | +0.000000 | +0.000000 | +0.000000 |

Negative delta means lower retrospective MAE than the frozen baseline on that
subset. Positive delta means regression.

## Repeated-Target Pressure

The four overrepresented registry targets are absent from the post-AME2020
holdout, so the holdout is not directly biased by registry-target repetition:

| Target | Z | A | Registry entry count | In holdout |
| --- | ---: | ---: | ---: | --- |
| `Ni-76` | 28 | 76 | 18 | no |
| `Ca-55` | 20 | 55 | 14 | no |
| `Ga-85` | 31 | 85 | 14 | no |
| `Zn-80` | 30 | 80 | 14 | no |

Chain-neighbor holdout rows (same Z, |A - registry_A| <= 2):

| Nuclide | Z | N | A | Registry target |
| --- | ---: | ---: | ---: | --- |
| `Ca-54` | 20 | 34 | 54 | `Ca-55` |
| `Ga-83` | 31 | 52 | 83 | `Ga-85` |
| `Ga-84` | 31 | 53 | 84 | `Ga-85` |
| `Ni-74` | 28 | 46 | 74 | `Ni-76` |
| `Ni-75` | 28 | 47 | 75 | `Ni-76` |
| `Zn-79` | 30 | 49 | 79 | `Zn-80` |

The `registry_repeat_chain_neighbor` subset has only six rows; the
chain-neighbor deltas reported above are not interpretable in isolation. They
track the same sign as the primary and magic-axis deltas for STRESS-SHELL-001,
STRESS-SHELL-002, and STRESS-SHELL-003, which is consistent with the
shell-axis signal being concentrated near the proton-axis magic line rather
than being a registry-target artifact.

## Rejections Preserved

- `STRESS-SHELL-007`, free-sigma proton Gaussian: rejected because tuning sigma on an 11-row residual slice adds a nonlinear free knob with high overfit risk and duplicates the fixed-sigma probe `STRESS-SHELL-001`.
- `STRESS-SHELL-008`, per-magic-number offsets: rejected because 7 free coefficients on an 11-row training slice inflate degrees of freedom and memorize shell-cluster rows.
- `STRESS-SHELL-009`, SHELL-SCOUT-001 additive form re-test: rejected because the combined `beta_z * s_z2 + beta_n * s_n2` form is already documented OVERFITTED in `docs/reviews/nuclear-scout-lane-synthesis-after-pred-0062.md`; re-running it would be duplicate-search rather than adversarial stress.

## Interpretation

Three shell-axis re-evaluations (`STRESS-SHELL-001`, `STRESS-SHELL-002`,
`STRESS-SHELL-003`) reproduce the post-PRED-0062 sub-MeV signals: each
improves the primary surface by 0.06–0.09 MeV, improves at least one
magic-axis subset by 0.29–0.59 MeV, and produces consistent
chain-neighbor improvement around 0.4–0.8 MeV. The frontier contrast is
negative for all three (i.e. mid-mass improves more than the light/heavy
average), which is the same pattern reported in the prior synthesis.

The sign-inverted control `STRESS-SHELL-004` regresses every shell-related
subset by the same magnitude as `STRESS-SHELL-001` improves them (e.g. primary
+0.127 MeV vs −0.091 MeV; chain-neighbor +0.825 MeV vs −0.825 MeV). This is
the expected behavior of a real signal under sign inversion: the inverted
correction adds the wrong direction back into the residual, so the surface
gets worse. The verdict rule only triggers `OVERFITTED` if the inverted form
*improves* primary, which would have indicated unreliable signal direction;
that did not happen here.

The shuffled control `STRESS-SHELL-005` (cyclic-shift-5) collapses every
subset delta to a near-noise-floor magnitude (|delta| <= 7e-4 MeV on every
subset reported). This is the expected behavior when the row-feature
correspondence is destroyed: the lstsq fit on shuffled features yields a tiny
beta (~1.2e-3 vs ~1.16 for the unshuffled fit), and applying that tiny beta to
the shuffled holdout produces sub-milli-MeV deltas. The strict triage rule
labels it `PARTIALLY_VALID` because primary is technically negative, but the
practical interpretation is that the shuffle destroys the signal — the
shell-axis effect depends on the actual row-feature correspondence, not on
the fitted coefficient absorbing the residual.

The near-null control `STRESS-SHELL-006` returns exactly zero deltas on every
subset, as required by the design.

## Limitations

- Retrospective committed post-AME2020 rows are used only as a stress surface.
- Coefficients are fitted on an 11-row residual slice.
- The `registry_repeat_chain_neighbor` subset has only six holdout rows; the chain-neighbor delta is fragile.
- Adversarial verdicts are sandbox-triage labels, not scientific acceptance.
- The shuffled control's `PARTIALLY_VALID` label is an artifact of strict rules applied to a near-noise-floor delta; it should not be read as a real shuffled signal.
- No prediction registry entries are created or updated.
- No canonical results, claims, or knowledge entries are promoted.

## Verdict

`REVIEW_READY` as sandbox evidence. The shell-axis stress lane survives
sign-inversion (inverted control regresses as expected), shuffle (collapses
to noise floor), and the near-null sanity check. The three re-evaluations
reproduce the prior post-PRED-0062 sub-MeV signal on the same subsets. No
scientific success claim is promoted; any future registry expansion must be
a separate maintainer-reviewed task that designs target batches without
amplifying the four overrepresented registry targets (`Ni-76`, `Ca-55`,
`Ga-85`, `Zn-80`).
