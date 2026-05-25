# Limitations

Task: `TASK-0367`
Agent run: `AGENT-RUN-0033`

- The audit is retrospective and depends on committed full-known baseline residual labels.
- The high-error threshold perturbation uses p80 as one deterministic stronger threshold; other perturbations may differ.
- The smooth-A/local-density control is intentionally simple and does not exhaust all smoothers.
- Leave-one-training-row-out stability is deterministic but limited by the small training residual slice.
- No live fetch, reveal scoring, registry write, canonical result, claim, or knowledge update is authorized.
