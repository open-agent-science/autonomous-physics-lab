# Particle-Mass Common-Scheme Preflight

- Task: `TASK-0820`
- Related claim: `CLAIM-0007`
- Related result: `RESULT-0011`
- Verdict: `NEEDS_MAINTAINER_SOURCE_DECISION`

## Scope

This preflight checks whether the mixed quark mass scheme/scale limitation in
the particle-mass falsifier MVP can be reduced by a narrow future source-policy
task. It does not rerun the Koide relation, search formulas, fit constants,
add particle families, edit `CLAIM-0007`, change `RESULT-0011`, or create a
knowledge artifact.

`RESULT-0011` remains useful `AGENT_VALIDATED` negative memory for the stored
inputs. `CLAIM-0007` should remain `DRAFT` because the current quark rows are
not on a common quark scheme/scale.

## Source Route Assessed

Candidate route:

- Source: Antusch, Hinze, and Saad, "Updated Running Quark and Lepton
  Parameters at Various Scales", arXiv:2510.01312.
- Input basis: 2024 PDG quark and lepton mass inputs, evolved with Standard
  Model running/matching tools.
- Proposed future rerun surface: all six quark masses as `MS-bar` running
  masses at a single benchmark scale, preferably `mu = M_Z`, with the source's
  published one-sigma uncertainties.

Why this route is relevant:

- PDG's quark-mass review states that quark mass values depend on the chosen
  renormalization scheme and scale, and that the `MS-bar` scheme is the common
  high-energy convention.
- The candidate source explicitly provides running quark parameters at common
  benchmark scales derived from the current PDG input set.
- A common `MS-bar, mu = M_Z` table would remove the current within-quark-family
  mixture of `2 GeV`, `mc(mc)`, `mb(mb)`, and direct top-mass semantics.

Why this is not automatically ready:

- The route is a derived arXiv table, not the current committed PDG/FLAG source
  policy.
- A maintainer must decide whether a derived running-parameter table is
  acceptable, or whether the repo should require a PDG/FLAG-only source path or
  a local deterministic RGE pipeline with pinned software versions.
- The top-quark conversion is especially source-policy sensitive because the
  current row is a direct measurement, while a common-scale rerun would consume
  a running `MS-bar` top mass.

## Scheme And Scale Table

| Family row | Current stored semantics | Future common-route semantics | Preflight decision |
| --- | --- | --- | --- |
| `u`, `d`, `s` | `MS-bar` running masses at `2 GeV` | `MS-bar` running masses at `M_Z` | Compatible only after source-policy approval and row pinning |
| `c` | `MS-bar` running mass at `mc(mc)` | `MS-bar` running mass at `M_Z` | Compatible only after source-policy approval and row pinning |
| `b` | `MS-bar` running mass at `mb(mb)` | `MS-bar` running mass at `M_Z` | Compatible only after source-policy approval and row pinning |
| `t` | direct-measurement mass, no common scale | `MS-bar` running mass at `M_Z` | Needs explicit maintainer decision because semantics change most |
| charged leptons | stored PDG pole masses | unchanged for existing charged-lepton benchmark rows | Leave unchanged unless a future task explicitly creates a parallel running-lepton provenance note |

## Compatibility With The Fixed Koide Target

The fixed target stays exactly `Q = 2/3`. A future rerun may recompute the same
stored falsifier calculation on a newly pinned common-scheme quark table, but it
must not fit a new target value, add families, search alternate relations, or
promote a claim.

The proposed route is compatible with a narrow rerun task only if the maintainer
accepts the source policy. It would test whether the up-type and down-type
quark INVALID outcomes survive after the quark rows are put on a common
`MS-bar` scale. It would not prove or explain particle-mass generation.

## Charged-Lepton Handling

For the existing `RESULT-0011` and charged-lepton benchmark rows, no change is
recommended. The stored charged-lepton inputs are pole masses and should remain
the clean reference for the original falsifier MVP.

If a future all-charged-fermion common-scale study consumes running charged
lepton masses from the same source route, it should create a separate dataset
or provenance note instead of overwriting the existing pole-mass rows. That
future task should state that it is a new source-policy surface, not an
upgrade of the old result.

## Future Task Recommendation

Recommended next task wording:

```text
Pin a maintainer-approved common-scheme quark mass table for the particle-mass
falsifier MVP. Use a single accepted source route, record citation, scheme,
scale, units, uncertainty semantics, and checksum/provenance metadata. Do not
run Koide metrics, edit CLAIM-0007, or change RESULT-0011 in the source-pinning
task.
```

Only after that source-pinning task lands should a separate rerun task be
considered.

## Output Routing Summary

| Field | Value |
| --- | --- |
| Destination | source/scheme readiness review |
| Verdict | `NEEDS_MAINTAINER_SOURCE_DECISION` |
| Source route | candidate common `MS-bar, M_Z` quark table from a derived running-parameter source |
| CLAIM impact | none; `CLAIM-0007` remains `DRAFT` |
| RESULT impact | none; `RESULT-0011` metrics and tier are unchanged |
| Knowledge impact | none |
| Gate C blocker | maintainer source-policy decision plus a separate pinned common-scheme source task |

