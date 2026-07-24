# TASK-1079: N_f=2+1+1 f_K/f_pi dependency-edge resolution

- Review date: 2026-07-23
- Mode: metadata-only source and dependency curation
- Verdict: **`PARTIAL_HOLD_UNKNOWN_EDGES`**

## Scope and boundary

This audit covers exactly these five frozen FLAG-input publication identities:

- `pub-fnal-milc-17`
- `pub-hpqcd-13a`
- `pub-etm-14e`
- `pub-callat-20`
- `pub-etm-21`

It classifies all ten unordered publication pairs independently on four axes:
configuration/data, scale setting, normalization/renormalization, and named
uncertainty lineage. It does not copy or assess central values, uncertainty
magnitudes, averages, covariance magnitudes, agreement, precision, tension, or
physics conclusions.

Different collaborations, actions, citations, ensemble-family labels, or the
absence of an overlap statement are not treated as proof of disjointness.

## Method

1. Freeze the five publication identities already selected by `TASK-1055`.
2. Inspect the pinned primary-paper TeX source for ensemble tables, generation
   metadata, scale routes, current-normalization equations, and named
   uncertainty categories.
3. Cross-check the already recorded FLAG overlap/independence statements.
4. Classify each axis as `CONFIRMED_SHARED`, `CONFIRMED_DISJOINT`,
   `POSSIBLE_SHARED`, or `UNKNOWN`.
5. Preserve `UNKNOWN` whenever the bounded sources do not identify shared or
   disjoint data lineage.

No source bytes are committed. The SHA-256 values below identify the temporary
arXiv source packages inspected on 2026-07-23.

## Primary evidence catalog

