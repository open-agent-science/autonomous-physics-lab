# Atomic Second Direct-Ratio Source Triage

**Task:** `TASK-0403`
**Predecessor:** `TASK-0371` (first-batch Beloy 2021 curation), `TASK-0401` (row readiness re-check), `TASK-0402` (cross-ratio covariance approximation)
**Campaign:** Atomic-Clock Residuals
**Triage verdict:** `CANDIDATE_TRIAGED_SOURCE_INGESTION_BLOCKED` (sandbox-only; no PDF committed; no rows added)

## Scope

The Atomic-Clock Residuals campaign currently has exactly one committed
direct-ratio source (Beloy 2021 / BACON,
`ACR-0001-BELOY-2021-DIRECT-RATIOS`). The `TASK-0401` re-check listed
"single-source replay risk" as Blocker 4 before any `BASELINE_READY`
promotion: either a second independent direct-ratio source must be
committed under the same source-readiness gate, or an explicit
single-source baseline waiver must be obtained.

This task performs **triage only**: it identifies one candidate source
for direct optical frequency-ratio rows that is independent of Beloy
2021 / BACON, evaluates whether the candidate is admissible under the
existing source-readiness contracts (`TASK-0332`, `TASK-0344`,
`TASK-0363`, `TASK-0372`), and lists the exact missing conditions that
must be satisfied by a future source-ingestion task before any row is
committed.

This document does **not** commit a source PDF, copy any clock value,
record any uncertainty number, create or modify any
`data/atomic_clocks/*.yaml`, change the source manifest template, fit
any drift, derive any constants-variation constraint, write to the
prediction registry, or promote any claim or knowledge entry.

## Candidate Sources Considered

The triage evaluated public-domain candidates that publish a direct
optical-clock frequency ratio independent of the NIST + JILA + NIST
BACON 2018 campaign behind Beloy 2021:

| Candidate | Ratio | Lab | Year | Source class | Why considered |
| --- | --- | --- | --- | --- | --- |
| Nemitz, N., et al. | ⁸⁸Sr / ¹⁷¹Yb (neutral optical lattice clocks) | RIKEN (Japan) | 2016 | Primary frequency-ratio measurement paper | Same clock species as Beloy 2021 `Yb/Sr`; independent lab; published with explicit uncertainty budget; arXiv preprint available. Strongest direct cross-check for the Beloy `ACR-0001-ROW-003` row. |
| Pizzocaro, M., et al. | ¹⁷¹Yb / ⁸⁷Sr | INRIM (Italy) | 2020 | Primary frequency-ratio measurement paper | Same species pair as Beloy `Yb/Sr`; independent lab; published values. |
| Lange, R., et al. | ¹⁷¹Yb⁺ E3 / ¹³³Cs | PTB (Germany) | 2021 | Primary frequency-ratio measurement paper | Independent lab, different clock species (Yb⁺ ion, not neutral Yb; Cs microwave reference). Useful for atomic-clock breadth, weaker for direct cross-check of Beloy. |
| Schwarz, R., et al. | ¹⁷¹Yb⁺ E2 / ¹⁷¹Yb⁺ E3 | PTB (Germany) | 2020 | Within-ion clock-transition ratio | Same ion, different transitions; not a cross-clock comparison; weaker independence story. |
| BIPM Recommended Frequency Values (CCTF) | Many | International evaluation | annual | Evaluation/review summary | Review-summary row class; per the existing schema (`data/atomic_clocks/schema.md`) cannot be ingested as a direct row unless source list and combination rules are recoverable. |

### Recommended candidate

**Nemitz, N., et al. (RIKEN), "Frequency ratio of Yb and Sr clocks with
5×10⁻¹⁷ uncertainty at 150 seconds averaging time", Nature Photonics
10, 258 (2016); arXiv:1511.07738.**

Rationale:

- It is the strongest direct independent cross-check for the
  load-bearing Beloy 2021 `Yb/Sr` ratio (`ACR-0001-ROW-003`).
- It is the same species pair (neutral ¹⁷¹Yb optical lattice clock vs
  ⁸⁷Sr optical lattice clock), so the comparison is value-on-value and
  unit-on-unit comparable without sensitivity-coefficient mediation.
- RIKEN's clock pair and 2014-era campaign are physically independent
  of the NIST + JILA + NIST BACON 2018 campaign, satisfying the
  intent of Blocker 4 of `TASK-0401`.
- An arXiv preprint exists, so a future source-artifact task can
  follow the same arXiv-permitted redistribution path used for the
  Beloy artifact under `TASK-0363` / `TASK-0371`.

