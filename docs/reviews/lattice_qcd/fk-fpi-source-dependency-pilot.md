# TASK-1055: f_K/f_pi source-dependency pilot

- Review date: 2026-07-19
- Mode: metadata-only source and lineage curation
- Verdict: **`HOLD_COVARIANCE_UNRESOLVED`**

## Selection freeze

The pilot set was selected before inspecting publication lineage. The rule was
to include every primary publication cited as an input to the two direct
`f_K/f_pi` averages in FLAG Review 2024, and no other paper. This yields eleven
publications: five in the `N_f=2+1+1` set (FLAG references 20 and 42-45) and six
in the `N_f=2+1` set (references 12 and 46-50).

FLAG identity is pinned to arXiv:2411.04268, Table 17 and equations 76-77. The
retrieved Fermilab copy had SHA-256
`a1ddc84062a5e815be4ed0a46a4970070c9a773f91444447da3355a7636134f1`.
No FLAG table, figure, prose, or source file is committed.

## Coverage

All eleven primary identities resolve to an arXiv version and publication DOI.
For every paper the source manifest records:

- flavor content and sea-quark setup;
- isospin/QED treatment;
- axial-current normalization or cancellation route;
- scheme/scale applicability and scale-setting route;
- collaboration, ensemble family, and fermion action;
- named uncertainty-component categories without their numerical values;
- source locator, access date, metadata-only rights posture, and citation rule.

The graph binds every publication to collaboration, ensemble, action, scale,
normalization, and evaluated-average nodes. Both FLAG averages link to every
one of their primary inputs and are explicitly forbidden from being counted as
independent observations alongside those inputs.

## Dependency evidence

FLAG explicitly identifies partial MILC-HISQ configuration overlap among
FNAL/MILC 17, HPQCD 13A, and CalLat 20. Their statistical lineage is therefore
`CONFIRMED_SHARED`; FLAG also correlates the total systematic lineage of the
two HISQ-valence analyses. The MILC-asqtad subset used by HPQCD/UKQCD 07 and
MILC 10 is likewise `CONFIRMED_SHARED` for statistical and systematic lineage.

ETM 21 is source-described as an independent estimate using a new
Wilson-clover twisted-mass ensemble family, so its configuration relation to
ETM 14E is `CONFIRMED_DISJOINT`; the publications remain joined for a
collaboration-disjoint policy. BMW 10 and BMW 16 use the same collaboration and
2HEX-clover action family, but the exact configuration overlap was not resolved
from the bounded source pass, so that edge remains `POSSIBLE_SHARED`.

FLAG's common NLO SU(3) strong-isospin conversion for the isosymmetric
HPQCD/UKQCD 07, BMW 10, and RBC/UKQCD 14B inputs is represented as a shared
uncertainty-lineage node. This is dependency metadata only; no correction value
or uncertainty magnitude is copied.

## Why the verdict is HOLD

The graph adds machine-actionable evidence beyond reproducing a FLAG average,
so `STOP_DUPLICATES_FLAG` does not apply. Source use is metadata-only with no
publisher or arXiv bytes committed, so `HOLD_SOURCE_OR_RIGHTS` does not apply.

However, only six of the 55 unordered publication pairs have direct
shared/disjoint/possible configuration classification. The other 49 remain
`UNKNOWN`. Absence of an edge is not evidence of independence, and the six
provisional connected groups are not certified disjoint folds. A later numeric
task therefore cannot yet construct a defensible publication-disjoint split or
covariance policy. The correct bounded verdict is
`HOLD_COVARIANCE_UNRESOLVED`.

## Distinction from FLAG

FLAG supplies expert evaluation and averages. This pilot does not reproduce or
challenge either. Its added artifact is an explicit graph of collaboration,
ensemble, action, scale, normalization, configuration, average-membership, and
uncertainty lineage, including conservative unresolved states suitable for an
automation gate.

## Limitations

- No primary-paper supplementary configuration identifiers were exhaustively
  reconciled across all pairs.
- No numeric covariance matrix is available or reconstructed.
- Named uncertainty categories do not establish shared magnitudes or complete
  cross-paper correlation.
- The metadata does not assess agreement, tension, precision, or any physics
  conclusion.

## Output routing

- Canonical destination: `data/lattice_qcd/fk_fpi_source_manifest.yaml` and
  `data/lattice_qcd/fk_fpi_dependency_graph.yaml`.
- Gate A / Gate B: not attempted; this is metadata curation, not a result.
- Result, prediction, claim, and knowledge impact: none.
- Campaign activation: not authorized.
- Publication blocker: resolve the 49 `UNKNOWN` publication pairs and freeze a
  maintainer-reviewed value/covariance policy before ingesting any numeric
  `f_K/f_pi` values or uncertainties.
