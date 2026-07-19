# Nuclear Prediction Reveal Protocol

## Purpose

This protocol defines how a future reviewed task may compare frozen
nuclear-mass prediction registry entries against later measured data.

It is a narrow reveal-readiness checklist for
`prediction_registry/nuclear_masses/`. It extends the boundary already defined
by [Prediction Registry Policy](./prediction-registry-policy.md) and
[Blind Holdout Benchmark Protocol](./blind-holdout-benchmark-protocol.md);
it does not replace either document.

Shared cross-surface rule: source admissibility scouting for ANY sealed
prediction surface is governed by
[Prospective Reveal Source Admissibility](./prospective-reveal-source-admissibility.md)
(official-metadata-only discovery, no search-result snippets, manifest before
target matching, values only in an approved reveal task, contamination =>
`BLOCKED_NO_PEEK_AUDIT` + clean-session retry). This protocol adds the
domain-specific layer on top of that policy.


The goal is to preserve an auditable before/after boundary:

- predictions are frozen before later measurements are reviewed;
- measurement sources are pinned before comparison;
- no-peek state is checked before any scoring;
- partial reveals are recorded without rewriting unrevealed targets;
- negative, null, or inconclusive outcomes remain visible.

## Scope

Use this protocol only for prospective nuclear-mass prediction entries under:

```text
prediction_registry/nuclear_masses/PRED-XXXX.yaml
```

The protocol applies when a canonical task explicitly asks to reveal or compare
registered predictions against a reviewed source that became available after
the relevant registry timestamps.

It does not apply to:

- retrospective post-AME2020 time-split benchmarks;
- sandbox feature-term slates;
- pre-reveal registry selection work;
- broad claim promotion;
- rewriting prediction values after registration.

## Forbidden In This Protocol-Definition Task

`TASK-0266` defines the protocol only. It must not:

- fetch live external measurements;
- pin a new measured dataset;
- compare registry entries against measurements;
- compute reveal scores;
- create canonical result artifacts;
- promote claims or accepted knowledge;
- modify frozen `PRED-*.yaml` values or reveal conditions.

Future reveal work must be a separate maintainer-reviewed task with its own
source manifest, checksum record, comparison artifact, and review boundary.

## Roles

| Role | Responsibility |
| --- | --- |
| Maintainer | Approves the reveal task, accepted source class, registry snapshot, and final wording boundary. |
| Source curator | Pins reviewed measurement sources, checks licenses and provenance, records checksums, and separates measured from extrapolated values. |
| Reveal executor | Runs the approved comparison command without changing frozen registry entries or source inputs. |
| Reviewer | Audits no-peek state, reproducibility, partial reveal handling, metrics, limitations, and negative-result wording. |

A small task may combine roles, but the artifacts must make each step
reviewable.

## Stepwise Reveal Workflow

### 1. Create Or Reference A Reveal Task

The task must state:

- registry entries or registry range under review;
- accepted measurement source class;
- whether partial reveal is allowed;
- comparison units and value semantics;
- required metrics;
- output paths for source manifest, comparison table, and review note;
- explicit prohibition on claim promotion.

The task should reference this protocol, the prediction registry policy, and
the blind-holdout benchmark protocol.

### 2. Discover Candidate Measurement Sources

Source discovery is not scoring. Before comparison, record:

- source title and version;
- issuing organization or collaboration;
- publication or release date;
- access date if fetched externally;
- whether values are measured, evaluated, extrapolated, or mixed;
- license or reuse notes when available;
- whether the source existed before each registry timestamp.

If source status is ambiguous, stop and mark the reveal task blocked or
inconclusive. Do not compare against an ambiguous source and clean it up later.

### 3. Pin Source Files And Checksums

Before any registry comparison, pin the exact source artifacts:

- raw source file or immutable source reference;
- normalized row-level dataset if parsing is needed;
- parser command and version;
- checksum file for raw and normalized artifacts;
- source manifest describing units and uncertainty fields.

