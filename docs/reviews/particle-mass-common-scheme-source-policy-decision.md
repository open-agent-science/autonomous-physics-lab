# Particle-Mass Common-Scheme Source-Policy Decision

**Task:** `TASK-0874`
**Related result:** `RESULT-0011`
**Related claim:** `CLAIM-0007`
**Decision:** `PUBLISHED_DERIVED_MZ_TABLE_RECOMMENDED_FOR_SOURCE_PINNING`
**Review date:** 2026-06-29

## Scope

This packet decides which source route should be used before any common-scheme
quark rerun of the fixed Koide target. It does not copy quark values, rerun
metrics, edit particle datasets, change `RESULT-0011`, change `CLAIM-0007`,
or search for another relation.

`RESULT-0011` remains `AGENT_VALIDATED` negative memory for its stored
inputs. `CLAIM-0007` remains `DRAFT` because the current quark rows mix
renormalization scales and top-mass semantics.

## Evidence Update Since TASK-0820

The source assessed by `TASK-0820` is no longer only an arXiv candidate.
Antusch, Hinze, and Saad now has an accepted Physical Review D publication
route, but this decision packet does not pin a publisher article identifier:

- S. Antusch, K. Hinze, and S. Saad, *Updated running quark and lepton
  parameters at various scales*;
