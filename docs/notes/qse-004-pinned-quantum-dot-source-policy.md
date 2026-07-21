# QSE-004 Pinned Quantum-Dot Source Policy Note

**Run:** `MICROTASK-RUN-0038`
**Verdict:** `REVIEW_NEEDED`

## Scope

This note condenses the existing Quantum Size Effects intake rules into a
pre-benchmark checklist. The canonical policy remains
`docs/quantum-direct-source-artifact-intake.md`; this note does not weaken or
replace it, approve a source, curate a row, or authorize a benchmark.

## Pinning Rule

A published quantum-dot size-property value must not enter a `qd-*.yaml` file
or benchmark surface until its source is registered in
`data/quantum_dots/source_manifest.yaml` and its exact evidence route is
reviewable at commit time. Silent ingestion of unpinned data is disallowed.
A live URL or successful live fetch is not a substitute for a pinned source
identity and version record.

## Required Pre-Benchmark Record

The source-artifact package must preserve all thirteen canonical intake fields:

1. `source_id`, title, authors, and publication year;
2. DOI or equivalent persistent identifier;
3. exact access path and ISO-8601 retrieval date;
4. artifact type and exact version or upstream filename;
5. full SHA-256 checksum, or an explicit `PENDING` metadata-only blocker;
6. license and redistribution decision;
7. material family and property kind;
8. expected row/evidence class.

The compact groups above do not reduce the canonical field count. They make
the following provenance questions explicit before row use:

- **Identity:** which version-of-record publication or dataset is meant?
- **Bytes:** which exact file was inspected, and what checksum binds it?
- **Rights:** may bytes, tables, figures, or only metadata be committed?
- **Semantics:** is the property absorption peak, emission peak, bandgap, or
  band edge, and is size diameter, radius, edge length, volume, or equivalent
  diameter?
- **Lineage:** which table, figure, text statement, supplement, or deterministic
  extraction record produced each row?
- **Evidence class:** is the row `table_derived`, `digitization_required`,
  `text_stated_summary` under an approved contract, calibration-derived, or
  blocked?

## Version And Change Control

- A changed source file, supplement, repository version, or corrected edition
  receives a new checksum and an explicit supersession note; old provenance is
  not overwritten silently.
- DOI-only or metadata-only records remain blockers for row curation when the
  accepted evidence requires unavailable bytes.
- A row must retain its `source_id`, property kind, size-axis semantics, source
  table/figure/text locator, and derivation mode so later metric code cannot
  erase provenance differences.
- Absorption, emission, and bandgap values remain separate target surfaces even
  when they come from the same paper or sample.

## Stop Conditions

Do not ingest or benchmark a value when any of these is unresolved:

- ambiguous source version, missing stable locator, or missing manifest entry;
- unknown rights or redistribution posture;
- missing checksum where source bytes are required;
- property-kind or size-axis ambiguity;
- undocumented table, figure, text, calibration, or transformation lineage;
- an attempt to infer provenance after values have already been pooled; or
- a live-fetch result proposed as a replacement for committed pinning metadata.

## Review Criteria And Limitations

The note passes its microtask criteria by naming more than three provenance
fields and explicitly forbidding silent unpinned ingestion. It is still
`REVIEW_NEEDED` because maintainers decide whether a concrete source and its
rights/evidence class satisfy the canonical intake contract.

No source bytes or values were opened, fetched, copied, or changed. No dataset,
split, metric, `RESULT`, `CLAIM`, or `KNOW` artifact is created. The checklist
does not imply that a quantum-dot source is scientifically suitable merely
because its metadata is complete.

## Output Routing

- Destination: this planning note and `MICROTASK-RUN-0038`.
- Gate A / Gate B: not attempted.
- Claim and knowledge impact: none.
- Publication blocker: concrete source acceptance remains maintainer-reviewed
  under the canonical intake policy.
