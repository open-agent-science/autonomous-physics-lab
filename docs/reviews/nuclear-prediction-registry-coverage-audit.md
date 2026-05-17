# Nuclear Prediction Registry Coverage Audit

**Task:** TASK-0272
**Machine-readable summary:** `data/nuclear_masses/nuclear_prediction_registry_coverage.yaml`
**Registry scope:** `prediction_registry/nuclear_masses/PRED-0001.yaml` through `PRED-0062.yaml`
**Live external fetch allowed:** `false`

This audit maps the committed nuclear prediction registry after the selected
feature-term factory wave. It does not reveal, score, validate, or promote any
prediction. It is a pre-reveal coverage and risk review for future planning.

## Method

The audit uses committed registry YAML only:

```bash
python3 scripts/audit_nuclear_prediction_registry_coverage.py \
  --out data/nuclear_masses/nuclear_prediction_registry_coverage.yaml
```

The helper validates entries through the existing nuclear prediction registry
loader, groups entries by task/source lane, target batch, quantity,
transform-class heuristic, target-domain heuristic, repeated nuclides, and
reveal-readiness flags.

Limitations:

- group labels are inferred from metadata, task ids, model ids, and target
  labels;
- repeated targets are review signals, not automatic errors;
- no measurement source is fetched or compared;
- reveal eligibility still needs a later source manifest and no-peek audit.

## Registry Scope

| Metric | Value |
| --- | ---: |
| Committed entries | 54 |
| Target rows | 213 |
| Lowest id | `PRED-0001` |
| Highest id | `PRED-0062` |
| Quantity | `mass_excess_mev` only |
| `live_external_fetch_allowed` values | `false` only |

The numeric id range intentionally has gaps:

- `PRED-0031` through `PRED-0036`
- `PRED-0039`
- `PRED-0040`

Those gaps are not a validation error. They reflect earlier selected waves and
deferred/manual lanes rather than a contiguous registry guarantee.

## Source-Lane Coverage

| Source task | Entries | Interpretation |
| --- | ---: | --- |
| `TASK-0205` | 20 | First broad prospective registry wave. |
| `TASK-0265` | 12 | Selected feature-term factory wave, `PRED-0051` through `PRED-0062`. |
| `TASK-0251` | 10 | Selected coefficient-transform factory wave, `PRED-0041` through `PRED-0050`. |
| `TASK-0228` | 2 | Smooth semi-empirical controls. |
| `TASK-0229` | 2 | Pairing / odd-even controls. |
| `TASK-0230` | 2 | Shell and magic-number controls. |
| `TASK-0231` | 2 | Neutron-excess / asymmetry controls. |
| `TASK-0232` | 2 | Isotope-chain controls. |
| `TASK-0236` | 2 | Minimal-complexity controls. |

The registry is now balanced between one early broad wave, selected factory
waves, and smaller manual control lanes. The next registry expansion should be
curated; raw prediction multiplication would make reveal interpretation harder.

## Transform-Class Coverage

| Transform class | Entries |
| --- | ---: |
| Manual pairing or odd-even control | 13 |
| Feature-term selected registry | 12 |
| Factory coefficient-transform selected registry | 10 |
| Baseline or unspecified control | 8 |
| Smooth or reference control | 7 |
| Manual neutron-excess or asymmetry control | 2 |
| Manual shell or magic control | 2 |

Interpretation:

- feature-term coverage is now present but concentrated in the selected
  slate-002 wave;
- coefficient-transform controls remain represented through the selected
  slate-001 wave;
- manual shell and neutron-excess lanes are thin as standalone lanes, but
  their themes are now partly represented by feature-term entries;
- pairing/odd-even controls are relatively broad because early waves included
  odd-even stress rows and later selected pairing controls.

## Target-Batch Pressure

Most-used target batches:

| Target batch | Entries | Audit note |
| --- | ---: | --- |
| `frontier-next-row` | 14 | Overrepresented; useful for contrast, but future additions should avoid reflexively adding more frontier rows. |
| `heavy-extension-row` | 4 | Covered through first-wave rows. |
| `n50-forward-row` | 4 | Covered through first-wave rows. |
| `n82-neighborhood-row` | 4 | Covered through first-wave rows. |
| `neutron-rich-stress` | 4 | Covered through selected feature-term wave. |
| `nickel-isotope-chain` | 4 | Covered through selected feature-term wave. |
| `odd-even-stress-row` | 4 | Covered through first-wave rows. |
| `shell-magic-probe` | 4 | Covered through selected feature-term wave. |

