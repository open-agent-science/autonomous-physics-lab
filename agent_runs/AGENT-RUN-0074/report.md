# AGENT-RUN-0074 - Stellar M-L Baseline-Adequacy Audit

**Task:** `TASK-0762`
**Outcome:** `PIECEWISE_OR_FITTED_BASELINE_MATERIALLY_BETTER`

## Scope

Last control before Gate A for the Stellar M-L Route 2 evidence. On the same
frozen, main-sequence-restricted DEBCat rows (Route 2; raw `debs.dat` not
committed), compares the textbook single exponent against alternatives. All
exponents predeclared; the fitted exponent is least-squares with intercept fixed
at L0=1, fit on the train lane only (no holdout peek). No fit-to-holdout, no
RESULT/PRED/CLAIM.

## Result (main-sequence holdout, 65 rows; null MAE 0.332 dex)

| Baseline | alpha | Holdout MAE (dex) | vs textbook 3.5 |
| --- | ---: | ---: | ---: |
| textbook single | 3.5 | 0.185 | — |
| textbook piecewise mid-mass | 4.0 | 0.138 | −0.047 |
| train-fitted | **4.53** | **0.120** | **−0.065** |

All three power-law exponents beat the per-mass-band-median null (0.332 dex), so
a power-law mass-luminosity relation holds robustly on the main-sequence slice.
But the textbook single `M^3.5` is the **weakest** of the three: a steeper
exponent (fitted `4.53`, or the piecewise mid-mass `4.0`) is materially better,
by `0.065` dex — beyond the `~0.04` dex across-seed split noise measured in
TASK-0759.

## Interpretation

`M^3.5` is not the adequate baseline for `0.5-2.0 M_sun` main-sequence stars; the
relation here is **steeper (alpha ~= 4-4.5)**. This matches standard stellar
astrophysics: the classic piecewise M-L uses alpha ~= 4 for `0.43-2 M_sun`, while
`M^3.5` is the higher-mass (`>~2 M_sun`) branch. The audit therefore both
(a) confirms a robust power-law M-L signal and (b) shows the benchmark can
discriminate exponents.

## Decision

`PIECEWISE_OR_FITTED_BASELINE_MATERIALLY_BETTER`. Sandbox evidence only; no
universal law and no canonical result is claimed. Any Gate A RESULT must use the
adequate baseline framing (steeper-than-3.5 / fitted alpha), not "M^3.5
validated."

## Output Routing

- Task verdict: `PIECEWISE_OR_FITTED_BASELINE_MATERIALLY_BETTER`.
- Canonical destination: `agent_runs/AGENT-RUN-0074/metrics.json`, this report, and `docs/reviews/stellar-ml-route2-baseline-adequacy.md`.
- Review tier: `none`. Gate A: not attempted. Gate B: not applicable.
- Claim impact: none. Knowledge impact: none.
- Publication blocker: Gate A packaging is maintainer-only and must reframe the headline to the steeper, fitted/piecewise baseline; raw DEBCat stays local-only (Route 2).
