# Particle-Mass Relation Falsifier MVP

- Result: `RESULT-0011`
- Run: `RUN-0001`
- Experiment: `EXP-0009`
- Hypothesis: `HYP-0009`
- Task: `TASK-0040`
- Global verdict: `INVALID`

## Tested Relation

`Q = (m1 + m2 + m3) / (sqrt(m1) + sqrt(m2) + sqrt(m3))^2 = 2/3`

The MVP tests only guardrail-compliant, within-family charged fermion triplets.

## Family Results

| Family | Particles | Q | Gap to 2/3 | 1-sigma Q uncertainty | Gap sigma | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Charged leptons | e, mu, tau | 0.666664463415 | 2.203252e-06 | 5.080958e-06 | 0.434 | `VALID` |
| Up-type quarks | u, c, t | 0.848980777661 | 1.823141e-01 | 1.145462e-03 | 159 | `INVALID` |
| Down-type quarks | d, s, b | 0.731496757563 | 6.483009e-02 | 7.331243e-03 | 8.84 | `INVALID` |

## Baseline Calibration

| Family | Analytic Q-window fraction | Random baseline fraction within observed gap | Best random gap |
| --- | ---: | ---: | ---: |
| Charged leptons | 6.609756e-06 | 0.000000e+00 | 9.438120e-06 |
| Up-type quarks | 5.469423e-01 | 5.762000e-01 | 7.382196e-05 |
| Down-type quarks | 1.944903e-01 | 1.732000e-01 | 3.302185e-05 |

## Complexity Penalty

- Parameter count penalty: `0.0`
- Arbitrary constant penalty: `0.0`
- Tuned exponent penalty: `0.0`
- Structural flexibility penalty: `1.0`
- Cross-family mixing penalty: `0.0`
- Post hoc prediction penalty: `0.0`
- Total penalty: `1.0` (`low`)

## Limitations

- This MVP evaluates the fixed standard Koide relation only.
- The result is a cross-family survival falsification, not a discovery-level claim.
- Quark inputs preserve the mixed scale and scheme limitations of the stored PDG-backed dataset.
- The random baseline is a calibration aid, not a physical mass-generation model.
- No claim promotion is proposed by this run.

## Verdict

The cross-family survival hypothesis receives repository verdict `INVALID` because at least one guardrail-compliant family triplet misses the `2/3` target outside its propagated uncertainty.
