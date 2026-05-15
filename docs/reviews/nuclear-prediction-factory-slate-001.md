# Nuclear Prediction Factory Slate-001 Review

**Task:** TASK-0250  
**Factory config:** `examples/nuclear_prediction_factory_slate_001.yaml`  
**Factory id:** `nuclear-prediction-factory-slate-001`  
**Baseline model:** `RESULT-0015::model_fitted_semi_empirical`
(coefficients sourced from `results/EXP-0012/RUN-0001/result.yaml`)  
**Source commit:** `9025ae2266b97b8173b4b8c904f9f7f4e4e810bb`  
**Live external fetch allowed:** `false`  
**Candidate count:** 36 (within the TASK-0250 30–80 bound)  
**Draft PRED YAML:** written to `/tmp/apl-nuclear-factory-slate-001/` for review only;
no draft files are committed to the registry.

> Slate-001 is a sandbox review surface. It produces no claims, no results, no
> knowledge entries, and no canonical PRED registrations. Candidate values are
> deterministic point estimates from bounded coefficient transforms applied to
> the RESULT-0015 fitted semi-empirical baseline. No comparison against future
> or holdout measurements is made or implied.

## 1. Slate Scope

Slate-001 is the first coefficient-transform-only factory run. Per the
TASK-0250 task note and `docs/notes/nuclear-prediction-variant-factory.md`,
feature-term variants (shell, magic, neutron-excess) are deferred to TASK-0252;
any candidate selected from slate-001 should be treated as **provisional**
until feature-term coverage is reviewed in a later slate.

Allowed transform families in slate-001 (all currently supported by
`physics_lab/engines/nuclear_prediction_variants.py`):

- `blend_with_reference` — interpolation toward repository reference SEMF
  coefficients;
- `scale` — multiplicative perturbation of one coefficient;
- `delta` — bounded additive perturbation of one coefficient;
- `set` — explicit coefficient assignment, including pairing ablation.

## 2. Target Batch Coverage

| Target batch | Nuclides | Notes |
| --- | --- | --- |
| `frontier-next-row` | Ca-55, Ni-76, Zn-80, Ga-85 | Neutron-rich frontier; not in NMD-0002 measured slice. |
| `odd-even-probe` | Co-59, Ni-60, Cu-64 | Mixed pairing classes (odd-A, even-even, odd-A). |
| `light-region-controls` | C-12, Mg-24, Si-28, S-32 | Light even-even doubly-aligned; sensitive to surface and pairing. |
| `neutron-rich-N50` | Ni-78, Cu-79, Sr-92, Kr-94 | N≈50 region including doubly-magic Ni-78. |
| `mid-mass-stable` | Cu-63, Zn-66, Ge-72, Se-78 | Well-constrained mid-mass anchors. |

None of the slate target nuclides appear in
`data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`, and a manual sweep
against `data/nuclear_masses/post_ame2020_holdout.yaml` did not surface
overlaps. Slate-001 does not commit any of these nuclides as registered
predictions, so the holdout overlap rule from
`docs/notes/nuclear-prediction-variant-expansion-wave.md` is not directly
binding here, but the target picks were chosen to remain forward-compatible
with a future selected-registry pass.

### Candidates per batch

| Batch | Candidates |
| --- | --- |
| `frontier-next-row` | 18 |
| `odd-even-probe` | 6 |
| `light-region-controls` | 5 |
| `neutron-rich-N50` | 5 |
| `mid-mass-stable` | 2 |

The frontier batch is intentionally over-weighted because most coefficient
transforms (volume, surface, Coulomb, asymmetry) have their largest absolute
deltas on heavy neutron-rich targets, and that is where the agent attention
during selection should focus. The ranker flagged this concentration as
`REDUNDANT_TARGET_BATCH`; the rationale above is the answer.

## 3. Model Diversity

All 36 candidates share the single model-family prefix
`RESULT-0015::model_fitted_semi_empirical::<variant_id>` (or
`RESULT-0015::model_fitted_reference_blend_*` for blend variants). This is
expected: slate-001 is a coefficient-transform-only slate. Feature-term
diversity (shell, magic, neutron-excess) will appear only after TASK-0252.

