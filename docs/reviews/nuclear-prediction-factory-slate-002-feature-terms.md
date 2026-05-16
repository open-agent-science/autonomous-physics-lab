# Nuclear Prediction Factory Slate-002 Feature-Term Review

**Task:** TASK-0264
**Factory config:** `examples/nuclear_prediction_factory_slate_002_feature_terms.yaml`
**Ranking report:** `docs/reviews/nuclear-prediction-factory-slate-002-feature-terms-ranking.md`
**Factory id:** `nuclear-prediction-factory-slate-002-feature-terms`
**Baseline model:** `RESULT-0015::model_fitted_semi_empirical`
**Source commit:** `6bf1ed737c4b51aac87582164ded5a668b233861`
**Live external fetch allowed:** `false`
**Candidate count:** 48

Slate-002 is a sandbox review surface for feature-term variants. It produces no
claims, no canonical results, no knowledge entries, and no committed registry
predictions. Draft PRED-style YAML was generated only under `/tmp` for
reproduction checks.

## Scope

This slate is the first factory wave after feature-term support and the
reusable target-batch library landed. It intentionally exercises:

- `shell_proximity_gaussian` terms on proton and neutron axes;
- `asymmetry_polynomial` terms, including sign-symmetric and damped quartic
  controls;
- `asymmetric_neutron_excess` terms, including near-null and sign-symmetric
  controls;
- combined coefficient-plus-feature variants.

The slate keeps the generation-before-registration split: `PRED-9401` through
`PRED-9448` are sandbox ids only. A later TASK-0265-style PR may select a small
subset for the canonical registry after maintainer review.

## Target-Batch Coverage

The config reuses `data/nuclear_masses/factory_target_batches.yaml` and does
not copy ad hoc target lists.

| Target batch | Candidates | Review role |
| --- | ---: | --- |
| `shell-magic-probe` | 12 | Shell and magic-number proximity behavior near N=50/N=82 targets. |
| `neutron-rich-stress` | 12 | High neutron-excess asymmetry and neutron-excess stress behavior. |
| `nickel-isotope-chain` | 12 | Fixed-Z isotope-chain behavior across N=48, 50, 52, 54. |
| `mid-mass-region-probe` | 12 | Cross-region transfer behavior away from the explicit shell-focused batch. |

The ranker raised `REDUNDANT_TARGET_BATCH` for all four batches because each
has 12 candidates. This is expected for slate-002: the design intentionally
creates matched within-batch control families rather than a broad one-candidate
per-batch sweep.

## Candidate Diversity

Feature-term usage in the 48-candidate slate:

| Feature family | Candidate appearances |
| --- | ---: |
| `shell_proximity_gaussian` | 29 |
| `asymmetry_polynomial` | 13 |
| `asymmetric_neutron_excess` | 12 |

Some combined variants include more than one feature family, so appearances
sum above the candidate count. Coefficient-plus-feature composition appears in
`PRED-9411`, `PRED-9412`, `PRED-9424`, `PRED-9436`, `PRED-9447`, and
`PRED-9448`.

The ranking helper detected no duplicate prediction ids and no near-duplicate
value vectors at the 1e-4 MeV threshold.

## Sensitivity Review

Largest absolute deltas from baseline:

| Variant | Batch | max abs delta MeV | Review interpretation |
| --- | --- | ---: | --- |
| `asymmetry-quartic-only-minus-neutron-rich` | `neutron-rich-stress` | 64.182 | Extreme sensitivity diagnostic; not a default registry candidate. |
| `asymmetry-quartic-only-plus-neutron-rich` | `neutron-rich-stress` | 64.182 | Extreme sensitivity diagnostic; sign counterpart. |
| `asymmetry-quartic-plus-coefficient-scale-neutron-rich` | `neutron-rich-stress` | 49.360 | Extreme combined diagnostic; defer by default. |
| `asymmetry-quartic-reviewed-neutron-rich` | `neutron-rich-stress` | 48.476 | Reviewed coefficient set but too large for default registry selection without explicit approval. |
| `asymmetry-quartic-sign-inverted-neutron-rich` | `neutron-rich-stress` | 48.476 | Sign counterpart; defer by default. |
| `asymmetry-quadratic-plus-neutron-rich` | `neutron-rich-stress` | 15.706 | Large quadratic-only stress; defer by default. |
| `asymmetry-quadratic-minus-neutron-rich` | `neutron-rich-stress` | 15.706 | Sign counterpart; defer by default. |
| `asymmetric-neutron-excess-cubic-plus-neutron-rich` | `neutron-rich-stress` | 4.860 | Bounded nonlinear stress below the ranker extreme threshold. |
| `asymmetric-neutron-excess-cubic-minus-neutron-rich` | `neutron-rich-stress` | 4.860 | Sign counterpart below the ranker extreme threshold. |
| `shell-zn-reviewed-coefficients-shell-magic` | `shell-magic-probe` | 3.208 | Bounded shell/magic control with visible but non-extreme deltas. |
| `shell-zn-sign-inverted-shell-magic` | `shell-magic-probe` | 3.208 | Sign counterpart. |

