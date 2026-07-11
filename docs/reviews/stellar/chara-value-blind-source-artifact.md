# TASK-0989: CHARA value-blind source artifact and DEBCat de-dup

## Scope and freeze

This package converts the TASK-0939 paper-level pin into a reviewable,
value-blind source artifact. It records identifiers and source identities only.
No mass, luminosity, radius, temperature, orbit, residual, or model-performance
value was extracted; no M-L metric was run; and no RESULT-0022/0024 or claim was
changed.

Retrieval date for the artifacts below: `2026-07-11`. SHA-256 values are for
the downloaded arXiv PDF bytes held in the temporary, uncommitted source cache;
the PDFs are not added to the repository.

## Pinned source surfaces

| Source surface | Paper-level locator | Artifact | Bytes | SHA-256 | Rights posture |
| --- | --- | --- | ---: | --- | --- |
| CHARA I | DOI `10.3847/1538-3881/ab064d`; arXiv `1902.05557`; HD 224355 | arXiv PDF | 610985 | `8860E1F9B2C37B13864F71996256177F5EBED98702DC63416B12B4C1D86DC3AE` | AAS, all rights reserved; local inspection only |
| CHARA II | DOI `10.3847/1538-3881/ab449d`; arXiv `1909.09161`; HD 185912 | arXiv PDF | 2922018 | `581DEBE7CE77DA900EB250E418BF020DE848A90EF7A8384186AD3381726B62C1` | AAS, all rights reserved; local inspection only |
| CHARA III | DOI `10.3847/1538-3881/ab8f95`; arXiv `2005.00546`; HD 8374 and HD 24546 | arXiv PDF | 958390 | `1F61A6DDCFEFD1225459EA6A3485B2C17EC09870A91DC15025FE531BBEEE7B5C` | AAS, all rights reserved; local inspection only |
| CHARA IV | DOI `10.3847/1538-3881/ac9385`; arXiv `2209.09993`; HD 61859, HD 89822, HD 109510, HD 191692 | arXiv PDF | 1227253 | `BF700038072502164842A92384713F9C030BE56CDAC9A6E243DD4D4942ADFD6B` | CC BY 4.0; attribution required |
| Hyades six | arXiv `2406.01674`; HD 27483, HD 283882, HD 26874, HD 27149, HD 30676, HD 28545 | arXiv PDF | 1717730 | `C8BC5D92F3CD3386F648A777C6BDBE50C324CA666E56AF23A0F13543895229D0` | CC BY 4.0; attribution required |
| HD 284163 | DOI `10.1093/mnras/stad3803`; arXiv `2312.05301`; article and online supplementary material | arXiv PDF; publisher supplement locator recorded, bytes not redistributed | 2695999 | `B70C76A0EB77F7E2C723471361FBD0B832F4AB9944F52D94BE09BDDE6D87182F` | CC BY 4.0; attribution required |

The HD 284163 supplementary surface is identified by the article DOI and the
publisher's online supplementary-material link (`stad3803_supplemental_file.zip`).
Its signed download URL was not retained and no supplement hash is asserted.
The article page states that the underlying data are available in the article
and online supplementary material. This is sufficient for the paper-level
package, but a future row-curation task must pin the supplement bytes before
using any table values.

## Identifier-only de-dup ledger

The comparison surface is the committed
`data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml` (748
component rows, 373 system identifiers). Normalization is limited to stable
identifier spelling; no fuzzy inference or value comparison is used.

| Paper surface | Candidate identifier | DEBCat match at this stage | Decision |
| --- | --- | --- | --- |
| CHARA I | HD 224355 | V1022_Cas | `EXCLUDE_OVERLAP` |
| CHARA II | HD 185912 | V1143_Cyg | `EXCLUDE_OVERLAP` |
| CHARA III | HD 8374 | none | `ALIAS_AUDIT_REQUIRED` |
| CHARA III | HD 24546 | none | `ALIAS_AUDIT_REQUIRED` |
| CHARA IV | HD 61859 | none | `ALIAS_AUDIT_REQUIRED` |
| CHARA IV | HD 89822 | none | `ALIAS_AUDIT_REQUIRED` |
| CHARA IV | HD 109510 | none | `ALIAS_AUDIT_REQUIRED` |
| CHARA IV | HD 191692 | none | `ALIAS_AUDIT_REQUIRED` |
| Hyades six | HD 27483 | none | `ALIAS_AUDIT_REQUIRED` |
| Hyades six | HD 283882 | none | `ALIAS_AUDIT_REQUIRED` |
| Hyades six | HD 26874 | none | `ALIAS_AUDIT_REQUIRED` |
| Hyades six | HD 27149 | none | `ALIAS_AUDIT_REQUIRED` |
| Hyades six | HD 30676 | none | `ALIAS_AUDIT_REQUIRED` |
| Hyades six | HD 28545 | none | `ALIAS_AUDIT_REQUIRED` |
| HD 284163 | HD 284163; BD +23 635; Pels 20; V1136 Tau | none | `ALIAS_AUDIT_REQUIRED` |

The two explicit matches are excluded as whole physical systems. Any future
stable alias intersection must produce the same whole-system exclusion. An
ambiguous or unresolved alias is also excluded from an independent holdout; it
must not be counted as independent by default.

## Counts and verdict

| Quantity | Value |
| --- | ---: |
| Paper-level systems | 15 |
| Known DEBCat overlaps excluded now | 2 |
| Candidates after known exclusions | 13 |
| Independent holdout-ready systems | 0 |
| Value rows extracted | 0 |
| Metrics or fits run | false |
| Result/claim mutations | 0 |

**Verdict: `SOURCE_ARTIFACT_READY`.** The source package is ready for a later
identifier-complete row-curation task. It is not yet an independent Stellar
M-L holdout and does not support a benchmark or claim.

## Future row-curation contract

Before any value extraction, the next task must freeze the DEBCat revision and
source hashes, collect paper/HD/HIP/HR/GCVS/Gaia/cluster/hierarchy identifiers,
pin alias responses, apply whole-system exclusion on stable intersections, and
exclude ambiguity. Only after that ledger is reviewed may a separate task
extract values and define the benchmark split. That task must retain source
attribution and must not retroactively change this value-blind package.

## Output routing

- Gate A: source-artifact readiness only; no prediction or result is produced.
- Gate B: not applicable; no replay or metric is run.
- Claim impact: none.
- Knowledge impact: source pin and de-dup handoff for the Stellar M-L lane.
- Publication blocker: full alias audit and a maintainer-approved row-curation
  task remain before any independent holdout claim.

