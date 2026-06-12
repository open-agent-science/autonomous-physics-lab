# Quantum Vossmeyer 1994 Source-Copy Handoff

**Task:** `TASK-0710`
**Campaign:** Quantum Size Effects
**Source ID:** `vossmeyer-1994-jpc-cds-absorption`
**Mode:** planning/source-artifact handoff only
**Decision:** `SOURCE_COPY_HANDOFF_DEFINED_ROW_READY_BLOCKED`

## Scope

This note turns the Vossmeyer 1994 CdS source from a promising metadata-only
blocker into an executable source-copy handoff. It defines acceptable routes,
metadata, checksum, and Table 1 verification requirements for a later
source-artifact task. It does not commit an ACS publisher PDF, transcribe Table
1 values, digitize figures, create `qd-*.yaml` rows, run size-effect baselines,
or promote claims.

## Inputs Reviewed

| Input | Role |
| --- | --- |
| `docs/reviews/quantum-cds-vossmeyer-source-artifact-verification.md` | `TASK-0687`; found promising Table 1 candidate but no committable source artifact. |
| `data/quantum_dots/source_manifest.yaml` | Current excluded manifest entry. |
| `docs/quantum-direct-source-artifact-intake.md` | Required source-artifact metadata and row-class evidence. |

## Accepted Source-Copy Routes

| Route | Accepted? | Requirements |
| --- | --- | --- |
| Maintainer-provided copy | Yes | Maintainer supplies a local full-text copy for checksum and inspection. The copy may be used for extraction metadata; it must not be committed unless the maintainer also records a license route allowing repository storage. |
| Institutional access review | Yes | A maintainer or curator with legitimate institutional access may inspect the article and record Table 1 headers/units. Access alone does not authorize committing the ACS PDF. |
| ACS publisher PDF commit | Blocked by default | Allowed only if a maintainer-approved license route explicitly permits committing the publisher PDF or a publisher-authorized copy. |
| Replacement source | Contingency | Use only if Vossmeyer Table 1 cannot be inspected or reuse cannot support even metadata-ledger row curation. The replacement source needs its own task/source-id review. |

The preferred next step is a maintainer-provided or institutional-access
inspection that produces checksum metadata and a table-structure ledger, while
keeping the publisher PDF out of git unless a separate license decision allows
it.

## Required Source-Copy Metadata

The next source-artifact task must record:

- DOI: `10.1021/j100082a044`;
- source locator used for access;
- retrieval or maintainer-supply date;
- upstream filename or maintainer-supplied filename;
- byte size of the inspected copy;
- SHA-256 checksum of the inspected copy;
- whether the copy is committed, checksum-only, or maintainer-local only;
- reuse note explaining why the PDF is or is not committed;
- citation for the source article;
- exact Table 1 page/location in the inspected copy.

If no committable copy is allowed, a checksum-only or maintainer-local ledger is
still useful, but row curation remains blocked until the extraction ledger is
reviewed.

## Article Table 1 Verification Checklist

Before any `qd-*.yaml` row exists, a curator must verify Table 1 directly from
the inspected source copy:

1. Confirm Table 1 is present in the primary article, not inferred only from
   secondary metadata.
2. Record the table title/caption verbatim enough to identify the surface.
3. Record column headers and units for sample identifier, SAXS or equivalent mean
   diameter / size axis, excitonic transition energy or wavelength, oscillator
   strength if present, and uncertainty or measurement spread if present.
4. Decide whether `absorption_peak_eV` is directly printed or requires a
   wavelength-to-energy conversion. If conversion is required, record the formula
   and source units before transcription.
5. Confirm the material family is pure-core CdS, not core-shell or device
   context.
6. Confirm the row count and whether all rows are discrete measured samples.
7. Record exclusions for rows missing size, energy, unit, or provenance fields.

This checklist verifies row admissibility only. It does not itself authorize
benchmark scoring or claim language.

## Extraction Ledger Fields

The later extraction ledger must include, per row:

- source_id: `vossmeyer-1994-jpc-cds-absorption`;
- source copy checksum;
- table reference and page/location;
- row identifier;
- material: `CdS`;
- size value and units as printed;
- normalized `diameter_nm` value and conversion note, if any;
- optical value as printed;
- normalized `absorption_peak_eV` and conversion note, if any;
- uncertainty fields or `uncertainty_class: unknown`;
- inclusion status and exclusion reason when applicable;
- curator identity and extraction date.

No LLM-memory, abstract-only, or secondary-summary value may enter the ledger.

## Manifest Decision

The source remains `inclusion_decision: excluded` and is not row-ready. The
manifest is updated only to point at this handoff and to clarify that the next
checksum policy is maintainer/institutional source-copy pending, not a completed
artifact.

## Still Forbidden

- committing ACS publisher PDFs without an explicit maintainer-approved license
  route;
- transcribing Table 1 values in this task;
- using abstract-level diameter or energy summaries as rows;
- digitizing figures as a shortcut around the Table 1 source-copy gate;
- running size-effect baselines or creating `RESULT-*`, `PRED-*`, `CLAIM`, or
  `KNOW` artifacts.

## Limitations

- No primary full text was inspected in this task.
- Table 1 remains promising but unverified at source-copy level.
- The future row task may still reject the source if headers, units, or reuse
  terms are insufficient.

## Output Routing Summary

- **Task verdict:** `SOURCE_COPY_HANDOFF_DEFINED_ROW_READY_BLOCKED`.
- **Canonical destination:** this review note,
  `docs/reviews/quantum-vossmeyer-source-copy-handoff.md`, plus a metadata-only
  manifest update.
- **Review tier:** none; no `RESULT-*` / `PRED-*` artifact.
- **Gate A status:** not applicable because no rows or metrics were produced.
- **Gate B status:** not applicable.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Dataset impact:** no `qd-*.yaml` row created; Vossmeyer remains excluded from
  usable rows.
- **Publication blocker:** primary source-copy checksum, reuse decision, Table 1
  header/unit verification, extraction ledger, and row-readiness review remain
  missing.
