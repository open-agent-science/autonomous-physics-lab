# Quantum ZnSe Frozen-Row Transfer Readiness Gate

Task: `TASK-0903`
Campaign: `quantum-size-effects`
Dataset surface: `data/quantum_dots/qd-0004-toufanian-2021-znse-absorption.yaml`
Verdict: `FROZEN_ROWS_READY_TRANSFER_BENCHMARK_NEEDS_MAINTAINER_DECISION`

## Scope

This note freezes the already committed Toufanian 2021 ZnSe row surface for any
later transfer task and defines what a future comparison may and may not do. It
adds no rows, fetches no live sources, vendors no source bytes, runs no model,
refits no parameter, and creates no RESULT, PRED, CLAIM, or KNOW artifact.

The gate uses only committed evidence: the ZnSe row file, the source manifest,
the TASK-0870 source-rights decision, the campaign profile/page, and the routed
effective-mass transfer negative memory.

## Source-Rights Boundary

The ZnSe route is usable only in a narrow form:

- source: Toufanian et al. 2021, DOI `10.1021/acs.chemmater.1c02501`;
- row basis: limited factual extract with attribution;
- source bytes redistribution: not allowed;
- committed data class: re-expressed factual numeric rows only;
- forbidden bytes: publisher PDF, figures, supporting information, and Table 1
  image;
- license context: ACS and ChemRxiv v4 recorded as `CC BY-NC-ND 4.0`, PMC mirror
  as NIHPA author manuscript, not a CC-BY source-byte grant.

This is enough for a bounded source-aware comparison over the existing committed
rows. It is not permission to redistribute source artifacts, expand the table,
or turn the source decision into a design-law claim.

## Frozen Input Set

The frozen ZnSe input surface for later task scoping is exactly:

- dataset id: `qd-0004-toufanian-2021-znse-absorption`;
- source id: `toufanian-2021-znse`;
- material: ZnSe;
- morphology: spherical;
- size axis: direct SAXS `diameter_nm`;
- property axis: optical `absorption_peak_eV` from 1S sample nomenclature;
- row provenance: direct table-derived factual numeric extract;
- row count: 10;
- included entry ids:
  - `toufanian-2021-znse-qd361`
  - `toufanian-2021-znse-qd364`
  - `toufanian-2021-znse-qd375`
  - `toufanian-2021-znse-qd383`
  - `toufanian-2021-znse-qd390`
  - `toufanian-2021-znse-qd397`
  - `toufanian-2021-znse-qd405`
  - `toufanian-2021-znse-qd410`
  - `toufanian-2021-znse-qd419`
  - `toufanian-2021-znse-qd422`

A later benchmark must consume this row set as committed. It must not add,
remove, relabel, rederive, or reorder rows after seeing metrics unless a new
row-curation task explicitly authorizes and reviews that change first.

## Admissible Comparison Axes

A future transfer task may compare only predeclared axes that preserve the
InP/ZnSe separation:

- InP source surface: the existing Almeida InP direct rows, kept separate from
  ZnSe and from calibration-derived Yu/Moreels rows.
- ZnSe source surface: the ten Toufanian direct SAXS rows above.
- Size semantics: InP tetrahedral edge-length/TEM semantics and ZnSe spherical
  SAXS diameter semantics must be handled by a predeclared conversion or by
  reporting a sensitivity framing before reveal.
- Property semantics: absorption peak energy only; do not merge emission peaks,
  bandgap, calibration curves, or device metrics.
- Controls: include source/material mean controls and a shuffled-size or other
  no-size control fixed before any new holdout inspection.
- Public interpretation: transfer, failure, or sensitivity memory only; no
  material recommendation, device-performance, biomedical, or design-law text.

## Leakage And Do-Not-Repeat Risks

The prior effective-mass transfer route is already negative memory, not an
invitation to tune a rescue:

- TASK-0850 found that the fixed bulk reduced-mass prefactor worsened the
  primary InP -> ZnSe and ZnSe -> InP transfer directions relative to the
  bulk-gap-only route and lost to the strongest controls.
- TASK-0871 routed that evidence as sandbox-only negative memory and explicitly
  blocked rerunning the same surface with tuned masses, coefficients, exponents,
  geometry mappings, thresholds, or post-hoc favorable framing.
- The task YAML points to
  `docs/reviews/quantum-effective-mass-negative-memory-routing.md` as the
  operative negative-memory reference for future task authors.

## Readiness Decision

The row set is frozen and source-ready for a future bounded task, but a new
transfer benchmark is not automatically READY. The correct campaign posture is:

`FROZEN_ROWS_READY_TRANSFER_BENCHMARK_NEEDS_MAINTAINER_DECISION`

Maintainer choice is needed because a later task must decide whether it is:

1. a strict replay/publication-preflight of the existing bulk-gap-only transfer
   memory;
2. a no-new-fit negative-control package that preserves prior failures; or
3. a genuinely new predeclared transfer question with changed source surface or
   physically justified model inputs before scoring.

Without that decision, another benchmark risks duplicating the already-routed
negative memory or selecting a favorable framing after reveal.

## Future Task Shape

A safe future task should state all of the following up front:

- exact frozen input paths and row ids;
- InP/ZnSe size-harmonization rule or a declared sensitivity pair;
- model family and all fixed physical inputs before seeing target residuals;
- control baselines and survival threshold;
- no-refit/no-correction-search rule;
- no source-byte redistribution rule;
- output routing as sandbox/review memory unless Gate A publication is
  separately authorized and passes.

## Stop Conditions

Stop before running or packaging metrics if the future task tries to:

- add or edit ZnSe rows;
- vendor source bytes or images;
- mix ZnSe with calibration-derived Yu/Moreels rows as if all were direct
  measurements;
- tune model parameters on the target material;
- reuse the failed effective-mass route without a new source surface or
  maintainer-approved replay purpose;
- promote a quantum-dot design law, material recommendation, biomedical claim,
  device-performance claim, RESULT, PRED, CLAIM, or KNOW artifact.

## Output Routing

- Task verdict: `FROZEN_ROWS_READY_TRANSFER_BENCHMARK_NEEDS_MAINTAINER_DECISION`.
- Canonical destination: `docs/reviews/` transfer-readiness note.
- Review tier: none.
- Gate A status: not attempted.
- Gate B status: not attempted.
- Claim impact: none.
- Knowledge impact: none.
- Prediction impact: none.
- Result impact: none; no benchmark metrics or canonical result artifact.
- Dataset impact: none; `qd-0004` rows and source manifest are unchanged.
- Remaining blocker: maintainer must approve the exact future transfer task
  shape before any new benchmark, replay package, or public result wording.
