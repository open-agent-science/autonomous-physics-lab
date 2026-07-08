# Particle AHS Common-Scheme Geometric-Midpoint Baseline

- Task: `TASK-0958`
- Sandbox run: `AGENT-RUN-0091`
- Source: `PARTICLE-MASS-AHS-2024-PDG-MZ-YUKAWAS`
- Verdict: `INCONCLUSIVE`
- Routing: sandbox benchmark diagnostic; no canonical RESULT

## Scope

This benchmark spends the source pin created by `TASK-0926` on one bounded,
non-Koide diagnostic. It uses exactly the six source-reported dimensionless
running Yukawa couplings on the single `MS-bar` at `M_Z` surface. It does not
convert Yukawas to masses, fit a relation, search formulas, combine schemes,
or change any source row.

The metric definition was frozen in
`examples/benchmarks/particle_ahs_common_scheme_baseline.yaml` before scoring.
That predeclaration is procedural, not an enforceable blind, because the source
rows were already committed and readable.

## Predeclared Metric

The fixed charge sectors are:

- up type: `y_u`, `y_c`, `y_t`;
- down type: `y_d`, `y_s`, `y_b`.

For each ordered sector, the zero-parameter null baseline predicts the middle
Yukawa as the geometric mean of the endpoints:

`y_middle_baseline = sqrt(y_light * y_heavy)`

The signed diagnostic is:

`r = log10(y_middle / y_middle_baseline)`

A positive residual means the observed middle value is above the geometric
midpoint; a negative residual means it is below. Absolute residuals are
reported in dex. No success threshold was defined.

## Input Integrity

- source-row SHA-256:
  `b96709627e13542c6c047ca565713028321bba98fcb070d1a016ab774e29b480`;
- expected rows present: `6/6`;
- representation: `running_yukawa`;
- scheme and scale: `MS-bar` at `M_Z`;
- units: dimensionless;
- live fetches: none.

## Results

| Sector | Baseline middle | Observed middle | Signed residual (dex) | Absolute factor |
| --- | ---: | ---: | ---: | ---: |
| up type (`u-c-t`) | `0.00260915311931` | `0.00356` | `+0.134950431` | `1.364427` |
| down type (`d-s-b`) | `0.000501018961717` | `0.000306` | `-0.214132736` | `1.637317` |

Aggregate diagnostics:

- mean signed residual: `-0.039591152 dex`;
- mean absolute residual: `0.174541584 dex`;
- root-mean-square residual: `0.178975484 dex`;
- maximum absolute residual: `0.214132736 dex`.

All six output files were regenerated twice in disposable directories and were
byte-identical between replays.

## Interpretation

The equal-log-spacing null is not uniformly aligned with both sectors: the
middle up-type value lies above its geometric midpoint while the middle
down-type value lies below its midpoint. This is descriptive benchmark memory,
not evidence for or against a particle-mass law. With only two sectors and no
predeclared quality threshold, no scientific pass/fail classification is
available.

The source provides marginal one-sigma intervals but no recoverable
six-parameter covariance matrix. The benchmark therefore does not combine
those intervals or report residual significance.

## Output Routing

- Task verdict: `INCONCLUSIVE` bounded diagnostic.
- Canonical destination: sandbox `agent_runs/AGENT-RUN-0091/` and this review
  note.
- Review tier: `none`; no `RESULT-*` was created.
- Gate A / Gate B: not attempted.
- Claim impact: none; `CLAIM-0006` and `CLAIM-0007` are unchanged.
- Knowledge impact: none.
- Prediction impact: none.
- Limitations: six source-derived Yukawas, two sectors, one common-scheme
  surface, no holdout, no threshold, and no covariance-aware inference.
