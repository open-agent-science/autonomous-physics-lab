# Nuclear Shell-Axis Mini-Wave Reveal Comparison

**Task:** TASK-0305
**Status:** review-ready source gate outcome; no reveal score computed
**Target batch:** `shell-axis-balanced-001`
**Registry entries:** `PRED-0063` through `PRED-0068`
**Readiness decision:** `BLOCKED_SOURCE_NOT_PINNED`
**Scientific verdict:** `INCONCLUSIVE_NO_REAL_REVEAL`

## Scope

TASK-0305 was reopened by maintainer decision D2-5
(`docs/reviews/maintainer-decision-day-2026-07-06.md`) after the earlier
source-preflight, dry-run, and source-manifest tasks reached `DONE`.

This review executes the TASK-0305 gate against the committed repository
state. It does not fetch external nuclear data, does not inspect row-level
target values, does not edit frozen `PRED-*` entries, and does not compute
MAE/RMSE from any unpinned source.

## Inputs Checked

| Input | Status |
| --- | --- |
| `tasks/archive/0000-0499/TASK-0303-prepare-nuclear-shell-axis-mini-wave-source-preflight.yaml` | `DONE`; defines source classes, manifest fields, no-peek checks, and stop conditions. |
| `tasks/archive/0000-0499/TASK-0304-add-nuclear-shell-axis-mini-wave-reveal-dry-run.yaml` | `DONE`; synthetic plumbing only, not real measurement evidence. |
| `tasks/archive/0000-0499/TASK-0307-prepare-nuclear-shell-axis-reveal-source-manifest.yaml` | `DONE`; produced a negative source-manifest review, not a pinned source manifest. |
| `docs/reviews/maintainer-decision-day-2026-07-06.md` | D2-5 says TASK-0305 is unblocked to READY. |
| `data/nuclear_masses/shell_axis_reveal_source_manifest_template.yaml` | Template only; `template_status: not_pinned`; contains `TBD_*` placeholders. |
| `docs/reviews/nuclear-shell-axis-reveal-source-manifest-review.md` | Records `BLOCKED_SOURCE_NOT_PINNED` and explicitly states no concrete source manifest was prepared. |

Repository inventory found no committed
`data/nuclear_masses/shell_axis_reveal_source_manifest_<source-id>.yaml`.
The only matching file is the template.

## Gate Result

The source-readiness gate is not satisfied.

| Gate | Result | Reason |
| --- | --- | --- |
| Canonical reveal task approved | `PASS_WITH_SCOPE_LIMIT` | D2-5 approves attempting TASK-0305. |
| Concrete source manifest | `FAIL` | No non-template source manifest is committed. |
| Source title, release date, locator | `FAIL` | No approved source candidate exists in repo. |
| Archive policy and checksum record | `FAIL` | No raw or normalized artifact checksum exists for a source. |
| Measured/non-measured row flag | `FAIL` | No source field semantics can be reviewed without a source. |
| No-peek audit against concrete source | `NOT_RUN` | A concrete source date and artifact are required first. |
| Row-level eligibility labels | `NOT_RUN` | Labelling targets would require source inspection after pinning. |
| Real reveal metrics | `NOT_RUN` | Protocol forbids metrics from a file whose checksum has not been reviewed. |

The correct readiness decision is therefore `BLOCKED_SOURCE_NOT_PINNED`, not
`INCONCLUSIVE_ZERO_ELIGIBLE_TARGETS`. Zero-eligible-targets can be assigned
only after a source is pinned and reviewed, then found to contain no eligible
measured targets.

## Coverage And Metrics

No target rows were eligible for real scoring because no approved source
manifest exists.

| Field | Value |
| --- | ---: |
| Registry entries checked | 6 |
| Target rows in frozen batch | 48 |
| Unique target nuclides | 8 |
| Eligible measured rows scored | 0 |
| MAE/RMSE rows | 0 |

Per-entry metrics are intentionally null:

