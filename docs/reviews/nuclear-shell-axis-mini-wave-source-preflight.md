# Nuclear Shell-Axis Mini-Wave Source Preflight

**Task:** TASK-0303
**Status:** preflight review (no source pinned, no values fetched, no reveal scored)
**Target batch:** `shell-axis-balanced-001`
**Registry entries under review:** `PRED-0063` through `PRED-0068`
**Inputs reviewed:**

- `prediction_registry/nuclear_masses/PRED-0063.yaml`
- `prediction_registry/nuclear_masses/PRED-0064.yaml`
- `prediction_registry/nuclear_masses/PRED-0065.yaml`
- `prediction_registry/nuclear_masses/PRED-0066.yaml`
- `prediction_registry/nuclear_masses/PRED-0067.yaml`
- `prediction_registry/nuclear_masses/PRED-0068.yaml`
- `docs/reviews/nuclear-shell-axis-prospective-mini-wave-review.md`
- `docs/nuclear-prediction-reveal-protocol.md`
- `docs/nuclear-reveal-source-readiness-checklist.md`
- `docs/blind-holdout-benchmark-protocol.md`
- `docs/campaigns/nuclear-mass-surface.md`

## Scope

This preflight identifies source readiness for a future reveal of the
`shell-axis-balanced-001` mini-wave (`PRED-0063`..`PRED-0068`). It does
not pin any external source, does not fetch any nuclear-mass dataset,
does not record measured `mass_excess` values for the eight target
nuclides, does not compute reveal metrics, and does not unblock
`TASK-0305` or any successor real-reveal task.

The preflight artifact has two outputs:

1. this review note, documenting plausible source classes, source-manifest
   requirements, archive/checksum expectations, no-peek evidence,
   classification labels, and stop conditions;
2. a template at
   `data/nuclear_masses/shell_axis_reveal_source_manifest_template.yaml`
   that a future reveal task must populate before any row-level inspection.

## Frozen Registry Boundary

| Entry | Role | Frozen family | Origin family id |
| --- | --- | --- | --- |
| `PRED-0063` | primary candidate | proton-axis Gaussian | `STRESS-SHELL-001` |
| `PRED-0064` | companion candidate | proton x neutron product | `STRESS-SHELL-002` |
| `PRED-0065` | diagnostic candidate | neutron-axis Gaussian | `STRESS-SHELL-003` |
| `PRED-0066` | negative control | sign-inverted proton-axis Gaussian | `STRESS-SHELL-004` |
| `PRED-0067` | negative control | near-null shell-axis correction | `STRESS-SHELL-006` |
| `PRED-0068` | reference control | frozen baseline reference | `RESULT-0015::model_fitted_semi_empirical` |

Eight target nuclides per entry, frozen as `mass_excess_mev` in `MeV` with
`uncertainty_mev: null` throughout:

| Nuclide | Z | N | A |
| --- | ---: | ---: | ---: |
| `V-70` | 23 | 47 | 70 |
| `Mn-75` | 25 | 50 | 75 |
| `Co-77` | 27 | 50 | 77 |
| `Cu-81` | 29 | 52 | 81 |
| `Ag-129` | 47 | 82 | 129 |
| `Cd-130` | 48 | 82 | 130 |
| `Sb-135` | 51 | 84 | 135 |
| `Cs-139` | 55 | 84 | 139 |

Source commit at registration: `9e8d7d339a4f0f432e41689862a649eb029b8575`.
This commit is the no-peek boundary used in every audit check below.

## Candidate Source Classes

The reveal task must choose a source whose class matches the readiness
checklist taxonomy. The classes below are reviewed source-class candidates
only. No specific external publication, edition, release, table, file
locator, or measured value is recorded here.

### Class A — Official nuclear-mass evaluation

A new or updated official nuclear-mass evaluation released after the
registration commit. Source-class label: `official_evaluation`.

Required source-manifest fields:

- `source_class: official_evaluation`;
- `source_title`, `issuing_body`, `publication_or_release_date`;
- `source_locator` (DOI, release page, or pinned archive path);
- `license_or_reuse_notes` with explicit reuse terms;
- `archive_policy` chosen from `committed_copy`,
  `external_archive_with_checksum`, or `manifest_only_with_retrieval_instructions`;
- `raw_artifact_checksum` and (if normalised)
  `normalized_artifact_checksum`;
- `parser_or_normalizer` script path, command, version, and inputs;
- `quantity: mass_excess_mev`, `units`, and `uncertainty_fields`;
- `value_semantics` declaring whether rows are measured, evaluated,
  extrapolated, derived, or mixed;