- accepted manuscript: [arXiv:2510.01312v2](https://arxiv.org/abs/2510.01312),
  whose arXiv metadata records acceptance for publication in Physical Review D;
- publisher DOI, article number, and final journal reference: not pinned here;
  verify from the publisher before committing any source artifact;
- reuse posture: arXiv distribution license and any publisher open-access
  license must be recorded by the future source-pinning task.

The paper derives Standard Model running parameters in the
`MS-bar` scheme at `M_Z` and higher benchmark scales from 2022 and 2024 PDG
inputs. It reports one-sigma intervals and uses a documented two-loop RGE
pipeline with threshold conversions. This materially strengthens the
published-derived-table route, but it does not turn the rows into direct mass
measurements.

## Route Comparison

| Route | Strength | Load-bearing limitation | Decision |
| --- | --- | --- | --- |
| Antusch-Hinze-Saad accepted-manuscript table | Complete six-quark common `MS-bar`, `mu = M_Z` surface; 2024 PDG input branch; one-sigma intervals; accepted PRD route | Values are derived through a specific SM running/matching pipeline; marginal intervals do not establish an independent six-row covariance matrix; final publisher DOI/article metadata remain to be pinned | **Recommended for a source-pinning task** |
| PDG/FLAG-only table | Highest-authority low-energy mass inputs and mature lattice averaging | PDG publishes `u,d,s` at 2 GeV, `c` at `m_c`, `b` at `m_b`, and top with different direct/pole/cross-section semantics; FLAG does not supply the top route needed for a six-quark common-`M_Z` table | **Not sufficient by itself** |
| Local deterministic RGE pipeline | Maximum repository control and future replayability | Requires pinned software, electroweak/QCD matching choices, threshold order, input covariance, uncertainty propagation, and parity tests against a published table | **Defer as an independent validation lane** |

## Recommended Source Contract

The next source-pinning task should use exactly one surface:

| Field | Required value |
| --- | --- |
| Source | Antusch, Hinze, and Saad accepted manuscript; final PRD article metadata to verify from publisher |
| DOI | not pinned here; source-pinning task must verify publisher DOI before copying values |
| Accepted manuscript | `arXiv:2510.01312v2` |
| Input branch | 2024 PDG inputs |
| Theory branch | Standard Model only |
| Renormalization scheme | `MS-bar` |
| Renormalization scale | `mu = M_Z` |
| Flavors | `u, d, s, c, b, t` |
| Uncertainty | source-reported one-sigma marginal interval, preserving asymmetric bounds where present |
| Row class | `derived_running_parameter`, not `direct_measurement` |
| Intended use | separate common-scheme sensitivity dataset; never overwrite stored PDG rows |

The source-pinning task must identify the exact version-of-record table and
column. The 2024-PDG Standard Model `M_Z` column must not be mixed with the
2022 branch, higher scales, MSSM values, or `DR-bar` quantities.

## Mass Versus Yukawa Semantics

The source presents running fermion parameters. A future source artifact must
record whether the selected entries are running masses or Yukawa couplings.

- If the version-of-record table publishes `m_q(M_Z)`, store them as
  `derived_running_mass` with units.
- If it publishes `y_q(M_Z)`, store them as `derived_running_yukawa` and do
  not relabel them as masses.
- A conversion between `y_q` and `m_q` requires an explicit electroweak
  convention and must not be inserted silently.

For a fixed Koide quotient, a common positive multiplicative factor cancels
within one three-member family. That mathematical invariance may support a
later rerun on common-scale Yukawa values, but only under a separate task that
freezes the representation before scoring. It does not authorize value
transcription or a metric run here.

## Top-Quark Semantics

The top entry is the most important source-policy boundary:

- the current repository row is based on a direct-measurement mass surface;
- the recommended common-`M_Z` entry is a derived running parameter;
- the paper starts from a top pole-mass input and applies its documented
  conversion/running pipeline;
- the future dataset must therefore label the top row as derived and preserve
  the pole-input provenance, matching assumptions, and scale.

The common-scale top row must never be described as an independent direct
measurement or silently compared with the old top row as though the two had
identical semantics.

## Uncertainty And Dependence Policy

The source reports one-sigma intervals generated from sampled input
uncertainties. The future pin must preserve:

- confidence level and asymmetric bounds;
- the PDG input edition;
- the sampling and RGE method stated by the source;
- the fact that the six outputs share upstream inputs and are not proven
  statistically independent.

Unless the source supplies a recoverable covariance matrix, a future rerun
must not present diagonal propagation as full covariance-aware evidence.
Allowed handling is:

1. report source marginals;
2. run any later metric as an explicitly diagonal-only sensitivity analysis;
3. keep claim promotion blocked on the missing cross-row dependence model.

## Citation And Provenance Requirements

A source-pinning task must record:

- full PRD citation and DOI, verified from the publisher rather than inferred;
- arXiv v2 locator as the accepted-manuscript audit surface;
- exact table, column, theory branch, scheme, and scale;
- retrieval date and SHA-256 for any committed redistributable text/table
  artifact;
- CC BY 4.0 attribution;
- upstream 2024 PDG citation;
- explicit derived-row provenance from low-scale inputs through the source
  pipeline.

No value should be copied from a search snippet, secondary database, or
LLM-generated table.

## Exact Future Task Shape

Recommended future task:

> Pin the peer-reviewed Antusch-Hinze-Saad 2024-PDG Standard Model
> `MS-bar`, `mu = M_Z` six-quark parameter surface as a separate
> derived common-scheme dataset. Record the version-of-record citation,
> accepted-manuscript locator, exact table/column, representation
> (mass or Yukawa), units, one-sigma interval semantics, top pole-input
> conversion provenance, shared-dependence limitation, checksum, and license.
> Do not run Koide metrics, overwrite the existing particle-mass dataset,
> change `RESULT-0011`, or edit `CLAIM-0007`.

Only after that source artifact passes review should a separate task rerun the
unchanged `Q = 2/3` falsifier on the frozen common-scale surface.

## Stop Conditions

Stop source pinning or any later rerun if:

1. the exact 2024-PDG SM `M_Z` table or publisher DOI/journal reference cannot
   be identified;
2. mass and Yukawa representations are mixed or silently converted;
3. top pole/direct semantics are retained while the row is labelled
   common-scale `MS-bar`;
4. confidence-level or asymmetric-interval semantics are lost;
5. 2022 and 2024 inputs, SM and MSSM branches, or `MS-bar` and `DR-bar`
   values are mixed;
6. derived rows overwrite the existing direct/PDG-backed dataset;
7. missing covariance is hidden behind independent-error wording;
8. the task expands into alternate targets, phase extensions, family search,
   or particle-mass-generation claims.

## Output Routing

- Task verdict:
  `PUBLISHED_DERIVED_MZ_TABLE_RECOMMENDED_FOR_SOURCE_PINNING`.
- Canonical destination: this source-policy decision packet.
- Review tier: `none`.
- Gate A status: not attempted; no result or prediction artifact.
- Gate B status: not applicable.
- Gate C blocker: a reviewed source-pinning task, then a separate fixed-target
  rerun, then maintainer interpretation.
- Claim impact: none; `CLAIM-0007` remains `DRAFT`.
- Result impact: none; `RESULT-0011` remains unchanged.
- Knowledge impact: none.
- Limitations: derived source surface, shared input dependence, no committed
  covariance, and no local RGE parity replay.
