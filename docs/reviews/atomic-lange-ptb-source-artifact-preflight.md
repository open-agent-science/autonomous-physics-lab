# Atomic Lange/PTB Yb+ Source-Artifact Preflight

**Task:** `TASK-0652`
**Campaign:** Atomic-Clock Residuals
**Mode:** planning only (source-artifact preflight; no value transcription, no benchmark)
**Verdict:** `METADATA_PINNED_ARTIFACT_RETRIEVAL_GATED`
**Provenance verification date (UTC):** 2026-06-07

## Scope And Boundaries

This preflight pins the exact source locator, citation metadata, reuse posture,
and checksum/archive feasibility for the Lange/PTB Yb⁺ fallback candidate that
[`TASK-0606`](./atomic-second-yb-sr-fallback-source-scout.md) named but left
blocked on the locator. It uses bibliographic provenance verification only. It
does **not**:

- transcribe any clock frequency or ratio value (none appear in this note);
- fit constants drift or compute any benchmark/consistency metric;
- compare Lange/PTB against Beloy, Nemitz, or Pizzocaro;
- create any `RESULT-*`, `CLAIM-*`, `PRED-*`, `KNOW-*`, or `data/atomic_clocks/acr-*.yaml` row;
- retrieve or commit the publisher/preprint PDF (artifact retrieval is deferred).

## Inputs

- [atomic-second-yb-sr-fallback-source-scout.md](./atomic-second-yb-sr-fallback-source-scout.md) (`TASK-0606`)
- [atomic-clock-residuals campaign](../campaigns/atomic-clock-residuals.md)
- [data/atomic_clocks/source_manifest.yaml](../../data/atomic_clocks/source_manifest.yaml)
- [fresh-data-intake-protocol.md](../fresh-data-intake-protocol.md)
- bibliographic records for the candidate publication (arXiv abstract page + DOI landing page), provenance only.

## Pinned Source Locators And Citation

| Field | Value |
| --- | --- |
| Title | "Improved limits for violations of local position invariance from atomic clock comparisons" |
| Authors | R. Lange, N. Huntemann, J. M. Rahm, C. Sanner, H. Shao, B. Lipphardt, Chr. Tamm, S. Weyers, E. Peik (PTB) |
| Publication of record | Phys. Rev. Lett. **126**, 011102 (2021), published 2021-01-08 |
| Publication DOI | `10.1103/PhysRevLett.126.011102` |
| Preprint | arXiv:`2010.06620` (v1 2020-10-13, v2 2021-01-07) |
| arXiv DOI | `10.48550/arXiv.2010.06620` |
| Abstract locator | `https://arxiv.org/abs/2010.06620` |
| Preprint PDF locator | `https://arxiv.org/pdf/2010.06620` |

This resolves the scout's open item *"Stable locator status: not pinned"*. The
locator is now pinned at metadata level.

## Source Class And Admissibility

This is **not** a Yb/Sr direct-ratio source. The measured quantities are:

- the ¹⁷¹Yb⁺ **E3 vs Cs** absolute frequency (two Cs fountains as the reference);
- the intra-ion **E3/E2** optical frequency ratio (Cs-independent);

used over multi-year repeated comparisons for a local-position-invariance / α-drift
limit. Consequences for the campaign:

1. **Different source family.** It is a Yb⁺ (E3/Cs, E3/E2) family, not a second
   member of the Yb/Sr direct-ratio family used by Beloy/Nemitz/Pizzocaro.
2. **Does not unblock the first Yb/Sr benchmark.** Because it carries no Yb/Sr
   row, it cannot serve as the second Yb/Sr row for `TASK-0456`. That benchmark
   still depends on a Pizzocaro covariance reconstruction
   ([feasibility review](./atomic-pizzocaro-covariance-reconstruction-feasibility.md))
   or another Yb/Sr source.
3. **It is still valuable** as the campaign's *alternate high-precision fresh-data
   path*: a future Yb⁺ E3/Cs absolute-frequency or E3/E2-ratio benchmark axis from
   an institution (PTB) independent of the BACON (NIST+JILA+NIST) and INRiM/NICT
   surfaces, matching the `strategy_alignment` goal of reducing single-source
   dependence.
4. **Covariance separability** (Cs reference vs optical-ratio systematics) is
   plausible because the paper reports a systematic budget, but that is an
   extraction-stage question and is **not** resolved here.

## Reuse Posture (published ≠ redistributable)

| Surface | Posture |
| --- | --- |
| Citation / DOI / arXiv id / dates | Committable as facts (metadata-only). |
| PRL publisher PDF | **Not redistributable** (APS copyright). `redistributable_here: false`. |
| arXiv preprint PDF | Under arXiv `nonexclusive-distrib/1.0` — this grants **arXiv** a non-exclusive distribution licence, not a clear third-party redistribution right. Committing the PDF into the repo is a **license-review decision**, not an automatic yes. |

