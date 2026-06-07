# Exoplanet PS versus PSCompPars Query Boundary Review

- Task: `TASK-0647`
- Domain: Exoplanet Mass-Radius Benchmark
- Mode: planning-only source-protocol review (no rows fetched)
- Verdict: `KEEP_PS_DEFAULT_FLAG_QUERY_FAMILY_CLARIFY_NAMING`

## Scope

This review resolves the PS-versus-PSCompPars ambiguity surfaced by the
`TASK-0629` EXO-0003 metadata scout: campaign wording and filenames say
"PSCompPars," but the committed query selects from the Planetary Systems (`ps`)
table. It compares the committed ADQL query, the acquisition runbook, the source
manifest, and the README, recommends one route, and corrects the prose that
misstates the committed contract. It does **not** fetch rows, run residual
metrics, or change the query.

## Inputs

- `data/exoplanets/snapshot_plans/pscomppars_query.adql` (committed query)
- [`exoplanet-exo0003-metadata-trigger-scout.md`](exoplanet-exo0003-metadata-trigger-scout.md) (`TASK-0629`)
- `docs/runbooks/exoplanet-second-snapshot-acquisition-runbook.md`
- `data/exoplanets/source_manifest.yaml`
- `data/exoplanets/README.md`

## Finding

The committed query contract is unambiguous:

```sql
FROM ps
WHERE default_flag = 1
```

It selects **one self-consistent default published solution per planet** from
the Planetary Systems (`ps`) table, and it requests `pl_bmassprov` (the
per-planet mass-provenance flag the campaign uses to separate true-mass from
minimum-mass rows).

The surrounding labels disagree with the query in two ways:

| Surface | Wording | Accurate? |
| --- | --- | --- |
| `pscomppars_query.adql` SQL | `FROM ps WHERE default_flag = 1` | yes (authoritative) |
| `pscomppars_query.adql` title/comment | "PSCompPars Snapshot Query Contract" then clarifies it queries `ps` | loose title, self-corrected body |
| `source_manifest.yaml` | "Planetary Systems table" | yes |
| runbook "Source Surface" | "Planetary Systems Composite Parameters (`PSCompPars`)" | **misstates** the table |
| README admissible classes | "composite-catalog snapshots ... (`PSCompPars`)" | **misstates** the row class |
| filenames (`*pscomppars*`) | legacy label | label only, not a contract |

## Why the distinction matters

`ps` with `default_flag = 1` and the composite `pscomppars` table are different
NASA Exoplanet Archive surfaces:

- `ps default_flag = 1` returns a single **internally self-consistent** published
  solution per planet, with each field traceable to one reference set
  (`pl_refname`, `pl_bmassprov`).
- `pscomppars` returns archive-**composited** values that can combine different
  references per field to fill gaps.

The mass-radius benchmark depends on per-row provenance (`pl_bmassprov`) to keep
true-mass, minimum-mass, and model-derived values in separate row classes — a
campaign guardrail. Composite per-field mixing would undermine that. The
committed `ps default_flag = 1` choice is therefore the scientifically correct
one; the "PSCompPars/composite" prose is the error, not the query.

## Recommendation

Route: **keep the current `ps default_flag = 1` query family.**

- Do **not** switch to the literal `pscomppars` table. That would change value
  semantics (per-field compositing), break the `pl_bmassprov` row-class
  discipline, and invalidate the EXO-0001/EXO-0002 negative/control memory built
  on the current contract. No query-amendment task is needed to keep the lane
  closed.
- A future query-amendment review is required only if a maintainer ever
  deliberately wants composite semantics; that is not recommended here.
- Correct the prose that misstates which table is queried (done in this PR).
- Leave the `pscomppars_*` filenames as legacy labels; renaming them is a
  larger, reference-touching change and is out of scope. The corrected prose
  notes the filenames are legacy.

## Documentation corrections made

- `docs/runbooks/exoplanet-second-snapshot-acquisition-runbook.md`: the Purpose
  and Source Surface now describe the source as the Planetary Systems (`ps`)
  table with `default_flag = 1` (not the composite `PSCompPars` table), and note
  the `pscomppars_*` filenames are legacy labels.
- `data/exoplanets/README.md`: the `EXO-SRC-CLASS-001` row now reads
  "default-solution-per-planet snapshots ... Planetary Systems (`ps`) with
  `default_flag = 1` (not the composite `PSCompPars` table)."

The committed query file, manifests, and snapshot filenames are unchanged.

## Stop conditions preserved

- Do not fetch value-bearing rows or run residual metrics.
- Do not change the committed ADQL query in this task.
- Do not switch the table family without a dedicated query-amendment review.

## Output routing

- Task verdict: `KEEP_PS_DEFAULT_FLAG_QUERY_FAMILY_CLARIFY_NAMING`.
- Canonical destination:
  `docs/reviews/exoplanet-ps-pscomppars-query-boundary-review.md`, plus prose
  corrections in the runbook and README.
- Review tier: `none`.
- Gate A status: not attempted; no `RESULT-*` or `PRED-*` artifact.
- Gate B status: not applicable.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result artifact impact: no `results/` artifacts modified; no rows fetched.
- Limitations / blockers: this is a metadata/source-protocol clarification only;
  the Exoplanet lane stays closed under the existing reopen gate.
