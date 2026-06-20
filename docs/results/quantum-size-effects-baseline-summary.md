# Quantum Size Effects Baseline Summary

`TASK-0225` produced a `VALID_IN_RANGE` sandbox baseline on the six direct Almeida 2023 InP absorption rows.

The frozen selection chose `almeida_fixed_reference`. Its largest-size holdout absolute error is `0.048395 eV`, compared with `0.420200 eV` for the constant train-mean null and `0.375676 eV` for the deterministic shuffled-size control.

This establishes a reproducible source-scoped baseline surface for later review. It does not establish cross-material transfer, a universal size law, a material recommendation, or an independently validated quantum-confinement model.

Detailed evidence: `agent_runs/AGENT-RUN-0076/report.md`.
