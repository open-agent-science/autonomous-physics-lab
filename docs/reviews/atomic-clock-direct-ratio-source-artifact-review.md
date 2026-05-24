# Atomic-Clock Direct Ratio Source Artifact Review

**Task:** TASK-0355
**Status:** review (metadata-only; no values; no fits; no claims)
**Campaign:** Atomic-Clock Residuals
**Source candidate:** Beloy et al. 2021 — Boulder Atomic Clock
Optical Network optical-frequency-ratio measurements
**Inputs reviewed:**

- `docs/campaigns/atomic-clock-residuals.md`
- `docs/reviews/atomic-clock-source-manifest-template-review.md`
- `docs/reviews/atomic-clock-primary-frequency-ratio-source-review.md`
- `docs/reviews/atomic-clock-derived-constraint-source-review.md`
- `docs/reviews/atomic-clock-covariance-uncertainty-semantics.md`
  (TASK-0344, sibling PR; the covariance contract this review
  consumes)
- `data/atomic_clocks/source_manifest_template.yaml`
- `data/atomic_clocks/schema.md`

## Scope

This review selects **exactly one** concrete source-artifact
candidate for direct frequency-ratio rows in the Atomic-Clock
Residuals campaign. It records the source locator and provenance
fields, evaluates recoverability of the discipline fields the
TASK-0344 covariance contract requires, and returns an explicit
admissibility verdict.

It does not ingest any frequency value, does not fit any drift,
does not derive any constraint, does not add any prediction
registry entry, and does not promote any claim. Source-artifact
caching, checksum capture, and per-row YAML curation belong to a
**separate** maintainer-approved follow-up task.

## Source Candidate

**Beloy, K., et al. (2021)** — *Frequency ratio measurements at
18-digit accuracy using an optical clock network*, **Nature 591,
564**, on behalf of the Boulder Atomic Clock Optical Network
(BACON) Collaboration.