The triage uses Nemitz 2016 as the working candidate for the gate
evaluation below. Pizzocaro 2020 is held as the strongest secondary
fallback if Nemitz turns out to be unrecoverable under the existing
gates.

## Provenance Checklist Status (Nemitz 2016)

Per `docs/notes/atomic-clock-source-candidates.md` and the
`TASK-0332` readiness-gate inputs, each provenance question is
answered below from publicly-stated metadata only. **No values, no
uncertainties, and no per-systematic numbers are transcribed into this
review.**

| Question | Triage status |
| --- | --- |
| What exact source or archive is frozen? | Not yet — the future source-ingestion task must record the arXiv abs/pdf URL, the Nature DOI, and the locator for any supplementary information. |
| Is there a checksum or archive policy? | Not yet — a checksum sidecar (analogous to `data/atomic_clocks/source_artifacts/2021-beloy-bacon/arxiv-2005.14694.sha256`) must be committed at ingestion time. |
| What is the retrieval date? | Not yet — must be recorded at ingestion. |
| Is the license recoverable? | The arXiv perpetual licence is the documented reusable path (same pattern as Beloy 2021); the Nature version-of-record PDF is publisher-restricted and must not be redistributed. |
| Which transition, isotope, ratio partner, epoch? | Public metadata identifies the ratio as ⁸⁸Sr (or ⁸⁷Sr — to be confirmed at ingestion) optical lattice clock vs ¹⁷¹Yb optical lattice clock, RIKEN campaign 2014. Exact transition labels (`1S0_to_3P0`) and campaign window must be transcribed from the source artifact at ingestion. |
| Uncertainty semantics and covariance notes recoverable? | The paper is known to report a per-systematic budget with statistical/systematic separation. The exact field names, asymmetric/symmetric handling, and per-systematic-component table can only be locked at ingestion under the `TASK-0344` contract. |
| Is the row direct, derived, review-summary, or synthetic? | `direct_measurement` (single optical-clock-pair ratio measurement). |
| Holdout / no-peek boundary? | Must be set at ingestion. The Beloy rows currently carry `holdout.split: unassigned`; the same gap applies here and remains Blocker 2 of `TASK-0401`. |

## Source-Manifest Decision

`TASK-0403` lists `data/atomic_clocks/source_manifest.yaml` as a
possible update target, but the file does not exist in the
repository — only the template
`data/atomic_clocks/source_manifest_template.yaml` is committed under
`TASK-0327`. Creating a non-template manifest would be a structural
campaign decision (single multi-source manifest vs per-source
manifest), and it is outside the triage-only scope of this task.

**Decision:** do not create or update a source manifest in this PR.
Defer to the future source-ingestion task to decide whether to use the
template-shaped manifest pattern (one manifest per source family) or
to introduce a campaign-level aggregate manifest. The decision is
itself worth maintainer input.

## Stop Conditions That Would Block Ingestion

The future source-ingestion task must stop and preserve a negative
source-review result if any of the following applies to Nemitz 2016
(or to whichever candidate is taken forward):

1. The arXiv preprint version disagrees with the Nature
   version-of-record on any value-bearing or row-defining field
   (`SOURCE_ARTIFACT_VERSION_DRIFT` per `TASK-0372`).
2. The source does not separate direct measurement from any derived
   constants-variation constraint that the paper also reports.
3. Uncertainty semantics are not recoverable per the `TASK-0344`
   required-fields list (total, statistical, systematic,
   confidence-level label, bound style, covariance reference).
4. Per-systematic budget cannot be transcribed without inference from
   plots or secondary summaries.
5. License or reuse terms for the chosen archive (arXiv vs Nature) are
   not explicitly resolvable.
6. The required holdout / no-peek freeze manifest cannot be set before
   any benchmark consumer touches the row.

If any of the above fires, the ingestion task must record the negative
result as a blocker review and not commit a row.

## Required Outputs Of The Follow-Up Source-Ingestion Task

When a future task ingests Nemitz 2016 (or the chosen candidate), it
must produce at minimum:

- a committed source artifact (arXiv preprint PDF) with checksum
  sidecar, mirroring the
  `data/atomic_clocks/source_artifacts/2021-beloy-bacon/` layout;
- a `provenance.yaml` recording retrieval date, license, and the
  arXiv-vs-Nature version-drift cross-check verdict;
- one or more direct-measurement rows under a fresh dataset id
  (e.g. `ACR-0002-NEMITZ-2016-DIRECT-RATIO`) following the same row
  shape as `acr-0001-beloy-2021-direct-ratios.yaml`, including
  per-systematic component breakdowns;
- a source-specific covariance/uncertainty review covering the same
  fields the Beloy curation answered;
