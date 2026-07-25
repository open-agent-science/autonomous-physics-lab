# TASK-1080: bounded N_f=2+1 dependency-edge resolution

- Review date: 2026-07-23
- Mode: metadata-only primary-source lineage audit
- Scope: the six frozen `N_f=2+1` FLAG-average inputs and all fifteen unordered pairs
- Verdict: **`PARTIAL_HOLD_UNKNOWN_EDGES`**

## Method and guardrails

The audit classified configuration/data, scale-setting, normalization or
renormalization, and named-uncertainty lineage independently. A common
collaboration, action, observable, or citation was not treated as proof of
shared data, and different labels were not treated as proof of disjointness.
When the bounded primary sources did not cross-identify an input or explicitly
certify separation, the axis remains `UNKNOWN`.

No central values, uncertainty magnitudes, averages, covariance magnitudes, or
physics comparisons were extracted. The note does not assess agreement,
precision, tension, or any physics conclusion.

## Source ledger and exact locators

| Code | Stable identity and locator | Metadata supported |
| --- | --- | --- |
| R | arXiv:1411.7017v2, PDF pp. 3-4; Sec. III C; Sec. IV | RBC/UKQCD ensemble sets, axial-current normalization, and hadron-mass global-fit scale route |
| H | arXiv:0706.1726v2, PDF p. 1 Table I; PDF p. 2 PCAC and `r1/a` paragraphs | HPQCD/UKQCD MILC configurations, PCAC current, and MILC scale lineage |
| M | arXiv:1012.0868v1 and the official PoS(Lattice 2010)074 PDF, pp. 2-3 Sec. 2 and Table 1; p. 5 scale paragraph | MILC ensemble table and mass-independent `r1/a` route with the later physical-scale choice |
| B10 | arXiv:1001.4692v1, PDF pp. 2-4 Introduction, Sec. 2.1, and Table 1; Sec. 2.5; action identity from cited Ref. [9], arXiv:0802.2706v2 Sec. II.A | BMW 2010 six-step stout-clover action, Xi primary scale with Omega alternative, and systematic-analysis route; normalization lineage not established by the bounded locator |
| B16 | arXiv:1601.05998v2, PDF pp. 2-5 Secs. 2-3.1; pp. 17-18 appendix ensemble table | BMW 2016 2HEX family, Omega scale route, and axial-factor cancellation in the ratio |
| Q | arXiv:1612.04798v1, PDF p. 5 Sec. 3; pp. 8-10 Sec. 4 and continuum paragraph | QCDSF/UKQCD simulation setup, improved axial current, and prior-spacing route |
| F-set | arXiv:2411.04268, FLAG Review 2024 Table 17 and Eqs. 76-77 | Frozen average membership only; the evaluated average is not an independent observation |
| F-asqtad | arXiv:2411.04268, FLAG Review 2024 Sec. 5.3.2, PDF p. 74 | Shared MILC subset and correlated statistical/systematic lineage for H-M |
| F-iso | arXiv:2411.04268, FLAG Review 2024 Table 18 and Eqs. 74-75 | Common FLAG NLO SU(3) strong-isospin conversion for R, H, and B10 |

The official MILC conference PDF is
<https://pos.sissa.it/105/074/pdf>. The other primary identities are pinned to
the arXiv versions shown above. Source bytes were used transiently and are not
committed.

## Fifteen-pair coverage

States are axis-specific. `CONFIRMED_SHARED` does not imply a numeric
correlation magnitude, and `POSSIBLE_SHARED` is a conservative hold rather than
an assertion of reuse.

| Pair | Configuration/data | Scale setting | Normalization | Named uncertainty | Evidence |
| --- | --- | --- | --- | --- | --- |
| R-H | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `CONFIRMED_SHARED` | R, H, F-iso |
| R-M | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | R, M |
| R-B10 | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `CONFIRMED_SHARED` | R, B10, F-iso |
| R-B16 | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | R, B16 |
| R-Q | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | R, Q |
| H-M | `CONFIRMED_SHARED` | `CONFIRMED_SHARED` | `UNKNOWN` | `CONFIRMED_SHARED` | H Table I, M Table 1, F-asqtad |
| H-B10 | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `CONFIRMED_SHARED` | H, B10, F-iso |
| H-B16 | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | H, B16 |
| H-Q | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | H, Q |
| M-B10 | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | M, B10 |
| M-B16 | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | M, B16 |
| M-Q | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | M, Q |
| B10-B16 | `UNKNOWN` | `POSSIBLE_SHARED` | `UNKNOWN` | `UNKNOWN` | B10 action Ref. [9], B16 |
| B10-Q | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | B10, Q |
| B16-Q | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | B16, Q |

## Resolved and preserved lineage

HPQCD/UKQCD Table I identifies the gauge fields as MILC configurations. The
two fine-ensemble rows used there are also present in MILC Table 1, which is
direct primary-source support for shared configuration lineage. Both papers
also consume MILC `r1/a`; the graph records that shared relative-scale lineage
without equating their later physical `r1` choices. FLAG's pair-specific
statistical/systematic treatment is retained as named-uncertainty lineage.

BMW 2010 delegates its action definition to Ref. [9], whose arXiv:0802.2706v2
Sec. II.A specifies a tree-level Symanzik gauge action with six-step
stout-smeared clover fermions. BMW 2016 instead documents a 2HEX-clover family.
The bounded sources provide no configuration crosswalk, so the B10-B16
configuration state is `UNKNOWN`, not shared. The independently supported scale
routes still justify `POSSIBLE_SHARED`: BMW 2010 uses Xi with an Omega
alternative, while BMW 2016 uses Omega, but no common scale-data input is
established. The BMW 2010 locator does not identify axial-factor cancellation,
so only BMW 2016 retains that graph route and pair normalization stays
`UNKNOWN`.

The common FLAG strong-isospin conversion remains attached to R, H, and B10,
which resolves that named-uncertainty axis for their three pairs. All six
publications remain linked to the same FLAG evaluated-average node, with the
explicit rule that the average cannot count independently alongside its inputs.
Neither relation is used to manufacture configuration or scale independence.

## Remaining UNKNOWN states

Every configuration axis other than H-M remains `UNKNOWN`, including B10-B16.
No pair receives `CONFIRMED_DISJOINT`: separate collaborations, actions,
ensemble labels, or scale observables are insufficient without an explicit
primary-source or official-ensemble identity statement. Normalization remains
`UNKNOWN` for every pair because the bounded sources establish per-paper
methods but not reuse or separation of a fitted cross-paper normalization
input. Named uncertainty remains `UNKNOWN` except for the FLAG-documented
asqtad and strong-isospin lineages.

## Limitations

- No exhaustive configuration-ID crosswalk was available for the two BMW
  publications.
- The MILC conference proceeding does not expose a pair-specific fitted
  normalization lineage, so a common staggered-current method is not promoted.
- Named uncertainty categories alone do not establish shared random variables
  or covariance magnitudes.
- The audit does not authorize a publication-disjoint split, covariance model,
  value ingestion, campaign-wide GO, or scientific claim.

## Output routing

- Canonical destination: the `nf_2p1_pair_resolution` section of
  `data/lattice_qcd/fk_fpi_dependency_graph.yaml` and this review note.
- Review tier: maintainer review required by the task closeout policy.
- Gate A / Gate B: not applicable; this is source/dependency metadata, not a
  scientific result.
- Result, prediction, claim, and knowledge impact: none.
- Publication blocker: unresolved pair axes prevent a certified disjoint split
  or covariance policy.