If a source cannot be stored directly in the repository, store a manifest with
the immutable reference, retrieval instructions, checksums, and reviewer notes.

### 4. Freeze The Registry Snapshot

Record a registry snapshot before comparison:

- git commit used for the registry files;
- list of `PRED-XXXX` entries included;
- each entry's `registered_at_utc`;
- each entry's `source_state.git_commit`;
- target nuclides and prediction values;
- reveal conditions copied by reference, not rewritten;
- whether the entry was modified after the candidate source became available.

Frozen prediction entries must not be edited during reveal. If a metadata
correction is necessary, make a separate reviewed correction note and keep the
original before/after state visible.

### 5. Run Eligibility Screening

A registry entry is eligible only if:

- the prediction was registered before the reviewed measurement source was
  available to the project;
- the target nuclide appears in the pinned source with measured semantics or
  another task-approved value class;
- unit conversion is deterministic and documented;
- the target was not already present in committed training, baseline, or
  holdout datasets at registration time unless the entry explicitly declares a
  weaker evidence class;
- no post-registration edit changed the prediction value, target set, model
  state, or reveal rule.

Ineligible entries must stay in the reveal artifact with a reason such as:

- `SOURCE_PREDATES_REGISTRATION`
- `TARGET_NOT_REVEALED`
- `NON_MEASURED_VALUE_ONLY`
- `UNIT_SEMANTICS_AMBIGUOUS`
- `REGISTRY_MUTATED_AFTER_SOURCE`
- `NO_PEEK_AUDIT_FAILED`

### 6. Perform The No-Peek Audit

Before scoring, reviewers should check:

- task history and PR history for source exposure before registration;
- committed datasets and source manifests present at registration time;
- whether any candidate selection used the revealed values;
- whether target batches were altered after source discovery;
- whether prediction wording stayed pre-reveal and non-promotional.

If the no-peek audit fails, the comparison may still be useful as a
retrospective diagnostic, but it must not be described as prospective reveal
evidence.

### 7. Execute Comparison

The reveal executor may compare only eligible target rows from the frozen
registry snapshot against the pinned measured source.

The comparison table should include at minimum:

- prediction id;
- nuclide identifier, `Z`, `N`, and `A`;
- predicted value and unit;
- measured value and unit;
- uncertainty fields when available;
- signed error;
- absolute error;
- baseline or reference error when task-approved;
- eligibility status;
- exclusion reason for non-scored rows.

The command must be recorded exactly. Any deviation from the task-approved
command must be documented in the review note before interpretation.

### 8. Handle Partial Reveals

Partial reveal is expected when only some target nuclides receive reviewed
measurements.

Rules:

- score only eligible revealed targets;
- preserve unrevealed targets unchanged;
- do not fill missing targets from live, informal, or unpinned sources;
- report coverage as both count and target-list fraction;
- avoid ranking registry entries by partial coverage alone;
- keep unrevealed entries eligible for later reveal unless a no-peek violation
  or source-timing issue blocks them.

Partial reveal wording must say that the result covers only the revealed
subset and does not validate the full target list.

### 9. Report Metrics Conservatively

Allowed metrics include:

- target count and coverage fraction;
- signed error distribution;
- `MAE` and `RMSE` in `MeV`;
- uncertainty-normalized residuals only when uncertainty semantics are trusted;
- baseline-relative deltas only when the baseline value and unit conventions
  are frozen in the reveal task;
- per-target table for small reveal sets.

Do not convert a small partial reveal into broad model ranking. Do not infer a
new nuclear-mass law from reveal scores.

### 10. Preserve Negative And Inconclusive Outcomes

The reveal artifact must keep negative outcomes visible:

- high error;
- worse-than-baseline behavior;
- sign-instability;
- failed no-peek audit;
- ambiguous source semantics;
- zero eligible revealed targets;
- partial reveal too small for interpretation.

Recommended verdict vocabulary:

- `VALID_IN_RANGE`
- `PARTIALLY_VALID`
- `OVERFITTED`
- `INCONCLUSIVE`
- `INVALID`

For very small partial reveals, prefer `INCONCLUSIVE` unless the task defines a
stronger pre-registered decision rule.

## Required Artifacts For A Future Reveal Task

A reveal PR should include or reference:

- canonical reveal task file;
- source manifest with source class, dates, units, and measurement semantics;
- checksum record for raw and normalized artifacts;
- parser or normalization code reference when applicable;
- registry snapshot manifest;
- eligibility and no-peek audit note;
- comparison command;
- comparison table with scored and excluded rows;
- metrics summary;
- limitations and negative-result section;
- reviewer-facing wording boundary;
- explicit statement that claim promotion, if any, requires a later
  maintainer-reviewed claim or result task.

Recommended paths may be task-specific, but the following layout keeps the
audit trail discoverable:

```text
data/nuclear_masses/<source-name>_sources.yaml
data/nuclear_masses/<source-name>_checksums.md
docs/reviews/nuclear-prediction-reveal-<wave>.md
docs/reviews/nuclear-prediction-reveal-<wave>-comparison.md
```

## Wording Boundary

Allowed wording:

- "registered prospective prediction compared against a later pinned source"
- "partial reveal on N eligible targets"
- "reviewed measurement-source comparison"
- "inconclusive due to sparse reveal coverage"
- "negative reveal outcome preserved"

Forbidden wording:

- "proved"
- "confirmed" without a scoped verdict and maintainer-reviewed claim path
- "breakthrough"
- "discovered a nuclear mass law"
- "validated all targets" when only a partial reveal occurred
- "blind prediction" when the no-peek audit failed or source timing is weak

Registration and reveal comparison are not claim promotion. A later claim or
canonical result must pass its own review path.

## Checklist

Before reveal scoring:

- [ ] Reveal task is canonical and reviewed.
- [ ] Source manifest and checksum policy are approved.
- [ ] Registry snapshot is frozen.
- [ ] Eligibility rules are written down.
- [ ] No-peek audit is complete.
- [ ] Comparison command is recorded.
- [ ] Claim promotion is explicitly out of scope.

After reveal scoring:

- [ ] Comparison table includes scored and excluded rows.
- [ ] Partial reveal coverage is reported.
- [ ] Negative or inconclusive results are preserved.
- [ ] Limitations are written in scope-aware language.
- [ ] No frozen prediction values were rewritten.
- [ ] Any claim or result promotion is deferred to a separate maintainer task.

## Standing Prospective-Reveal Pipeline

### Why A Standing Pipeline

The single-shot reveal workflow above assumes a maintainer notices a qualifying
post-registration official release signal, opens a source-manifest decision,
and only later authorizes target matching and comparison. `TASK-1031` completed
a clean official-metadata-only scout and found only AME2020/NUBASE2020 records
that predate the `2026-05-20` registration boundary. It recorded no target value
or measured-status exposure and returned `SOURCE_PREDATES_REGISTRATION`.

Repeated availability scouts without a new official event add no evidence and
increase no-peek risk. The standing state is therefore
`MONITOR_ONLY_NO_SCOUT`, governed by the
[post-registration trigger ledger](./reviews/nuclear/nuclear-post-registration-reveal-trigger-ledger.md).
The ledger adds no scoring authority and relaxes no source, timing, checksum,
target-matching, or no-peek gate.

### Pipeline Stages

The pipeline has six ordered stages. No stage is recurring and no stage may be
skipped.

1. **Monitor only.** Remain `MONITOR_ONLY_NO_SCOUT`. Do not run scheduled
   availability checks or create a no-signal monitoring artifact.

2. **Record an official metadata signal.** A signal may enter only through a
   maintainer-provided direct official alert, an issuing-body notice encountered
   through normal project monitoring, or another directly locatable official
   repository/version/DOI record. Record only the trigger-ledger fields.