- `measurement_flag_field` identifying the row-level flag that separates
  measured from non-measured entries.

Why this class is plausible: nuclear-mass evaluations include
row-level `measured` vs `extrapolated` flags directly, which is the
required separation under the readiness checklist.

Why this class is not automatic: the reveal executor must still verify
each individual target row against the `value_semantics` field before
scoring. Several target nuclides in `shell-axis-balanced-001` lie in
regions where official evaluations historically use extrapolated rather
than measured values; those rows must be labelled `NON_MEASURED_VALUE_ONLY`
even when the source itself is officially endorsed.

### Class B — Peer-reviewed primary mass-measurement publication

A peer-reviewed publication or supplementary table reporting direct mass
measurements (Penning trap, storage ring, MR-TOF, etc.) for one or more
of the eight target nuclides. Source-class label: `peer_reviewed_table`.

Required source-manifest fields:

- `source_class: peer_reviewed_table`;
- per-row attribution to the specific publication;
- `value_semantics: measured` with explicit measurement method recorded
  in `reviewer_notes`;
- `target_matching_rules` resolving any nuclide naming or isomer-state
  ambiguity (V-70 ground state vs isomers; high-Z isotopes with
  long-lived isomers may need explicit handling);
- a manifest-level note that multiple peer-reviewed publications must not
  be silently averaged; each row should attribute its primary source.

### Class C — Collaboration data release

A collaboration-led data release (lab consortium, evaluation working
group, working data tables) containing measured mass values published
under a documented reuse policy. Source-class label:
`collaboration_release`.

Same required fields as Class B, plus:

- explicit `license_or_reuse_notes` because collaboration releases
  sometimes carry restricted reuse;
- `archive_policy: external_archive_with_checksum` or
  `manifest_only_with_retrieval_instructions` when the release cannot be
  redistributed.

### Class D — Archive copy of a measured table

A pinned archive copy (institutional repository, persistent identifier
archive) of a table already published as Class A, B, or C. Source-class
label: `archive_copy`.

This is acceptable only as a reproducibility mirror; the primary class
must still be Class A, B, or C, and the archive copy's checksum must be
recorded in `raw_artifact_checksum`.

### Excluded classes

- live web fetches without an archive policy;
- chat-derived, blog-derived, or social-media-derived tables;
- aggregator websites that do not expose row-level provenance;
- LLM-recalled values for any of the eight target nuclides;
- model-derived or theory-only predictions presented as measurements;
- mass tables that do not separate measured from extrapolated rows.

A reveal task that finds only an excluded source must stop and label the
preflight outcome `BLOCKED_VALUE_SEMANTICS` per the readiness checklist.

## Source-Manifest Field Requirements

The template at
`data/nuclear_masses/shell_axis_reveal_source_manifest_template.yaml`
mirrors the readiness checklist field list. Every `TBD_*` placeholder
must be filled before the reveal executor sees any row-level value.

Hard requirements for the shell-axis-balanced-001 reveal:

- `quantity` must be `mass_excess_mev`. A source that reports only
  binding energy, atomic mass, or kinetic-energy difference must be
  normalised to `mass_excess_mev` via a reviewed parser, with the
  conversion factor recorded.
- `units` must declare both the source unit and the normalised unit. If
  the source uses `keV`, the conversion factor `1e-3` must be recorded.
- `uncertainty_fields` must declare semantics (1σ, k=1, k=2, or other).
  Mixed uncertainty semantics across sources is forbidden.
- `measurement_flag_field` is mandatory. A source without a row-level
  measured/non-measured flag cannot be used in a measured-only reveal.

## Archive And Checksum Expectations

The reveal task must declare one of three archive policies before
inspection:

| Policy | When allowed | Required evidence |
| --- | --- | --- |
| `committed_copy` | License and size both allow committing raw or normalized files. | raw and normalised file paths, hash algorithm, digest, parser command, file bytes. |
| `external_archive_with_checksum` | Source is immutable or archived but cannot be redistributed locally. | persistent locator, retrieval instructions, source-state timestamp, hash, reviewer access note. |
| `manifest_only_with_retrieval_instructions` | Source cannot be archived locally and the maintainer accepts the limit. | stable locator, exact retrieval instructions, reason a pinned copy is absent, explicit reproducibility limitation. |

Reveal scoring is forbidden against a file whose checksum has not been
reviewed under one of the three policies. If a parser normalises rows,
both the raw and the normalised checksum are required.

## No-Peek Evidence For shell-axis-balanced-001

