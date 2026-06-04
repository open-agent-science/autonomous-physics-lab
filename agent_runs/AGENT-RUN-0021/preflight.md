# AGENT-RUN-0021 Preflight

**Task:** TASK-0321  
**Lane:** nuclear shell-axis magic-axis asymmetry audit  
**Mode:** sandbox-only retrospective audit

## Inputs Checked

- `TASK-0321`
- `scripts/run_nuclear_shell_axis_full_known_audit.py`
- `agent_runs/AGENT-RUN-0018/metrics.json`
- `docs/reviews/nuclear-shell-axis-validity-domain-after-0310.md`
- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`

## Guardrails

- Live external fetch: not allowed and not used.
- Prediction registry writes: not allowed and not used.
- Canonical results, claims, and knowledge promotion: not allowed and not used.
- PRED-0063 through PRED-0068 are not reveal-scored.

## Plan

1. Reuse the TASK-0310 committed full-known audit surface.
2. Evaluate proton-axis, neutron-axis, product, sign-inverted, shuffled, and baseline candidates.
3. Build deterministic non-magic A-matched controls for magic-N, magic-Z, near-magic, and double-magic subsets.
4. Report row counts, sparse warnings, subset deltas, and directional labels.
5. Keep outputs sandbox-only.
