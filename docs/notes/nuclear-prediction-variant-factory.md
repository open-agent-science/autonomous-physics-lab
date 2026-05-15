# Nuclear Prediction Variant Factory

## Purpose

The nuclear prediction variant factory turns bounded Nuclear Mass Surface
variant ideas into deterministic candidate slates.

It is not a reveal workflow and not a claim-promotion workflow. The factory
exists so agents can spend attention on model choice, leakage review,
complexity, target selection, and scientific value while repository code
handles coefficient transforms, target-batch expansion, and `mass_excess_mev`
calculation.

## Workflow

1. Define a YAML config with the frozen baseline source, source-state metadata,
   bounded coefficient transforms, and target batches.
2. Generate a candidate slate:

   ```bash
   python3 scripts/generate_nuclear_prediction_variants.py examples/nuclear_prediction_variant_factory.yaml
   ```

3. Optionally write draft PRED-style YAML files to a scratch directory:

   ```bash
   python3 scripts/generate_nuclear_prediction_variants.py \
     examples/nuclear_prediction_variant_factory.yaml \
     --write-drafts \
     --output-dir /tmp/apl-nuclear-variant-drafts
   ```

4. Review the slate for leakage, duplicate hypotheses, target quality,
   coefficient sensitivity, and no-claim wording.
5. Copy only selected draft entries into `prediction_registry/nuclear_masses/`
   in a dedicated reviewed PR.

## Next Factory Wave

After `TASK-0249`, the recommended next work is:

- `TASK-0250`: generate and review the first larger factory slate, without
  committing draft PRED YAML files;
- `TASK-0252`: extend the factory beyond coefficient transforms into bounded
  shell, magic-number, and neutron-excess feature terms;
- `TASK-0253`: add a deterministic slate-ranking helper for redundancy,
  coverage, and sensitivity review;
- `TASK-0254`: create a reusable target-batch library for future factory runs;
- `TASK-0251`: register only the selected slate entries as `PRED-0041+` after
  `TASK-0250` is reviewed.

The important split is generation before registration. Large slates may be
useful for search and review, but the registry should contain only a curated
subset with stable reveal conditions.

## Supported First-Pass Variant Families

The initial implementation supports semi-empirical coefficient transforms:

- `scale`: multiply one or more coefficients by bounded factors;
- `delta`: add bounded offsets;
- `set`: ablate or freeze coefficients to explicit values;
- `blend_with_reference`: interpolate the current coefficient set with the
  repository reference semi-empirical coefficients.

This covers smooth controls, pairing sensitivity, and ablation-style variants.
More complex shell, neutron-excess, or ensemble controls should be added only
when they can still be made deterministic and reviewable.

## Guardrails

- `source_state.live_external_fetch_allowed` must be `false`.
- The only supported factory quantity is currently `mass_excess_mev`.
- Draft PRED YAML is written only to an explicit output directory.
- Writing directly into `prediction_registry/nuclear_masses/` is blocked by
  default; selected candidates should be copied into the registry separately
  after review.
- Duplicate requested `prediction_id` values and duplicate draft filenames are
  rejected before writing.
- Generated candidates remain prospective pre-reveal records. They do not
  become results, claims, accepted knowledge, or evidence of predictive success
  until later maintainer-reviewed reveal work exists.
