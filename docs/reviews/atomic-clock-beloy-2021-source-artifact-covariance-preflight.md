# Atomic-Clock Beloy 2021 Source Artifact And Covariance Preflight

**Task:** TASK-0363
**Status:** preflight (metadata-only; no clock values; no fits; no claims)
**Campaign:** Atomic-Clock Residuals
**Source candidate:** Beloy, K., et al. (2021) — Boulder Atomic Clock
Optical Network (BACON) optical-frequency-ratio measurements
(*Nature* **591**, 564; arXiv:2005.14694).

## Inputs reviewed

- `docs/campaigns/atomic-clock-residuals.md`
- `docs/reviews/atomic-clock-direct-ratio-source-artifact-review.md`
  (TASK-0355 source selection and B1/B2/B3 blocker definitions)
- `docs/reviews/atomic-clock-covariance-uncertainty-semantics.md`
  (TASK-0344 covariance and uncertainty contract)
- `data/atomic_clocks/schema.md`
- `data/atomic_clocks/source_manifest_template.yaml`
- `data/atomic_clocks/source_artifacts/2021-beloy-bacon/README.md`
  (this task's directory README)

## Scope

This preflight clears the highest-risk covariance and redistribution
blockers identified by TASK-0355 (B1, B2, B3) before any future
row-curation task may extract a real direct-ratio row from the
Beloy 2021 / BACON paper. It records:

1. the pinned source-artifact directory and the planned PDF cache
   policy (per-task `README.md`);
2. the **covariance-handling contract** the row-curation task must
   follow, restated against the TASK-0344 stop conditions;
3. the **extraction-shape lock** for the first row batch
   (per-ratio totals only, no per-component table on the first
   pass);
4. the unresolved verification step that remains gated on actual
   retrieval of the arXiv preprint and SI.

This preflight does **not** fetch the arXiv preprint, does **not**
record any frequency-ratio value, does **not** record any
uncertainty number, does **not** fit any drift, does **not** add
any prediction registry entry, and does **not** promote any claim,
result, or knowledge file. It is a paper-metadata and
campaign-policy document.

## Source artifact pinning

A new directory at
`data/atomic_clocks/source_artifacts/2021-beloy-bacon/` is created
with a metadata-only `README.md`. The README records:

- the planned arXiv-preprint artifact (`arxiv-2005.14694.pdf`) and
  its checksum sidecar file (`arxiv-2005.14694.sha256`);
- the planned optional SI artifact and optional covariance-matrix
  YAML;
- the retrieval policy (arXiv-preprint-only; Nature PDF forbidden);
- the covariance-handling contract restated below;
- the locked first-batch extraction shape (per-ratio totals only).

The arXiv preprint itself is **not** committed by this task. The
follow-up row-curation task fetches it, archives it under that
directory, and commits the SHA-256 sidecar plus a per-artifact
`provenance.yaml`.

### B2 — arXiv vs Nature PDF (cleared by policy)

Verdict: **CLEARED BY POLICY.**

The row-curation task must commit the arXiv preprint only and must
not commit the Nature version-of-record PDF. This decision is now a
policy line in the directory `README.md` rather than a TBD. The
Nature DOI remains the publication-of-record reference and must be
recorded alongside the arXiv locator in any per-row source field;
this preserves the publisher citation while keeping the
redistributable artifact bounded to the arXiv perpetual licence.

If the arXiv preprint and the Nature-published table values disagree,
the row-curation task must halt with
`SOURCE_ARTIFACT_VERSION_DRIFT` (a new stop condition recommended
to the maintainer below) and not commit any row until the
discrepancy is resolved.

## Covariance preflight

### Restatement of the TASK-0344 contract

The TASK-0344 contract requires that any row claiming a direct
measurement axis carry one of three valid covariance treatments
(C1, C2, C3 below) and that rows whose covariance treatment cannot
be recovered from the source are excluded with explicit
`inclusion_reason`. The three Beloy 2021 ratios (Al⁺/Yb, Al⁺/Sr,
Yb/Sr) share underlying clock systems and therefore are **not
independent**. The Yb clock appears in two ratios, the Sr clock
appears in two, and the Al⁺ clock appears in two.

The C1 / C2 / C3 stop conditions therefore apply directly:

- **C1** — `SOURCE_MANIFEST_INCOMPLETE: shared_campaign_systematics_not_separable`
  fires if the SI does not separate or fold the shared-systematic
  contribution.
- **C2** — shared sensitivity coefficients must be recorded per row
  alongside a documented combination rule.
- **C3** — direct rows must not be double-counted with a derived
  drift bound or constants constraint that depends on the same
  ratios.

### B1 — covariance verification (partially cleared; protocol locked)

Verdict: **PROTOCOL CLEARED; FACT-CHECK REMAINS GATED ON RETRIEVAL.**

This preflight cannot fetch the arXiv preprint and SI inside the
TASK-0363 scope (no network ingestion of value-bearing material is
authorised, and the source-artifact retrieval is a separate
maintainer-approved task). The verification protocol that the
future row-curation task **must** follow is locked here:

1. Fetch the arXiv preprint and SI under the policy in
   `data/atomic_clocks/source_artifacts/2021-beloy-bacon/README.md`.
2. Locate the SI section on shared systematics and covariance.
3. **Branch A — full covariance matrix present.** Commit the
   matrix as `covariance_matrix.yaml` under the source-artifact
   directory. For each of the three rows, record
   `covariance_reference: covariance_matrix.yaml#full_three_by_three`
   and cite the SI table number and equation reference.
4. **Branch B — only per-ratio totals, with explicit text that
   shared-systematic contributions are folded in.** For each row,
   record
   `covariance_reference: diagonal_per_paper_explicit_<paragraph_cite>`
   and cite the paragraph in `provenance.yaml`. Note the residual
   axis must still treat the three ratios as mildly correlated and
   the covariance contract should record this with an explicit
   `correlation_treatment: diagonal_per_paper_documented_assumption`
   field.
5. **Branch C — neither A nor B.** Halt with
   `SOURCE_MANIFEST_INCOMPLETE: shared_campaign_systematics_not_separable`
   per TASK-0344 stop condition C1. No row is committed; the
   row-curation task closes with `BLOCKED_VALUE_SEMANTICS`.

The factual check (which branch holds) cannot be performed here.
The row-curation task is the only authorised place to perform it,
because performing it here would either require fetching the
artifact (not authorised by TASK-0363) or copying second-hand
covariance claims into the campaign without a verifiable source
field.

### B1 fallback if SI is paywalled separately

If the SI is paywalled separately from the arXiv preprint and the
arXiv preprint does not include the covariance section, the
row-curation task must:

- attempt to locate an open-access mirror of the SI (NIST and
  NIST-collaborator postprint servers commonly mirror BACON SI);
- if no open-access copy exists, halt with
  `SOURCE_MANIFEST_INCOMPLETE: covariance_section_not_open_access`
  and do not commit any row;
- maintainer review is required to either drop Beloy 2021 as the
  first source or accept a documented diagonal approximation
  caveated as `covariance_treatment: paywalled_si_not_audited` and
  marked as sandbox-only evidence not admissible to the residual
  axis until audited.

### C2 — sensitivity-coefficient bookkeeping (locked)

The per-row schema must add a `shared_clock_systems` field listing
the clock species that contribute to that ratio. For the three
Beloy 2021 ratios this is:

| ratio | shared clock systems |
| --- | --- |
| Al⁺/Yb | Al⁺, Yb |
| Al⁺/Sr | Al⁺, Sr |
| Yb/Sr | Yb, Sr |

This is paper-metadata at the species level only, not a value.
Recording it now lets the C2 combination rule (TASK-0344) gate any
later derived-constraint row that depends on these same species.

### C3 — direct/derived double-count gate (locked)

The row-curation task must check that no derived drift bound or
constants-variation constraint that depends on Al⁺, Yb, or Sr
ratios is already present in the residual axis before committing
the Beloy 2021 direct rows. Per TASK-0344 stop condition C3, if a
derived row with overlapping input list is already present, the
direct rows are committed but the derived row is flagged for
re-review under a separate task.

## B3 — extraction-shape lock

Verdict: **LOCKED TO PER-RATIO TOTALS FOR THE FIRST BATCH.**

The row-curation task is now locked to extract only per-ratio
totals (Al⁺/Yb, Al⁺/Sr, Yb/Sr) carrying:

- `total_uncertainty`
- `total_uncertainty_unit`
- `statistical_uncertainty` (when separately reported)
- `systematic_uncertainty` (when separately reported)
- `confidence_level_label`
- `asymmetric_upper` / `asymmetric_lower` (recorded explicitly,
  `null` only when the paper documents symmetric uncertainties)
- `bound_style: measurement`
- `direct_vs_derived_status: direct`

The per-systematic-component table is **deferred** to a separate
maintainer-approved task. Rationale:

- the per-component table multiplies the row count from 3 to
  3 × number-of-components and changes the schema shape;
- locking the simpler shape first keeps the first batch reviewable
  and reversible;
- the per-component extraction can run after the per-ratio rows
  pass the TASK-0344 discipline gate and the TASK-0332 readiness
  gate.

## Recommended new stop condition

Add `SOURCE_ARTIFACT_VERSION_DRIFT` to the campaign
`global_stop_conditions` in
`data/atomic_clocks/source_manifest_template.yaml` under a separate
maintainer-approved task. Definition:

> The arXiv preprint and the version-of-record published table
> disagree on a ratio value, an uncertainty, or a campaign window.
> No row is committed until the row-curation task resolves the
> discrepancy in a separate review.

This preflight does **not** edit the manifest template; the edit
is logged here as a recommendation for the maintainer to assign.

## What this preflight did not do

- It did not fetch the arXiv preprint or the Nature article.
- It did not commit any PDF, SHA-256, or covariance matrix.
- It did not record any frequency-ratio value, uncertainty number,
  or drift fit.
- It did not edit `data/atomic_clocks/source_manifest_template.yaml`.
- It did not edit the TASK-0344 covariance contract.
- It did not run a TASK-0332 readiness gate or any reveal.
- It did not promote any claim, knowledge entry, or RESULT-*.

## Verdict

**`PARTIALLY_CLEARED`** —

- B2 (arXiv vs Nature redistribution) is **cleared by policy** and
  locked in the source-artifact directory README.
- B3 (extraction-shape lock) is **cleared** at per-ratio totals
  only; per-component extraction is deferred.
- B1 (covariance verification protocol) is **protocol-cleared** —
  the verification branches A / B / C and the paywalled-SI
  fallback are locked here, but the factual check of which branch
  holds remains gated on actual retrieval of the arXiv preprint
  and SI. That retrieval is owned by the future row-curation
  task and is not authorised by TASK-0363.

The campaign remains sandbox-only with respect to real
direct-ratio rows. The next maintainer-approved task is the
row-curation task that executes the locked B1 verification
protocol and, if Branch A or Branch B holds, commits the three
Beloy 2021 per-ratio rows.

## Limitations

- This preflight cannot decide between B1 Branch A and Branch B
  without the SI in hand. The decision is deferred to the
  row-curation task.
- The arXiv-vs-Nature redistribution policy assumes current
  publisher conventions; the row-curation task must reconfirm at
  retrieval time.
- The per-row `shared_clock_systems` field recommended above is
  species-level only and is not a covariance substitute; the
  TASK-0344 contract still requires a `covariance_reference`
  field per row.
- The SI fallback path (paywalled SI) is a real risk for Nature
  publications and may force a maintainer-level review.
- No row is committed; no value is copied; no claim is promoted.

## Recommended next task shape

A future maintainer-approved task should:

- fetch the arXiv preprint and SI under the directory README policy;
- record `arxiv-2005.14694.pdf`, `arxiv-2005.14694.sha256`, and
  `provenance.yaml`;
- execute the B1 verification protocol (Branch A / Branch B /
  Branch C) and commit either a covariance matrix or a documented
  diagonal-with-cite per row;
- commit the three direct rows under
  `data/atomic_clocks/aclock-0001-beloy-2021-bacon.yaml` with the
  locked per-ratio-totals shape;
- run the TASK-0344 BLOCKER recommendations against the committed
  rows (asymmetric-bound enforcement, shared-clock-systems field,
  confidence-level normalisation);
- not run a TASK-0332 reveal in the same task;
- not write any drift fit, derived constants constraint, or PRED-*
  entry in the same task.

If the B1 verification fails (Branch C), the row-curation task
closes with `BLOCKED_VALUE_SEMANTICS` and the campaign stays
sandbox-only.
