# Nuclear post-AME2020 reveal source manifest scout

- Task: `TASK-0585`
- Campaign: `nuclear_mass_surface`
- Protocol class: value-free source-manifest scout
- Status: no target values fetched, copied, transcribed, inspected, or scored

## Scope

This review scouts source candidates for a future reveal of registered
nuclear-mass prediction entries without crossing the no-peek boundary. It uses
metadata-level evidence only: source titles, issuing bodies, release dates,
locators, access or reuse notes, checksum feasibility, and value-semantics
risks.

This task does not fetch source tables, inspect target rows, record measured
mass values, update `PRED-*` entries, run reveal metrics, or create result,
claim, prediction, or knowledge artifacts.

## Registry timing boundary

The current shell-axis mini-wave preflight records `PRED-0063` through
`PRED-0068` as registered at `2026-05-20T00:00:00Z`, with source commit
`9e8d7d339a4f0f432e41689862a649eb029b8575`. A prospective reveal source must
therefore be demonstrably available to the project only after that registry
freeze, or the comparison must be downgraded to a retrospective diagnostic.

## Sources checked

### AME2020 official evaluation

- Candidate class: `official_evaluation`.
- Source title: Atomic Mass Evaluation 2020.
- Issuing body / source surface: Atomic Mass Data Center distribution and
  Chinese Physics C AME2020 papers.
- Locator:
  `https://amdc.impcas.ac.cn/web/masseval.html`;
  `https://doi.org/10.1088/1674-1137/abddaf`.
- Release timing: published in 2021, with the table article available online
  in 2021.
- Quantity support: AMDC lists the `mass_1.mas20` file as atomic masses with
  mass excess, binding energy per nucleon, beta-decay energy, and atomic mass.
- Checksum feasibility: feasible if a future task pins the exact AMDC file or
  an immutable mirror and records a raw checksum.
- Value semantics: official evaluation mixes evaluated mass values and
  extrapolated/systematics-marked rows; a reveal task would need row-level
  measured/non-measured separation before scoring.
- Decision: not admissible for prospective reveal of the current registry
  entries because the source predates the 2026-05-20 registry freeze. It
  remains a baseline/source-format reference only.

### Post-AME2020 compiled new-mass survey

- Candidate class: `peer_reviewed_table` or `secondary_compilation`
  candidate, not an official evaluation.
- Source title: "Benchmarking nuclear energy density functionals with new mass
  data".
- Issuing body / venue: Nuclear Science and Techniques; arXiv preprint surface
  also available.
- Locator:
  `https://arxiv.org/abs/2505.09914`;
  `https://doi.org/10.1007/s41365-025-01821-1`.
- Release timing: arXiv v1 submitted `2025-05-15`; journal metadata records
  2025 publication.
- Metadata observation: the abstract describes a compilation of newly measured
  masses for 296 nuclides from 40 references published between 2021 and 2024,
  after AME2020.
- Checksum feasibility: feasible for a paper PDF or source package if the
  license and local archive policy are accepted; not sufficient by itself for
  a measured-only reveal table.
- Value semantics: likely mixed-source and secondary. A future task would have
  to trace each eligible row back to a primary measurement source or prove the
  compilation's row semantics are measured-only and target-matchable.
- Decision: not admissible for prospective reveal of current registry entries
  because it predates the 2026-05-20 registry freeze. It is useful only as a
  source-discovery index for future primary-source scouting, and even that use
  must avoid target-row inspection until a reviewed reveal task exists.

### Post-freeze official evaluation or primary measurement release

- Candidate class: `official_evaluation`, `peer_reviewed_table`, or
  `collaboration_release`.
- Locator: none identified in committed repository context or metadata-level
  web scan without target-row inspection.
- Release timing: must be later than `2026-05-20T00:00:00Z`.
- Checksum feasibility: unknown until an exact source exists.
- Value semantics: must separate measured rows from evaluated, extrapolated,
  model-derived, and ambiguous rows.
- Decision: no admissible post-freeze candidate was identified by this task.

## Readiness decision

`BLOCKED_SOURCE_NOT_PINNED`

No value-free source manifest candidate is prepared because the reviewed
metadata did not identify a source that simultaneously:

1. postdates the `2026-05-20T00:00:00Z` registry freeze;
2. has an exact immutable locator or acceptable archive policy;
3. can be checksummed before scoring;
4. separates measured from non-measured rows;
5. can be reviewed without exposing target-row mass values.

## Handoff for a future scout

A later source-manifest task should look for one of these source classes only
after a source exists that postdates the registry freeze:

- a new official AME/NUBASE-style release with row-level measured/extrapolated
  flags and an immutable electronic distribution;
- a primary peer-reviewed mass-measurement table whose publication date
  postdates the registry freeze and whose target rows can be pinned without
  ad hoc selection;
- a collaboration or facility data release with explicit reuse terms,
  checksumable artifacts, and measured/non-measured row flags.

The future task may use the 2025 new-mass survey as a bibliography map only if
it does not inspect target-row values before the no-peek audit. It must not use
that survey as prospective reveal evidence for entries registered in 2026.

## Stop conditions preserved

- Do not fetch or parse source tables that expose target mass values.
- Do not inspect target rows while deciding source admissibility.
- Do not score partial reveals from a source that predates registration.
- Do not modify frozen `PRED-*` entries.
- Do not promote any claim or result from this scout.

## Output routing

- Task verdict: `INCONCLUSIVE` for reveal readiness.
- Canonical destination:
  `docs/reviews/nuclear-post-ame2020-reveal-source-manifest-scout.md`.
- Review tier: `none`.
- Gate A status: not attempted; no `RESULT-*` or `PRED-*` artifact.
- Gate B status: not attempted; no independent replay target.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result artifact impact: no `results/` artifacts modified.
- Publication blocker: no admissible post-freeze measured-source manifest is
  pinned; future reveal scoring remains blocked.

## Metadata sources

- AMDC AME2020 distribution page:
  `https://amdc.impcas.ac.cn/web/masseval.html`.
- AME2020 Part II article:
  `https://doi.org/10.1088/1674-1137/abddaf`.
- Qu et al. new-mass survey preprint:
  `https://arxiv.org/abs/2505.09914`.
- Qu et al. journal DOI:
  `https://doi.org/10.1007/s41365-025-01821-1`.
