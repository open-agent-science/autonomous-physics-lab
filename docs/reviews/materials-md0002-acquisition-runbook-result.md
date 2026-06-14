# Materials MD-0002 Acquisition Runbook Result

**Task:** `TASK-0699`
**Campaign:** Materials Property Residuals
**Status:** stopped by predeclared row cap
**Verdict:** `CAP_EXCEEDED_NO_DATASET_COMMITTED`

## Scope

`TASK-0699` executed the maintainer-gated Materials Project acquisition check
for `MD-0002` using `MP_API_KEY` from the local environment. The key was not
committed, written to an artifact, or printed in command output.

The task did not create MD-0002 dataset files because the frozen acquisition
contract requires a hard stop when the included row count exceeds the
predeclared 1500-row cap per axis.

## Source Pin

| Field | Observed value |
| --- | --- |
| Source | Materials Project REST API |
| Heartbeat `db_version` | `2026.04.13` |
| API version | `0.87.0rc14.dev3+g264f4151c` |
| Query date | `2026-06-13` |
| Query endpoint | `https://api.materialsproject.org/materials/summary/` |
| Candidate predicates | `elements=O`, `nelements=3`, `is_stable=true` |
| Page size | `1000` |
| Candidate pages fetched | `4` |

Requested fields:

```text
material_id, formula_pretty, composition, nelements, elements,
energy_above_hull, is_stable, formation_energy_per_atom, band_gap,
symmetry, theoretical, builder_meta, origins
```

The heartbeat also reported `pymatgen=2026.5.18` and suffix `blue`.

## Row-Cap Check

The bounded candidate query returned:

```text
raw_candidate_rows: 3473
```

The acquisition then applied the declared stable-ternary-oxide inclusion intent:

- exactly three elements;
- includes oxygen;
- stable row (`is_stable=true`, `energy_above_hull=0.0`);
- both `formation_energy_per_atom` and `band_gap` present;
- excluded common non-oxygen anion chemistries from the cation-pair slice:
  `H`, `N`, `F`, `Cl`, `Br`, `I`, `S`, `Se`, `Te`.

This conservative classifier still produced:

```text
included_rows_per_axis: 2738
row_cap_per_axis: 1500
cap_status: EXCEEDED
```

Observed excluded common non-O anion occurrences in the candidate set:

| Element | Candidate occurrence count |
| --- | ---: |
| `S` | `150` |
| `Te` | `149` |
| `Se` | `131` |
| `I` | `79` |
| `F` | `76` |
| `H` | `74` |
| `N` | `59` |
| `Cl` | `39` |
| `Br` | `18` |

Because `2738 > 1500`, the contract requires stopping and reporting the count
and predicate. The run did not silently narrow, subsample, truncate, compute
metrics, or commit value-bearing row data.

## Artifacts Not Created

The following acquisition artifacts were intentionally **not** created because
the row cap was exceeded:

- `data/materials/snapshots/materials_project_stable_ternary_oxides_2026.04.13.json`
- `data/materials/md-0002-materials-project-formation-energy.yaml`
- `data/materials/md-0002-materials-project-band-gap.yaml`
- populated value-bearing row assignments in
  `data/materials/md0002_holdout_manifest.yaml`

`data/materials/md0002_holdout_manifest.yaml` remains a no-peek scaffold until
a narrowed, reviewed acquisition predicate clears the cap.

## Recommended Follow-Up

Open a separate pre-acquisition amendment or task to narrow the stable ternary
oxide predicate before any value-bearing commit. Acceptable narrowing should be
reviewed before another fetch and could include a more precise cation-oxide
definition, chemistry family restriction, or another predeclared stable subset.

Do not use post-fetch row inspection, residual behavior, material desirability,
or property values to choose the narrowing rule.

## Guardrails Preserved

- `MP_API_KEY` was used only from the local environment and was not committed.
- No raw Materials Project rows, material identifiers, normalized MD-0002
  dataset rows, residuals, benchmarks, predictions, recommendations, `RESULT-*`,
  `PRED-*`, `CLAIM-*`, or knowledge-promotion artifacts were committed.
- Formation energy and band gap remain separate planned axes.
- No no-peek split assignment was populated because the acquisition stopped
  before a valid capped dataset existed.

## Output Routing Summary

- Task verdict: `CAP_EXCEEDED_NO_DATASET_COMMITTED`.
- Canonical destination: this review note plus the `TASK-0699` review-ready
  cap-exceeded state.
- Review tier: source/data acquisition preflight execution only.
- Gate A status: `not_attempted`; no dataset artifact was created.
- Gate B status: `not_applicable`; no replay or benchmark metric was attempted.
- Claim impact: no claim change.
- Knowledge impact: workflow memory only; MD-0002 acquisition needs a narrowed
  pre-fetch predicate before value-bearing publication.
- Publication blocker: MD-0002 remains unpublished because the frozen predicate
  exceeded the hard cap.
