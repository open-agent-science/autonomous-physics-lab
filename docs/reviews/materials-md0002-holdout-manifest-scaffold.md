# Materials MD-0002 Holdout Manifest Scaffold

Task: `TASK-0644`
Domain: Materials Property Residuals
Mode: planning only
Verdict: `SCAFFOLD_DEFINED_NO_ROWS_NO_METRICS`

## Purpose

This review records the no-peek split scaffold for the planned `MD-0002`
stable ternary oxides slice. It creates
`data/materials/md0002_holdout_manifest.yaml` but does not fetch Materials
Project rows, commit value-bearing row ids, compute metrics, or promote a
result, claim, prediction, or dataset publication.

The manifest is intentionally a scaffold: source version, snapshot checksum,
raw snapshot path, dataset files, and row counts remain acquisition-time
placeholders.

## Evidence Reviewed

- `docs/reviews/materials-md0002-wider-replication-slice-plan.md`
- `docs/reviews/materials-md0001-result-or-dataset-publication-decision.md`
- `data/materials/holdout_manifest.yaml`
- `data/materials/schema.md`

## Scaffold Scope

`MD-0002` is scoped to Materials Project stable ternary oxides:

- exactly three distinct elements;
- one oxygen element;
- two non-oxygen cations;
- computed DFT provenance only;
- stable rows under the future pinned Materials Project convention.

This keeps `MD-0002` comparable to `MD-0001` while widening from binary to
ternary oxides. It does not mix providers, measured rows, elastic moduli, or
new property axes.

## Property Axis Policy

The scaffold declares two separate axes:

| Axis | Units | Boundary |
| --- | --- | --- |
| `formation_energy_per_atom` | `eV_per_atom` | Primary retest axis for the stronger MD-0001 signal. |
| `band_gap` | `eV` | Kept visible but separate because MD-0001 band gap was split-fragile. |

The axes must not be pooled. Any future metric report must keep formation
energy and band gap separate and must not use band-gap behavior to promote the
formation-energy result or vice versa.

## Split Candidates

The manifest records these pre-score split candidates:

- material-id modulo buckets;
- seeded random split families;
- cation-pair family groups;
- exact spacegroup or predeclared structure/prototype buckets;
- property-range bins declared separately for each property kind;
- source-version splits when a later second snapshot exists.

All split thresholds, seeds, grouping rules, and exclusion policies must be
frozen before residuals, model errors, or benchmark metrics are inspected.

## No-Peek Boundaries

The scaffold forbids:

- live fetch;
- value-bearing row ids;
- baseline metrics or residual maps;
- post-score split tuning;
- pooling property axes;
- mixing computed DFT with measured or model-only rows;
- material-design, synthesis, device, biomedical, discovery, or new-law claims.

The future acquisition task must replace placeholders with pinned source
metadata before any benchmark can bind to the manifest.

## Output Routing Summary

- Task verdict: `SCAFFOLD_DEFINED_NO_ROWS_NO_METRICS`
- Canonical destination: `data/materials/md0002_holdout_manifest.yaml` and this
  review note
- Review tier: `none`
- Gate A status: not applicable; no result publication attempted
- Gate B status: not applicable; no replay attempted
- Claim impact: none
- Knowledge impact: none
- Publication blocker: MD-0002 remains unavailable for scoring until a later
  acquisition task pins source version, checksum, row counts, and admissible row
  metadata.
