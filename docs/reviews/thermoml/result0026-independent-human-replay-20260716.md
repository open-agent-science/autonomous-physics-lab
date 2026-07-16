# ThermoML RESULT-0026 Independent-Human Replay

- Task: `TASK-1047`
- Result: `RESULT-0026`
- Task verdict: `INDEPENDENT_GATE_B_PASS`
- Replay date: 2026-07-16

## Replayer Identity

| Field | Value |
| --- | --- |
| contributor_id | `akutenyov` |
| github_username | `akutenyov` |
| agent/tool | `Codex Desktop` |
| model/version | `GPT-5` |
| validation_independence | `independent` |

Publisher `romanhladun24-dot` and replayer `akutenyov` are different human
contributors. Both used Codex/GPT-5, so this is independent-human,
same-tool validation.

## Replay Outcome

- Helper status: `PASS`.
- Compared numeric fields: `23`.
- Maximum absolute drift: `0.0`.
- Tolerance: `1.0e-9`.
- Joback aggregate MAE: `14.925825 K`, unchanged.
- Best non-oracle control MAE: `43.427943 K`, unchanged.
- Families clearing the 5 K margin: `7/8`, unchanged.
- Failed family: `esters/lactones`, unchanged.
- Existing verdict: `VALID_IN_RANGE`, unchanged.

## Scope Guard

The replay uses only the bounded 40-row Tb fixture and frozen Joback
implementation. It does not reopen the exact-80 expansion, fetch or commit raw
ThermoML bytes, fit a new estimator, or promote a universal Joback claim.
The esters/lactones negative-family memory remains paired with this result.

## Output Routing

- Canonical destinations: this review note and RESULT-0026 review metadata.
- Review tier: `AGENT_VALIDATED`, unchanged.
- Gate B: `PASS`.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: maintainer review remains required.