| Provenance field | Recorded value |
| --- | --- |
| `source_id` (proposed) | `aclock-2021-beloy-bacon-frequency-ratios` |
| `source_class` | `peer_reviewed_table` (direct frequency-ratio measurement axis) |
| `source_title` | Frequency ratio measurements at 18-digit accuracy using an optical clock network |
| `issuing_body` | Nature (peer-reviewed primary publication) plus BACON Collaboration |
| `publication_date` | 2021-03-25 |
| `nature_doi` | [10.1038/s41586-021-03253-4](https://doi.org/10.1038/s41586-021-03253-4) |
| `arxiv_preprint` | [arXiv:2005.14694](https://arxiv.org/abs/2005.14694) |
| `clock_pairs_reported` | Al⁺/Yb, Al⁺/Sr, Yb/Sr ratios (three independent optical-clock comparisons reported in one campaign) |
| `expected_row_count` | 3 ratio rows per measurement campaign window plus per-component uncertainty rows |
| `retrieval_date` | not retrieved by this task (planning-only review) |
| `access_path_for_metadata` | Nature article page (DOI link above); arXiv preprint freely accessible |
| `archive_plan` | future row-curation task to commit a pinned PDF of the arXiv preprint as a `committed_copy` artefact under `data/atomic_clocks/source_artifacts/2021-beloy-bacon/`, with SHA-256 recorded |
| `license_or_reuse_notes` | arXiv perpetual licence allows archival redistribution of the author's accepted manuscript; the Nature-published version-of-record carries Nature's standard licence terms and must not be redistributed verbatim. The curator must commit the arXiv preprint, not the Nature PDF. |

The Beloy 2021 paper is chosen because:

- it reports three direct optical-clock frequency ratios (Al⁺/Yb,
  Al⁺/Sr, Yb/Sr) in a single coordinated campaign, which yields a
  small, reviewable first batch of direct rows;
- the arXiv preprint is openly accessible under arXiv's perpetual
  licence, so the source-artifact PDF can be committed under the
  `committed_copy` archive policy without breaching publisher
  terms;
- the paper explicitly reports per-ratio total uncertainty,
  statistical and systematic components, and the campaign window,
  satisfying the TASK-0344 minimum-discipline fields when the
  curator extracts the per-ratio summary table;
- the same campaign produces three correlated ratios (the same
  underlying clocks contribute to multiple ratios), which directly
  exercises the TASK-0344 C2 (shared sensitivity coefficients) and
  C3 (direct/derived double count) stop conditions and lets the
  campaign learn its covariance handling on a single
  well-understood publication before scaling.

## Recoverability Check Against TASK-0344 Discipline Fields

The following fields are required by the TASK-0344 covariance and
uncertainty contract before any direct row enters the residual
axis. The check is **paper-level metadata only**; no values are
copied here.

| Field | Recoverable from Beloy 2021? | Notes |
| --- | --- | --- |
| `transition_label` (per clock) | Yes | The paper names the optical transitions for each clock species used. |
| `ratio_partner` | Yes | Each ratio explicitly names both clock systems. |
| `campaign_epoch` / `campaign_window` | Yes | The paper records the measurement window for the campaign. |
| `units` (e.g. dimensionless ratio, `Hz`, `relative`) | Yes | Frequency ratios are dimensionless; the paper records the convention explicitly. |
| `total_uncertainty` | Yes | Reported per ratio. |
| `statistical_uncertainty` | Yes | Reported separately per ratio. |
| `systematic_uncertainty` | Yes | Reported separately per ratio. |
| `systematic_components` (optional) | Partially | The paper itemises systematic budgets; future curator must decide whether to copy the per-component table or only the totals. |
| `confidence_level_label` | Yes | The paper records the confidence level used. |
| `asymmetric_upper` / `asymmetric_lower` | Likely `null` | Reports symmetric uncertainties by default. The curator must verify and excplicitly record `null` rather than silently assume symmetry. |
| `bound_style` | Yes | The paper reports measurements, not one-sided bounds, for these ratios. |
| `covariance_reference` | **Partial** | The paper documents that the three ratios share underlying clock systems and therefore share systematic budget. The full covariance matrix may or may not be in the SI; the curator must verify. **This is the highest-priority verification step.** |
| `direct_vs_derived_status` | Yes | All three rows are direct measurements; no derivation chain. |

## Blockers Found

### B1 — Covariance matrix verification required

Per the TASK-0344 stop condition C2, when two or more derived
constraint rows share a sensitivity coefficient, the manifest must
record the shared coefficient and the combination rule that handles
it. The same logic applies to direct rows when they share
systematic budget. The three Beloy 2021 ratios share underlying
clock systems (Yb appears in two ratios; Sr appears in two;
Al⁺ appears in two), which means the three rows are **not
independent** on the residual axis.

A future row-curation task must verify:

- whether the Beloy 2021 SI publishes the full 3×3 covariance
  matrix, OR
- whether the per-ratio total uncertainties already include the
  shared-systematic contribution (in which case a diagonal
  approximation is documented as adequate by the source itself).

If neither holds, ingestion stops with
`SOURCE_MANIFEST_INCOMPLETE: shared_campaign_systematics_not_separable`
per TASK-0344 C1.

### B2 — Source-artifact PDF must be the arXiv preprint, not the Nature PDF

The Nature-published version-of-record carries Nature's standard
licence terms. The arXiv preprint is the only freely
redistributable form. The future row-curation task must commit
the arXiv PDF under `data/atomic_clocks/source_artifacts/2021-beloy-bacon/`
and record its SHA-256, not the Nature PDF. The curator must
verify that the arXiv preprint matches the Nature-published table
values before extracting rows.

### B3 — Per-systematic-component table extraction is optional and
must be decided in advance

The paper itemises systematic-budget components per ratio. A
future curator may extract only the per-ratio totals (simpler,
loses per-component visibility) or the full per-component table
(richer, more conflict-prone). The choice must be locked in the
follow-up task's `planning_context` before any row is committed,
because the per-component table multiplies the row count and
changes the schema shape.

## Verdict

**`ADMISSIBLE_WITH_BLOCKERS`**

The Beloy 2021 / BACON paper is the strongest single concrete
source-artifact candidate for direct frequency-ratio rows in the
Atomic-Clock Residuals campaign. It satisfies the TASK-0344
minimum-discipline fields at the paper-metadata level, the arXiv
preprint provides a clean archive-and-redistribute path, and the
three correlated ratios exercise the shared-systematic discipline
on a small reviewable batch.

Three blockers must be cleared before any row is curated:

1. **B1** — covariance verification (highest priority);
2. **B2** — confirm the arXiv preprint is the artifact to commit;
3. **B3** — lock per-row vs per-component extraction decision in
   the follow-up task spec.

## Recommended Next Row-Curation Task Shape

A future maintainer-approved row-curation task should:

- pin the arXiv preprint as a `committed_copy` artefact under
  `data/atomic_clocks/source_artifacts/2021-beloy-bacon/` with
  SHA-256 recorded in `source_manifest.yaml`;
- verify B1 (covariance) — read the SI section on shared
  systematics; if a full covariance matrix is present, commit the
  matrix as a separate artefact and record `covariance_reference`
  per row; if only diagonal totals are present, record
  `covariance_reference: diagonal_per_paper_explicit` with the
  paragraph cite;
- pick the extraction shape (per-ratio total or per-component) per
  B3 and lock it before any row is written;
- commit 3 direct rows (Al⁺/Yb, Al⁺/Sr, Yb/Sr) under
  `data/atomic_clocks/aclock-0001-beloy-2021-bacon.yaml`;
- mark each row `mass_class`-equivalent for atomic-clock semantics:
  `row_class: direct_frequency_ratio_measurement`,
  `direct_vs_derived_status: direct`,
  `confidence_level_label` per paper, `bound_style: measurement`;
- run the TASK-0344 BLOCKER recommendations (e.g. asymmetric-bound
  enforcement) against the committed rows;
- do not score any drift fit, derived constants constraint, or
  reveal in the same task.

The follow-up task should reference both this source-artifact
review and the TASK-0344 covariance contract as
`related_objects`. If the covariance verification (B1) fails, the
follow-up task stops with `BLOCKED_VALUE_SEMANTICS` and the
campaign stays sandbox-only.

## What This Review Did Not Do

- It did not fetch, download, or read the Beloy 2021 paper.
- It did not commit the arXiv preprint or any source-artifact PDF.
- It did not edit `data/atomic_clocks/source_manifest_template.yaml`
  (deferred to the follow-up task to avoid TASK-0344 conflict
  surface).
- It did not record any frequency-ratio value or uncertainty
  number.
- It did not authorise a real `TASK-0332` reveal.
- It did not promote any claim, knowledge entry, or canonical
  result.

## Limitations

- The recoverability check uses paper-metadata knowledge only.
  The curator running the follow-up task must verify the SI
  structure (especially the covariance section) at retrieval time;
  the verdict may shift to `NOT_ADMISSIBLE` if B1 cannot be
  cleared.
- The choice of Beloy 2021 is one strong candidate, not the only
  one. McGrew et al. 2018 (Yb-Sr-Hg ratios), Lange et al. 2021
  (Yb⁺ E2/E3 ratio), and BIPM CCTF working-group reports are
  alternative single-source candidates the maintainer may prefer.
  Each would need its own source-artifact review under a new
  TASK-XXXX.
- This review does not estimate how many ratios will survive the
  TASK-0344 discipline gate. That is a per-source-artifact
  diagnostic owned by the follow-up curation task.
- The arXiv-vs-Nature redistribution split assumes current
  publisher conventions. The curator must reconfirm at retrieval
  time.

## Verdict (Restated)

`ADMISSIBLE_WITH_BLOCKERS` — Beloy 2021 / BACON is the
recommended first concrete source-artifact for the campaign's
direct frequency-ratio axis. Three blockers (covariance
verification, arXiv-preprint pinning, extraction-shape lock) must
be cleared by the follow-up row-curation task before any row is
written.