3. **Open a metadata-only manifest decision.** When stage 2 qualifies, open a
   fresh independent task to decide source identity, post-registration timing,
   source class, rights posture, immutable locator, and checksum feasibility.
   Do not download a payload, match targets, or inspect measured status.

4. **Pin and gate (single-shot, after manifest approval).** Only after the
   maintainer approves stage 3 may a separate task build the source manifest
   required by the
   [readiness checklist](./nuclear-reveal-source-readiness-checklist.md): all
   manifest fields, raw and normalized checksums, target-matching rules, and the
   no-peek audit (`NO_PEEK_PASS` / `NO_PEEK_WEAK` / `NO_PEEK_FAIL` /
   `NO_PEEK_INCONCLUSIVE`). This is "Discover Candidate Measurement Sources"
   through "Perform The No-Peek Audit" above. If the source cannot be pinned or
   the no-peek audit does not pass, the pipeline returns to
   `MONITOR_ONLY_NO_SCOUT`; it does not score.

5. **Score (single-shot, separately authorized).** Apply the existing
   `nuclear_prediction_reveal` workflow against the frozen prediction set — the
   **61 frozen PRED entries** under `prediction_registry/nuclear_masses/`
   (`PRED-0001` … the current registry head; see
   [registry coverage](./reviews/nuclear-prediction-registry-coverage-audit.md))
   — using only `ELIGIBLE_MEASURED` rows. This is "Execute Comparison" through
   "Preserve Negative And Inconclusive Outcomes" above: partial reveal is
   expected, only eligible revealed targets are scored, unrevealed targets are
   preserved unchanged, and negative or inconclusive outcomes stay visible.
   Verdict vocabulary and wording boundary are unchanged from this protocol.

6. **Return to monitor-only.** After a reveal wave, unscored and not-yet-revealed
   targets remain eligible for a later reveal unless a no-peek or source-timing
   failure blocks them. Update the watch manifest's coverage notes (counts and
   region status only, never values) and return to `MONITOR_ONLY_NO_SCOUT` for
   the regions still open.

### Reveal-Watch Manifest Concept

The reveal-watch manifest is a value-free planning surface stored at
`data/nuclear_masses/reveal_watch_manifest.yaml`. It is APL-authored planning
metadata, **not** a measurement dataset: it is not validated against the
nuclear-mass dataset schema and must never carry measured rows, so it is exempt
from the dataset entry-schema and from redistribution declaration.

The manifest records, for each watched program:

- a stable `program_id`, human-readable name, and facility or collaboration;
- the `source_class` from the
  [source-class scout](./reviews/nuclear-post-ame2020-reveal-source-scout.md)
  taxonomy (`official_evaluation`, `peer_reviewed_table`,
  `collaboration_release`, `archive_copy`, `secondary_compilation`);
- the admissibility posture for prospective reveal (`admissible_when_published`,
  `needs_maintainer_access`, `date_version_ambiguous`, `not_relevant`);
- a stable locator class (DOI root, portal URL, or edition page) — a *pointer*,
  not a fetched artifact;
- the nuclide regions to watch as `(Z, N)` ranges and optional named region
  labels, chosen to overlap the registered `PRED-*` target regions;
- value-free coverage and watch notes.

The manifest deliberately omits any measured value, any predicted value, any
metric, any per-nuclide measurement flag, and any reveal score. Listing only
program names and `(Z, N)` regions keeps it a planning artifact with no source
redistribution and no leakage surface.

The manifest is not a polling schedule. Agents must not traverse its programs,
regions, or target-adjacent locators unless a ledger-qualified official event
has first been recorded and a separate metadata-only manifest-decision task has
been approved.

### Event Trigger Condition

An event opens a fresh metadata-only source-manifest decision only when all of
the following are available without target search or payload access:

- a direct official issuing-body release notice, official repository/version
  record, or version-of-record DOI metadata;
- an identified issuer and source class;
- a publication or release date strictly after `2026-05-20`;
- a stable official locator plus version, edition, or DOI identity; and
- a value-free reason the event may contain post-registration nuclear-mass
  evaluation or primary measurement information.

