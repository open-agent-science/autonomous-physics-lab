# Quantum Direct-Source Candidate Brief

Task: `TASK-0556`
Campaign: Quantum Size Effects
Contributor: `akutenyov`
Status: source-candidate classification only

## Scope

This brief classifies already-known Quantum Size Effects direct-source
candidates using the `blocker_type` vocabulary from the
[Published-Source and Reusable-Dataset Standard](../../published-source-dataset-standard.md)
and the lane routing in
[Source Acquisition, Pinning, and Extraction Lane](../../source-acquisition-lane.md).

It reviews repository memory only:

- [Quantum Size Effects campaign](../../campaigns/quantum-size-effects.md)
- [Quantum direct-source artifact intake](../../quantum-direct-source-artifact-intake.md)
- [source_manifest.yaml](../../../data/quantum_dots/source_manifest.yaml)
- [Norris-Bawendi source-artifact review](../../reviews/quantum-norris-bawendi-source-artifact-review.md)
- [Kang-Wise source-path review](../../reviews/quantum-kang-wise-1997-pbs-source-path.md)
- [Jasieniak source-artifact package review](../../reviews/quantum-jasieniak-2011-source-artifact-package.md)
- [Yu direct-absorption seed investigation](../../reviews/quantum-size-direct-absorption-seed-review.md)
- [Moreels row-level extension review](../../reviews/quantum-size-moreels-2009-pbs-row-level-extension-review.md)

This brief does not copy or transcribe measurement values, run digitization,
add `qd-*.yaml` rows, run baseline metrics, modify claims, or promote a
result. It is a planning/source-routing artifact.

## Candidate Classifications

| Candidate | Source locator | Expected row type | `blocker_type` | License / redistribution posture | Extraction feasibility | Next unblock lane |
| --- | --- | --- | --- | --- | --- | --- |
| `norris-bawendi-1996-prb-cdse-band-edge` | DOI: <https://doi.org/10.1103/PhysRevB.53.16338>; artifact note: [README](../../../data/quantum_dots/source_artifacts/norris-bawendi-1996-prb-cdse-band-edge/README.md) | `digitization_required`; prior review verified figure-derived evidence and no usable printed direct table. | `T2_extraction_tool` | APS / Physical Review B source; DOI-pinned metadata and extraction ledger are acceptable, but publisher PDFs, figures, or rasterized source panels must not be committed without permission. | High relative to the other candidates once a legitimate source copy is available: the required future artifact shape is already specified and table-derived curation has been ruled out. | Deterministic WebPlotDigitizer-class package under `data/quantum_dots/digitization/norris-bawendi-1996-prb-cdse-band-edge/`, then a separate row-curation task if enough reviewed points remain. |
| `kang-wise-1997-josab-pbs-band-edge` | DOI: <https://doi.org/10.1364/JOSAB.14.001632>; review: [Kang-Wise source path](../../reviews/quantum-kang-wise-1997-pbs-source-path.md) | `blocked`; visible tables are model-parameter tables, while any direct rows would require legitimate access to source figures or non-visible article content. | `T1_access` | Optica / JOSA B source; visible metadata only. Article content and figures are not redistributable in this repo without explicit permission or a maintainer-held artifact. | Low until access is resolved. The current repository memory records no direct rows, no machine-readable supplement, and no figure-digitization artifact. | Maintainer-provided source artifact or access review. Only after that should a curator decide whether the source routes to digitization or remains negative memory. |
| `jasieniak-2011-acs-nano-band-edge` | DOI: <https://doi.org/10.1021/nn201681s>; artifact note: [README](../../../data/quantum_dots/source_artifacts/jasieniak-2011/README.md) | Potential `table_derived` from Supporting Information, with figure-derived fallback only if a deterministic digitization artifact exists. | `T1_access` | ACS source; metadata-only posture. Do not commit ACS PDFs, figures, or full tables unless redistribution is explicitly allowed. | Medium if a maintainer supplies the official Supporting Information or a non-copyrighted extraction; blocked for an ordinary agent because the SI/table artifact is not checksum-pinned in the repo. | Maintainer-provided SI/table artifact with checksum and license decision, or a non-copyrighted table extraction. Row curation remains a later task. |
| `yu-2003-cm-absorption` | DOI: <https://doi.org/10.1021/cm034081k>; review: [Yu direct-absorption investigation](../../reviews/quantum-size-direct-absorption-seed-review.md) | `digitization_required` for direct measurement rows. Existing `qd-0001` rows are calibration-derived from sizing polynomials and must stay separate. | `T2_extraction_tool` | ACS source; citation and DOI metadata are acceptable, but publisher figures/tables are not redistributable without permission. | Medium. The direct surface appears to be Figure 2 scatter points with mixed provenance; an LLM-only read is below the precision floor and cannot create rows. | Deterministic figure-digitization run with axis calibration, extracted points, per-point uncertainty, and primary-source attribution. |
| `moreels-2009-acs-nano-pbs-absorption` | DOI: <https://doi.org/10.1021/nn900863a>; review: [Moreels row-level extension](../../reviews/quantum-size-moreels-2009-pbs-row-level-extension-review.md) | Potential direct absorption rows only if source table/figure evidence is separately verified. Existing `qd-0002` rows are calibration-derived from the published sizing relation. | `T2_extraction_tool` | ACS source; metadata-only posture for publisher material unless permission is granted. Curated factual rows may be possible only after a compliant extraction record. | Medium-low. The current committed dataset is useful as a calibration surface but does not provide direct measurement rows. A future pass must find and extract direct first-exciton evidence instead of reusing the formula. | Source-artifact review plus deterministic extraction runner; row curation only after direct row provenance is verified. |

## Recommendation

The clearest next bounded task is an extraction-runner task for
`norris-bawendi-1996-prb-cdse-band-edge`.

Rationale:

- the source locator is concrete;
- prior review has already ruled out table-derived curation;
- the expected row type is therefore unambiguous: `digitization_required`;
- the needed artifact layout is already recorded in the source-artifact package;
- the work is bounded to a deterministic digitization package, not immediate
  row curation or benchmark scoring.

Suggested follow-up task:

```yaml
title: "Run deterministic Quantum digitization preflight for Norris-Bawendi 1996"
type: scientific_dataset
status: READY
requirements:
  - "Use a legitimate source copy for DOI 10.1103/PhysRevB.53.16338."
  - "Create a WebPlotDigitizer-class artifact with axis calibration, extracted points, tool/version notes, and uncertainty notes."
  - "Do not add qd rows, run baselines, or create claims."
  - "Record license/redistribution posture and keep publisher figures/PDFs out of the repo unless permission is explicit."
accepted_outputs:
  - "data/quantum_dots/digitization/norris-bawendi-1996-prb-cdse-band-edge/"
  - "docs/reviews/quantum-norris-bawendi-1996-digitization-runner.md"
```

## Output Routing Summary

- Task verdict: `VALID` as source-candidate classification.
- Canonical destination: this source-candidate brief under
  `docs/source-candidates/quantum/`.
- Review tier: `none`; this is not a `RESULT-*`, `PRED-*`, `CLAIM-*`, or
  `KNOW-*` artifact under the
  [Result Promotion Protocol](../../result-promotion-protocol.md).
- Claim impact: none.
- Knowledge impact: none.
- Dataset impact: no rows, no source files, no digitization artifacts, and no
  manifest state changes.
- Benchmark impact: no baseline or holdout gate was run.
