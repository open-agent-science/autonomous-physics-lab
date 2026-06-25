# Nuclear Prediction Reveal Protocol

## Purpose

This protocol defines how a future reviewed task may compare frozen
nuclear-mass prediction registry entries against later measured data.

It is a narrow reveal-readiness checklist for
`prediction_registry/nuclear_masses/`. It extends the boundary already defined
by [Prediction Registry Policy](./prediction-registry-policy.md) and
[Blind Holdout Benchmark Protocol](./blind-holdout-benchmark-protocol.md);
it does not replace either document.

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
post-freeze measurement source, opens a reveal task, and runs the comparison.
The post-AME2020 source scouts
([source-class scout](./reviews/nuclear-post-ame2020-reveal-source-scout.md),
[concrete-source scout](./reviews/nuclear-post-ame2020-reveal-source-manifest-scout.md))
both concluded `BLOCKED_SOURCE_NOT_PINNED`: no admissible source postdating the
`2026-05-20T00:00:00Z` freeze was published in the weeks after the freeze, while
the admissibility lane for each source class is already mapped. New mass
measurements (Penning-trap, storage-ring, FRIB / ISOLDE / CARIBU programs) are
published continuously, so the reveal is not terminally blocked — it is only
*"no admissible post-freeze source published yet."*

This section converts that externally gated reveal into a standing,
time-based process: a low-cost recurring check that watches for an admissible
post-freeze source and, only when one appears, hands it to the existing
single-shot reveal workflow against the frozen prediction set. The pipeline adds
**no new scoring authority and no new admissibility relaxation**. It is a
scheduler and a watch list wrapped around the gates already defined above and in
the [readiness checklist](./nuclear-reveal-source-readiness-checklist.md).

It does not fetch any source, ingest any measured value, register or score any
prediction, or promote any claim. At design time it is **armed and waiting, not
blocked**: every gate is pre-stated, and the first admissible source trips the
trigger.

### Pipeline Stages

The pipeline has five stages. Stages 1, 2, and 5 are recurring and value-free.
Stages 3 and 4 run only when stage 2 fires, and they are exactly the
single-shot reveal workflow and readiness checklist already defined — not a new
shortcut around them.

1. **Watch (recurring, value-free).** Maintain a reveal-watch manifest of
   candidate upcoming or recent measurement programs and the nuclide regions to
   watch. The manifest lists program names, issuing bodies, source classes, and
   `(Z, N)` regions only. It records **no** measured values, **no** predicted
   values, and **no** metrics. See "Reveal-Watch Manifest Concept" below.

2. **Trigger (recurring availability check).** On each cadence, check whether an
   admissible post-freeze source now exists for any watched program. A source is
   admissible only when it satisfies the trigger condition below. If no source
   qualifies, record `armed_and_waiting` and stop until the next cadence. This
   check inspects publication metadata (titles, DOIs, release dates, source
   class, measured-vs-extrapolated posture) — **never** target-row values.

3. **Pin and gate (single-shot, on trigger only).** When stage 2 fires, open a
   canonical reveal task and build the source manifest required by the
   [readiness checklist](./nuclear-reveal-source-readiness-checklist.md): all
   manifest fields, raw and normalized checksums, target-matching rules, and the
   no-peek audit (`NO_PEEK_PASS` / `NO_PEEK_WEAK` / `NO_PEEK_FAIL` /
   `NO_PEEK_INCONCLUSIVE`). This is "Discover Candidate Measurement Sources"
   through "Perform The No-Peek Audit" above. If the source cannot be pinned or
   the no-peek audit does not pass, the pipeline returns to
   `armed_and_waiting`; it does not score.

4. **Score (single-shot, on trigger only).** Apply the existing
   `nuclear_prediction_reveal` workflow against the frozen prediction set — the
   **61 frozen PRED entries** under `prediction_registry/nuclear_masses/`
   (`PRED-0001` … the current registry head; see
   [registry coverage](./reviews/nuclear-prediction-registry-coverage-audit.md))
   — using only `ELIGIBLE_MEASURED` rows. This is "Execute Comparison" through
   "Preserve Negative And Inconclusive Outcomes" above: partial reveal is
   expected, only eligible revealed targets are scored, unrevealed targets are
   preserved unchanged, and negative or inconclusive outcomes stay visible.
   Verdict vocabulary and wording boundary are unchanged from this protocol.

5. **Re-arm (recurring).** After a reveal wave, unscored and not-yet-revealed
   targets remain eligible for a later reveal unless a no-peek or source-timing
   failure blocks them. Update the watch manifest's coverage notes (counts and
   region status only, never values) and return to `armed_and_waiting` for the
   regions still open.

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

### Trigger Condition (Admissibility Gate)

