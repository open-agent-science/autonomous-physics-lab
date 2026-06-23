# Quantum Independent Transfer Source Scout

**Task:** `TASK-0810`
**Campaign:** `quantum-size-effects`
**Selected route:** Norris-Bawendi 1996 CdSe first-exciton / band-edge figure route
**Source ID:** `norris-bawendi-1996-prb-cdse-band-edge`
**Verdict:** `SOURCE_BLOCKED`

## Scope

This scout selects exactly one independent transfer route and records whether it
is ready for a future row-curation task. It does not add rows, fetch live data,
run metrics, edit `qd-0003`, open `TASK-0226`, or create RESULT/PRED/CLAIM/KNOW
artifacts.

## Why This Route

Norris-Bawendi 1996 is the strongest fully identified non-Almeida route already
preserved in the committed Quantum campaign memory:

- independent source from Almeida 2023;
- independent material family (`CdSe` rather than `InP`);
- potentially relevant first-exciton / band-edge optical surface;
- existing manifest entry and metadata-only source-artifact package;
- prior verification already established the key blocker class.

This route is not selected because it is ready. It is selected because the
repository has enough committed provenance to classify it without speculation
and avoid reopening the same source in another vague scout.

## Evidence Reviewed

- `data/quantum_dots/source_manifest.yaml`
- `data/quantum_dots/source_artifacts/norris-bawendi-1996-prb-cdse-band-edge/README.md`
- `docs/reviews/quantum-norris-bawendi-source-artifact-review.md`
- `docs/reviews/quantum-pmc-arxiv-direct-table-source-attempt.md`
- `docs/reviews/quantum-open-licensed-first-source-selection-application.md`
- `docs/quantum-direct-measurement-digitization-protocol.md`
- `docs/campaigns/quantum-size-effects.md`

## Admissibility Table

| Gate | Assessment |
| --- | --- |
| Source identity | Concrete: Norris, D. J.; Bawendi, M. G., Physical Review B 53, 16338-16346 (1996), DOI `10.1103/PhysRevB.53.16338`. |
| Independence from Almeida | Strong: different publication, material (`CdSe`), morphology/source family, and historical measurement route. |
| Source accessibility | Blocked for row work: DOI-pinned metadata exists, but no redistributable source copy, checksum-pinned PDF, figure raster, or extraction package is committed. |
| License/reuse posture | Closed APS publication posture; repository records metadata only. Tables/figures/PDFs must not be redistributed without a maintainer-approved license decision. |
| Row-level availability | Not ready: `TASK-0364` found zero printed tables and no inline size-to-energy value pairs in the provided PDF inspection. The data-bearing surface is figure-derived. |
| Property-kind semantics | Potentially useful for `absorption_peak_eV` or `bandgap_eV`, but a future task must separate first-exciton, assignment-derived, and model-derived quantities before rows exist. |
| Size-axis semantics | Manifest route records `radius_nm`; future digitization must verify radius-vs-diameter and axis units from the target panel before row curation. |
| Direct/calibration status | Not calibration-derived by default, but not yet direct row-level evidence either. It requires a WebPlotDigitizer-class extraction with axis calibration and per-point uncertainty. |
| Holdout feasibility | Good in principle: CdSe rows would provide a cross-material/source transfer test away from the Almeida InP slice, if at least six admissible points survive extraction. |
| Leakage risk | Low relative to Almeida if rows are curated from the primary Norris-Bawendi source only. High if later agents mix it with Yu 2003 calibration curves or back-computed sizing equations. |
| Open-licensed-first policy | This is a Tier 4 fallback. `TASK-0751` recommends scouting Tier 1/2 open tabular sources before spending new extraction effort on closed figure-derived routes. |

## Blocker Class

`BLOCKER_FIGURE_DERIVED_CLOSED_SOURCE_NO_DIGITIZATION_ARTIFACT`

The route is scientifically plausible but not row-ready. A metadata-only
source-artifact package is not enough for `qd-*.yaml` rows, and LLM-estimated
coordinates are explicitly forbidden.

## Future Task Shape If Maintainer Chooses This Route

Only a later maintainer-approved row task should proceed, and only with this
bounded shape:

1. Record a license/reuse decision for the exact source copy or keep the copy
   metadata-only.
2. Record SHA-256 for any maintainer-supplied source file, if available.
3. Use a deterministic WebPlotDigitizer-class tool under
   `data/quantum_dots/digitization/norris-bawendi-1996-prb-cdse-band-edge/`.
4. Commit axis calibration anchors, extracted points, tool/version notes,
   coordinate uncertainty, and inclusion/exclusion decisions.
5. Add `qd-*` rows only after separating property kinds and rejecting model,
   calibration, or assignment-derived values that are not direct measurements.
6. Do not run baseline metrics in the row-curation task unless a separate
   benchmark task authorizes it.

## Recommendation

Do not open a Norris-Bawendi row-curation task yet unless the maintainer
explicitly chooses a Tier 4 closed figure route. The stronger next campaign move
is still the `TASK-0751` recommendation: scout one Tier 1/2 open tabular source
route before investing in closed-source figure digitization.

If the maintainer chooses to pursue Norris-Bawendi anyway, the next task should
be a deterministic digitization artifact task, not a benchmark or autonomous
correction task.

## No-Claim Wording

This scout does not support a quantum-dot design law, material recommendation,
device-performance claim, biomedical claim, universal size law, transfer
success claim, or discovery claim. It only records that one independent CdSe
route is blocked at the source/digitization gate.

## Output-Routing Summary

- **Canonical destination:** source-gate review note under `docs/reviews/`.
- **Review tier:** none; no RESULT/PRED/CLAIM/KNOW artifact.
- **Gate A status:** not applicable.
- **Gate B status:** not applicable.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Transfer-holdout blocker:** no license-cleared/checksum-pinned source copy
  and no deterministic figure-digitization artifact.

## Verdict

`SOURCE_BLOCKED`
