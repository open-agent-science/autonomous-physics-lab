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
