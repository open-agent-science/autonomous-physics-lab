# Nuclear Prediction Reveal Protocol

## Purpose

This protocol defines the reviewed path for comparing frozen nuclear-mass
prediction registry entries against later reviewed measurement sources.

It protects the no-peek boundary created by
`prediction_registry/nuclear_masses/` and separates six steps that must remain
auditable:

1. source discovery;
2. source pinning;
3. reveal eligibility screening;
4. no-peek audit;
5. comparison execution;
6. result wording and follow-up review.

This document is downstream of
[Prediction Registry Policy](./prediction-registry-policy.md),
[Blind Holdout Benchmark Protocol](./blind-holdout-benchmark-protocol.md), and
[Nuclear Mass Holdout Protocol](./nuclear-mass-holdout-protocol.md). It does
not replace those policies.

## Scope

Use this protocol when a future canonical task asks a contributor or agent to
compare one or more registered nuclear-mass predictions against later reviewed
measured data.

The protocol applies to entries under:

```text
prediction_registry/nuclear_masses/PRED-XXXX.yaml
```

It does not apply to retrospective post-AME2020 time-split benchmarks, sandbox
residual studies, raw factory slate review, or ordinary registry entry
creation before reveal.

## Non-Goals

This protocol does not:

- fetch live external measurements during registry creation;
- authorize ad hoc comparison against live external pages;
- modify frozen registry predictions;
- create a canonical result package by default;
- promote any prediction to a claim or accepted knowledge;
- convert retrospective benchmarks into strict blind predictions.

Any reveal comparison is evidence for maintainer review, not automatic claim
promotion.

## Roles

| Role | Responsibility |
| --- | --- |
| Contributor or agent | Executes the reveal task from committed inputs, records artifacts, and reports limitations. |
| Maintainer | Approves the reveal task, accepts the pinned source state, and decides whether any follow-up result or claim work is appropriate. |
| Reviewer | Checks no-peek integrity, source provenance, unchanged registry state, metrics, and wording. |

One person may fill more than one role in a small private-alpha workflow, but
the artifacts must still show which step happened when.

## Required Reveal Task Inputs

A reveal task must name all of these before any comparison is executed:

- canonical task id;
- target registry entries, by `PRED-XXXX` id;
- registry snapshot commit or tree reference;
- future measured-data source manifest path;
- source checksum or content hash record;
- comparison script or exact command;
- output path for reveal artifacts;
- expected metric set;
- wording boundary and limitation expectations.

If any item is missing, the task should stop at `BLOCKED` or produce a source
review note only.

## Stepwise Workflow

### 1. Source Discovery

Source discovery is the act of finding a candidate future measurement source.
It may happen before a reveal task, but it must not be mixed with scoring.

Source discovery output should be a reviewable source note or task comment that
records:

- source title and publisher;
- version, release, or access date;
- whether the source was added after the prediction registration timestamp;
- whether it contains measured values or only extrapolated/systematic values;
- target nuclides believed to overlap registry entries;
- unresolved source-quality questions.

Discovery alone does not reveal predictions. Do not compute errors or inspect
measured values against frozen predictions in the discovery step.

### 2. Source Pinning And Checksums

Before eligibility screening or scoring, the measured-data source must be
pinned in a committed artifact or maintainer-reviewed manifest.

Minimum source manifest fields:

- source id;
- source citation;
- source version or release identifier;
- retrieval method;
- retrieval timestamp;
- file path or immutable URL;
- checksum for committed data files;
- unit conventions;
- measured versus extrapolated semantics;
- row-level provenance for each target nuclide;
- reviewer note for any converted quantity.

If the source cannot be committed directly, commit a source manifest with enough
metadata for another reviewer to reproduce the same source state.

### 3. Registry Snapshot Freeze

The reveal task must freeze the registry side before comparison. Record:

- repository commit at reveal start;
- registry entry file paths;
- `registered_at_utc` for each entry;
- `source_state.git_commit` for each entry;
- target nuclide list and predicted values;
- reveal conditions copied from each entry;
- whether any selected entry changed after initial registration.

Prediction files must not be edited to make a reveal succeed. If an entry was
changed after registration, the reveal report must classify the change before
scoring:

- metadata-only clarification, no value or target change;
- value, target, model, or reveal-rule change;
- unclear change requiring maintainer decision.

Value, target, model, or reveal-rule changes should normally disqualify the
entry from strict pre-reveal interpretation unless the earlier frozen version is
recovered and compared separately.

### 4. Eligibility Screening

Eligibility is checked per registry entry and per target nuclide.

A target is eligible only if:

- the registry entry was registered before the pinned measured source state was
  reviewed for reveal;
- the target nuclide appears unchanged in the registry entry;
- the measured source provides a reviewable measured or convertible value for
  the same nuclide;
