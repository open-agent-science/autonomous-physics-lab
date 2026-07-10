# Quantum RESULT-0029 Independent-Human Replay

- Task: `TASK-1015`
- Result artifact: `results/EXP-0022/RUN-0001/result.yaml`
- Existing verdict: `INCONCLUSIVE`
- Task verdict: `INDEPENDENT_GATE_B_PASS`
- Replay date: 2026-07-10

## Replayer Identity

| Field | Value |
| --- | --- |
| contributor_id | `akutenyov` |
| github_username | `akutenyov` |
| agent_tool | `Codex Desktop` |
| model/version | `GPT-5` |
| validation_independence | `independent` |

Publisher `gladunrv` and replayer `akutenyov` are different human
contributors. This satisfies the task's independent-human requirement.

## Replay Command

```powershell
python scripts/apl_validate_agent_published_result.py `
  results/EXP-0022/RUN-0001/result.yaml `
  --root . `
  --output-dir C:\Users\Master\Documents\APL\.task-1015-runtime\replay `
  --tolerance 1e-9 `
  --validator-contributor-id akutenyov `
  --validator-github-username akutenyov `
  --validator-agent-tool "Codex Desktop" `
  --validator-model "GPT-5" `
  --expect-status PASS `
  --json
```

The helper replayed the committed command without changing it:

```text
python -m physics_lab.cli run examples/quantum_znse_contract_transfer_result.yaml
```

## Outcome

- Helper status: `PASS`.
- Compared numeric metrics: `22`.
- Metrics within tolerance: `22/22`.
- Tolerance: `1.0e-9`.
- Maximum absolute drift: `0.0`.
- Existing verdict: `INCONCLUSIVE`, unchanged.
- Best model: `model_inp_no_refit_confinement_power_law`, unchanged.

The primary margin remains `0.04658368 eV`, below the frozen `0.05 eV`
survival rule by `0.00341632 eV`. Independent replay strengthens the trust in
deterministic reproduction; it does not turn the inconclusive scientific
outcome into a positive result.

## Scope Guard

No input, code reference, threshold, margin, metric, model id, scientific
verdict, claim, or knowledge artifact changed. No refit, correction search,
effective-mass rescue, or new benchmark was performed.

## Output Routing

- Canonical destinations: this replay note and RESULT-0029 review metadata.
- Review tier: `AGENT_VALIDATED`, unchanged.
- Effective validation independence: `independent`.
- Prior same-account/different-tool replay: retained in `replays` history.
- Claim impact: none.
- Knowledge impact: none.
- Scientific metric and verdict impact: none.
