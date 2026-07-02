# ThermoML esters/lactones negative-result preflight

Task: `TASK-0918`
Source result: `RESULT-0026`
Source experiment/run: `EXP-0020` / `RUN-0001`
Recommendation: `PACKAGE_AS_NEGATIVE_RESULT`
Review date: 2026-07-02

## Scope

This preflight asks whether the already recorded esters/lactones failed-family
memory should remain only a review note, wait for a larger fixture, or become a
canonical negative/control result candidate.

The answer is narrow: package it in a later task as a bounded negative/control
result whose statement is only that the frozen Joback normal-boiling-temperature
transfer benchmark did not clear the predeclared esters/lactones family margin
inside the committed `RESULT-0026` fixture.

This task does not edit `RESULT-0026`, fixture rows, Joback coefficients,
claims, knowledge, prediction registry entries, or any raw ThermoML source
artifact.

## Evidence Reviewed

- `docs/reviews/thermoml-esters-lactones-negative-memory.md`
- `results/EXP-0020/RUN-0001/result.yaml`
- `results/EXP-0020/RUN-0001/metrics.json`
- `docs/reviews/thermoml-result0026-gate-b-replay.md`
- `docs/result-promotion-protocol.md`

Key committed metrics:

| Scope | Joback MAE (K) | Best non-oracle control | Control MAE (K) | Joback margin (K) | Required margin (K) | Outcome |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| Aggregate, 40 rows | `14.925825` | `molecular_weight_only` | `43.427943` | `28.502118` | `5.0` | clears |
| Esters/lactones, 5 rows | `26.134000` | `molecular_weight_only` | `20.584245` | `-5.549755` | `5.0` | does not clear |

`RESULT-0026` remains aggregate-positive and family-dependent: seven of eight
families clear the margin, while esters/lactones is the failed held-out family.
The esters/lactones shortfall relative to the survival rule is `10.549755 K`
because the family margin is `-5.549755 K` instead of at least `+5.0 K`.

The formal Gate B bridge recorded in
`docs/reviews/thermoml-result0026-gate-b-replay.md` replayed `RESULT-0026` with
`0.0` maximum absolute drift across 23 numeric fields and upgraded the result to
`AGENT_VALIDATED`. That strengthens the packaging case, but it does not broaden
the scientific interpretation.

## Gate A Readiness Checklist

| Gate A item | Status | Preflight finding |
| --- | --- | --- |
| Deterministic run | `PASS` | `RESULT-0026` now records a `physics-lab run examples/thermoml_tb_family_transfer_benchmark.yaml` workflow bridge and formal replay. |
| Verification block populated | `PASS` | `RESULT-0026` includes aggregate, family-survival, fidelity, and source-provenance checks. |
| Input hashes recorded | `PASS` | The result pins config, fixture, experiment, hypothesis, and task input hashes. |
| Limitations listed | `PASS` | Current limitations already name the esters/lactones family exception and no-claim boundary. |
| Engine version and commit pinned | `PASS` | `RESULT-0026` records engine version, original commit, command, and code reference. |
| Schema validation path | `PASS_WITH_CONDITION` | Use schema-safe `best_verdict: INVALID` for the negative/control result unless the result schema is later updated to accept `FALSIFIED`. |
| No protected-artifact rewrite | `PASS_WITH_CONDITION` | Package as a new result artifact only; do not mutate `RESULT-0026` metrics, verdict, review tier, or golden-result pinning. |
| No forbidden overclaim wording | `PASS_WITH_CONDITION` | Public text must keep the fixture size, `Tb` property, family scope, control comparison, and aggregate-positive context visible. |
| Dataset provenance valid | `PASS` | ThermoML source DOI, archive SHA-256, citation request, and source-rights boundary are already recorded. |

The package route clears the scope and schema gates if the later task preserves
the conditions above.

## Recommendation

`PACKAGE_AS_NEGATIVE_RESULT`.

