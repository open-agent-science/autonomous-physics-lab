# AGENT-RUN-0019 Preflight

**Task:** TASK-0316
**Lane:** nuclear shell-axis coefficient stability audit
**Mode:** sandbox-only retrospective audit

## Inputs Checked

- `TASK-0316`
- `scripts/run_nuclear_shell_axis_full_known_audit.py`
- `agent_runs/AGENT-RUN-0018/metrics.json`
- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`

## Guardrails

- Live external fetch: not allowed and not used.
- Prediction registry writes: not allowed and not used.
- Canonical results, claims, and knowledge promotion: not allowed and not used.
- `PRED-0063` through `PRED-0068` are not reveal-scored.