| Entry | Role | Eligible measured rows | MAE (MeV) | RMSE (MeV) | Status |
| --- | --- | ---: | --- | --- | --- |
| `PRED-0063` | primary candidate, proton-axis Gaussian | 0 | `not_computed` | `not_computed` | `SOURCE_MANIFEST_INCOMPLETE` |
| `PRED-0064` | companion candidate, proton x neutron product | 0 | `not_computed` | `not_computed` | `SOURCE_MANIFEST_INCOMPLETE` |
| `PRED-0065` | diagnostic candidate, neutron-axis Gaussian | 0 | `not_computed` | `not_computed` | `SOURCE_MANIFEST_INCOMPLETE` |
| `PRED-0066` | sign-inverted negative control | 0 | `not_computed` | `not_computed` | `SOURCE_MANIFEST_INCOMPLETE` |
| `PRED-0067` | near-null control | 0 | `not_computed` | `not_computed` | `SOURCE_MANIFEST_INCOMPLETE` |
| `PRED-0068` | frozen baseline reference | 0 | `not_computed` | `not_computed` | `SOURCE_MANIFEST_INCOMPLETE` |

This is a gate outcome, not evidence for or against the shell-axis
mini-wave.

## Per-Target Handling

No per-target measured, unmeasured, ambiguous, extrapolated, or
source-absent labels are assigned here. TASK-0303 requires those labels to be
assigned from a pinned source after source manifest approval and before
metrics. Assigning them now would infer target-row availability before the
source gate is satisfied.

The frozen target list remains:

| Nuclide | Z | N | A | TASK-0305 handling |
| --- | ---: | ---: | ---: | --- |
| `V-70` | 23 | 47 | 70 | not inspected; source manifest incomplete |
| `Mn-75` | 25 | 50 | 75 | not inspected; source manifest incomplete |
| `Co-77` | 27 | 50 | 77 | not inspected; source manifest incomplete |
| `Cu-81` | 29 | 52 | 81 | not inspected; source manifest incomplete |
| `Ag-129` | 47 | 82 | 129 | not inspected; source manifest incomplete |
| `Cd-130` | 48 | 82 | 130 | not inspected; source manifest incomplete |
| `Sb-135` | 51 | 84 | 135 | not inspected; source manifest incomplete |
| `Cs-139` | 55 | 84 | 139 | not inspected; source manifest incomplete |

## Controls And Registry Boundary

The paired reporting surface is preserved: the three primary candidate entries
remain paired with the sign-inverted control, near-null control, and frozen
baseline reference. No registry files were edited.

The earlier synthetic dry-run remains valid only as plumbing evidence. Its toy
MAE/RMSE values are not copied into this real-reveal comparison and must not
be cited as measurement evidence.

## Relationship To D2-5

D2-5 is treated as authorization to attempt TASK-0305, not as permission to
override the reveal protocol. The committed TASK-0307 artifact still states
that no concrete source manifest was prepared. Under
`docs/nuclear-reveal-source-readiness-checklist.md`, missing source
provenance, archive policy, checksums, and row semantics require a stop at
source-readiness review.

## Follow-Up

The next legitimate step is not manual scoring. It is a fresh source-gated
manifest task or reveal-source watch update that supplies a concrete
post-registration source before any row-level target values are inspected.

That task must provide:

- source class, title, issuing body, release date, and immutable locator;
- archive policy and raw/normalized checksums, or an explicitly accepted
  manifest-only limitation;
- parser or normalizer reference if any row conversion is needed;
- `mass_excess_mev` unit semantics and uncertainty semantics;
- measured/non-measured row flag and deterministic target matching rules;
- no-peek audit against the concrete source;
- only then, a comparison artifact with scored and excluded rows.

## Limitations

- No external source was fetched or inspected.
- No target mass value, uncertainty, or measured/extrapolated flag was
  recorded.
- No MAE, RMSE, signed error, baseline delta, claim, result, or knowledge
  artifact was produced.
- This review resolves the current TASK-0305 execution attempt only; it does
  not prevent a later source-triggered reveal wave.

## Verdict

`BLOCKED_SOURCE_NOT_PINNED`.

TASK-0305 is review-ready as a protocol-preserving no-score outcome. The
shell-axis mini-wave remains prospective and armed for a future source-gated
reveal, but it has not been scored against real measurements.
