# ThermoML RESULT-0028 Gate-B Workflow Bridge

- Task: `TASK-1016`
- Result artifact: `results/EXP-0020/RUN-0002/result.yaml`
- Existing verdict: `INVALID`
- Task verdict: `GATE_B_PASS`
- Review tier: `AGENT_VALIDATED`
- Replay date: 2026-07-10

## Scope

This task moves RESULT-0028 from an unsupported packaging-script command onto
the repository's supported `physics-lab run` workflow path. The bridge reads
only committed RESULT-0026 metrics and the committed five-row esters/lactones
slice. It does not fetch ThermoML bytes, rerun the benchmark, refit Joback,
change the fixture, or create a new scientific result.

## Gate-B Command

```powershell
physics-lab run examples/thermoml_esters_lactones_negative_result.yaml
```

The workflow is registered as
`thermoml_esters_lactones_negative_result` and writes the canonical
`EXP-0020/RUN-0002` artifact layout when an output directory is supplied.

## Replay Outcome

- Helper status: `PASS`.
- Compared numeric metrics: `21`.
- Metrics within tolerance: `21/21`.
- Tolerance: `1.0e-9`.
- Maximum absolute drift: `0.0`.
- Verdict: `INVALID`, unchanged.
- Best model: `model_joback_frozen_tb`, unchanged.

The family margin remains `-5.549755 K` against the predeclared `+5 K`
survival rule, a shortfall of `10.549755 K`. Joback MAE remains `26.134 K`
versus `20.584245 K` for the diagnostic molecular-weight-only control across
five rows. The aggregate RESULT-0026 context remains positive for seven of
eight families with aggregate margin `28.502118 K`.

## Metadata Boundary

The canonical RESULT update is limited to the supported command path,
workflow code reference, review tier, and Gate-B validation metadata. Metrics,
input hashes, model id, verdict, source fixture, RESULT-0026, claims, and
knowledge artifacts are unchanged.

Validation independence is `independent`: publisher `gladunrv` and replayer
`akutenyov` are different human contributors. The result is independently
reproducible, but it is not maintainer-reviewed and does not support a
universal Joback or broad property-estimation claim.

## Output Routing

- Canonical destinations: workflow bridge, regression tests, this review note,
  and RESULT-0028 review metadata.
- Gate A: previously passed; unchanged.
- Gate B: `PASS`, 21 metrics, max drift `0.0`.
- Claim impact: none.
- Knowledge impact: none.
- Scientific metric and verdict impact: none.