Each `PRED-0063`..`PRED-0068` entry already records the same
`source_state.git_commit` and the same `target_batch_label`. That makes
the no-peek audit easier than for heterogeneous registry slices, but the
reveal executor must still verify the following per entry before the
source is inspected:

1. `registered_at_utc` predates the source's `publication_or_release_date`.
   Every shell-axis-balanced-001 entry currently records
   `registered_at_utc: 2026-05-20T00:00:00Z`.
2. `source_state.git_commit` predates the source's
   `source_state_timestamp_utc`. The committed value is
   `9e8d7d339a4f0f432e41689862a649eb029b8575`.
3. No post-registration edit changed `predicted_value_mev`,
   `target_nuclides`, `source_state`, `reveal_conditions`, or
   `claim_ceiling`. The shell-axis-balanced-001 target list and
   per-entry prediction values must remain byte-identical to the values
   in this preflight's "Frozen Registry Boundary" table.
4. The eight target nuclides were absent from committed training,
   baseline, source-manifest, and holdout files at registration time
   except as already-disclosed `training_data_references` (currently
   `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`). The
   reveal task should re-verify against the committed snapshot at the
   registration commit.
5. No task, PR, review note, or commit message authored before the
   reveal task inspected any measured `mass_excess` value for the eight
   target nuclides. The preflight reviewer should grep the repository
   history at the registration commit for explicit numeric values
   adjacent to the nuclide ids; an exact-match find is grounds for
   marking the no-peek audit failed.
6. The target batch was not modified after source discovery. The
   `target_batch_label: shell-axis-balanced-001` field must be byte-
   identical between the design document at TASK-0296 closeout, the
   review at TASK-0297, this preflight, and the future reveal task.
7. Candidate selection did not use the source or a derivative of the
   source. The shell-axis evidence basis is the deterministic factory
   stress family `STRESS-SHELL-001`..`STRESS-SHELL-006`; the source must
   be reviewed only as a comparator, never as a selection input.
8. Public wording at the reveal still describes shell-axis-balanced-001
   as prospective and sandbox-grade until scoring. The future reveal
   review note must echo the existing "Limitations" section of the
   TASK-0297 mini-wave review.
9. Paired controls `PRED-0066` (sign-inverted) and `PRED-0067` (near-null)
   plus the `PRED-0068` reference baseline must be reported alongside any
   candidate-row score. A reveal artifact that drops the controls is
   not a legitimate reveal of this mini-wave.

If any of (1)–(9) fail, the reveal preflight returns
`NO_PEEK_FAIL` or `NO_PEEK_INCONCLUSIVE` and TASK-0305 stays blocked
until the maintainer resolves the ambiguity.

## Per-Target Classifications Without Scoring

The reveal task will encounter target rows that fall into different
classifications. The preflight defines the vocabulary the reveal task
must apply per target, without recording any actual measured value here.

| Class | Use when |
| --- | --- |
| `ELIGIBLE_MEASURED` | Row exists in the pinned source with `value_semantics: measured`, unit conversion is deterministic, and the no-peek audit passes. |
| `TARGET_NOT_REVEALED` | The target has no row in the pinned source. |
| `NON_MEASURED_VALUE_ONLY` | The target appears only as evaluated, extrapolated, derived, or otherwise non-measured. |
| `SOURCE_PREDATES_REGISTRATION` | The source's publication or release date is earlier than the entry's `registered_at_utc`. |
| `REGISTRY_MUTATED_AFTER_SOURCE` | A relevant prediction field changed after the source became available. |
| `UNIT_SEMANTICS_AMBIGUOUS` | Quantity, units, uncertainty, or conversion semantics cannot be reviewed. |
| `TARGET_MATCH_AMBIGUOUS` | Nuclide identity, isomer state, duplicate rows, or matching rules are unclear. |
| `NO_PEEK_AUDIT_FAILED` | Timing or history review fails the no-peek gate. |
| `SOURCE_MANIFEST_INCOMPLETE` | Required manifest or checksum fields are missing. |

The reveal artifact must label every target row with exactly one class.
The preflight does not predict which class any individual target will
receive; predicting the class would be a peek.

Per-target reasoning for what to expect about availability without
peeking at values:

- **V-70 (Z=23, N=47, A=70)** — proton-rich vanadium isotope; expected to
  appear with rather large uncertainty in evaluations; class to be
  decided per source.
- **Mn-75 (Z=25, N=50, A=75)** — N=50 shell-closure neutron-rich; class
  to be decided per source.
- **Co-77 (Z=27, N=50, A=77)** — N=50 shell-closure neutron-rich; class
  to be decided per source.