The signal record must include observer, observation time, visibility route,
and a no-value-exposure attestation. Generic snippets, secondary summaries,
theory/model papers, unchanged AME2020/NUBASE2020 mirrors, ambiguous preprints,
target-name searches, and value-bearing previews are non-triggers.

This is an intake gate, not source admissibility approval. Immutable artifact
pinning, measured-separability, target overlap, and no-peek status are evaluated
only in the later reviewed stages. Failure or ambiguity returns the campaign to
`MONITOR_ONLY_NO_SCOUT`; it never authorizes scoring.

### Event-Triggered Monitoring

- **Standing state:** `MONITOR_ONLY_NO_SCOUT`.
- **No calendar trigger:** elapsed time, a monthly reminder, or a curator review
  interval does not authorize browsing or an availability-check task.
- **Allowed visibility:** a maintainer-provided direct official alert, an
  issuing-body notice encountered through normal project monitoring, or another
  directly locatable official metadata record.
- **First allowed action:** record the bounded metadata signal and request a
  fresh independent metadata-only source-manifest decision.
- **No automatic gated stage:** the event never auto-fetches, auto-pins,
  target-matches, opens values, or scores. Every later stage remains a separate
  maintainer-reviewed task.

### Do-Not-Do List

The standing pipeline must not, during monitoring or at any later stage:

- perform a live fetch of any measurement source from an executor task, or
  trigger such a fetch automatically from an official event;
- expose, transcribe, inspect, or commit any target measured value, predicted
  value, uncertainty, or reveal metric into the watch manifest;
- inspect target-row values while deciding source admissibility (admissibility
  is decided from publication metadata only);
- peek at revealed values before the registry snapshot and no-peek audit are
  complete, or use a revealed value to select candidates or edit target batches;
- edit, reorder, or re-time any frozen `prediction_registry/nuclear_masses/PRED-*.yaml`
  entry, its values, target set, model state, or reveal conditions;
- score against a source that predates registration, or describe a
  predates-registration or `NO_PEEK_FAIL` comparison as prospective reveal
  evidence;
- weaken or bypass any admissibility, checksum, measured-separability, or no-peek
  gate defined in this protocol or the readiness checklist;
- promote any claim, result, or knowledge entry from a watch check or a reveal
  wave; claim and result promotion remain separate maintainer-reviewed tasks.

### Monitor-Only Status

Until a ledger-qualified official signal exists, the pipeline state is
**`MONITOR_ONLY_NO_SCOUT`**:

- the event classes, evidence fields, non-triggers, stop rule, and ordered
  transition are pre-stated and reviewed;
- the frozen PRED entries and registry snapshot remain unchanged;
- no no-signal artifact or periodic scout is produced; and
- a qualifying signal advances only to a fresh metadata-only manifest decision,
  not directly to pinning, target matching, or scoring.

If target values or per-target measured status appear before manifest approval,
stop with `STOP_VALUE_EXPOSURE`, record no exposed content, and retire that
session from source, target-matching, and reveal work.

### Standing-Pipeline Output Routing

- Destination: prediction / reveal readiness. No `PRED`, `RESULT`, `CLAIM`, or
  `KNOW` artifact is created by the ledger or monitor-only state.
- Trigger: a ledger-qualified official metadata signal postdating `2026-05-20`.
- Cadence: none. Monitoring is event-trigger-only.
- First transition: a fresh independent metadata-only source-manifest decision;
  source pinning, target matching, no-peek review, and scoring stay separate.
- Review tier: none for the ledger and monitor-only state. A real reveal wave
  runs the single-shot reveal workflow and its own review.
- Gate A / Gate B: not attempted; no result or prediction artifact is produced.
- Limitations: no new source is asserted to exist; a future reveal wave still
  requires a reviewed source manifest, checksum record, target-matching task,
  no-peek audit, and comparison authorization before any scoring.
