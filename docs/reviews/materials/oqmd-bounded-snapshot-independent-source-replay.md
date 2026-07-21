# TASK-1063: independent replay of the bounded OQMD source snapshot

## Verdict

**`INDEPENDENT_SOURCE_REPLAY_PASS`.** An independent session replayed the
committed source artifacts without contacting OQMD and reproduced the pinned
bytes, row counts, schema boundary, and conservative overlap accounting.

## Independent replay identity and environment

The maintainer replay was contributor-distinct from the TASK-1042 executor and
used a separate agent session. It did not contact OQMD or inspect target-value
summaries.

| Field | Recorded value |
| --- | --- |
| Contributor / GitHub | `gladunrv` |
| Agent tool | `Codex Desktop` |
| Model | `GPT-5` |
| Session ID | `codex-maintainer-pr1597-replay-20260718` |
| Operating system | `macOS 14.5 (build 23F79), arm64` |
| Python runtime | `Python 3.12.13` |
| Exact PR head | `e03d4628e7685cb9560e554a4b90771dda29f623` |

Exact commands, run with the recorded APL Python environment active:

```text
python -m pytest -n0 tests/test_materials_oqmd_independent_replay.py tests/test_materials_oqmd_bounded_snapshot.py tests/test_data_redistribution_declarations.py tests/test_docs_links.py
python -m physics_lab.cli validate-repo . --strict --fail-on-warnings
```

The replay produced `14 passed` and strict validation produced `0 ERROR, 0
WARNING`. It independently reproduced the raw bytes, hash, API-page identity,
373-row count, 201 reduced-composition exclusions, 90 composition-plus-space-
group coincidences, 172 retained rows, zero normalized MD-0002 composition
overlap, normalized hash and schema, OQMD property semantics, and the bounded
CC BY 4.0 redistribution posture. No split, target distribution, residual,
correlation, metric, model, RESULT, PRED, CLAIM, or KNOW artifact was computed.

## Pinned artifacts

| Surface | Bytes | SHA-256 | Rows |
| --- | ---: | --- | ---: |
| Raw API response | 94,115 | `d39fc1c126434e9b178f88ee1afcaf15938993f2e6fc1528cdf5c4b0ea3bcb35` | 373 |
| Normalized snapshot | 114,834 | `af8991aefda6f408a3ad33251aa5564f5fed37a7d527b696d68442971bc978a4` | 172 |

The raw response reports API version `1.0`, one complete page, 373 returned
and available rows, and no next page. Entry identifiers are unique. Every raw
row retains the declared ternary oxide predicate: `ntypes=3`,
`stability=0`, one oxygen-containing composition, and the provider's
`noduplicate=True` query.

## Independent accounting

The replay recomputed identifier-level counts from committed bytes and compared
them with the acquisition manifest:

- MD-0002 unique reduced compositions: 360.
- Raw OQMD rows excluded by reduced-composition overlap: 201.
- Composition plus space-group coincidences: 90.
- Required-field exclusions: 0.
- Remaining normalized rows: 172, below the hard cap of 2,000.
- Reduced-composition overlap between the normalized OQMD surface and the
  MD-0002 identity surface: 0.

The equality `373 - 201 - 0 = 172` closes the count ledger. Target values were
not used to select, narrow, or deduplicate rows.

## Schema and rights

Normalized rows retain the declared OQMD identifiers, computed-DFT fields, unit
labels, provenance class, and source snapshot ID. `delta_e` remains OQMD
computed formation energy in eV/atom under OQMD conventions; it is not treated
as numerically interchangeable with Materials Project
`formation_energy_per_atom`. OQMD attribution and CC BY 4.0 routing remain
pinned in the repository license registry.

## Boundary and routing

This replay validates source integrity only. It does not create a split,
inspect target summaries, fit a model, calculate a benchmark metric, or mutate
a RESULT, PRED, CLAIM, or KNOW artifact. Gate A and Gate B are not attempted.
The snapshot may proceed only to the separately reviewed identifier-only split
freeze and predeclared benchmark contract.
