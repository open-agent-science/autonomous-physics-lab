# Nuclear Mass Prediction Registry

`prediction_registry/nuclear_masses/` stores **prospective** nuclear-mass
predictions that are frozen before later measurements are reviewed.

This registry exists to separate:

- retrospective time-split benchmarks;
- sandbox residual comparisons;
- true before-measurement forecasts.

It is a review surface, not a claim surface:

- registry entries are not canonical `results/`;
- registry entries do not promote claims;
- registry entries do not become accepted knowledge automatically;
- registry entries require later maintainer-reviewed comparison against measured
  data before any stronger interpretation.

For nuclear-mass reveal work, use
[Nuclear Prediction Reveal Protocol](../../docs/nuclear-prediction-reveal-protocol.md)
before any source comparison or scoring task.

## Layout

Use one YAML file per registered prediction:

```text
prediction_registry/
  nuclear_masses/
    PRED-TEMPLATE.yaml
    PRED-0001.yaml
```

## Minimum Required Content

Every prediction entry must freeze:

- prediction id and task id;
- timestamp;
- repository source state, including git commit;
- frozen model reference and baseline reference;
- training / source dataset references;
- target nuclide list;
- predicted values and unit semantics;
- uncertainty or confidence semantics;
- reveal conditions and comparison trigger;
- explicit no-claim-promotion wording.

## Review Boundary

Before later measurement comparison, a registry entry may support only these
readings:

- "registered prospective forecast"
- "awaiting reveal"
- "review-needed pre-measurement record"

It may not support:

- claim promotion;
- canonical result creation;
- discovery wording;
- reframing a retrospective time-split benchmark as blind prediction.

## Validation

Prediction entries use the schema
`physics_lab/schemas/nuclear_mass_prediction.schema.json`.

Common checks:

```bash
python3 -m physics_lab.cli validate prediction_registry/nuclear_masses/PRED-0001.yaml --kind nuclear_mass_prediction
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
```

## Variant Factory Drafts

For larger pre-reveal variant waves, use the deterministic factory before
committing new registry entries:

```bash
python3 scripts/generate_nuclear_prediction_variants.py examples/nuclear_prediction_variant_factory.yaml
python3 scripts/generate_nuclear_prediction_variants.py examples/nuclear_prediction_variant_factory.yaml --write-drafts --output-dir /tmp/apl-nuclear-variant-drafts
```

The factory generates candidate slates and optional draft PRED-style YAML files
in an explicit scratch directory. It refuses to write into this committed
registry directory by default. Copy only reviewed, selected candidates into
`prediction_registry/nuclear_masses/` in a dedicated PR.
