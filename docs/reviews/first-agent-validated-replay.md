# First AGENT_VALIDATED replay review

**Task:** `TASK-0415`  
**Result:** `RESULT-0016`  
**Artifact:** `results/EXP-0011/RUN-0002/result.yaml`  
**Replay output:** `/tmp/apl-gateb-result-0016`

## Scope

This review records the first Gate B replay of an `AGENT_PUBLISHED` result.
It upgrades `RESULT-0016` to `AGENT_VALIDATED` because the deterministic replay
matched the committed result metrics within tolerance and preserved the
`VALID_IN_RANGE` verdict. It does not promote any claim, update knowledge, pin
the result to `results/golden-results.yaml`, or change the benchmark numbers.

## Replay Command

```bash
python3 scripts/apl_validate_agent_published_result.py results/EXP-0011/RUN-0002/result.yaml --output-dir /tmp/apl-gateb-result-0016 --validator-contributor-id roman --validator-github-username gladunrv --validator-agent-tool codex --validator-model "GPT-5 Codex" --json
```

## Gate B Outcome

- Status: `PASS`
- Compared metrics: `36`
- Maximum absolute numeric drift: `0.0`
- Tolerance: `1.0e-09`
- Verdict unchanged: `VALID_IN_RANGE`
- Contested report: none

## Warning Preserved

The replay helper emitted `original-publisher-unknown` because `RESULT-0016`
does not store original publisher metadata inside `agent_proposal_evaluation`.
The replay identity is recorded in `validation_record`, but the helper cannot
mechanically compare the original and validating agents for this older
AGENT_PUBLISHED artifact.

## Result Routing

- Canonical destination: `results/EXP-0011/RUN-0002/result.yaml`
- Review tier: `AGENT_VALIDATED`
- Gate A status: already satisfied by `TASK-0412`
- Gate B status: `PASS`
- Claim impact: none
- Knowledge impact: none
- Publication blocker: maintainer review is still required before any claim
  status transition.

## Verdict

`VALID_IN_RANGE` result replayed with Gate B `PASS`; review tier upgraded to
`AGENT_VALIDATED`.
