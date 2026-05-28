# Limitations

Task: `TASK-0367`  
Agent run: `AGENT-RUN-0033`

- High-error membership and cluster labels still come from committed retrospective residuals; this lane sharpens controls but remains a diagnostic rather than a blind prediction.
- Coefficients are fit on the 11-row NMD-0002 training slice, so the leave-one-out stability check is itself a small-sample diagnostic.
- The three new adversarial controls do not exhaust the space of possible attacks (e.g. stronger label shuffles weighted by chain structure, richer non-linear smoothers, or feature-set ablations).
- Threshold perturbation rebuilds the ClusterIndex at each percentile, so cluster-membership composition shifts between thresholds; the diagnostic measures coefficient and delta stability rather than a fixed cluster definition.
- No live source fetch, reveal scoring, registry write, claim update, or canonical result write is authorized.
