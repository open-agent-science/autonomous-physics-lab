# Atomic Beloy 2021 Row Readiness Re-check

**Task:** `TASK-0401`
**Predecessor:** `TASK-0371` (first-batch row curation), `TASK-0344` (covariance/uncertainty contract), `TASK-0332` (real-row readiness gate), `TASK-0372` (source-artifact version-drift stop condition)
**Campaign:** Atomic-Clock Residuals
**Source under test:** Beloy, K., et al. (BACON), arXiv:2005.14694 / Nature 591, 564 (2021)
**Re-check verdict:** `PINNED_DATASET` (sandbox-only; no benchmark; no claim)

## Scope

`TASK-0371` committed the first three direct frequency-ratio rows
(`ACR-0001-ROW-001..003`) for the Atomic-Clock Residuals campaign as a
sandbox-only first-batch seed. The task explicitly required that the
`TASK-0344` covariance/uncertainty contract and the `TASK-0332` real-row
readiness gate be re-checked before any downstream benchmark consumes
these rows.

This re-check re-runs the readiness gate against the now-committed
artifacts and classifies the campaign state per the
`TASK-0401` vocabulary:

- `SOURCE_SURFACE` — only templates, manifests, and source candidates exist.
- `PINNED_DATASET` — at least one source artifact is checksummed and at
  least one real row is committed under explicit covariance and
  version-drift rules, with no benchmark consumer yet authorised.
- `BASELINE_READY` — additionally, a deterministic real-row loader path,
  a holdout/no-peek boundary, a documented cross-row covariance policy,
  and either a second independent source or a maintainer-approved
  single-source baseline plan exist.

This document does **not** fit drift, derive constants-variation
constraints, write to the prediction registry, edit any `CLAIM`, `KNOW`,
or canonical `RESULT` artifact, or change `data/atomic_clocks/*.yaml`.

## Inputs Reviewed

| Input | Role in re-check |
| --- | --- |
| `data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml` | Committed first-batch rows under test. |
| `data/atomic_clocks/source_artifacts/2021-beloy-bacon/arxiv-2005.14694.pdf` | Committed source PDF. |
| `data/atomic_clocks/source_artifacts/2021-beloy-bacon/arxiv-2005.14694.sha256` | Sidecar checksum. |
| `data/atomic_clocks/source_artifacts/2021-beloy-bacon/provenance.yaml` | Retrieval, licence, version-of-record cross-check record. |
| `data/atomic_clocks/source_artifacts/2021-beloy-bacon/README.md` | Version-drift halt condition for this artifact. |
| `data/atomic_clocks/schema.md` | Row-class and minimum-fields schema sketch. |
| `data/atomic_clocks/source_manifest_template.yaml` | Stop conditions and source-family discipline. |
| `physics_lab/engines/atomic_clock_residuals.py` | Current loader (synthetic-only). |
| `docs/reviews/atomic-clock-real-row-readiness-gate.md` | TASK-0332 gate definition and blockers. |
| `docs/reviews/atomic-clock-covariance-uncertainty-semantics.md` | TASK-0344 required/forbidden uncertainty fields and C1–C4 stop conditions. |
| `docs/reviews/atomic-clock-beloy-2021-source-artifact-covariance-preflight.md` | TASK-0363 source-artifact + covariance preflight. |
| `docs/reviews/atomic-clock-source-artifact-version-drift-stop-condition.md` | TASK-0372 `SOURCE_ARTIFACT_VERSION_DRIFT` policy. |
| `docs/reviews/atomic-clock-beloy-2021-direct-ratio-row-curation.md` | TASK-0371 first-batch curation record. |

## Method

For each readiness dimension required by `TASK-0401`, the re-check
records the committed evidence, applies the `TASK-0344` BLOCKER rules
where they bind, and reports `PASS`, `PASS_WITH_NOTE`, or `BLOCKER`.
A `BLOCKER` row keeps the campaign below `BASELINE_READY`; a
`PASS_WITH_NOTE` does not block the current pin but constrains
downstream benchmark design.

No clock value, ratio, drift estimate, sensitivity coefficient, or
prediction-registry entry is written or modified by this re-check.

## Per-Dimension Findings

### Source artifact presence and pinning — `PASS`

- Committed PDF: `data/atomic_clocks/source_artifacts/2021-beloy-bacon/arxiv-2005.14694.pdf`.
- Recomputed SHA-256 on the committed PDF matches both the sidecar
  `arxiv-2005.14694.sha256` and the `checksum_sha256` value embedded in
  `acr-0001-beloy-2021-direct-ratios.yaml`:
  `bec1548829e7d4697ffd78dec453c00990c2937b71cc624c420a58e31ca60467`.
