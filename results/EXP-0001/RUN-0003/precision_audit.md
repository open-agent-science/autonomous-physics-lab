# RUN-0003 Precision Audit

- Task: `TASK-0011`
- Result: `RESULT-0004`
- Run: `RUN-0003`
- Model: `model_t4_x1`
- Formula: `1 + a*theta^4 + b*x`

## Verdict

- Error source classification: `model_residual`
- Summary: Reported in-range error is dominated by model residual rather than reference precision or coefficient rounding.

## Grid

- Sample count: 200
- Split index: 140
- Test sample count: 60
- Test range (rad): `1.1080` to `1.5708`

## Key Metrics

| Metric | Mean Relative Error | Max Relative Error |
| --- | ---: | ---: |
| Full model vs standard reference | 0.000305245964122281 | 0.000948057126266689 |
| Full model vs independent reference | 0.000305245964122241 | 0.000948057126266689 |
| Standard vs independent reference | 7.22351219135287e-17 | 3.92045598218881e-16 |
| Full vs rounded prediction | 8.38410000988178e-07 | 1.47236647832305e-06 |

## Ratios

- Reference discrepancy / model residual (mean): `2.36645624852884e-13`
- Rounding discrepancy / model residual (mean): `0.00274667022510549`
- Max quadrature absolute error estimate: `3.69822358366576e-14`

## Interpretation

The independent quadrature reference agrees with the current elliptic-integral reference to far below the reported `3.1e-4` scale. Six-decimal coefficient rounding changes the mean relative error only at the sub-`1e-6` level. The reported RUN-0003 in-range error should therefore be interpreted as approximation residual on the configured test range.

## Limitations

- The independent reference still uses double-precision quadrature, not arbitrary precision arithmetic.
- The coefficient-rounding audit uses six decimal places because that is the current presentation precision in docs/notes/pendulum-gauntlet-100.md.
- This audit only covers the configured RUN-0003 test grid, not behavior outside that range.