- a row-readiness gate review for the new dataset analogous to
  `docs/reviews/atomic-beloy-2021-row-readiness-recheck.md`;
- explicit sandbox-only and no-benchmark/no-claim promotion boundaries.

## Cross-Source Implications For `TASK-0401` And `TASK-0402`

Once a second independent source is committed:

- Blocker 4 of `TASK-0401` (single-source replay risk) is resolved
  and the campaign may progress toward `BASELINE_READY` review,
  subject to Blockers 1–3 (covariance, holdout, real-row loader)
  still being addressed.
- The `TASK-0402` cross-ratio covariance approximation remains
  per-dataset (it is internal to the Beloy 2018 BACON campaign). A new
  dataset's rows are not in the same physical campaign, so they
  introduce **inter-dataset** correlation considerations only via any
  shared systematic effect (e.g. realisation of the SI second through
  the Cs hyperfine transition) — usually negligible for Sr/Yb optical
  ratios but should be re-examined at ingestion.
- A direct value-on-value comparison between Beloy 2021 `Yb/Sr`
  (ROW-003) and Nemitz 2016 `Yb/Sr` becomes possible. That comparison
  is the natural first Gate-B-style external-style validation and
  must remain inside a benchmark task, not inside the ingestion task.

## Sandbox-Only Boundary

This triage is metadata-only. It does not:

- fetch any source PDF;
- commit any source artifact, checksum sidecar, or provenance file;
- copy any clock value, ratio, uncertainty number, or systematic
  component;
- create or modify any `data/atomic_clocks/*.yaml` (including the
  source manifest template);
- create, modify, or extend the synthetic-only loader at
  `physics_lab/engines/atomic_clock_residuals.py`;
- create or modify any `prediction_registry/`, `claims/`,
  `knowledge/`, `results/`, or `agent_runs/` entry;
- claim a discovery or breakthrough.

## Output-Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `not_applicable` for scientific claim;
  `CANDIDATE_TRIAGED_SOURCE_INGESTION_BLOCKED` for the
  source-triage workflow output.
- **Canonical destination:**
  `docs/reviews/atomic-second-direct-ratio-source-triage.md` (this
  file). Review-only artifact; no data files added.
- **Review tier:** `none` (no `RESULT/PRED` tier applies).
- **Gate A status:** `not_attempted` (no `RESULT/PRED` artifact
  proposed).
- **Gate B status:** `not_attempted` (no second source ingested yet;
  Gate B cross-source replay becomes possible only after the future
  source-ingestion task lands).
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Limitations and blockers:** see "Stop Conditions" and the
  Provenance Checklist. The triage establishes Nemitz 2016 as the
  recommended candidate; actual ingestion is deferred to a follow-up
  task because it requires committing a source PDF, computing
  checksums, recording retrieval/license, and running the source-
  artifact + covariance preflight analogous to `TASK-0363`.

## Limitations

- The triage relies on publicly-known metadata about the candidate
  papers (lab, year, ratio, species pair, arXiv availability). It does
  not transcribe values or per-systematic budgets and therefore cannot
  pre-confirm that the `TASK-0344` uncertainty-semantics contract will
  pass; that confirmation belongs to the source-ingestion task.
- The Nemitz 2016 candidate is selected as the strongest cross-check
  for the load-bearing Beloy `Yb/Sr` ratio. A different maintainer
  preference (e.g. broader species coverage via Lange 2021 Yb⁺/Cs)
  would be an acceptable scope change for the ingestion task; this
  triage is not a maintainer decision.
- The triage does not create or update a source manifest file; that
  structural decision is left for the maintainer-reviewed ingestion
  task.
- The triage does not attempt to perform any value-on-value
  cross-source comparison between Beloy 2021 and the candidate; such
  comparison must live inside a future benchmark task with the
  appropriate freeze/reveal discipline.

## Verdict

`CANDIDATE_TRIAGED_SOURCE_INGESTION_BLOCKED` (sandbox-only).
**Nemitz, N., et al. (RIKEN), arXiv:1511.07738 / Nature Photonics 10,
258 (2016)** is the recommended candidate to resolve Blocker 4 of
`TASK-0401`. Ingestion is intentionally deferred to a maintainer-
reviewed follow-up task that will commit the source artifact, compute
the checksum, record retrieval/license metadata, run the
arXiv-vs-Nature version-drift cross-check, transcribe per-systematic
budget under the `TASK-0344` contract, and add the row(s) under a
fresh dataset id with the appropriate readiness-gate review. Until
then, the Atomic-Clock Residuals campaign remains single-source and
the `TASK-0401` Blocker 4 stays open.