- Retrieval date and licence are recorded in `provenance.yaml`
  (arXiv perpetual licence, retrieval 2026-05-25). Nature paper-of-record
  PDF is intentionally **not** committed and only cited by DOI.

### Source-artifact version-drift status — `PASS`

- `provenance.yaml` records a maintainer-side local cross-check of all
  three ratio values and the figure-caption uncertainties against the
  Nature version-of-record PDF. Result: `NO_DRIFT`, with explicit
  `not_recheckable_from_committed_artifacts_alone: true`.
- This satisfies the `SOURCE_ARTIFACT_VERSION_DRIFT` stop condition
  defined by `TASK-0372` for this source family.
- Follow-up re-verification is documentation-only and does not block a
  pin.

### Row class and direct/derived separation — `PASS`

- Every committed row carries `row_class: direct_measurement`,
  `classification.direct_measurement: true`, and explicit `false` on
  `derived_constraint`, `review_summary`, and `synthetic`.
- The schema's direct/derived/review/synthetic separation
  (`data/atomic_clocks/schema.md`) is preserved.

### Ratio orientation and transition semantics — `PASS`

- Each row carries `clock_system` and `reference_system` with species,
  isotope, charge state, and transition label
  (`1S0_to_3P0` for all three clocks).
- Ratios are explicitly oriented (Al⁺/Yb, Al⁺/Sr, Yb/Sr), matching the
  Beloy 2021 paper's Table 1.

### Units and epoch semantics — `PASS`

- `observable.units = dimensionless_ratio` on all three rows.
- `observable.epoch_start = 2017-11`, `epoch_end = 2018-06` on every
  row, matching the campaign window declared in
  `campaign_window.start_yyyymm`/`end_yyyymm` and consistent with the
  paper's "November 2017 through June 2018, 17 measurement days" range.

### Uncertainty semantics — `PASS_WITH_NOTE`

Required fields from `TASK-0344` are present on every row:

| TASK-0344 required field | Mapping in `acr-0001-*` | Status |
| --- | --- | --- |
| Combined 1-σ total | `uncertainty.total` (5.9e-18 / 8.0e-18 / 6.8e-18) | PASS |
| Total unit | dimensionless ratio implicit; `total` is fractional | PASS |
| Statistical-only | `uncertainty.statistical` + `statistical_basis` | PASS |
| Systematic-only | `uncertainty.systematic` + `systematic_basis` | PASS |
| Per-component systematic | `uncertainty.systematic_components_e_minus_18` | PASS |
| Confidence-level label | `uncertainty.confidence_level_label: 1_sigma` | PASS |
| Asymmetric handling | not applicable (Bayesian-model 1-σ is symmetric in source) | N/A |
| Bound vs measurement | `uncertainty.bound_style: measurement` | PASS |
| Covariance reference | `uncertainty.covariance_reference: diagonal_per_paper_explicit_fold_in_bayesian_sec_4_5` | PASS |

**Notes (non-blocking, benchmark-design constraints):**

1. The dataset uses the field name `uncertainty.total` rather than
   `total_uncertainty` from the `TASK-0344` field list. The
   value-bearing semantics (Bayesian-model 1-σ, combined statistical
   + systematic) are present and labelled by
   `total_basis: comprehensive_bayesian_model_standard_deviation`.
   Downstream readers must map the two field names. A future schema
   freeze should standardise on one name.
2. The value-notation `value(last_digits)` on each row encodes a
   different uncertainty convention than `uncertainty.total`. For
   example, ROW-001 reports `2.162887127516663703(13)` with
   `value_uncertainty_last_digits_unit_label: 1e-18`, i.e. ±13 × 10⁻¹⁸,
   while the Bayesian-model 1-σ in `uncertainty.total` is 5.9 × 10⁻¹⁸.
   ROW-002 shows the same kind of gap (±21 × 10⁻¹⁸ vs 8.0 × 10⁻¹⁸).
   Both numbers come from the paper, but they reflect different
   combination rules (the value-notation is the paper's parenthetical
   per-row uncertainty; `uncertainty.total` is Table 1's Bayesian-model
   row). A future task should add a note in the dataset that
   `uncertainty.total` is the authoritative residual-axis 1-σ and the
   parenthetical is informational only.
3. Per-row χ²_red treatment is intentionally asymmetric across rows
   (`weighted_standard_error_with_chi2red_inflation_1_5` on ROW-001,
   `standard_error_of_mean_ignoring_chi2red_per_paper_dagger_footnote_chi2red_0_2`
   on ROW-002, `weighted_standard_error_with_chi2red_inflation_6_0` on
   ROW-003). The asymmetry is per the paper. A benchmark consumer must
   preserve this asymmetry; collapsing all three to a uniform inflation
   rule would silently misweight rows.

### Covariance and shared-systematic discipline — `PASS_WITH_NOTE`