Per-transform-family counts:

| Transform family | Count | Examples |
| --- | --- | --- |
| `blend_with_reference` | 7 | 9101–9104, 9124, 9129, 9134 |
| `scale` (single coefficient ±) | 18 | volume, surface, Coulomb, asymmetry, pairing |
| `delta` (additive ±) | 2 | asymmetry ±0.5 MeV on N=50 batch |
| `set` (ablation / explicit) | 4 | pairing zero on 3 batches, pairing→12.0 |
| `blend_with_reference` = 1.0 (full reference swap) | 2 | mid-mass + frontier |
| Cross-batch pairing sanity | 1 | pairing-zero-ablation-frontier |

## 4. Coefficient Sensitivity Summary

The factory ranking helper sorted candidates by `max_abs_delta_mev`. Top
findings (largest absolute deltas first):

| Rank | Variant | Batch | max Δ (MeV) | mean Δ (MeV) |
| --- | --- | --- | --- | --- |
| 1 | `volume-scale-plus-1pct-frontier` | frontier-next-row | 13.187 | 11.481 |
| 1 (mirror) | `volume-scale-minus-1pct-frontier` | frontier-next-row | 13.187 | 11.481 |
| 3 | `surface-scale-plus-3pct-frontier` | frontier-next-row | 10.029 | 9.118 |
| 3 (mirror) | `surface-scale-minus-3pct-frontier` | frontier-next-row | 10.029 | 9.118 |
| 5 | `volume-scale-plus-0p5pct-frontier` | frontier-next-row | 6.594 | 5.740 |
| 7 | `pairing-zero-ablation-light` | light-region-controls | 4.616 | 3.432 |
| 8 | `coulomb-scale-plus-2pct-neutron-rich-N50` | neutron-rich-N50 | 4.284 | 3.283 |
| 10 | `surface-scale-plus-2pct-light` | light-region-controls | 3.486 | 2.841 |
| 12 | `full-reference-coefficients-mid-mass` | mid-mass-stable | 3.358 | 2.990 |
| 15 | `full-reference-coefficients-frontier` | frontier-next-row | 3.311 | 2.022 |
| 16 | `asymmetry-delta-plus-0p5-neutron-rich-N50` | neutron-rich-N50 | 3.103 | 2.465 |

Smaller-end controls (smooth blends, bounded pairing scale on odd-even-probe):

| Variant | max Δ (MeV) | mean Δ (MeV) |
| --- | --- | --- |
| `blend-with-reference-10-frontier` | 0.331 | 0.202 |
| `blend-with-reference-25-frontier` | 0.828 | 0.506 |
| `pairing-scale-plus-5pct-odd-even` | 0.103 | 0.068 |
| `pairing-scale-plus-5pct-light` | 0.231 | 0.172 |
| `pairing-set-to-reference-odd-even` | 0.515 | 0.338 |

The `50/50` blend example at the frontier batch produces the following
coefficient set (verified deterministically against `RESULT-0015` +
`REFERENCE_SEMI_EMPIRICAL_COEFFICIENTS`):

| coefficient | fitted (RESULT-0015) | reference | blend 0.50 | Δ from fitted |
| --- | --- | --- | --- | --- |
| volume | 15.51424 | 15.80 | 15.65712 | +0.14288 |
| surface | 17.29318 | 18.30 | 17.79659 | +0.50341 |
| coulomb | 0.68782 | 0.714 | 0.70091 | +0.01309 |
| asymmetry | 23.84656 | 23.20 | 23.52328 | −0.32328 |
| pairing | 15.99085 | 12.00 | 13.99542 | −1.99543 |

Pairing has the largest fitted-vs-reference gap (≈4 MeV per pair); this is
visible in the large `pairing-zero-ablation-light` delta because the light
even-even batch is uniformly pair-affected.

## 5. Duplicate / Redundancy Analysis

