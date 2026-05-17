# Nuclear Prediction Factory Feature-Term Selected Registry Wave 001

**Task:** TASK-0265
**Selection source:** `docs/reviews/nuclear-prediction-factory-slate-002-feature-terms.md`
**Factory config:** `examples/nuclear_prediction_factory_slate_002_feature_terms.yaml`
**Frozen source commit:** `3f64aa258da42d62b383395ec8c5dc10d05a3082`
**Registry entries:** `PRED-0051` through `PRED-0062`
**Live external fetch allowed:** `false`

This review note registers a maintainer-approved subset of the TASK-0264 feature-term slate. It does not reveal, score, validate, or promote any prediction. All entries remain prospective registry records only.

## Selection Method

The selected set keeps paired controls so later reveal work can compare sign direction without rewriting pre-reveal assumptions. It prioritizes visible but bounded feature-term behavior from the slate review and excludes extreme-sensitivity and near-null candidates by default.

| Registry id | Source sandbox id | Variant | Target batch | Max abs correction MeV | Selection rationale |
| --- | --- | --- | --- | ---: | --- |
| `PRED-0051` | `PRED-9401` | `shell-zn-reviewed-coefficients-shell-magic` | `shell-magic-probe` | 3.207681 | Reviewed Z+N shell proximity control on the shell/magic batch. |
| `PRED-0052` | `PRED-9402` | `shell-zn-sign-inverted-shell-magic` | `shell-magic-probe` | 3.207681 | Sign-inverted Z+N shell proximity counterpart for paired pre-reveal contrast. |
| `PRED-0053` | `PRED-9403` | `shell-n-reviewed-coefficient-shell-magic` | `shell-magic-probe` | 1.604907 | Reviewed neutron-axis shell proximity control on the shell/magic batch. |
| `PRED-0054` | `PRED-9404` | `shell-n-sign-inverted-shell-magic` | `shell-magic-probe` | 1.604907 | Sign-inverted neutron-axis shell proximity counterpart. |
| `PRED-0055` | `PRED-9420` | `asymmetric-neutron-excess-plus-neutron-rich` | `neutron-rich-stress` | 0.900000 | Bounded asymmetric neutron-excess plus control on neutron-rich targets. |
| `PRED-0056` | `PRED-9421` | `asymmetric-neutron-excess-minus-neutron-rich` | `neutron-rich-stress` | 0.900000 | Sign-symmetric asymmetric neutron-excess minus counterpart. |
| `PRED-0057` | `PRED-9422` | `asymmetric-neutron-excess-cubic-plus-neutron-rich` | `neutron-rich-stress` | 4.860000 | Cubic asymmetric neutron-excess plus stress below the extreme-sensitivity threshold. |
| `PRED-0058` | `PRED-9423` | `asymmetric-neutron-excess-cubic-minus-neutron-rich` | `neutron-rich-stress` | 4.860000 | Sign-symmetric cubic asymmetric neutron-excess counterpart. |
| `PRED-0059` | `PRED-9425` | `shell-n-reviewed-nickel-chain` | `nickel-isotope-chain` | 1.604907 | Reviewed neutron-axis shell control on the nickel isotope-chain batch. |
| `PRED-0060` | `PRED-9426` | `shell-n-sign-inverted-nickel-chain` | `nickel-isotope-chain` | 1.604907 | Sign-inverted neutron-axis shell counterpart on the nickel isotope chain. |
| `PRED-0061` | `PRED-9429` | `asymmetric-neutron-excess-plus-nickel-chain` | `nickel-isotope-chain` | 0.824390 | Bounded asymmetric neutron-excess plus control on the nickel isotope chain. |
| `PRED-0062` | `PRED-9430` | `asymmetric-neutron-excess-minus-nickel-chain` | `nickel-isotope-chain` | 0.824390 | Sign-symmetric asymmetric neutron-excess minus counterpart on the nickel isotope chain. |

## Deferred Candidates And Negative Selection

Deferred by default:

- `PRED-9413` through `PRED-9418` and `PRED-9424`: neutron-rich asymmetry-polynomial candidates flagged as extreme-sensitivity diagnostics in the slate review.
- `PRED-9419`, `PRED-9427`, and `PRED-9439`: near-null or all-zero controls, useful as sanity checks but not selected for this first feature-term registry wave.
- `PRED-9441` through `PRED-9444`: mid-mass neutron-excess/asymmetry candidates left for a possible later cross-region wave to keep this registry batch focused on shell/magic, neutron-rich, and nickel-chain feature-term behavior.
- `PRED-9445` through `PRED-9448`: dormant or coefficient-composed mid-mass controls, deferred until a separate review asks for them explicitly.

These deferrals are selection boundaries, not evidence against the models. They keep the first feature-term registry wave narrow and reviewable.

## Reproducibility And Guardrails

The selected entries were regenerated from slate-002 factory output and remapped from sandbox ids to canonical registry ids. The frozen `source_state.git_commit` is the post-merge repository state that contains TASK-0264, TASK-0266, and the TASK-0265 unblock.

Reproduction commands:

```bash
python3 scripts/generate_nuclear_prediction_variants.py \
  examples/nuclear_prediction_factory_slate_002_feature_terms.yaml \
  --write-drafts \
  --output-dir /tmp/apl-task0265-slate002-drafts \
  --summary-out /tmp/apl-task0265-slate002-summary.yaml

python3 -m pytest tests/test_nuclear_mass_prediction_registry.py
```

Validation expectations:

- Each registry entry validates against `physics_lab/schemas/nuclear_mass_prediction.schema.json`.
- `source_state.live_external_fetch_allowed` remains `false`.
- Target nuclides remain absent from committed measured and post-AME2020 holdout datasets.
- Deterministic recomputation from slate-002 reproduces every frozen `mass_excess_mev` value.
- Feature-term metadata remains traceable through the model id and frozen parameters note.
- Later comparison requires a separate maintainer-reviewed reveal task.

## Limitations

- The selected wave is feature-term factory registration only.
- The entries are point estimates with `uncertainty_mev: null`; no statistical interval or confidence ranking is claimed.
- The source slate is a single-baseline RESULT-0015 SEMF feature-term variant surface.
- No future or live measurement source was fetched during registration.
- Registration does not create a scientific result, claim, or knowledge entry.

## Verdict

`REVIEW_READY` for maintainer review as a prospective feature-term registry selection. No scientific validation verdict is assigned pre-reveal.