Re-check against the `TASK-0344` stop conditions:

- **C1 (repeated campaign without separable epochs).** All three rows
  share the BACON 2018 campaign (`covariance_group: bacon_2018_campaign`,
  same 17-day epoch). The dataset represents them as a single source
  family with a documented combination rule (Branch B fold-in from
  arXiv:2005.14694 Sec. 4.5). **Satisfied.**
- **C2 (shared sensitivity coefficients).** Not applicable — no
  derived-constraint rows in this dataset.
- **C3 (direct/derived duplicate evidence).** Not applicable — no
  derived rows.
- **C4 (covariance matrix referenced but not committed).** The paper
  does not publish a 3×3 cross-ratio matrix. The dataset records this
  explicitly via `covariance_reference: diagonal_per_paper_explicit_fold_in_bayesian_sec_4_5`,
  and per-row `correlation_notes` plus the top-level
  `cross_row_shared_clock_systematics_note` make the shared-clock
  cross-row coupling visible. **Satisfied for the diagonal axis.**

**Note (non-blocking for the pin):**

- The Branch B fold-in commits each row's `total` as the Bayesian-model
  1-σ that already absorbs within-row shared systematics. It does not
  publish a 3×3 cross-ratio covariance matrix. Any downstream benchmark
  combining two or more rows must therefore either reconstruct an
  approximate cross-ratio covariance from the per-clock columns
  (the explicit purpose of `TASK-0402`) or document that cross-ratio
  correlations are ignored. The dataset already exposes the per-clock
  decomposition for both paths.

### Schema validity — `PASS_WITH_NOTE`

- The dataset structure matches the row-class, classification, holdout,
  source, uncertainty, and observable groups defined in
  `data/atomic_clocks/schema.md`.
- The `source` group uses field names
  (`citation`, `doi`, `archive_url`, `retrieval_date`,
  `checksum_sha256`, `checksum_scope`, `license_note`) that match the
  schema sketch exactly.