- **Duplicate prediction_ids:** none detected by the ranker. PRED-9101..PRED-9136 are unique.
- **Near-duplicate value vectors (threshold 1e-4 MeV):** none.
- **Cross-batch sanity:** `pairing-zero-ablation-frontier` (PRED-9123) does
  not trip `ALL_ZERO_DELTA` because Ni-76 and Zn-80 are even-even and the
  pairing-zero transform alters their mass-excess. Ca-55 and Ga-85 are
  odd-N / odd-Z respectively, so their pairing contribution was already zero
  and the transform is a no-op for them.

## 6. Heuristic Flags

The ranker raised 10 advisory flags. All are explainable and do not block
further review of the slate; they do indicate where pre-registration scrutiny
should concentrate.

### EXTREME_SENSITIVITY (6 flags)

All six are volume- or surface-coefficient perturbations on the heavy frontier
batch. The magnitudes are expected: the SEMF volume term scales as
`a_V * A`, so a 1 percent perturbation of `a_V ≈ 15.5 MeV` on A≈80 nucleons
yields ≈12 MeV per nucleus before sign cancellation with other terms. The
ranker correctly surfaces these as candidates that need plausibility review
before any registry selection:

- `volume-scale-plus-1pct-frontier`, `volume-scale-minus-1pct-frontier` (±13.2 MeV)
- `volume-scale-plus-0p5pct-frontier`, `volume-scale-minus-0p5pct-frontier` (±6.6 MeV)
- `surface-scale-plus-3pct-frontier`, `surface-scale-minus-3pct-frontier` (±10.0 MeV)

Recommendation: keep these as sensitivity-only diagnostics. They should not
be selected for `PRED-XXXX` registry promotion in TASK-0251 unless the
maintainer specifically approves stress-test variants with that magnitude.

### REDUNDANT_TARGET_BATCH (4 flags)

The ranker flags any batch with ≥3 candidates. All four batches here have
3+ candidates, so this is an information-only flag rather than a defect:

- `frontier-next-row` (18 candidates) — chosen as the primary sensitivity stage;
- `odd-even-probe` (6 candidates) — chosen for pairing-class diversity;
- `light-region-controls` (5 candidates) — chosen for low-A surface/pairing leverage;
- `neutron-rich-N50` (5 candidates) — chosen for isospin and Coulomb gradient.

Recommendation: leave the threshold-based flag as-is for slate-001. Future
slates may want to enrich the `mid-mass-stable` batch (currently 2 candidates)
when more variant families are available.

### Other flag categories — none raised

- `ALL_ZERO_DELTA`: not raised (every variant has at least one nuclide with non-zero delta).
- `MISSING_REVIEW_NOTES`: not raised (every variant carries at least one review note).
- `DUPLICATE_PREDICTION_ID`: not raised.
- `NEAR_DUPLICATE_VECTOR`: not raised at the 1e-4 MeV threshold.

## 7. Leakage Review

- `source_state.live_external_fetch_allowed` is `false` in the slate config.
- Slate-001 reads only `results/EXP-0012/RUN-0001/result.yaml` for coefficients
  and `physics_lab/engines/nuclear_mass_baselines.REFERENCE_SEMI_EMPIRICAL_COEFFICIENTS`
  for the blend reference; both are committed repository state.
- All draft PRED YAML output is written to `/tmp/apl-nuclear-factory-slate-001/`
  (explicit scratch directory) and is **not committed** by this PR.
- Slate target nuclides do not appear in the committed measured slice
  `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`, and overlap with
  `data/nuclear_masses/post_ame2020_holdout.yaml` was checked for the chosen
  identifiers.
- The factory engine's hard-coded refusal to write into
  `prediction_registry/nuclear_masses/` without `allow_prediction_registry_output: true`
  was not invoked; the slate's `draft_prediction_dir` is in `/tmp/`.

## 8. Recommended Candidates for Later Registry Review

These suggestions are guidance only. The selected subset for TASK-0251 (or a
successor) must still go through maintainer review, must remain `PRED-XXXX`
in the normal registry range (not the `PRED-9xxx` sandbox range used here),
and is contingent on feature-term coverage from TASK-0252 if breadth beyond
coefficient transforms is desired.

