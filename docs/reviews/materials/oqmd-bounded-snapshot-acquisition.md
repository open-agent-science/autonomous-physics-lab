# TASK-1042: bounded OQMD live-API snapshot

## Scope

This task executes the bounded acquisition authorized by TASK-1026. It fetches
one dated OQMD live-API response, preserves the raw response, and creates a
normalized computed-DFT source slice after identifier-only overlap screening
against MD-0002. It does not claim byte identity with the 21.1 GB OQMD v1.8
dump.

No train/holdout split, target summary, residual, fit, benchmark metric,
RESULT, PRED, CLAIM, KNOW artifact, or material recommendation was created.

## Retrieval identity

- Fetch window: 2026-07-14T09:24:15.6158604Z to
  2026-07-14T09:24:34.6962444Z.
- API route: official oqmdapi/formationenergy, API version 1.0.
- Response timestamp: 2026-07-14 04:24:35 as returned by OQMD.
- Pagination: one page, offset 0, limit 1000; 373 returned and available;
  more_data_available is false.
- Raw bytes: 94,115; SHA-256
  d39fc1c126434e9b178f88ee1afcaf15938993f2e6fc1528cdf5c4b0ea3bcb35.
- Normalized bytes: 114,834; SHA-256
  af8991aefda6f408a3ad33251aa5564f5fed37a7d527b696d68442971bc978a4.

The raw and normalized snapshots and their manifest are under data/materials/.
OQMD data are CC BY 4.0; the registry preserves the two canonical OQMD
citations and records that the raw response is vendored.

## Predicate and semantics

The request uses the TASK-1026 source-side predicate: exactly one
alkali/alkaline-earth element, one Sc-Zn first-row transition element, oxygen,
ntypes=3, stability=0, and noduplicate=True. All 373 returned rows pass that
predicate and have unique entry_id values. For this response,
duplicate_entry_id identifies the same preferred entry rather than being null;
this provider behavior is recorded and does not create a second row.

delta_e remains OQMD computed formation energy under OQMD's canonical
reference/correction conventions. band_gap remains the OQMD DFT-PBE band gap.
Neither field is declared numerically interchangeable with Materials Project
formation_energy_per_atom, and neither field was used to select, narrow,
deduplicate, or overlap-screen the rows.

## Overlap and cap result

| Check | Count |
| --- | ---: |
| Raw OQMD rows | 373 |
| MD-0002 unique reduced compositions | 360 |
| Rows excluded by reduced-composition overlap | 201 |
| Composition plus space-group coincidences | 90 |
| Rows excluded for required-field missingness | 0 |
| Normalized rows | 172 |
| Hard cap | 2,000 |

The overlap check uses reduced composition only. Composition plus space-group
coincidences are logged as an identifier audit and were already excluded by
the conservative composition rule. The exclusion ledger records identity
fields and reasons; no target threshold was applied.

## Verdict

**SNAPSHOT_READY_FOR_SPLIT_FREEZE.** The dated, hash-pinned OQMD API snapshot
is within the cap, satisfies the frozen predicate, has explicit OQMD
computed-DFT semantics, and is composition-disjoint from the included MD-0002
surface after conservative exclusion. This verdict authorizes a later no-peek
split-freeze task only.

## Limitations and routing

- The API response has no database-version field. The artifact is a dated
  post-v1.8 live snapshot, not an exact v1.8 dump reconstruction.
- OQMD and Materials Project use different DFT/correction pipelines. Their
  similarly named energies must remain on separate within-source axes.
- MD-0002 has no ICSD lineage field, so composition exclusion is the
  conservative overlap control.
- The snapshot is computed DFT evidence, not an independent experimental
  replication or a materials-design dataset.
- Gate A and Gate B are not attempted; claim and knowledge impact is none.
