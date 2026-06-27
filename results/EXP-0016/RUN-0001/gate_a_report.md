# Gate A Report — RESULT-0023 (FIRAS/Wien consistency slice)

- Artifact: `results/EXP-0016/RUN-0001/result.yaml` · Task: TASK-0845 · Exp: EXP-0016 · Hyp: HYP-0016
- Checker: `python3 scripts/apl_check_result_publication.py results/EXP-0016/RUN-0001/result.yaml`
- Result: PASS · Tier: AGENT_PUBLISHED · Verdict: VALID_IN_RANGE (CONSISTENT_IN_SCOPE)

## Headline
raw-bin relative difference 0.013071 (tol 0.02); interpolated 0.000917 (tol 0.005);
4/4 predeclared controls pass; reference T 2.72548 K (separately pinned).

## Routing
- Canonical destination: `results/EXP-0016/RUN-0001/` (RESULT-0023).
- Gate A: PASS. Gate B: NOT attempted — needs engine-workflow repackaging (TASK-0786/0799 pattern), then a different agent replays.
- Claim impact: none. Knowledge impact: none.
- Limitation: FIRAS spectral-domain self-consistency only (reference T is FIRAS-derived).
