# Nuclear Shell-Axis Post-Registration Source-Manifest Scout

- Task: `TASK-1023`
- Target batch: `shell-axis-balanced-001`
- Registry entries: `PRED-0063` through `PRED-0068`
- Registration boundary: `2026-05-20T00:00:00Z`
- Verdict: `BLOCKED_NO_PEEK_AUDIT`

## Scope

This task retried the metadata-only source-manifest scout after the earlier
`TASK-0307` `BLOCKED_SOURCE_NOT_PINNED` outcome. The allowed question was
whether a concrete official evaluation, peer-reviewed table, collaboration
release, or archive copy had become available after the registration boundary
and could be pinned before any target-row inspection.

No source manifest was created. No external table or data file was downloaded,
no checksum was claimed for an unpinned source, no target value was copied or
committed, and no reveal score or model comparison was computed.

## Metadata-Only Source Screen

| Candidate source class | Metadata surface | Timing and pinning assessment | Decision |
| --- | --- | --- | --- |
| Official atomic-mass evaluation | [IAEA Atomic Mass Data Center](https://www-nds.iaea.org/amdc/) and the repository's reviewed AME2020/NUBASE2020 baseline | The reviewed evaluation baseline predates `2026-05-20`; no new immutable post-registration evaluation artifact was safely pinned before the stop condition fired. | Not accepted. |
| Continuously updated evaluated-data service | [IAEA ENSDF resource page](https://nucleus.iaea.org/Pages/evaluated-nuclear-structure-data-file.aspx) | The service is a periodically updated nuclear-structure/decay surface, not by itself an immutable mass-excess release with a reviewed artifact checksum, publication boundary, and measured/evaluated row flag contract. | Not accepted. |
| Reference atomic-weight service | [NIST Atomic Weights and Isotopic Compositions](https://www.nist.gov/pml/atomic-weights-and-isotopic-compositions-relative-atomic-masses) | The landing-page metadata identifies an older convenience compilation, not a new post-registration critical mass evaluation. Its timing therefore cannot unlock this prospective reveal. | Not accepted. |
| Post-registration peer-reviewed or collaboration release | Publication-page discovery only | No candidate was promoted to a concrete source manifest before the no-peek stop. | Search stopped. |

This table records source-level metadata only. It does not assert whether any
of the eight target nuclides has a measured, evaluated, extrapolated, or missing
row in any source.

## No-Peek Stop Event

The metadata search used a target-name publication query to discover official
source pages. Before an immutable post-registration source had been selected,
the search engine rendered row-level relative-atomic-mass snippets from a
reference-data page directly in its result response.

No mass-excess field was intentionally queried, and no displayed number was
copied into repository memory, normalized, compared, or scored. Nevertheless,
relative atomic mass is convertible to mass excess. This executor can therefore
no longer provide a clean declaration that it remained isolated from all
target-value information during source selection.

The protocol-safe action is to stop with `BLOCKED_NO_PEEK_AUDIT`. Treating the
incident as harmless because no metric was computed would weaken the source-
before-values boundary that makes a later prospective reveal reviewable.

## Registry Integrity Check

Repository-only checks were completed without reading prediction payload values.

| Check | Result |
| --- | --- |
| Registration timestamp | All six entries record `2026-05-20T00:00:00Z`. |
| Source-state commit | All six entries retain `9e8d7d339a4f0f432e41689862a649eb029b8575`. |
| File history | Current history shows one commit touching the six entries: `52941c3b1be6eee8d25614a5930aef589ae6559e`; no later registry edit is present. |
| Working-tree mutation | No `PRED-0063` through `PRED-0068` file was edited by this task. |
| Controls | The candidate family remains paired with the sign-inverted, near-null, and reference-baseline entries required by the reveal protocol. |

Current file identity:

| Entry | SHA-256 |
| --- | --- |
| `PRED-0063` | `44e4c21469fc06369096aec240007a967be728867655eb7bcf1debc9558d98ed` |
| `PRED-0064` | `bf94e95e8dfd5043d991a51f84163f22f3aabd1f0bf25d873bef390bc9c28833` |
| `PRED-0065` | `6025d879eae5cc67ff19698888e3fb3b4fde6f64963c8d4bd45917436286f47b` |
| `PRED-0066` | `7931224d562a6c244e5f2358ef6136479f94f2aa758435dc24de5bc1a2b25590` |
| `PRED-0067` | `f212906c7fdaf3d054e2d5f54d1e74c4180b06c41052e7eb0f590959bff0360c` |
| `PRED-0068` | `c45fccc82b4eb8eba71388df7295fd602aaa34cfffd07cfde76cc10261510487` |

These hashes establish registry identity only. They do not authorize scoring.

## Safe Retry Contract

A future retry should be assigned to a human or agent that has not seen the
search-rendered target snippets. It should:

1. start from an allowlist of direct official release or DOI landing pages;
2. forbid search-result snippets and isotope-row endpoints during discovery;
3. pin source title, issuing body, release date, immutable locator, rights,
   archive policy, and checksum feasibility before any target-name query;
4. have a separate reviewer approve measured/evaluated/extrapolated semantics
   and the row-level measurement flag before target matching;
5. open a later reveal-scoring task only after the concrete manifest and
   no-peek audit are reviewed.

The retry must not reuse this executor as the clean no-peek evaluator. A
retrospective diagnostic remains possible only through a separate task that
explicitly weakens the evidence class before values are inspected.

## Limitations

- The source screen stopped immediately after the no-peek incident, so it does
  not prove that no qualifying post-registration publication exists.
- No raw artifact was pinned or hashed, and no row semantics were reviewed.
- The blocker is a process-integrity outcome, not evidence for or against any
  registered prediction family.
- Zero eligible targets, source timing, and value semantics remain unknown.

## Output Routing

- Canonical destination: this source-readiness blocker review.
- Source manifest: not created.
- Review tier: not applicable; no RESULT or PRED artifact was created or
  promoted.
- Gate A / Gate B: not applicable.
- Reveal-source readiness: blocked at the no-peek audit.
- Prediction impact: none; `PRED-0063` through `PRED-0068` are unchanged.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: a clean evaluator must pin and review a qualifying
  post-registration source before any target matching or reveal scoring.

## Verdict

`BLOCKED_NO_PEEK_AUDIT`. The task preserves the contamination event as durable
negative workflow memory and stops before manifest creation, target matching,
or scoring.
