# Nuclear Reveal Source Readiness Checklist

## Purpose

This checklist turns the nuclear prediction reveal protocol into a
maintainer-facing gate for future real measurement-source comparison tasks. It
defines what a reveal task must pin before any registered nuclear-mass
prediction is compared with a later source.

This is a readiness artifact only. It does not fetch live nuclear data, add
real source rows, score predictions, edit frozen `PRED-*` entries, or unblock a
future reveal task automatically.

Use it with:

- [Nuclear Prediction Reveal Protocol](./nuclear-prediction-reveal-protocol.md)
- [Nuclear Prediction Registry Status After PRED-0062](./reviews/nuclear-prediction-registry-status-after-pred-0062.md)
- [Nuclear Prediction Registry Coverage Audit](./reviews/nuclear-prediction-registry-coverage-audit.md)
- [Nuclear Prediction Synthetic Reveal Dry-Run](./reviews/nuclear-prediction-synthetic-reveal-dry-run.md)

The synthetic reveal dry-run is workflow plumbing only. Its fabricated toy
values are not measurement evidence and must not be cited as reveal support.

## Required Source Manifest Fields

A future real reveal task must include a source manifest before comparison.
The manifest should be committed or referenced by immutable archive metadata
before the reveal executor sees row-level values.

| Field | Required content | Gate reason |
| --- | --- | --- |
| `manifest_id` | Stable id for the manifest. | Lets review notes and comparison tables cite the exact source gate. |
| `task_id` | Canonical reveal task id. | Ties the source gate to a reviewed work item. |
| `source_class` | Source category such as `official_evaluation`, `peer_reviewed_table`, `collaboration_release`, or `archive_copy`. | Prevents mixing source types without review. |
| `source_title` | Human-readable title of the source. | Makes the source auditable without relying on file names. |
| `issuing_body` | Organization, collaboration, journal, or archive owner. | Records source authority and provenance. |
| `publication_or_release_date` | Date the source became publicly available. | Needed for no-peek and predate checks. |
| `source_state_timestamp_utc` | UTC timestamp when the source was pinned for the reveal task. | Freezes source-state timing before scoring. |
| `accessed_at_utc` | UTC access timestamp if externally retrieved. | Separates source release timing from local retrieval timing. |
| `source_locator` | DOI, release page, archive URI, repository URL, or local pinned-copy path. | Lets reviewers retrieve or inspect the same source. |
| `license_or_reuse_notes` | Reuse terms or a note that terms are unknown. | Avoids accidentally committing restricted raw files. |
| `archive_policy` | `committed_copy`, `external_archive_with_checksum`, or `manifest_only_with_retrieval_instructions`. | Explains how reproducibility is preserved. |
| `raw_artifact_checksum` | Hash algorithm and digest, or an explicit `not_committed` reason. | Detects source drift. |
| `normalized_artifact_checksum` | Hash for any parsed row-level table used for comparison. | Detects parser or normalization drift. |
| `parser_or_normalizer` | Script path, command, version, and input/output paths, if parsing is used. | Makes row generation reproducible. |
| `quantity` | Quantity being compared, currently expected as `mass_excess_mev` unless a reveal task says otherwise. | Prevents unit or observable mismatches. |
| `units` | Source units and normalized units. | Makes conversions reviewable. |
| `uncertainty_fields` | Field names, units, and semantics for uncertainties. | Allows uncertainty-normalized metrics only when trusted. |
| `value_semantics` | Whether rows are measured, evaluated, extrapolated, derived, or mixed. | Prevents non-measured values from being scored accidentally. |
| `measurement_flag_field` | Row-level flag that separates measured from non-measured values. | Required for eligibility screening. |
| `target_id_fields` | Nuclide matching fields such as `symbol`, `Z`, `N`, `A`, and optional isomer state. | Prevents ambiguous target joins. |
| `target_matching_rules` | Deterministic matching rules, including isotope naming and duplicate handling. | Avoids ad hoc row selection during scoring. |
| `exclusion_policy` | How ambiguous units, non-measured-only rows, repeated rows, and missing targets are labeled. | Keeps negative or incomplete outcomes visible. |
| `reviewer_notes` | Known limitations, source caveats, and required follow-up. | Keeps the final reveal interpretation bounded. |

If any required field is missing or ambiguous, the reveal task should stop at
source-readiness review. It may still produce a blocked or inconclusive review
note, but it must not score prediction entries.

## Source Pinning And Checksums

Before comparison, a reveal task must choose one of these reproducibility
policies:

| Policy | Allowed when | Required evidence |
| --- | --- | --- |
| `committed_copy` | The source license and size allow committing raw or normalized files. | Raw file path, normalized file path if any, hash algorithm, digest, and parser command. |
| `external_archive_with_checksum` | The source is immutable or archived but cannot be committed. | Immutable locator, retrieval instructions, source-state timestamp, checksum, and reviewer access note. |
| `manifest_only_with_retrieval_instructions` | The source cannot be archived locally and the maintainer accepts that limit. | Stable locator, exact retrieval instructions, reason a pinned copy is absent, and explicit reproducibility limitation. |

Checksum records should include file size and hash algorithm. If parsing
produces a normalized table, checksum both the raw source and normalized output.
Do not compute reveal metrics from a file whose checksum has not been reviewed.

## No-Peek Audit Checklist

Run the no-peek audit after source pinning and before scoring.

For each included `PRED-*` entry, reviewers must check:

- the entry `registered_at_utc` predates `publication_or_release_date`;
- the entry `source_state.git_commit` predates the pinned measurement source;
- no post-registration edit changed prediction values, target rows, model
  state, or reveal conditions;
