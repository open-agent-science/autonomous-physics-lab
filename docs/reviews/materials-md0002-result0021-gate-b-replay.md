# Materials MD-0002 RESULT-0021 Gate B replay

Task: `TASK-0775`
Result: `RESULT-0021`
Canonical artifact: `results/EXP-0014/RUN-0001/result.yaml`

## Replay Command

```powershell
$env:PYTHONPATH='C:\tmp\apl-task-0775'
& 'C:\Users\sviti\OneDrive\Documents\APL\.venv\Scripts\python.exe' scripts\apl_validate_agent_published_result.py results\EXP-0014\RUN-0001\result.yaml --output-dir .\_gateb_replay --validator-contributor-id romanhladun24-dot --validator-github-username romanhladun24-dot --validator-agent-tool Codex --validator-model GPT-5 --json
```

Replay output directory: `C:\tmp\apl-task-0775\_gateb_replay`

## Gate B Outcome

- Status: `PASS`
- Issues: none
- Contested report: none
- Verdict: `VALID_IN_RANGE` unchanged
- Review tier update: `AGENT_PUBLISHED` to `AGENT_VALIDATED`
- Tolerance: `1e-09`
- Compared numeric fields: `42`
- Maximum absolute drift: `0.0`

## Compared Metrics

- Cation-pair holdout MAE: expected `0.200606`, observed `0.200606`, delta `0.0`
- Global-median null holdout MAE: expected `0.506092`, observed `0.506092`, delta `0.0`
- Improvement absolute: expected `0.305485` eV/atom, observed `0.305485`, delta `0.0`
- Improvement fraction: expected `0.6036`, observed `0.6036`, delta `0.0`
- Split sensitivity range: expected and observed `0.172441` to `0.216158`
- Label-shuffle control minimum: expected and observed `0.530919`
- Cation-label-shuffle control minimum: expected and observed `0.474316`
- Row-order invariant flag: expected and observed `1`

## Limitations

This Gate B replay validates deterministic reproduction of the committed artifact only. `RESULT-0021` remains a computed-DFT benchmark on the frozen 362-row MD-0002 stable ternary-oxide slice. It is not a material recommendation, material-discovery claim, experimental measurement result, predictive materials model, or universal-law claim. Band gap remains diagnostic-only and excluded from promoted metrics.

## Output Routing

- Canonical destination: `results/EXP-0014/RUN-0001/result.yaml`
- Gate A status: `PASS` from the existing AGENT_PUBLISHED publication package
- Gate B status: `PASS`; replay metadata recorded under `agent_proposal_evaluation.validation_record`
- Claim impact: none
- Knowledge impact: none
- Publication blocker: none for `AGENT_VALIDATED`; maintainer endorsement is still required for any `MAINTAINER_REVIEWED` tier or claim/knowledge promotion
