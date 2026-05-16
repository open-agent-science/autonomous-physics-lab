# Nuclear Prediction Factory Selected Registry Wave 001

**Task:** TASK-0251
**Selection source:** `docs/reviews/nuclear-prediction-factory-slate-001.md`
**Factory config:** `examples/nuclear_prediction_factory_slate_001.yaml`
**Frozen source commit:** `7c315dfcebe5c062f9fc9f1a1817390c0bcfaa7c`
**Registry entries:** `PRED-0041` through `PRED-0050`
**Live external fetch allowed:** `false`

This review note registers a selected subset of the reviewed TASK-0250
coefficient-transform slate. It does not reveal, score, validate, or promote
any prediction. All entries remain prospective registry records only.

## Source Slate Choice

TASK-0252 feature-term support and TASK-0254 reusable target-batch library
support had landed before this registration wave. This TASK-0251 wave
intentionally still uses the reviewed coefficient-transform slate-001 as the
immediate selection source because no refreshed feature-term slate has been
generated and reviewed yet.

That choice keeps the audit trail narrow: every registered value is
deterministically traceable to `examples/nuclear_prediction_factory_slate_001.yaml`
and the TASK-0250 review. Feature-term variants should be registered only after
a separate reviewed slate or task explicitly selects them.

## Selection Method

The selected set follows the TASK-0250 review recommendation rather than raw
factory ranking. It keeps smooth controls, sign-symmetric bounded controls,
and one pairing ablation probe while excluding extreme volume/surface
sensitivity diagnostics.

| Registry id | Source sandbox id | Variant | Target batch | Selection rationale |
| --- | --- | --- | --- | --- |
| `PRED-0041` | `PRED-9101` | `blend-with-reference-10-frontier` | `frontier-next-row` | Small smooth interpolation; low-sensitivity floor for the frontier batch. |
| `PRED-0042` | `PRED-9103` | `blend-with-reference-50-frontier` | `frontier-next-row` | Midpoint fitted/reference anchor on the frontier batch. |
| `PRED-0043` | `PRED-9134` | `blend-with-reference-50-mid-mass-stable` | `mid-mass-stable` | Same midpoint control on a cross-region mid-mass batch. |
| `PRED-0044` | `PRED-9117` | `pairing-scale-plus-5pct-odd-even` | `odd-even-probe` | Small positive pairing perturbation on mixed pairing classes. |
| `PRED-0045` | `PRED-9118` | `pairing-scale-minus-5pct-odd-even` | `odd-even-probe` | Sign-symmetric counterpart to `PRED-0044`. |
| `PRED-0046` | `PRED-9121` | `pairing-zero-ablation-odd-even` | `odd-even-probe` | Pairing ablation control on a mixed-class target batch. |
| `PRED-0047` | `PRED-9113` | `coulomb-scale-plus-1pct-frontier` | `frontier-next-row` | Bounded Coulomb perturbation on heavy neutron-rich targets. |
| `PRED-0048` | `PRED-9114` | `coulomb-scale-minus-1pct-frontier` | `frontier-next-row` | Sign-symmetric counterpart to `PRED-0047`. |
| `PRED-0049` | `PRED-9115` | `asymmetry-scale-plus-1pct-frontier` | `frontier-next-row` | Bounded asymmetry perturbation for neutron-rich frontier sensitivity. |
| `PRED-0050` | `PRED-9116` | `asymmetry-scale-minus-1pct-frontier` | `frontier-next-row` | Sign-symmetric counterpart to `PRED-0049`. |

## Deferred Candidates And Negative Selection

The following slate-001 candidates remain sandbox-only and are not registered
in this wave:

- `PRED-9105` through `PRED-9108`: volume-scale frontier variants flagged as
  extreme-sensitivity diagnostics.
- `PRED-9111` and `PRED-9112`: surface-scale ±3% frontier variants flagged as
  extreme-sensitivity diagnostics.
- `PRED-9135` and `PRED-9136`: full-reference coefficient swaps, left for a
  future cross-region control wave to keep this first registration wave at ten
  entries.
- All feature-term candidates: not applicable to slate-001 and not registered
  until a refreshed feature-term slate is generated and reviewed.

These deferrals are negative selection results, not evidence against the
models. They simply preserve the registry boundary: selected prospective
entries only, no raw dump.

## Reproducibility And Guardrails

The selected entries were regenerated from the factory output and remapped from
sandbox ids to registry ids. The frozen `source_state.git_commit` is
`7c315dfcebe5c062f9fc9f1a1817390c0bcfaa7c`, the post-merge repository state
that contained TASK-0250, TASK-0252, TASK-0254, and the TASK-0251 unblock.

Reproduction commands:

```bash
python3 scripts/generate_nuclear_prediction_variants.py \
  examples/nuclear_prediction_factory_slate_001.yaml \
  --write-drafts \
  --output-dir /tmp/apl-task-0251-slate-001-drafts \
  --summary-out /tmp/apl-task-0251-slate-001-summary.yaml

python3 -m pytest tests/test_nuclear_mass_prediction_registry.py
```

Validation expectations:

- Each registry entry validates against
  `physics_lab/schemas/nuclear_mass_prediction.schema.json`.
- `source_state.live_external_fetch_allowed` remains `false`.
- Target nuclides remain absent from committed measured and holdout datasets.
- Deterministic recomputation from `slate-001` reproduces each frozen
  `mass_excess_mev` value.
- Later comparison requires a separate maintainer-reviewed reveal task.

## Limitations

- The selected wave is coefficient-transform-only.
- The entries are point estimates with `uncertainty_mev: null`; no statistical
  interval or confidence ranking is claimed.
- The source slate is a single-baseline RESULT-0015 SEMF variant surface.
- No future or live measurement source was fetched during registration.
- Registration does not create a scientific result, claim, or knowledge entry.

## Verdict

`REVIEW_READY` for maintainer review as a prospective registry selection.
No scientific validation verdict is assigned pre-reveal.
