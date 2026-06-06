# Materials MD-0001 Formation-Energy Factory Smoke Sprint

**Task:** `TASK-0626`
**Outcome:** `NEGATIVE`

## Summary

This smoke sprint runs bounded residual-offset candidates on committed MD-0001 formation-energy rows only. It keeps the frozen cation-group baseline and split, runs deterministic controls, excludes band gap, and creates no result, prediction, claim, knowledge, or materials guidance.

## Decision

- Best candidate: `oxygen_stoichiometry_residual_offsets`.
- Best control: `cation_group_shuffle_control`.
- Candidate minus best-control penalized holdout improvement: `0.038777` eV/atom.
- Interpretation: No candidate clears the frozen baseline plus controls in this smoke sprint.

## Candidate Slate

| lane | validation improvement | holdout improvement | penalized holdout | verdict |
| --- | ---: | ---: | ---: | --- |
| `cation_group_residual_offsets` | `0.0` | `0.0` | `-0.06` | `negative` |
| `formula_family_residual_offsets` | `-0.016832` | `-0.067957` | `-0.127957` | `negative` |
| `oxygen_stoichiometry_residual_offsets` | `-0.043205` | `-0.002585` | `-0.032585` | `negative` |
| `formula_family_x_cation_group_offsets` | `0.005677` | `-0.12619` | `-0.40619` | `negative` |

## Controls

| control | holdout improvement | penalized holdout |
| --- | ---: | ---: |
| `label_shuffle_control` | `0.000662` | `-0.259338` |
| `cation_group_shuffle_control` | `-0.011362` | `-0.071362` |
| `matched_random_formula_family_control` | `-0.012435` | `-0.072435` |

## Output Routing Summary

- Task verdict: `NEGATIVE`.
- Canonical destination: `agent_runs/AGENT-RUN-0069/metrics.json`, `agent_runs/AGENT-RUN-0069/report.md`, `docs/reviews/materials-md0001-formation-energy-factory-smoke-sprint.md`.
- Review tier: `none`.
- Gate A status: `not_attempted`.
- Gate B status: `not_applicable`.
- Claim impact: `none`.
- Knowledge impact: `none`.
- Result impact: `no RESULT artifact created`.
- Publication blocker: `diagnostic-only factory smoke sprint; no canonical result promotion in task scope`.