The main target-pressure concern is not the existence of repeats; sign-paired
and model-paired controls need repeated rows. The concern is that `frontier-next-row`
dominates the registry and should not be the default target for future waves.

## Domain Coverage

| Domain | Entries | Audit note |
| --- | ---: | --- |
| Neutron-rich / asymmetry | 23 | Broadest coverage, combining frontier, manual neutron-excess controls, and selected feature terms. |
| Frontier | 18 | Strongly represented, partly because `frontier-next-row` appears in many waves. |
| Odd-even / pairing | 18 | Well represented through first-wave and pairing-control entries. |
| Shell / magic | 16 | Represented by N=50/N=82 rows, manual shell controls, and selected shell feature terms. |
| Isotope-chain | 6 | Covered, but still relatively small. |
| Mid-mass | 1 | Thin; only `PRED-0043` directly covers this domain in the committed registry. |

Coverage gaps and planning implications:

- mid-mass registry coverage is thin and lacks selected feature-term entries;
- isotope-chain coverage is present but should remain visible as a distinct
  reveal slice rather than being pooled into frontier behavior;
- future scout tasks should avoid adding new frozen registry entries until the
  synthetic reveal dry-run and this audit are reviewed.

## Repeated Nuclides

Highest target repeats:

| Nuclide | Entries | Target batches |
| --- | ---: | --- |
| `Ni-76` | 18 | `frontier-next-row`, `nickel-isotope-chain` |
| `Ca-55` | 14 | `frontier-next-row` |
| `Ga-85` | 14 | `frontier-next-row` |
| `Zn-80` | 14 | `frontier-next-row` |
| `Ni-82` | 10 | `neutron-excess-control-probe`, `neutron-rich-stress`, `nickel-isotope-chain` |
| `Co-81` | 6 | `neutron-excess-control-probe`, `neutron-rich-stress` |
| `Cu-79` | 6 | `shell-magic-control-probe`, `shell-magic-probe` |
| `Kr-86` | 6 | `shell-magic-control-probe`, `shell-magic-probe` |
| `Mg-40` | 6 | `neutron-excess-control-probe`, `neutron-rich-stress` |
| `Na-39` | 6 | `neutron-excess-control-probe`, `neutron-rich-stress` |
| `Te-134` | 6 | `shell-magic-control-probe`, `shell-magic-probe` |
| `Xe-138` | 6 | `shell-magic-control-probe`, `shell-magic-probe` |

Review interpretation:

- high-repeat rows are expected for sign-paired and family-paired controls;
- `Ni-76`, `Ca-55`, `Ga-85`, and `Zn-80` should get extra no-peek/source-state
  attention in any future reveal because they carry many model comparisons;
- repeated shell and neutron-rich rows are useful for contrast but should not
  be mistaken for independent target breadth.

## Reveal-Readiness Flags

The machine summary marks entries with review flags such as:

- `manual_lane_source_review`
- `near_null_or_ablation_control`
- `high_reuse_target_batch`
- `high_reuse_target_nuclide`
- `feature_term_selected_wave`

These are audit flags, not failures.

Entries from older manual lanes should receive source-state and no-peek review
care because their wording and selection context predate the current reveal
protocol. Entries from the selected factory waves are more uniform, but their
target-batch repetition still matters for partial-reveal interpretation.

## Recommended Next Step

Proceed to `TASK-0273` before adding new frozen predictions. A synthetic reveal
dry-run harness can exercise:

- registry snapshot handling;
- partial reveal coverage;
- ineligible-row exclusion reasons;
- repeated-target reporting;
- no mutation of frozen prediction entries;
- conservative wording for negative or inconclusive synthetic outcomes.

The scout tasks `TASK-0278`, `TASK-0279`, and `TASK-0280` can run after or in
parallel only if they remain sandbox-only and do not write new `PRED-*`
entries.

## Verdict

`REVIEW_READY` for maintainer review as a registry coverage audit.

No scientific success verdict is assigned. This audit provides planning and
review-risk context for future reveal tooling and sandbox scout work only.
