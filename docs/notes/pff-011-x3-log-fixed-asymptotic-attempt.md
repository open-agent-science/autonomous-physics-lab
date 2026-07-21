# PFF-011 Fixed-Asymptotic x3-Log Attempt

**Run:** `MICROTASK-RUN-0036`
**Verdict:** `FALSIFIED`

## Candidate And Inputs

This repeatable attempt tests

`T/T0 = 1 + a*x + b*x^2 + (1/pi)*x^3*log(1/(1-x))`,

where `x = sin^2(theta/2)`. The exact reference is
`(2/pi) K(x)` from
`physics_lab.engines.simulation.exact_pendulum_period_ratio`.

The `x^3` factor suppresses the log term at small amplitude while tending to
one at the separatrix. Therefore its fixed `1/pi` coefficient gives the
correct leading slope `2/pi` with respect to `-log(pi-theta)` as
`theta -> pi`. Only `a` and `b` were fitted by the repository's linear
least-squares helper.

## Frozen Method And Gates

- Fit: 500 evenly spaced points on `[0.01, 1.10]` rad.
- Configured test: 200 points on `[1.11, pi/2]` rad.
- Near-separatrix diagnostic: 500 points on `[3*pi/4, pi-0.001]` rad.
- Slope diagnostic: 300 points on `[pi-0.1, pi-0.001]` rad.
- Pass gates declared before execution: configured test MRE at most `1e-3`,
  near-separatrix max relative error at most `5e-2`, and asymptotic-slope
  relative error at most `5e-2`.

Code references:

- `physics_lab/engines/simulation.py`
- `physics_lab/engines/formula_discovery.py`

## Metrics

| Quantity | Value | Gate |
| --- | ---: | --- |
| fitted `a` | `0.2502334789149173` | descriptive |
| fitted `b` | `0.1473489146300460` | descriptive |
| train MRE | `1.584713757570333e-5` | descriptive |
| train max relative error | `1.0091283630351904e-4` | descriptive |
| configured test MRE | `2.481508302576918e-3` | **FAIL** (`> 1e-3`) |
| configured test max relative error | `7.788276642876002e-3` | descriptive |
| near-separatrix MRE | `1.69035799823652e-1` | descriptive |
| near-separatrix max relative error | `1.9860520692567105e-1` | **FAIL** (`> 5e-2`) |
| fitted asymptotic slope | `0.6408429142478926` | descriptive |
| expected slope `2/pi` | `0.6366197723675814` | reference |
| slope relative error | `6.633695753126611e-3` | PASS (`< 5e-2`) |
| minimum prediction step on `[0.001, pi-0.001]` | `3.508206172231354e-7` | monotone on sampled grid |

## Interpretation

The family recovers the leading logarithmic growth rate but fails both
predeclared accuracy gates. The result falsifies this particular two-fit-
coefficient matched-asymptotic candidate under the stated grids. A correct
leading slope is not sufficient: the additive asymptotic constant and the
intermediate-angle curvature remain materially wrong.

## Novelty And Limitations

The earlier `PFF-011` run tested `(1+a*x)/(1-b*x)`. Existing gauntlet families
contain `x*log` and `x^2*log` atoms, but not this fixed-coefficient `x^3*log`
construction. This is one candidate and one set of frozen grids, not an
exhaustive search. It does not falsify all physics-constrained, logarithmic, or
matched-asymptotic pendulum approximations and does not create or promote a
canonical result, claim, or knowledge artifact.

## Output Routing

- Destination: this note and the append-only microtask run record.
- Gate A / Gate B: not attempted.
- Claim and knowledge impact: none.
- Publication blocker: human review is still required before treating the
  negative result as stable campaign memory.
