# Particle Mass Dataset Schema Notes

This document defines the intended structure for particle-mass input files in
`data/particle_masses/`.

These files are lightweight YAML datasets, not claim artifacts.

## File Shape

Recommended top-level fields:

- `dataset_id`
- `title`
- `status`
- `description`
- `source_policy`
- `entries`

## Entry Fields

Each mass entry should record:

| Field | Required | Meaning |
| --- | --- | --- |
| `particle` | yes | canonical particle name |
| `symbol` | recommended | short particle symbol |
| `family` | yes | particle family, e.g. `charged_lepton` |
| `mass_value` | yes | central mass value |
| `mass_unit` | yes | unit for `mass_value`, usually `MeV` |
| `uncertainty` | yes | uncertainty object with value and unit |
| `source` | yes | structured source metadata |
| `mass_type` | yes | e.g. `pole`, `running`, or another explicit definition |
| `scheme` | yes | renormalization scheme when applicable; otherwise `null` |
| `scale` | yes | renormalization scale when applicable; otherwise `null` |
| `notes` | yes | interpretation caveats or source-specific remarks |

## Uncertainty Object

Use a structured uncertainty block:

```yaml
uncertainty:
  type: symmetric
  value: 0.0001
  unit: MeV
  confidence: one_sigma
```

If a source reports asymmetric uncertainty, use:

```yaml
uncertainty:
  type: asymmetric
  plus: 0.10
  minus: 0.12
  unit: MeV
  confidence: one_sigma
```

## Source Object

Recommended source fields:

```yaml
source:
  authority: Particle Data Group
  edition: "2025 update"
  citation: "S. Navas et al. (Particle Data Group), Phys. Rev. D 110, 030001 (2024) and 2025 update"
  url: "https://pdg.lbl.gov/2025/listings/rpp2025-list-electron.pdf"
  accessed_on: "2026-05-03"
  value_origin_note: "PDG listing carries the 2018 CODATA value"
```

## Interpretation Rules

- `mass_value` and `uncertainty` must use the same unit.
- `mass_type` must be explicit even when the value looks standard.
- `scheme` and `scale` must never be omitted.
- `scheme: null` and `scale: null` are allowed only when the source does not
  require them.
- future quark datasets must not reuse charged-lepton conventions blindly,
  because quark masses often depend on scheme and scale.

## Non-Goals

These dataset files should not contain:

- Koide ratios;
- fitted constants;
- benchmark verdicts;
- claim promotion language;
- unexplained mixed-source averages.
