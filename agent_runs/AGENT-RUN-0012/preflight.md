# AGENT-RUN-0012 Preflight

TASK-0278 is sandbox-only. Inputs are limited to committed repository data:

- `results/EXP-0012/RUN-0001/result.yaml`
- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`

No live external measurements are fetched. No `prediction_registry/nuclear_masses/`
files are edited. The scout generates nine bounded shell-neighborhood variants,
executes six deterministic residual probes, rejects three before execution, and
preserves one near-null control.
