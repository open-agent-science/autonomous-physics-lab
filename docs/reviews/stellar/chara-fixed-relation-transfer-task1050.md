# TASK-1050 CHARA Fixed-Relation Transfer

## Scope

TASK-1050 applies the frozen RESULT-0022 relation
`log10(L/Lsun) = 4.526004 * log10(M/Msun)` to exactly twelve source-curated
components from six CHARA systems. No coefficient, intercept, threshold,
exclusion, or rescue model is fitted on CHARA.

The input gate reproduces the TASK-1049 `INDEPENDENT_SOURCE_REPLAY_PASS`, all
three source/dependence hashes, twelve rows, six physical systems, and zero
admitted Melotte-25 rows. Each binary remains one effective group.

## Method

The primary metric is component-level log-luminosity MAE. The predeclared
eligible controls are fixed `alpha=3.5`, fixed `alpha=4.0`, and the RESULT-0022
main-sequence train-lane mass-band median null with a global-train-median
fallback for unseen bands. CHARA targets are never used to construct the null.

The frozen relation must beat the lowest-MAE control by at least `0.04 dex`.
System-level sensitivity deletes one physical-system group at a time; two
components never count as two environments.

## Metrics

| Model or control | Component MAE (dex) |
| --- | ---: |
| frozen RESULT-0022 alpha `4.526004` | `0.060530` |
| fixed textbook alpha `4.0` | `0.097317` |
| fixed textbook alpha `3.5` | `0.223985` |
| RESULT-0022 train-only mass-band median null | `0.621336` |

The frozen relation beats the best control (`alpha=4.0`) by `0.036787 dex`,
which is `0.003213 dex` below the frozen survival threshold. Leave-one-system-
group-out margins range from `0.021022` to `0.065474 dex`, so the bounded
surface is also visibly sensitive to which one of six systems is withheld.

## Verdict

`INCONCLUSIVE`

The relation wins narrowly on this surface but does not clear the predeclared
margin. The result is retained without threshold relaxation or refit. It does
not establish a population result or universal stellar mass-luminosity law.

## Output Routing

- Canonical destination: `results/EXP-0023/RUN-0001/` as `RESULT-0031` when
  Gate A passes.
- Review tier: `AGENT_PUBLISHED`.
- Gate A: mechanical validation required and expected to pass.
- Gate B: not attempted in this task.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: none for bounded evidence publication after Gate A;
  independent replay and maintainer interpretation remain pending.
