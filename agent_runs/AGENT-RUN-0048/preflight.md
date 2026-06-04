# AGENT-RUN-0048 Preflight

**Task:** TASK-0476
**Lane:** nuclear isotope-chain leave-family-out audit
**Mode:** sandbox-only retrospective audit

## Inputs Checked

- `TASK-0476`
- `agent_runs/AGENT-RUN-0018/metrics.json`
- `agent_runs/AGENT-RUN-0020/metrics.json`
- `agent_runs/AGENT-RUN-0021/metrics.json`
- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`

## Guardrails

- Live external fetch: not allowed and not used.
- Prediction registry writes: not allowed and not used.
- Canonical results, claims, and knowledge promotion: not allowed and not used.
- New formula families: not fit.