**Note:** The current schema sketch uses `source:` as the per-row group
name; the synthetic loader expects `source_metadata:` instead
(see `physics_lab/engines/atomic_clock_residuals.py`,
`REQUIRED_ROW_KEYS`). The Beloy dataset uses `source:`, which means it
follows the schema sketch but cannot be parsed by the synthetic-only
loader as-is. This is a real-row-loader scoping issue (see "Loader
path" below), not a schema-validity defect.

### Holdout boundary — `BLOCKER_FOR_BENCHMARK_ONLY`

- Every row carries `holdout.split: unassigned` and
  `holdout.freeze_manifest: null`.
- This is acceptable for the current sandbox-only first-batch pin,
  because no model selection has occurred. It is a `BLOCKER` per
  `TASK-0332`'s "Holdout boundary missing" before any benchmark or
  fit consumes these rows. The pin must therefore include the explicit
  rule that a holdout / no-peek freeze manifest is required before
  promoting from `PINNED_DATASET` to `BASELINE_READY`.

### Deterministic loader path for real rows — `BLOCKER_FOR_BENCHMARK_ONLY`

- `physics_lab/engines/atomic_clock_residuals.py` currently only
  validates `synthetic_dry_run` rows; its `ALLOWED_SYNTHETIC_ROW_CLASSES`
  set excludes `direct_measurement`, and its required-key set expects
  `source_metadata` rather than the real-row `source`.
- Per `TASK-0332`, "Loader not real-row capable" is a direct-measurement
  blocker. It does not block the pin (the dataset is already committed
  and reviewed) but it does block any benchmark or fit consumer, and
  it must be cleared before `BASELINE_READY`.

### Promotion-boundary discipline — `PASS`

- `scope.sandbox_only: true`, all of `benchmark_allowed`,
  `drift_fitting_allowed`, `derived_constants_constraint_allowed`,
  `claim_promotion_allowed`, `prediction_registry_allowed` are
  `false`.
- `promotion_boundary` block names the required next step
  (maintainer review before any baseline benchmark) and re-asserts
  that `TASK-0344` and `TASK-0332` must be re-checked. This re-check
  is the `TASK-0344`/`TASK-0332` re-evaluation.

## Campaign State Classification

`PINNED_DATASET`.

Rationale:

- one source artifact is pinned with checksum, retrieval date, licence,
  and version-of-record cross-check;
- at least one real row is committed under an explicit covariance rule
  (Branch B fold-in) and an explicit version-drift policy
  (`NO_DRIFT`);
- the dataset is correctly sandbox-only with all benchmark and promotion
  switches off;
- the readiness gate dimensions that bind on the pin all `PASS` or
  `PASS_WITH_NOTE` only.

The campaign is **not** `BASELINE_READY`. The pin is locked, but at
least four real blockers remain before any baseline benchmark can run.

## Blockers Before `BASELINE_READY`

| # | Blocker | Required resolution | Owner candidate |
| --- | --- | --- | --- |
| 1 | Cross-ratio covariance unresolved (no 3×3 matrix; per-row Branch B totals only) | Reconstruct approximate cross-ratio covariance from per-clock columns, OR commit explicit "ignore cross-row correlations" policy for the first benchmark with a flagged limitation. | `TASK-0402` |
| 2 | Holdout / reveal boundary missing | Set `holdout.split` and a `freeze_manifest` (or a campaign-wide no-peek manifest) on every row before any model selection. | Future benchmark-design task. |
| 3 | Deterministic real-row loader path missing | Extend `physics_lab/engines/atomic_clock_residuals.py` (or add a sibling loader) to validate `row_class: direct_measurement` rows with the real-row required-key set, including the `source` vs `source_metadata` reconciliation. | Future loader task. |
| 4 | Single-source replay risk | Either commit a second independent direct-ratio source (per `TASK-0403`) and pin it under the same gate, OR obtain explicit maintainer approval for a single-source first baseline with a stated multiple-testing/replay limitation. | `TASK-0403` (preferred) or maintainer waiver. |

Additionally, the documentation gaps in the uncertainty-semantics
section (field-name standardisation `total` vs `total_uncertainty`, the
value-notation vs `uncertainty.total` reconciliation note, and the
per-row χ²_red asymmetry preservation rule) should be addressed in the
benchmark-readiness work, but they are not blockers for the pin
itself.

## Sandbox-Only Boundary (Reaffirmed)

This re-check is metadata-only. It does not:

- fit any drift or trend;
- derive any constants-variation constraint;
- write or modify any `data/atomic_clocks/*.yaml`;
- modify the synthetic-only `physics_lab/engines/atomic_clock_residuals.py`;
- create or modify any `prediction_registry/` entry;
- modify any `claims/`, `knowledge/`, or canonical `results/` artifact;
- claim a discovery, new physics, or breakthrough.

The committed Beloy 2021 rows remain `status: sandbox_first_seed` with
all of `benchmark_allowed`, `drift_fitting_allowed`,
`derived_constants_constraint_allowed`, `claim_promotion_allowed`, and
`prediction_registry_allowed` set to `false`.

## Limitations

- The cross-check against the Nature version-of-record relies on a
  maintainer-side local comparison
  (`not_recheckable_from_committed_artifacts_alone: true`). This
  re-check does not re-derive that comparison; it confirms the
  documented `NO_DRIFT` result is recorded in `provenance.yaml` and
  preserved in the dataset's `source_artifact.version_check_with_publication_of_record`
  block.
- No 3×3 cross-ratio covariance matrix is published by the source; the
  re-check accepts the documented Branch B fold-in as the per-row
  covariance treatment for the pin, while flagging the cross-row
  reconstruction as a benchmark-time requirement.
- The re-check does not authorise any benchmark, drift fit,
  constants-variation constraint, or promotion. The
  benchmark-readiness gate must be re-run after Blockers 1–4 are
  resolved.
- The campaign remains single-source; a true Gate-B style independent
  replay across atomic-clock sources cannot be performed until
  `TASK-0403` (or equivalent) commits a second direct-ratio source.

## Verdict

`PINNED_DATASET` (sandbox-only). The Beloy 2021 direct-ratio rows pass
the row-readiness gate at the pin level: source artifact pinned and
version-drift cleared, row-class and uncertainty semantics intact,
within-row covariance treatment documented under Branch B, and
promotion boundaries correctly held at sandbox-only. Promotion to
`BASELINE_READY` remains blocked by (1) the unresolved cross-ratio
covariance policy, (2) the missing holdout/no-peek boundary,
(3) the synthetic-only loader's lack of a `direct_measurement`
validation path, and (4) the absence of a second independent source
(or explicit single-source baseline waiver).

## Output-Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `not_applicable` for scientific claim; reviewable
  workflow output is `PINNED_DATASET` for the Atomic-Clock Residuals
  campaign (sandbox-only).
- **Canonical destination:** `docs/reviews/atomic-beloy-2021-row-readiness-recheck.md`
  (this file). Review-only artifact; no `agent_runs/`, `results/`,
  `prediction_registry/`, `claims/`, or `knowledge/` entries.
- **Review tier:** `none` (campaign-status review; no RESULT/PRED
  tier applies).
- **Gate A status:** not attempted (no `RESULT/PRED` artifact
  proposed).
- **Gate B status:** not attempted (single-source; no independent
  replay possible yet).
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Limitations and blockers:** see the four `BASELINE_READY` blockers
  above and the limitations section. The single-source replay risk and
  the missing real-row loader path are the load-bearing items for the
  next round of atomic-clock work.
