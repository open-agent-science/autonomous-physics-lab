# AGENT-RUN-0072 Report

## Scope

`TASK-0703` evaluates formation energy only on the checksum-pinned MD-0002
stable ternary-oxide slice. The run uses 253 train, 55 validation, and 54
holdout rows with no live fetch.

## Method

Five train-only baselines were compared: global mean, global median,
cation-family mean, exact unordered cation-pair mean, and exact spacegroup
mean. Unseen groups fall back to the global train mean. The run also executes
label-shuffle and cation-label-shuffle controls, row-order invariance, five
seeded 70/30 split checks, and leave-group-out diagnostics.

## Metrics

The best global null was the global median with holdout MAE `0.506092`
eV/atom. The exact cation-pair mean reached holdout MAE `0.200606` eV/atom,
an absolute improvement of `0.305486` eV/atom and a relative improvement of
`0.603618`.

The cation-pair baseline won all five seeded split checks. Its seeded mean MAE
was `0.192881` eV/atom, versus `0.542966` for the runner-up global mean. The
mean margin (`0.350085`) exceeded the measured across-seed noise (`0.015359`).
Its real holdout MAE also beat every label-shuffle control and every
cation-label-shuffle control.

## Verdict

`SANDBOX_PASS`. All predeclared benchmark gates passed. The scoped benchmark
behavior is `VALID_IN_RANGE` for this frozen computed-DFT slice only.

## Output Routing

- Canonical destination: future task-authorized result packaging
- Review tier: none
- Gate A: blocked before packaging
- Claim impact: none
- Knowledge impact: none
- Publication blocker: TASK-0703 does not authorize new canonical hypothesis
  or experiment identities
