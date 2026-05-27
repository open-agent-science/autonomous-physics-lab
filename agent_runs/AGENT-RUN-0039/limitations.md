# Limitations

Task: `TASK-0394`
Agent run: `AGENT-RUN-0039`

- Retrospective committed rows are used; this is not strict blind prediction evidence.
- Fold-local fitting over the 11-row NMD-0002 slice can be coefficient-sensitive.
- The no-leakage controls are bounded and deterministic, not exhaustive.
- No live fetch, reveal scoring, registry write, canonical result, claim, or knowledge update is authorized.
