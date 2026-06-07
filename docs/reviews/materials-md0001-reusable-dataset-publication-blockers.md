# Materials MD-0001 Reusable-Dataset Publication Blockers

Task: `TASK-0643`
Domain: Materials property residuals
Mode: planning only
Verdict: `WAIT_FOR_MD0002_PAIRING_KEEP_MD0001_INTERNAL_SEED`

## Purpose

This note packages the exact blockers before `MD-0001` can be treated as an
external reusable dataset or DOI-ready dataset package. It does not fetch rows,
change values, run metrics, publish a dataset, create claims, or promote any
result.

The decision is conservative: `MD-0001` remains useful as internal seed data,
but external dataset posture should wait for `MD-0002` pairing unless
maintainers explicitly request a metadata-only package task.

## Evidence Reviewed

- `docs/reviews/materials-md0001-result-or-dataset-publication-decision.md`
- `docs/reviews/materials-md0001-benchmark-promotion-preflight.md`
- `docs/reviews/materials-md0001-independent-baseline-replay.md`
- `docs/reviews/materials-md0001-split-sensitivity-audit.md`
- `docs/reviews/materials-md0001-band-gap-null-control-audit.md`
- `data/materials/source_manifest.yaml`
- `data/materials/holdout_manifest.yaml`
- `data/materials/schema.md`

## Blocker Checklist

| Area | Current state | Publication blocker |
| --- | --- | --- |
| Citation and reuse | Materials Project source, CC BY 4.0 posture, attribution notes, and source snapshot are recorded. | External package still needs maintainer-approved citation wording and reuse-facing README language before DOI posture. |
| Source version | Source database version and retrieval date are recorded in the manifest. | No blocker for internal use; external package should carry the same version pin in release-facing metadata. |
| Checksums | `MD-0001` snapshot checksum is recorded in the holdout manifest. | No blocker for internal use; external package should expose checksum and file-level scope clearly. |
| Row schema | `data/materials/schema.md` defines computed DFT property axes, units, provenance, and stop conditions. | External package should include a concise row-schema summary and avoid implying measured experimental values. |
| Excluded rows | Inclusion scope is clear: stable binary oxides, computed DFT source, two separate property axes. | A reusable package still needs an explicit excluded-row / non-covered-row summary so downstream users know what was not included. |
| Holdout boundary | `MD-0001` holdout manifest forbids benchmark claims, prediction registry entries, and live fetch. | Any result or claim promotion remains blocked; dataset packaging must not be presented as benchmark validation. |
| Public wording | Existing reviews preserve computed-DFT and benchmark-residual language. | Public wording must avoid material design, synthesis, discovery, measured-property, or generalization claims. |

## Property-Axis Separation

Formation energy and band gap must remain separate dataset axes.

Formation energy has the stronger internal benchmark posture from prior audits:
it is the better candidate for a future widened Materials adapter or `MD-0002`
pairing.

Band gap remains split-fragile. Prior checks found band-gap behavior useful as a
diagnostic signal, but not robust enough for external dataset-promotion wording
or shared benchmark-result wording. A dataset package must not pool band-gap
rows with formation-energy rows, must not present band-gap residuals as a stable
result, and must not use band-gap metrics to justify publication posture.

## Recommended Route

Recommended route: wait for `MD-0002` pairing and keep `MD-0001` as internal
seed data.

This is the best match to the existing `MD0002_WIDENING_FIRST` decision:
`MD-0001` is useful, pinned, and auditable, but external dataset posture would
be stronger after a widened or paired dataset clarifies reuse scope and reduces
the chance that a split-fragile axis dominates interpretation.

Fallback route if maintainers need near-term packaging: create a separate
metadata-only dataset package task. That task should write citation, reuse,
checksum, source-version, schema, excluded-row, and public wording notes only.
It must not add rows, run metrics, change values, publish a DOI, or promote
results.

Not recommended: external publication of `MD-0001` alone as a reusable dataset
with benchmark language.

## Output Routing Summary

- New dataset rows: none
- Changed dataset values: none
- New result artifact: none
- New claim artifact: none
- External dataset publication: not authorized
- Current routing: `MD-0001` remains internal seed data and a future
  `MD-0002` pairing candidate
