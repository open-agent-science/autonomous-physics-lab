# AHS Common-Scheme Geometric-Midpoint Baseline

- Task: `TASK-0958`
- Sandbox run: `AGENT-RUN-0091`
- Verdict: `INCONCLUSIVE`
- Source SHA-256: `b96709627e13542c6c047ca565713028321bba98fcb070d1a016ab774e29b480`

## Method

For each fixed charge sector, the zero-parameter baseline predicts the middle
running Yukawa as `sqrt(y_light * y_heavy)`. The signed diagnostic is
`log10(y_middle / predicted_middle)` in dex. The metric and sector ordering
were frozen in the fixture before scoring; this is procedural rather than blind
because the source rows were already committed and readable.

## Results

| sector | ordered parameters | predicted middle | observed middle | signed residual (dex) | deviation factor |
| --- | --- | ---: | ---: | ---: | ---: |
| up_type | y_u / y_c / y_t | 0.00260915311931 | 0.00356 | 0.134950431 | 1.364427 |
| down_type | y_d / y_s / y_b | 0.000501018961717 | 0.000306 | -0.214132736 | 1.637317 |

- Mean signed residual: `-0.039591152` dex
- Mean absolute residual: `0.174541584` dex
- Root-mean-square residual: `0.178975484` dex
- Maximum absolute residual: `0.214132736` dex

## Interpretation Boundary

The two residuals are a descriptive reference for equal log spacing on one
common-scheme surface. No quality threshold was predeclared, and two sectors
cannot support generalization. Residual size is not statistical significance.

## Limitations

- Exactly six source-derived running Yukawa couplings and two charge sectors on one MS-bar-at-M_Z surface.
- The geometric-midpoint baseline is descriptive and zero-parameter; it is not a physical mass-generation model.
- The source does not provide a recoverable six-parameter covariance matrix, so no uncertainty significance is reported.
- The values were already committed and readable; fixture predeclaration is a procedural convention, not an enforceable blind.
- Sandbox diagnostic only; no Koide test, formula search, canonical RESULT, CLAIM, KNOW, PRED, or BSM interpretation.

## Output Routing

- Canonical destination: sandbox `agent_runs/AGENT-RUN-0091/` plus review note.
- Review tier: `none`; no canonical RESULT was created.
- Gate A / Gate B: not attempted.
- Claim / knowledge / prediction impact: none.