- the target was absent from committed training, baseline, source manifests, or
  holdout files at registration time unless the reveal task declares a weaker
  retrospective evidence class;
- task, PR, and review notes do not show that row-level revealed values were
  inspected before registration;
- target batches were not modified after source discovery to fit revealed
  rows;
- candidate selection did not use the source or a derivative of the source;
- public wording still describes entries as prospective and unvalidated before
  reveal scoring.

Recommended no-peek outcomes:

| Status | Meaning |
| --- | --- |
| `NO_PEEK_PASS` | Timing and history checks support prospective comparison. |
| `NO_PEEK_WEAK` | Comparison may proceed only as a weaker diagnostic with explicit limitations. |
| `NO_PEEK_FAIL` | Do not describe the comparison as prospective reveal evidence. |
| `NO_PEEK_INCONCLUSIVE` | Block scoring or mark the reveal inconclusive until review resolves the ambiguity. |

## Eligibility And Exclusion Labels

The reveal artifact must keep scored, unscored, and excluded rows in one table.
Use explicit labels so negative and incomplete outcomes remain visible.

| Label | Use when |
| --- | --- |
| `ELIGIBLE_MEASURED` | Source row is measured, unit conversion is deterministic, and no-peek passes. |
| `TARGET_NOT_REVEALED` | The target has no row in the pinned source. |
| `NON_MEASURED_VALUE_ONLY` | The target appears only as evaluated, extrapolated, derived, or otherwise non-measured when the task requires measured rows. |
| `SOURCE_PREDATES_REGISTRATION` | Source availability is earlier than the registry entry timestamp. |
| `REGISTRY_MUTATED_AFTER_SOURCE` | A relevant prediction field changed after the source became available. |
| `UNIT_SEMANTICS_AMBIGUOUS` | Quantity, units, uncertainty, or conversion semantics are not reviewable. |
| `TARGET_MATCH_AMBIGUOUS` | Nuclide identity, isomer state, duplicate rows, or matching rules are unclear. |
| `NO_PEEK_AUDIT_FAILED` | Timing or history review fails the no-peek gate. |
| `SOURCE_MANIFEST_INCOMPLETE` | Required manifest or checksum fields are missing. |

Only `ELIGIBLE_MEASURED` rows may be scored in a measured-only reveal. A future
task may define another accepted value class, but it must do so before source
inspection and keep the weaker evidence class explicit.

## Partial-Reveal Handling

Partial reveal is expected. A future source may include only some registered
targets or may include many repeated rows for a small set of nuclides.

Rules:

- score only eligible rows from the pinned source;
- preserve unrevealed target rows unchanged and unscored;
- report coverage as both target-row coverage and unique-nuclide coverage;
- report repeated-target pressure separately from broad target coverage;
- keep high-reuse target batches visible as review flags, not automatic
  failures;
- do not average repeated target rows as if they were independent breadth;
- do not fill missing rows from live, informal, or unpinned sources;
- do not rank registry families by partial coverage alone;
- keep unrevealed rows eligible for a later reveal unless no-peek or source
  timing fails.

For high-reuse rows identified by the coverage audit, including `Ni-76`,
`Ca-55`, `Ga-85`, and `Zn-80`, the reveal artifact should show:

- number of registry entries touching the nuclide;
- source availability status;
- measured versus non-measured status;
- whether repeated rows are sign-paired, model-paired, or target-batch reuse;
- whether a single measured target dominates the reported metric.

For high-reuse target batches such as `frontier-next-row` and
`nickel-isotope-chain`, report batch coverage and unique-nuclide coverage
separately.

## Readiness Decision

A source-readiness review may return:

| Decision | Meaning |
| --- | --- |
| `READY_FOR_REVEAL_TASK` | Manifest, checksums, no-peek plan, target matching, and partial-reveal policy are complete. |
| `READY_WITH_LIMITATIONS` | Comparison may proceed with explicit weaker evidence limits. |
| `BLOCKED_SOURCE_NOT_PINNED` | Source provenance, archive policy, or checksums are incomplete. |
| `BLOCKED_NO_PEEK_AUDIT` | Timing or history review prevents prospective interpretation. |
| `BLOCKED_VALUE_SEMANTICS` | Measured, evaluated, extrapolated, or derived source rows cannot be separated. |
| `INCONCLUSIVE_ZERO_ELIGIBLE_TARGETS` | Source is pinned but no target rows are eligible for scoring. |

This readiness decision is not a scientific verdict. It only states whether a
future comparison task is allowed to proceed and under what limitations.

## Future Reveal Handoff Checklist

Before any real reveal scoring command runs:

- [ ] Canonical reveal task exists and explicitly allows comparison.
- [ ] Source manifest is complete and reviewed.
- [ ] Raw and normalized checksums are recorded, or the archive limitation is
      explicitly accepted.
- [ ] Registry snapshot commit and included `PRED-*` ids are recorded.
- [ ] No frozen prediction values or target rows are edited in the reveal PR.
- [ ] No-peek audit status is recorded per included prediction entry.
- [ ] Target matching rules are deterministic.
- [ ] Measured, non-measured, and ambiguous rows are separated.
- [ ] Partial-reveal coverage reporting is defined before scoring.
- [ ] Synthetic dry-run artifacts are cited only as plumbing tests.
- [ ] Claim promotion is explicitly out of scope.

After reveal scoring, the review note must still preserve excluded rows,
negative outcomes, sparse-coverage limits, and any no-peek weaknesses. Claim or
result promotion requires a separate maintainer-reviewed task.