**Smooth-control anchors (lowest sensitivity, broadest review utility):**

- `blend-with-reference-10-frontier` (PRED-9101) — small smooth interpolation; minimal sensitivity floor.
- `blend-with-reference-50-frontier` (PRED-9103) — natural midpoint between fitted and reference SEMF.
- `blend-with-reference-50-mid-mass-stable` (PRED-9134) — smooth-control anchor in the well-constrained region.

**Bounded sensitivity controls (informative without extreme deltas):**

- `pairing-scale-plus-5pct-odd-even` (PRED-9117) / `pairing-scale-minus-5pct-odd-even` (PRED-9118) — small, sign-symmetric pairing pair.
- `pairing-zero-ablation-odd-even` (PRED-9121) — pairing ablation on a mixed-class batch.
- `coulomb-scale-plus-1pct-frontier` (PRED-9113) / `coulomb-scale-minus-1pct-frontier` (PRED-9114) — bounded Coulomb pair on heavy targets.
- `asymmetry-scale-plus-1pct-frontier` (PRED-9115) / `asymmetry-scale-minus-1pct-frontier` (PRED-9116) — bounded asymmetry pair on neutron-rich frontier.

**Cross-region reference-swap controls:**

- `full-reference-coefficients-mid-mass` (PRED-9135) — full SEMF-reference swap on a well-constrained batch; useful as a known-fixed-point control.
- `full-reference-coefficients-frontier` (PRED-9136) — same swap on the frontier batch for cross-region comparison with PRED-9135.

**Defer (`EXTREME_SENSITIVITY` flagged):**

- Volume ±0.5%/±1% on frontier-next-row (PRED-9105..PRED-9108).
- Surface ±3% on frontier-next-row (PRED-9111, PRED-9112).

These can be useful diagnostics in a future stress-test slate, but their
magnitudes exceed the 5 MeV plausibility threshold and they are not suitable
for default registry inclusion without explicit maintainer approval.

## 9. Limitations

- **Coefficient-transform-only:** slate-001 does not yet exercise shell,
  magic-number, or neutron-excess feature terms. Selection for registry
  promotion should wait for TASK-0252 coverage to avoid baking in a
  coefficient-only bias.
- **Mid-mass-stable thin coverage:** only two candidates target this batch.
  A future slate should add more transform diversity in the well-constrained
  region as a contrast surface.
- **Single source baseline:** all candidates inherit from RESULT-0015. The
  factory engine does not yet support multi-baseline ensembles.
- **No predictive scoring:** the ranking report intentionally does not assign
  predictive-value scores. Selection is pre-reveal triage, not validation.
- **Sandbox-only:** all `PRED-9xxx` ids in slate-001 are sandbox identifiers
  and should never be promoted, copied verbatim into the registry, or cited
  as registered predictions.
- **No reveal comparison:** slate-001 does not compare against future or
  holdout measurements and does not establish any predictive claim.

## 10. Reproduction Commands

```bash
python3 scripts/generate_nuclear_prediction_variants.py \
  examples/nuclear_prediction_factory_slate_001.yaml \
  --write-drafts \
  --output-dir /tmp/apl-nuclear-factory-slate-001

python3 scripts/generate_nuclear_prediction_variants.py \
  examples/nuclear_prediction_factory_slate_001.yaml \
  --summary-out /tmp/apl-nuclear-factory-slate-001.yaml

python3 scripts/rank_nuclear_prediction_variant_slate.py \
  /tmp/apl-nuclear-factory-slate-001.yaml \
  --out /tmp/apl-nuclear-factory-slate-001-ranking.md
```

The factory output and ranking report are byte-for-byte deterministic for a
given source commit and config; rerunning the commands above should reproduce
the same 36 candidates, the same delta-sensitivity ordering, and the same set
of 10 advisory flags.

---

*Slate-001 is a sandbox review surface. No claim, canonical result, or
accepted knowledge is promoted by this review.*