| Publication | Stable identity | Exact locator | Retrieved source SHA-256 |
| --- | --- | --- | --- |
| FNAL/MILC 17 | [arXiv:1712.09262v4](https://arxiv.org/abs/1712.09262v4), DOI `10.1103/PhysRevD.98.074512` | Sec. II, table captioned "Ensembles used in this calculation"; Sec. III correlator-covariance discussion; Sec. IV scale-setting and error-budget tables | `b4256851a6633efc609ce79964bfe3795964dc6b266fe92fce28750b925d0b4a` |
| HPQCD 13A | [arXiv:1303.1670v2](https://arxiv.org/abs/1303.1670v2), DOI `10.1103/PhysRevD.88.074504` | Sec. II, Tables I-II and "Meson Correlators"; Sec. III, table captioned "Sources of uncertainty in the final results" | `655b0a831af0c00f485a547c0ba2aa3e770c4596bd11126777ee8345575ce2df` |
| ETM 14E | [arXiv:1411.7908v2](https://arxiv.org/abs/1411.7908v2), DOI `10.1103/PhysRevD.91.054507` | Introduction ensemble/analysis-branch paragraphs; Sec. 2, Eq. (4); uncertainty discussion following Eq. (9) | `4e5bf691c23cdac9dc0074888f61fb59f1fa4ef52ff0dc94ec696870cd8b5726` |
| CalLat 20 | [arXiv:2005.04795v3](https://arxiv.org/abs/2005.04795v3), DOI `10.1103/PhysRevD.102.034507` | Sec. II.A, Table I; Sec. II.B, Eq. (2); Sec. IV.C "Full analysis and uncertainty breakdown"; App. C | `5e71ae3a2ac43898d269fe019f963e8afa17264165e6c69507416e73e7707365` |
| ETM 21 | [arXiv:2104.06747v3](https://arxiv.org/abs/2104.06747v3), DOI `10.1103/PhysRevD.104.074520` | Sec. II, Table I and Eq. (15); Secs. IV-V; App. A simulation-parameter table; App. D | `fd2104c59248041246072ddfb4b1014b5605ae65952ec7cc3eb557623a1cdadc` |

The FLAG cross-check remains pinned to
[arXiv:2411.04268](https://arxiv.org/abs/2411.04268), Sec. 5.3.2 and
Table 17. It supplies the existing expert statements about partial MILC-HISQ
configuration overlap and the independence of the later ETM estimate; the
primary tables above supply the auditable ensemble and method identities.

## Ten-pair coverage

Abbreviations: `SHARED` = `CONFIRMED_SHARED`, `DISJOINT` =
`CONFIRMED_DISJOINT`, `POSSIBLE` = `POSSIBLE_SHARED`, and `UNKNOWN` =
`UNKNOWN`.

| Pair | Configuration/data | Scale setting | Normalization | Named uncertainty lineage |
| --- | --- | --- | --- | --- |
| FNAL/MILC 17 - HPQCD 13A | SHARED | UNKNOWN | UNKNOWN | SHARED |
| FNAL/MILC 17 - ETM 14E | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| FNAL/MILC 17 - CalLat 20 | SHARED | UNKNOWN | UNKNOWN | SHARED |
| FNAL/MILC 17 - ETM 21 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| HPQCD 13A - ETM 14E | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| HPQCD 13A - CalLat 20 | SHARED | POSSIBLE | UNKNOWN | SHARED |
| HPQCD 13A - ETM 21 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| ETM 14E - CalLat 20 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| ETM 14E - ETM 21 | DISJOINT | UNKNOWN | UNKNOWN | UNKNOWN |
| CalLat 20 - ETM 21 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

### Evidence interpretation

- The three pairs among FNAL/MILC 17, HPQCD 13A, and CalLat 20 retain
  `CONFIRMED_SHARED` configuration/statistical lineage. FLAG records partial
  overlap, and the primary ensemble tables identify the MILC-HISQ family and
  matching ensemble metadata.
- FNAL/MILC 17 and HPQCD 13A share a staggered-PCAC method label, but this
  does not establish a common fitted normalization input; the axis remains
  `UNKNOWN`.
- HPQCD 13A and CalLat 20 are `POSSIBLE_SHARED` on scale setting because both
  use a `w0` route on overlapping ensembles, but the inspected sources do not
  identify whether the same flow measurements or fitted scale data were
  reused.
- ETM 14E and ETM 21 retain the pilot's configuration-level
  `CONFIRMED_DISJOINT` state: FLAG calls the later estimate independent, while
  the pinned primary sources identify the legacy and Wilson-clover ensemble
  families. Their common maximal-twist Ward-identity method likewise does not
  establish reuse of a fitted normalization input, so normalization remains
  `UNKNOWN`.
- Generic category-name overlap such as "statistics", "continuum", or
  "finite volume" is not enough to declare shared uncertainty lineage.

## Remaining UNKNOWN states

Six pairs remain `UNKNOWN` on every axis:

- FNAL/MILC 17 - ETM 14E
- FNAL/MILC 17 - ETM 21
- HPQCD 13A - ETM 14E
- HPQCD 13A - ETM 21
- ETM 14E - CalLat 20
- CalLat 20 - ETM 21

All ten normalization axes remain `UNKNOWN`: method-label equality is not
dependency identity.

Additional axis-specific unknowns remain even for the four partially resolved
pairs. In particular, no pair has a confirmed-disjoint scale-setting,
normalization, or named-uncertainty lineage. A later consumer must not convert
these absences into independence.

## Verdict

**`PARTIAL_HOLD_UNKNOWN_EDGES`**

The bounded audit makes the four dependency axes explicit and adds stable
primary locators, but six cross-family pairs remain fully unknown and the
remaining four pairs retain axis-specific unknowns. The subgraph therefore
does not authorize a publication-disjoint split, covariance policy, or numeric
ingestion.

## Limitations

- No official cross-collaboration configuration registry was found that
  explicitly certifies the six cross-family pairs as disjoint.
- Shared normalization methods do not imply a shared numerical
  renormalization input or a covariance magnitude.
- Shared ensemble metadata establishes lineage but does not reconstruct which
  configuration indices entered every resampling stream.
- The temporary arXiv source packages were inspected only for metadata and
  locators; no publisher, arXiv, HDF5, or collaboration source bytes are
  committed.

## Output routing

- Canonical destination:
  `data/lattice_qcd/fk_fpi_dependency_graph.yaml` and this review note.
- Review tier: maintainer source/dependency review; no scientific result tier.
- Gate A / Gate B: not applicable; no result or prediction was produced.
- Result impact: none.
- Claim impact: none.
- Prediction impact: none.
- Knowledge impact: none.
- Campaign-wide GO: not authorized.
- Publication blocker: resolve the remaining `UNKNOWN` axes with explicit
  primary or official cross-source identity evidence and obtain maintainer
  review before any disjoint split, covariance policy, or value ingestion.