# AGENT-RUN-0020 Preflight

**Task:** TASK-0317  
**Lane:** nuclear shell-axis specificity controls  
**Mode:** sandbox-only retrospective control audit

## Inputs Checked

- `tasks/TASK-0317-run-nuclear-shell-axis-specificity-controls.yaml`
- `scripts/run_nuclear_shell_axis_full_known_audit.py`
- `agent_runs/AGENT-RUN-0018/metrics.json`
- `agent_runs/AGENT-RUN-0019/metrics.json`
- `results/EXP-0012/RUN-0001/result.yaml`
- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`

## Guardrails

- Live external fetch: not allowed and not used.
- Prediction registry writes: not allowed and not used.
- Canonical results, claims, and knowledge promotion: not allowed and not used.
- PRED-0063 through PRED-0068 are not reveal-scored.

## Plan

1. Reuse the TASK-0310 committed full-known audit surface.
2. Recompute the three primary shell-axis candidates.
3. Fit predeclared low-complexity non-shell controls on the same 11 training rows.
4. Report full-known, holdout, training, magic-Z, magic-N, light, and worst-regression deltas.
5. Classify specificity conservatively and keep outputs sandbox-only.
