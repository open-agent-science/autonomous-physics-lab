# Materials RESULT-0021 Independent-Human Replay

- Task: `TASK-1044`
- Result: `RESULT-0021`
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

Publisher `gladunrv` and replayer `akutenyov` are different human
contributors. Both used Codex/GPT-5, so this is independent-human,
same-tool validation.

## Replay

```powershell
python scripts/apl_validate_agent_published_result.py `
  results/EXP-0014/RUN-0001/result.yaml `
  --root . `
  --output-dir C:\tmp\apl-task-1044-gateb-final `
  --validator-contributor-id akutenyov `
  --validator-github-username akutenyov `
  --validator-agent-tool "Codex Desktop" `
  --validator-model "GPT-5" `
  --expect-status PASS `
  --json
```

The helper executed the committed command:
`physics-lab run examples/materials_md0002_formation_energy_benchmark.yaml`.

## Outcome

- Helper status: `PASS`.
- Compared numeric fields: `42`.
- Maximum absolute drift: `0.0`.
- Tolerance: `1.0e-9`.
- Existing verdict: `VALID_IN_RANGE`, unchanged.
- Existing model: `model_cation_pair_mean`, unchanged.

## Scope Guard

The replay used the frozen 362-row computed-DFT MD-0002 slice and changed no
source data, split, controls, metrics, model, result scope, claim, knowledge,
or release artifact. This is deterministic reproducibility evidence only, not
a materials-discovery or universal-law claim.

## Output Routing

- Canonical destinations: this review note and RESULT-0021 review metadata.
- Review tier: `AGENT_VALIDATED`, unchanged.
- Gate B: `PASS`.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: maintainer review remains required.
