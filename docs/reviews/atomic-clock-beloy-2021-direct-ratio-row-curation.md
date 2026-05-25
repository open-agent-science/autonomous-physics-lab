# Atomic-Clock Beloy 2021 Direct-Ratio Row Curation

**Task:** `TASK-0371`
**Predecessor:** `TASK-0363` (source-artifact + covariance preflight)
**Campaign:** Atomic-Clock Residuals
**Source candidate:** Beloy, K., et al. (BACON Collaboration), *Nature* **591**, 564 (2021); arXiv:2005.14694
**Outcome:** `FIRST_BATCH_SEED_COMMITTED` (sandbox-only; per-ratio totals; no benchmarks; no claims)

## Boundary

This row-curation task commits the first real direct-frequency-ratio values
into the Atomic-Clock Residuals campaign. It does **not** fit drift, does
**not** derive any constants-variation constraint, does **not** write a
prediction-registry entry, does **not** update any canonical RESULT-*
artifact, and does **not** promote any claim or knowledge file. The rows are
explicitly flagged sandbox-only.

## Source artifact

| Field | Value |
| --- | --- |
| Committed artifact | `data/atomic_clocks/source_artifacts/2021-beloy-bacon/arxiv-2005.14694.pdf` |
| Checksum sidecar | `arxiv-2005.14694.sha256` |
| SHA-256 | `bec1548829e7d4697ffd78dec453c00990c2937b71cc624c420a58e31ca60467` |
| Source locator | https://arxiv.org/abs/2005.14694 |
| Archive URL | https://arxiv.org/pdf/2005.14694 |
| Retrieval date (UTC) | 2026-05-25 |
| Licence | arXiv perpetual licence (committed preprint only) |
| Publication of record (cited, not committed) | doi:[10.1038/s41586-021-03253-4](https://doi.org/10.1038/s41586-021-03253-4) — Nature 591, 564 (2021) |

The Nature paper-of-record PDF is **not** committed. Nature's copyright
prohibits verbatim redistribution; the arXiv perpetual licence does permit
redistribution of the author's accepted manuscript, which is what this
artifact contains.

## Cross-version check (arXiv vs Nature)

TASK-0363 requires that the arXiv preprint values match the Nature
version-of-record values **before** any row is extracted.

| Step | Status |
| --- | --- |
| arXiv preprint fetched + checksummed | ✅ |
| Nature paper PDF held locally on maintainer machine | ✅ (not committed) |
| Side-by-side comparison of the three primary ratio values | ✅ all three matched bit-for-bit |
| Side-by-side comparison of the final 1-σ uncertainties (figure caption) | ✅ 5.9 / 8.0 / 6.8 × 10⁻¹⁸ matched |
| Result | **`NO_DRIFT`** |

Compared lines (identical in both versions):

- ν(Al⁺)/ν(Yb) = `2.162887127516663703(13)`
- ν(Al⁺)/ν(Sr) = `2.611701431781463025(21)`
- ν(Yb)/ν(Sr)  = `1.2075070393433378482(82)`

Full record is in
`data/atomic_clocks/source_artifacts/2021-beloy-bacon/provenance.yaml` under
`version_check_with_publication_of_record`. The cross-check is recorded as
`performer: roman (maintainer-side local cross-check)`,
`not_recheckable_from_committed_artifacts_alone: true`. A future maintainer
with continued Nature access can re-verify; no new commit is required if the
values still match.

## Covariance gate decision (TASK-0363 contract)

**Selected branch: B — per-ratio totals with explicit fold-in.**

| Branch | Required condition | Holds? |
| --- | --- | --- |
| A | Full 3×3 ratio covariance matrix published | **No** — neither arXiv nor Nature publishes a 3×3 ratio covariance matrix. |
| B | Per-ratio totals + explicit text stating shared systematics folded into each total | **Yes** — Table 1 publishes per-ratio totals; Sec. 4.5 ("Comprehensive Bayesian model") states "We make the conservative assumption that these systematic effects are fully correlated across all days of measurement", and the final Bayesian-model 1-σ is reported as Table 1's last row. |
| C | Halt | **No** — Branch B is satisfied. |

Each row's `uncertainty.total` is the Bayesian-model 1-σ from Table 1's
last row (`5.9 × 10⁻¹⁸` / `8.0 × 10⁻¹⁸` / `6.8 × 10⁻¹⁸`). The
`covariance_reference` field on every row is
`diagonal_per_paper_explicit_fold_in_bayesian_sec_4_5`.

## Per-row uncertainty budget (from Table 1, units 10⁻¹⁸)

| Contribution | Al⁺/Yb | Al⁺/Sr | Yb/Sr |
| --- | ---: | ---: | ---: |
| Systematic — Sr clock | — | 4.8 | 5.0 |
| Systematic — Yb clock | 1.4 | — | 1.4 |
| Systematic — Al⁺ clock | 1.7 | 1.5 | — |
| Systematic — Network (σN) | 0.3 | 0.5 | 0.5 |
| Systematic — Geopotential (σG) | 0.2 | 0.4 | 0.4 |
| Systematic — Quadrature subtotal | 2.2 | 5.1 | 5.2 |
| Statistical — WSE / SE† | 4.3 | 4.8† | 3.7 |
| Quadrature (sys ⊕ stat) | 4.8 | 7.0 | 6.4 |
| **Bayesian model (TOTAL committed)** | **5.9** | **8.0** | **6.8** |

†Al⁺/Sr uses the standard error of the mean without χ²ᵣₑd deflation per the
dagger footnote of Table 1 (χ²ᵣₑd = 0.2, under-scattered).

These per-component magnitudes are committed as
`uncertainty.systematic_components_e_minus_18` on each row so a future
benchmark can reconstruct an approximate cross-ratio covariance if needed.

## Cross-row shared-clock systematics

| Clock | Contributes to | Magnitude (10⁻¹⁸) |
| --- | --- | --- |
| Al⁺ | Al⁺/Yb, Al⁺/Sr | 1.7, 1.5 |
| Yb  | Al⁺/Yb, Yb/Sr  | 1.4, 1.4 |
| Sr  | Al⁺/Sr, Yb/Sr  | 4.8, 5.0 |

These are visible in Table 1 but the source does **not** publish a 3×3
cross-ratio covariance matrix. Any downstream benchmark that combines two or
more of these rows must either reconstruct an approximate matrix from Table 1
or explicitly document that cross-ratio correlations are being ignored. The
dataset YAML makes this visible per row in `correlation_notes`.

## Rows committed

| `row_id` | Ratio | Value | Total (1σ, fractional) |
| --- | --- | --- | --- |
| `ACR-0001-ROW-001` | Al⁺/Yb | 2.162887127516663703 | 5.9 × 10⁻¹⁸ |
| `ACR-0001-ROW-002` | Al⁺/Sr | 2.611701431781463025 | 8.0 × 10⁻¹⁸ |
| `ACR-0001-ROW-003` | Yb/Sr  | 1.2075070393433378482 | 6.8 × 10⁻¹⁸ |

Each row is `row_class: direct_measurement`, `classification.direct_measurement: true`,
`covariance_group: bacon_2018_campaign`, `epoch_start: 2017-11`,
`epoch_end: 2018-06`.

## What this curation did NOT do

- It did not commit the Nature paper PDF or Supplementary Information PDF.
- It did not extract or commit a per-systematic-component table; the
  extraction-shape lock from TASK-0363 limits the first batch to per-ratio
  totals.
- It did not commit a 3×3 cross-ratio covariance matrix (none is published).
- It did not fit any drift, derive any constants constraint, run any baseline
  benchmark, or produce any PRED-*, RESULT-*, CLAIM-*, or knowledge entry.
- It did not promote any campaign artifact beyond `sandbox_first_seed`.

## Follow-up steps available to a future task

These are documented here as visible follow-ups; **none are authorized by this
PR**:

1. **Repeated Nature cross-check.** A maintainer with continued Nature access
   can re-verify the three ratio values against the version-of-record; no
   commit needed unless drift is found.
2. **Per-component table expansion.** A maintainer-approved follow-up task may
   extract the per-systematic-component breakdown (Table S-series in the SI
   pages of the arXiv preprint) under a separate dataset id; it must keep the
   per-ratio-total rows in `acr-0001-*.yaml` immutable as the first batch.
3. **Cross-ratio covariance reconstruction.** A separate task may construct an
   approximate 3×3 cross-ratio covariance matrix from Table 1's per-clock
   contributions for benchmark use; must be explicitly labelled as
   reconstructed-from-per-clock-totals, not as a published matrix.
4. **TASK-0344 readiness re-check.** Before any benchmark run consumes these
   rows, the TASK-0344 covariance/uncertainty contract and the TASK-0332
   readiness gate must both be re-checked.

## Limitations

- Per-row totals are the published Bayesian-model 1-σ values; the per-clock
  systematic decomposition is informational, not a 3×3 cross-ratio covariance.
- The Al⁺/Sr row uses the standard error of the mean without χ²ᵣₑd deflation
  per the paper's dagger footnote; downstream consumers should preserve this
  asymmetry.
- Sandbox-only first-batch seed. Do not benchmark, fit drifts, derive
  constants constraints, or promote claims from these rows without explicit
  maintainer-approved follow-up.
- The arXiv preprint's SI sections are embedded in the same PDF (pages
  13–51) and are sufficient for the Bayesian-model description used by the
  Branch B decision. A separate SI artifact has not been committed.
