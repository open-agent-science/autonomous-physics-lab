# Particle Common-Scheme Source Artifact

**Task:** `TASK-0902`

**Campaign:** `particle-mass-relations`

**Review date:** 2026-06-30

**Verdict:** `SOURCE_METADATA_PINNED_VALUES_NOT_CURATED`

## Decision

The Antusch-Hinze-Saad source is sufficiently unambiguous for a metadata-only
pin. The publicly pinned audit surface is the accepted arXiv manuscript:

- Stefan Antusch, Kevin Hinze, and Shaikh Saad, "Updated running quark and
  lepton parameters at various scales,"
  [arXiv:2510.01312v2](https://arxiv.org/abs/2510.01312v2), revised
  2026-03-23;
- publication status: the arXiv v2 comment says the version was accepted for
  publication in *Physical Review D*;
- reuse posture: the arXiv accepted-manuscript page identifies
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) with attribution.

No source bytes or quark values are committed by this task. PRD volume, article
number, publication date, DOI, and publisher locator are deliberately not pinned
here because they were not independently verified during this review; a future
metadata refresh may add them after a public publisher or Crossref record is
checked.

## Exact Surface

| Field | Pinned choice |
|---|---|
| Input branch | 2024 PDG |
| Theory | Standard Model |
| Representation | dimensionless running Yukawa couplings |
| Scheme | `MS-bar` |
| Scale | `M_Z` |
| Exact source location | Equation (2.4) |
| Parameter labels | `y_u`, `y_d`, `y_s`, `y_c`, `y_b`, `y_t` |
| Row class | `derived_running_yukawa` |
| Uncertainty | source-reported one-sigma HPD marginals |

The source does **not** present the selected surface as six running masses.
Equation (2.4) is the exact 2024-PDG `M_Z` Yukawa surface. Table 2 contains the
2024-PDG Standard Model running parameters at higher benchmark scales and must
not be cited as the `M_Z` location.

## Provenance Boundary

The source begins with low-scale PDG mass and electroweak inputs, including a
top pole mass. It uses SMDR for matching and running to `M_Z`, samples 100,000
input points with assumed Gaussian errors, and reports one-sigma
highest-posterior-density intervals. Its note states that non-top quark masses
reported at 90% confidence by PDG were rescaled to one sigma before propagation.

The six outputs share upstream inputs and matching assumptions. No six-output
covariance matrix is pinned, so a future sensitivity run may report source
marginals but must not claim a full covariance-aware test or independent row
errors. The top entry is a derived `y_t(M_Z)`, not a direct or pole-mass row.

## Representation Decision

The metadata artifact deliberately records `derived_running_yukawa` rather
than `derived_running_mass`. A future Koide sensitivity task may use a frozen
common-scale Yukawa representation only after a separate value-curation task.
It must not silently convert Yukawas to masses, because that would require an
explicit electroweak convention and running vacuum expectation value.

## Next Allowed Task

A separate source-row task may transcribe only the six Equation (2.4) 2024-PDG
SM Yukawa entries into a new common-scheme sensitivity dataset. It must:

1. pin and checksum the exact source version used for transcription;
2. preserve parameter labels, asymmetric/symmetric interval shape, one-sigma
   semantics, and shared-dependence warning;
3. keep the rows separate from existing PDG/direct mass datasets;
4. add schema and source-parity tests;
5. stop before calculating a Koide quotient.

Only a later metric task may freeze the unchanged target and score that curated
surface.

## Stop Conditions

- Do not copy values from search snippets, secondary tables, or this note.
- Do not mix Equation (2.4) with the 2022 branch, MSSM/`DR-bar` tables, or
  higher-scale columns.
- Do not relabel Yukawa couplings as masses.
- Do not describe `y_t(M_Z)` as a direct top-mass measurement.
- Do not assume diagonal covariance is complete evidence.
- Do not overwrite existing particle-mass datasets, run Koide metrics, or
  change `RESULT-0011` or `CLAIM-0007`.

## Output Routing

| Destination | Action |
|---|---|
| Source artifact | Metadata-only provenance pin created |
| Particle rows | None created or changed |
| `RESULT-0011` | Unchanged |
| `CLAIM-0007` | Unchanged and remains `DRAFT` |
| Gate A / Gate B | Not attempted / not applicable |
| Knowledge | No impact |