A watched program trips the trigger **only** when a candidate source satisfies
every condition below, evaluated from publication metadata without inspecting
target-row values. These conditions are the readiness checklist's admissibility
gate, restated as the standing trigger; the pipeline adds none and relaxes none.

- **Post-freeze.** The source's `publication_or_release_date` is strictly after
  the registry freeze `2026-05-20T00:00:00Z`, and after each included entry's
  `registered_at_utc`. A source that predates registration is
  `SOURCE_PREDATES_REGISTRATION` and is downgraded to a retrospective
  diagnostic, never prospective reveal evidence.
- **Immutable and pinnable.** The source has an exact immutable locator (DOI,
  versioned release, or archivable `.mas`-style file) and an accepted archive
  policy (`committed_copy`, `external_archive_with_checksum`, or
  `manifest_only_with_retrieval_instructions`) so raw and normalized checksums
  can be recorded before scoring.
- **Measured-separable.** Measured rows are separable from evaluated,
  extrapolated, or derived rows by an explicit row-level flag, so only
  `ELIGIBLE_MEASURED` targets are scored.
- **No-peek-clean.** The no-peek audit returns `NO_PEEK_PASS` (or, with explicit
  weaker-evidence limitations, `NO_PEEK_WEAK`). `NO_PEEK_FAIL` or
  `NO_PEEK_INCONCLUSIVE` blocks prospective scoring.
- **Target-overlapping.** At least one watched `(Z, N)` region containing a
  registered `PRED-*` target appears in the source with measured semantics;
  otherwise the readiness decision is
  `INCONCLUSIVE_ZERO_ELIGIBLE_TARGETS` and the pipeline stays armed.

If any condition fails or is ambiguous, the pipeline stays `armed_and_waiting`
(or records a blocked readiness decision) and does **not** score. The most
realistic near-term trigger is source-class B (primary Penning-trap /
storage-ring tables); source-class A (the next AME / NUBASE edition) would
supersede it as the cleanest trigger the moment such an edition is released.

### Recurring Cadence

- **Default cadence: monthly.** Once per month a maintainer (or a maintainer-run
  availability-check task) re-runs stage 2 against the watch manifest: scan for
  newly published post-freeze sources for the watched programs and regions,
  using metadata only.
- **Event cadence.** A maintainer may also run the check on demand when a
  relevant edition or measurement campaign is announced (for example a new AME /
  NUBASE edition, or a flagged Penning-trap result in a watched region).
- **Cheap by construction.** The recurring check is metadata-only and produces
  no scientific artifact when no admissible source exists; its normal output is
  `armed_and_waiting` with the date of the check. The expensive stages (pin,
  gate, score) run only on a real trigger.
- **No automation of the gated stages.** The cadence may remind and may scan
  metadata, but pinning, the no-peek audit, and scoring remain maintainer-driven
  reviewed steps. The cadence never auto-fetches, auto-pins, or auto-scores.

### Do-Not-Do List

The standing pipeline must not, at any cadence or stage:

- perform a live fetch of any measurement source from an executor task, or
  trigger such a fetch automatically from the cadence;
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

### Armed-And-Waiting Status

At design time, and whenever stage 2 finds no admissible post-freeze source, the
pipeline state is **`armed_and_waiting`**, not blocked:

- the watch manifest, trigger condition, scoring step, cadence, and do-not-do
  list are all pre-stated and reviewed;
- the 61 frozen PRED entries are fixed and the registry snapshot is reproducible;
- the first source that satisfies the trigger condition advances the pipeline to
  the pin / gate / score stages with no further design work.

This mirrors the source scouts' standing conclusion: the reveal is not
terminally blocked, only waiting for an admissible post-freeze source to be
published.

### Standing-Pipeline Output Routing

- Destination: prediction / reveal readiness. No `PRED`, `RESULT`, `CLAIM`, or
  `KNOW` artifact is created by the pipeline design or by a `armed_and_waiting`
  cadence check.
- Trigger: an admissible, immutable, post-`2026-05-20T00:00:00Z` source per the
  readiness checklist, decided from publication metadata only.
- Cadence: monthly availability check, plus on-demand event checks.
- Admissibility gates: post-freeze, immutable / pinnable, measured-separable,
  no-peek-clean, target-overlapping — all inherited unchanged from this protocol
  and the readiness checklist.
- Review tier: none for the design and for `armed_and_waiting` checks. A real
  reveal wave runs the single-shot reveal workflow and its own review.
- Gate A / Gate B: not attempted; no result or prediction artifact is produced.
- Limitations: no live fetch performed; no admissible post-freeze source exists
  at design time; the pipeline is armed and waiting; a future reveal wave still
  requires a separate maintainer-reviewed source manifest, checksum record,
  no-peek audit, and comparison artifact before any scoring.
