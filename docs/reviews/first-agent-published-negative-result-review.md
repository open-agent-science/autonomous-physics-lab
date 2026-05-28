# First AGENT_PUBLISHED Negative Result Review

**Task:** `TASK-0413`  
**Result ID:** `RESULT-0017`  
**Run:** `EXP-0001/RUN-0006`  
**Review tier:** `AGENT_PUBLISHED`  
**Verdict:** `OVERFITTED`

## Candidate Selection

This task selects the mature `EXP-0001` pendulum gauntlet overfit result as
the first negative/overfit `AGENT_PUBLISHED` result.

The source evidence is the legacy canonical `RESULT-0008` run at
`results/EXP-0001/RUN-0004/result.yaml`. That run already preserved the key
negative scientific memory: a systematic 100-candidate pendulum gauntlet can
find candidates that fit the configured training slice but fail enough
verification checks to remain `OVERFITTED` rather than validated.

This PR creates a new `RESULT-0017` artifact rather than rewriting
`RESULT-0008`, so the legacy result remains unchanged.

## Method

The deterministic workflow was replayed with:

```bash
python3 -m physics_lab.cli run examples/pendulum_agent_published_negative_result.yaml
```

The replay uses the committed `EXP-0001` experiment, `HYP-0001` hypothesis,
`TASK-0413` task contract, and `physics_lab/workflows/gauntlet.py` workflow.
It evaluates the legacy 10-atom candidate surface plus the configured
constrained comparison candidate. The current runner counts that comparison in
the 101-candidate total.

## Metrics Preserved

- Total candidates evaluated: `101`
- Best model: `model_t2_x4_l2`
- Best candidate verdict: `OVERFITTED`
- Verification gate passed: `false`
- Failing checks include small-angle window accuracy, large-angle window
  accuracy, and separatrix asymptotic alignment.
- Two legacy placeholder diagnostics are treated as non-passing in `RESULT-0017`
  so Gate A does not publish unresolved placeholder checks.

These numbers preserve the `RESULT-0008` overfit evidence pattern while using
the current runner's 101-candidate accounting. They are not edited to make the
result look stronger.

## Gate A Routing

- Canonical destination: `results/EXP-0001/RUN-0006/result.yaml`
- Review tier: `AGENT_PUBLISHED`
- Gate A status: local checker expected for
  `python3 scripts/apl_check_result_publication.py results/EXP-0001/RUN-0006/result.yaml`
- Gate B status: not attempted
- Claim impact: no claim status transition; `CLAIM-0001` remains `DRAFT`
- Knowledge impact: no knowledge status transition

`HYP-0001` is updated only to reference `RESULT-0017` in its evidence list so
the new canonical result is not orphaned.

## Limitations

- This is agent-published evidence only, not independently replayed or
  maintainer-reviewed interpretation.
- This is an ideal mathematical pendulum benchmark with no damping or driving.
- Candidate families are limited to the configured gauntlet basis.
- The result records an overfit/failed-verification surface only; it does not
  weaken already reviewed range-limited positive pendulum evidence.
- No exact symbolic formula, global-validity claim, or knowledge promotion is
  made.
