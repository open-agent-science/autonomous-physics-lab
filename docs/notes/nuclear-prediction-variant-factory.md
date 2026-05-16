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
   bounded coefficient transforms, and target batches. Prefer the reusable
   target-batch library for common Nuclear Mass Surface review sets.
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

## Reusable Target-Batch Library

`TASK-0254` adds a reviewed target-batch library at
`data/nuclear_masses/factory_target_batches.yaml`. Factory configs can reuse
those batches instead of repeating target lists:

```yaml
target_batch_library:
  path: data/nuclear_masses/factory_target_batches.yaml
  include_batches:
    - frontier-next-row
    - odd-even-pairing-probe
```

The library currently includes reviewed batches for:

- frontier controls;
- odd-even and pairing probes;
- shell and magic-number probes;
- neutron-rich stress tests;
- isotope-chain probes;
- mid-mass region probes.

Each batch records rationale and limitations. The factory validation layer
checks that target rows satisfy `A = Z + N`, that nuclide ids are unique within
each batch, and that committed measured or holdout rows are not accidentally
included unless a batch is explicitly labeled `retrospective_control: true`.
This guardrail uses committed repository files only and does not fetch live
external measurements.

Configs may still define small inline `target_batches` for one-off scratch
experiments. If a config uses both a library and inline batches, labels must
not collide; this keeps reviewed batch reuse explicit.

## Slate Ranking Helper

Once a factory config is generated, use the slate ranking helper to surface
diversity and risk signals before committing any candidates to the registry:

```bash
python3 scripts/generate_nuclear_prediction_variants.py \
  examples/nuclear_prediction_variant_factory.yaml \
  --summary-out /tmp/apl-nuclear-factory-summary.yaml

python3 scripts/rank_nuclear_prediction_variant_slate.py \
  /tmp/apl-nuclear-factory-summary.yaml \
  --out /tmp/apl-nuclear-factory-ranking.md
```

The ranking report covers:

- candidate count and target-batch coverage;
- model-family prefix coverage;
- duplicate prediction ids and near-duplicate value vectors;
- delta sensitivity table sorted by largest absolute delta from baseline;
- heuristic flags: `EXTREME_SENSITIVITY`, `ALL_ZERO_DELTA`,
  `REDUNDANT_TARGET_BATCH`, `MISSING_REVIEW_NOTES`, `DUPLICATE_PREDICTION_ID`,
  `NEAR_DUPLICATE_VECTOR`.

The report assigns no scientific success scores and makes no comparison against
future or holdout measurements. It is a deterministic pre-selection triage
aid only. Implementation lives in
`physics_lab/engines/nuclear_prediction_variant_review.py`.

## Next Factory Wave

After `TASK-0249`, the recommended next work is:

- `TASK-0252`: extend the factory beyond coefficient transforms into bounded
  shell, magic-number, and neutron-excess feature terms;
- `TASK-0250`: generate and review the first larger factory slate, without
  committing draft PRED YAML files, and run the ranking helper on the summary;
- `TASK-0254`: create a reusable target-batch library for future factory runs;
- `TASK-0251`: register only the selected slate entries as `PRED-0041+` after
  `TASK-0250` is reviewed.

The important split is generation before registration. Large slates may be
useful for search and review, but the registry should contain only a curated
subset with stable reveal conditions.

The older manual registry lanes `TASK-0233`, `TASK-0234`, `TASK-0235`, and
`TASK-0237` are paused as fallback lanes. Their scientific ideas remain useful,
but they should normally be represented inside the factory slate rather than
committed as isolated hand-written PRED pairs.

## Supported First-Pass Variant Families

The initial implementation supports semi-empirical coefficient transforms:

- `scale`: multiply one or more coefficients by bounded factors;
- `delta`: add bounded offsets;
- `set`: ablate or freeze coefficients to explicit values;
- `blend_with_reference`: interpolate the current coefficient set with the
  repository reference semi-empirical coefficients.

This covers smooth controls, pairing sensitivity, and ablation-style variants.

## Supported Feature-Term Families

`TASK-0252` extends the factory beyond pure coefficient transforms with bounded
additive feature terms. Each feature term contributes an additive correction
`r_corr` (in MeV) to the semi-empirical binding energy before mass-excess
conversion. Multiple terms in one variant are summed; coefficient transforms
and feature terms compose freely in the same `transform` block.

A worked example lives at
`examples/nuclear_prediction_variant_factory_feature_terms.yaml`.

### `shell_proximity_gaussian`

```text
r_corr = coefficient * exp(-d(axis_value, magic_numbers)^2 / (2 * sigma^2))
```

Required:

- `axis`: `z` or `n`
- `coefficient` (MeV)

Optional:

- `sigma` (default `2.0`; must be `> 0`)
- `magic_numbers` (default `(2, 8, 20, 28, 50, 82, 126)`)

Use a separate term per axis when both axes need their own coefficient (this
mirrors the `PRED-0025` Z+N control pattern).

### `asymmetry_polynomial`

```text
r_corr = sum_k coefficient_k * ((N - Z) / A) ** power_k
```

Required:

- `terms`: a non-empty list of `{power, coefficient}` entries

Each `power` must be an integer in `[1, 6]`. Duplicate powers in the same term
list are rejected.

### `asymmetric_neutron_excess`

```text
r_corr = coefficient * max(N - Z, 0) ** power / A
```

Required:

- `coefficient` (MeV)

Optional:

- `power` (default `2`; integer `>= 1`)

Returns exactly `0.0` for neutron-poor (`N <= Z`) targets, which is the design
intent of the control family from `PRED-0028`.

### Combining Coefficient and Feature-Term Transforms

```yaml
transform:
  scale:
    asymmetry: 1.01
  feature_terms:
    - type: shell_proximity_gaussian
      axis: n
      coefficient: 1.6049071729432316
```

Coefficient transforms reshape the SEMF baseline; feature terms add a separate
deterministic correction to the resulting binding energy. Both contributions
appear in the candidate slate summary, and per-target rows expose
`feature_term_correction_mev` whenever a variant uses feature terms.

More complex ensemble controls or trainable feature families should be added
only when they can still be made deterministic and reviewable.

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