Near-zero and null controls:

- `shell-zn-near-null-shell-magic` produced all-zero rounded deltas.
- `asymmetric-neutron-excess-near-null-neutron-rich` produced all-zero rounded
  deltas.
- `asymmetric-neutron-excess-near-null-nickel-chain` produced all-zero rounded
  deltas.
- The mid-mass neutron-axis shell controls are effectively dormant on the
  chosen mid-mass targets, with max delta around 0.000538 MeV.

These are preserved negative/sanity results. They do not invalidate the slate;
they show which feature terms are dormant or negligible on particular target
batches.

## Leakage Review

- `source_state.live_external_fetch_allowed` is `false`.
- The generator reads committed `RESULT-0015` coefficients and the committed
  reusable target-batch library.
- Draft PRED-style YAML was written to
  `/tmp/apl-nuclear-factory-slate-002-feature-terms`.
- The committed PR includes the config and review/ranking docs only, not the
  generated draft PRED YAML files.
- No future or live measurement source was fetched.
- No comparison against later measurements, holdout rows, or future source
  manifests was performed.

## Recommended Candidates For Later Registry Review

These are review suggestions only, not selected predictions and not validation
claims. A later registry PR should still choose a smaller subset and preserve
frozen values, target batches, no-peek rules, and reveal boundaries.

Good candidates for a first feature-term registry subset:

- `PRED-9401` / `PRED-9402`: reviewed Z+N shell proximity and sign counterpart
  on `shell-magic-probe`.
- `PRED-9403` / `PRED-9404`: neutron-axis shell proximity and sign counterpart
  on `shell-magic-probe`.
- `PRED-9420` / `PRED-9421`: bounded asymmetric neutron-excess quadratic pair
  on `neutron-rich-stress`.
- `PRED-9422` / `PRED-9423`: bounded asymmetric neutron-excess cubic pair just
  below the extreme-sensitivity threshold.
- `PRED-9425` / `PRED-9426`: neutron-axis shell pair on `nickel-isotope-chain`.
- `PRED-9429` / `PRED-9430`: neutron-excess pair on `nickel-isotope-chain`.
- `PRED-9441` / `PRED-9442`: low-amplitude neutron-excess pair on
  `mid-mass-region-probe`.
- `PRED-9443` / `PRED-9444`: mild quadratic asymmetry pair on
  `mid-mass-region-probe`.

Defer by default:

- `PRED-9413` through `PRED-9418` and `PRED-9424`, because the neutron-rich
  asymmetry-polynomial deltas are extreme under the ranker threshold.
- Near-null/all-zero controls unless the maintainer wants explicit null
  registry entries.
- Mid-mass neutron-axis shell controls if selection is meant to prioritize
  visible feature-term effects rather than dormancy checks.

## Reproduction Commands

```bash
python3 scripts/generate_nuclear_prediction_variants.py \
  examples/nuclear_prediction_factory_slate_002_feature_terms.yaml \
  --write-drafts \
  --output-dir /tmp/apl-nuclear-factory-slate-002-feature-terms

python3 scripts/generate_nuclear_prediction_variants.py \
  examples/nuclear_prediction_factory_slate_002_feature_terms.yaml \
  --summary-out /tmp/apl-nuclear-factory-slate-002-feature-terms.yaml

python3 scripts/rank_nuclear_prediction_variant_slate.py \
  /tmp/apl-nuclear-factory-slate-002-feature-terms.yaml \
  --out /tmp/apl-nuclear-factory-slate-002-feature-terms-ranking.md
```

The generated slate is deterministic for the committed config and source
commit. Re-running the commands should reproduce 48 candidates, four balanced
target batches, no duplicate ids, no near-duplicate value vectors, and the same
expected heuristic flags.

## Limitations

- Single baseline: all candidates inherit from RESULT-0015 fitted SEMF.
- No predictive scoring: ranking is pre-reveal triage only.
- Some asymmetry-polynomial controls are intentionally extreme and should be
  treated as stress diagnostics.
- Some near-null and mid-mass shell controls are effectively dormant on their
  target batches.
- The slate does not establish whether any feature term is physically valid or
  predictively useful.

## Verdict

`REVIEW_READY` as a sandbox feature-term slate. No scientific success verdict is
assigned before a separate maintainer-reviewed reveal/comparison task.