Keeping the observation only as review-note memory would underuse a clean,
predeclared, deterministic, agent-validated failure case. Waiting for an expanded
fixture is still useful for confirmation, but it is not required before recording
the current bounded negative/control result. The canonical result should not say
that Joback fails generally for esters, lactones, boiling points, or
thermophysical property estimation.

Safe one-sentence wording:

> On the committed 40-row ThermoML normal-boiling-temperature fixture, the
> frozen Joback estimator cleared the aggregate and seven of eight held-out
> family margins, but esters/lactones did not clear the predeclared +5 K
> family-survival margin: Joback MAE was 26.134 K versus 20.584245 K for the
> molecular-weight-only control across five rows.

Do not shorten this to a broad success or broad failure claim.

## Future Task Shape

Title:
`Package RESULT-0026 esters/lactones failed-family memory as a bounded negative/control RESULT`

Inputs:

- `docs/reviews/thermoml-esters-lactones-negative-memory.md`
- `docs/reviews/thermoml-esters-lactones-negative-result-preflight.md`
- `results/EXP-0020/RUN-0001/result.yaml`
- `results/EXP-0020/RUN-0001/metrics.json`
- `docs/reviews/thermoml-result0026-gate-b-replay.md`
- `docs/result-promotion-protocol.md`

Requirements:

- Create a new canonical negative/control result artifact, not a rewrite of
  `RESULT-0026`.
- Use only the existing committed `RESULT-0026` metrics and input hashes; do not
  rerun, refit, fetch, or expand ThermoML data unless the task explicitly asks
  for a replay check.
- Use `best_verdict: INVALID` if current schema support still requires that
  spelling for negative/falsification results.
- State the negative result as an esters/lactones family-survival failure inside
  the 40-row `Tb` fixture only.
- Preserve the aggregate-positive `RESULT-0026` context: Joback clears the
  aggregate margin and seven of eight family margins.
- Preserve ThermoML attribution, publisher-permission/source-rights limits, and
  no-claim wording.
- Do not edit claims, knowledge, prediction registry entries, Joback
  coefficients, fixture rows, raw source artifacts, or `RESULT-0026` metrics.

Expected accepted output:

- A new `RESULT-*` package under the maintainer-approved `EXP-0020` result path,
  plus any required index/review metadata allowed by the task contract.
- Public-safe wording matching the bounded sentence above.
- Validation via `ruff`, focused ThermoML tests, and strict repository
  validation.

## Blockers And Stop Conditions

- Stop if the future result package cannot preserve the distinction between
  aggregate `TRANSFER_SUPPORTED_IN_SCOPE` and the failed esters/lactones family.
- Stop if schema requirements would force a misleading verdict or a protected
  rewrite of `RESULT-0026`.
- Stop if any package text frames the result as chemical-design guidance, safety
  guidance, synthesis advice, process-design evidence, universal Joback
  validation/falsification, or a broad property-estimation claim.
- Stop if source-rights wording drops the ThermoML attribution, citation request,
  or raw-archive non-vendoring boundary.
- Stop if a later task tries to tune on these five rows and then present them as
  independent confirmation.

## Output Routing

- Task verdict: `PACKAGE_AS_NEGATIVE_RESULT` preflight only.
- Canonical destination for this task:
  `docs/reviews/thermoml-esters-lactones-negative-result-preflight.md`.
- Result impact: none in this task; no `RESULT-*` artifact is created or edited.
- Gate A status: preflight `PASS_WITH_CONDITIONS` for a future bounded negative
  result package.
- Gate B status: inherited source evidence is `PASS` for `RESULT-0026`; this
  task performs no new replay.
- Claim impact: none.
- Knowledge impact: none.
- Prediction impact: none.
- Safe public boundary: bounded ThermoML `Tb` fixture, five esters/lactones rows,
  frozen Joback estimator, explicit best-control comparison, no broad
  thermophysical-property or chemical-design claim.