The repository has previously committed arXiv preprint PDFs for Beloy
(`arXiv:2005.14694`) and Nemitz (`arXiv:1601.04582`) under a
`arXiv_perpetual_licence_for_committed_preprint` note. Applying that same posture
here would be a consistency decision for the maintainer/retrieval task; the
default arXiv licence does **not** by itself authorize third-party
redistribution, so this preflight flags it as `LICENSE_REVIEW_REQUIRED` rather
than asserting the PDF is committable. Contrast with Pizzocaro, whose Zenodo
dataset files are CC-BY-4.0 and therefore clearly redistributable.

## Checksum / Archive Feasibility

- **Feasible:** the arXiv preprint PDF is a stable, versioned, checksummable
  archive object (the same artifact shape already checksummed for Beloy and
  Nemitz). A future retrieval task can pin a `checksum_sha256` over the arXiv PDF
  exactly as those entries did.
- **No open machine-readable dataset:** unlike Pizzocaro (Zenodo CSV), this paper
  exposes its values in the article text/tables, not a separate open data record.
  Value extraction would therefore be PDF table/text transcription, which is an
  `EXTRACTION_NOT_REVIEWED` step deferred to a later task.
- **Metadata-only locator policy** is always safe and is what this task commits.

## Manifest Update

The live manifest [`data/atomic_clocks/source_manifest.yaml`](../../data/atomic_clocks/source_manifest.yaml)
previously held only a free-form `source_family_member_planning_only` placeholder
for Lange 2021. This task replaces that placeholder with a **structured
metadata-only candidate member** under `ACLOCK-SRC-CLASS-001`
(`source_id: ACLOCK-SRC-CANDIDATE-2021-LANGE-PTB-YBPLUS`) with:

- pinned locators, citation, and `publication_of_record` (`redistributable_here: false`);
- `value_status: metadata_only_no_values`, `checksum_sha256: null`,
  `retrieval_date: null` (no artifact retrieved);
- `readiness_state: SOURCE_CANDIDATE_METADATA_PINNED_ARTIFACT_RETRIEVAL_DEFERRED`;
- explicit `ingestion_blockers` (license review, not-a-Yb/Sr-row, extraction not
  started, checksum not pinned, epoch/systematic budget not locked, holdout unset).

No measurement values, datasets, covariance artifacts, or benchmark fields are
added.

## Recommended Next Step

Open a follow-up **artifact-retrieval task** (maintainer-assigned `TASK-XXXX` or
`TASK-PROPOSAL`) that, only after a license decision on the arXiv PDF:

1. retrieves and checksums the chosen archive object (or stays metadata-only if
   redistribution is declined);
2. records a `provenance.yaml` under
   `data/atomic_clocks/source_artifacts/2021-lange-ptb-ybplus/`;
3. scopes extraction as a Yb⁺ E3/Cs + E3/E2 **separate-family** surface, explicitly
   not a Yb/Sr row;
4. defers any benchmark/covariance work to the first-benchmark covariance policy.

Keep this candidate as the named fallback; do not reject it. It does not replace
the Pizzocaro Yb/Sr path but de-risks single-source dependence.

## Limitations

- Bibliographic provenance verification only; no artifact file was retrieved,
  checksummed, or committed, and no values were transcribed.
- The arXiv-PDF redistribution question is unresolved by design and is the main
  gate before any artifact commit.
- Covariance separability and exact campaign-window/epoch handling are
  extraction-stage questions, explicitly out of scope here.
- This review creates no follow-up task; canonical task creation is
  maintainer/proposal-gated.

## Output Routing Summary

- **Task verdict:** `METADATA_PINNED_ARTIFACT_RETRIEVAL_GATED` (source-candidate
  metadata pinned; artifact retrieval and row curation deferred).
- **Canonical destination:**
  `docs/reviews/atomic-lange-ptb-source-artifact-preflight.md` plus a metadata-only
  candidate entry in `data/atomic_clocks/source_manifest.yaml`.
- **Review tier:** `none`.
- **Gate A status:** not attempted (no result/dataset published).
- **Gate B status:** not applicable.
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Result / dataset artifact impact:** no `results/` or `acr-*.yaml` row created;
  manifest gains a metadata-only candidate (no values).
- **Limitations / blockers:** `LICENSE_REVIEW_REQUIRED` for the arXiv PDF;
  `DIRECT_ROWS_NOT_PRESENT` for Yb/Sr (different source family); extraction and
  checksum deferred. `TASK-0456` (first Yb/Sr benchmark) remains blocked.
