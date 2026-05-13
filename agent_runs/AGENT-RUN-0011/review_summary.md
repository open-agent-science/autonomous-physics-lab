# AGENT-RUN-0011 Review Summary

## Maintainer Decision Requested

Review `TASK-0201` as a sandbox-complete pairing / odd-even batch. The evidence
supports preserving the run as negative and split-sensitive diagnostic context,
not promoting any candidate.

## Files To Review

- `scripts/run_nuclear_pairing_batch.py`
- `tests/test_nuclear_pairing_batch.py`
- `agent_runs/AGENT-RUN-0011/metrics.json`
- `agent_runs/AGENT-RUN-0011/report.md`
- `hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0038-odd-a-offset.yaml`
- `hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0039-pairing-class-offsets.yaml`
- `hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0040-free-odd-even-exponent-rejected.yaml`
- `hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0041-per-chain-odd-even-rejected.yaml`
- `hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0042-pairing-shell-interaction-rejected.yaml`
- `experiment_proposals/nuclear-mass/EXP-PROPOSAL-0008-nuclear-pairing-batch.yaml`
- `docs/reviews/autonomous-nuclear-pairing-batch-01.md`

## Review Reading

- The odd-A offset is the only internally positive candidate, but it regresses
  post-AME2020 primary MAE by `+0.0796 MeV`.
- The pairing-class offsets are overfit under structured holdouts and regress
  primary MAE by `+0.0876 MeV`.
- No canonical scientific memory artifact is changed.
