# Stellar M-L RESULT-0022 Gate B replay

Task: `TASK-0776`
Result: `RESULT-0022`
Canonical artifact: `results/EXP-0015/RUN-0001/result.yaml`

## Replay Command

```powershell
$env:PYTHONPATH='C:\tmp\apl-task-0776'
& 'C:\Users\sviti\OneDrive\Documents\APL\.venv\Scripts\python.exe' scripts\apl_validate_agent_published_result.py results\EXP-0015\RUN-0001\result.yaml --output-dir .pytest-basetemp\task0776-gateb-replay --validator-contributor-id romanhladun24-dot --validator-github-username romanhladun24-dot --validator-agent-tool Codex --validator-model GPT-5 --json
```

Replay output directory: `C:\tmp\apl-task-0776\.pytest-basetemp\task0776-gateb-replay`

## Gate B Outcome

- Status: `PASS`
- Issues: none
- Contested report: none
- Verdict: `VALID_IN_RANGE` unchanged
- Review tier update: `AGENT_PUBLISHED` to `AGENT_VALIDATED`
- Tolerance: `1e-09`
- Compared numeric fields: `68`
- Maximum absolute drift: `0.0`

## Compared Metrics

- Textbook alpha=3.5 holdout MAE: expected `0.184954` dex, observed `0.184954`, delta `0.0`
- Train-fitted alpha holdout MAE: expected `0.119925` dex, observed `0.119925`, delta `0.0`
- Piecewise alpha=4.0 holdout MAE: expected `0.137608` dex, observed `0.137608`, delta `0.0`
- Per-mass-band null holdout MAE: expected `0.331817` dex, observed `0.331817`, delta `0.0`
- Single alpha=3.5 minus fitted gap: expected `0.065029` dex, observed `0.065029`, delta `0.0`
- Single alpha=3.5 minus piecewise gap: expected `0.047346` dex, observed `0.047346`, delta `0.0`
- Split/noise margin range: expected and observed `0.102269` to `0.180271` dex
- Luminosity-shuffle maximum margin: expected and observed `-0.092278` dex
- Stage diagnostics: main-sequence `0.184954`, subgiant `0.30805`, evolved `1.708908`, unknown `0.237776` dex

## Limitations

This Gate B replay validates deterministic reproduction of the committed artifact only. `RESULT-0022` remains scoped to the frozen CC-BY-4.0 DEBCat main-sequence-compatible slice (0.5-2.0 Msun, 223 components). It does not validate or falsify the mass-luminosity relation universally and does not support stellar-evolution, target-priority, application-domain, or other astrophysical discovery claims. Evolved/subgiant/unknown stages remain diagnostics only.

## Output Routing

- Canonical destination: `results/EXP-0015/RUN-0001/result.yaml`
- Gate A status: `PASS` from the existing AGENT_PUBLISHED publication package
- Gate B status: `PASS`; replay metadata recorded under `agent_proposal_evaluation.validation_record`
- Claim impact: none
- Knowledge impact: none
- Publication blocker: none for `AGENT_VALIDATED`; maintainer endorsement is still required for any `MAINTAINER_REVIEWED` tier or claim/knowledge promotion
