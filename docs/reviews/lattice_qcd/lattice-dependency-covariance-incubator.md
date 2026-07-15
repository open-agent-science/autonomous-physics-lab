# Lattice-QCD Dependency And Covariance Incubator

- Task: `TASK-1030`
- Campaign profile: `lattice-qcd-aggregated-consistency`
- Review date: 2026-07-14
- Mode: metadata-only campaign incubator
- Verdict: **`GO_LATTICE_DEPENDENCY_AUDIT`**

## Decision

Select the dimensionless pseudoscalar decay-constant ratio `f_K/f_pi` for one
future dependency-graph audit. The useful APL artifact is not another average.
It is a machine-readable account of when publications share collaborations,
gauge ensembles, scale setting, normalization routes, configurations, or
evaluated-average membership. Unknown dependence remains unknown or is linked
conservatively.

This packet contains no central values, uncertainties, scientific rows,
averages, tensions, or anomaly scores. The accompanying graph is deliberately
fabricated and demonstrates structure only.

## Bounded Candidate Comparison

At most three candidates were reviewed.

| Candidate | Definition stability | Dependency visibility | Main complication | Decision |
| --- | --- | --- | --- | --- |
| `f_K/f_pi` | Dimensionless ratio with a mature light-meson definition; flavor content and isospin convention must still be explicit | Collaboration, ensemble family, action, scale-setting source, and publication lineage are commonly described | Shared ensembles and correlated scale/normalization choices are not a complete published covariance matrix | **Select** |
| `f_+(0)` for semileptonic `K -> pi` at zero momentum transfer | Dimensionless and convention-stable when the kinematic point and flavor setup are fixed | Similar lineage metadata is available | Kinematic interpolation and current-normalization choices add another dependency layer | Defer |
| `B_K` | Mature observable | Collaboration and ensemble lineage can be traced | Renormalization scheme, scale, operator matching, and running make cross-paper compatibility more demanding | Defer |

`f_K/f_pi` is selected because it gives the cleanest first test of dependency
bookkeeping while retaining the core scientific problem: papers are not
independent merely because they have different citations. This selection does
not assert that covariance is recoverable or that any published result agrees
with another.

## Source And Rights Plan

The source boundary is metadata-first:

- FLAG Review 2024, arXiv identity: <https://arxiv.org/abs/2411.04268>
- International Lattice Data Grid metadata standards:
  <https://www2.ccs.tsukuba.ac.jp/ILDG/>
- ILDG overview and metadata/file-format description:
  <https://arxiv.org/abs/0910.1692>
- ILDG FAIR-data update: <https://arxiv.org/abs/2212.08392>

A future source manifest may use FLAG only to identify the evaluated set and
its inclusion relationships. Every included result must then resolve to a
primary publication with stable DOI, arXiv, or INSPIRE identity. Ensemble
identity should use official collaboration or ILDG records when available.

Only factual bibliographic and dependency metadata may be committed. Do not
copy FLAG tables, plots, prose, publisher files, or ensemble configurations.
Record source access date, version, locator, citation requirement, rights
status, and checksum or immutable-archive policy. If reuse terms for a required
artifact remain unclear, return `HOLD_SOURCE_OR_RIGHTS` before acquisition.

## Observable Contract

The selected observable must be represented as:

| Field | Required contract |
| --- | --- |
| Observable id | `pseudoscalar_decay_constant_ratio_fk_fpi` |
| Quantity | `f_K/f_pi` |
| Unit | dimensionless |
| Flavor content | Explicit `N_f` and sea-quark content per publication |
| Isospin/QED convention | Explicitly record isospin-symmetric, strong-isospin-breaking, and QED treatment; never pool unknown conventions |
| Normalization | Record axial-current normalization or cancellation claim and its source |
| Scheme/scale | Mark not applicable only when the primary source supports it; otherwise preserve the reported scheme and scale |
| Uncertainty | Keep quoted statistical and systematic components separate; preserve asymmetric form and named correlated components |
| Average class | Distinguish primary result, collaboration update, and evaluated average |

No row is eligible when observable identity, flavor convention, normalization,
or uncertainty meaning is unresolved.

## Dependency Graph Contract

The graph vocabulary is frozen in the fabricated schema example at
[`lattice-dependency-graph-fabricated.yaml`](./lattice-dependency-graph-fabricated.yaml).
Future real metadata must support these node classes:

- collaboration;
- publication;
- gauge-ensemble family;
- fermion action;
- scale-setting source;
- renormalization or normalization route;
- shared configurations/data source;
- evaluated average;
- quoted uncertainty component.

Required edges include authorship, result inclusion, ensemble use, shared
configuration/data, action use, scale-setting dependence, normalization or
renormalization dependence, uncertainty-component dependence, and
evaluated-average inclusion.

Each edge carries evidence identity and one dependence state:
`CONFIRMED_SHARED`, `CONFIRMED_DISJOINT`, `POSSIBLE_SHARED`, or `UNKNOWN`.
`UNKNOWN` and `POSSIBLE_SHARED` are conservatively linked for any later split.
Absence of a documented edge never means independence.

## Future Comparison Families

These are contracts only and were not run:

1. `naive_aggregation`: diagnostic reproduction of treating eligible primary
   publications as separate rows; never the preferred inference.
2. `collaboration_disjoint`: units sharing any collaboration identity stay in
   one fold.
3. `ensemble_family_disjoint`: units sharing confirmed, possible, or unknown
   ensemble/configuration lineage stay in one fold.
4. `leave_one_collaboration_out`: hold out one collaboration-connected
   component at a time.

An evaluated FLAG average must remain linked to all included publications and
must never be counted as independent evidence alongside them. No comparison
family is authorized until a later task freezes real source metadata and a
covariance policy.

## Distinction From FLAG

FLAG supplies expert review, quality assessment, source selection, and
evaluated summaries. Reproducing those summaries would be duplication and is
out of scope. The proposed APL contribution is narrower and operational:

- explicit graph edges with source-level evidence;
- conservative machine-actionable unknown-dependence states;
- deterministic collaboration- and ensemble-disjoint partition contracts;
- an audit trail showing why a publication pair may not be independent.

The future audit must stop with `STOP_DUPLICATES_FLAG` if it cannot populate
this graph beyond relationships already available in a directly reusable FLAG
artifact, or if its only output would be another world average.

## Stops And Next Gate

Stop before real metadata acquisition if primary identities cannot be pinned,
source rights are unclear, flavor/normalization conventions are incompatible,
or shared-ensemble lineage is too incomplete to distinguish known from unknown
dependence. Missing numeric covariance alone does not justify false
independence; it routes affected links to conservative graph components and may
later produce `HOLD_COVARIANCE_UNRESOLVED`.

The next permitted task is a metadata-only `f_K/f_pi` source-manifest and
dependency-edge pilot covering a maintainer-bounded publication set. It may
record identities and lineage, but no central values or uncertainties. Real
rows, loaders, averages, sensitivity runs, `RESULT`, `PRED`, `CLAIM`, and
`KNOW` artifacts require separate reviewed tasks after that source gate.

## Output Routing

`GO_LATTICE_DEPENDENCY_AUDIT` activates only a bounded metadata-audit path. It
does not activate a Lattice-QCD data campaign, certify independence, reproduce
FLAG, or promote scientific evidence.
