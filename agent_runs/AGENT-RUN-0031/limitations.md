# Limitations

Task: `TASK-0351`
Agent run: `AGENT-RUN-0031`

- Features still use committed full-known neighbor residual context and are retrospective diagnostics, not blind predictions.
- Coefficients are fit on the 11-row NMD-0002 residual slice; small-sample fit variance limits the precision of the survival-margin check.
- The label-shuffle control uses a deterministic Z permutation; alternative permutation schemes may produce different control strengths.
- The chain-blind smoother uses a simple 1-D linear regression over the A-window; richer smoothers (local quadratic, loess) are not exercised here.
- No live source fetch, reveal scoring, registry write, claim update, or canonical result write is authorized.
