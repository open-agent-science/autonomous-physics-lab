# Nuclear Mass Dataset Schema Notes

This document defines the intended structure for nuclear mass input files in
`data/nuclear_masses/`.

These files are lightweight YAML datasets, not benchmark verdicts or claim
artifacts.

## File Shape

Recommended top-level fields:

- `dataset_id`
- `title`
- `status`
- `description`
- `source_policy`
- `source_dataset`
- `entries`

## Top-Level Source Fields

`source_dataset` should be a structured mapping such as:

```yaml
source_dataset:
  authority: "Atomic Mass Evaluation"
  version: "AME20XX"
  citation: "Exact citation string"
  url: "https://example.org/source-table"
  accessed_on: "2026-05-10"
  checksum_sha256: "..."
  checksum_scope: "raw table file"
  license_note: "Redistribution note or packaging caveat"
```

## Entry Fields

Each nuclide entry should record:

| Field | Required | Meaning |
| --- | --- | --- |
| `nuclide_id` | yes | stable nuclide key such as `He-4` |
| `element` | yes | human-readable element name |
| `symbol` | yes | chemical symbol |
| `Z` | yes | proton number |
| `N` | yes | neutron number |
| `A` | yes | mass number |
| `evaluation` | yes | `measured`, `extrapolated`, or `unspecified` |
| `source_entry` | yes | source-specific row or table note |
| `notes` | yes | interpretation caveats |

## Supported Numeric Encodings

Each entry must contain at least one complete numeric pair:

1. Atomic-mass encoding

```yaml
atomic_mass_u: 4.00260325413
atomic_mass_uncertainty_u: 0.00000000006
```

2. Mass-excess encoding

```yaml
mass_excess_keV: 2424.9156
mass_excess_uncertainty_keV: 0.0001
```

Storing both is allowed. The loader will normalize both views into a consistent
derived representation.

## Interpretation Rules

- `A` must equal `Z + N`.
- `evaluation` must never be omitted.
- if only one numeric encoding is stored, the other must be derived
  deterministically by the engine rather than copied manually without source.
- uncertainty values use the same unit family as the field they accompany.
- benchmark or correction-model outputs must not be embedded in the dataset.

## Derived Helper Targets

The engine currently derives:

- atomic mass in `u`
- mass excess in `keV`
- binding energy in `MeV`
- binding energy per nucleon in `MeV`

These are deterministic convenience targets for later baseline and holdout
tasks. They are not correction-model outputs.

## Non-Goals

These dataset files should not contain:

- fitted correction parameters;
- benchmark verdicts;
- shell-model claims;
- holdout scores;
- unlabeled mixtures of measured and extrapolated data.