- units and quantity semantics can be converted to `mass_excess_mev`;
- no live external fetch is required during comparison;
- the reveal trigger in the registry entry is satisfied.

A target is not eligible if:

- the source value is extrapolated when the reveal task requires measured data;
- nuclide identity or isomer state is ambiguous;
- unit conversion cannot be audited;
- the registry entry was changed post-registration in a value-relevant way;
- the target was already present in a committed measured dataset before the
  entry was registered and the entry did not disclose that fact.

Eligibility failures are negative or blocked outcomes. Preserve them in the
reveal report instead of silently dropping rows.

### 5. No-Peek Audit

Before comparison execution, run a no-peek audit and record:

- registry entries were selected before inspecting measured errors;
- frozen predicted values were not edited during the reveal task;
- source data was pinned before metric computation;
- comparison code path was named before execution;
- no live external data fetch occurred in the scoring command;
- excluded targets and exclusion reasons are listed.

If the audit fails, stop the reveal or label the output as a compromised
comparison. Do not present it as a prospective reveal.

### 6. Comparison Execution

Comparison execution should be deterministic and local. The command should read
only committed registry files and the pinned source manifest or committed data
file.

Minimum row-level output:

- `prediction_id`;
- `nuclide_id`;
- `Z`, `N`, `A`;
- predicted `mass_excess_mev`;
- measured or converted `mass_excess_mev`;
- signed error in `MeV`;
- absolute error in `MeV`;
- source row reference;
- eligibility status;
- limitation note when applicable.

Minimum aggregate output, when at least two eligible targets exist:

- count of eligible targets;
- MAE in `MeV`;
- RMSE in `MeV`;
- median absolute error in `MeV`;
- worst absolute error row;
- missing or ineligible target count.

For one eligible target, report row-level error and avoid overinterpreting
aggregate metrics.

### 7. Partial Reveals

Partial reveal is expected. A later source may cover only some target nuclides
from a registry entry.

Rules for partial reveal:

- compare only eligible measured targets;
- keep unrevealed targets in `PENDING_REVEAL`;
- do not replace, remove, or add targets to the original registry entry;
- do not treat missing targets as failures or successes;
- report per-entry metrics on the eligible subset only;
- report common-subset metrics when comparing multiple entries with different
  eligible target coverage;
- keep future reveal conditions active for unrevealed targets.

The reveal report should include a target-status matrix:

| Status | Meaning |
| --- | --- |
| `ELIGIBLE_REVEALED` | Target has a pinned reviewed value and was scored. |
| `PENDING_REVEAL` | Target remains unrevealed because no reviewed value is available. |
| `INELIGIBLE_SOURCE` | A value exists but fails source, unit, or semantics checks. |
| `DISQUALIFIED_NO_PEEK` | Target or entry fails the no-peek audit. |

### 8. Result Wording

Reveal reports must use bounded language:

- "prospective reveal comparison";
- "eligible revealed subset";
- "row-level error";
- "pre-registered prediction entry";
- "requires maintainer review before any claim update."

Do not use:

- "proved";
- "confirmed";
- "breakthrough";
- "discovered";
- "strict blind prediction" unless the full blind protocol artifacts exist;
- "canonical result" unless a separate result task explicitly creates one.

Negative results, ineligible rows, and null comparisons are valid outputs.
Preserve them with the same care as favorable comparisons.

## Required Reveal Artifacts

A future reveal PR should include:

- source manifest or committed measured dataset;
- checksum record for committed data;
- registry snapshot note;
- eligibility table;
- no-peek audit checklist;
- comparison table;
- metrics summary;
- limitations section;
- negative-result and ineligible-row handling;
- maintainer review notes;
- explicit statement that claim promotion is out of scope unless separately
  authorized.

Recommended paths:

```text
data/nuclear_masses/<source-id>.yaml
data/nuclear_masses/<source-id>-checksums.md
docs/reviews/<reveal-task-slug>.md
```

If a canonical result package is later approved, it should reference the reveal
review rather than rewrite it.

## Review Checklist

Before a reveal PR is considered ready:

- [ ] The source manifest is pinned and checksummed.
- [ ] Registry entries and predicted values are unchanged for scored rows.
- [ ] Eligibility decisions are row-level and explicit.
- [ ] Partial reveals preserve unrevealed targets as pending.
- [ ] No live external fetch occurs in scoring.
- [ ] Metrics distinguish row-level, per-entry, and common-subset results.
- [ ] Negative and ineligible outcomes are preserved.
- [ ] Wording does not promote claims, results, or knowledge.
- [ ] Any follow-up promotion path is left to a separate maintainer-reviewed
      task.

## Relationship To Claim Promotion

A reveal comparison can support later review, but it is not itself a claim
promotion path.

Any future claim, result, or knowledge update must:

- reference the reveal report;
- state the eligible target subset;
- include limitations and negative rows;
- preserve the original registry entry unchanged;
- pass the normal maintainer review process.

