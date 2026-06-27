# TE-001 Light-Clock Consistency Benchmark

- Task: `TASK-0847`
- Experiment: `EXP-0017`
- Sandbox run: `AGENT-RUN-0086`
- Verdict: `CONSISTENT`

## Method

The benchmark evaluates the frozen Special Relativity light-clock
relations on beta values `0, 0.1, 0.5, 0.9, 0.99`. It rejects
`beta >= 1` before numerical evaluation and checks a deliberately
wrong Newtonian candidate as a regression control.

Reference equations:

- `T_rest = 2 L / c`
- `gamma = 1 / sqrt(1 - beta^2)`
- `T_moving = gamma T_rest`
- `d/2 = sqrt(L^2 + (v T_moving / 2)^2)`

## Per-Case Checks

| beta | gamma | LC-001 | LC-002 | LC-003 | LC-005 | verdict |
| ---: | ---: | --- | --- | --- | --- | --- |
| 0.00 | 1 | PASS | PASS | PASS | PASS | CONSISTENT |
| 0.10 | 1.00503781526 | PASS | PASS | PASS | PASS | CONSISTENT |
| 0.50 | 1.15470053838 | PASS | PASS | PASS | PASS | CONSISTENT |
| 0.90 | 2.29415733871 | PASS | PASS | PASS | PASS | CONSISTENT |
| 0.99 | 7.08881205008 | PASS | PASS | PASS | PASS | CONSISTENT |

`LC-004`: `PASS`. Undefined guard cases: beta=1.0: UNDEFINED, beta=1.01: UNDEFINED.

## Metrics

- LC-001 maximum relative error: `0.000e+00`
- LC-002 maximum relative error: `1.936e-16`
- LC-003 maximum relative error: `1.988e-16`
- Newtonian `T_moving = T_rest` control: `FAIL` on LC-001, overall `INCONSISTENT`.

## Limitations

- This validates APL's implementation of the named SR thought experiment, not SR empirically.
- Only TE-001 and the declared beta sweep are in scope.
- General Relativity, acceleration, longitudinal clocks, and other thought experiments are excluded.
- No claim, knowledge, or discovery promotion is authorized.

## Output Routing

- Canonical destination: sandbox agent run plus review note.
- Review tier: `none`.
- Gate A: not attempted; this task keeps the first implementation
  sandbox-first rather than publishing a canonical RESULT.
- Gate B: not attempted.
- Claim impact: none.
- Knowledge impact: none.
