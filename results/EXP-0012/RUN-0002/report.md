# AGENT-RUN-0068 - Nuclear F2 Survival-Margin Component Ablation

**Task:** `TASK-0625`
**Outcome:** `COMPONENT_DIAGNOSTIC_ONLY`

## Summary

This run applies a predeclared component ablation to the frozen F2 finer taxonomy. It keeps the committed NMD-0003 rows, stratified split, region baseline, and controls-first survival rule unchanged. No prediction, result, claim, knowledge, or discovery wording is created.

## Decision

- Classification: `COMPONENT_DIAGNOSTIC_ONLY`.
- Best single-component variant: `only_magic_n_near` with `0.074761` MeV full-known MAE improvement.
- Full F2 reference improvement: `0.200411` MeV.
- Interpretation: only_magic_n_near carries useful diagnostic signal, but no ablation variant clears the predeclared controls-first survival margin.

## Variant Slate

| variant | active components | validation improvement | full-known improvement | margin clears |
| --- | --- | ---: | ---: | --- |
| `full_f2_reference` | doubly_magic_near, light_a_lt_50, magic_n_near, magic_z_near, mid_shell_balanced, mid_shell_neutron_rich | `0.193465` | `0.200411` | `False` |
| `without_doubly_magic_near` | light_a_lt_50, magic_n_near, magic_z_near, mid_shell_balanced, mid_shell_neutron_rich | `0.13644` | `0.170684` | `False` |
| `without_magic_z_near` | doubly_magic_near, light_a_lt_50, magic_n_near, mid_shell_balanced, mid_shell_neutron_rich | `0.21491` | `0.204096` | `False` |
| `without_magic_n_near` | doubly_magic_near, light_a_lt_50, magic_z_near, mid_shell_balanced, mid_shell_neutron_rich | `0.141841` | `0.12565` | `False` |
| `without_mid_shell_neutron_rich` | doubly_magic_near, light_a_lt_50, magic_n_near, magic_z_near, mid_shell_balanced | `0.140672` | `0.144523` | `False` |
| `without_mid_shell_balanced` | doubly_magic_near, light_a_lt_50, magic_n_near, magic_z_near, mid_shell_neutron_rich | `0.139331` | `0.155521` | `False` |
| `without_light_a_lt_50` | doubly_magic_near, magic_n_near, magic_z_near, mid_shell_balanced, mid_shell_neutron_rich | `0.194132` | `0.20158` | `False` |
| `only_doubly_magic_near` | doubly_magic_near | `0.057025` | `0.029727` | `False` |
| `only_magic_z_near` | magic_z_near | `-0.021445` | `-0.003685` | `False` |
| `only_magic_n_near` | magic_n_near | `0.051625` | `0.074761` | `False` |
| `only_mid_shell_neutron_rich` | mid_shell_neutron_rich | `0.052793` | `0.055888` | `False` |
| `only_mid_shell_balanced` | mid_shell_balanced | `0.054135` | `0.04489` | `False` |
| `only_light_a_lt_50` | light_a_lt_50 | `-0.000667` | `-0.001169` | `False` |

## Output Routing Summary

- Task verdict: `COMPONENT_DIAGNOSTIC_ONLY`.
- Canonical destination: `agent_runs/AGENT-RUN-0068/metrics.json`, `agent_runs/AGENT-RUN-0068/report.md`, `docs/reviews/nuclear-f2-survival-margin-component-ablation.md`.
- Review tier: `none`.
- Gate A status: `not_attempted`.
- Gate B status: `not_applicable`.
- Claim impact: `none`.
- Knowledge impact: `none`.
- Result impact: `no RESULT artifact created`.
- Publication blocker: `diagnostic-only ablation; no canonical result promotion in task scope`.
