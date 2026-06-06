# Materials MD-0001 Result Or Dataset Publication Decision

Task: `TASK-0614`
Domain: Materials Property Residuals
Mode: planning only
Verdict: `MD0002_WIDENING_FIRST`

## Scope

This review adjudicates the next durable Materials path after the committed
MD-0001 formation-energy controls and split-sensitivity evidence. It adds no
rows, fetches no live Materials Project data, computes no new metrics, and does
not create a result, prediction, claim, knowledge artifact, DOI, or external
dataset package.

Inputs reviewed:

- `docs/reviews/materials-md0001-baseline-residual-benchmark.md`
- `docs/reviews/materials-md0001-independent-baseline-replay.md`
- `docs/reviews/materials-md0001-band-gap-null-control-audit.md`
- `docs/reviews/materials-md0001-benchmark-promotion-preflight.md`
- `docs/reviews/materials-md0001-formation-energy-null-control-audit.md`
- `docs/reviews/materials-md0001-split-sensitivity-audit.md`
- `docs/reviews/materials-md0002-wider-replication-slice-plan.md`
- `docs/reviews/materials-research-factory-adapter-fit-review.md`
- `docs/publication-roadmap.md`
- `docs/campaigns/materials-property-residuals.md`

## Evidence Summary

Formation energy remains the only Materials axis with a robust current signal:

- The committed MD-0001 baseline found `cation_group_mean` at holdout MAE
  `0.646030` eV/atom, compared with global-median holdout MAE `0.967090`.
- The formation-energy null-control audit found the real cation-group baseline
  beat the global null and was not matched by deterministic label or cation-group
  shuffle controls in the checked permutation runs.
- The split-sensitivity audit found the formation-energy baseline ordering
  `split_robust`: `cation_group_mean` won `5 / 5` seeded random holdouts with a
  seeded mean MAE margin larger than split noise.

Band gap stays diagnostic and split-fragile:

- The committed band-gap signal was weaker and validation/holdout ordering was
  mixed.
- The split-sensitivity audit found the band-gap ordering `split_sensitive`.
- Band gap should remain out of the next promotion or factory scope unless a
  later larger slice changes the evidence.

Promotion remains blocked:

- `TASK-0566` found the frozen MD-0001 holdout manifest disallows RESULT, PRED,
  CLAIM, and benchmark promotion from this slice.
- The benchmark verdict remains `INCONCLUSIVE`; the useful formation-energy
  evidence is diagnostic baseline/control memory, not a promoted scientific
  result.
- MD-0001 rows are computed DFT values only and do not support material-design,
  synthesis, device, biomedical, or discovery wording.

## Route Decision

Chosen route: `MD0002_WIDENING_FIRST`.

Rationale:

1. `RESULT_PROMOTION_PREFLIGHT` is not the right next route because the existing
   preflight already found a hard manifest boundary against promotion.
2. `DATASET_PUBLICATION_PACKAGE` is premature as the primary next route because
   MD-0001 is small, pilot-scoped, and still needs citation/reuse/version
   packaging before any external dataset posture. It remains a reusable-dataset
   candidate, not a publication package.
3. `DO_NOT_PROMOTE` is true for result/claim promotion but too weak as the
   overall next Materials action: formation energy has survived enough controls
   to justify a larger, source-pinned replication slice.
4. `MD0002_WIDENING_FIRST` directly tests whether the MD-0001 formation-energy
   advantage generalizes beyond stable binary oxides while keeping the band-gap
   question separate and underpowered evidence visible.

The recommended next task is the existing blocked `TASK-0631` path: prepare an
MD-0002 acquisition preflight package for Materials Project stable ternary
oxides. That preflight should remain metadata-only and no-live-fetch unless the
maintainer later authorizes acquisition.

## Dataset Publication Blockers

If maintainers later choose a dataset-publication package for MD-0001, the
missing pieces are:

- final citation/reuse wording for a reusable dataset package;
- source version and checksum presentation suitable for an external dataset
  record;
- explicit row-schema and excluded-row summary for public reuse;
- clear separation between computed DFT rows and any measured-property language;
- public wording that states formation energy and band gap are separate axes;
- a maintainer-approved decision on whether MD-0001 is published alone or paired
  with a wider MD-0002 replication slice.

These blockers do not prevent the MD-0002 preflight. They prevent treating
MD-0001 as an externally publishable dataset package in this task.

## Guardrails For The Follow-Up

The next MD-0002 preflight should:

- keep formation energy and band gap separate;
- treat formation energy as the primary retest axis;
- treat band gap as split-fragile unless the larger slice changes that;
- avoid live fetches, committed MD-0002 rows, material recommendations, synthesis
  guidance, device claims, biomedical claims, and discovery wording;
- define query contract, row cap, version pin, checksum plan, citation/reuse
  metadata, and holdout/no-peek manifest plan before acquisition.

## Output Routing

Canonical destination: this review note.

Review tier: source/benchmark planning only. Gate A is not attempted because the
frozen MD-0001 holdout manifest blocks result promotion. Gate B is not
applicable.

Claim impact: none. No material-property claim, material-design claim, synthesis
claim, device claim, biomedical claim, prediction, or new-law statement is
created.

Knowledge impact: none. MD-0001 remains reviewed diagnostic memory and a
reusable-dataset candidate; it is not promoted to accepted knowledge here.

Publication blocker: result publication remains blocked by the frozen manifest.
Dataset publication remains blocked on citation/reuse/version packaging and a
maintainer decision about whether MD-0001 is sufficient alone or should be
paired with a wider MD-0002 replication slice.
