# MD-0002 Zenodo Record — Validation-Independence Clarification Pack

- Target record: https://zenodo.org/records/21207072 (version DOI
  10.5281/zenodo.21207072).
- Action type: **Zenodo metadata edit only** — same DOI, no new version
  (the dataset payload, checksums, and benchmark numbers are unchanged),
  per Decision Day #2 refinement R3. This is a classification note, not a
  correction or erratum, and must not be framed as one.
- Maintainer steps: Zenodo -> the record -> Edit -> append the paragraph
  below to the end of the Description -> Save (metadata-only publish).

## Paragraph to append to the record Description

> Validation-independence clarification (2026-07-06): the RESULT-0021
> benchmark cited in this record is AGENT_VALIDATED, meaning it was
> deterministically replayed with zero drift. The APL repository
> additionally records a validation_independence field for every
> validation; for RESULT-0021 the replay was performed via a second
> account of the same maintainer (same_owner_different_account), not by an
> independent contributor. Independent-contributor replays are tracked in
> the repository and can accumulate over time; see
> docs/result-promotion-protocol.md ("Validation Independence") in the
> repository for the exact semantics.

## Non-goals

- No dataset file change, no new version DOI, no change to the quoted
  benchmark numbers or the no-claim wording already in the record.
- Do not remove or reword existing description content; append only.