- **Cu-81 (Z=29, N=52, A=81)** — neutron-rich copper near the N=50 shell;
  class to be decided per source.
- **Ag-129 (Z=47, N=82, A=129)** — N=82 shell-closure neutron-rich;
  class to be decided per source.
- **Cd-130 (Z=48, N=82, A=130)** — N=82 shell-closure neutron-rich;
  class to be decided per source.
- **Sb-135 (Z=51, N=84, A=135)** — N=84 above shell closure; class to be
  decided per source.
- **Cs-139 (Z=55, N=84, A=139)** — N=84 above shell closure; class to be
  decided per source.

Recording a specific measured value or a "very likely measured"
expectation for any of these eight nuclides would weaken the no-peek
boundary and is intentionally avoided.

## Stop Conditions

The preflight reviewer must stop and report that TASK-0305 must remain
blocked when any of the following holds:

- **Source inspection cannot avoid exposing target rows.** If the only
  way to verify Class A/B/C metadata is to read the full table in a
  format that simultaneously reveals row-level measured values for any
  of the eight target nuclides, the inspection is itself a peek and the
  reveal task is blocked.
- **A source-discovery script needs to be written that loads the source
  into memory.** The preflight may describe what such a script should
  look like, but it must not run a script that loads measured values for
  the target rows.
- **The maintainer has not yet approved the reveal task by id.** The
  reveal-readiness checklist is satisfied as planning, but the executor
  needs a maintainer-approved successor task (TASK-0305 or named
  equivalent) before any row is read.
- **Required manifest fields are unfilled.** A `TBD_*` placeholder
  remaining in the manifest template at reveal time means
  `SOURCE_MANIFEST_INCOMPLETE` and stops scoring.
- **Paired-control coverage is missing.** Any reveal artifact that
  reports `PRED-0063`, `PRED-0064`, or `PRED-0065` without the matching
  `PRED-0066` (sign-inverted), `PRED-0067` (near-null), and `PRED-0068`
  (baseline reference) controls is rejected.

Each stop returns one of the readiness-checklist outcomes:
`BLOCKED_SOURCE_NOT_PINNED`, `BLOCKED_NO_PEEK_AUDIT`,
`BLOCKED_VALUE_SEMANTICS`, or `INCONCLUSIVE_ZERO_ELIGIBLE_TARGETS`. The
preflight does not promote the mini-wave from sandbox to claim under
any of these outcomes.

## Partial-Reveal Pre-Commitments

The future reveal must:

- score only `ELIGIBLE_MEASURED` rows from the pinned source;
- preserve unrevealed target rows unchanged and unscored;
- report coverage as both target-row coverage and unique-nuclide
  coverage;
- preserve paired controls alongside any candidate row score;
- never average repeated target rows as if they were independent
  breadth;
- never fill missing rows from live, informal, or unpinned sources;
- never rank registry families by partial coverage alone.

These commitments are recorded in the manifest template under
`partial_reveal_handling`.

## What This Preflight Did Not Do

- It did not pin any external nuclear-mass source.
- It did not fetch, download, or read any external measurement table.
- It did not record measured `mass_excess` values for `V-70`, `Mn-75`,
  `Co-77`, `Cu-81`, `Ag-129`, `Cd-130`, `Sb-135`, or `Cs-139`.
- It did not edit `PRED-0063`..`PRED-0068`.
- It did not score, partial-reveal, or rank any registry family.
- It did not unblock `TASK-0305` or promote any sandbox evidence.
- It did not update or rewrite the existing reveal protocol or readiness
  checklist documents.

## Limitations

- The list of source classes is review-level guidance, not a maintainer
  pre-approval of any specific source.
- The per-target reasoning is intentionally limited to nuclide identity
  and shell-region context; no measured value or "expected" class is
  recorded.
- The manifest template uses `TBD_*` placeholders deliberately; any
  reveal task that copies the template forward must replace every
  placeholder before scoring.
- The preflight does not estimate how many of the eight target nuclides
  will end up `ELIGIBLE_MEASURED` under any specific source. Estimating
  that figure before the reveal is itself a peek and is therefore
  intentionally avoided.

## Verdict

`PARTIALLY_VALID` for source-readiness planning. The preflight defines
the source-class options, manifest field requirements, archive and
checksum policies, no-peek evidence, classification labels,
partial-reveal pre-commitments, and stop conditions that a future
reveal task must satisfy. It does not by itself unblock the reveal; the
reveal task (TASK-0305 or successor) still needs maintainer approval
and a real pinned source.
